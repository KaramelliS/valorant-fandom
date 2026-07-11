# Valorant Fandom

Valorant Fandom Wiki verileri — sunucusuz, GitHub raw URL ile çalışan JS kutuphanesi.

## Ozellikler

- **5 modul**: Agents, Weapons, Maps, Ranks, Skins
- **Sunucusuz**: Tum veriler `raw.githubusercontent.com`'dan cekilir, PHP/backend gerekmez
- **UMD**: HTML script tag, npm, AMD hepsi destekli
- **Cache**: Ayni istek tekrar cekilmez

## 1. HTML'e direkt import

```html
<script src="https://raw.githubusercontent.com/KaramelliS/valorant-fandom/master/dist/valorant-fandom.min.js"></script>
<script>
  ValorantFandom.getAgents().then(function(agents) {
    console.log(agents); // 29 ajan
  });
</script>
```

## 2. Direkt JSON (dil bagimsiz)

```
https://raw.githubusercontent.com/KaramelliS/valorant-fandom/master/data/agents.json
https://raw.githubusercontent.com/KaramelliS/valorant-fandom/master/data/weapons.json
https://raw.githubusercontent.com/KaramelliS/valorant-fandom/master/data/maps.json
https://raw.githubusercontent.com/KaramelliS/valorant-fandom/master/data/ranks.json
https://raw.githubusercontent.com/KaramelliS/valorant-fandom/master/data/skins.json
```

## 3. Rank ikonlari (statik)

Her rank PNG'si tek basina cekilebilir:

```
https://raw.githubusercontent.com/KaramelliS/valorant-fandom/master/ranks/Gold_2.png
```

Picker: https://karamellis.github.io/valorant-fandom/ranks.html

## Demo

- Ana demo: https://karamellis.github.io/valorant-fandom/
- Rank picker: https://karamellis.github.io/valorant-fandom/ranks.html

## API

### Agents

| Metod | Donus |
|-------|-------|
| `getAgents()` | Tum ajanlar (29) |
| `getAgent('Jett')` | Tek ajan |
| `getAgentsByRole('Duelist')` | Role gore filtre |

### Weapons

| Metod | Donus |
|-------|-------|
| `getWeapons()` | Tum silahlar (19) |
| `getWeapon('Vandal')` | Tek silah |
| `getWeaponsByCategory('Rifle')` | Kategoriye gore filtre |

### Maps

| Metod | Donus |
|-------|-------|
| `getMaps()` | Tum haritalar (12) |
| `getMap('Ascent')` | Tek harita |

### Ranks

| Metod | Donus |
|-------|-------|
| `getRanks()` | Tum ranklar (25) |
| `getRanks('Gold')` | Belirli tier'in ranklari |
| `getRank('Gold 2')` | Tek rank (isim veya dosya adiyla) |

### Skins

| Metod | Donus |
|-------|-------|
| `getSkins()` | Tum skinler (1068) |
| `getSkins('Vandal')` | Sadece Vandal skinleri |

### Genel

| Metod | Donus |
|-------|-------|
| `search('Vandal')` | Agents + weapons + maps arama |
| `setBaseUrl(url)` | Kendi JSON endpoint'in |
| `clearCache()` | Cache temizle |
| `version()` | Kutuphane versiyonu |

## Veri

| Dosya | Kayit | Detay |
|-------|-------|-------|
| `data/agents.json` | 29 ajan | portre, bust ikon, role ikon, yetenekler |
| `data/weapons.json` | 19 silah | resim, killfeed ikon, cost, stats |
| `data/maps.json` | 12 harita | loading screen, lokasyon, patch |
| `data/ranks.json` | 25 rank | tier, numara, ikon URL (raw) |
| `data/skins.json` | 1068 skin | 19 silaha ait, ikon URL |

## Python Scraper

Veriler `valorant_fandom/` paketiyle Fandom API + HTML parsing ile uretilir:

```
python -m valorant_fandom.export
```

Cache: `~/.valorant_cache/` (TTL 1 saat). Cache silinip tekrar export ile guncellenir.

## Lisans

MIT
