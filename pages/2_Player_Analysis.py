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

player_summary = player_summary[
    player_summary[metrics].sum(axis=1) > 0
].copy()

if len(player_summary) == 0:
    st.warning("No useful player data found for this scope.")
    st.stop()

# =========================
# ADVANCED FOOTBALL INDICES
# =========================

def normalize(series):
    max_val = series.max()

    if max_val == 0:
        return series * 0

    return series / max_val


player_summary["attacking_index"] = normalize(
    player_summary["goals"] * 5.0
    +
    player_summary["assists"] * 3.0
    +
    player_summary["shots"] * 1.5
)

player_summary["creativity_index"] = normalize(
    player_summary["assists"] * 5.0
    +
    player_summary["passes"] * 0.06
    +
    player_summary["shots"] * 0.4
)

player_summary["possession_index"] = normalize(
    player_summary["passes"] * 0.10
    +
    player_summary["recoveries"] * 0.45
)

player_summary["defensive_index"] = normalize(
    player_summary["interceptions"] * 1.5
    +
    player_summary["recoveries"] * 1.1
)

player_summary["pressing_index"] = normalize(
    player_summary["recoveries"] * 1.3
    +
    player_summary["interceptions"] * 0.8
    +
    player_summary["shots"] * 0.2
)

player_summary["overall_index"] = (
    player_summary["attacking_index"] * 0.25
    +
    player_summary["creativity_index"] * 0.20
    +
    player_summary["possession_index"] * 0.20
    +
    player_summary["defensive_index"] * 0.20
    +
    player_summary["pressing_index"] * 0.15
)

advanced_metrics = [
    "attacking_index",
    "creativity_index",
    "possession_index",
    "defensive_index",
    "pressing_index"
]

advanced_labels = {
    "attacking_index": "Attacking Impact",
    "creativity_index": "Creativity",
    "possession_index": "Possession",
    "defensive_index": "Defensive Activity",
    "pressing_index": "Pressing / Recovery"
}

# =========================
# ROLE DETECTION
# =========================

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


def detect_tactical_role(row):

    position_group = detect_position_group(row["position"])

    attack = row["attacking_index"]
    creativity = row["creativity_index"]
    possession = row["possession_index"]
    defense = row["defensive_index"]
    pressing = row["pressing_index"]

    if position_group == "forward":

        scores = {
            "Finisher": attack,
            "Creative Forward": creativity,
            "Pressing Forward": pressing,
            "Link-up Forward": possession
        }

    elif position_group == "midfielder":

        scores = {
            "Creative Midfielder": creativity,
            "Possession Connector": possession,
            "Ball-Winning Midfielder": defense,
            "Box-to-Box Midfielder": (
                creativity + possession + defense + pressing
            ) / 4
        }

    elif position_group == "defender":

        scores = {
            "Defensive Ball-Winner": defense,
            "Build-up Defender": possession,
            "Advanced Full-back": (
                creativity + possession + pressing
            ) / 3,
            "Conservative Defender": (
                defense + possession
            ) / 2
        }

    elif position_group == "goalkeeper":

        scores = {
            "Goalkeeper - Limited Model": row["overall_index"]
        }

    else:

        scores = {
            "Attacking Profile": attack,
            "Creative Profile": creativity,
            "Possession Profile": possession,
            "Defensive Profile": defense,
            "Pressing Profile": pressing
        }

    return max(scores, key=scores.get)


player_summary["tactical_role"] = player_summary.apply(
    detect_tactical_role,
    axis=1
)

player_summary = player_summary.sort_values(
    by="overall_index",
    ascending=False
)

# =========================
# PLAYER OVERVIEW
# =========================

st.header("Player Overview")

overview_columns = [
    "playerName",
    "position",
    "tactical_role",
    "goals",
    "assists",
    "shots",
    "passes",
    "interceptions",
    "recoveries",
    "performance_score",
    "overall_index"
]

st.dataframe(
    player_summary[overview_columns],
    use_container_width=True
)

# =========================
# TEAM PROFILE MAP
# =========================

st.header("Team Tactical Profile Map")

fig_map = px.scatter(
    player_summary,
    x="attacking_index",
    y="defensive_index",
    size="overall_index",
    color="tactical_role",
    hover_name="playerName",
    hover_data=[
        "position",
        "goals",
        "assists",
        "shots",
        "passes",
        "interceptions",
        "recoveries"
    ],
    title="Attacking Impact vs Defensive Activity"
)

st.plotly_chart(
    fig_map,
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
    y="overall_index",
    color="tactical_role",
    title="Top Players by Overall Index"
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
    "Overall Index",
    round(selected_player_data["overall_index"], 3)
)

st.metric(
    "Detected Role",
    selected_player_data["tactical_role"]
)

# =========================
# PLAYER RADAR RAW
# =========================

st.subheader("Player Raw Stats Radar")

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
    line_close=True,
    title="Raw Statistical Profile"
)

fig_radar.update_traces(
    fill="toself"
)

st.plotly_chart(
    fig_radar,
    use_container_width=True
)

# =========================
# PLAYER RADAR ADVANCED
# =========================

st.subheader("Player Tactical Radar")

advanced_radar_df = pd.DataFrame({
    "Metric": [
        advanced_labels[m] for m in advanced_metrics
    ],
    "Value": [
        selected_player_data[m] for m in advanced_metrics
    ]
})

fig_adv_radar = px.line_polar(
    advanced_radar_df,
    r="Value",
    theta="Metric",
    line_close=True,
    title="Advanced Tactical Profile"
)

fig_adv_radar.update_traces(
    fill="toself"
)

st.plotly_chart(
    fig_adv_radar,
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

st.subheader("Raw Comparison")

comparison_table = pd.DataFrame({
    "Metric": metrics + ["performance_score"],
    player_1: [p1[m] for m in metrics] + [p1["performance_score"]],
    player_2: [p2[m] for m in metrics] + [p2["performance_score"]]
})

st.dataframe(
    comparison_table,
    use_container_width=True
)

st.subheader("Advanced Tactical Comparison")

advanced_table = pd.DataFrame({
    "Metric": [
        advanced_labels[m] for m in advanced_metrics
    ],
    player_1: [
        round(p1[m], 3) for m in advanced_metrics
    ],
    player_2: [
        round(p2[m], 3) for m in advanced_metrics
    ]
})

st.dataframe(
    advanced_table,
    use_container_width=True
)

compare_df = pd.DataFrame({
    "Metric": [
        advanced_labels[m] for m in advanced_metrics
    ] * 2,
    "Value": (
        [p1[m] for m in advanced_metrics]
        +
        [p2[m] for m in advanced_metrics]
    ),
    "Player": (
        [player_1] * len(advanced_metrics)
        +
        [player_2] * len(advanced_metrics)
    )
})

fig_compare = px.line_polar(
    compare_df,
    r="Value",
    theta="Metric",
    color="Player",
    line_close=True,
    title="Advanced Player Comparison"
)

fig_compare.update_traces(
    fill="toself"
)

st.plotly_chart(
    fig_compare,
    use_container_width=True
)

# =========================
# SIMILAR PLAYER FINDER
# =========================

st.header("Similar Player Finder")

selected_vector = selected_player_data[advanced_metrics].values.astype(float)

similarity_rows = []

for _, row in player_summary.iterrows():

    if row["playerName"] == selected_player:
        continue

    other_vector = row[advanced_metrics].values.astype(float)

    distance = np.linalg.norm(
        selected_vector - other_vector
    )

    similarity = 1 / (1 + distance)

    similarity_rows.append({
        "playerName": row["playerName"],
        "position": row["position"],
        "tactical_role": row["tactical_role"],
        "similarity_score": round(similarity, 3)
    })

similarity_df = pd.DataFrame(similarity_rows)

if len(similarity_df) > 0:

    similarity_df = similarity_df.sort_values(
        by="similarity_score",
        ascending=False
    )

    st.dataframe(
        similarity_df.head(5),
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

    role = player["tactical_role"]

    goal_pct = percentile_rank(player_summary["goals"], goals)
    assist_pct = percentile_rank(player_summary["assists"], assists)
    shot_pct = percentile_rank(player_summary["shots"], shots)
    pass_pct = percentile_rank(player_summary["passes"], passes)
    interception_pct = percentile_rank(
        player_summary["interceptions"],
        interceptions
    )
    recovery_pct = percentile_rank(
        player_summary["recoveries"],
        recoveries
    )
    overall_pct = percentile_rank(
        player_summary["overall_index"],
        player["overall_index"]
    )

    best_advanced_metric = max(
        advanced_metrics,
        key=lambda m: player[m]
    )

    weakest_advanced_metric = min(
        advanced_metrics,
        key=lambda m: player[m]
    )

    text = f"""
### {name} — AI Tactical Profile

**Data position:** {position}  
**Detected role:** {role}  
**Overall squad impact percentile:** {overall_pct}%  

"""

    if position_group == "forward":

        text += f"""
{name} is evaluated as an attacking player, so the model focuses mainly on goals, shots, assists, link-up actions and pressing from the front.

His goal percentile is **{goal_pct}%**, shot percentile is **{shot_pct}%**, and assist percentile is **{assist_pct}%**.
"""

        if goals == 0:
            text += """
He has **0 goals** in the selected scope, so the model does not treat him as a pure finisher.
"""
        else:
            text += f"""
He has **{int(goals)} goals**, which gives him direct attacking end-product.
"""

        if role == "Creative Forward":
            text += """
The role suggests a forward who contributes more through chance creation and link-up than only finishing.
"""

        elif role == "Pressing Forward":
            text += """
The role suggests a forward who adds value through pressing, recoveries and defensive work from the front.
"""

        elif role == "Link-up Forward":
            text += """
The role suggests a forward who helps connect midfield and attack.
"""

        elif role == "Finisher":
            text += """
The role suggests a forward with strong direct goal or shooting impact.
"""

    elif position_group == "midfielder":

        text += f"""
{name} is evaluated as a midfielder, where passing, creativity, recoveries and interceptions matter more than only goals.

His passing percentile is **{pass_pct}%**, assist percentile is **{assist_pct}%**, and recovery percentile is **{recovery_pct}%**.
"""

        if role == "Creative Midfielder":
            text += """
The role suggests that his main value comes from chance creation and final-third connection.
"""

        elif role == "Possession Connector":
            text += """
The role suggests that he helps U Cluj keep the ball moving and connect phases of play.
"""

        elif role == "Ball-Winning Midfielder":
            text += """
The role suggests that he is useful in transition moments and defensive recovery.
"""

        elif role == "Box-to-Box Midfielder":
            text += """
The role suggests a balanced midfield profile with involvement in several phases.
"""

    elif position_group == "defender":

        text += f"""
{name} is evaluated as a defender, so the model prioritizes defensive activity, recoveries and build-up involvement.

His interception percentile is **{interception_pct}%**, recovery percentile is **{recovery_pct}%**, and passing percentile is **{pass_pct}%**.
"""

        if role == "Build-up Defender":
            text += """
The role suggests that he contributes to circulation and controlled progression from the back.
"""

        elif role == "Defensive Ball-Winner":
            text += """
The role suggests that his strongest value is defending and regaining possession.
"""

        elif role == "Advanced Full-back":
            text += """
The role suggests a defender with higher attacking or possession involvement.
"""

        elif role == "Conservative Defender":
            text += """
The role suggests a safer defensive profile with less attacking emphasis.
"""

    elif position_group == "goalkeeper":

        text += """
This player is a goalkeeper. The current dataset does not include goalkeeper-specific features such as saves, claims, goals conceded or distribution accuracy, so the interpretation is limited.
"""

    else:

        text += f"""
{name} has a mixed or unknown position label, so the model classifies him based on statistical tendencies rather than a strict role.
"""

    text += f"""

**Strongest tactical area:** {advanced_labels[best_advanced_metric]}  
**Weakest tactical area:** {advanced_labels[weakest_advanced_metric]}  

**Advanced index values:**
- Attacking Impact: **{round(player["attacking_index"], 3)}**
- Creativity: **{round(player["creativity_index"], 3)}**
- Possession: **{round(player["possession_index"], 3)}**
- Defensive Activity: **{round(player["defensive_index"], 3)}**
- Pressing / Recovery: **{round(player["pressing_index"], 3)}**

**Raw metric percentiles inside U Cluj squad:**
- Goals: **{goal_pct}%**
- Assists: **{assist_pct}%**
- Shots: **{shot_pct}%**
- Passes: **{pass_pct}%**
- Interceptions: **{interception_pct}%**
- Recoveries: **{recovery_pct}%**
"""

    if role in ["Finisher", "Creative Forward", "Pressing Forward", "Link-up Forward"]:

        prediction = (
            f"{name} should be evaluated as an attacking option, but with the specific role of **{role}**. "
            "This helps avoid treating every forward only as a goal scorer."
        )

    elif role in [
        "Creative Midfielder",
        "Possession Connector",
        "Ball-Winning Midfielder",
        "Box-to-Box Midfielder"
    ]:

        prediction = (
            f"{name} fits a midfield usage pattern of **{role}**. "
            "His selection value depends on whether U Cluj needs creativity, control, or transition coverage."
        )

    elif role in [
        "Defensive Ball-Winner",
        "Build-up Defender",
        "Advanced Full-back",
        "Conservative Defender"
    ]:

        prediction = (
            f"{name} should be used according to his defensive profile: **{role}**. "
            "This gives a better interpretation than comparing defenders only by goals or assists."
        )

    else:

        prediction = (
            f"{name} should be interpreted carefully because the available dataset is limited for this role."
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
