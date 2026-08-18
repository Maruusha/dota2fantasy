import requests

GAME_ID = 8948311007  # replace with the actual Dota game ID

url = f"https://api.opendota.com/api/matches/{GAME_ID}"

response = requests.get(url, timeout=30)
response.raise_for_status()

data = response.json()

print("Match ID :", data.get("match_id"))
print("League ID:", data.get("leagueid"))
print("Start time:", data.get("start_time"))
print("Radiant:", data.get("radiant_name"))
print("Dire:", data.get("dire_name"))