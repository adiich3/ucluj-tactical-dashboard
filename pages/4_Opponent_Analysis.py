import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Opponent Analysis")

UCLUJ_TEAM_ID = 60374

# =========================
# LOAD DATA
# =========================

player_df = pd.read_csv("player_stats.csv")

# filtrare U Cluj

ucluj_players = player_df[
    player_df["teamId"] == UCLUJ_TEAM_ID
].copy()

# filtrare adversari

opponent_players = player_df[
    player_df["teamId"] != UCLUJ_TEAM_ID
].copy()

# =========================
# BASIC CHECK
# =========================

st.header("Opponent Overview")

st.write(
    "Total players:",
    len(player_df)
)

st.write(
    "Opponent players:",
    len(opponent_players)
)

# =========================
# TEAM LIST
# =========================

teams = (
    opponent_players
    .groupby("teamId")
    .size()
    .reset_index(name="matches")
)

if len(teams) == 0:

    st.warning("No opponent teams found")

else:

    selected_team = st.selectbox(
        "Select Opponent Team",
        teams["teamId"]
    )

    team_players = opponent_players[
        opponent_players["teamId"]
        == selected_team
    ]

    # =========================
    # TEAM STATS
    # =========================

    st.subheader("Opponent Team Stats")

    goals_sum = team_players["goals"].sum()
    assists_sum = team_players["assists"].sum()
    passes_sum = team_players["passes"].sum()
    interceptions_sum = team_players["interceptions"].sum()
    recoveries_sum = team_players["recoveries"].sum()

    stats_df = pd.DataFrame({
        "Metric": [
            "Goals",
            "Assists",
            "Passes",
            "Interceptions",
            "Recoveries"
        ],
        "Value": [
            goals_sum,
            assists_sum,
            passes_sum,
            interceptions_sum,
            recoveries_sum
        ]
    })

    fig = px.bar(
        stats_df,
        x="Metric",
        y="Value",
        title="Opponent Performance Overview"
    )

    st.plotly_chart(fig)

    # =========================
    # TOP PLAYERS
    # =========================

    st.subheader("Top Opponent Players")

    top_players = (
        team_players
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