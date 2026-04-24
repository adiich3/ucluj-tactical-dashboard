import os
import json
import pandas as pd

MATCH_FOLDER = "date - meciuri-final"
OUTPUT_FILE = "ucluj_match_vectors.csv"

UCLUJ_TEAM_ID = 60374

rows = []

def get_stat(player, key):

    total = player.get("total", {})
    return total.get(key, 0)


for filename in os.listdir(MATCH_FOLDER):

    if not filename.endswith(".json"):
        continue

    filepath = os.path.join(MATCH_FOLDER, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    players = data.get("players", [])

    ucluj_players = []

    for p in players:

        if p.get("teamId") == UCLUJ_TEAM_ID:
            ucluj_players.append(p)

    if len(ucluj_players) == 0:
        continue

    progression = 0
    risk = 0
    final_third = 0
    defensive = 0
    pressing = 0
    possession = 0
    attacking = 0

    for player in ucluj_players:

        progression += (
            get_stat(player, "progressivePasses")
            + get_stat(player, "passesToFinalThird")
            + get_stat(player, "successfulVerticalPasses")
        )

        risk += (
            get_stat(player, "losses")
            + 2 * get_stat(player, "ownHalfLosses")
            + 4 * get_stat(player, "dangerousOwnHalfLosses")
        )

        final_third += (
            get_stat(player, "touchInBox")
            + get_stat(player, "keyPasses")
            + get_stat(player, "shotsOnTarget")
        )

        defensive += (
            get_stat(player, "recoveries")
            + get_stat(player, "interceptions")
            + get_stat(player, "clearances")
        )

        pressing += (
            get_stat(player, "pressingDuelsWon")
            + get_stat(player, "counterpressingRecoveries")
        )

        possession += (
            get_stat(player, "successfulPasses")
            - get_stat(player, "losses")
        )

        attacking += (
            get_stat(player, "xgShot")
            + get_stat(player, "xgAssist")
            + get_stat(player, "shots")
        )

    row = {
        "match": filename,
        "progression_index": progression,
        "risk_index": risk,
        "final_third_index": final_third,
        "defensive_stability_index": defensive,
        "pressing_recovery_index": pressing,
        "possession_security_index": possession,
        "attacking_threat_index": attacking
    }

    rows.append(row)

df = pd.DataFrame(rows)

df.to_csv(OUTPUT_FILE, index=False)

print("Vectori tactici generati.")
print("Numar meciuri U Cluj:", len(df))