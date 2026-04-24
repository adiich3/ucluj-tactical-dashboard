import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.title("Team Overview")

UCLUJ_TEAM_ID = 60374

# =========================
# LOAD DATA
# =========================

player_df = pd.read_csv("player_stats.csv")

ucluj_players = player_df[
    player_df["teamId"] == UCLUJ_TEAM_ID
].copy()

metrics = [
    "goals",
    "assists",
    "shots",
    "passes",
    "interceptions",
    "recoveries"
]

# =========================
# SEASON SUMMARY
# =========================

st.header("Season Summary")

total_matches = (
    ucluj_players["match"]
    .nunique()
)

total_goals = (
    ucluj_players["goals"]
    .sum()
)

total_assists = (
    ucluj_players["assists"]
    .sum()
)

total_shots = (
    ucluj_players["shots"]
    .sum()
)

st.write("Total Matches:", total_matches)
st.write("Total Goals:", total_goals)
st.write("Total Assists:", total_assists)
st.write("Total Shots:", total_shots)

# =========================
# GOALS TREND
# =========================

st.header("Goals per Match")

goals_per_match = (
    ucluj_players
    .groupby("match")["goals"]
    .sum()
    .reset_index()
)

fig_goals = px.line(
    goals_per_match,
    x="match",
    y="goals"
)

st.plotly_chart(fig_goals)

# =========================
# ASSISTS TREND
# =========================

st.header("Assists per Match")

assists_per_match = (
    ucluj_players
    .groupby("match")["assists"]
    .sum()
    .reset_index()
)

fig_assists = px.line(
    assists_per_match,
    x="match",
    y="assists"
)

st.plotly_chart(fig_assists)

# =========================
# SHOTS TREND
# =========================

st.header("Shots per Match")

shots_per_match = (
    ucluj_players
    .groupby("match")["shots"]
    .sum()
    .reset_index()
)

fig_shots = px.line(
    shots_per_match,
    x="match",
    y="shots"
)

st.plotly_chart(fig_shots)

# =========================
# TEAM STRENGTH INDEX
# =========================

st.header("Team Strength Index")

team_strength_rows = []

for m in metrics:

    avg_val = (
        ucluj_players[m]
        .mean()
    )

    team_strength_rows.append({
        "Metric": m,
        "Average": avg_val
    })

strength_df = pd.DataFrame(
    team_strength_rows
)

fig_strength = px.bar(
    strength_df,
    x="Metric",
    y="Average"
)

st.plotly_chart(fig_strength)

# =========================
# ATTACK VS DEFENSE
# =========================

st.header("Attack vs Defense Balance")

attack_value = (
    ucluj_players["goals"].sum() +
    ucluj_players["assists"].sum() +
    ucluj_players["shots"].sum()
)

defense_value = (
    ucluj_players["interceptions"].sum() +
    ucluj_players["recoveries"].sum()
)

balance_df = pd.DataFrame({
    "Category": [
        "Attack",
        "Defense"
    ],
    "Value": [
        attack_value,
        defense_value
    ]
})

fig_balance = px.pie(
    balance_df,
    names="Category",
    values="Value"
)

st.plotly_chart(fig_balance)

# =========================
# ROLLING TEAM FORM
# =========================

st.header("Rolling Team Form")

ucluj_players["form_score"] = (
    ucluj_players["goals"] * 1.5 +
    ucluj_players["assists"] * 1.2 +
    ucluj_players["shots"] * 0.1 +
    ucluj_players["passes"] * 0.01 +
    ucluj_players["interceptions"] * 0.05 +
    ucluj_players["recoveries"] * 0.05
)

form_per_match = (
    ucluj_players
    .groupby("match")["form_score"]
    .mean()
    .reset_index()
)

fig_form = px.line(
    form_per_match,
    x="match",
    y="form_score"
)

st.plotly_chart(fig_form)

# =========================
# POSITION CONTRIBUTION
# =========================

st.header("Position Contribution")

position_goals = (
    ucluj_players
    .groupby("position")["goals"]
    .sum()
    .reset_index()
)

fig_position = px.bar(
    position_goals,
    x="position",
    y="goals"
)

st.plotly_chart(fig_position)

# =========================
# DEFENSIVE TREND
# =========================

st.header("Defensive Stability Trend")

defensive_per_match = (
    ucluj_players
    .groupby("match")["interceptions"]
    .sum()
    .reset_index()
)

fig_def = px.line(
    defensive_per_match,
    x="match",
    y="interceptions"
)

st.plotly_chart(fig_def)

# =========================
# TEAM EFFICIENCY
# =========================

st.header("Team Efficiency")

ucluj_players["efficiency"] = (
    ucluj_players["goals"] /
    (ucluj_players["shots"] + 1)
)

efficiency_per_match = (
    ucluj_players
    .groupby("match")["efficiency"]
    .mean()
    .reset_index()
)

fig_eff = px.line(
    efficiency_per_match,
    x="match",
    y="efficiency"
)

st.plotly_chart(fig_eff)

st.header("Last Matches Form")

last_n = st.slider(
    "Number of recent matches",
    min_value=3,
    max_value=10,
    value=5
)

form_recent = (
    ucluj_players
    .groupby("match")["goals"]
    .sum()
    .tail(last_n)
    .reset_index()
)

fig_recent = px.line(
    form_recent,
    x="match",
    y="goals"
)

st.plotly_chart(fig_recent)