import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Ball Loss Analysis")

UCLUJ_TEAM_ID = 60374

# =========================
# LOAD DATA
# =========================

player_df = pd.read_csv("player_stats.csv")

# =========================
# CHECK REQUIRED COLUMNS
# =========================

required_cols = ["losses"]

missing_cols = [
    c for c in required_cols
    if c not in player_df.columns
]

if len(missing_cols) > 0:

    st.error(
        f"Missing required columns: {missing_cols}"
    )

    st.stop()

# Optional columns

has_own_half = "ownHalfLosses" in player_df.columns
has_danger = "dangerousOwnHalfLosses" in player_df.columns

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
# LOSS ZONE DISTRIBUTION
# =========================

st.header("Ball Loss Zones Distribution")

total_losses = ucluj_players["losses"].sum()

own_losses = (
    ucluj_players["ownHalfLosses"].sum()
    if has_own_half
    else 0
)

danger_losses = (
    ucluj_players["dangerousOwnHalfLosses"].sum()
    if has_danger
    else 0
)

loss_zone_df = pd.DataFrame({

    "Zone": [
        "Total Losses",
        "Own Half Losses",
        "Dangerous Own Half Losses"
    ],

    "Value": [
        total_losses,
        own_losses,
        danger_losses
    ]

})

fig_loss_zone = px.bar(
    loss_zone_df,
    x="Zone",
    y="Value",
    title="Ball Loss Zones Overview"
)

st.plotly_chart(fig_loss_zone)

# =========================
# TOP LOSS PLAYERS
# =========================

st.header("Top Players with Most Ball Losses")

player_loss_df = (
    ucluj_players
    .groupby("playerName")[
        ["losses"]
    ]
    .sum()
    .reset_index()
)

player_loss_df = player_loss_df.sort_values(
    by="losses",
    ascending=False
)

st.dataframe(
    player_loss_df.head(10)
)

# =========================
# LOSS TREND PER MATCH
# =========================

st.header("Ball Loss Trend per Match")

if "match" in ucluj_players.columns:

    match_loss_df = (
        ucluj_players
        .groupby("match")[
            ["losses"]
        ]
        .sum()
        .reset_index()
    )

    fig_match_losses = px.line(
        match_loss_df,
        x="match",
        y="losses",
        title="Ball Losses per Match"
    )

    st.plotly_chart(fig_match_losses)

else:

    st.info(
        "Match column not available for trend analysis"
    )

# =========================
# LOSS RISK CLASSIFICATION
# =========================

st.header("Loss Risk Classification")

ucluj_players["loss_risk"] = pd.cut(

    ucluj_players["losses"],

    bins=[-1, 5, 15, 1000],

    labels=[
        "Low Risk",
        "Medium Risk",
        "High Risk"
    ]

)

risk_distribution = (
    ucluj_players
    .groupby("loss_risk")
    .size()
    .reset_index(name="count")
)

fig_risk = px.pie(

    risk_distribution,

    names="loss_risk",

    values="count",

    title="Loss Risk Distribution"

)

st.plotly_chart(fig_risk)

# =========================
# POSITION LOSS ANALYSIS
# =========================

st.header("Ball Loss by Position")

if "position" in ucluj_players.columns:

    position_loss_df = (
        ucluj_players
        .groupby("position")[
            ["losses"]
        ]
        .sum()
        .reset_index()
    )

    fig_position = px.bar(

        position_loss_df,

        x="position",

        y="losses",

        title="Ball Losses by Position"

    )

    st.plotly_chart(fig_position)

else:

    st.info(
        "Position column not available"
    )