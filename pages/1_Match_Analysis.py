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
# FEATURES
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

cluster_names = {

    0: "High Risk Build-up Match",

    1: "Low Intensity Match",

    2: "Defensive Pressure Match",

    3: "Dominant Attacking Match"
}

# =========================
# NORMALIZATION
# =========================

season_avg = vectors[features].mean()

def safe_norm(value, avg):

    if avg == 0:
        return 0

    val = value / avg

    if val > 2:
        val = 2

    if val < 0:
        val = 0

    return val

norm_attack = safe_norm(
    vector_row["attacking_threat_index"],
    season_avg["attacking_threat_index"]
)

norm_progression = safe_norm(
    vector_row["progression_index"],
    season_avg["progression_index"]
)

norm_possession = safe_norm(
    vector_row["possession_security_index"],
    season_avg["possession_security_index"]
)

norm_defense = safe_norm(
    vector_row["defensive_stability_index"],
    season_avg["defensive_stability_index"]
)

norm_pressing = safe_norm(
    vector_row["pressing_recovery_index"],
    season_avg["pressing_recovery_index"]
)

norm_final = safe_norm(
    vector_row["final_third_index"],
    season_avg["final_third_index"]
)

norm_risk = safe_norm(
    vector_row["risk_index"],
    season_avg["risk_index"]
)

# =========================
# SCORE
# =========================

raw_team_score = (

    0.20 * norm_attack +

    0.15 * norm_progression +

    0.15 * norm_possession +

    0.15 * norm_defense +

    0.10 * norm_pressing +

    0.10 * norm_final -

    0.15 * norm_risk
)

raw_team_score = max(
    0,
    min(raw_team_score, 2)
)

team_score = round(
    raw_team_score * 5,
    2
)

opponent_score = round(
    10 - team_score,
    2
)

overall_score = round(
    (team_score + opponent_score) / 2,
    2
)

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

st.write("Match:", selected_match)

st.write(
    "Cluster Type:",
    cluster_label
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
        "Team Score",
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

    st.write("-", row["match"])

# =========================
# MATCH TAGS
# =========================

st.header("Match Tags")

tags = []

if norm_attack > 1.1:
    tags.append("Strong Attack")

if norm_defense < 0.9:
    tags.append("Weak Defense")

if norm_risk > 1.1:
    tags.append("High Risk Build-up")

if norm_progression > 1.1:
    tags.append("Strong Progression")

if norm_final > 1.1:
    tags.append("High Final Third Presence")

if len(tags) == 0:
    tags.append("Balanced Match")

for t in tags:

    st.write("•", t)

# =========================
# STRENGTH BREAKDOWN
# =========================

st.header("Match Strength Breakdown")

strength_df = pd.DataFrame({

    "Category": [
        "Attack",
        "Defense",
        "Possession",
        "Progression",
        "Pressing",
        "Final Third",
        "Risk"
    ],

    "Strength": [
        norm_attack,
        norm_defense,
        norm_possession,
        norm_progression,
        norm_pressing,
        norm_final,
        norm_risk
    ]
})

fig_strength = px.bar(
    strength_df,
    x="Category",
    y="Strength"
)

st.plotly_chart(fig_strength)

# =========================
# TEAM PERFORMANCE SUMMARY
# =========================

st.header("Team Performance Summary")

summary_df = pd.DataFrame({

    "Metric": [
        "Attack",
        "Defense",
        "Possession",
        "Progression"
    ],

    "Score": [
        norm_attack * 10,
        norm_defense * 10,
        norm_possession * 10,
        norm_progression * 10
    ]
})

fig_summary = px.bar(
    summary_df,
    x="Metric",
    y="Score"
)

st.plotly_chart(fig_summary)