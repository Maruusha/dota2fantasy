import json
import glob
import os

with open("leagues.json", "r", encoding="utf-8") as f:
    leagues_data = json.load(f)

with open("data/heroes.json", "r", encoding="utf-8") as f:
    heroes_data = json.load(f)

with open("data/hero_types.json", "r", encoding="utf-8") as f:
    hero_types = json.load(f)

try:
    with open('players_stat.json', 'r', encoding='utf-8') as f:
        player_stat = json.load(f)
except FileNotFoundError:
    player_stat = {}

leagues_ids = list(map(int, leagues_data.keys()))

# OpenDota position_est (1-5) -> fantasy role bucket: 0 = core, 1 = mid, 2 = support
POSITION_BUCKETS = {1: 0, 3: 0, 2: 1, 4: 2, 5: 2}

# OpenDota series_type: 0 = best of 1, 1 = best of 3, 2 = best of 5
MAX_GAMES_BY_SERIES_TYPE = {0: 1, 1: 3, 2: 5}

# hero name -> set of prefix categories it belongs to (a hero can have several)
HERO_CATEGORIES_BY_NAME = {}
for category, hero_names in hero_types.items():
    for hero_name in hero_names:
        HERO_CATEGORIES_BY_NAME.setdefault(hero_name, set()).add(category.lower())

PREFIX_KEYS = [category.lower() for category in hero_types.keys()]

def get_player_pos(player):
    return POSITION_BUCKETS.get(player.get('position_est'))

def compute_is_last_game(matches):
    series_groups = {}
    for match_r in matches:
        series_key = match_r.get('series_id') or f"single_{match_r['match_id']}"
        series_groups.setdefault(series_key, []).append(match_r)

    is_last_game_by_match = {}
    for series_matches in series_groups.values():
        series_matches.sort(key=lambda m: m.get('start_time', 0))
        series_type = series_matches[0].get('series_type')
        max_games = MAX_GAMES_BY_SERIES_TYPE.get(series_type, len(series_matches))
        for idx, match_r in enumerate(series_matches, start=1):
            is_last_game_by_match[match_r['match_id']] = idx == max_games
    return is_last_game_by_match

def addPlayerFields(league_id, player, match_r, pos):
    if player['name'] not in player_stat:
        player_stat[player['name']] = {}

    if league_id not in player_stat[player['name']]:
        player_stat[player['name']][league_id] = {
            "stats": {},
            "titles": {key: 0 for key in PREFIX_KEYS},
            "subtitles": {
                "lost_games": 0,
                "clutch": 0,
                "lucky": 0
            }
        }

        if "general" not in player_stat[player['name']]:
            player_stat[player['name']]["general"] = {}

        player_stat[player['name']]["general"]["team_logo"] = (match_r['radiant_team']['logo_url'] if player['isRadiant'] else match_r['dire_team']['logo_url'])
        player_stat[player['name']]["general"]["pos"] = pos

        if pos in (0, 1):
            player_stat[player['name']][league_id]['stats']['red'] = {
                "kills": [],
                "deaths": [],
                "creep_score": [],
                "gpm": [],
                "madstone_collected": [],
                "tower_kills": [],
            }
        if pos in (1, 2):
            player_stat[player['name']][league_id]['stats']['blue'] = {
                "obs_placed": [],
                "camps_stacked": [],
                "runes_grabbed": [],
                "watchers_taken": [],
                "smokes_used": [],
            }
        if pos in (0, 1, 2):
            player_stat[player['name']][league_id]['stats']['green'] = {
                "roshan_kills": [],
                "teamfight_participation": [],
                "stuns": [],
                "courier_kills": [],
                "tormentor_kills": [],
                "firstblood": [],
            }

matches_by_league = {league_id: [] for league_id in leagues_ids}
for filepath in glob.glob(os.path.join("data", "main_event", "matches", "*.json")):
    with open(filepath, "r", encoding="utf-8") as f:
        cached_match = json.load(f)
    if cached_match.get('leagueid') in matches_by_league:
        matches_by_league[cached_match['leagueid']].append(cached_match)

for league_id in leagues_ids:
    matches = matches_by_league[league_id]
    total_matches_count = 0
    is_last_game_by_match = compute_is_last_game(matches)

    for match_r in matches:
        firstbloodTime = match_r.get('first_blood_time', 0)
        is_match_counted = False
        is_tormentor_kill = False
        is_lucky_game = str(match_r['duration'])[-1] == '8'

        for player in match_r['players']:
            pos = get_player_pos(player)
            if pos is None:
                continue

            if player['name'] not in player_stat:
                player_stat[player['name']] = {}
            if league_id not in player_stat[player['name']]:
                addPlayerFields(league_id, player, match_r, pos)

            if player['lose']:
                player_stat[player['name']][league_id]['subtitles']['lost_games'] += 1

            if is_last_game_by_match[match_r['match_id']]:
                player_stat[player['name']][league_id]['subtitles']['clutch'] += 1

            if is_lucky_game:
                player_stat[player['name']][league_id]['subtitles']['lucky'] += 1

            if not is_match_counted:
                total_matches_count += 1
                is_match_counted = True

            if pos in (0, 1) and 'red' in player_stat[player['name']][league_id]['stats']:
                player_stat[player['name']][league_id]['stats']['red']['kills'].append(player['kills'])
                player_stat[player['name']][league_id]['stats']['red']['deaths'].append(player['deaths'])
                player_stat[player['name']][league_id]['stats']['red']['creep_score'].append(player['last_hits'] + player['denies'])
                player_stat[player['name']][league_id]['stats']['red']['gpm'].append(player['gold_per_min'])
                player_stat[player['name']][league_id]['stats']['red']['madstone_collected'].append(player.get('item_uses', {}).get('madstone_bundle', 0))
                player_stat[player['name']][league_id]['stats']['red']['tower_kills'].append(player['towers_killed'])
            if pos in (1, 2) and 'blue' in player_stat[player['name']][league_id]['stats']:
                player_stat[player['name']][league_id]['stats']['blue']['obs_placed'].append(player['obs_placed'])
                player_stat[player['name']][league_id]['stats']['blue']['camps_stacked'].append(player['camps_stacked'])
                player_stat[player['name']][league_id]['stats']['blue']['runes_grabbed'].append(player['rune_pickups'])
                player_stat[player['name']][league_id]['stats']['blue']['watchers_taken'].append(player.get('ability_uses', {}).get('ability_lamp_use', 0))
                player_stat[player['name']][league_id]['stats']['blue']['smokes_used'].append(player.get('item_uses', {}).get('smoke_of_deceit', 0))
            if pos in (0, 1, 2) and 'green' in player_stat[player['name']][league_id]['stats']:
                player_stat[player['name']][league_id]['stats']['green']['roshan_kills'].append(player['roshans_killed'])
                player_stat[player['name']][league_id]['stats']['green']['teamfight_participation'].append(player['teamfight_participation'])
                player_stat[player['name']][league_id]['stats']['green']['stuns'].append(player['stuns'])
                player_stat[player['name']][league_id]['stats']['green']['courier_kills'].append(player['courier_kills'])
                player_stat[player['name']][league_id]['stats']['green']['firstblood'].append(player['firstblood_claimed'])
                player_stat[player['name']][league_id]['stats']['green']['tormentor_kills'].append(player.get('killed', {}).get('npc_dota_miniboss', 0))

            hero_name = heroes_data[str(player['hero_id'])]['name']
            for category in HERO_CATEGORIES_BY_NAME.get(hero_name, set()):
                player_stat[player['name']][league_id]['titles'][category] += 1

            if player['killed_by'].get('npc_dota_miniboss', 0) > 0:
                is_tormentor_kill = True

        if is_tormentor_kill:
            leagues_data[str(league_id)]['total_deaths_from_torm'] += 1

        if firstbloodTime > 600:
            leagues_data[str(league_id)]['firstblood_before_10min'] += 1

        if firstbloodTime < 0:
            leagues_data[str(league_id)]['firstblood_before_horn'] += 1

        if match_r['duration'] < 1500:
            leagues_data[str(league_id)]['games<25min'] += 1

    leagues_data[str(league_id)]['total_matches_parsed'] = total_matches_count

with open('players_stat.json', "w", encoding="utf-8") as f:
    json.dump(player_stat, f, ensure_ascii=False, indent=4)

with open('leagues.json', "w", encoding="utf-8") as f:
    json.dump(leagues_data, f, ensure_ascii=False, indent=4)
