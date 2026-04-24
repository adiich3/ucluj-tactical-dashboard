import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.metrics.pairwise import euclidean_distances

st.title("Match Analysis")

# =========================
# LOAD DATA
# =========================

reports = pd.read_csv("match_tactical_reports.csv")
vectors = pd.read_csv("ucluj_match_vectors.csv")

feature_labels = {
    "progression_index": "Ball Progression",
    "risk_index": "Build-up Risk",
    "final_third_index": "Final Third Presence",
    "defensive_stability_index": "Defensive Stability",
    "pressing_recovery_index": "Pressing Recovery",
    "possession_security_index": "Possession Security",
    "attacking_threat_index": "Attacking Threat"
}

features = list(feature_labels.keys())

cluster_names = {
    0: "High Risk Build-up Match",
    1: "Low Intensity Match",
    2: "Defensive Pressure Match",
    3: "Dominant Attacking Match"
}

# =========================
# SELECT MATCH + SEARCH
# =========================

match_list = reports["match"].tolist()

search_text = st.text_input(
    "Search Match"
)

if search_text:

    match_list = [
        m for m in match_list
        if search_text.lower() in m.lower()
    ]

selected_match = st.selectbox(
    "Select Match",
    match_list
)

match_row = reports[
    reports["match"] == selected_match
].iloc[0]

vector_row = vectors[
    vectors["match"] == selected_match
].iloc[0]

# =========================
# MATCH OVERVIEW
# =========================

st.header("Match Overview")

cluster_id = int(match_row["cluster"])

cluster_label = cluster_names.get(
    cluster_id,
    "Unknown"
)

quality = (
    "GOOD MATCH"
    if match_row["predicted_quality"] == 1
    else "BAD MATCH"
)

st.write("Cluster Type:", cluster_label)
st.write("Predicted Quality:", quality)

# =========================
# MATCH SCORE
# =========================

season_avg = vectors[features].mean()

norm_attack = vector_row["attacking_threat_index"] / season_avg["attacking_threat_index"]
norm_progression = vector_row["progression_index"] / season_avg["progression_index"]
norm_possession = vector_row["possession_security_index"] / season_avg["possession_security_index"]
norm_defense = vector_row["defensive_stability_index"] / season_avg["defensive_stability_index"]
norm_pressing = vector_row["pressing_recovery_index"] / season_avg["pressing_recovery_index"]
norm_final = vector_row["final_third_index"] / season_avg["final_third_index"]
norm_risk = vector_row["risk_index"] / season_avg["risk_index"]

score = (
    0.20 * norm_attack +
    0.15 * norm_progression +
    0.15 * norm_possession +
    0.15 * norm_defense +
    0.10 * norm_pressing +
    0.10 * norm_final -
    0.15 * norm_risk
)

score = max(0, score)
score = round(score * 5, 2)

st.subheader("Match Score")

st.metric(
    label="Overall Match Score",
    value=f"{score} / 10"
)

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

if len(tags) == 0:
    tags.append("Balanced Match")

for t in tags:
    st.write("•", t)
# =========================
# MATCH STRENGTH BREAKDOWN
# =========================

st.header("Match Strength Breakdown")

strength_df = pd.DataFrame({
    "Category": [
        "Attack",
        "Defense",
        "Possession",
        "Progression",
        "Risk"
    ],
    "Strength": [
        norm_attack,
        norm_defense,
        norm_possession,
        norm_progression,
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

st.header("Metric Comparison vs Season Average")

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
    y=["Match Value", "Season Average"],
    barmode="group"
)

st.plotly_chart(fig_bar)

# =========================
# AI RECOMMENDATIONS
# =========================

st.header("AI Tactical Recommendations")

recommendations = []

if vector_row["risk_index"] > season_avg["risk_index"]:
    recommendations.append("Reduce build-up risk")

if vector_row["progression_index"] < season_avg["progression_index"]:
    recommendations.append("Increase ball progression")

if vector_row["attacking_threat_index"] < season_avg["attacking_threat_index"]:
    recommendations.append("Improve attacking threat")

if vector_row["defensive_stability_index"] < season_avg["defensive_stability_index"]:
    recommendations.append("Improve defensive stability")

if len(recommendations) == 0:
    recommendations.append("Balanced tactical performance")

for r in recommendations:
    st.write("-", r)

# =========================
# STRENGTHS AND WEAKNESSES
# =========================

st.header("Strengths and Weaknesses")

comparison_values = []

for f in features:

    diff = (
        vector_row[f]
        -
        season_avg[f]
    )

    comparison_values.append({
        "metric": feature_labels[f],
        "difference": diff
    })

diff_df = pd.DataFrame(
    comparison_values
)

strengths = diff_df.sort_values(
    by="difference",
    ascending=False
)

st.subheader("Top 3 Strengths")

for i in range(3):
    st.write("•", strengths.iloc[i]["metric"])

weaknesses = diff_df.sort_values(
    by="difference",
    ascending=True
)

st.subheader("Top 3 Weaknesses")

for i in range(3):
    st.write("•", weaknesses.iloc[i]["metric"])

# =========================
# SIMILAR MATCHES
# =========================

st.header("Most Similar Matches")

vector_matrix = vectors[features]

match_index = vectors[
    vectors["match"] == selected_match
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
    similar_df["match"] != selected_match
]

top_similar = similar_df.head(3)

for _, row in top_similar.iterrows():
    st.write("-", row["match"])