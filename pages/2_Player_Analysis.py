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

# =========================
# DATA CHECK
# =========================

required_cols = ["teamId", "playerName", "position"] + metrics

for col in required_cols:
    if col not in player_df.columns:
        st.error(f"Missing column: {col}")
        st.stop()

# =========================
# ONLY U CLUJ
# =========================

ucluj_players = player_df[
    player_df["teamId"] == UCLUJ_TEAM_ID
].copy()

if len(ucluj_players) == 0:
    st.error("No Universitatea Cluj players found.")
    st.stop()

# =========================
# FILTERS
# =========================

st.header("Filters")

analysis_scope = st.radio(
    "Select Analysis Scope",
    ["Full Season", "Single Match"]
)

base_players = ucluj_players.copy()

if analysis_scope == "Single Match":

    if "match" not in ucluj_players.columns:
        st.warning("Missing match column")
        st.stop()

    ucluj_matches = ucluj_players[
        ucluj_players["match"]
        .astype(str)
        .str.contains(UCLUJ_NAME, case=False, na=False)
    ]

    match_list = sorted(ucluj_matches["match"].dropna().unique())

    selected_match = st.selectbox("Select Match", match_list)

    base_players = ucluj_matches[
        ucluj_matches["match"] == selected_match
    ]

# Position filter

positions = sorted(ucluj_players["position"].dropna().unique())

selected_position = st.selectbox(
    "Select Position",
    ["All"] + positions
)

if selected_position != "All":
    filtered_players = base_players[
        base_players["position"] == selected_position
    ]
else:
    filtered_players = base_players.copy()

# =========================
# PERFORMANCE SCORE
# =========================

filtered_players["performance_score"] = (
    filtered_players["goals"] * 5
    + filtered_players["assists"] * 4
    + filtered_players["shots"] * 1.2
    + filtered_players["passes"] * 0.02
    + filtered_players["interceptions"] * 1.2
    + filtered_players["recoveries"] * 1.0
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

# 🔥 REMOVE players with no impact
player_summary = player_summary[
    player_summary[metrics].sum(axis=1) > 0
]

player_summary = player_summary.sort_values(
    by="performance_score",
    ascending=False
)

st.header("Player Overview")
st.dataframe(player_summary, use_container_width=True)

# =========================
# TOP PLAYERS
# =========================

st.header("Top Players")

fig = px.bar(
    player_summary.head(5),
    x="playerName",
    y="performance_score",
    color="position"
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# PLAYER SELECT
# =========================

player_list = player_summary["playerName"].unique()

selected_player = st.selectbox("Select Player", player_list)

player = player_summary[
    player_summary["playerName"] == selected_player
].iloc[0]

# =========================
# METRICS
# =========================

st.subheader("Key Stats")

col1, col2, col3 = st.columns(3)

col1.metric("Goals", int(player["goals"]))
col1.metric("Assists", int(player["assists"]))

col2.metric("Shots", int(player["shots"]))
col2.metric("Passes", int(player["passes"]))

col3.metric("Interceptions", int(player["interceptions"]))
col3.metric("Recoveries", int(player["recoveries"]))

st.metric("Performance Score", round(player["performance_score"], 2))

# =========================
# RADAR
# =========================

radar_values = []

for m in metrics:
    max_val = player_summary[m].max()
    radar_values.append(player[m] / max_val if max_val > 0 else 0)

radar_df = pd.DataFrame({
    "Metric": [metric_labels[m] for m in metrics],
    "Value": radar_values
})

fig_radar = px.line_polar(
    radar_df,
    r="Value",
    theta="Metric",
    line_close=True
)

fig_radar.update_traces(fill="toself")
st.plotly_chart(fig_radar, use_container_width=True)

# =========================
# AI INSIGHT
# =========================

st.header("AI Player Insight")

def percentile(series, value):
    if value == 0:
        return 0
    return round((series < value).mean() * 100, 1)

def insight(p):

    name = p["playerName"]
    pos = p["position"]

    g = p["goals"]
    a = p["assists"]
    s = p["shots"]
    pas = p["passes"]
    inter = p["interceptions"]
    rec = p["recoveries"]

    g_p = percentile(player_summary["goals"], g)
    a_p = percentile(player_summary["assists"], a)
    s_p = percentile(player_summary["shots"], s)
    p_p = percentile(player_summary["passes"], pas)
    i_p = percentile(player_summary["interceptions"], inter)
    r_p = percentile(player_summary["recoveries"], rec)

    attack = g_p*0.5 + s_p*0.3 + a_p*0.2
    defend = i_p*0.6 + r_p*0.4
    poss = p_p

    profiles = {
        "Attacker": attack,
        "Defender": defend,
        "Playmaker": a_p,
        "Possession Player": poss
    }

    main = max(profiles, key=profiles.get)

    text = f"""
### {name}

**Position:** {pos}  
**Main role:** {main}

"""

    if main == "Attacker":
        text += f"""
This player contributes mainly in attacking phases.

- Goals percentile: {g_p}%
- Shots percentile: {s_p}%

"""

    elif main == "Defender":
        text += f"""
This player contributes mainly defensively.

- Interceptions: {i_p}%
- Recoveries: {r_p}%

"""

    elif main == "Playmaker":
        text += f"""
This player creates chances.

- Assists percentile: {a_p}%

"""

    else:
        text += f"""
This player helps control possession.

- Passing percentile: {p_p}%

"""

    if g == 0:
        text += "\n⚠️ No goal contribution.\n"

    return text

st.markdown(insight(player))

# =========================
# EXPORT
# =========================

st.header("Export")

csv = player_summary.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download CSV",
    csv,
    "ucluj_players.csv",
    "text/csv"
)
