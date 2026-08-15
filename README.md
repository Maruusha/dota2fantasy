# Dota 2 Fantasy

> Legacy version of my Dota 2 Fantasy League project, originally built for **The International 2025**.

This repository contains the data processing and statistics pipeline behind the original version of the project.

The application was built to collect match data, process player performance and generate additional Fantasy League statistics from competitive Dota 2 matches.

## ✦ Current version

The original project is no longer the main version.

The newer version of the project is available here:

**[Dota Fantasy 2026](https://bydoodle.github.io/dota-fantasy-2026/)**

This repository is kept as an archive and as a reference for the previous version of the project.

## What it does

The project processes competitive Dota 2 match data and calculates a wide range of statistics used by the Fantasy League system.

Among other things, it tracks:

* player performance and role-based statistics
* kills, deaths, assists and creep score
* GPM and other gameplay metrics
* wards, camps, runes, smokes and watchers
* Roshan, Tormentor and Courier kills
* teamfight participation and stuns
* first blood and pick order
* buybacks and other match events
* active item usage
* hero attributes and custom hero categories
* cosmetic / Arcana related statistics
* Dota Plus hero mastery
* various additional Fantasy titles and subtitles

The resulting data is stored locally in JSON files and used by the web application.

## Data sources

The parser uses data from:

* [OpenDota](https://www.opendota.com/)
* [STRATZ](https://stratz.com/)

OpenDota is used for match and player statistics, while STRATZ provides additional data that is not available through the standard OpenDota endpoints.

## Project structure

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

### Main scripts

`main.py`
Collects match data, calculates player statistics and updates the stored datasets.

`heroes_parser.py`
Fetches Dota 2 hero information and generates the local hero dataset.

`generate_heroes_values.py`
Initializes additional hero attributes used by the Fantasy system.

`items_with_active_abilities.py`
Fetches item data from STRATZ and generates a list of items with active abilities.

## Running the parser

To collect data yourself, create a `.env` file in the project root:

```env
STRATZ_TOKEN=your_token
```

A STRATZ API token can be obtained from:

[STRATZ API](https://stratz.com/api)

Then install the required Python packages and run the corresponding parser script.

> The dataset shipped with this repository is intended for the original project version and should not be treated as a live source of current Dota 2 data.

## Status

**Archived / Legacy**

This version was created for TI2025 and is no longer actively developed.

The project has since been redesigned and rebuilt for the next iteration.
