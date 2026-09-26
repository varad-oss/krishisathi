"""Canonical crop list. Used to allow-list crop inputs before they reach prompts or rules."""

CROPS: dict[str, str] = {
    "Wheat": "cereal",
    "Rice": "cereal",
    "Maize": "cereal",
    "Sorghum": "millet",
    "Pearl millet": "millet",
    "Finger millet": "millet",
    "Chickpea": "legume",
    "Pigeon pea": "legume",
    "Soybean": "legume",
    "Groundnut": "legume",
    "Mustard": "oilseed",
    "Cotton": "fibre",
    "Sugarcane": "cash",
    "Potato": "vegetable",
    "Tomato": "vegetable",
    "Onion": "vegetable",
}
ALIASES = {"corn": "Maize", "paddy": "Rice", "bajra": "Pearl millet", "jowar": "Sorghum", "ragi": "Finger millet", "tur": "Pigeon pea", "arhar": "Pigeon pea", "gram": "Chickpea"}


def normalize_crop(value: str | None) -> str | None:
    """Returns the canonical crop name, or None for unknown/other/empty input."""
    if not value:
        return None
    v = value.strip().lower()
    if v in ALIASES:
        return ALIASES[v]
    for name in CROPS:
        if name.lower() == v:
            return name
    return None


def crop_group(crop: str | None) -> str | None:
    return CROPS.get(crop) if crop else None
