import os
import json
import re
from collections import defaultdict, Counter

MATCH_FOLDER = "date - meciuri-updated"
OUTPUT_FILE = "team_mapping.json"
UNKNOWN_FILE = "unknown_team_ids.json"

team_votes = defaultdict(lambda: defaultdict(int))
all_team_ids = set()

def extract_teams(filename):

    name = filename.replace(".json", "")

    parts = re.split(r"\s*-\s*", name)

    if len(parts) >= 2:

        team1 = parts[0].strip()
        team2 = parts[1].split(",")[0].strip()

        return team1, team2

    return None, None


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

    team1, team2 = extract_teams(filename)

    if not team1 or not team2:
        continue

    filepath = os.path.join(MATCH_FOLDER, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    players = data.get("players", [])

    team_counter = Counter()

    for player in players:

        if not is_active_player(player):
            continue

        team_id = player.get("teamId")

        if team_id:
            team_counter[team_id] += 1
            all_team_ids.add(team_id)

    most_common = team_counter.most_common(2)

    if len(most_common) < 2:
        continue

    id1 = most_common[0][0]
    id2 = most_common[1][0]

    team_votes[id1][team1] += 1
    team_votes[id2][team2] += 1


final_mapping = {}

for team_id in team_votes:

    votes = team_votes[team_id]

    best_name = max(votes, key=votes.get)

    final_mapping[team_id] = best_name


unknown_ids = []

for team_id in all_team_ids:

    if team_id not in final_mapping:
        unknown_ids.append(team_id)


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(final_mapping, f, indent=4, ensure_ascii=False)

with open(UNKNOWN_FILE, "w", encoding="utf-8") as f:
    json.dump(unknown_ids, f, indent=4)

print("Team mapping creat:", len(final_mapping))
print("TeamId fara mapping:", len(unknown_ids))
