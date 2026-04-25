import os
import json
import pandas as pd

DATA_FOLDER = "date - meciuri-final"
UCLUJ_TEAM_ID = 60374

all_vectors = []
all_reports = []

files = os.listdir(DATA_FOLDER)

print("Total files found:", len(files))

for file in files:

    if not file.endswith(".json"):
        continue

    path = os.path.join(DATA_FOLDER, file)

    try:

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

    except Exception as e:

        print("Error reading:", file)
        continue

    players = []

    for p in data:

        if "teamId" not in p:
            continue

        if p["teamId"] == UCLUJ_TEAM_ID:

            players.append(p)

    if len(players) == 0:
        continue

    progression = 0
    risk = 0
    final_third = 0
    defense = 0
    pressing = 0
    possession = 0
    attack = 0

    for p in players:

        progression += p.get("passes", 0)

        risk += p.get("losses", 0)

        final_third += p.get("shots", 0)

        defense += (
            p.get("interceptions", 0)
            + p.get("recoveries", 0)
        )

        pressing += p.get("interceptions", 0)

        possession += p.get("passes", 0)

        attack += (
            p.get("goals", 0)
            + p.get("assists", 0)
        )

    match_name = file.replace("_players_stats.json", "")

    vector = {

        "match": match_name,

        "progression_index": progression,

        "risk_index": risk,

        "final_third_index": final_third,

        "defensive_stability_index": defense,

        "pressing_recovery_index": pressing,

        "possession_security_index": possession,

        "attacking_threat_index": attack

    }

    all_vectors.append(vector)

    report = {

        "match": match_name,

        "cluster": 0,

        "predicted_quality": 0

    }

    all_reports.append(report)

print("Processed matches:", len(all_vectors))

vectors_df = pd.DataFrame(all_vectors)

reports_df = pd.DataFrame(all_reports)

vectors_df.to_csv(
    "ucluj_match_vectors.csv",
    index=False
)

reports_df.to_csv(
    "match_tactical_reports.csv",
    index=False
)

print("CSV files generated successfully")