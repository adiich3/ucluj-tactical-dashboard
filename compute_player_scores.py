import os
import json

MATCH_FOLDER = "date - meciuri-final"
OUTPUT_FOLDER = "date - meciuri-scored"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

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

    for player in players:

        # Offensive

        offensive = (
            get_stat(player, "goals") * 5
            + get_stat(player, "assists") * 4
            + get_stat(player, "xgShot") * 3
            + get_stat(player, "xgAssist") * 3
            + get_stat(player, "shotsOnTarget") * 1.5
            + get_stat(player, "keyPasses") * 1.2
            + get_stat(player, "touchInBox") * 0.5
        )

        # Defensive

        defensive = (
            get_stat(player, "duelsWon") * 0.5
            + get_stat(player, "interceptions") * 1.2
            + get_stat(player, "recoveries") * 1
            + get_stat(player, "clearances") * 1
            + get_stat(player, "successfulDefensiveAction") * 1
            + get_stat(player, "pressingDuelsWon") * 0.8
        )

        # Progression

        progression = (
            get_stat(player, "progressivePasses") * 1
            + get_stat(player, "successfulProgressivePasses") * 1.2
            + get_stat(player, "progressiveRun") * 1
            + get_stat(player, "passesToFinalThird") * 0.5
        )

        # Risk

        risk = (
            get_stat(player, "losses") * 0.5
            + get_stat(player, "ownHalfLosses") * 1
            + get_stat(player, "dangerousOwnHalfLosses") * 2
            + get_stat(player, "missedBalls") * 0.8
        )

        final_score = (
            offensive
            + defensive
            + progression
            - risk
        )

        player["scores"] = {
            "offensive": round(offensive, 2),
            "defensive": round(defensive, 2),
            "progression": round(progression, 2),
            "risk": round(risk, 2),
            "finalScore": round(final_score, 2)
        }

    output_path = os.path.join(OUTPUT_FOLDER, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("Procesat:", filename)

print("Player scores calculate.")