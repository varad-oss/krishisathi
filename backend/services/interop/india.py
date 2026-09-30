"""India adapter: publishes KrishiSathi's existing Indian data as schema v1.0 signals.

Sources: Open-Meteo forecasts at state reference points (rule-evaluated), KrishiSathi photo diagnoses
(AI-classified, aggregated to 0.5° cells, groups under MIN_GROUP suppressed), outbreak clusters, and
authenticated state federation submissions. Nothing is estimated to fill gaps.
"""
import math
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

from models.interop_v1 import (
    CropV1, DiseaseV1, GeoRefV1, GridCellV1, ObservationV1, PeriodV1, PrivacyV1, ProvenanceV1, ReferenceSourceV1, RiskSignalV1,
)
from services.crops import ALIASES, CROPS, normalize_crop
from services.disease_reference_service import disease_reference_service
from services.persistence_service import OUTBREAK_MIN_REPORTS, OUTBREAK_WINDOW_DAYS, persistence_service
from services.regions import INDIAN_STATES, iso_region, state_weather_risk

CELL_DEG = 0.5
MIN_GROUP = OUTBREAK_MIN_REPORTS  # the same minimum KrishiSathi uses before calling anything a cluster
INSIGHT_LEVEL = {"info": "low", "watch": "moderate", "warning": "high"}
FEDERATION_LEVEL = {"info": "low", "low": "low", "moderate": "moderate", "high": "high", "critical": "high"}
WEATHER_CATEGORY = {"heavy_rain": "waterlogging", "rain_expected": "rain", "heat_stress": "heat_stress", "cold_stress": "cold_stress",
                    "fungal_risk": "disease", "dry_spell": "water_stress", "spray_wind": "spray_window"}

AI_REPORTS = ProvenanceV1(
    source="KrishiSathi photo diagnoses (India)", kind="ai_classified_reports",
    method=f"Moderate/high-certainty AI photo detections, counted per {CELL_DEG}° cell; groups under {MIN_GROUP} suppressed",
    notes="Not laboratory-confirmed and not official statistics; reflects where the app is used.",
)


def crop_code(name: str | None) -> str | None:
    canonical = normalize_crop(name)
    return canonical.lower().replace(" ", "_") if canonical else None


def cell(lat: float, lng: float) -> GridCellV1:
    return GridCellV1(cell_deg=CELL_DEG, lat=math.floor(lat / CELL_DEG) * CELL_DEG, lng=math.floor(lng / CELL_DEG) * CELL_DEG)


def _grid_geo(lat: float, lng: float) -> GeoRefV1:
    return GeoRefV1(country_code="IN", grid=cell(lat, lng), basis="grid_cell")


class IndiaAdapter:
    country_code = "IN"
    name = "India (KrishiSathi)"
    privacy = PrivacyV1(aggregation=f"{CELL_DEG}° grid cells or state reference points", minimum_group_size=MIN_GROUP,
                        spatial_resolution=f"{CELL_DEG}° (~55 km)")

    def describe(self) -> dict:
        return {
            "country_code": self.country_code,
            "name": self.name,
            "schema_version": "1.0",
            "sources": [
                {"id": "weather", "name": "Open-Meteo forecast at one reference point per state", "kind": "forecast"},
                {"id": "diagnoses", "name": "KrishiSathi photo diagnoses", "kind": "ai_classified_reports"},
                {"id": "federation", "name": "Authenticated state federation submissions", "kind": "authenticated_submission"},
                {"id": "disease_reference", "name": "Curated ICAR disease reference", "kind": "curated_reference"},
            ],
            "coverage": {"states": [iso_region(s["code"]) for s in INDIAN_STATES]},
            "privacy": self.privacy.model_dump(),
            "limitations": [
                "Weather signals are rule evaluations at one point per state, not statewide.",
                "Disease observations are AI-classified app reports, not surveillance statistics.",
                "Satellite crop-health aggregation is not published.",
            ],
        }

    async def crops(self) -> list[CropV1]:
        aliases = defaultdict(list)
        for alias, name in ALIASES.items():
            aliases[name].append(alias)
        return [CropV1(crop_code=crop_code(name), name_en=name, group=group, aliases=sorted(aliases[name])) for name, group in CROPS.items()]

    async def diseases(self) -> list[DiseaseV1]:
        out = []
        for d in disease_reference_service.data:
            codes = sorted({c for c in (crop_code(x) for x in d.get("crops", [])) if c})
            out.append(DiseaseV1(
                disease_code=d["id"], name_en=d["name"], scientific_name=d.get("scientific_name"), crop_codes=codes,
                references=[ReferenceSourceV1(**{k: s.get(k) for k in ("organization", "title", "url")}) for s in d.get("sources", [])],
                provenance=ProvenanceV1(source="KrishiSathi curated disease reference (ICAR institutes)", kind="curated_reference"),
            ))
        return out

    async def weather_signals(self) -> list[RiskSignalV1]:
        risk = await state_weather_risk()
        issued = datetime.now(timezone.utc)
        retrieved = datetime.fromisoformat(risk["provenance"]["retrieved_at"])
        out = []
        for region in risk["regions"]:
            if region["status"] != "available":
                continue  # an unavailable forecast publishes nothing, rather than "no risk"
            for i in region["insights"]:
                day = date.fromisoformat(i["date"]) if i.get("date") else issued.date()
                out.append(RiskSignalV1(
                    signal_id=f"IN-wx-{region['state']}-{i['id']}-{day.isoformat()}", signal_type="weather_risk",
                    category=WEATHER_CATEGORY.get(i["id"], i["id"]), severity=INSIGHT_LEVEL[i["severity"]],
                    geo=GeoRefV1(country_code="IN", region_code=iso_region(region["state"]), basis="region_reference_point"),
                    source_region=iso_region(region["state"]), period=PeriodV1(start=day, end=day), issued_at=issued, confidence="moderate",
                    provenance=ProvenanceV1(source="Open-Meteo forecast", kind="forecast", retrieved_at=retrieved,
                                            method=f"KrishiSathi agro rule '{i['id']}' (threshold source: {i['basis']['source']['name']}) "
                                                   "at the state's reference point"),
                ))
        return out

    async def observations(self, since: date) -> list[ObservationV1]:
        rows = await persistence_service.detection_rows(datetime.combine(since, datetime.min.time()))
        groups: dict[tuple, list] = defaultdict(list)
        for disease, crop, lat, lng, day in rows:
            c = cell(lat, lng)
            groups[(disease, crop_code(crop), c.lat, c.lng)].append(day)
        today = date.today()
        out = []
        for (disease, crop, lat, lng), days in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            if len(days) < MIN_GROUP:
                continue
            ref = next((d for d in disease_reference_service.data if d.get("name") == disease), None)
            out.append(ObservationV1(
                observation_type="disease_observation", geo=GeoRefV1(country_code="IN", grid=GridCellV1(cell_deg=CELL_DEG, lat=lat, lng=lng), basis="grid_cell"),
                period=PeriodV1(start=since, end=today), crop_code=crop, subject=ref["id"] if ref else disease,
                variable="ai_classified_detections", value=len(days), unit="count", sample_size=len(days), confidence="low", provenance=AI_REPORTS,
            ))
        return out

    async def risk_signals(self, since: date) -> list[RiskSignalV1]:
        out = []
        for o in await persistence_service.get_outbreaks():
            last = datetime.fromisoformat(o["timestamp"])
            if last.date() < since:
                continue
            out.append(RiskSignalV1(
                signal_id=f"IN-cluster-{o['id']}", signal_type="disease_cluster", category="disease", severity=o["severity"],
                geo=_grid_geo(o["lat"], o["lng"]), crop_codes=[c for c in (crop_code(x) for x in o["crop_targets"]) if c],
                disease=o["disease"], report_count=o["report_count"],
                period=PeriodV1(start=last.date() - timedelta(days=OUTBREAK_WINDOW_DAYS), end=last.date()), issued_at=last, confidence="low",
                provenance=ProvenanceV1(source="KrishiSathi outbreak clusters", kind="ai_classified_reports",
                                        method=f"≥{MIN_GROUP} AI-classified detections of one disease within 50 km in {OUTBREAK_WINDOW_DAYS} days",
                                        notes="A cluster of app reports, not a confirmed outbreak or evidence of spread."),
            ))
        for s in await persistence_service.get_federation_signals():
            if s.timestamp.date() < since:
                continue
            ts = s.timestamp if s.timestamp.tzinfo else s.timestamp.replace(tzinfo=timezone.utc)
            out.append(RiskSignalV1(
                signal_id=f"IN-fed-{s.signal_id}", signal_type=s.signal_type.value if hasattr(s.signal_type, "value") else s.signal_type,
                severity=FEDERATION_LEVEL.get(getattr(s.severity, "value", s.severity), "moderate"),
                geo=GeoRefV1(country_code="IN", region_code=iso_region(s.from_state), basis="region"),
                source_region=iso_region(s.from_state), affected_region=iso_region(s.to_state) if s.to_state else None,
                crop_codes=[c for c in [crop_code(s.affected_crop)] if c], disease=s.disease_name, report_count=s.report_count,
                period=PeriodV1(start=ts.date(), end=ts.date()), issued_at=ts, confidence="moderate",
                provenance=ProvenanceV1(source=f"State system {s.from_state} (authenticated submission)", kind="authenticated_submission",
                                        notes="Published by an authenticated state system; content is the publisher's."),
            ))
        return sorted(out, key=lambda r: r.issued_at, reverse=True)
