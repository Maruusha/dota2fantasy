import requests
import json
import os
import time

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MATCHES_DIR = os.path.join(DATA_DIR, "main_event", "matches")
EXISTING_IDS_FILE = os.path.join(DATA_DIR, "match_existed_id.txt")

os.makedirs(MATCHES_DIR, exist_ok=True)

with open(os.path.join(os.path.dirname(__file__), "..", "leagues.json"), "r", encoding="utf-8") as f:
    leagues_data = json.load(f)

league_ids = list(map(int, leagues_data.keys()))

if os.path.exists(EXISTING_IDS_FILE):
    with open(EXISTING_IDS_FILE, "r", encoding="utf-8") as f:
        existing_ids = {line.strip() for line in f if line.strip()}
else:
    existing_ids = set()

def mark_downloaded(match_id):
    existing_ids.add(str(match_id))
    with open(EXISTING_IDS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{match_id}\n")

for league_id in league_ids:
    matches = requests.get(f"https://api.opendota.com/api/leagues/{league_id}/matches").json()
    time.sleep(1.2)

    for match in matches:
        match_id = match["match_id"]

        if str(match_id) in existing_ids:
            continue

        match_r = requests.get(f"https://api.opendota.com/api/matches/{match_id}").json()

        max_retries = 3
        for attempt in range(max_retries):
            if "players" in match_r:
                break
            print(f"Failed to fetch match {match_id} (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                time.sleep(3)
                match_r = requests.get(f"https://api.opendota.com/api/matches/{match_id}").json()
        else:
            print(f"Skipping match {match_id} after {max_retries} failed attempts")
            time.sleep(1.2)
            continue

        match_path = os.path.join(MATCHES_DIR, f"{match_id}.json")
        with open(match_path, "w", encoding="utf-8") as f:
            json.dump(match_r, f, ensure_ascii=False, indent=4)

        mark_downloaded(match_id)
        print(f"Saved match {match_id}")

        time.sleep(1.2)
