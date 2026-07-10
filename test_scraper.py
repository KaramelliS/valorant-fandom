from valorant_fandom.client import ValorantClient

c = ValorantClient()

# Test agents
print("=== AGENTS ===")
agents = c.get_agents(parse_details=True)
a = agents[0]
print(f"Name: {a.name}")
print(f"Role Icon: {a.role_icon_url[:80] if a.role_icon_url else 'NONE'}")
print(f"Bust Icon: {a.bust_icon_url[:80] if a.bust_icon_url else 'NONE'}")
print("Abilities:")
for ab in a.abilities:
    icon = ab.icon_url[:80] if ab.icon_url else "NONE"
    print(f"  {ab.slot}: {ab.name} | icon={icon}")

# Test weapons
print("\n=== WEAPONS ===")
weapons = c.get_weapons(parse_details=True)
for w in weapons[:3]:
    print(f"{w.name}: cost={w.cost} | fire_rate={w.stats.fire_rate} | killfeed={w.killfeed_icon_url[:80] if w.killfeed_icon_url else 'NONE'}")

# Test maps
print("\n=== MAPS ===")
maps = c.get_maps(parse_details=True)
for m in maps[:3]:
    print(f"{m.name}: location={m.location} | patch={m.release_patch}")
