import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.title("Player Analysis")

UCLUJ_TEAM_ID = 60374

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
# POSITION FILTER
# =========================

st.header("Filters")

positions = sorted(
    ucluj_players["position"].unique()
)

selected_position = st.selectbox(
    "Select Position",
    ["All"] + positions
)

if selected_position != "All":

    filtered_players = ucluj_players[
        ucluj_players["position"]
        == selected_position
    ]

else:

    filtered_players = ucluj_players

# =========================
# TOP PLAYER METRICS
# =========================

st.header("Top Player Contributions")

top_goals = (
    filtered_players
    .groupby("playerName")["goals"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

st.subheader("Top Goal Scorers")

st.dataframe(top_goals)

top_assists = (
    filtered_players
    .groupby("playerName")["assists"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

st.subheader("Top Assist Providers")

st.dataframe(top_assists)

top_defensive = (
    filtered_players
    .groupby("playerName")["interceptions"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

st.subheader("Top Defensive Players")

st.dataframe(top_defensive)

# =========================
# NORMALIZE
# =========================

norm_players = filtered_players.copy()

for m in metrics:

    max_val = norm_players[m].max()

    if max_val > 0:

        norm_players[m] = (
            norm_players[m] /
            max_val
        )

# =========================
# PROGRESSION
# =========================

progression_rows = []

for player in norm_players["playerName"].unique():

    p_data = norm_players[
        norm_players["playerName"] == player
    ]

    if len(p_data) < 4:
        continue

    p_data = p_data.sort_values(
        by="match"
    )

    half = len(p_data) // 2

    first_half = p_data.iloc[:half]
    second_half = p_data.iloc[-half:]

    change_total = 0

    for m in metrics:

        change_total += (
            second_half[m].mean()
            -
            first_half[m].mean()
        )

    progression_rows.append({
        "playerName": player,
        "position": p_data["position"].iloc[0],
        "progress_score": round(
            change_total,
            3
        )
    })

progression_df = pd.DataFrame(
    progression_rows
)

progression_df = progression_df.sort_values(
    by="progress_score",
    ascending=False
)

st.header("Player Progression")

st.subheader("Top Improving")

st.dataframe(
    progression_df.head(5)
)

st.subheader("Top Regressing")

st.dataframe(
    progression_df.tail(5)
)

# =========================
# EXPORT CSV
# =========================

st.header("Export Data")

csv = progression_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Progression Report",
    data=csv,
    file_name="player_progression_report.csv",
    mime="text/csv"
)

# =========================
# PLAYER RADAR
# =========================

st.header("Player Radar")

player_list = sorted(
    filtered_players["playerName"]
    .unique()
)

selected_player = st.selectbox(
    "Select Player",
    player_list
)

player_data = filtered_players[
    filtered_players["playerName"]
    == selected_player
]

avg_values = []

for m in metrics:

    avg_values.append(
        player_data[m].mean()
    )

radar_df = pd.DataFrame({
    "Metric": metrics,
    "Value": avg_values
})

fig_radar = px.line_polar(
    radar_df,
    r="Value",
    theta="Metric",
    line_close=True
)

st.plotly_chart(fig_radar)

# =========================
# PLAYER COMPARISON TOOL
# =========================

st.header("Player Comparison")

player_list = sorted(
    filtered_players["playerName"]
    .unique()
)

col1, col2 = st.columns(2)

with col1:

    player_1 = st.selectbox(
        "Select Player 1",
        player_list,
        key="player1"
    )

with col2:

    player_2 = st.selectbox(
        "Select Player 2",
        player_list,
        index=1 if len(player_list) > 1 else 0,
        key="player2"
    )

player1_data = filtered_players[
    filtered_players["playerName"] == player_1
]

player2_data = filtered_players[
    filtered_players["playerName"] == player_2
]

# =========================
# CALCULATE AVERAGES
# =========================

metrics = [
    "goals",
    "assists",
    "shots",
    "passes",
    "interceptions",
    "recoveries"
]

p1_values = []
p2_values = []

for m in metrics:

    p1_values.append(
        player1_data[m].mean()
    )

    p2_values.append(
        player2_data[m].mean()
    )

# =========================
# RADAR COMPARISON
# =========================

radar_compare_df = pd.DataFrame({
    "Metric": metrics * 2,
    "Value": p1_values + p2_values,
    "Player": (
        [player_1] * len(metrics)
        +
        [player_2] * len(metrics)
    )
})

fig_compare = px.line_polar(
    radar_compare_df,
    r="Value",
    theta="Metric",
    color="Player",
    line_close=True
)

st.plotly_chart(fig_compare)

# =========================
# TABLE COMPARISON
# =========================

st.subheader("Metric Comparison Table")

comparison_table = pd.DataFrame({
    "Metric": metrics,
    player_1: p1_values,
    player_2: p2_values
})

st.dataframe(comparison_table)