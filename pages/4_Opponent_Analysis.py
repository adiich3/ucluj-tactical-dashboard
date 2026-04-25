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
# =========================
# U CLUJ VS OPPONENT COMPARISON
# =========================

st.header("U Cluj vs Opponent Tactical Comparison")

vectors = pd.read_csv("ucluj_match_vectors.csv")

ucluj_vectors = vectors[
    vectors["match"].str.contains(
        "Universitatea Cluj",
        case=False,
        na=False
    )
]

opponent_vectors = ucluj_vectors[
    ucluj_vectors["match"].str.contains(
        selected_opponent,
        case=False,
        na=False
    )
]

if len(opponent_vectors) > 0:

    avg_metrics = opponent_vectors.mean(numeric_only=True)

    comparison_df = pd.DataFrame({
        "Metric": [
            "Attack",
            "Progression",
            "Possession",
            "Defense",
            "Risk"
        ],
        "Value": [
            avg_metrics["attacking_threat_index"],
            avg_metrics["progression_index"],
            avg_metrics["possession_security_index"],
            avg_metrics["defensive_stability_index"],
            avg_metrics["risk_index"]
        ]
    })

    fig_compare = px.bar(
        comparison_df,
        x="Metric",
        y="Value",
        title="Average Tactical Profile vs Opponent"
    )

    st.plotly_chart(fig_compare)

else:

    st.warning("No tactical data found vs this opponent")
