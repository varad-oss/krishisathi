"""Brazil adapter: official Brazilian crop statistics published through the same v1.0 schemas as India.

Source (the only one used): IBGE, Produção Agrícola Municipal (PAM), SIDRA table 5457 - "Área plantada ou destinada
à colheita, área colhida, quantidade produzida, rendimento médio e valor da produção das lavouras temporárias e
permanentes" - read from the public SIDRA API (https://apisidra.ibge.gov.br, no key). IBGE is Brazil's official
statistics agency; PAM is its annual survey of crop area, production and yield, published about a year after the
reference year. Values are copied as published, per state (Unidade da Federação), for the latest published year.

Why this source: public and keyless, a long-stable documented API, official semantics (variable names and units come
with every response), national coverage at state level, and structured JSON. Embrapa's AgroAPI Agritec v2 (ZARC
planting windows and climate-risk zoning) is the natural source for planting-risk signals, but it requires AgroAPI
registration (OAuth) and its response semantics were not verified from this deployment, so it is listed as
identified-but-not-integrated rather than guessed at. The Ministry of Agriculture (MAPA) open-data portal publishes
ZARC as bulk tables; also not integrated yet.

Nothing is estimated: if SIDRA cannot be reached the adapter raises SourceUnavailable (the API answers 503), and
categories without a real Brazilian source raise UnsupportedCategory (the API answers status "unsupported").
"""
import asyncio
import logging
import time
import unicodedata
from datetime import date, datetime, timezone

import httpx

from models.interop_v1 import CropV1, DiseaseV1, GeoRefV1, ObservationV1, PeriodV1, PrivacyV1, ProvenanceV1, RiskSignalV1
from services.interop.adapter import SourceUnavailable, UnsupportedCategory

logger = logging.getLogger(__name__)

SIDRA_BASE = "https://apisidra.ibge.gov.br/values"
PAM_TABLE = "5457"
PRODUCT_CLASSIFICATION = "c782"   # "Produto das lavouras temporárias e permanentes"
# SIDRA variable code -> (schema variable, word the Portuguese variable name must contain). The name check guards
# against a code being reused for something else: a mismatching row is dropped, never relabelled.
VARIABLES = {"216": ("harvested_area", "colhida"), "214": ("production", "produzida"), "112": ("yield", "rendimento")}
UNITS = {"hectares": "ha", "toneladas": "t", "quilogramas por hectare": "kg/ha"}
# IBGE marks cells without a number: "-" zero (not from rounding), ".." not applicable, "..." not available,
# "X" withheld for confidentiality. All are omitted; none is turned into a number.
NON_NUMERIC = {"-", "..", "...", "X", ""}
SIDRA_URL = (f"{SIDRA_BASE}/t/{PAM_TABLE}/n3/all/v/{','.join(VARIABLES)}/p/last%201/{PRODUCT_CLASSIFICATION}/all")
TIMEOUT_S = 20.0
CACHE_TTL_S = 24 * 3600           # an annual statistic; one fetch a day is plenty

# IBGE state (UF) codes -> ISO 3166-2:BR subdivision codes.
UF_ISO = {
    "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
    "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
    "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF",
}

# PAM product name (normalized, text before any parenthesis) -> (crop_code, English name, group). Codes match the India
# adapter where the crop is the same (soybean, maize, rice, ...), so partners can line the catalogues up. This is a
# translation table for IBGE's product list, not data; PAM products without a confident English equivalent are left out.
PRODUCTS = {
    "soja": ("soybean", "Soybean", "legume"),
    "milho": ("maize", "Maize", "cereal"),
    "arroz": ("rice", "Rice", "cereal"),
    "trigo": ("wheat", "Wheat", "cereal"),
    "sorgo": ("sorghum", "Sorghum", "millet"),
    "algodao herbaceo": ("cotton", "Cotton", "fibre"),
    "cana-de-acucar": ("sugarcane", "Sugarcane", "cash"),
    "batata-inglesa": ("potato", "Potato", "vegetable"),
    "tomate": ("tomato", "Tomato", "vegetable"),
    "cebola": ("onion", "Onion", "vegetable"),
    "amendoim": ("groundnut", "Groundnut", "legume"),
    "feijao": ("dry_bean", "Common bean (dry)", "legume"),
    "mandioca": ("cassava", "Cassava", "root"),
    "cafe": ("coffee", "Coffee", "cash"),
}
PT_NAMES = {"soybean": "Soja (em grão)", "maize": "Milho (em grão)", "rice": "Arroz (em casca)", "wheat": "Trigo (em grão)",
            "sorghum": "Sorgo (em grão)", "cotton": "Algodão herbáceo (em caroço)", "sugarcane": "Cana-de-açúcar",
            "potato": "Batata-inglesa", "tomato": "Tomate", "onion": "Cebola", "groundnut": "Amendoim (em casca)",
            "dry_bean": "Feijão (em grão)", "cassava": "Mandioca", "coffee": "Café (em grão) Total"}

PROVENANCE_SOURCE = f"IBGE - Produção Agrícola Municipal (PAM), SIDRA table {PAM_TABLE}"
PROVENANCE_URL = f"https://sidra.ibge.gov.br/tabela/{PAM_TABLE}"

_cache: dict[str, tuple[float, list[ObservationV1]]] = {}
_inflight: dict[str, asyncio.Future] = {}


def _normalize(text: str) -> str:
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return plain.split("(")[0].strip()


def product_crop(name: str) -> tuple[str, str, str] | None:
    """Maps a PAM product name to (crop_code, English name, group); "Café (em grão) Total" and its variants map to
    coffee only through the total row, so arabica and canephora are not counted twice."""
    key = _normalize(name)
    if key == "cafe" and "total" not in name.lower():
        return None
    return PRODUCTS.get(key)


def _dimensions(header: dict) -> dict[str, str]:
    """Which Dn column holds which dimension, read from SIDRA's own header row (dimension order is not assumed)."""
    found = {}
    for key, label in header.items():
        if not (key.startswith("D") and key.endswith("C")):
            continue
        text = _normalize(label)
        if text.startswith("unidade da federacao"):
            found["uf"] = key
        elif text.startswith("ano"):
            found["year"] = key
        elif text.startswith("variavel"):
            found["variable"] = key
        elif text.startswith("produto"):
            found["product"] = key
    if set(found) != {"uf", "year", "variable", "product"}:
        raise SourceUnavailable("ibge_sidra_unexpected_format")
    return found


def parse_pam(payload: list, retrieved_at: datetime) -> list[ObservationV1]:
    """SIDRA JSON (first row = header labels) -> ObservationV1 per state, product and variable with a numeric value."""
    if not isinstance(payload, list) or not payload or not isinstance(payload[0], dict):
        raise SourceUnavailable("ibge_sidra_unexpected_format")
    dims = _dimensions(payload[0])
    name_key = lambda k: k[:-1] + "N"
    out = []
    for row in payload[1:]:
        value = str(row.get("V", "")).strip()
        variable = VARIABLES.get(str(row.get(dims["variable"])))
        uf = UF_ISO.get(str(row.get(dims["uf"])))
        crop = product_crop(str(row.get(name_key(dims["product"]), "")))
        unit = UNITS.get(str(row.get("MN", "")).strip().lower())
        if value in NON_NUMERIC or not (variable and uf and crop and unit):
            continue
        if variable[1] not in _normalize(str(row.get(name_key(dims["variable"]), ""))):
            continue
        try:
            number = float(value)
            year = int(str(row.get(dims["year"])))
        except ValueError:
            continue
        out.append(ObservationV1(
            observation_type="production_statistic",
            geo=GeoRefV1(country_code="BR", region_code=f"BR-{uf}", basis="region"),
            period=PeriodV1(start=date(year, 1, 1), end=date(year, 12, 31)),
            crop_code=crop[0], subject=str(row.get(name_key(dims["product"]))),
            variable=variable[0], value=number, unit=unit,
            provenance=ProvenanceV1(
                source=PROVENANCE_SOURCE, kind="official_statistic", url=PROVENANCE_URL, retrieved_at=retrieved_at,
                method=f"IBGE annual municipal crop survey, state totals for reference year {year}, copied as published "
                       f"(SIDRA variable {row.get(dims['variable'])}: {row.get(name_key(dims['variable']))})",
                notes="Official statistic for the whole state and year, not a farm or field value. Cells IBGE marks as "
                      "zero, not applicable, not available or confidential are omitted, not filled.",
            ),
        ))
    return out


async def _fetch() -> list[ObservationV1]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
            res = await client.get(SIDRA_URL, params={"formato": "json"})
        res.raise_for_status()
        payload = res.json()
    except (httpx.HTTPError, ValueError) as e:
        logger.error("IBGE SIDRA request failed: %s", e)
        raise SourceUnavailable("ibge_sidra_unavailable") from None
    observations = parse_pam(payload, datetime.now(timezone.utc))
    if not observations:
        raise SourceUnavailable("ibge_sidra_no_usable_rows")
    return observations


async def pam_observations() -> list[ObservationV1]:
    """Latest PAM year, cached for a day; concurrent callers share one request. Failures are not cached."""
    cached = _cache.get("pam")
    if cached and time.monotonic() < cached[0]:
        return cached[1]
    pending = _inflight.get("pam")
    if pending is None:
        pending = asyncio.ensure_future(_fetch())
        _inflight["pam"] = pending
        pending.add_done_callback(lambda _f: _inflight.pop("pam", None))
    observations = await asyncio.shield(pending)
    _cache["pam"] = (time.monotonic() + CACHE_TTL_S, observations)
    return observations


UNSUPPORTED = {
    "diseases": "No authoritative Brazilian disease catalogue is connected.",
    "weather_signals": "No Brazilian weather or agro-climatic risk source is connected (INMET and Embrapa Agritec/ZARC not integrated).",
    "risk_signals": "No Brazilian risk or early-warning source is connected; Embrapa Agritec (ZARC) needs AgroAPI registration.",
}


class BrazilAdapter:
    country_code = "BR"
    name = "Brazil (IBGE official crop statistics)"
    privacy = PrivacyV1(aggregation="State (UF) totals as published by IBGE; IBGE applies its own disclosure control",
                        minimum_group_size=0, spatial_resolution="state (Unidade da Federação)")

    def describe(self) -> dict:
        return {
            "country_code": self.country_code,
            "name": self.name,
            "schema_version": "1.0",
            "sources": [{"id": "ibge_pam", "name": f"IBGE Produção Agrícola Municipal (PAM), SIDRA table {PAM_TABLE}",
                         "kind": "official_statistic", "url": PROVENANCE_URL, "api": SIDRA_BASE,
                         "license": "Public official statistics; cite IBGE (SIDRA) as the source"}],
            "identified_not_integrated": [
                {"id": "embrapa_agritec_zarc", "name": "Embrapa AgroAPI Agritec v2 (ZARC planting windows, climate-risk zoning)",
                 "url": "https://www.agroapi.cnptia.embrapa.br/portal/",
                 "reason": "Requires AgroAPI registration (OAuth client credentials); response semantics not verified from this deployment."},
                {"id": "mapa_zarc_open_data", "name": "MAPA open-data portal: ZARC tables", "url": "https://dados.agricultura.gov.br/",
                 "reason": "Bulk tabular releases; not integrated."},
            ],
            "categories": {"crops": "available", "observations": "available",
                           **{k: "unsupported" for k in UNSUPPORTED}},
            "publishes": {
                "crops": {"types": ["crop_catalogue"], "geography": "national", "period": "reference list (IBGE PAM product list)",
                          "provenance_kind": "official_statistic", "confidence": None, "access": "public"},
                "observations": {"types": ["production_statistic"], "geography": "state (ISO 3166-2)",
                                 "period": "calendar year (latest published)", "provenance_kind": "official_statistic",
                                 "confidence": None, "access": "public"},
            },
            "coverage": {"states": sorted(f"BR-{uf}" for uf in UF_ISO.values()), "period": "latest published PAM reference year"},
            "privacy": self.privacy.model_dump(),
            "limitations": [
                "Annual state-level official statistics with about a one-year publication lag; not current-season conditions.",
                "Only PAM products with a clear English crop equivalent are mapped (see crops); others are not published.",
                "The 'since' filter does not apply: the latest published reference year is always returned.",
                "No disease, weather or risk signals: those categories are reported as unsupported, never simulated.",
            ],
        }

    async def crops(self) -> list[CropV1]:
        return [CropV1(crop_code=code, name_en=name, group=group, aliases=[PT_NAMES[code]]) for code, name, group in PRODUCTS.values()]

    async def diseases(self) -> list[DiseaseV1]:
        raise UnsupportedCategory("diseases", UNSUPPORTED["diseases"])

    async def weather_signals(self) -> list[RiskSignalV1]:
        raise UnsupportedCategory("weather_signals", UNSUPPORTED["weather_signals"])

    async def observations(self, since: date) -> list[ObservationV1]:
        return sorted(await pam_observations(), key=lambda o: (o.geo.region_code, o.crop_code, o.variable))

    async def risk_signals(self, since: date) -> list[RiskSignalV1]:
        raise UnsupportedCategory("risk_signals", UNSUPPORTED["risk_signals"])
