#!/usr/bin/env python3
"""
Build JP / EN / zh_TW localization JSON for Pokopia names.

Sources:
  - Pokémon names (en/ja/zh_tw): Infipoke Pokédex NUXT payload
    https://infipoke.com/zh-hant/game/pokopia/pokedex
  - Item names (en/ja) + categories: Infipoke Items NUXT payload
    https://infipoke.com/game/pokopia/items
  - Item / category names (zh_tw): Pokopia GamerTW wiki
    https://pokopia.gamertw.com/zh-TW/item
  - Favorite categories (en/ja): naru-pokopia-zukan Google Sheets CSV
    https://github.com/naru08-creator/naru-pokopia-zukan
  - Favorite categories (zh_tw): Pokopia GamerTW wiki
    https://pokopia.gamertw.com/zh-TW/favorite
  - Specialties / ideal habitats (en/ja): same naru Google Sheets
  - Specialties (zh_tw): Infipoke skills page labels
  - Ideal habitats (zh_tw): conventional Traditional Chinese game terms
    aligned to naru EN habitat keys
"""

from __future__ import annotations

import csv
import io
import json
import re
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "localization.json"

UA = "pokopia-data-collector/1.0 (+https://github.com/pomodorozhong/pokopia)"
# GamerTW sits behind Cloudflare; a browser-like UA is required.
UA_BROWSER = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

INFIPOKE_POKEDEX = "https://infipoke.com/zh-hant/game/pokopia/pokedex"
INFIPOKE_ITEMS = "https://infipoke.com/game/pokopia/items"
INFIPOKE_SKILLS_ZH = "https://infipoke.com/zh-hant/game/pokopia/skills"

NARU_SHEET_ID = "1KLawCBmZsMP-seDsEQu5pFUf4_NOIR6wbu3TqvbDXmk"
NARU_JP_CSV = (
    f"https://docs.google.com/spreadsheets/d/{NARU_SHEET_ID}/"
    "gviz/tq?tqx=out:csv&gid=0&range=A:F"
)
NARU_EN_CSV = (
    f"https://docs.google.com/spreadsheets/d/{NARU_SHEET_ID}/"
    "gviz/tq?tqx=out:csv&gid=893275471&range=A:F"
)
NARU_REPO = "https://github.com/naru08-creator/naru-pokopia-zukan"

GAMERTW_FAVORITES = "https://pokopia.gamertw.com/zh-TW/favorite"
GAMERTW_ITEMS_ZH = "https://pokopia.gamertw.com/zh-TW/item"
GAMERTW_ITEMS_EN = "https://pokopia.gamertw.com/item"

# EN favorite (naru / Serebii) -> zh_TW (gamertw slug pages / listing)
FAVORITE_ZH_TW = {
    "Blocky stuff": "方方的",
    "Cleanliness": "整潔的",
    "Colorful stuff": "色彩繽紛的",
    "Complicated stuff": "艱深難懂的",
    "Construction": "建設",
    "Containers": "容器",
    "Cute stuff": "可愛的",
    "Electronics": "以電力驅動的",
    "Exercise": "訓練用的",
    "Fabric": "布製的",
    "Garbage": "垃圾",
    "Gatherings": "集聚在一起的",
    "Glass stuff": "有玻璃的",
    "Group activities": "大家一起用的",
    "Hard stuff": "堅硬的",
    "Healing": "能治癒傷口的",
    "Letters and words": "有文字的",
    "Looks like food": "像食物的",
    "Lots of dirt": "能感受土的",
    "Lots of fire": "能感受火的",
    "Lots of nature": "能感受大自然的",
    "Lots of water": "能感受水的",
    "Luxury": "豪華的",
    "Metal stuff": "金屬的",
    "Nice breezes": "能感受風的",
    "Noisy stuff": "會發出聲響的",
    "Ocean vibes": "能感受海的",
    "Play spaces": "遊戲區",
    "Pretty flowers": "花朵綻放的",
    "Rides": "交通工具",
    "Round stuff": "圓滾滾的",
    "Sharp stuff": "尖尖的",
    "Shiny stuff": "閃亮亮的",
    "Slender objects": "細長的",
    "Soft stuff": "柔軟的",
    "Spinning stuff": "會旋轉的",
    "Spooky stuff": "詭異的",
    "Stone stuff": "石製的",
    "Strange stuff": "奇妙的",
    "Symbols": "象徵",
    "Watching stuff": "觀賞用的",
    "Wobbly stuff": "會搖晃的",
    "Wooden stuff": "木製的",
    "Sweet flavors": "甜甜的",
    "Sour flavors": "酸酸的",
    "Spicy flavors": "辣辣的",
    "Bitter flavors": "苦苦的",
    "Dry flavors": "澀澀的",
}

# Infipoke skill id -> naru EN specialty (and Pokopia.csv wording variants)
SKILL_TO_SPECIALTY_EN = {
    "farming": "Grow",
    "watering": "Water",
    "fire": "Burn",
    "flying": "Fly",
    "building": "Build",
    "trampling": "Bulldoze",
    "crushing": "Crush",
    "logging": "Chop",
    "trading": "Trade",
    "cheering": "Hype",
    "scattering": "Litter",
    "sorting": "Sort",
    "recycling": "Recycle",
    "power": "Generate",
    "finding": "Search",
    "teleport": "Teleport",
    "honey": "Gather Honey",
    "painting": "Paint",
    "dreamland": "Dream Island",
    "dj": "DJ",
    "identify": "Appraise",
    "storing": "Storage",
    "explosion": "Explode",
    "party": "Party",
    "rare-item": "Rarify",
    "craftsman": "Engineer",
    "collector": "Collect",
    "yawning": "Yawn",
    "transform": "Transform",
    "unknown": "???",
}

IDEAL_HABITAT_ZH_TW = {
    "Bright": "明亮",
    "Cool": "涼爽",
    "Dark": "陰暗",
    "Dry": "乾燥",
    "Humid": "濕潤",
    "Warm": "溫暖",
}

# Manual EN→JA specialty map (naru sheet / in-game JP terms).
# Used to fill gaps when per-row list alignment fails.
SPECIALTY_EN_TO_JA = {
    "Appraise": "かんてい",
    "Build": "けんちく",
    "Bulldoze": "じならし",
    "Burn": "もやす",
    "Chop": "きをきる",
    "Collect": "コレクター",
    "Crush": "つぶす",
    "DJ": "DJ",
    "Dream Island": "ゆめしま",
    "Eat": "くいしんぼ",
    "Engineer": "しょくにん",
    "Explode": "ばくはつ",
    "Fly": "そらをとぶ",
    "Gather": "しわける",
    "Gather Honey": "ミツあつめ",
    "Generate": "はつでん",
    "Grow": "さいばい",
    "Hype": "もりあげる",
    "Illuminate": "はっこう",
    "Litter": "ちらかす",
    "Paint": "ペイント",
    "Party": "パーティー",
    "Rarify": "レアもの",
    "Recycle": "リサイクル",
    "Search": "さがしもの",
    "Sort": "ぶんるい",
    "Storage": "しゅうのう",
    "Teleport": "テレポート",
    "Trade": "とりひき",
    "Transform": "へんしん",
    "Water": "うるおす",
    "Yawn": "あくび",
    "???": "不明",
}

SPECIALTY_EN_TO_ZH_TW = {
    "Appraise": "鑑定",
    "Build": "建築",
    "Bulldoze": "整地",
    "Burn": "燃燒",
    "Chop": "伐木",
    "Collect": "收藏家",
    "Crush": "粉碎",
    "DJ": "DJ",
    "Dream Island": "夢之島",
    "Eat": "貪吃",
    "Engineer": "工匠",
    "Explode": "爆炸",
    "Fly": "飛翔",
    "Gather": "分類",
    "Gather Honey": "採蜜",
    "Generate": "發電",
    "Grow": "栽培",
    "Hype": "炒熱氣氛",
    "Illuminate": "發光",
    "Litter": "散佈",
    "Paint": "彩繪",
    "Party": "開派對",
    "Rarify": "稀有物",
    "Recycle": "回收",
    "Search": "尋物",
    "Sort": "分類",
    "Storage": "收納",
    "Teleport": "瞬間移動",
    "Trade": "交易",
    "Transform": "變身",
    "Water": "潤澤",
    "Yawn": "哈欠",
    "???": "不明",
}

ITEM_CATEGORY_EN_TO_KEY = {
    "Materials": "materials",
    "Food": "food",
    "Furniture": "furniture",
    "Misc.": "misc",
    "Outdoor": "outdoor",
    "Utilities": "utilities",
    "Nature": "nature",
    "Buildings": "buildings",
    "Blocks": "blocks",
    "Kits": "kits",
    "Key Items": "key_items",
    "Other": "other",
    "Lost Relics (Large)": "lost_relics_large",
    "Lost Relics (Small)": "lost_relics_small",
    "Fossils": "fossils",
}

# GamerTW zh-TW item filter labels from https://pokopia.gamertw.com/zh-TW/item
GAMERTW_CATEGORY_ZH_TW = {
    "materials": "材料",
    "food": "食物",
    "furniture": "家具",
    "misc": "雜物",
    "outdoor": "戶外",
    "utilities": "設備",
    "nature": "自然",
    "buildings": "建築",
    "blocks": "方塊",
    "kits": "套件",
    "key_items": "關鍵道具",
    "other": "其他",
    "lost_relics_large": "遺跡寶物(大)",
    "lost_relics_small": "遺跡寶物(小)",
    "fossils": "化石",
}


def fetch(url: str, user_agent: str = UA) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def fetch_text(url: str, user_agent: str = UA) -> str:
    return fetch(url, user_agent=user_agent).decode("utf-8", "ignore")


def load_nuxt(url: str) -> list:
    html = fetch_text(url)
    match = re.search(
        r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', html, re.S
    )
    if not match:
        raise RuntimeError(f"No __NUXT_DATA__ in {url}")
    return json.loads(match.group(1))


def resolve(data: list, idx, depth: int = 0):
    if depth > 12:
        return idx
    if not isinstance(idx, int) or idx < 0 or idx >= len(data):
        return idx
    value = data[idx]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [resolve(data, item, depth + 1) for item in value]
    if isinstance(value, dict):
        return {key: resolve(data, item, depth + 1) for key, item in value.items()}
    return value


def normalize_key(text: str) -> str:
    text = text.strip().lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def alnum_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.strip().lower())


def normalize_en_name(text: str) -> str:
    text = text.lower().replace("&", " and ")
    text = text.replace("’", "'").replace("é", "e").replace("♪", "")
    text = text.replace("poké", "poke")
    return alnum_key(text)


def split_csv_list(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def extract_gamertw_items(html: str) -> list[dict]:
    """Parse item cards from GamerTW Next.js RSC payload."""
    pattern = re.compile(
        r'\{\\"id\\":\\"([^\\"]+)\\"'
        r',\\"category\\":\\"([^\\"]+)\\"'
        r',\\"imageSlug\\":\\"([^\\"]+)\\"'
        r'.*?\\"displayName\\":\\"([^\\"]*)\\"',
        re.S,
    )
    items: dict[str, dict] = {}
    for match in pattern.finditer(html):
        item_id = match.group(1)
        items.setdefault(
            item_id,
            {
                "id": item_id,
                "category": match.group(2),
                "imageSlug": match.group(3),
                "displayName": match.group(4),
            },
        )
    if not items:
        raise RuntimeError("No GamerTW items found in page payload")
    return list(items.values())


def load_gamertw_item_names() -> dict:
    """Fetch GamerTW EN + zh-TW item payloads for later Infipoke slug matching."""
    zh_items = extract_gamertw_items(fetch_text(GAMERTW_ITEMS_ZH, user_agent=UA_BROWSER))
    en_items = extract_gamertw_items(fetch_text(GAMERTW_ITEMS_EN, user_agent=UA_BROWSER))
    en_by_id = {item["id"]: item for item in en_items}
    zh_by_id = {item["id"]: item for item in zh_items}
    if set(en_by_id) != set(zh_by_id):
        raise RuntimeError("GamerTW EN/ZH item id sets differ")
    return {
        "zh_by_id": zh_by_id,
        "en_by_id": en_by_id,
    }


def apply_gamertw_item_names(items: dict, gamertw: dict) -> dict:
    """
    Attach zh_tw names from GamerTW onto Infipoke item entries.

    Matching priority against Infipoke catalog slugs:
      1. GamerTW id with hyphens removed
      2. Unique imageSlug
      3. Alphanumeric equivalence of id / imageSlug
      4. Exact / normalized English displayName (EN GamerTW page)
    Already-matched Infipoke slugs are skipped so generic EN labels
    (e.g. "Leaf") do not steal more specific GamerTW ids.
    """
    zh_by_id: dict = gamertw["zh_by_id"]
    en_by_id: dict = gamertw["en_by_id"]

    by_imageslug: dict[str, list[str]] = defaultdict(list)
    for item_id, item in zh_by_id.items():
        by_imageslug[item["imageSlug"]].append(item_id)

    en_exact: dict[str, list[str]] = defaultdict(list)
    en_norm: dict[str, list[str]] = defaultdict(list)
    alnum_to_slugs: dict[str, list[str]] = defaultdict(list)
    for slug, entry in items.items():
        en_name = entry.get("en", "")
        en_exact[en_name].append(slug)
        en_norm[normalize_en_name(en_name)].append(slug)
        alnum_to_slugs[alnum_key(slug)].append(slug)

    matched: dict[str, str] = {}
    methods: Counter = Counter()
    unmatched_gamertw: list[str] = []

    for item_id, zh_item in zh_by_id.items():
        en_item = en_by_id[item_id]
        en_name = en_item["displayName"]
        image_slug = zh_item["imageSlug"]
        zh_name = zh_item["displayName"]
        slug = None
        method = None

        id_slug = item_id.replace("-", "")
        if id_slug in items and id_slug not in matched:
            slug, method = id_slug, "id"
        elif (
            image_slug in items
            and image_slug not in matched
            and len(by_imageslug[image_slug]) == 1
        ):
            slug, method = image_slug, "imageslug_unique"
        else:
            for key, label in (
                (alnum_key(item_id), "alnum_id"),
                (alnum_key(image_slug), "alnum_imageslug"),
            ):
                hits = [s for s in alnum_to_slugs.get(key, []) if s not in matched]
                if len(hits) == 1:
                    slug, method = hits[0], label
                    break
            if slug is None:
                hits = [s for s in en_exact.get(en_name, []) if s not in matched]
                if len(hits) == 1:
                    slug, method = hits[0], "en_exact"
                else:
                    hits = [
                        s
                        for s in en_norm.get(normalize_en_name(en_name), [])
                        if s not in matched
                    ]
                    if len(hits) == 1:
                        slug, method = hits[0], "en_norm"
                    elif (
                        image_slug in items
                        and image_slug not in matched
                        and normalize_en_name(items[image_slug].get("en", ""))
                        == normalize_en_name(en_name)
                    ):
                        slug, method = image_slug, "imageslug_en"

        if slug:
            matched[slug] = zh_name
            items[slug]["zh_tw"] = zh_name
            methods[method] += 1
        else:
            unmatched_gamertw.append(item_id)

    missing_local = sorted(slug for slug in items if "zh_tw" not in items[slug])
    return {
        "matched": len(matched),
        "methods": dict(methods),
        "unmatched_gamertw_ids": unmatched_gamertw,
        "missing_local_slugs": missing_local,
    }


def align_token_maps(en_rows: list[dict], jp_rows: list[dict], en_field: str, jp_field: str):
    """Majority-vote EN->JA map by aligning same-index lists per Pokémon row."""
    votes: dict[str, Counter] = defaultdict(Counter)
    by_no_jp = {row["No."].strip(): row for row in jp_rows}
    for en_row in en_rows:
        jp_row = by_no_jp.get(en_row["No."].strip())
        if not jp_row:
            continue
        en_vals = split_csv_list(en_row[en_field])
        jp_vals = split_csv_list(jp_row[jp_field])
        if len(en_vals) != len(jp_vals):
            continue
        for en_val, jp_val in zip(en_vals, jp_vals):
            votes[en_val][jp_val] += 1
    return {en: counter.most_common(1)[0][0] for en, counter in votes.items()}


def parse_naru_csv(text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(text)))


def build_pokemon(data: list) -> dict:
    pokemon = {}
    for item in data:
        if not isinstance(item, dict) or "pokopiaNo" not in item or "name_zh_tw" not in item:
            continue
        pokopia_no = resolve(data, item["pokopiaNo"])
        slug = resolve(data, item["name"])
        name_ja = resolve(data, item["name_ja"])
        name_zh_tw = resolve(data, item["name_zh_tw"])
        if not isinstance(pokopia_no, int) or not isinstance(slug, str):
            continue
        pokemon[f"{pokopia_no:03d}"] = {
            "en": " ".join(part.capitalize() for part in slug.split("-")),
            "ja": name_ja,
            "zh_tw": name_zh_tw,
            "slug": slug,
        }
    return dict(sorted(pokemon.items(), key=lambda kv: int(kv[0])))


def build_items(data: list) -> tuple[dict, dict]:
    items = {}
    for item in data:
        if not isinstance(item, dict) or "slug" not in item or "name" not in item:
            continue
        slug = resolve(data, item["slug"])
        name_en = resolve(data, item["name"])
        name_ja = resolve(data, item.get("name_ja")) if "name_ja" in item else None
        name_zh = resolve(data, item.get("name_zh")) if "name_zh" in item else None
        category = resolve(data, item.get("category")) if "category" in item else None
        if not isinstance(slug, str) or not isinstance(name_en, str):
            continue
        entry = {"en": name_en}
        if isinstance(name_ja, str) and name_ja:
            entry["ja"] = name_ja
        if isinstance(name_zh, str) and name_zh:
            entry["zh"] = name_zh  # Infipoke Simplified Chinese (traceability)
        if isinstance(category, str) and category:
            entry["category"] = category
        items[slug] = entry

    # Category EN/JA from Infipoke; zh_tw from GamerTW zh-TW item filters.
    category_i18n = {
        "materials": {"en": "Materials", "ja": "素材", "zh_tw": GAMERTW_CATEGORY_ZH_TW["materials"]},
        "food": {"en": "Food", "ja": "食べ物", "zh_tw": GAMERTW_CATEGORY_ZH_TW["food"]},
        "furniture": {"en": "Furniture", "ja": "家具", "zh_tw": GAMERTW_CATEGORY_ZH_TW["furniture"]},
        "misc": {"en": "Misc.", "ja": "雑貨", "zh_tw": GAMERTW_CATEGORY_ZH_TW["misc"]},
        "outdoor": {"en": "Outdoor", "ja": "屋外", "zh_tw": GAMERTW_CATEGORY_ZH_TW["outdoor"]},
        "utilities": {"en": "Utilities", "ja": "設備", "zh_tw": GAMERTW_CATEGORY_ZH_TW["utilities"]},
        "nature": {"en": "Nature", "ja": "自然", "zh_tw": GAMERTW_CATEGORY_ZH_TW["nature"]},
        "buildings": {"en": "Buildings", "ja": "建物", "zh_tw": GAMERTW_CATEGORY_ZH_TW["buildings"]},
        "blocks": {"en": "Blocks", "ja": "ブロック", "zh_tw": GAMERTW_CATEGORY_ZH_TW["blocks"]},
        "kits": {"en": "Kits", "ja": "キット", "zh_tw": GAMERTW_CATEGORY_ZH_TW["kits"]},
        "key_items": {"en": "Key Items", "ja": "大事なもの", "zh_tw": GAMERTW_CATEGORY_ZH_TW["key_items"]},
        "other": {"en": "Other", "ja": "その他", "zh_tw": GAMERTW_CATEGORY_ZH_TW["other"]},
        "lost_relics_large": {
            "en": "Lost Relics (Large)",
            "ja": "失われた遺物 (大)",
            "zh_tw": GAMERTW_CATEGORY_ZH_TW["lost_relics_large"],
        },
        "lost_relics_small": {
            "en": "Lost Relics (Small)",
            "ja": "失われた遺物 (小)",
            "zh_tw": GAMERTW_CATEGORY_ZH_TW["lost_relics_small"],
        },
        "fossils": {"en": "Fossils", "ja": "化石", "zh_tw": GAMERTW_CATEGORY_ZH_TW["fossils"]},
    }
    categories = dict(sorted(category_i18n.items()))
    return dict(sorted(items.items())), categories


def extract_skill_labels(url: str) -> dict[str, str]:
    html = fetch_text(url)
    skill_ids = list(SKILL_TO_SPECIALTY_EN.keys())
    labels: dict[str, str] = {}
    # Prefer ordered id list then nearby CJK/English labels in filter strip
    # Capture sequences like >栽培< near skill id occurrences in markup.
    for skill_id in skill_ids:
        # Find occurrences not inside long script blobs if possible
        for match in re.finditer(re.escape(skill_id), html):
            window = html[match.end() : match.end() + 400]
            label_match = re.search(r">([^<>{}]{1,40})</", window)
            if not label_match:
                continue
            label = label_match.group(1).strip()
            if not label or label.lower() == skill_id:
                continue
            if "http" in label or "&amp;" in label or label.startswith("+"):
                continue
            # Skip game-title false positives for "fire"
            if skill_id == "fire" and ("Leaf" in label or "リーフ" in label or "葉綠" in label or "叶绿" in label):
                continue
            labels[skill_id] = label
            break
    return labels


def build_favorites(en_rows: list[dict], jp_rows: list[dict]) -> dict:
    en_to_ja = align_token_maps(en_rows, jp_rows, "Favorites", "好きなもの")
    favorites = {}
    for en_name, ja_name in sorted(en_to_ja.items(), key=lambda kv: kv[0].lower()):
        if en_name in {"None", "なし"} or ja_name in {"なし", "None"}:
            continue
        key = normalize_key(en_name)
        favorites[key] = {
            "en": en_name,
            "ja": ja_name,
            "zh_tw": FAVORITE_ZH_TW.get(en_name, FAVORITE_ZH_TW.get(en_name.title(), "")),
        }
        # Case-insensitive zh_tw lookup
        if not favorites[key]["zh_tw"]:
            for en_key, zh in FAVORITE_ZH_TW.items():
                if en_key.lower() == en_name.lower():
                    favorites[key]["zh_tw"] = zh
                    break
        if not favorites[key]["zh_tw"]:
            del favorites[key]["zh_tw"]
    return favorites


def build_specialties(en_rows: list[dict], jp_rows: list[dict], zh_labels: dict[str, str]) -> dict:
    en_to_ja = align_token_maps(en_rows, jp_rows, "Specialties", "得意なこと")
    en_to_ja = {**en_to_ja, **SPECIALTY_EN_TO_JA}

    en_names = set(en_to_ja) | set(SPECIALTY_EN_TO_JA) | set(SKILL_TO_SPECIALTY_EN.values())
    for row in en_rows:
        en_names.update(split_csv_list(row["Specialties"]))

    specialties = {}
    for en_name in sorted(en_names, key=lambda s: s.lower()):
        key = "unknown" if en_name in {"???", "不明"} else normalize_key(en_name)
        entry = {"en": en_name}
        ja = en_to_ja.get(en_name) or SPECIALTY_EN_TO_JA.get(en_name)
        if ja:
            entry["ja"] = ja
        zh = SPECIALTY_EN_TO_ZH_TW.get(en_name)
        if not zh:
            for skill_id, mapped_en in SKILL_TO_SPECIALTY_EN.items():
                if mapped_en == en_name and skill_id in zh_labels:
                    zh = zh_labels[skill_id]
                    break
        if zh:
            entry["zh_tw"] = zh
        specialties[key] = entry
    return dict(sorted(specialties.items()))


def build_ideal_habitats(en_rows: list[dict], jp_rows: list[dict]) -> dict:
    en_to_ja = align_token_maps(en_rows, jp_rows, "Ideal Habitat", "好きな環境")
    habitats = {}
    for en_name, ja_name in sorted(en_to_ja.items(), key=lambda kv: kv[0].lower()):
        key = normalize_key(en_name)
        habitats[key] = {
            "en": en_name,
            "ja": ja_name,
            "zh_tw": IDEAL_HABITAT_ZH_TW.get(en_name, ""),
        }
        if not habitats[key]["zh_tw"]:
            del habitats[key]["zh_tw"]
    return habitats


def override_pokemon_english_from_naru(pokemon: dict, en_rows: list[dict]) -> None:
    """Prefer official English names from naru sheet when available."""
    for row in en_rows:
        no = row["No."].strip()
        name = row["Pokémon (EN)"].strip()
        if not no.isdigit() or not name:
            continue
        key = f"{int(no):03d}"
        if key in pokemon:
            pokemon[key]["en"] = name


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Fetching Infipoke Pokédex…")
    pokedex_data = load_nuxt(INFIPOKE_POKEDEX)
    pokemon = build_pokemon(pokedex_data)
    print(f"  {len(pokemon)} Pokémon")

    print("Fetching Infipoke items…")
    items_data = load_nuxt(INFIPOKE_ITEMS)
    items, item_categories = build_items(items_data)
    print(f"  {len(items)} items, {len(item_categories)} item categories")

    print("Fetching GamerTW zh-TW / EN item names…")
    gamertw = load_gamertw_item_names()
    zh_stats = apply_gamertw_item_names(items, gamertw)
    print(
        f"  zh_tw matched={zh_stats['matched']} "
        f"methods={zh_stats['methods']} "
        f"unmatched_gamertw={len(zh_stats['unmatched_gamertw_ids'])} "
        f"missing_local={len(zh_stats['missing_local_slugs'])}"
    )
    if zh_stats["missing_local_slugs"]:
        print(f"  missing local slugs: {zh_stats['missing_local_slugs']}")

    print("Fetching naru JP/EN CSV…")
    en_rows = parse_naru_csv(fetch_text(NARU_EN_CSV))
    jp_rows = parse_naru_csv(fetch_text(NARU_JP_CSV))
    override_pokemon_english_from_naru(pokemon, en_rows)

    print("Building favorites / specialties / habitats…")
    favorites = build_favorites(en_rows, jp_rows)
    zh_skill_labels = extract_skill_labels(INFIPOKE_SKILLS_ZH)
    specialties = build_specialties(en_rows, jp_rows, zh_skill_labels)
    ideal_habitats = build_ideal_habitats(en_rows, jp_rows)
    print(
        f"  favorites={len(favorites)} specialties={len(specialties)} "
        f"ideal_habitats={len(ideal_habitats)}"
    )

    payload = {
        "meta": {
            "locales": ["en", "ja", "zh_tw"],
            "sources": {
                "pokemon_names": {
                    "name": "Infipoke Pokopia Pokédex",
                    "url": INFIPOKE_POKEDEX,
                    "fields": "name (slug), name_ja, name_zh_tw",
                },
                "item_names": {
                    "name": "Infipoke Pokopia Items + Pokopia GamerTW wiki",
                    "infipoke_url": INFIPOKE_ITEMS,
                    "gamertw_zh_tw_url": GAMERTW_ITEMS_ZH,
                    "gamertw_en_url": GAMERTW_ITEMS_EN,
                    "fields": "Infipoke name/name_ja/name_zh; GamerTW displayName (zh_tw)",
                    "zh_tw_note": (
                        "zh_tw item names come from Pokopia GamerTW "
                        f"({GAMERTW_ITEMS_ZH}) displayName, matched to Infipoke "
                        "slugs via id/imageSlug/English name. Infipoke Simplified "
                        "Chinese is kept as 'zh' for traceability. No OpenCC."
                    ),
                    "zh_tw_match_stats": zh_stats,
                },
                "favorite_categories_en_ja": {
                    "name": "naru-pokopia-zukan Google Sheets",
                    "repo": NARU_REPO,
                    "en_csv": NARU_EN_CSV,
                    "ja_csv": NARU_JP_CSV,
                },
                "favorite_categories_zh_tw": {
                    "name": "Pokopia GamerTW wiki — 喜好",
                    "url": GAMERTW_FAVORITES,
                },
                "specialties_en_ja": {
                    "name": "naru-pokopia-zukan Google Sheets",
                    "repo": NARU_REPO,
                },
                "specialties_zh_tw": {
                    "name": "Infipoke Pokopia Skills",
                    "url": INFIPOKE_SKILLS_ZH,
                },
                "ideal_habitats_en_ja": {
                    "name": "naru-pokopia-zukan Google Sheets",
                    "repo": NARU_REPO,
                },
                "ideal_habitats_zh_tw": {
                    "name": "Conventional Traditional Chinese habitat terms",
                    "note": "Manual mapping for Bright/Cool/Dark/Dry/Humid/Warm",
                },
                "item_categories": {
                    "name": "Infipoke EN/JA labels + GamerTW zh-TW item filters",
                    "infipoke_url": INFIPOKE_ITEMS,
                    "gamertw_zh_tw_url": GAMERTW_ITEMS_ZH,
                },
            },
            "generated_by": "scripts/build_localization.py",
        },
        "pokemon": pokemon,
        "favorites": favorites,
        "specialties": specialties,
        "ideal_habitats": ideal_habitats,
        "item_categories": item_categories,
        "items": items,
    }

    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
