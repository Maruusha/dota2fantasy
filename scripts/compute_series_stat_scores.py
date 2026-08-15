import csv
import os
from collections import defaultdict

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")
INPUT_FILE = os.path.join(ROOT_DIR, "data", "group_stage", "total.csv")
OUTPUT_FILE = os.path.join(ROOT_DIR, "data", "group_stage", "series_stat_scores.csv")

STAT_WEIGHTS = {
    "kills": 107,
    "creep_score": 3,
    "gpm": 2,
    "madstone_collected": 13,
    "tower_kills": 352,
    "obs_placed": 117,
    "camps_stacked": 234,
    "runes_grabbed": 141,
    "watchers_taken": 147,
    "smokes_used": 293,
    "teamfight_participation": 2124,
    "stuns": 10,
    "firstblood_claimed": 1934,
    "roshan_kills": 1172,
    "tormentor_kills": 879,
    "courier_kills": 703,
}

RED_STATS = ["kills", "deaths", "creep_score", "gpm", "madstone_collected", "tower_kills"]
BLUE_STATS = ["obs_placed", "camps_stacked", "runes_grabbed", "watchers_taken", "smokes_used"]
GREEN_STATS = ["roshan_kills", "teamfight_participation", "stuns", "courier_kills", "tormentor_kills", "firstblood_claimed"]
ALL_STATS = RED_STATS + BLUE_STATS + GREEN_STATS

# core = red + green (no support-only stats), support = blue + green (no core-only stats), mid = everything
STATS_BY_POSITION = {
    "core": RED_STATS + GREEN_STATS,
    "mid": ALL_STATS,
    "support": BLUE_STATS + GREEN_STATS,
}

def stat_score(stat, raw_value):
    value = float(raw_value)
    if stat == "deaths":
        return 1950 - 195 * value
    return value * STAT_WEIGHTS[stat]

def normalize_versus(versus):
    team_a, team_b = versus.split(" vs ")
    team_a, team_b = team_a.strip(), team_b.strip()
    return f"{team_a} vs {team_b}" if team_a <= team_b else f"{team_b} vs {team_a}"

with open(INPUT_FILE, "r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

match_info = {row["matchID"]: {"seriesID": row["seriesID"], "Versus": normalize_versus(row["Versus"])} for row in rows}
team_names_by_id = {row["teamID"]: row["teamName"] for row in rows}

# (matchID, teamID, position) -> player rows for that team+position in that single game
match_team_position_players = defaultdict(list)
for row in rows:
    match_team_position_players[(row["matchID"], row["teamID"], row["position"])].append(row)

# (seriesID, teamID, position) -> {matchID: [player rows]}
series_team_position_games = defaultdict(dict)
for (match_id, team_id, position), players in match_team_position_players.items():
    series_id = match_info[match_id]["seriesID"]
    series_team_position_games[(series_id, team_id, position)][match_id] = players

output_rows = []
for (series_id, team_id, position), games_by_match in series_team_position_games.items():
    applicable_stats = STATS_BY_POSITION[position]
    any_match_id = next(iter(games_by_match))
    any_players = games_by_match[any_match_id]

    row_out = {
        "seriesID": series_id,
        "Versus": match_info[any_match_id]["Versus"],
        "teamID": team_id,
        "teamName": team_names_by_id.get(team_id, ""),
        "position": position,
        "players": " & ".join(p["playerName"] for p in any_players),
    }

    for stat in ALL_STATS:
        if stat not in applicable_stats:
            row_out[stat] = ""
            continue

        game_scores = []
        for player_rows in games_by_match.values():
            per_player = [stat_score(stat, p[stat]) for p in player_rows]
            game_scores.append(sum(per_player) / len(per_player))

        game_scores.sort(reverse=True)
        best_two = game_scores[:2]
        row_out[stat] = round(sum(best_two), 2)

    output_rows.append(row_out)

POSITION_ORDER = {"core": 0, "mid": 1, "support": 2}
output_rows.sort(key=lambda r: (r["Versus"], r["teamName"], POSITION_ORDER.get(r["position"], 99)))

fieldnames = ["seriesID", "Versus", "teamID", "teamName", "position", "players"] + ALL_STATS

with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output_rows)

print(f"Wrote {len(output_rows)} rows to {OUTPUT_FILE}")
