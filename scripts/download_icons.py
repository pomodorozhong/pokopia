#!/usr/bin/env python3
"""
Download / refresh Pokopia Pokémon and item icons.

Sources (in order):
  1) Serebii.net Pokémon Pokopia
     - Numbered small sprites:
       https://www.serebii.net/pokemonpokopia/pokemon/small/{###}.png
       → icons/pokemon/by_number/{###}.png
     - Item icons discovered from items + favorites pages:
       https://www.serebii.net/pokemonpokopia/items/{slug}.png
       → icons/items/{slug}.png
  2) Optional seed from Pokopia Habitat Planner image cache
     (also Serebii-derived; useful for slug-named Pokémon icons)
     https://github.com/SergioPalGam/Pokopia-Habitat-Planner/releases
     → icons/pokemon/{slug}.png and icons/items/{slug}.png
"""

from __future__ import annotations

import argparse
import io
import re
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POKEMON_DIR = ROOT / "icons" / "pokemon"
POKEMON_BY_NUMBER_DIR = POKEMON_DIR / "by_number"
ITEMS_DIR = ROOT / "icons" / "items"

SEREBII = "https://www.serebii.net"
HABITAT_PLANNER_CACHE_URL = (
    "https://github.com/SergioPalGam/Pokopia-Habitat-Planner/releases/"
    "download/v0.1.0-beta/Pokopia-Habitat-Planner-Image-Cache-v0.1.0.zip"
)
UA = "pokopia-data-collector/1.0 (+https://github.com/pomodorozhong/pokopia)"

FAVORITE_SLUGS = [
    "blockystuff",
    "cleanliness",
    "colorfulstuff",
    "complicatedstuff",
    "construction",
    "containers",
    "cutestuff",
    "electronics",
    "exercise",
    "fabric",
    "garbage",
    "gatherings",
    "glassstuff",
    "groupactivities",
    "hardstuff",
    "healing",
    "lettersandwords",
    "lookslikefood",
    "lotsofdirt",
    "lotsoffire",
    "lotsofnature",
    "lotsofwater",
    "luxury",
    "metalstuff",
    "nicebreezes",
    "noisystuff",
    "oceanvibes",
    "playspaces",
    "prettyflowers",
    "rides",
    "roundstuff",
    "sharpstuff",
    "shinystuff",
    "slenderobjects",
    "softstuff",
    "spinningstuff",
    "spookystuff",
    "stonestuff",
    "strangestuff",
    "symbols",
    "watchingstuff",
    "wobblystuff",
    "woodenstuff",
]


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.read()


def fetch_text(url: str) -> str:
    return fetch(url).decode("utf-8", "ignore")


def download_file(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True
    try:
        data = fetch(url)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        raise
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return True


def seed_from_habitat_planner_cache() -> None:
    print(f"Seeding from Habitat Planner cache:\n  {HABITAT_PLANNER_CACHE_URL}")
    raw = fetch(HABITAT_PLANNER_CACHE_URL)
    counts = {"pokemon": 0, "items": 0}
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        for name in zf.namelist():
            if name.endswith("/"):
                continue
            if name.startswith("image_cache/pokemon/") and name.endswith(".png"):
                dest = POKEMON_DIR / Path(name).name
                if not dest.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(zf.read(name))
                    counts["pokemon"] += 1
            elif name.startswith("image_cache/items/") and name.endswith(".png"):
                dest = ITEMS_DIR / Path(name).name
                if not dest.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(zf.read(name))
                    counts["items"] += 1
    print(f"  seeded pokemon={counts['pokemon']} items={counts['items']}")


def download_numbered_pokemon() -> None:
    print("Downloading numbered Serebii small Pokémon icons…")
    html = fetch_text(f"{SEREBII}/pokemonpokopia/availablepokemon.shtml")
    numbers = sorted(set(re.findall(r"/pokemonpokopia/pokemon/small/(\d+)\.png", html)))
    POKEMON_BY_NUMBER_DIR.mkdir(parents=True, exist_ok=True)
    ok = 0
    for num in numbers:
        url = f"{SEREBII}/pokemonpokopia/pokemon/small/{num}.png"
        if download_file(url, POKEMON_BY_NUMBER_DIR / f"{num}.png"):
            ok += 1
        time.sleep(0.04)
    print(f"  {ok}/{len(numbers)} → {POKEMON_BY_NUMBER_DIR}")


def discover_item_slugs() -> list[str]:
    slugs: set[str] = set()
    pages = [f"{SEREBII}/pokemonpokopia/items.shtml"]
    pages += [f"{SEREBII}/pokemonpokopia/favorites/{slug}.shtml" for slug in FAVORITE_SLUGS]
    for url in pages:
        try:
            html = fetch_text(url)
        except urllib.error.HTTPError as exc:
            print(f"  skip {url}: HTTP {exc.code}")
            continue
        found = re.findall(r"/pokemonpokopia/items/([a-z0-9_-]+)\.png", html, flags=re.I)
        slugs.update(name.lower() for name in found)
        time.sleep(0.1)
    return sorted(slugs)


def download_items() -> None:
    print("Downloading Serebii item icons…")
    slugs = discover_item_slugs()
    ITEMS_DIR.mkdir(parents=True, exist_ok=True)
    ok = 0
    for slug in slugs:
        url = f"{SEREBII}/pokemonpokopia/items/{slug}.png"
        if download_file(url, ITEMS_DIR / f"{slug}.png"):
            ok += 1
        time.sleep(0.04)
    print(f"  {ok}/{len(slugs)} → {ITEMS_DIR}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-cache-seed",
        action="store_true",
        help="Do not seed from Habitat Planner image cache",
    )
    args = parser.parse_args()

    POKEMON_DIR.mkdir(parents=True, exist_ok=True)
    ITEMS_DIR.mkdir(parents=True, exist_ok=True)

    if not args.skip_cache_seed:
        seed_from_habitat_planner_cache()
    download_numbered_pokemon()
    download_items()


if __name__ == "__main__":
    main()
