"""Regenerative practice recommendations.

Recommendations come from a fixed practice list. Each one lists the data signals
that raised or lowered its priority, so the farmer can see why it is shown. No
yield numbers or benefit percentages are produced: the practice text (rendered by
the frontend in the farmer's language) describes benefits qualitatively.
"""
from services.crops import crop_group

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _rec(id, priority, triggers, params=None):
    return {"id": id, "priority": priority, "triggers": triggers, "params": params or {}}


def recommend(crop: str | None, soil: dict, insights: list[dict]) -> list[dict]:
    group = crop_group(crop)
    soil_ok = soil.get("status") == "available"
    props = soil.get("properties", {}) if soil_ok else {}
    ratings = soil.get("ratings", {}) if soil_ok else {}
    oc_rating = ratings.get("organic_carbon")
    ph_rating = ratings.get("ph")
    insight_ids = {i["id"] for i in insights}

    oc_trigger = (
        {"signal": "soil_organic_carbon", "value": props.get("organic_carbon_pct"), "rating": oc_rating}
        if oc_rating else {"signal": "soil_data", "value": None, "rating": "unavailable"}
    )
    crop_trigger = {"signal": "crop", "value": crop, "rating": group} if crop else None
    recs = []

    # A lab test is the gateway to every nutrient decision; most important when modelled data is missing.
    recs.append(_rec("soil_test", "high" if not soil_ok else "medium", [oc_trigger]))

    if oc_rating != "high":
        recs.append(_rec("organic_matter", "high" if oc_rating == "low" else "medium", [oc_trigger]))

    if group in ("cereal", "millet", "cash", "fibre"):
        recs.append(_rec("residue_retention", "high" if oc_rating == "low" else "medium", [t for t in (crop_trigger, oc_trigger) if t]))
        recs.append(_rec("legume_rotation", "medium", [crop_trigger]))
    elif group == "legume":
        recs.append(_rec("cereal_legume_rotation", "medium", [crop_trigger]))
    else:
        recs.append(_rec("crop_rotation", "medium", [crop_trigger] if crop_trigger else []))

    recs.append(_rec("cover_crop", "high" if oc_rating == "low" else "medium", [oc_trigger]))

    water_triggers = []
    if "dry_spell" in insight_ids:
        water_triggers.append({"signal": "forecast_dry_spell", "value": None, "rating": "watch"})
    sand = props.get("sand_pct")
    if sand is not None and sand >= 60:
        water_triggers.append({"signal": "soil_sand_pct", "value": sand, "rating": "sandy"})
    recs.append(_rec("water_conservation", "high" if water_triggers else "medium", water_triggers))

    if ph_rating in ("strongly_acidic", "strongly_alkaline"):
        recs.append(_rec(
            "ph_management", "high",
            [{"signal": "soil_ph", "value": props.get("ph"), "rating": ph_rating}],
            {"direction": "acidic" if ph_rating == "strongly_acidic" else "alkaline"},
        ))

    recs.append(_rec("reduced_tillage", "low", []))
    recs.append(_rec("integrated_nutrients", "medium" if soil_ok else "low", [oc_trigger]))
    recs.append(_rec("biodiversity", "low", []))

    recs.sort(key=lambda r: PRIORITY_ORDER[r["priority"]])
    return recs
