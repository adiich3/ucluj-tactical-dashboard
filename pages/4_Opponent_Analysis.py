import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.title("Opponent Analysis")

UCLUJ_TEAM_ID = 60374


ucluj_players = player_df[
    player_df["teamId"] == UCLUJ_TEAM_ID
].copy()

opponent_players = player_df[
    player_df["teamId"] != UCLUJ_TEAM_ID
].copy()# =========================
# LOAD DATA
# =========================

player_df = pd.read_csv("player_stats.csv")

# =========================
# SELECT MATCH
# =========================

match_list = sorted(
    player_df["match"].unique()
)

selected_match = st.selectbox(
    "Select Match",
    match_list
)

match_data = player_df[
    player_df["match"] == selected_match
]

ucluj_data = match_data[
    match_data["teamId"] == UCLUJ_TEAM_ID
]

opponent_data = match_data[
    match_data["teamId"] != UCLUJ_TEAM_ID
]

# =========================
# TEAM SCORES
# =========================

st.header("Team Comparison")

ucluj_score = (
    ucluj_data["player_score"]
    .mean()
)

opponent_score = (
    opponent_data["player_score"]
    .mean()
)

comparison_df = pd.DataFrame({
    "Team": ["U Cluj", "Opponent"],
    "Score": [
        ucluj_score,
        opponent_score
    ]
})

fig_compare = px.bar(
    comparison_df,
    x="Team",
    y="Score",
    title="Team Performance Comparison"
)

st.plotly_chart(fig_compare)

# =========================
# OPPONENT STRENGTH
# =========================

st.header("Opponent Strength")

metrics = [
    "goals",
    "assists",
    "shots",
    "passes",
    "interceptions",
    "recoveries"
]

ucluj_strength = []

opponent_strength = []

for m in metrics:

    ucluj_strength.append(
        ucluj_data[m].sum()
    )

    opponent_strength.append(
        opponent_data[m].sum()
    )

strength_df = pd.DataFrame({
    "Metric": metrics,
    "U Cluj": ucluj_strength,
    "Opponent": opponent_strength
})

fig_strength = px.bar(
    strength_df,
    x="Metric",
    y=["U Cluj", "Opponent"],
    barmode="group",
    title="Metric Comparison"
)

st.plotly_chart(fig_strength)

# =========================
# MATCH DIFFICULTY
# =========================

st.header("Match Difficulty Index")

difficulty_score = opponent_score - ucluj_score

difficulty_value = round(
    difficulty_score,
    2
)

if difficulty_value > 0:

    difficulty_label = "Hard Match"

elif difficulty_value < -0.2:

    difficulty_label = "Easy Match"

else:

    difficulty_label = "Balanced Match"

st.metric(
    label="Difficulty Score",
    value=difficulty_value
)

st.write(
    "Match Type:",
    difficulty_label
)

# =========================
# OPPONENT TREND
# =========================

st.header("Opponent Performance Trend")

opponent_trend = (
    player_df[
        player_df["teamId"] != UCLUJ_TEAM_ID
    ]
    .groupby("match")["player_score"]
    .mean()
    .reset_index()
)

fig_trend = px.line(
    opponent_trend,
    x="match",
    y="player_score",
    title="Opponent Trend"
)

st.plotly_chart(fig_trend)

# =========================
# OPPONENT WEAKNESS
# =========================

st.header("Opponent Weakness Indicator")

weakness_list = []

for m in metrics:

    opp_val = opponent_data[m].mean()
    u_val = ucluj_data[m].mean()

    diff = u_val - opp_val

    weakness_list.append({
        "Metric": m,
        "Difference": diff
    })

weakness_df = pd.DataFrame(
    weakness_list
)

weakness_df = weakness_df.sort_values(
    by="Difference",
    ascending=False
)

st.subheader("Top Opportunities")

st.dataframe(
    weakness_df.head(3)
)

st.subheader("Opponent Advantages")

st.dataframe(
    weakness_df.tail(3)
)
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
# =========================
# LAST MATCH FORM
# =========================

st.header("Recent Team Form")

last_n = st.slider(
    "Last Matches",
    min_value=3,
    max_value=10,
    value=5
)

recent_goals = (
    ucluj_players
    .groupby("match")["goals"]
    .sum()
    .tail(last_n)
    .reset_index()
)

fig_recent = px.bar(
    recent_goals,
    x="match",
    y="goals"
)

st.plotly_chart(fig_recent)