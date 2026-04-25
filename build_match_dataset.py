import os
import json
import pandas as pd

DATA_FOLDER = "date - meciuri-final"

UCLUJ_TEAM_ID = 60374

all_vectors = []
ucluj_vectors = []

all_reports = []
ucluj_reports = []

files = os.listdir(DATA_FOLDER)

print("Total files found:", len(files))

all_count = 0
ucluj_count = 0

for file in files:

    if not file.endswith(".json"):
        continue

    path = os.path.join(DATA_FOLDER, file)

    with open(path, "r", encoding="utf-8") as f:

        data = json.load(f)

    if "players" not in data:
        continue

    players = data["players"]

    # =========================
    # ALL TEAMS METRICS
    # =========================

    total_passes = 0
    total_progressive = 0
    total_final_third = 0
    total_recoveries = 0
    total_losses = 0
    total_shots = 0

    for p in players:

        stats = p["total"]

        total_passes += stats.get("passes", 0)

        total_progressive += stats.get(
            "progressivePasses",
            0
        )

        total_final_third += stats.get(
            "passesToFinalThird",
            0
        )

        total_recoveries += stats.get(
            "recoveries",
            0
        )

        total_losses += stats.get(
            "losses",
            0
        )

        total_shots += stats.get(
            "shots",
            0
        )

    if total_passes == 0:
        continue

    progression_index = (
        total_progressive /
        total_passes
    )

    risk_index = (
        total_losses /
        total_passes
    )

    final_third_index = (
        total_final_third /
        total_passes
    )

    defensive_stability_index = (
        total_recoveries /
        total_passes
    )

    pressing_recovery_index = (
        total_recoveries /
        (total_losses + 1)
    )

    possession_security_index = (
        total_passes /
        (total_losses + 1)
    )

    attacking_threat_index = (
        total_shots /
        (total_passes + 1)
    )

    match_name = file.replace(
        "_players_stats.json",
        ""
    )

    vector_data = {

        "match": match_name,

        "progression_index":
            progression_index,

        "risk_index":
            risk_index,

        "final_third_index":
            final_third_index,

        "defensive_stability_index":
            defensive_stability_index,

        "pressing_recovery_index":
            pressing_recovery_index,

        "possession_security_index":
            possession_security_index,

        "attacking_threat_index":
            attacking_threat_index
    }

    all_vectors.append(vector_data)

    all_reports.append({

        "match": match_name,
        "cluster": 0,
        "predicted_quality": 1
    })

    all_count += 1

    # =========================
    # UCLUJ ONLY
    # =========================

    ucluj_players = [

        p for p in players

        if p["teamId"] == UCLUJ_TEAM_ID
    ]

    if len(ucluj_players) > 0:

        u_passes = 0
        u_progressive = 0
        u_final_third = 0
        u_recoveries = 0
        u_losses = 0
        u_shots = 0

        for p in ucluj_players:

            stats = p["total"]

            u_passes += stats.get("passes", 0)

            u_progressive += stats.get(
                "progressivePasses",
                0
            )

            u_final_third += stats.get(
                "passesToFinalThird",
                0
            )

            u_recoveries += stats.get(
                "recoveries",
                0
            )

            u_losses += stats.get(
                "losses",
                0
            )

            u_shots += stats.get(
                "shots",
                0
            )

        if u_passes > 0:

            u_vector = {

                "match": match_name,

                "progression_index":
                    u_progressive / u_passes,

                "risk_index":
                    u_losses / u_passes,

                "final_third_index":
                    u_final_third / u_passes,

                "defensive_stability_index":
                    u_recoveries / u_passes,

                "pressing_recovery_index":
                    u_recoveries / (u_losses + 1),

                "possession_security_index":
                    u_passes / (u_losses + 1),

                "attacking_threat_index":
                    u_shots / (u_passes + 1)
            }

            ucluj_vectors.append(u_vector)

            ucluj_reports.append({

                "match": match_name,
                "cluster": 0,
                "predicted_quality": 1
            })

            ucluj_count += 1

print("All matches processed:", all_count)
print("U Cluj matches processed:", ucluj_count)

# =========================
# SAVE FILES
# =========================

pd.DataFrame(all_vectors).to_csv(
    "all_match_vectors.csv",
    index=False
)

pd.DataFrame(all_reports).to_csv(
    "all_match_reports.csv",
    index=False
)

pd.DataFrame(ucluj_vectors).to_csv(
    "ucluj_match_vectors.csv",
    index=False
)

pd.DataFrame(ucluj_reports).to_csv(
    "ucluj_match_reports.csv",
    index=False
)

print("All datasets saved.")