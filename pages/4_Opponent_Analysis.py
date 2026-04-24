import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Opponent Analysis")

UCLUJ_TEAM_ID = 60374

# =========================
# LOAD DATA
# =========================

player_df = pd.read_csv("player_stats.csv")
match_reports = pd.read_csv("match_tactical_reports.csv")

# =========================
# GET OPPONENT LIST
# =========================

ucluj_matches = match_reports[
    match_reports["match"].str.contains(
        "Universitatea Cluj",
        case=False,
        na=False
    )
]

opponents = []

for m in ucluj_matches["match"]:

    teams = m.split(" - ")

    if len(teams) == 2:

        t1 = teams[0].strip()
        t2 = teams[1].split(",")[0].strip()

        if "Universitatea Cluj" in t1:
            opponents.append(t2)

        else:
            opponents.append(t1)

opponents = sorted(list(set(opponents)))

# =========================
# SELECT OPPONENT
# =========================

if len(opponents) == 0:

    st.warning("No opponent matches found")

else:

    selected_opponent = st.selectbox(
        "Select Opponent",
        opponents
    )

    st.header("Matches vs Opponent")

    opponent_matches = ucluj_matches[
        ucluj_matches["match"].str.contains(
            selected_opponent,
            case=False,
            na=False
        )
    ]

    st.dataframe(opponent_matches)

    # =========================
    # OPPONENT PLAYER STATS
    # =========================

    st.header("Opponent Player Performance")

    opponent_players = player_df[
        player_df["teamId"] != UCLUJ_TEAM_ID
    ]

    top_players = (
        opponent_players
        .groupby("playerName")[
            [
                "goals",
                "assists",
                "passes",
                "interceptions",
                "recoveries"
            ]
        ]
        .mean()
        .reset_index()
    )

    top_players["performance_score"] = (
        top_players["goals"] * 1.5 +
        top_players["assists"] * 1.2 +
        top_players["passes"] * 0.05 +
        top_players["interceptions"] * 0.7 +
        top_players["recoveries"] * 0.7
    )

    top_players = top_players.sort_values(
        by="performance_score",
        ascending=False
    )

    st.dataframe(
        top_players.head(10)
    )

    # =========================
    # MATCH CLUSTER TYPES
    # =========================

    st.header("Opponent Match Types")

    cluster_counts = (
        opponent_matches["cluster"]
        .value_counts()
        .reset_index()
    )

    cluster_counts.columns = [
        "Cluster",
        "Matches"
    ]

    fig = px.bar(
        cluster_counts,
        x="Cluster",
        y="Matches",
        title="Match Types vs Opponent"
    )

    st.plotly_chart(fig)