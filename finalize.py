import os
import json
from collections import Counter

MATCH_FOLDER = "date - meciuri-updated"
OUTPUT_FOLDER = "date - meciuri-final"
TEAM_MAPPING_FILE = "team_mapping.json"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# incarcare mapping echipe

with open(TEAM_MAPPING_FILE, "r", encoding="utf-8") as f:
    team_mapping = json.load(f)

def is_active_player(player):

    total = player.get("total", {})

    if not isinstance(total, dict):
        return False

    for value in total.values():

        if isinstance(value, (int, float)) and value > 0:
            return True

    return False


for filename in os.listdir(MATCH_FOLDER):

    if not filename.endswith(".json"):
        continue

    filepath = os.path.join(MATCH_FOLDER, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    players = data.get("players", [])

    team_counter = Counter()

    # luam doar jucatori activi

    for player in players:

        if not is_active_player(player):
            continue

        team_id = player.get("teamId")

        if team_id:
            team_counter[str(team_id)] += 1

    most_common = team_counter.most_common(2)

    main_team_ids = []

    for t in most_common:
        main_team_ids.append(str(t[0]))

    # adaugare teamName

    for player in players:

        team_id = str(player.get("teamId"))

        if team_id in main_team_ids:

            if team_id in team_mapping:
                player["teamName"] = team_mapping[team_id]
            else:
                player["teamName"] = "Unknown"

        else:

            player["teamName"] = "Secondary"

    output_path = os.path.join(OUTPUT_FOLDER, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("Procesat:", filename)

print("Toate fisierele finalizate.")