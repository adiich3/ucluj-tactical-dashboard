import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.title("Player Analysis")

UCLUJ_TEAM_ID = 60374
UCLUJ_NAME = "Universitatea Cluj"

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

metric_labels = {
    "goals": "Goals",
    "assists": "Assists",
    "shots": "Shots",
    "passes": "Passing",
    "interceptions": "Interceptions",
    "recoveries": "Recoveries"
}

required_cols = [
    "teamId",
    "playerName",
    "position"
] + metrics

for col in required_cols:
    if col not in player_df.columns:
        st.error(f"Missing column: {col}")
        st.stop()

# =========================
# FILTERS
# =========================

st.header("Filters")

analysis_scope = st.radio(
    "Select Analysis Scope",
    [
        "Full Season",
        "Single Match"
    ]
)

base_players = ucluj_players.copy()

if analysis_scope == "Single Match":

    if "match" not in ucluj_players.columns:
        st.warning("The dataset does not contain a match column.")
        st.stop()

    ucluj_only_matches = ucluj_players[
        ucluj_players["match"]
        .astype(str)
        .str.contains(UCLUJ_NAME, case=False, na=False)
    ]

    ucluj_match_list = sorted(
        ucluj_only_matches["match"]
        .dropna()
        .unique()
    )

    if len(ucluj_match_list) == 0:
        st.warning("No Universitatea Cluj matches found.")
        st.stop()

    selected_match = st.selectbox(
        "Select Universitatea Cluj Match",
        ucluj_match_list
    )

    base_players = ucluj_only_matches[
        ucluj_only_matches["match"] == selected_match
    ].copy()

# IMPORTANT: positions from all U Cluj players, not only current match
all_positions = sorted(
    ucluj_players["position"]
    .dropna()
    .unique()
)

selected_position = st.selectbox(
    "Select Position",
    ["All"] + all_positions
)

if selected_position != "All":
    filtered_players = base_players[
        base_players["position"] == selected_position
    ].copy()
else:
    filtered_players = base_players.copy()

if len(filtered_players) == 0:
    st.warning("No players found for this position in the selected scope.")
    st.stop()

# =========================
# PERFORMANCE SCORE
# =========================

filtered_players["performance_score"] = (
    filtered_players["goals"] * 4
    +
    filtered_players["assists"] * 3
    +
    filtered_players["shots"] * 1
    +
    filtered_players["passes"] * 0.03
    +
    filtered_players["interceptions"] * 1.5
    +
    filtered_players["recoveries"] * 1.2
)

# =========================
# PLAYER OVERVIEW
# =========================

st.header("Player Overview")

if analysis_scope == "Full Season":

    player_summary = (
        filtered_players
        .groupby(["playerName", "position"])[
            metrics + ["performance_score"]
        ]
        .mean()
        .reset_index()
    )

else:

    player_summary = filtered_players[
        [
            "playerName",
            "position",
            "goals",
            "assists",
            "shots",
            "passes",
            "interceptions",
            "recoveries",
            "performance_score"
        ]
    ].copy()

player_summary = player_summary.sort_values(
    by="performance_score",
    ascending=False
)

st.dataframe(player_summary)

# =========================
# TOP PLAYERS
# =========================

st.header("Top Player Contributions")

top_players = player_summary.head(5)

fig_top = px.bar(
    top_players,
    x="playerName",
    y="performance_score",
    color="position",
    title="Top Players by Performance Score"
)

st.plotly_chart(
    fig_top,
    use_container_width=True
)

# =========================
# INDIVIDUAL PLAYER ANALYSIS
# =========================

st.header("Individual Player Analysis")

player_list = sorted(
    player_summary["playerName"]
    .dropna()
    .unique()
)

selected_player = st.selectbox(
    "Select Player",
    player_list
)

selected_player_data = player_summary[
    player_summary["playerName"] == selected_player
].iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Goals", round(selected_player_data["goals"], 2))
    st.metric("Assists", round(selected_player_data["assists"], 2))

with col2:
    st.metric("Shots", round(selected_player_data["shots"], 2))
    st.metric("Passes", round(selected_player_data["passes"], 2))

with col3:
    st.metric("Interceptions", round(selected_player_data["interceptions"], 2))
    st.metric("Recoveries", round(selected_player_data["recoveries"], 2))

st.metric(
    "Performance Score",
    round(selected_player_data["performance_score"], 2)
)

# =========================
# PLAYER RADAR
# =========================

st.subheader("Player Radar")

radar_values = []

for m in metrics:

    max_val = player_summary[m].max()

    if max_val > 0:
        radar_values.append(
            selected_player_data[m] / max_val
        )
    else:
        radar_values.append(0)

radar_df = pd.DataFrame({
    "Metric": [
        metric_labels[m] for m in metrics
    ],
    "Value": radar_values
})

fig_radar = px.line_polar(
    radar_df,
    r="Value",
    theta="Metric",
    line_close=True
)

fig_radar.update_traces(
    fill="toself"
)

st.plotly_chart(
    fig_radar,
    use_container_width=True
)

# =========================
# PLAYER COMPARISON
# =========================

st.header("Player Comparison")

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

p1 = player_summary[
    player_summary["playerName"] == player_1
].iloc[0]

p2 = player_summary[
    player_summary["playerName"] == player_2
].iloc[0]

comparison_table = pd.DataFrame({
    "Metric": metrics + ["performance_score"],
    player_1: [p1[m] for m in metrics] + [p1["performance_score"]],
    player_2: [p2[m] for m in metrics] + [p2["performance_score"]]
})

st.dataframe(comparison_table)

compare_df = pd.DataFrame({
    "Metric": metrics * 2,
    "Value": (
        [p1[m] for m in metrics]
        +
        [p2[m] for m in metrics]
    ),
    "Player": (
        [player_1] * len(metrics)
        +
        [player_2] * len(metrics)
    )
})

fig_compare = px.line_polar(
    compare_df,
    r="Value",
    theta="Metric",
    color="Player",
    line_close=True
)

fig_compare.update_traces(
    fill="toself"
)

st.plotly_chart(
    fig_compare,
    use_container_width=True
)

# =========================
# AI PLAYER INSIGHT
# =========================

st.header("AI Player Insight")

def generate_player_insight(player):

    name = player["playerName"]

    goals = player["goals"]
    assists = player["assists"]
    shots = player["shots"]
    passes = player["passes"]
    interceptions = player["interceptions"]
    recoveries = player["recoveries"]
    score = player["performance_score"]

    attacking_value = goals * 4 + assists * 3 + shots
    defensive_value = interceptions * 1.5 + recoveries * 1.2
    possession_value = passes * 0.03

    strengths = []

    if attacking_value >= defensive_value and attacking_value >= possession_value:
        main_role = "attacking contributor"
        strengths.append("strong offensive involvement")

    elif defensive_value >= attacking_value and defensive_value >= possession_value:
        main_role = "defensive contributor"
        strengths.append("good defensive activity")

    else:
        main_role = "possession-oriented player"
        strengths.append("important in ball circulation")

    if goals > 0:
        strengths.append("goal threat")

    if assists > 0:
        strengths.append("creative passing")

    if recoveries > interceptions:
        strengths.append("active ball recovery")

    if interceptions > recoveries:
        strengths.append("good anticipation")

    if len(strengths) == 0:
        strengths.append("balanced contribution")

    if score >= player_summary["performance_score"].quantile(0.75):
        prediction = "Expected to remain an important player if this level is maintained."

    elif score >= player_summary["performance_score"].median():
        prediction = "Expected to be a useful rotation or support player."

    else:
        prediction = "Needs improvement or more minutes to become more influential."

    insight = f"""
{name} is mainly profiled as a **{main_role}** for Universitatea Cluj.

Main strengths:
- {strengths[0]}
"""

    if len(strengths) > 1:
        insight += f"- {strengths[1]}\n"

    insight += f"""

Tactical interpretation:
The player has a performance score of **{round(score, 2)}** in the selected analysis scope.

Prediction:
**{prediction}**
"""

    return insight

selected_ai_player = player_summary[
    player_summary["playerName"] == selected_player
].iloc[0]

st.markdown(
    generate_player_insight(selected_ai_player)
)

# =========================
# EXPORT
# =========================

st.header("Export Data")

csv = player_summary.to_csv(
    index=False
).encode("utf-8")

file_name = (
    "ucluj_full_season_player_analysis.csv"
    if analysis_scope == "Full Season"
    else "ucluj_single_match_player_analysis.csv"
)

st.download_button(
    label="Download Player Analysis",
    data=csv,
    file_name=file_name,
    mime="text/csv"
)
