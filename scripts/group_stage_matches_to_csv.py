import json
import csv
import glob
import os
from datetime import datetime, timezone

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")
MATCHES_DIR = os.path.join(ROOT_DIR, "data", "group_stage", "matches")
OUTPUT_FILE = os.path.join(ROOT_DIR, "data", "group_stage", "total.csv")

with open(os.path.join(ROOT_DIR, "data", "heroes.json"), "r", encoding="utf-8") as f:
    heroes_data = json.load(f)

with open(os.path.join(ROOT_DIR, "data", "hero_types.json"), "r", encoding="utf-8") as f:
    hero_types = json.load(f)

# hero name -> set of prefix categories it belongs to (a hero can have several)
HERO_CATEGORIES_BY_NAME = {}
for category, hero_names in hero_types.items():
    for hero_name in hero_names:
        HERO_CATEGORIES_BY_NAME.setdefault(hero_name, set()).add(category)

CATEGORY_COLUMNS = {
    category: f"is_{category.lower().replace(' ', '_').replace('/', '_')}"
    for category in hero_types.keys()
}

def get_hero_category_flags(hero_name):
    categories_present = HERO_CATEGORIES_BY_NAME.get(hero_name, set())
    return {
        column: 1 if category in categories_present else 0
        for category, column in CATEGORY_COLUMNS.items()
    }

# OpenDota series_type: 0 = best of 1, 1 = best of 3, 2 = best of 5
MAX_GAMES_BY_SERIES_TYPE = {0: 1, 1: 3, 2: 5}

POSITION_BUCKETS = {
    1: "core",
    3: "core",
    2: "mid",
    4: "support",
    5: "support",
}

STAT_COLUMNS = [
    "kills",
    "deaths",
    "creep_score",
    "gpm",
    "madstone_collected",
    "tower_kills",
    "obs_placed",
    "camps_stacked",
    "runes_grabbed",
    "watchers_taken",
    "smokes_used",
    "teamfight_participation",
    "stuns",
    "firstblood_claimed",
    "roshan_kills",
    "tormentor_kills",
    "tormentor_deaths",
    "courier_kills",
    "win",
]

def get_player_stats(player):
    return {
        "kills": player.get("kills", 0),
        "deaths": player.get("deaths", 0),
        "creep_score": player.get("last_hits", 0) + player.get("denies", 0),
        "gpm": player.get("gold_per_min", 0),
        "madstone_collected": player.get("item_uses", {}).get("madstone_bundle", 0),
        "tower_kills": player.get("tower_kills", 0),
        "obs_placed": player.get("obs_placed", 0),
        "camps_stacked": player.get("camps_stacked", 0),
        "runes_grabbed": player.get("rune_pickups", 0),
        "watchers_taken": player.get("ability_uses", {}).get("ability_lamp_use", 0),
        "smokes_used": player.get("item_uses", {}).get("smoke_of_deceit", 0),
        "teamfight_participation": player.get("teamfight_participation", 0),
        "stuns": player.get("stuns", 0),
        "firstblood_claimed": player.get("firstblood_claimed", 0),
        "roshan_kills": player.get("roshan_kills", 0),
        "tormentor_kills": player.get("killed", {}).get("npc_dota_miniboss", 0),
        "tormentor_deaths": player.get("killed_by", {}).get("npc_dota_miniboss", 0),
        "courier_kills": player.get("courier_kills", 0),
        "win": player.get("win", 0),
    }

matches = []
for filepath in glob.glob(os.path.join(MATCHES_DIR, "*.json")):
    with open(filepath, "r", encoding="utf-8") as f:
        matches.append(json.load(f))

# Group matches into series to compute Game_number / isLastGame
series_groups = {}
for match in matches:
    series_key = match.get("series_id") or f"single_{match['match_id']}"
    series_groups.setdefault(series_key, []).append(match)

game_number_by_match = {}
is_last_game_by_match = {}
for series_matches in series_groups.values():
    series_matches.sort(key=lambda m: m.get("start_time", 0))
    series_type = series_matches[0].get("series_type")
    max_games = MAX_GAMES_BY_SERIES_TYPE.get(series_type, len(series_matches))
    for idx, match in enumerate(series_matches, start=1):
        game_number_by_match[match["match_id"]] = idx
        # isLastGame = this is the last possible game of the series (e.g. game 3
        # of a Bo3), not just the latest one we happen to have crawled.
        is_last_game_by_match[match["match_id"]] = 1 if idx == max_games else 0

rows = []
for match in matches:
    match_id = match["match_id"]
    radiant_name = match.get("radiant_name") or (match.get("radiant_team") or {}).get("name", "")
    dire_name = match.get("dire_name") or (match.get("dire_team") or {}).get("name", "")
    versus = f"{radiant_name} vs {dire_name}"
    date_str = datetime.fromtimestamp(match.get("start_time", 0), tz=timezone.utc).strftime("%d/%m/%Y")
    series_id = match.get("series_id") or f"single_{match_id}"

    for player in match.get("players", []):
        is_radiant = player.get("isRadiant")
        row = {
            "matchID": match_id,
            "seriesID": series_id,
            "Versus": versus,
            "Game_number": game_number_by_match[match_id],
            "gametime": match.get("duration", 0),
            "first_blood_time": match.get("first_blood_time", 0),
            "isLastGame": is_last_game_by_match[match_id],
            "playerID": player.get("account_id", ""),
            "playerName": player.get("name") or player.get("personaname", ""),
            "teamID": match.get("radiant_team_id") if is_radiant else match.get("dire_team_id"),
            "teamName": radiant_name if is_radiant else dire_name,
            "position": POSITION_BUCKETS.get(player.get("position_est"), ""),
            "heroID": player.get("hero_id"),
            "heroName": heroes_data.get(str(player.get("hero_id")), {}).get("name", ""),
        }
        row.update(get_hero_category_flags(row["heroName"]))
        row.update(get_player_stats(player))
        row["date"] = date_str
        rows.append(row)

fieldnames = ["matchID", "seriesID", "Versus", "Game_number", "gametime", "first_blood_time", "isLastGame", "playerID", "playerName", "teamID", "teamName", "position", "heroID", "heroName"] + list(CATEGORY_COLUMNS.values()) + STAT_COLUMNS + ["date"]

with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows from {len(matches)} matches to {OUTPUT_FILE}")
