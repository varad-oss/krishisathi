"""Deterministic agro-meteorological rules.

Each insight is derived only from Open-Meteo values that are present. Every insight
carries the threshold that triggered it and where that threshold comes from, so
the farmer-facing text is explainable and never invented. Human-readable text is
rendered by the frontend from `id` + `params` so it can be localized without AI.

Severity levels: "info" < "watch" < "warning".
"""
from typing import Optional

IMD = {"name": "India Meteorological Department (IMD)", "url": "https://mausam.imd.gov.in/"}
GUIDANCE = {"name": "General agronomic guidance (KrishiSathi rule)", "url": None}

SEVERITY_ORDER = {"info": 0, "watch": 1, "warning": 2}

# Thresholds (kept here so they are visible, testable and documented in one place)
HEAVY_RAIN_MM = 64.5          # IMD: "heavy rain" is 64.5–115.5 mm in 24 h
RAIN_SKIP_IRRIGATION_MM = 5.0
RAIN_PROBABILITY_PCT = 60
HEAT_WATCH_C = 40.0           # IMD: heat-wave consideration for plains starts at 40 °C
HEAT_WARNING_C = 45.0         # IMD: 45 °C or more is a heat wave irrespective of normal
COLD_WATCH_C = 4.0            # IMD: cold wave for plains when minimum is 4 °C or below
COLD_WARNING_C = 2.0          # IMD: severe cold wave at 2 °C or below
FUNGAL_HUMIDITY_PCT = 85.0
FUNGAL_TEMP_RANGE_C = (15.0, 30.0)
DRY_SPELL_RAIN_MM = 2.0
DRY_SPELL_ET0_MM = 25.0
SPRAY_WIND_KMH = 15.0
OUTLOOK_DAYS = 3


def _num(v) -> Optional[float]:
    return float(v) if isinstance(v, (int, float)) else None


def _insight(id, category, severity, basis_kind, source, threshold, params, date=None):
    return {
        "id": id,
        "category": category,
        "severity": severity,
        "date": date,
        "params": params,
        "basis": {"kind": basis_kind, "threshold": threshold, "source": source},
    }


def evaluate(conditions: dict) -> list[dict]:
    insights: list[dict] = []
    days = (conditions.get("daily") or [])
    outlook = days[:OUTLOOK_DAYS]
    current = conditions.get("current") or {}

    # Heavy rain (warning) takes precedence over the lighter "rain expected" advice.
    heavy = next((d for d in outlook if (_num(d.get("precipitation_mm")) or 0) >= HEAVY_RAIN_MM), None)
    if heavy:
        insights.append(_insight(
            "heavy_rain", "weather", "warning", "forecast", IMD,
            {"precipitation_mm_gte": HEAVY_RAIN_MM},
            {"precipitation_mm": heavy["precipitation_mm"]}, heavy["date"],
        ))
    else:
        for d in days[:2]:
            mm = _num(d.get("precipitation_mm")) or 0
            prob = _num(d.get("precipitation_probability_pct"))
            if mm >= RAIN_SKIP_IRRIGATION_MM and (prob is None or prob >= RAIN_PROBABILITY_PCT):
                insights.append(_insight(
                    "rain_expected", "water", "info", "forecast", GUIDANCE,
                    {"precipitation_mm_gte": RAIN_SKIP_IRRIGATION_MM, "probability_pct_gte": RAIN_PROBABILITY_PCT},
                    {"precipitation_mm": mm, "probability_pct": prob}, d["date"],
                ))
                break

    hottest = max(outlook, key=lambda d: _num(d.get("temp_max_c")) or -99, default=None)
    t_max = _num(hottest.get("temp_max_c")) if hottest else None
    if t_max is not None and t_max >= HEAT_WATCH_C:
        severity = "warning" if t_max >= HEAT_WARNING_C else "watch"
        insights.append(_insight(
            "heat_stress", "crop_stress", severity, "forecast", IMD,
            {"temp_max_c_gte": HEAT_WARNING_C if severity == "warning" else HEAT_WATCH_C},
            {"temp_max_c": t_max}, hottest["date"],
        ))

    coldest = min(outlook, key=lambda d: _num(d.get("temp_min_c")) or 99, default=None)
    t_min = _num(coldest.get("temp_min_c")) if coldest else None
    if t_min is not None and t_min <= COLD_WATCH_C:
        severity = "warning" if t_min <= COLD_WARNING_C else "watch"
        insights.append(_insight(
            "cold_stress", "crop_stress", severity, "forecast", IMD,
            {"temp_min_c_lte": COLD_WARNING_C if severity == "warning" else COLD_WATCH_C},
            {"temp_min_c": t_min}, coldest["date"],
        ))

    for d in outlook:
        rh = _num(d.get("humidity_mean_pct"))
        hi, lo = _num(d.get("temp_max_c")), _num(d.get("temp_min_c"))
        if rh is None or hi is None or lo is None:
            continue
        mean_t = (hi + lo) / 2
        if rh >= FUNGAL_HUMIDITY_PCT and FUNGAL_TEMP_RANGE_C[0] <= mean_t <= FUNGAL_TEMP_RANGE_C[1]:
            insights.append(_insight(
                "fungal_risk", "disease", "watch", "forecast", GUIDANCE,
                {"humidity_mean_pct_gte": FUNGAL_HUMIDITY_PCT, "temp_mean_c_range": list(FUNGAL_TEMP_RANGE_C)},
                {"humidity_mean_pct": rh, "temp_mean_c": round(mean_t, 1)}, d["date"],
            ))
            break

    week = days[:7]
    rain_week = [_num(d.get("precipitation_mm")) for d in week]
    et0_week = [_num(d.get("et0_mm")) for d in week]
    if len(week) >= 5 and None not in rain_week and None not in et0_week:
        rain_total, et0_total = sum(rain_week), sum(et0_week)
        if rain_total < DRY_SPELL_RAIN_MM and et0_total >= DRY_SPELL_ET0_MM:
            insights.append(_insight(
                "dry_spell", "water", "watch", "forecast", GUIDANCE,
                {"precipitation_total_mm_lt": DRY_SPELL_RAIN_MM, "et0_total_mm_gte": DRY_SPELL_ET0_MM},
                {"precipitation_total_mm": round(rain_total, 1), "et0_total_mm": round(et0_total, 1), "days": len(week)},
                week[0]["date"],
            ))

    wind = _num(current.get("wind_kmh"))
    if wind is not None and wind >= SPRAY_WIND_KMH:
        insights.append(_insight(
            "spray_wind", "weather", "info", "current_model_estimate", GUIDANCE,
            {"wind_kmh_gte": SPRAY_WIND_KMH},
            {"wind_kmh": wind}, None,
        ))

    insights.sort(key=lambda i: SEVERITY_ORDER[i["severity"]], reverse=True)
    return insights
