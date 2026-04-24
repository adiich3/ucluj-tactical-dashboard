import os
import json

# ===== CONFIG =====

PLAYERS_FILE = "players.json"
MATCH_FOLDER = "date - meciuri"
OUTPUT_FOLDER = "date - meciuri-updated"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ===== incarcare lista jucatori =====

with open(PLAYERS_FILE, "r", encoding="utf-8") as f:
    players_data = json.load(f)

player_map = {}

for p in players_data["players"]:

    player_id = str(p["wyId"])

    first = p.get("firstName", "").strip()
    last = p.get("lastName", "").strip()

    full_name = (first + " " + last).strip()

    team_id = p.get("currentTeamId")

    role = p.get("role", {}).get("name")

    player_map[player_id] = {
        "playerName": full_name,
        "teamId": team_id,
        "position": role
    }

print("Player mapping creat:", len(player_map))

# ===== procesare fisiere meci =====

for filename in os.listdir(MATCH_FOLDER):

    if not filename.endswith(".json"):
        continue

    filepath = os.path.join(MATCH_FOLDER, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        match_data = json.load(f)

    players = match_data.get("players", [])

    updated = 0

    for player in players:

        player_id = str(player.get("playerId"))

        if player_id in player_map:

            info = player_map[player_id]

            player["playerName"] = info["playerName"]
            player["teamId"] = info["teamId"]
            player["position"] = info["position"]

            updated += 1

        else:

            player["playerName"] = "Unknown"
            player["teamId"] = None
            player["position"] = None

    # ===== salvare fisier nou =====

    output_path = os.path.join(OUTPUT_FOLDER, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(match_data, f, indent=4, ensure_ascii=False)

    print(filename, "→ actualizati:", updated)

print("Proces complet.")