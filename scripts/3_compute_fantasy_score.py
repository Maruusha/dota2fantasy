import csv
import os

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")
INPUT_FILE = os.path.join(ROOT_DIR, "data", "main_event", "total.csv")
OUTPUT_FILE = os.path.join(ROOT_DIR, "data", "main_event", "fantasy_score.csv")

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
    "courier_kills",
]

POSITION_ORDER = {"core": 0, "mid": 1, "support": 2}

def score_stat(stat, raw_value):
    value = float(raw_value)
    if stat == "deaths":
        return 1950 - 195 * value
    return value * STAT_WEIGHTS[stat]

def normalize_versus(versus):
    # radiant/dire side (and therefore team order in "Versus") can flip between
    # games of the same series, so sort/group on an alphabetically fixed order.
    team_a, team_b = versus.split(" vs ")
    team_a, team_b = team_a.strip(), team_b.strip()
    return f"{team_a} vs {team_b}" if team_a <= team_b else f"{team_b} vs {team_a}"

with open(INPUT_FILE, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

output_rows = []
for row in rows:
    output_row = {
        "matchID": row["matchID"],
        "seriesID": row["seriesID"],
        "Versus": normalize_versus(row["Versus"]),
        "Game_number": int(row["Game_number"]),
        "gametime": int(row["gametime"]),
        "isLastGame": int(row["isLastGame"]),
        "playerID": row["playerID"],
        "playerName": row["playerName"],
        "teamID": row["teamID"],
        "teamName": row["teamName"],
        "position": row["position"],
        "heroID": row["heroID"],
        "heroName": row["heroName"],
    }
    for stat in STAT_COLUMNS:
        output_row[stat] = round(score_stat(stat, row[stat]), 2)
    output_row["date"] = row["date"]
    output_rows.append(output_row)

output_rows.sort(key=lambda r: (
    r["Versus"],
    r["Game_number"],
    POSITION_ORDER.get(r["position"], 99),
))

fieldnames = ["matchID", "seriesID", "Versus", "Game_number", "gametime", "isLastGame", "playerID", "playerName", "teamID", "teamName", "position", "heroID", "heroName"] + STAT_COLUMNS + ["date"]

with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(output_rows)

print(f"Wrote {len(output_rows)} rows to {OUTPUT_FILE}")
