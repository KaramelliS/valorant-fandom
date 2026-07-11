import json
import re
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .cache import Cache
from .models import Agent, AgentAbility, Map, Weapon, WeaponSkin, WeaponStats


API_BASE = "https://valorant.fandom.com/api.php"
WIKI_BASE = "https://valorant.fandom.com/wiki/"

ROLE_CATEGORIES = {
    "Controllers": "Controller",
    "Duelists": "Duelist",
    "Initiators": "Initiator",
    "Sentinels": "Sentinel",
}

WEAPON_CATEGORIES = {
    "Sidearms": "Sidearm",
    "SMGs": "SMG",
    "Shotguns": "Shotgun",
    "Rifles": "Rifle",
    "Machine Guns": "Machine Gun",
    "Snipers": "Sniper",
}

WEAPON_NAMES = [
    "Classic", "Shorty", "Frenzy", "Ghost", "Sheriff", "Bandit",
    "Stinger", "Spectre",
    "Bucky", "Judge",
    "Bulldog", "Guardian", "Phantom", "Vandal",
    "Ares", "Odin",
    "Marshal", "Operator", "Outlaw",
    "Melee",
]


class ValorantClient:
    def __init__(self, cache_ttl: int = 3600):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ValorantFandomBot/1.0 (GitHub: hzKamburga/valorant-fandom)",
        })
        self.cache = Cache(ttl=cache_ttl)

    def _api_get(self, params: dict) -> dict:
        params["format"] = "json"
        key = f"api:{json.dumps(params, sort_keys=True)}"
        cached = self.cache.get(key)
        if cached:
            return cached
        resp = self.session.get(API_BASE, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        self.cache.set(key, data)
        return data

    def _get_thumbnail(self, title: str, size: int = 500) -> Optional[str]:
        data = self._api_get({
            "action": "query",
            "prop": "pageimages",
            "titles": title,
            "pithumbsize": size,
        })
        pages = data.get("query", {}).get("pages", {})
        for pid in pages:
            thumb = pages[pid].get("thumbnail", {}).get("source")
            if thumb:
                return thumb
        return None

    def _parse_infobox(self, soup: BeautifulSoup) -> dict:
        aside = soup.find("aside", class_="portable-infobox")
        if not aside:
            aside = soup.find("aside")
        if not aside:
            return {"info": {}, "images": {}}

        info = {}
        for item in aside.select(".pi-data"):
            label_el = item.select_one(".pi-data-label")
            value_el = item.select_one(".pi-data-value")
            if label_el and value_el:
                label = label_el.get_text(strip=True)
                value = value_el.get_text(" ", strip=True)
                info[label] = value

        images = {}
        for tab in aside.select(".pi-image-collection .wds-tab__content"):
            tab_label_id = tab.get("aria-labelledby", "")
            tab_btn = aside.find(id=tab_label_id)
            tab_name = tab_btn.get_text(strip=True) if tab_btn else ""
            img = tab.find("img")
            if img:
                src = img.get("src") or img.get("data-src", "")
                if src and "base64" not in src:
                    images[tab_name] = src

        if not images:
            for img in aside.select(".pi-image-thumbnail"):
                src = img.get("src") or img.get("data-src", "")
                if src and "base64" not in src:
                    images["main"] = src
                    break

        return {"info": info, "images": images}

    def _parse_agent_page(self, title: str) -> dict:
        data = self._api_get({
            "action": "parse",
            "page": title,
            "prop": "text",
        })
        html = data.get("parse", {}).get("text", {}).get("*", "")
        soup = BeautifulSoup(html, "html.parser")

        parsed = self._parse_infobox(soup)
        info = parsed["info"]
        images = parsed["images"]
        aside = soup.find("aside", class_="portable-infobox") or soup.find("aside")

        # Parse abilities from infobox HTML structure (with icons)
        abilities = []
        abi_sources = {
            "basic": "Basic",
            "signature": "Signature",
            "ultimate": "Ultimate",
            "passives": "Passive",
        }
        if aside:
            for data_source, slot in abi_sources.items():
                abi_item = aside.select_one(f'.pi-item[data-source="{data_source}"]')
                if abi_item:
                    value_div = abi_item.select_one(".pi-data-value")
                    if value_div:
                        # Find all <img> inside .Invert spans (ability icons, ordered)
                        icon_imgs = value_div.select(".Invert img")
                        icons = []
                        for img in icon_imgs:
                            src = img.get("data-src") or img.get("src")
                            if src and "base64" not in src:
                                icons.append(src.replace("scale-to-width-down/25", "scale-to-width-down/96"))
                            else:
                                icons.append(None)

                        # Find ability name links (skip image links with .image class)
                        name_links = value_div.select('a[href]')
                        icon_idx = 0
                        for link in name_links:
                            name = link.get_text(strip=True)
                            # Skip links that are just images (no text, or have .image class)
                            if not name or "image" in link.get("class", []):
                                continue
                            icon_url = icons[icon_idx] if icon_idx < len(icons) else None
                            abilities.append(AgentAbility(name=name, slot=slot, icon_url=icon_url))
                            icon_idx += 1

        # Extract role icon
        role_icon_url = None
        if aside:
            role_item = aside.select_one('.pi-item[data-source="role"] img')
            if role_item:
                role_icon_url = role_item.get("data-src") or role_item.get("src")
                if role_icon_url and "base64" not in role_icon_url:
                    role_icon_url = role_icon_url.replace("scale-to-width-down/25", "scale-to-width-down/96")

        # Extract bust icon (agent select icon in infobox title)
        bust_icon_url = None
        if aside:
            title_img = aside.select_one(".pi-title img")
            if title_img:
                bust_icon_url = title_img.get("data-src") or title_img.get("src")
                if bust_icon_url and "base64" not in bust_icon_url:
                    bust_icon_url = bust_icon_url.replace("scale-to-width-down/25", "scale-to-width-down/96")

        portrait = (
            images.get("Artwork")
            or images.get("VP Portrait")
            or images.get("main")
        )

        quote_el = soup.select_one("table.themebg i")
        description = quote_el.get_text(strip=True) if quote_el else ""

        if not description:
            desc_p = soup.select_one("aside ~ p")
            description = desc_p.get_text(strip=True) if desc_p else ""

        return {
            "info": info,
            "abilities": abilities,
            "description": description,
            "portrait_url": portrait,
            "role_icon_url": role_icon_url,
            "bust_icon_url": bust_icon_url,
        }

    def _get_role_for_agent(self, name: str) -> str:
        for cat, role in ROLE_CATEGORIES.items():
            cache_key = f"role:{cat}"
            members = self.cache.get(cache_key)
            if members is None:
                data = self._api_get({
                    "action": "query",
                    "list": "categorymembers",
                    "cmtitle": f"Category:{cat}",
                    "cmlimit": 50,
                })
                members = [
                    m["title"]
                    for m in data.get("query", {}).get("categorymembers", [])
                ]
                self.cache.set(cache_key, members)
            if name in members:
                return role
        return ""

    def get_agents(self, parse_details: bool = False) -> list[Agent]:
        data = self._api_get({
            "action": "query",
            "list": "categorymembers",
            "cmtitle": "Category:Agents",
            "cmlimit": 50,
        })

        members = data.get("query", {}).get("categorymembers", [])
        agent_names = [m["title"] for m in members if m["ns"] == 0 and m["title"] != "Agents"]

        bulk_data = self._api_get({
            "action": "query",
            "prop": "pageimages|info",
            "titles": "|".join(agent_names),
            "inprop": "url",
            "pithumbsize": 500,
        })

        pages = bulk_data.get("query", {}).get("pages", {})

        agents = []
        for name in agent_names:
            page = next((p for p in pages.values() if p.get("title") == name), {})
            thumb = page.get("thumbnail", {}).get("source")
            url = page.get("fullurl", WIKI_BASE + name.replace(" ", "_"))
            role = self._get_role_for_agent(name)

            agent = Agent(
                name=name,
                url=url,
                role=role,
                full_portrait_url=thumb,
                thumbnail_url=thumb,
            )

            if parse_details:
                details = self._parse_agent_page(name)
                agent.description = details["description"]
                agent.abilities = details["abilities"]
                agent.origin = details["info"].get("Origin", "")
                agent.codename = details["info"].get("Codenames", "")
                agent.release_patch = details["info"].get("Added", "")
                agent.role_icon_url = details.get("role_icon_url")
                agent.bust_icon_url = details.get("bust_icon_url")
                if details.get("portrait_url"):
                    agent.full_portrait_url = details["portrait_url"]

            agents.append(agent)

        return agents

    def get_weapons(self, parse_details: bool = False) -> list[Weapon]:
        all_weapons = []

        for cat, weapon_type in WEAPON_CATEGORIES.items():
            data = self._api_get({
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Category:{cat}",
                "cmlimit": 50,
            })

            members = data.get("query", {}).get("categorymembers", [])
            weapon_names = [
                m["title"] for m in members
                if m["ns"] == 0
                and not any(skip in m["title"] for skip in ["Weapons", "Skin", "Skins"])
            ]

            if not weapon_names:
                continue

            bulk_data = self._api_get({
                "action": "query",
                "prop": "pageimages|info",
                "titles": "|".join(weapon_names),
                "inprop": "url",
                "pithumbsize": 500,
            })

            pages = bulk_data.get("query", {}).get("pages", {})

            for name in weapon_names:
                page = next((p for p in pages.values() if p.get("title") == name), {})
                thumb = page.get("thumbnail", {}).get("source")
                url = page.get("fullurl", WIKI_BASE + name.replace(" ", "_"))

                weapon = Weapon(
                    name=name,
                    url=url,
                    category=weapon_type,
                    image_url=thumb,
                )

                if parse_details:
                    wdata = self._parse_weapon_page(name)
                    weapon.description = wdata["description"]
                    weapon.cost = wdata["cost"]
                    weapon.stats = wdata["stats"]
                    weapon.killfeed_icon_url = wdata.get("killfeed_icon_url")
                    if wdata.get("image_url"):
                        weapon.image_url = wdata["image_url"]

                all_weapons.append(weapon)

        return all_weapons

    def _parse_weapon_page(self, title: str) -> dict:
        data = self._api_get({
            "action": "parse",
            "page": title,
            "prop": "text",
        })
        html = data.get("parse", {}).get("text", {}).get("*", "")
        soup = BeautifulSoup(html, "html.parser")

        aside = soup.find("aside", class_="portable-infobox") or soup.find("aside")

        def _get_data_value(source):
            if not aside:
                return ""
            el = aside.select_one(f'div[data-source="{source}"] .pi-data-value')
            return el.get_text(" ", strip=True) if el else ""

        stats = WeaponStats(
            fire_rate=_get_data_value("rate"),
            run_speed=_get_data_value("run"),
            equip_speed=_get_data_value("equip"),
            reload_speed=_get_data_value("reload"),
            magazine_size=_get_data_value("magazine"),
            wall_penetration=_get_data_value("penetration"),
        )

        cost = _get_data_value("credits")

        # Killfeed icon
        killfeed_icon_url = None
        if aside:
            killfeed_img = aside.select_one('div[data-source="killfeed"] img')
            if killfeed_img:
                src = killfeed_img.get("data-src") or killfeed_img.get("src")
                if src and "base64" not in src:
                    killfeed_icon_url = src

        # Main weapon render image (fallback when pageimages API has no thumbnail)
        image_url = None
        if aside:
            main_img = aside.select_one(".pi-image-thumbnail")
            if main_img:
                src = main_img.get("data-src") or main_img.get("src") or ""
                if src and "base64" not in src:
                    image_url = src
            if not image_url:
                for img in aside.select("img"):
                    src = img.get("data-src") or img.get("src") or ""
                    if (src and "base64" not in src
                            and title.lower() in src.lower()
                            and "icon" not in src.lower()
                            and "killfeed" not in src.lower()
                            and "_comparison" not in src.lower()):
                        image_url = src
                        break
            if image_url:
                image_url = self._resolve_image_url(image_url, 500)

        desc_el = soup.select_one("aside ~ p")
        description = desc_el.get_text(strip=True) if desc_el else ""

        return {
            "description": description,
            "cost": cost,
            "stats": stats,
            "killfeed_icon_url": killfeed_icon_url,
            "image_url": image_url,
        }

    def get_weapon_skins(self, weapon_name: str) -> list[WeaponSkin]:
        cat_name = f"Category:{weapon_name}_Skins"
        data = self._api_get({
            "action": "query",
            "list": "categorymembers",
            "cmtitle": cat_name,
            "cmlimit": 500,
        })

        members = data.get("query", {}).get("categorymembers", [])
        file_titles = [
            m["title"] for m in members
            if m["ns"] == 6 and weapon_name in m["title"]
        ]

        if not file_titles:
            return []

        # MediaWiki limits titles to 50 per query — batch to avoid failures
        url_map = {}
        for i in range(0, len(file_titles), 50):
            batch = file_titles[i:i + 50]
            image_data = self._api_get({
                "action": "query",
                "prop": "imageinfo",
                "titles": "|".join(batch),
                "iiprop": "url",
                "iiurlwidth": 300,
            })
            pages = image_data.get("query", {}).get("pages", {})
            for pid, page_data in pages.items():
                ii = page_data.get("imageinfo", [])
                if ii:
                    url_map[page_data["title"]] = ii[0].get("thumburl") or ii[0].get("url", "")

        skins = []
        for ftitle in file_titles:
            name_part = ftitle.replace("File:", "").replace(f" {weapon_name}.png", "").replace(".png", "")
            skin_name = name_part.strip()
            img_url = url_map.get(ftitle, "")
            skins.append(WeaponSkin(name=skin_name, image_url=img_url))

        return skins

    def get_all_skins(self) -> dict[str, list[WeaponSkin]]:
        result = {}
        for wname in WEAPON_NAMES:
            skins = self.get_weapon_skins(wname)
            if skins:
                result[wname] = skins
        return result

    def get_maps(self, parse_details: bool = False) -> list[Map]:
        data = self._api_get({
            "action": "query",
            "list": "categorymembers",
            "cmtitle": "Category:Maps",
            "cmlimit": 50,
        })

        members = data.get("query", {}).get("categorymembers", [])
        skip_titles = {"Maps", "Range", "Summit"}
        map_names = [
            m["title"] for m in members
            if m["ns"] == 0 and m["title"] not in skip_titles
            and not any(q in m["title"] for q in ["Quotes", "Audio"])
        ]

        bulk_data = self._api_get({
            "action": "query",
            "prop": "pageimages|info",
            "titles": "|".join(map_names),
            "inprop": "url",
            "pithumbsize": 500,
        })

        pages = bulk_data.get("query", {}).get("pages", {})

        maps = []
        for name in map_names:
            page = next((p for p in pages.values() if p.get("title") == name), {})
            thumb = page.get("thumbnail", {}).get("source")
            url = page.get("fullurl", WIKI_BASE + name.replace(" ", "_"))

            m = Map(
                name=name,
                url=url,
                image_url=thumb,
            )

            if parse_details:
                mdata = self._parse_map_page(name)
                m.description = mdata["description"]
                m.location = mdata.get("location", "")
                m.release_patch = mdata.get("patch", "")
                if not m.image_url and mdata.get("image_url"):
                    m.image_url = mdata["image_url"]

            maps.append(m)

        return maps

    def _parse_map_page(self, title: str) -> dict:
        data = self._api_get({
            "action": "parse",
            "page": title,
            "prop": "text",
        })
        html = data.get("parse", {}).get("text", {}).get("*", "")
        soup = BeautifulSoup(html, "html.parser")

        aside = soup.find("aside", class_="portable-infobox") or soup.find("aside")

        def _get_data_value(source):
            if not aside:
                return ""
            el = aside.select_one(f'div[data-source="{source}"] .pi-data-value')
            return el.get_text(" ", strip=True) if el else ""

        desc_el = soup.select_one("aside ~ p")
        description = desc_el.get_text(strip=True) if desc_el else ""

        # Main map loading screen image (fallback when pageimages API has no thumbnail)
        image_url = None
        if aside:
            main_img = aside.select_one(".pi-image-thumbnail")
            if main_img:
                src = main_img.get("data-src") or main_img.get("src") or ""
                if src and "base64" not in src:
                    image_url = src
            if not image_url:
                for img in aside.select("img"):
                    src = img.get("data-src") or img.get("src") or ""
                    if src and "base64" not in src and "Loading_Screen" in src:
                        image_url = src
                        break
            if image_url:
                image_url = self._resolve_image_url(image_url, 500)

        return {
            "description": description,
            "image_url": image_url,
            "location": _get_data_value("location"),
            "patch": _get_data_value("patch") or _get_data_value("added"),
            "coordinates": _get_data_value("coordinates"),
        }

    def get_agent_icon(self, name: str, size: int = 96) -> Optional[str]:
        data = self._api_get({
            "action": "parse",
            "page": name,
            "prop": "text",
        })
        html = data.get("parse", {}).get("text", {}).get("*", "")
        soup = BeautifulSoup(html, "html.parser")
        aside = soup.find("aside", class_="portable-infobox")
        if aside:
            pi_title = aside.select_one(".pi-title img")
            if pi_title:
                src = pi_title.get("src") or pi_title.get("data-src", "")
                if src and "base64" not in src:
                    return self._resolve_image_url(src, size)
            for img in aside.select(".pi-image-thumbnail"):
                src = img.get("src") or img.get("data-src", "")
                if src and ("Portrait" in src or "icon" in src.lower()):
                    return self._resolve_image_url(src, size)

        return self._get_thumbnail(name, size)

    def _resolve_image_url(self, src: str, size: int) -> str:
        if "/scale-to-width-down/" in src:
            return re.sub(r"/scale-to-width-down/\d+", f"/scale-to-width-down/{size}", src)
        return src

    def get_weapon_icon(self, name: str, size: int = 96) -> Optional[str]:
        thumb = self._get_thumbnail(name, size)
        if thumb:
            return thumb
        return None

    def download_image(self, url: str, path: str) -> str:
        resp = self.session.get(url, timeout=30)
        resp.raise_for_status()
        with open(path, "wb") as f:
            f.write(resp.content)
        return path

    def search(self, query: str, limit: int = 10) -> list[dict]:
        data = self._api_get({
            "action": "opensearch",
            "search": query,
            "limit": limit,
        })
        results = []
        if len(data) >= 4:
            titles = data[1]
            descs = data[2]
            urls = data[3]
            for i in range(len(titles)):
                results.append({
                    "title": titles[i],
                    "description": descs[i],
                    "url": urls[i],
                })
        return results
