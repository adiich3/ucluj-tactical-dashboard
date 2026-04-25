import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.metrics.pairwise import euclidean_distances

st.title("Match Analysis")

UCLUJ_TEAM_ID = 60374

# =========================
# DATA SOURCE SELECTOR
# =========================

data_mode = st.radio(
    "Select Dataset",
    [
        "All Matches",
        "U Cluj Matches"
    ]
)

if data_mode == "All Matches":

    reports = pd.read_csv(
        "all_match_reports.csv"
    )

    vectors = pd.read_csv(
        "all_match_vectors.csv"
    )

else:

    reports = pd.read_csv(
        "ucluj_match_reports.csv"
    )

    vectors = pd.read_csv(
        "ucluj_match_vectors.csv"
    )

# IMPORTANT
# incarcam player data aici

player_df = pd.read_csv(
    "player_stats.csv"
)

# =========================
# FILTER U CLUJ
# =========================

if data_mode == "U Cluj Matches":

    reports = reports[
        reports["match"]
        .str.contains(
            "Universitatea Cluj",
            case=False,
            na=False
        )
    ].copy()

    vectors = vectors[
        vectors["match"]
        .str.contains(
            "Universitatea Cluj",
            case=False,
            na=False
        )
    ].copy()

# =========================
# SYNC
# =========================

common_matches = set(
    reports["match"]
).intersection(
    set(vectors["match"])
)

reports = reports[
    reports["match"]
    .isin(common_matches)
]

vectors = vectors[
    vectors["match"]
    .isin(common_matches)
]

# =========================
# MATCH LIST
# =========================

match_list = sorted(
    reports["match"]
    .dropna()
    .unique()
    .tolist()
)

st.caption(
    f"Matches loaded: {len(match_list)}"
)

search_text = st.text_input(
    "Search Match"
)

if search_text:

    match_list = [

        m for m in match_list

        if search_text.lower()
        in m.lower()
    ]

selected_match = st.selectbox(
    "Select Match",
    match_list
)

match_row = reports[
    reports["match"]
    == selected_match
].iloc[0]

vector_row = vectors[
    vectors["match"]
    == selected_match
].iloc[0]

# =========================
# PLAYER MATCH FILTER
# =========================

match_players = player_df[
    player_df["match"]
    .str.contains(
        selected_match.split(",")[0],
        case=False,
        na=False
    )
].copy()

if "minutesOnField" in match_players.columns:

    match_players = match_players[
        match_players["minutesOnField"] > 0
    ]

ucluj_players = match_players[
    match_players["teamId"]
    == UCLUJ_TEAM_ID
]

opponent_players = match_players[
    match_players["teamId"]
    != UCLUJ_TEAM_ID
]

# =========================
# SEASON BASELINE
# =========================

season_means = player_df[
    [
        "goals",
        "assists",
        "shots",
        "passes",
        "interceptions",
        "recoveries"
    ]
].mean()

def safe_ratio(val, avg):

    if avg == 0:
        return 0

    r = val / avg

    if r > 2:
        r = 2

    if r < 0:
        r = 0

    return r

def compute_scores(players):

    if len(players) == 0:

        return {

            "attack": 0,
            "defense": 0,
            "possession": 0,
            "control": 0,
            "overall": 0

        }

    totals = players[
        [
            "goals",
            "assists",
            "shots",
            "passes",
            "interceptions",
            "recoveries"
        ]
    ].sum()

    attack = (

        safe_ratio(
            totals["goals"],
            season_means["goals"]
        )

        +

        safe_ratio(
            totals["shots"],
            season_means["shots"]
        )

    ) / 2

    defense = (

        safe_ratio(
            totals["interceptions"],
            season_means["interceptions"]
        )

        +

        safe_ratio(
            totals["recoveries"],
            season_means["recoveries"]
        )

    ) / 2

    possession = safe_ratio(
        totals["passes"],
        season_means["passes"]
    )

    control = safe_ratio(
        totals["assists"],
        season_means["assists"]
    )

    overall_raw = (

        0.30 * attack +

        0.30 * defense +

        0.20 * possession +

        0.20 * control
    )

    def scale(x):

        val = x * 5

        if val > 10:
            val = 10

        return round(val, 2)

    return {

        "attack": scale(attack),
        "defense": scale(defense),
        "possession": scale(possession),
        "control": scale(control),
        "overall": scale(overall_raw)

    }

ucluj_scores = compute_scores(
    ucluj_players
)

opponent_scores = compute_scores(
    opponent_players
)

team_score = ucluj_scores["overall"]

opponent_score = opponent_scores["overall"]

overall_score = round(
    (team_score + opponent_score) / 2,
    2
)

# =========================
# SCORE DISPLAY
# =========================

st.subheader("Match Scores")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "U Cluj Score",
        f"{team_score} / 10"
    )

with col2:

    st.metric(
        "Opponent Score",
        f"{opponent_score} / 10"
    )

with col3:

    st.metric(
        "Overall Score",
        f"{overall_score} / 10"
    )

# =========================
# COMPONENT CHART
# =========================

st.header("Team Components")

ucluj_df = pd.DataFrame({

    "Metric": [
        "Attack",
        "Defense",
        "Possession",
        "Control"
    ],

    "Score": [

        ucluj_scores["attack"],
        ucluj_scores["defense"],
        ucluj_scores["possession"],
        ucluj_scores["control"]

    ]

})

fig = px.bar(
    ucluj_df,
    x="Metric",
    y="Score"
)

st.plotly_chart(fig)

# =========================
# RADAR (ramane)
# =========================

feature_labels = {

    "progression_index":
        "Ball Progression",

    "risk_index":
        "Build-up Risk",

    "final_third_index":
        "Final Third Presence",

    "defensive_stability_index":
        "Defensive Stability",

    "pressing_recovery_index":
        "Pressing Recovery",

    "possession_security_index":
        "Possession Security",

    "attacking_threat_index":
        "Attacking Threat"
}

features = list(
    feature_labels.keys()
)

st.header("Tactical Profile")

radar_df = pd.DataFrame({

    "Metric": [
        feature_labels[f]
        for f in features
    ],

    "Value": [
        vector_row[f]
        for f in features
    ]
})

fig = px.line_polar(
    radar_df,
    r="Value",
    theta="Metric",
    line_close=True
)

st.plotly_chart(fig)