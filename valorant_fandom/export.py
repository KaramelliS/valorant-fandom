"""Tum Valorant Fandom verisini JSON dosyalarina export eder.

Kullanim:
    python -m valorant_fandom.export

Cikti:
    data/agents.json      - Tum ajanlar (detayli)
    data/weapons.json     - Tum silahlar (detayli)
    data/maps.json        - Tum haritalar (detayli)
    data/skins.json       - Tum silah skinleri
"""

import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

from .client import ValorantClient


def _serialize(obj):
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _serialize(v) for k, v in asdict(obj).items()}
    if isinstance(obj, list):
        return [_serialize(i) for i in obj]
    return obj


def export_all(output_dir: str = "data"):
    client = ValorantClient(cache_ttl=3600)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("Agents cekiliyor...")
    agents = client.get_agents(parse_details=True)
    agents_data = [_serialize(a) for a in agents]
    (out / "agents.json").write_text(
        json.dumps(agents_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  -> {len(agents)} agents -> agents.json")

    print("Weapons cekiliyor...")
    weapons = client.get_weapons(parse_details=True)
    weapons_data = [_serialize(w) for w in weapons]
    (out / "weapons.json").write_text(
        json.dumps(weapons_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  -> {len(weapons)} weapons -> weapons.json")

    print("Maps cekiliyor...")
    maps = client.get_maps(parse_details=True)
    maps_data = [_serialize(m) for m in maps]
    (out / "maps.json").write_text(
        json.dumps(maps_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  -> {len(maps)} maps -> maps.json")

    print("Skins cekiliyor (bu biraz surer)...")
    skins = client.get_all_skins()
    skins_data = {
        weapon: [_serialize(s) for s in skin_list]
        for weapon, skin_list in skins.items()
    }
    (out / "skins.json").write_text(
        json.dumps(skins_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    total_skins = sum(len(v) for v in skins.values())
    print(f"  -> {total_skins} skins across {len(skins)} weapons -> skins.json")

    print(f"\nDone! Veriler {out.resolve()}/ altinda.")


if __name__ == "__main__":
    export_all()
