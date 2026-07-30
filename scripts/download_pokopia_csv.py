#!/usr/bin/env python3
"""Download Pokopia.csv from the PokopiaPlanning community dataset."""

from __future__ import annotations

import urllib.request
from pathlib import Path

SOURCE_URL = (
    "https://raw.githubusercontent.com/JEschete/PokopiaPlanning/"
    "main/reference/Pokopia.csv"
)
REPO_URL = "https://github.com/JEschete/PokopiaPlanning"
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "Pokopia.csv"


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {SOURCE_URL}")
    with urllib.request.urlopen(SOURCE_URL) as resp:
        data = resp.read()
    OUT_PATH.write_bytes(data)
    print(f"Wrote {OUT_PATH} ({len(data)} bytes)")
    print(f"Source repo: {REPO_URL}")


if __name__ == "__main__":
    main()
