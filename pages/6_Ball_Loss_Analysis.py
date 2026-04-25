import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Ball Pressure & Recovery Analysis")

UCLUJ_TEAM_ID = 60374

# =========================
# LOAD DATA
# =========================

player_df = pd.read_csv("player_stats.csv")

# =========================
# CHECK REQUIRED COLUMNS
# =========================

required_cols = [
    "recoveries",
    "interceptions"
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
# TEAM DEFENSIVE PRESSURE
# =========================

st.header("Defensive Pressure Overview")

total_interceptions = ucluj_players[
    "interceptions"
].sum()

total_recoveries = ucluj_players[
    "recoveries"
].sum()

pressure_df = pd.DataFrame({

    "Metric": [
        "Interceptions",
        "Recoveries"
    ],

    "Value": [
        total_interceptions,
        total_recoveries
    ]

})

fig_pressure = px.bar(

    pressure_df,

    x="Metric",

    y="Value",

    title="Team Defensive Pressure"

)

st.plotly_chart(fig_pressure)

# =========================
# TOP DEFENSIVE PLAYERS
# =========================

st.header("Top Defensive Players")

player_def_df = (
    ucluj_players
    .groupby("playerName")[
        [
            "interceptions",
            "recoveries"
        ]
    ]
    .sum()
    .reset_index()
)

player_def_df["defensive_score"] = (

    player_def_df["interceptions"] * 1.2 +

    player_def_df["recoveries"] * 1.0

)

player_def_df = player_def_df.sort_values(

    by="defensive_score",

    ascending=False

)

st.dataframe(

    player_def_df.head(10)

)

# =========================
# MATCH DEFENSIVE TREND
# =========================

st.header("Defensive Trend per Match")

if "match" in ucluj_players.columns:

    match_def_df = (

        ucluj_players

        .groupby("match")[
            [
                "interceptions",
                "recoveries"
            ]
        ]

        .sum()

        .reset_index()

    )

    fig_match = px.line(

        match_def_df,

        x="match",

        y=[
            "interceptions",
            "recoveries"
        ],

        title="Defensive Actions per Match"

    )

    st.plotly_chart(fig_match)

else:

    st.info(
        "Match column not available"
    )

# =========================
# POSITION DEFENSIVE LOAD
# =========================

st.header("Defensive Load by Position")

if "position" in ucluj_players.columns:

    position_df = (

        ucluj_players

        .groupby("position")[
            [
                "interceptions",
                "recoveries"
            ]
        ]

        .sum()

        .reset_index()

    )

    fig_position = px.bar(

        position_df,

        x="position",

        y=[
            "interceptions",
            "recoveries"
        ],

        title="Defensive Actions by Position"

    )

    st.plotly_chart(fig_position)

else:

    st.info(
        "Position column not available"
    )