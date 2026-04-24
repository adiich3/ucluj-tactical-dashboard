import os
import json

MATCH_FOLDER = "date - meciuri-final"

for filename in os.listdir(MATCH_FOLDER):

    if not filename.endswith(".json"):
        continue

    filepath = os.path.join(MATCH_FOLDER, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    players = data.get("players", [])

    for player in players:

        total = player.get("total")

        if isinstance(total, dict):

            print("Fisier:", filename)
            print("Metrici gasite in total:\n")

            for key in total.keys():
                print(key)

            exit()