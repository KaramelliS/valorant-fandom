# Valorant Fandom

Valorant Fandom Wiki verileri - Python kutuphanesi **veya** direkt JSON olarak kullanilabilir.

## Python Kutuphanesi

```bash
pip install valorant-fandom
```

```python
from valorant_fandom import ValorantClient

client = ValorantClient()

agents = client.get_agents()
weapons = client.get_weapons()
maps = client.get_maps()

# Detayli
agents = client.get_agents(parse_details=True)

# Skinler
skins = client.get_weapon_skins("Vandal")  # 96 skin
all_skins = client.get_all_skins()         # 1068 skin
```

## Direkt JSON (dil bagimsiz)

```js
// JavaScript
const agents = await fetch("data/agents.json").then(r => r.json());
const weapons = await fetch("data/weapons.json").then(r => r.json());
const skins = await fetch("data/skins.json").then(r => r.json());
```

```python
# Python (kutuphane kurmadan)
import json
agents = json.load(open("data/agents.json"))
```

## JSON Dosyalari

| Dosya | Icerik | Kayit |
|-------|--------|-------|
| `data/agents.json` | Ajanlar (isim, rol, yetenekler, origin, gorsel) | 29 |
| `data/weapons.json` | Silahlar (isim, kategori, istatistikler, gorsel) | 19 |
| `data/maps.json` | Haritalar (isim, konum, gorsel, patch) | 13 |
| `data/skins.json` | Tum silah skinleri (isim, gorsel) | 1068 |

## JSON'u Yeniden Olusturma

```bash
python -m valorant_fandom.export
```
