# Dota 2 Fantasy 2026

This project is forked from bydoodle/dota2fantasy (https://github.com/bydoodle/dota2fantasy)

This repository contains the data processing and statistics pipeline behind the original version of the project. The application was built to collect match data, process player performance and generate additional Fantasy League statistics from just The International 2026 matches.

## ✦ Current version

The original project is from 2025. I disagree with some processing pipeline, so i decide to rewrite that logic and keep only the React + Vite part with few modifications.

The newer version of the project is available here:

[**Dota Fantasy 2026**](https://maruusha.github.io/dota2fantasy/)

This repository will get update every year from now on (hopefully).

## What it does

The project processes competitive Dota 2 match data and calculates a wide range of statistics used by the Fantasy League system.

The resulting data is stored locally in CSV files and used by the web application.

## Data sources

The parser uses data from:

- [OpenDota](https://www.opendota.com/)

## Project structure (to-do)

```text
.
├── main.py
├── heroes_parser.py
├── data/heroes.json
├── leagues.json
├── players_stat.json
├── scripts/
│   ├── crawl_group_stage_matches.py
│   ├── group_stage_matches_to_csv.py
│   └── compute_fantasy_score.py
├── archive/
│   ├── generate_heroes_values.py
│   ├── items_with_active_abilities.py
│   ├── active_items.json
│   └── leagues.temp.json
└── dota2parser/
```

### Main scripts (to-do)

`scripts/`Collects match data, calculates player statistics and updates the stored datasets.

## TODO (next year)

Filter by team

Suggest by Kams - Average of all stat by 1 position in **Best Stat Scores**

Suggest by Kams - Select players, select X number of best game (by stat of choice), show X heros that player play, border hero icon with the color same as its color (for the prefix, might work with suffix). By me, show how much point gained if select this prefix for these X matches

Auto-loaded your stats with json: You input once, i export you json string, you keep somewhere, when you need to check score again, you paste the json string in (Or CV script to read <span style="color: rgb(8, 8, 9);">stat image - OCR</span>)

## Status

**Ongoing (update data everyday until the event ends)**