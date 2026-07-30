#!/usr/bin/env python3
"""
Download Pokopia Pokémon and item icons.

Pokémon icons (by English name only — no numbered duplicates)
  Source: Serebii.net Pokémon Pokopia
    - Available list: https://www.serebii.net/pokemonpokopia/availablepokemon.shtml
    - Event list:     https://www.serebii.net/pokemonpokopia/eventpokedex.shtml
    - Image files:    https://www.serebii.net/pokemonpokopia/pokemon/small/{file}.png
  Saved as: icons/pokemon/{sanitized_english_name}.png
    e.g. Bulbasaur → bulbasaur.png, Ho-Oh → hooh.png,
         Paldean Wooper → paldeanwooper.png, Farfetch'd → farfetchd.png

Item icons (unique Infipoke catalog entries)
  Primary source: Infipoke Pokopia Items
    - Page / NUXT data: https://infipoke.com/game/pokopia/items
    - Images: https://infipoke.com/img/pokopia/items/{slug}.webp
  Fallback source: Serebii item PNGs
    - https://www.serebii.net/pokemonpokopia/items/{slug}.png
    - plus a small alias map for known Infipoke/Serebii slug mismatches
  Saved as: icons/items/{slug}.png  (WebP converted to PNG when needed)
"""

from __future__ import annotations

import argparse
import io
import json
import re
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
POKEMON_DIR = ROOT / "icons" / "pokemon"
ITEMS_DIR = ROOT / "icons" / "items"

SEREBII = "https://www.serebii.net"
AVAILABLE_URL = f"{SEREBII}/pokemonpokopia/availablepokemon.shtml"
EVENT_URL = f"{SEREBII}/pokemonpokopia/eventpokedex.shtml"
INFIPOKE_ITEMS_URL = "https://infipoke.com/game/pokopia/items"
INFIPOKE_ITEM_IMAGE = "https://infipoke.com/img/pokopia/items/{slug}.webp"
SEREBII_ITEM_IMAGE = f"{SEREBII}/pokemonpokopia/items/{{slug}}.png"

UA = "pokopia-data-collector/1.0 (+https://github.com/pomodorozhong/pokopia)"

# Infipoke slug → alternate Serebii / CDN filename stems to try.
ITEM_SLUG_ALIASES: dict[str, list[str]] = {
    "speedposter": ["speedyposter"],
}

ROW_RE = re.compile(
    r'<td class="cen">#(\d+)</td>\s*'
    r'<td class="cen"><a href="/pokemonpokopia/pokedex/([^"]+)\.shtml">'
    r'<img src="(/pokemonpokopia/pokemon/small/[^"]+)"[^>]*></a></td>\s*'
    r'<td class="cen"><a href="/pokemonpokopia/pokedex/[^"]+\.shtml">'
    r"<u>([^<]+)</u></a></td>",
    re.S,
)


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.read()


def fetch_text(url: str) -> str:
    return fetch(url).decode("utf-8", "ignore")


def sanitize_name(name: str) -> str:
    """English display name → filename stem (letters/digits only, lower-case)."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def parse_pokemon_rows(html: str) -> list[tuple[str, str, str]]:
    """Return unique (name_key, display_name, image_path) rows."""
    seen: set[str] = set()
    rows: list[tuple[str, str, str]] = []
    for _num, _slug, image_path, display_name in ROW_RE.findall(html):
        key = sanitize_name(display_name)
        if not key or key in seen:
            continue
        seen.add(key)
        rows.append((key, display_name, image_path))
    return rows


def download_pokemon_icons(force: bool = False) -> None:
    print("Fetching Serebii available + event Pokémon lists…")
    available = parse_pokemon_rows(fetch_text(AVAILABLE_URL))
    event = parse_pokemon_rows(fetch_text(EVENT_URL))
    by_key = {key: (name, path) for key, name, path in available}
    for key, name, path in event:
        by_key.setdefault(key, (name, path))

    print(f"  {len(available)} available + {len(event)} event → {len(by_key)} unique")

    POKEMON_DIR.mkdir(parents=True, exist_ok=True)

    by_number = POKEMON_DIR / "by_number"
    if by_number.exists():
        shutil.rmtree(by_number)
        print(f"  removed {by_number}")

    keep = set(by_key)
    removed = 0
    for path in POKEMON_DIR.glob("*.png"):
        if path.stem not in keep:
            path.unlink()
            removed += 1
    if removed:
        print(f"  removed {removed} stale Pokémon icon(s)")

    ok = 0
    for key, (display_name, image_path) in sorted(by_key.items()):
        dest = POKEMON_DIR / f"{key}.png"
        if dest.exists() and dest.stat().st_size > 0 and not force:
            ok += 1
            continue
        url = f"{SEREBII}{image_path}"
        try:
            dest.write_bytes(fetch(url))
            ok += 1
        except urllib.error.HTTPError as exc:
            print(f"  FAIL {display_name} ({key}): HTTP {exc.code} {url}")
        time.sleep(0.03)
    print(f"  Pokémon icons ready: {ok}/{len(by_key)} → {POKEMON_DIR}")


def load_infipoke_item_slugs() -> list[str]:
    html = fetch_text(INFIPOKE_ITEMS_URL)
    match = re.search(
        r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', html, re.S
    )
    if not match:
        raise RuntimeError("No __NUXT_DATA__ on Infipoke items page")
    data = json.loads(match.group(1))

    def resolve(idx, depth: int = 0):
        if depth > 12:
            return idx
        if not isinstance(idx, int) or idx < 0 or idx >= len(data):
            return idx
        value = data[idx]
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, list):
            return [resolve(item, depth + 1) for item in value]
        if isinstance(value, dict):
            return {key: resolve(item, depth + 1) for key, item in value.items()}
        return value

    slugs: list[str] = []
    seen: set[str] = set()
    for item in data:
        if not isinstance(item, dict) or "slug" not in item or "name" not in item:
            continue
        slug = resolve(item["slug"])
        if not isinstance(slug, str) or not slug or slug in seen:
            continue
        seen.add(slug)
        slugs.append(slug)
    return slugs


def _save_image_bytes(raw: bytes, dest: Path, source_url: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if source_url.endswith(".webp") or raw[:4] == b"RIFF":
        Image.open(io.BytesIO(raw)).convert("RGBA").save(dest, format="PNG")
    else:
        dest.write_bytes(raw)


def _candidate_item_urls(slug: str) -> list[str]:
    aliases = ITEM_SLUG_ALIASES.get(slug, [])
    stems = [slug, *aliases]
    urls: list[str] = []
    for stem in stems:
        urls.append(INFIPOKE_ITEM_IMAGE.format(slug=stem))
        urls.append(INFIPOKE_ITEM_IMAGE.format(slug=urllib.parse.quote(stem, safe="")))
        urls.append(SEREBII_ITEM_IMAGE.format(slug=stem))
        urls.append(SEREBII_ITEM_IMAGE.format(slug=urllib.parse.quote(stem, safe="")))
    # de-dupe preserving order
    seen: set[str] = set()
    out: list[str] = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def _download_one_item(slug: str, force: bool) -> tuple[str, bool, str]:
    dest = ITEMS_DIR / f"{slug}.png"
    if dest.exists() and dest.stat().st_size > 0 and not force:
        return slug, True, "exists"
    last_err = "no candidates"
    for url in _candidate_item_urls(slug):
        try:
            raw = fetch(url)
            _save_image_bytes(raw, dest, url)
            return slug, True, url
        except urllib.error.HTTPError as exc:
            last_err = f"HTTP {exc.code}"
            continue
        except Exception as exc:  # noqa: BLE001
            last_err = str(exc)
            continue
    return slug, False, last_err


def download_item_icons(force: bool = False, workers: int = 12) -> None:
    print("Fetching Infipoke item catalog…")
    slugs = load_infipoke_item_slugs()
    print(f"  {len(slugs)} unique item slugs")
    ITEMS_DIR.mkdir(parents=True, exist_ok=True)

    keep = set(slugs)
    removed = 0
    for path in ITEMS_DIR.glob("*.png"):
        if path.stem not in keep:
            path.unlink()
            removed += 1
    if removed:
        print(f"  removed {removed} stale item icon(s)")

    ok = 0
    failed: list[str] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_download_one_item, slug, force) for slug in slugs]
        for i, fut in enumerate(as_completed(futures), 1):
            slug, success, detail = fut.result()
            if success:
                ok += 1
            else:
                failed.append(f"{slug}: {detail}")
            if i % 200 == 0:
                print(f"  progress {i}/{len(slugs)} ok={ok}")
    print(f"  Item icons ready: {ok}/{len(slugs)} → {ITEMS_DIR}")
    if failed:
        print(f"  failures ({len(failed)}):")
        for line in failed[:40]:
            print(f"    {line}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Re-download existing files")
    parser.add_argument("--pokemon-only", action="store_true")
    parser.add_argument("--items-only", action="store_true")
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()

    do_pokemon = not args.items_only
    do_items = not args.pokemon_only
    if do_pokemon:
        download_pokemon_icons(force=args.force)
    if do_items:
        download_item_icons(force=args.force, workers=args.workers)


if __name__ == "__main__":
    main()
