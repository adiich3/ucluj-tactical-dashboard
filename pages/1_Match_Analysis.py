import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.metrics.pairwise import euclidean_distances

st.title("Match Analysis")

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

cluster_names = {

    0: "High Risk Build-up Match",

    1: "Low Intensity Match",

    2: "Defensive Pressure Match",

    3: "Dominant Attacking Match"
}

# =========================
# SEARCH + MATCH SELECT
# =========================

match_list = sorted(

    reports["match"]
    .dropna()
    .unique()
    .tolist()
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
# MATCH OVERVIEW
# =========================

st.header("Match Overview")

cluster_id = int(
    match_row["cluster"]
)

cluster_label = cluster_names.get(
    cluster_id,
    "Unknown"
)

quality = (

    "GOOD MATCH"

    if match_row[
        "predicted_quality"
    ] == 1

    else "BAD MATCH"
)

st.write(
    "Match:",
    selected_match
)

st.write(
    "Cluster Type:",
    cluster_label
)

st.write(
    "Predicted Quality:",
    quality
)

# =========================
# SCORE CALCULATION
# =========================

season_avg = vectors[
    features
].mean()

norm_attack = (
    vector_row[
        "attacking_threat_index"
    ]
    /
    season_avg[
        "attacking_threat_index"
    ]
)

norm_progression = (
    vector_row[
        "progression_index"
    ]
    /
    season_avg[
        "progression_index"
    ]
)

norm_possession = (
    vector_row[
        "possession_security_index"
    ]
    /
    season_avg[
        "possession_security_index"
    ]
)

norm_defense = (
    vector_row[
        "defensive_stability_index"
    ]
    /
    season_avg[
        "defensive_stability_index"
    ]
)

norm_pressing = (
    vector_row[
        "pressing_recovery_index"
    ]
    /
    season_avg[
        "pressing_recovery_index"
    ]
)

norm_final = (
    vector_row[
        "final_third_index"
    ]
    /
    season_avg[
        "final_third_index"
    ]
)

norm_risk = (
    vector_row[
        "risk_index"
    ]
    /
    season_avg[
        "risk_index"
    ]
)

# =========================
# TEAM SCORE
# =========================

attack_score = norm_attack * 10

defense_score = norm_defense * 10

possession_score = norm_possession * 10

progression_score = norm_progression * 10

team_score = (

    attack_score * 0.30 +

    defense_score * 0.25 +

    possession_score * 0.25 +

    progression_score * 0.20
)

team_score = round(
    team_score,
    2
)

# =========================
# MATCH SCORE
# =========================

overall_score = (

    0.20 * norm_attack +

    0.15 * norm_progression +

    0.15 * norm_possession +

    0.15 * norm_defense +

    0.10 * norm_pressing +

    0.10 * norm_final -

    0.15 * norm_risk
)

overall_score = max(
    0,
    overall_score
)

overall_score = round(
    overall_score * 5,
    2
)

st.subheader("Scores")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        label="Overall Match Score",
        value=f"{overall_score} / 10"
    )

with col2:

    st.metric(
        label="Team Tactical Score",
        value=f"{team_score} / 10"
    )

# =========================
# MATCH TAGS
# =========================

st.header("Match Tags")

tags = []

if norm_attack > 1.1:

    tags.append(
        "Strong Attack"
    )

if norm_defense < 0.9:

    tags.append(
        "Weak Defense"
    )

if norm_risk > 1.1:

    tags.append(
        "High Risk Build-up"
    )

if norm_progression > 1.1:

    tags.append(
        "Strong Progression"
    )

if len(tags) == 0:

    tags.append(
        "Balanced Match"
    )

for t in tags:

    st.write("•", t)

# =========================
# RADAR PROFILE
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
# METRIC COMPARISON
# =========================

st.header(
    "Metric Comparison vs Season Average"
)

comparison_df = pd.DataFrame({

    "Metric": [

        feature_labels[f]

        for f in features
    ],

    "Match Value": [

        vector_row[f]

        for f in features
    ],

    "Season Average": [

        season_avg[f]

        for f in features
    ]
})

fig_bar = px.bar(

    comparison_df,

    x="Metric",

    y=[

        "Match Value",

        "Season Average"
    ],

    barmode="group"
)

st.plotly_chart(fig_bar)

# =========================
# SIMILAR MATCHES
# =========================

st.header(
    "Most Similar Matches"
)

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

similar_df[
    "distance"
] = distances

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