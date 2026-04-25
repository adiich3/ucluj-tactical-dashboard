import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Line Breaking Analysis")

UCLUJ_TEAM_ID = 60374

# =========================
# LOAD DATA
# =========================

player_df = pd.read_csv("player_stats.csv")

# =========================
# CHECK REQUIRED COLUMNS
# =========================

required_cols = [
    "passes",
    "shots",
    "assists"
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
# CREATE LINE BREAKING INDEX
# =========================

ucluj_players["line_breaking_index"] = (

    ucluj_players["assists"] * 1.5 +

    ucluj_players["shots"] * 1.2 +

    ucluj_players["passes"] * 0.05

)

# =========================
# TEAM LINE BREAKING OVERVIEW
# =========================

st.header("Team Line Breaking Overview")

total_lb = ucluj_players[
    "line_breaking_index"
].sum()

st.metric(
    label="Total Line Breaking Actions",
    value=round(total_lb, 2)
)

# =========================
# TOP LINE BREAKING PLAYERS
# =========================

st.header("Top Line Breaking Players")

player_lb_df = (

    ucluj_players

    .groupby("playerName")[
        ["line_breaking_index"]
    ]

    .sum()

    .reset_index()

)

player_lb_df = player_lb_df.sort_values(

    by="line_breaking_index",

    ascending=False

)

st.dataframe(

    player_lb_df.head(10)

)

fig_players = px.bar(

    player_lb_df.head(10),

    x="playerName",

    y="line_breaking_index",

    title="Top Line Breaking Players"

)

st.plotly_chart(fig_players)

# =========================
# MATCH LINE BREAKING TREND
# =========================

st.header("Line Breaking per Match")

if "match" in ucluj_players.columns:

    match_lb_df = (

        ucluj_players

        .groupby("match")[
            ["line_breaking_index"]
        ]

        .sum()

        .reset_index()

    )

    fig_match = px.line(

        match_lb_df,

        x="match",

        y="line_breaking_index",

        title="Line Breaking Trend per Match"

    )

    st.plotly_chart(fig_match)

else:

    st.info(
        "Match column not available"
    )

# =========================
# POSITION LINE BREAKING
# =========================

st.header("Line Breaking by Position")

if "position" in ucluj_players.columns:

    position_lb_df = (

        ucluj_players

        .groupby("position")[
            ["line_breaking_index"]
        ]

        .sum()

        .reset_index()

    )

    fig_position = px.bar(

        position_lb_df,

        x="position",

        y="line_breaking_index",

        title="Line Breaking by Position"

    )

    st.plotly_chart(fig_position)

else:

    st.info(
        "Position column not available"
    )

# =========================
# LINE BREAKING RATING
# =========================

st.header("Line Breaking Strength Rating")

avg_lb = ucluj_players[
    "line_breaking_index"
].mean()

rating = pd.cut(

    [avg_lb],

    bins=[-1, 5, 15, 1000],

    labels=[
        "Low",
        "Medium",
        "High"
    ]

)

st.metric(

    label="Team Line Breaking Level",

    value=rating[0]

)