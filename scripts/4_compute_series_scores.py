import csv
import os
from collections import defaultdict

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")
INPUT_FILE = os.path.join(ROOT_DIR, "data", "main_event", "total.csv")
OUTPUT_FILE = os.path.join(ROOT_DIR, "data", "main_event", "series_scores.csv")

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

def game_score(row):
    total = 0
    for stat, weight in STAT_WEIGHTS.items():
        total += float(row[stat]) * weight
    total += 1950 - 195 * float(row["deaths"])
    return total

def normalize_versus(versus):
    team_a, team_b = versus.split(" vs ")
    team_a, team_b = team_a.strip(), team_b.strip()
    return f"{team_a} vs {team_b}" if team_a <= team_b else f"{team_b} vs {team_a}"

with open(INPUT_FILE, "r", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

# Per-player-per-game total raw score
player_game_scores = {}
for row in rows:
    key = (row["matchID"], row["playerID"])
    player_game_scores[key] = game_score(row)

# Group into (matchID, teamID, position) -> list of player rows, to pair core/support
match_team_position_players = defaultdict(list)
for row in rows:
    match_team_position_players[(row["matchID"], row["teamID"], row["position"])].append(row)

# Position game score per (matchID, teamID, position): mid = solo score,
# core/support = the pair's two scores combined and divided by 2.
position_game_score = {}
series_versus_by_series = {}
match_info = {}
for (match_id, team_id, position), players in match_team_position_players.items():
    scores = [player_game_scores[(match_id, p["playerID"])] for p in players]
    position_game_score[(match_id, team_id, position)] = sum(scores) / len(scores)

for row in rows:
    match_info[row["matchID"]] = {
        "seriesID": row["seriesID"],
        "Versus": normalize_versus(row["Versus"]),
    }
    series_versus_by_series[row["seriesID"]] = normalize_versus(row["Versus"])

# Group position game scores into series: (seriesID, teamID, position) -> [(matchID, score), ...]
series_position_games = defaultdict(list)
for (match_id, team_id, position), score in position_game_score.items():
    series_id = match_info[match_id]["seriesID"]
    series_position_games[(series_id, team_id, position)].append((match_id, score))

team_names_by_id = {row["teamID"]: row["teamName"] for row in rows}

output_rows = []
for (series_id, team_id, position), games in series_position_games.items():
    games_sorted = sorted(games, key=lambda g: g[1], reverse=True)
    best_games = games_sorted[:2]
    series_score = sum(score for _, score in best_games)
    output_rows.append({
        "seriesID": series_id,
        "Versus": series_versus_by_series[series_id],
        "teamID": team_id,
        "teamName": team_names_by_id.get(team_id, ""),
        "position": position,
        "games_played": len(games_sorted),
        "games_counted": len(best_games),
        "series_score": round(series_score, 2),
    })

POSITION_ORDER = {"core": 0, "mid": 1, "support": 2}
output_rows.sort(key=lambda r: (r["Versus"], r["teamName"], POSITION_ORDER.get(r["position"], 99)))

fieldnames = ["seriesID", "Versus", "teamID", "teamName", "position", "games_played", "games_counted", "series_score"]

with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output_rows)

print(f"Wrote {len(output_rows)} rows to {OUTPUT_FILE}")
