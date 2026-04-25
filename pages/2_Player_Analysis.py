import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.title("Player Analysis")

UCLUJ_TEAM_ID = 60374
UCLUJ_NAME = "Universitatea Cluj"

player_df = pd.read_csv("player_stats.csv")

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
# ONLY U CLUJ PLAYERS
# =========================

ucluj_players = player_df[
    player_df["teamId"] == UCLUJ_TEAM_ID
].copy()

if len(ucluj_players) == 0:
    st.error("No Universitatea Cluj players found with this teamId.")
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
    ].copy()

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
    st.warning("No players found for this filter.")
    st.stop()

# =========================
# PERFORMANCE SCORE PER ROW
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
# PLAYER SUMMARY
# =========================

st.header("Player Overview")

player_summary = (
    filtered_players
    .groupby("playerName")
    .agg({
        "position": "first",
        "goals": "sum",
        "assists": "sum",
        "shots": "sum",
        "passes": "sum",
        "interceptions": "sum",
        "recoveries": "sum",
        "performance_score": "sum"
    })
    .reset_index()
)

player_summary = player_summary.sort_values(
    by="performance_score",
    ascending=False
)

st.dataframe(
    player_summary,
    use_container_width=True
)

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
    st.metric("Goals", int(selected_player_data["goals"]))
    st.metric("Assists", int(selected_player_data["assists"]))

with col2:
    st.metric("Shots", int(selected_player_data["shots"]))
    st.metric("Passes", int(selected_player_data["passes"]))

with col3:
    st.metric("Interceptions", int(selected_player_data["interceptions"]))
    st.metric("Recoveries", int(selected_player_data["recoveries"]))

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

st.dataframe(
    comparison_table,
    use_container_width=True
)

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
    position = str(player["position"])

    goals = player["goals"]
    assists = player["assists"]
    shots = player["shots"]
    passes = player["passes"]
    interceptions = player["interceptions"]
    recoveries = player["recoveries"]
    score = player["performance_score"]

    team_avg = player_summary[
        metrics + ["performance_score"]
    ].mean()

    team_max = player_summary[
        metrics + ["performance_score"]
    ].max()

    def level(value, metric):
        avg = team_avg[metric]
        max_val = team_max[metric]

        if max_val == 0:
            return "low"

        if value >= 0.75 * max_val:
            return "elite"
        elif value >= avg:
            return "above average"
        elif value > 0:
            return "limited"
        else:
            return "none"

    goal_level = level(goals, "goals")
    assist_level = level(assists, "assists")
    shot_level = level(shots, "shots")
    pass_level = level(passes, "passes")
    interception_level = level(interceptions, "interceptions")
    recovery_level = level(recoveries, "recoveries")

    attacking_score = goals * 4 + assists * 3 + shots
    possession_score = passes * 0.03
    defensive_score = interceptions * 1.5 + recoveries * 1.2

    profile_parts = {
        "attacking impact": attacking_score,
        "possession involvement": possession_score,
        "defensive contribution": defensive_score
    }

    main_profile = max(
        profile_parts,
        key=profile_parts.get
    )

    strongest_metric = max(
        metrics,
        key=lambda m: player[m]
    )

    weakest_metric = min(
        metrics,
        key=lambda m: player[m]
    )

    text = f"""
### {name} — AI Player Profile

**Position:** {position}  
**Main profile:** {main_profile}  
**Performance score:** {round(score, 2)}

"""

    position_lower = position.lower()

    if (
        "forward" in position_lower
        or "striker" in position_lower
        or position_lower in ["fw", "st", "attacker"]
    ):

        if goals > 0:
            text += f"""
{name} has a clear attacking profile. His goal output is **{goal_level}** compared with the rest of the U Cluj squad, and his **{int(shots)} shots** show direct involvement in finishing situations.
"""
        else:
            text += f"""
{name} is listed as an attacking player, but his goal impact is low in the selected scope. His contribution comes more from movement, involvement, or pressing than from finishing.
"""

        if assists > 0:
            text += f"""
He also contributes creatively, with **{int(assists)} assists**, which means he can influence attacks both as a finisher and as a provider.
"""

    elif (
        "midfielder" in position_lower
        or position_lower in ["mf", "cm", "dm", "am"]
    ):

        if passes >= team_avg["passes"]:
            text += f"""
{name} is strongly involved in ball circulation. His passing volume is **{pass_level}**, suggesting that he helps connect phases of play and supports possession.
"""
        else:
            text += f"""
{name} has a lower passing volume than the squad average, so his role may be more specific, transitional, or less possession-based.
"""

        if recoveries >= team_avg["recoveries"]:
            text += f"""
He also adds value after possession loss, with recoveries rated as **{recovery_level}**, which is important for counter-pressing and transition control.
"""

        if assists > 0:
            text += f"""
His assist output is **{assist_level}**, showing that he can also influence the final third.
"""

    elif (
        "defender" in position_lower
        or position_lower in ["df", "cb", "lb", "rb", "wb"]
    ):

        if (
            interceptions >= team_avg["interceptions"]
            or recoveries >= team_avg["recoveries"]
        ):
            text += f"""
{name} stands out mostly through defensive actions. His interceptions are **{interception_level}**, while recoveries are **{recovery_level}**, showing his defensive presence and ability to regain possession.
"""
        else:
            text += f"""
{name} has a more positional defensive profile in this scope. His direct defensive numbers are not very high, which may mean he was less exposed or had a more conservative role.
"""

        if passes >= team_avg["passes"]:
            text += f"""
His passing volume is **{pass_level}**, so he may also be relevant in build-up from the back.
"""

    elif (
        "goalkeeper" in position_lower
        or position_lower == "gk"
    ):

        text += f"""
{name} is a goalkeeper, so this model cannot fully evaluate his real performance. These metrics only show limited involvement in distribution or possession. A better goalkeeper profile would need saves, goals conceded, claims, crosses stopped, and long-ball accuracy.
"""

    else:

        text += f"""
{name} has a mixed statistical profile. His strongest visible area is **{strongest_metric}**, while the lowest contribution appears in **{weakest_metric}**.
"""

    text += f"""

**Metric interpretation:**
- Goals level: **{goal_level}**
- Assists level: **{assist_level}**
- Shots level: **{shot_level}**
- Passing level: **{pass_level}**
- Interceptions level: **{interception_level}**
- Recoveries level: **{recovery_level}**

**Strongest statistical signal:** {strongest_metric}  
**Lowest statistical signal:** {weakest_metric}

"""

    if score >= player_summary["performance_score"].quantile(0.80):
        text += f"""
**Prediction:** {name} profiles as one of the key U Cluj players in this scope. If this level continues, he should remain highly relevant for selection.
"""
    elif score >= player_summary["performance_score"].median():
        text += f"""
**Prediction:** {name} looks like a useful squad player with clear contribution, but not one of the dominant profiles in this scope.
"""
    else:
        text += f"""
**Prediction:** {name} has limited statistical impact in this scope and may need more minutes, a different tactical role, or stronger involvement to stand out.
"""

    return text

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
