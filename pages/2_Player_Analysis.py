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

# ====================
# AI PLAYER INSIGHT
# =========================

st.header("AI Player Insight")

def percentile_rank(series, value):
    if len(series) == 0:
        return 0

    return round(
        (series <= value).mean() * 100,
        1
    )


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

    # Percentile values compared with U Cluj players
    goal_pct = percentile_rank(player_summary["goals"], goals)
    assist_pct = percentile_rank(player_summary["assists"], assists)
    shot_pct = percentile_rank(player_summary["shots"], shots)
    pass_pct = percentile_rank(player_summary["passes"], passes)
    interception_pct = percentile_rank(player_summary["interceptions"], interceptions)
    recovery_pct = percentile_rank(player_summary["recoveries"], recoveries)
    score_pct = percentile_rank(player_summary["performance_score"], score)

    # Role scores based on relative importance, not raw values
    attacking_profile = (
        goal_pct * 0.45
        +
        assist_pct * 0.25
        +
        shot_pct * 0.30
    )

    creative_profile = (
        assist_pct * 0.45
        +
        pass_pct * 0.35
        +
        shot_pct * 0.20
    )

    possession_profile = (
        pass_pct * 0.70
        +
        recovery_pct * 0.30
    )

    defensive_profile = (
        interception_pct * 0.55
        +
        recovery_pct * 0.45
    )

    balanced_profile = (
        attacking_profile
        +
        creative_profile
        +
        possession_profile
        +
        defensive_profile
    ) / 4

    profiles = {
        "Finisher / attacking threat": attacking_profile,
        "Creative player": creative_profile,
        "Possession connector": possession_profile,
        "Defensive ball-winner": defensive_profile,
        "Balanced contributor": balanced_profile
    }

    main_profile = max(
        profiles,
        key=profiles.get
    )

    sorted_profiles = sorted(
        profiles.items(),
        key=lambda x: x[1],
        reverse=True
    )

    secondary_profile = sorted_profiles[1][0]

    strengths = []

    if goal_pct >= 75:
        strengths.append("high goal output compared with the squad")

    if assist_pct >= 75:
        strengths.append("strong chance creation / assist contribution")

    if shot_pct >= 75:
        strengths.append("frequent involvement in shooting situations")

    if pass_pct >= 75:
        strengths.append("very important in ball circulation")

    if interception_pct >= 75:
        strengths.append("good anticipation and defensive reading")

    if recovery_pct >= 75:
        strengths.append("active recovery after possession loss")

    if len(strengths) == 0:
        best_metric = max(
            {
                "goals": goal_pct,
                "assists": assist_pct,
                "shots": shot_pct,
                "passes": pass_pct,
                "interceptions": interception_pct,
                "recoveries": recovery_pct
            },
            key={
                "goals": goal_pct,
                "assists": assist_pct,
                "shots": shot_pct,
                "passes": pass_pct,
                "interceptions": interception_pct,
                "recoveries": recovery_pct
            }.get
        )

        strengths.append(
            f"best relative contribution comes from {best_metric}"
        )

    weaknesses = []

    if goal_pct <= 30:
        weaknesses.append("limited goal impact")

    if assist_pct <= 30:
        weaknesses.append("limited assist contribution")

    if pass_pct <= 30:
        weaknesses.append("low involvement in possession")

    if interception_pct <= 30 and recovery_pct <= 30:
        weaknesses.append("limited defensive event volume")

    if len(weaknesses) == 0:
        weaknesses.append("no major statistical weakness in the selected scope")

    position_lower = position.lower()

    text = f"""
### {name} — AI Player Profile

**Position:** {position}  
**Main profile:** {main_profile}  
**Secondary profile:** {secondary_profile}  
**Overall squad impact percentile:** {score_pct}%

"""

    # Position-aware explanation
    if (
        "forward" in position_lower
        or "striker" in position_lower
        or position_lower in ["fw", "st", "attacker", "centre-forward"]
    ):

        text += f"""
{name} is evaluated mainly as an attacking player. In this scope, his attacking profile is built from goals, assists and shots, not from defensive events.

He ranks in the **{goal_pct}% percentile for goals** and **{shot_pct}% percentile for shots**, which shows how much direct attacking threat he provides compared with the rest of the U Cluj squad.
"""

        if assist_pct >= 60:
            text += f"""
He also has a creative side, because his assist percentile is **{assist_pct}%**, so he is not only finishing actions but also helping create them.
"""

    elif (
        "midfielder" in position_lower
        or position_lower in ["mf", "cm", "dm", "am"]
    ):

        text += f"""
{name} is evaluated as a midfield profile. For this type of player, passes, recoveries, assists and interceptions matter more than only goals.

His passing percentile is **{pass_pct}%**, while his recovery percentile is **{recovery_pct}%**. This suggests how much he contributes to controlling possession and transitions.
"""

        if assist_pct >= 60:
            text += f"""
He also adds final-third value, with an assist percentile of **{assist_pct}%**.
"""

    elif (
        "defender" in position_lower
        or position_lower in ["df", "cb", "lb", "rb", "wb", "centre-back", "full-back"]
    ):

        text += f"""
{name} is evaluated mainly as a defensive player. For defenders, interceptions, recoveries and passing are more relevant than goals.

His interception percentile is **{interception_pct}%**, recovery percentile is **{recovery_pct}%**, and passing percentile is **{pass_pct}%**.
"""

        if pass_pct >= 60:
            text += f"""
The passing value suggests that he is not only defending, but also participates in build-up.
"""

    elif (
        "goalkeeper" in position_lower
        or position_lower == "gk"
    ):

        text += f"""
{name} is a goalkeeper, so this model can only give a limited interpretation. The current dataset does not include goalkeeper-specific metrics such as saves, goals conceded, claims or distribution accuracy.
"""

    else:

        text += f"""
{name} has a mixed role in the dataset. His strongest profile is **{main_profile}**, with a secondary tendency toward **{secondary_profile}**.
"""

    text += f"""

**Main strengths:**
- {strengths[0]}
"""

    if len(strengths) > 1:
        text += f"- {strengths[1]}\n"

    text += f"""

**Possible limitation:**
- {weaknesses[0]}

**Metric percentiles inside U Cluj squad:**
- Goals: **{goal_pct}%**
- Assists: **{assist_pct}%**
- Shots: **{shot_pct}%**
- Passes: **{pass_pct}%**
- Interceptions: **{interception_pct}%**
- Recoveries: **{recovery_pct}%**

"""

    # More personalized prediction
    if main_profile == "Finisher / attacking threat":
        if goal_pct >= 75:
            prediction = (
                f"{name} should be considered one of the main attacking options. "
                "He has strong direct impact in front of goal."
            )
        else:
            prediction = (
                f"{name} has attacking involvement, but needs better conversion "
                "or more end-product to become a dominant offensive player."
            )

    elif main_profile == "Creative player":
        prediction = (
            f"{name} can be useful when the team needs chance creation and better link-up "
            "in the final third."
        )

    elif main_profile == "Possession connector":
        prediction = (
            f"{name} fits matches where U Cluj needs control, safer possession, "
            "and continuity between defensive and attacking phases."
        )

    elif main_profile == "Defensive ball-winner":
        prediction = (
            f"{name} is valuable in matches where U Cluj expects pressure, transitions, "
            "or needs stronger defensive coverage."
        )

    else:
        prediction = (
            f"{name} looks like a balanced squad option who can contribute in multiple phases, "
            "even if he is not dominant in one single metric."
        )

    text += f"""
**Prediction / tactical use:**  
{prediction}
"""

    return text


selected_ai_player = player_summary[
    player_summary["playerName"] == selected_player
].iloc[0]

st.markdown(
    generate_player_insight(selected_ai_player)
)
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
