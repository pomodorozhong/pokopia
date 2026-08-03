#!/usr/bin/env python3
"""Build data/planner.json for the static living-area planner UI."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# CSV typos / wording drift → localization favorite keys
FAVORITE_ALIASES = {
    "group activites": "group_activities",
    "noise stuff": "noisy_stuff",
}

# CSV display names → localization pokemon entries (by slug or en)
NAME_OVERRIDES = {
    "Paldean Wooper": "wooper",
    "Stereo Rotom": "rotom",
    "Professor Tangrowth": "tangrowth",
    "Mosslax": "snorlax",
    "Peakychu": "pikachu",
}


def icon_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    loc = load_json(DATA / "localization.json")
    favorite_items = load_json(DATA / "favorite_items.json")

    fav_by_en = {meta["en"].lower(): key for key, meta in loc["favorites"].items()}
    loc_by_slug = {p["slug"]: p for p in loc["pokemon"].values()}
    loc_by_en = {p["en"].lower(): p for p in loc["pokemon"].values()}

    def favorite_key(label: str) -> str | None:
        text = (label or "").strip()
        if not text or text.lower() == "none":
            return None
        low = text.lower()
        if low in FAVORITE_ALIASES:
            return FAVORITE_ALIASES[low]
        return fav_by_en.get(low)

    def find_localization(csv_name: str):
        if csv_name in NAME_OVERRIDES:
            return loc_by_slug.get(NAME_OVERRIDES[csv_name])
        low = csv_name.lower()
        if low in loc_by_en:
            return loc_by_en[low]
        slug = icon_slug(csv_name)
        for entry in loc["pokemon"].values():
            if icon_slug(entry["en"]) == slug or entry["slug"].replace("-", "") == slug:
                return entry
        return None

    with (DATA / "Pokopia.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    pokemon = []
    for row in rows:
        favorites = []
        for i in range(1, 7):
            key = favorite_key(row[f"Favorite {i}"])
            if key and key not in favorites:
                favorites.append(key)

        loc_entry = find_localization(row["Name"])
        if loc_entry:
            names = {
                "en": loc_entry["en"],
                "ja": loc_entry["ja"],
                "zh_tw": loc_entry["zh_tw"],
            }
            loc_slug = loc_entry["slug"]
        else:
            names = {
                "en": row["Name"],
                "ja": row["Name"],
                "zh_tw": row["Name"],
            }
            loc_slug = None

        pokemon.append(
            {
                "id": row["Number"].lstrip("#"),
                "name_en": row["Name"],
                "icon": icon_slug(row["Name"]),
                "primary_location": row["Primary Location"],
                "specialty_1": row["Specialty 1"] or None,
                "specialty_2": row["Specialty 2"] or None,
                "ideal_habitat": (row["Ideal Habitat"] or "").strip().lower() or None,
                "favorites": favorites,
                "names": names,
                "loc_slug": loc_slug,
            }
        )

    out = {
        "meta": {
            "source": [
                "data/Pokopia.csv",
                "data/localization.json",
                "data/favorite_items.json",
            ],
            "pokemon_count": len(pokemon),
            "favorite_count": len(loc["favorites"]),
            "item_count": len(loc["items"]),
        },
        "pokemon": pokemon,
        "favorites": loc["favorites"],
        "ideal_habitats": loc["ideal_habitats"],
        "items": loc["items"],
        "item_categories": loc.get("item_categories", {}),
        "favorite_items": {
            key: value["item_slugs"]
            for key, value in favorite_items["favorite_items"].items()
        },
        "item_favorites": favorite_items["item_favorites"],
        "habitat_conflicts": [
            ["bright", "dark"],
            ["dry", "humid"],
            ["warm", "cool"],
        ],
    }

    out_path = DATA / "planner.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
