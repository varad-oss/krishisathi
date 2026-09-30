"""Agricultural early warning for administrators: disease signals, weather threats and crop-health anomalies.

Every signal states its geography, period, number of observations, confidence, source and limits. Nothing is
estimated to fill a gap: sources that cannot support a signal are reported as unavailable, and thin data is
flagged instead of producing trends.
"""
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from services.earth_engine_service import earth_engine_service
from services.persistence_service import OUTBREAK_MIN_REPORTS, persistence_service
from services.regions import AGGREGATION as WEATHER_AGGREGATION, state_weather_risk

WINDOW_DAYS = 7              # current window; compared with the 7 days before it
CELL_DEG = 0.5               # disease signals are aggregated to 0.5° cells (~55 km), coarser than any farm
MIN_OBSERVATIONS = 20        # fewer confident, located detections than this in 14 days: data flagged as insufficient
SEVERITY_ORDER = {"high": 3, "moderate": 2, "low": 1}
DISEASE_SOURCE = {"source": "KrishiSathi photo diagnoses", "kind": "ai_classified_user_reports"}
DISEASE_LIMITS = ["ai_classified", "app_usage_bias", "not_lab_confirmed"]


def confidence_for(n: int) -> str:
    """Sample-size rule, not a statistical test: the number of confident reports behind a signal."""
    return "high" if n >= 10 else "moderate" if n >= 5 else "low"


def trend_for(current: int, previous: int) -> str:
    if previous == 0:
        return "new"
    return "rising" if current > previous else "falling" if current < previous else "steady"


def _cell(lat: float, lng: float) -> tuple[float, float]:
    """Centre of the 0.5° cell containing the point."""
    return (math.floor(lat / CELL_DEG) * CELL_DEG + CELL_DEG / 2, math.floor(lng / CELL_DEG) * CELL_DEG + CELL_DEG / 2)


def disease_signals(records: list[dict], now: datetime) -> dict:
    """Groups detections by disease and 0.5° cell and compares the last 7 days with the 7 before.

    A signal needs at least OUTBREAK_MIN_REPORTS detections in the current window (the same bar as a cluster);
    groups below it are only counted, never shown as signals.
    """
    split = now - timedelta(days=WINDOW_DAYS)
    groups: dict[tuple, dict] = defaultdict(lambda: {"current": 0, "previous": 0, "severities": Counter(), "crops": Counter(), "last": None})
    for r in records:
        g = groups[(r["disease"], *_cell(r["lat"], r["lng"]))]
        if r["timestamp"] >= split:
            g["current"] += 1
            if r.get("severity"):
                g["severities"][r["severity"]] += 1
            if r.get("crop"):
                g["crops"][r["crop"]] += 1
            g["last"] = max(g["last"] or r["timestamp"], r["timestamp"])
        else:
            g["previous"] += 1

    signals, below = [], 0
    for (disease, lat, lng), g in groups.items():
        if g["current"] < OUTBREAK_MIN_REPORTS:
            below += 1 if g["current"] else 0
            continue
        severity = max(g["severities"], key=lambda s: (g["severities"][s], SEVERITY_ORDER[s])) if g["severities"] else None
        signals.append({
            "type": "disease",
            "disease": disease,
            "crops": [c for c, _ in g["crops"].most_common(3)],
            "geography": {"kind": "grid_cell", "size_deg": CELL_DEG, "lat": lat, "lng": lng},
            "observations": g["current"],
            "observations_previous": g["previous"],
            "trend": trend_for(g["current"], g["previous"]),
            "severity": severity,
            "confidence": confidence_for(g["current"]),
            "last_report": g["last"].isoformat(),
        })
    signals.sort(key=lambda s: (-SEVERITY_ORDER.get(s["severity"], 0), -s["observations"]))
    return {"signals": signals, "below_threshold": below}


def weather_threats(risk: dict) -> dict:
    threats, unavailable = [], []
    for region in risk["regions"]:
        if region["status"] != "available":
            unavailable.append(region["state"])
            continue
        for insight in region["insights"]:
            if insight["severity"] in ("warning", "watch"):
                threats.append({
                    "type": "weather",
                    "state": region["state"],
                    "id": insight["id"],
                    "category": insight.get("category"),
                    "severity": insight["severity"],
                    "date": insight.get("date"),
                    "params": insight.get("params", {}),
                    "basis": insight.get("basis"),
                    "geography": {"kind": WEATHER_AGGREGATION, "state": region["state"]},
                })
    threats.sort(key=lambda t: (t["severity"] != "warning", t.get("date") or ""))
    return {"threats": threats, "states_unavailable": unavailable, "provenance": risk["provenance"]}


async def early_warning(now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    records = await persistence_service.recent_detections(days=2 * WINDOW_DAYS)
    disease = disease_signals(records, now)
    weather = weather_threats(await state_weather_risk())
    observed_cells = {_cell(r["lat"], r["lng"]) for r in records}
    return {
        "generated_at": now.isoformat(),
        "period": {"start": (now - timedelta(days=WINDOW_DAYS)).date().isoformat(), "end": now.date().isoformat(),
                   "compared_with": {"start": (now - timedelta(days=2 * WINDOW_DAYS)).date().isoformat(),
                                     "end": (now - timedelta(days=WINDOW_DAYS)).date().isoformat()}},
        "disease": {**disease, "method": {"cell_deg": CELL_DEG, "min_reports": OUTBREAK_MIN_REPORTS, "window_days": WINDOW_DAYS,
                                          "confidence_rule": "reports: <5 low, 5-9 moderate, >=10 high"},
                    **DISEASE_SOURCE, "limitations": DISEASE_LIMITS},
        "weather": weather,
        "crop_health": {"status": "unavailable",
                        "reason": "not_configured" if not earth_engine_service.initialized else "regional_aggregation_not_implemented"},
        "coverage": {"observations_14d": len(records), "grid_cells_14d": len(observed_cells), "cell_deg": CELL_DEG,
                     "insufficient_data": len(records) < MIN_OBSERVATIONS, "min_observations": MIN_OBSERVATIONS},
    }
