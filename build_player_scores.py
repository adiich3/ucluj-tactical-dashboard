import json
import os
import pandas as pd

MATCH_FOLDER = "date - meciuri-final"

rows = []

for filename in os.listdir(MATCH_FOLDER):

    if not filename.endswith(".json"):
        continue

    filepath = os.path.join(
        MATCH_FOLDER,
        filename
    )

    try:

        with open(filepath, "r", encoding="utf-8") as f:

            data = json.load(f)

            players = data["players"]

            for p in players:

                stats = p.get("total", {})

                goals = stats.get("goals", 0)
                assists = stats.get("assists", 0)
                shots = stats.get("shots", 0)
                passes = stats.get("successfulPasses", 0)
                interceptions = stats.get("interceptions", 0)
                recoveries = stats.get("recoveries", 0)

                losses = stats.get("losses", 0)
                xg = stats.get("xgShot", 0)

                # scor jucator imbunatatit

                player_score = (
                    goals * 1.5 +
                    assists * 1.2 +
                    shots * 0.1 +
                    passes * 0.02 +
                    interceptions * 0.05 +
                    recoveries * 0.04 +
                    xg * 0.5 -
                    losses * 0.03
                )

                rows.append({
                    "match": filename,
                    "playerName": p.get("playerName"),
                    "teamId": p.get("teamId"),
                    "position": p.get("position"),
                    "goals": goals,
                    "assists": assists,
                    "shots": shots,
                    "passes": passes,
                    "interceptions": interceptions,
                    "recoveries": recoveries,
                    "player_score": round(player_score, 2)
                })

    except Exception as e:

        print("Eroare la:", filename)

df = pd.DataFrame(rows)

df.to_csv(
    "player_stats.csv",
    index=False
)

print("Fisier creat: player_stats.csv")

print("Total randuri:", len(df))
print("Jucatori unici:",
      df["playerName"].nunique())