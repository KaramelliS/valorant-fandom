from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgentAbility:
    name: str
    slot: str
    description: str = ""
    icon_url: Optional[str] = None


@dataclass
class Agent:
    name: str
    url: str
    description: str = ""
    role: str = ""
    role_icon_url: Optional[str] = None
    full_portrait_url: Optional[str] = None
    bust_icon_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    abilities: list[AgentAbility] = field(default_factory=list)
    origin: str = ""
    codename: str = ""
    release_patch: str = ""

    @property
    def icon_url(self) -> Optional[str]:
        return self.bust_icon_url or self.thumbnail_url


@dataclass
class WeaponStats:
    fire_rate: str = ""
    run_speed: str = ""
    equip_speed: str = ""
    reload_speed: str = ""
    magazine_size: str = ""
    wall_penetration: str = ""
    damage_ranges: list[dict] = field(default_factory=list)


@dataclass
class WeaponSkin:
    name: str
    image_url: Optional[str] = None
    tier: str = ""
    bundle: str = ""


@dataclass
class Weapon:
    name: str
    url: str
    category: str = ""
    description: str = ""
    cost: str = ""
    image_url: Optional[str] = None
    killfeed_icon_url: Optional[str] = None
    stats: WeaponStats = field(default_factory=WeaponStats)
    skins: list[WeaponSkin] = field(default_factory=list)

    @property
    def icon_url(self) -> Optional[str]:
        return self.killfeed_icon_url or self.image_url


@dataclass
class Map:
    name: str
    url: str
    description: str = ""
    image_url: Optional[str] = None
    minimap_url: Optional[str] = None
    location: str = ""
    release_patch: str = ""
    coordinates: str = ""
    sites: str = ""
