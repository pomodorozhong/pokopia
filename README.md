# pokopia

Tools and reference data for **Pokémon Pokopia**.

## Repository layout

| Path | Description |
|------|-------------|
| `data/Pokopia.csv` | Pokémon database (locations, habitats, favorites, specialties) |
| `data/localization.json` | `en` / `ja` / `zh_tw` names for Pokémon, favorites, specialties, habitats, items, and item categories |
| `icons/pokemon/` | Pokémon icons by English name (`bulbasaur.png`, `paldeanwooper.png`, …) |
| `icons/items/` | Item icons by catalog slug (`honey.png`, …) |
| `scripts/` | Scripts used to download / rebuild the datasets above |

## Data sources

All data and images here are fan-compiled from public community resources. This project is unofficial and not affiliated with Nintendo, The Pokémon Company, Game Freak, Creatures Inc., or the sites listed below.

### `data/Pokopia.csv`

- **Source:** [JEschete/PokopiaPlanning](https://github.com/JEschete/PokopiaPlanning) → [`reference/Pokopia.csv`](https://github.com/JEschete/PokopiaPlanning/blob/main/reference/Pokopia.csv)
- That dataset is scraped/compiled primarily from [Serebii — Pokémon Pokopia](https://www.serebii.net/pokemonpokopia/).
- Refresh: `python3 scripts/download_pokopia_csv.py`

### Icons (`icons/`)

Pokémon and item icons are downloaded by `scripts/download_icons.py`.

**Pokémon** (`icons/pokemon/{name}.png` — name only, no numbered copies)

- **Source:** [Serebii — Available Pokémon](https://www.serebii.net/pokemonpokopia/availablepokemon.shtml) and [Event Pokédex](https://www.serebii.net/pokemonpokopia/eventpokedex.shtml)
- Image files: `https://www.serebii.net/pokemonpokopia/pokemon/small/...`
- Filename = English display name with non-alphanumerics removed  
  (`Ho-Oh` → `hooh.png`, `Paldean Wooper` → `paldeanwooper.png`, `Farfetch'd` → `farfetchd.png`)

**Items** (`icons/items/{slug}.png`)

- **Primary source:** [Infipoke Pokopia Items](https://infipoke.com/game/pokopia/items)  
  Images: `https://infipoke.com/img/pokopia/items/{slug}.webp` (saved as PNG)
- **Fallback:** [Serebii Pokopia Items](https://www.serebii.net/pokemonpokopia/items.shtml)  
  `https://www.serebii.net/pokemonpokopia/items/{slug}.png`  
  (plus a small alias map in the script for known Infipoke/Serebii slug mismatches, e.g. `speedposter` → `speedyposter`)

Refresh: `python3 scripts/download_icons.py`

Note: Infipoke lists **1399** unique item slugs (1511 NUXT rows include duplicates). One catalog entry — `pokemoncenterrebuildkit` — currently has no reachable image on Infipoke or Serebii (both return HTTP 404); the script reports it and skips.

### `data/localization.json`

Built by `scripts/build_localization.py` from:

| Content | Source |
|---------|--------|
| Pokémon names (`en`/`ja`/`zh_tw`) | [Infipoke Pokopia Pokédex](https://infipoke.com/zh-hant/game/pokopia/pokedex) (`name` slug, `name_ja`, `name_zh_tw`); English display names prefer the [naru-pokopia-zukan](https://github.com/naru08-creator/naru-pokopia-zukan) sheet |
| Item names (`en`/`ja`) | [Infipoke Pokopia Items](https://infipoke.com/game/pokopia/items) (`name`, `name_ja`, `name_zh`). Not every item has `name_ja` upstream. |
| Item names (`zh_tw`) | OpenCC `s2tw` conversion of Infipoke `name_zh` (original Simplified Chinese kept as `zh`) |
| Item categories | Infipoke items filter labels (EN/JA/ZH-Hant pages) |
| Favorite categories (`en`/`ja`) | [naru-pokopia-zukan](https://github.com/naru08-creator/naru-pokopia-zukan) Google Sheets CSV |
| Favorite categories (`zh_tw`) | [Pokopia GamerTW — 喜好](https://pokopia.gamertw.com/zh-TW/favorite) |
| Specialties (`en`/`ja`) | naru-pokopia-zukan Google Sheets CSV (+ manual JP term map) |
| Specialties (`zh_tw`) | [Infipoke Pokopia Skills](https://infipoke.com/zh-hant/game/pokopia/skills) labels |
| Ideal habitats (`en`/`ja`) | naru-pokopia-zukan Google Sheets CSV |
| Ideal habitats (`zh_tw`) | Conventional Traditional Chinese terms for Bright / Cool / Dark / Dry / Humid / Warm |

Refresh:

```bash
uv sync --project scripts
uv run --project scripts python scripts/build_localization.py
```

naru sheet CSV endpoints used by the script:

- EN: `https://docs.google.com/spreadsheets/d/1KLawCBmZsMP-seDsEQu5pFUf4_NOIR6wbu3TqvbDXmk/gviz/tq?tqx=out:csv&gid=893275471&range=A:F`
- JA: `https://docs.google.com/spreadsheets/d/1KLawCBmZsMP-seDsEQu5pFUf4_NOIR6wbu3TqvbDXmk/gviz/tq?tqx=out:csv&gid=0&range=A:F`

## Localization JSON shape

```json
{
  "pokemon": {
    "001": { "en": "Bulbasaur", "ja": "フシギダネ", "zh_tw": "妙蛙種子", "slug": "bulbasaur" }
  },
  "favorites": {
    "lots_of_nature": { "en": "Lots of nature", "ja": "自然を感じる", "zh_tw": "能感受大自然的" }
  },
  "specialties": {
    "grow": { "en": "Grow", "ja": "さいばい", "zh_tw": "栽培" }
  },
  "ideal_habitats": {
    "bright": { "en": "Bright", "ja": "あかるい", "zh_tw": "明亮" }
  },
  "item_categories": {
    "materials": { "en": "Materials", "ja": "素材", "zh_tw": "素材" }
  },
  "items": {
    "honey": {
      "en": "Honey",
      "ja": "あまいミツ",
      "zh_tw": "蜂蜜",
      "zh": "蜂蜜",
      "category": "Materials"
    }
  }
}
```

## Rebuild everything

```bash
uv sync --project scripts
uv run --project scripts python scripts/download_pokopia_csv.py
uv run --project scripts python scripts/download_icons.py
uv run --project scripts python scripts/build_localization.py
```

## License / ownership

- Code in this repository is under the license in [`LICENSE`](LICENSE).
- Pokémon names, item names, sprites, and related assets remain the property of their respective rights holders / original publishers.
- Community source sites retain their own terms; redistributed reference copies here are for fan tooling and personal use.
