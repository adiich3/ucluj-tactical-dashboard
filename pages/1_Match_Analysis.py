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

# player data

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
# SYNC DATASETS
# =========================

common_matches = set(
    reports["match"]
).intersection(
    set(vectors["match"])
)

reports = reports[
    reports["match"]
    .isin(common_matches)
].copy()

vectors = vectors[
    vectors["match"]
    .isin(common_matches)
].copy()

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

# =========================
# SEARCH
# =========================

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

# =========================
# MATCH ROWS
# =========================

match_row = reports[
    reports["match"]
    == selected_match
].iloc[0]

vector_row = vectors[
    vectors["match"]
    == selected_match
].iloc[0]

# =========================
# PLAYER BASED TEAM SCORES
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

def compute_team_score(players):

    if len(players) == 0:
        return 0

    score = 0

    if "goals" in players.columns:
        score += players["goals"].sum() * 1.5

    if "assists" in players.columns:
        score += players["assists"].sum() * 1.2

    if "shots" in players.columns:
        score += players["shots"].sum() * 0.4

    if "passes" in players.columns:
        score += players["passes"].sum() * 0.01

    if "interceptions" in players.columns:
        score += players["interceptions"].sum() * 0.6

    if "recoveries" in players.columns:
        score += players["recoveries"].sum() * 0.5

    score = score / 10

    if score > 10:
        score = 10

    return round(score, 2)

team_score = compute_team_score(
    ucluj_players
)

opponent_score = compute_team_score(
    opponent_players
)

overall_score = round(
    (team_score + opponent_score) / 2,
    2
)

# =========================
# MATCH OVERVIEW
# =========================

st.header("Match Overview")

st.write(
    "Match:",
    selected_match
)

if overall_score >= 8:

    quality = "EXCELLENT MATCH"

elif overall_score >= 6.5:

    quality = "GOOD MATCH"

elif overall_score >= 5:

    quality = "AVERAGE MATCH"

else:

    quality = "POOR MATCH"

st.write(
    "Match Quality:",
    quality
)

# =========================
# SCORES
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
        "Overall Match Score",
        f"{overall_score} / 10"
    )

# =========================
# VECTOR FEATURES
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

# =========================
# RADAR
# =========================

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

# =========================
# SIMILAR MATCHES
# =========================

st.header("Most Similar Matches")

vector_matrix = vectors[
    features
]

match_index = vectors[
    vectors["match"]
    == selected_match
].index[0]

distances = euclidean_distances(

    [vector_matrix.iloc[match_index]],
    vector_matrix
)[0]

similar_df = vectors.copy()

similar_df["distance"] = distances

similar_df = similar_df.sort_values(
    by="distance"
)

similar_df = similar_df[
    similar_df["match"]
    != selected_match
]

top_similar = similar_df.head(3)

for _, row in top_similar.iterrows():

    st.write(
        "-",
        row["match"]
    )