"""Crop growth stage estimated from the sowing date.

Stage lengths are the FAO-56 "typical" lengths of the four crop development stages (Allen et al., 1998,
FAO Irrigation and Drainage Paper 56, Table 11): initial, crop development, mid-season, late season.
They vary with variety, season and climate, so the result is always labelled an *estimate* with its
method, the table row it came from, and a confidence. Only the Indian row of the table is "moderate";
rows from other regions are "low". Crops without a Table 11 row we can cite return `no_calendar`
rather than a guessed stage.
"""
from datetime import date

from services.crops import normalize_crop

REFERENCE = {
    "source": "FAO Irrigation and Drainage Paper 56, Table 11 (Allen et al., 1998)",
    "url": "https://www.fao.org/4/x0490e/x0490e0b.htm",
    "notes": "Typical stage lengths for one climate and planting period; your variety and season may differ.",
}
STAGES = ("initial", "development", "mid_season", "late_season")

# crop -> (initial, development, mid-season, late-season days, Table 11 row: planting period and region, India row?)
CALENDARS: dict[str, tuple[tuple[int, int, int, int], str, bool]] = {
    "Wheat": ((20, 25, 60, 30), "Spring wheat, November planting, Central India", True),
    "Maize": ((20, 35, 40, 30), "Maize (grain), October planting, India (dry, cool)", True),
    "Rice": ((30, 30, 60, 30), "Rice, December/May planting, tropics", False),
    "Sorghum": ((20, 35, 40, 30), "Sorghum (grain), May/June planting, USA/Pakistan/Mediterranean", False),
    "Pearl millet": ((15, 25, 40, 25), "Millet, June planting, Pakistan", False),
    "Soybean": ((15, 15, 40, 15), "Soybeans, December planting, tropics", False),
    "Groundnut": ((25, 35, 45, 25), "Groundnut, dry season, West Africa", False),
    "Cotton": ((30, 50, 60, 55), "Cotton, March-May planting, Egypt/Pakistan/California", False),
    "Sugarcane": ((35, 60, 190, 120), "Sugarcane (virgin), low latitudes", False),
    "Potato": ((25, 30, 45, 30), "Potato, January/November planting, semi-arid climate", False),
    "Tomato": ((30, 40, 40, 25), "Tomato, January planting, arid region", False),
    "Onion": ((15, 25, 70, 40), "Onion (dry), April planting, Mediterranean", False),
}


def estimate_stage(crop: str | None, sowing_date: date | None, today: date) -> dict:
    """Stage estimate with `status`: estimated | not_provided | no_calendar | before_sowing | beyond_season."""
    canonical = normalize_crop(crop)
    base = {"method": "sowing_date_calendar", "crop": canonical, "stage": None, "days_since_sowing": None,
            "season_length_days": None, "confidence": None, "calendar": None, "reference": REFERENCE}
    if not canonical or not sowing_date:
        return {**base, "status": "not_provided"}
    if canonical not in CALENDARS:
        return {**base, "status": "no_calendar"}

    lengths, row, india_row = CALENDARS[canonical]
    days = (today - sowing_date).days
    total = sum(lengths)
    common = {**base, "days_since_sowing": days, "season_length_days": total, "calendar": row}
    if days < 0:
        return {**common, "status": "before_sowing"}
    if days >= total:
        # Past the typical season: probably harvested or a longer variety. Do not guess a stage.
        return {**common, "status": "beyond_season", "confidence": "low"}

    end = 0
    for name, length in zip(STAGES, lengths):
        start, end = end, end + length
        if days < end:
            return {**common, "status": "estimated", "stage": name, "stage_day_range": [start, end],
                    "confidence": "moderate" if india_row else "low"}
    raise AssertionError("unreachable")
