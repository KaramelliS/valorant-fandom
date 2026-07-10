# Valorant Fandom

Valorant Fandom Wiki verileri — 3 kullanim sekli:

## 1. HTML'e direkt import (CDN)

```html
<script src="https://cdn.jsdelivr.net/gh/KaramelliS/valorant-fandom@master/dist/valorant-fandom.min.js"></script>
<script>
  ValorantFandom.getAgents().then(function(agents) {
    console.log(agents); // 29 ajan
  });
</script>
```

## 2. npm

```bash
npm i valorant-fandom
```

```js
import VF from 'valorant-fandom';
const agents = await VF.getAgents();
```

## 3. Direkt JSON (dil bagimsiz)

```
https://raw.githubusercontent.com/KaramelliS/valorant-fandom/main/data/agents.json
https://raw.githubusercontent.com/KaramelliS/valorant-fandom/main/data/weapons.json
https://raw.githubusercontent.com/KaramelliS/valorant-fandom/main/data/maps.json
https://raw.githubusercontent.com/KaramelliS/valorant-fandom/main/data/skins.json
```

## Demo

https://karamellis.github.io/valorant-fandom/

## API

| Metod | Donus |
|-------|-------|
| `getAgents()` | Tum ajanlar (29) |
| `getAgent('Jett')` | Tek ajan |
| `getWeapons()` | Tum silahlar (19) |
| `getWeapon('Vandal')` | Tek silah |
| `getMaps()` | Tum haritalar (13) |
| `getSkins()` | Tum skinler (1068) |
| `getSkins('Vandal')` | Sadece Vandal skinleri |
| `search('Vandal')` | Arama |
| `getAgentsByRole('Duelist')` | Role gore filtre |
| `setBaseUrl(url)` | Kendi JSON endpoint'in |
| `clearCache()` | Cache temizle |

## Veri

| Dosya | Kayit |
|-------|-------|
| `data/agents.json` | 29 ajan |
| `data/weapons.json` | 19 silah |
| `data/maps.json` | 13 harita |
| `data/skins.json` | 1068 skin |
