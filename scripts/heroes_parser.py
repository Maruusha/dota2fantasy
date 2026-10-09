import requests
import json
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HEROES_PATH = PROJECT_ROOT / 'data' / '2026' / 'heroes.json'

try:
    with HEROES_PATH.open('r', encoding='utf-8') as f:
        heroes_info = json.load(f)
except FileNotFoundError:
    heroes_info = {}

heroes = requests.get(f"https://api.opendota.com/api/heroes").json()

for hero in heroes:
    heroes_info[hero['id']] = {
        'name': hero['localized_name'],
        'attr': hero['primary_attr']
    }

with HEROES_PATH.open("w", encoding="utf-8") as f:
    json.dump(heroes_info, f, ensure_ascii=False, indent=4)
