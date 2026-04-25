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
    filtered_players["goals"] * 5.0
    +
    filtered_players["assists"] * 4.0
    +
    filtered_players["shots"] * 1.2
    +
    filtered_players["passes"] * 0.025
    +
    filtered_players["interceptions"] * 1.1
    +
    filtered_players["recoveries"] * 0.9
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

# Remove only players with absolutely no useful actions
player_summary = player_summary[
    player_summary[metrics].sum(axis=1) > 0
].copy()

if len(player_summary) == 0:
    st.warning("No useful player data found for this scope.")
    st.stop()

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

def percentile_rank(series, value):

    if len(series) == 0:
        return 0

    if value <= 0:
        return 0

    return round(
        (series < value).mean() * 100,
        1
    )


def detect_position_group(position):

    position_lower = str(position).lower()

    if (
        "goalkeeper" in position_lower
        or position_lower == "gk"
    ):
        return "goalkeeper"

    if (
        "forward" in position_lower
        or "striker" in position_lower
        or "attacker" in position_lower
        or position_lower in ["fw", "st", "cf", "lw", "rw"]
    ):
        return "forward"

    if (
        "midfielder" in position_lower
        or position_lower in ["mf", "cm", "dm", "am", "cdm", "cam"]
    ):
        return "midfielder"

    if (
        "defender" in position_lower
        or position_lower in ["df", "cb", "lb", "rb", "wb", "lwb", "rwb"]
        or "back" in position_lower
    ):
        return "defender"

    return "unknown"


def generate_player_insight(player):

    name = player["playerName"]
    position = str(player["position"])
    position_group = detect_position_group(position)

    goals = player["goals"]
    assists = player["assists"]
    shots = player["shots"]
    passes = player["passes"]
    interceptions = player["interceptions"]
    recoveries = player["recoveries"]
    score = player["performance_score"]

    goal_pct = percentile_rank(player_summary["goals"], goals)
    assist_pct = percentile_rank(player_summary["assists"], assists)
    shot_pct = percentile_rank(player_summary["shots"], shots)
    pass_pct = percentile_rank(player_summary["passes"], passes)
    interception_pct = percentile_rank(player_summary["interceptions"], interceptions)
    recovery_pct = percentile_rank(player_summary["recoveries"], recoveries)
    score_pct = percentile_rank(player_summary["performance_score"], score)

    # Role scores based on percentiles, not raw values
    finisher_score = (
        goal_pct * 0.55
        +
        shot_pct * 0.35
        +
        assist_pct * 0.10
    )

    creative_score = (
        assist_pct * 0.45
        +
        shot_pct * 0.25
        +
        pass_pct * 0.30
    )

    possession_score = (
        pass_pct * 0.70
        +
        assist_pct * 0.15
        +
        recovery_pct * 0.15
    )

    pressing_score = (
        recovery_pct * 0.55
        +
        interception_pct * 0.30
        +
        shot_pct * 0.15
    )

    defensive_score = (
        interception_pct * 0.55
        +
        recovery_pct * 0.35
        +
        pass_pct * 0.10
    )

    build_up_defender_score = (
        pass_pct * 0.45
        +
        interception_pct * 0.30
        +
        recovery_pct * 0.25
    )

    if position_group == "forward":

        profiles = {
            "Finisher / goal threat": finisher_score,
            "Creative forward": creative_score,
            "Pressing forward": pressing_score,
            "Link-up forward": possession_score
        }

    elif position_group == "midfielder":

        profiles = {
            "Creative midfielder": creative_score,
            "Possession connector": possession_score,
            "Ball-winning midfielder": defensive_score,
            "Box-to-box contributor": (
                creative_score
                +
                possession_score
                +
                defensive_score
            ) / 3
        }

    elif position_group == "defender":

        profiles = {
            "Defensive ball-winner": defensive_score,
            "Build-up defender": build_up_defender_score,
            "Possession defender": possession_score,
            "Attacking full-back / advanced defender": (
                assist_pct * 0.35
                +
                shot_pct * 0.25
                +
                pass_pct * 0.40
            )
        }

    elif position_group == "goalkeeper":

        profiles = {
            "Goalkeeper - limited model": score_pct
        }

    else:

        profiles = {
            "Finisher / goal threat": finisher_score,
            "Creative player": creative_score,
            "Possession connector": possession_score,
            "Defensive ball-winner": defensive_score,
            "Pressing player": pressing_score
        }

    sorted_profiles = sorted(
        profiles.items(),
        key=lambda x: x[1],
        reverse=True
    )

    main_profile = sorted_profiles[0][0]
    secondary_profile = sorted_profiles[1][0] if len(sorted_profiles) > 1 else "N/A"

    strengths = []

    if goals > 0 and goal_pct >= 60:
        strengths.append("real goal contribution")

    if shots > 0 and shot_pct >= 70:
        strengths.append("frequent involvement in shooting situations")

    if assists > 0 and assist_pct >= 60:
        strengths.append("chance creation / final pass contribution")

    if passes > 0 and pass_pct >= 70:
        strengths.append("important involvement in ball circulation")

    if interceptions > 0 and interception_pct >= 70:
        strengths.append("good anticipation and defensive reading")

    if recoveries > 0 and recovery_pct >= 70:
        strengths.append("active recovery work after possession loss")

    if len(strengths) == 0:

        metric_percentiles = {
            "goals": goal_pct,
            "assists": assist_pct,
            "shots": shot_pct,
            "passes": pass_pct,
            "interceptions": interception_pct,
            "recoveries": recovery_pct
        }

        best_metric = max(
            metric_percentiles,
            key=metric_percentiles.get
        )

        strengths.append(
            f"best relative contribution comes from {best_metric}"
        )

    limitations = []

    if position_group == "forward" and goals == 0:
        limitations.append("no goal contribution in the selected scope")

    if position_group == "forward" and shots == 0:
        limitations.append("low direct shooting presence")

    if position_group == "midfielder" and passes < player_summary["passes"].median():
        limitations.append("below-median passing involvement for the squad")

    if position_group == "defender" and interceptions == 0 and recoveries == 0:
        limitations.append("low visible defensive event volume")

    if assists == 0 and position_group in ["forward", "midfielder"]:
        limitations.append("no assist contribution in the selected scope")

    if len(limitations) == 0:
        limitations.append("no major statistical limitation visible in these metrics")

    text = f"""
### {name} — AI Player Profile

**Data position:** {position}  
**Detected football role:** {main_profile}  
**Secondary tendency:** {secondary_profile}  
**Overall squad impact percentile:** {score_pct}%

"""

    if position_group == "forward":

        text += f"""
{name} is listed as a forward, so the model evaluates him mainly through attacking involvement: goals, shots, assists, link-up actions and pressing work.

His goal percentile is **{goal_pct}%** and his shot percentile is **{shot_pct}%**.  
"""

        if goals == 0:
            text += f"""
He has **0 goals** in the selected scope, so he should not be described as a finisher here.
"""
        else:
            text += f"""
He scored **{int(goals)} goals**, so he has direct end-product in this scope.
"""

        if assists > 0:
            text += f"""
He also has **{int(assists)} assists**, which gives him a creative side, not only an attacking presence.
"""

        if main_profile == "Pressing forward":
            text += f"""
The reason he is detected as a pressing forward is that his recovery/interception profile is high compared with the squad, while still being classified as an attacking player. That means defensive work from the front, not a defender role.
"""

        if main_profile == "Creative forward":
            text += f"""
The profile suggests a forward who contributes more through chance creation, link-up and involvement around the final third than pure finishing.
"""

    elif position_group == "midfielder":

        text += f"""
{name} is evaluated as a midfielder. For this role, the model gives more importance to passing, assists, recoveries and interceptions.

His passing percentile is **{pass_pct}%**, recovery percentile is **{recovery_pct}%**, and assist percentile is **{assist_pct}%**.
"""

        if main_profile == "Possession connector":
            text += f"""
This suggests that he is useful for keeping the ball moving and connecting defensive and attacking phases.
"""

        if main_profile == "Creative midfielder":
            text += f"""
This suggests that his strongest value is in chance creation and final-third support.
"""

        if main_profile == "Ball-winning midfielder":
            text += f"""
This suggests that his main value comes from defensive activity and transition control.
"""

    elif position_group == "defender":

        text += f"""
{name} is evaluated as a defender. For this role, interceptions, recoveries and passing involvement are more relevant than goals.

His interception percentile is **{interception_pct}%**, recovery percentile is **{recovery_pct}%**, and passing percentile is **{pass_pct}%**.
"""

        if main_profile == "Build-up defender":
            text += f"""
This suggests that he is not only defending, but also helping the team progress or circulate the ball from deeper areas.
"""

        if main_profile == "Defensive ball-winner":
            text += f"""
This suggests that his strongest value is defensive presence and winning/regaining possession.
"""

    elif position_group == "goalkeeper":

        text += f"""
{name} is a goalkeeper, but this dataset does not contain goalkeeper-specific indicators such as saves, goals conceded, crosses claimed or distribution accuracy. The current model can only interpret limited possession-related involvement.
"""

    else:

        text += f"""
{name} has an unknown or mixed position label in the dataset. The model therefore classifies him mainly by statistical tendencies rather than by a strict tactical role.
"""

    text += f"""

**Main strengths:**
- {strengths[0]}
"""

    if len(strengths) > 1:
        text += f"- {strengths[1]}\n"

    text += f"""

**Possible limitation:**
- {limitations[0]}

**Metric percentiles inside U Cluj squad:**
- Goals: **{goal_pct}%**
- Assists: **{assist_pct}%**
- Shots: **{shot_pct}%**
- Passes: **{pass_pct}%**
- Interceptions: **{interception_pct}%**
- Recoveries: **{recovery_pct}%**

"""

    if main_profile == "Finisher / goal threat":
        prediction = (
            f"{name} should be used when U Cluj needs direct attacking threat and finishing presence."
        )

    elif main_profile == "Creative forward":
        prediction = (
            f"{name} fits better as a creative attacking option, useful for link-up play and chance creation rather than only finishing."
        )

    elif main_profile == "Pressing forward":
        prediction = (
            f"{name} is useful in matches where U Cluj wants pressure from the front and aggressive recovery after losing possession."
        )

    elif main_profile == "Link-up forward":
        prediction = (
            f"{name} can help connect midfield and attack, especially when the team needs attacking continuity."
        )

    elif main_profile == "Creative midfielder":
        prediction = (
            f"{name} should be valuable when the team needs more creativity and final-third connection."
        )

    elif main_profile == "Possession connector":
        prediction = (
            f"{name} is useful when U Cluj wants more control, safer possession and cleaner circulation."
        )

    elif main_profile == "Ball-winning midfielder":
        prediction = (
            f"{name} is useful in matches with many transitions, where recovering the ball quickly is important."
        )

    elif main_profile == "Box-to-box contributor":
        prediction = (
            f"{name} offers a balanced midfield profile and can contribute in multiple phases."
        )

    elif main_profile == "Defensive ball-winner":
        prediction = (
            f"{name} is valuable when U Cluj expects pressure and needs stronger defensive coverage."
        )

    elif main_profile == "Build-up defender":
        prediction = (
            f"{name} is useful when U Cluj wants defenders involved in build-up and controlled progression from the back."
        )

    elif main_profile == "Possession defender":
        prediction = (
            f"{name} can help the team keep possession from deeper areas and reduce chaotic clearances."
        )

    elif main_profile == "Attacking full-back / advanced defender":
        prediction = (
            f"{name} can be useful when U Cluj needs width, support in possession and advanced involvement from the defensive line."
        )

    else:
        prediction = (
            f"{name} has a mixed profile and should be evaluated together with match context and minutes played."
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
