import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Attacking Patterns Analysis")

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
    "shots",
    "assists",
    "passes"
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
# CREATE ATTACK INDEX
# =========================

ucluj_players["attacking_index"] = (

    ucluj_players["goals"] * 2 +

    ucluj_players["assists"] * 1.5 +

    ucluj_players["shots"] * 1.2 +

    ucluj_players["passes"] * 0.03

)

# =========================
# TEAM ATTACK OVERVIEW
# =========================

st.header("Team Attacking Overview")

total_attack = ucluj_players[
    "attacking_index"
].sum()

st.metric(
    label="Total Attacking Actions",
    value=round(total_attack, 2)
)

# =========================
# TOP ATTACKING PLAYERS
# =========================

st.header("Top Attacking Players")

player_attack_df = (

    ucluj_players

    .groupby("playerName")[
        ["attacking_index"]
    ]

    .sum()

    .reset_index()

)

player_attack_df = player_attack_df.sort_values(

    by="attacking_index",

    ascending=False

)

st.dataframe(
    player_attack_df.head(10)
)

fig_players = px.bar(

    player_attack_df.head(10),

    x="playerName",

    y="attacking_index",

    title="Top Attacking Players"

)

st.plotly_chart(fig_players)

# =========================
# MATCH ATTACK TREND
# =========================

st.header("Attacking Trend per Match")

if "match" in ucluj_players.columns:

    match_attack_df = (

        ucluj_players

        .groupby("match")[
            ["attacking_index"]
        ]

        .sum()

        .reset_index()

    )

    fig_match = px.line(

        match_attack_df,

        x="match",

        y="attacking_index",

        title="Attacking Trend per Match"

    )

    st.plotly_chart(fig_match)

else:

    st.info(
        "Match column not available"
    )

# =========================
# POSITION ATTACK STYLE
# =========================

st.header("Attacking by Position")

if "position" in ucluj_players.columns:

    position_attack_df = (

        ucluj_players

        .groupby("position")[
            ["attacking_index"]
        ]

        .sum()

        .reset_index()

    )

    fig_position = px.bar(

        position_attack_df,

        x="position",

        y="attacking_index",

        title="Attacking Contribution by Position"

    )

    st.plotly_chart(fig_position)

else:

    st.info(
        "Position column not available"
    )

# =========================
# ATTACK STYLE CLASSIFIER
# =========================

st.header("Team Attacking Style")

avg_goals = ucluj_players["goals"].mean()
avg_passes = ucluj_players["passes"].mean()

if avg_goals > 1.5:

    style = "Clinical Finishing"

elif avg_passes > 40:

    style = "Possession Attack"

else:

    style = "Direct Attack"

st.metric(
    label="Detected Attacking Style",
    value=style
)