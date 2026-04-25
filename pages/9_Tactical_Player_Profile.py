import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Tactical Player Profile")

UCLUJ_TEAM_ID = 60374

# =========================
# LOAD DATA
# =========================

player_df = pd.read_csv("player_stats.csv")

# =========================
# CHECK REQUIRED COLUMNS
# =========================

required_cols = [
    "goals",
    "assists",
    "shots",
    "passes",
    "interceptions",
    "recoveries",
    "playerName"
]

missing_cols = [
    c for c in required_cols
    if c not in player_df.columns
]

if len(missing_cols) > 0:

    st.error(
        f"Missing required columns: {missing_cols}"
    )

    st.stop()

# =========================
# FILTER U CLUJ DATA
# =========================

ucluj_players = player_df[
    player_df["teamId"] == UCLUJ_TEAM_ID
].copy()

if len(ucluj_players) == 0:

    st.warning(
        "No Universitatea Cluj data found"
    )

    st.stop()

# =========================
# CREATE TACTICAL SCORES
# =========================

ucluj_players["attacking_score"] = (

    ucluj_players["goals"] * 2 +

    ucluj_players["assists"] * 1.5 +

    ucluj_players["shots"] * 1.2

)

ucluj_players["defensive_score"] = (

    ucluj_players["interceptions"] * 1.3 +

    ucluj_players["recoveries"] * 1.0

)

ucluj_players["playmaking_score"] = (

    ucluj_players["passes"] * 0.05 +

    ucluj_players["assists"] * 1.2

)

ucluj_players["overall_score"] = (

    ucluj_players["attacking_score"] * 0.4 +

    ucluj_players["defensive_score"] * 0.3 +

    ucluj_players["playmaking_score"] * 0.3

)

# =========================
# PLAYER SELECTION
# =========================

st.header("Select Player")

player_list = sorted(
    ucluj_players["playerName"].unique()
)

selected_player = st.selectbox(
    "Choose Player",
    player_list
)

player_data = ucluj_players[
    ucluj_players["playerName"]
    == selected_player
]

# =========================
# PLAYER SUMMARY
# =========================

st.header("Player Tactical Scores")

attack_val = player_data[
    "attacking_score"
].mean()

defense_val = player_data[
    "defensive_score"
].mean()

play_val = player_data[
    "playmaking_score"
].mean()

overall_val = player_data[
    "overall_score"
].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Attack",
    round(attack_val, 2)
)

col2.metric(
    "Defense",
    round(defense_val, 2)
)

col3.metric(
    "Playmaking",
    round(play_val, 2)
)

col4.metric(
    "Overall",
    round(overall_val, 2)
)

# =========================
# RADAR CHART
# =========================

st.header("Player Tactical Radar")

radar_df = pd.DataFrame({

    "Metric": [
        "Attack",
        "Defense",
        "Playmaking"
    ],

    "Value": [
        attack_val,
        defense_val,
        play_val
    ]

})

fig_radar = px.line_polar(

    radar_df,

    r="Value",

    theta="Metric",

    line_close=True

)

st.plotly_chart(fig_radar)

# =========================
# TOP PLAYERS BY CATEGORY
# =========================

st.header("Top Players by Tactical Category")

player_summary = (

    ucluj_players

    .groupby("playerName")[

        [
            "attacking_score",
            "defensive_score",
            "playmaking_score",
            "overall_score"

        ]

    ]

    .mean()

    .reset_index()

)

colA, colB, colC = st.columns(3)

with colA:

    st.subheader("Top Attackers")

    top_attack = player_summary.sort_values(

        by="attacking_score",

        ascending=False

    )

    st.dataframe(
        top_attack.head(5)
    )

with colB:

    st.subheader("Top Defenders")

    top_def = player_summary.sort_values(

        by="defensive_score",

        ascending=False

    )

    st.dataframe(
        top_def.head(5)
    )

with colC:

    st.subheader("Top Overall")

    top_overall = player_summary.sort_values(

        by="overall_score",

        ascending=False

    )

    st.dataframe(
        top_overall.head(5)
    )