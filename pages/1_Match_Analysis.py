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

    reports = pd.read_csv("all_match_reports.csv")
    vectors = pd.read_csv("all_match_vectors.csv")

else:

    reports = pd.read_csv("ucluj_match_reports.csv")
    vectors = pd.read_csv("ucluj_match_vectors.csv")

# =========================
# FEATURES
# =========================

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
# SAFETY CHECK
# =========================

required_report_cols = [
    "match",
    "cluster"
]

required_vector_cols = [
    "match"
] + features

for col in required_report_cols:
    if col not in reports.columns:
        st.error(f"Missing column in reports: {col}")
        st.stop()

for col in required_vector_cols:
    if col not in vectors.columns:
        st.error(f"Missing column in vectors: {col}")
        st.stop()

# =========================
# FILTER U CLUJ
# =========================

if data_mode == "U Cluj Matches":

    reports = reports[
        reports["match"]
        .astype(str)
        .str.contains(
            "Universitatea Cluj",
            case=False,
            na=False
        )
    ].copy()

    vectors = vectors[
        vectors["match"]
        .astype(str)
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
    reports["match"].isin(common_matches)
].copy()

vectors = vectors[
    vectors["match"].isin(common_matches)
].copy()

if len(reports) == 0 or len(vectors) == 0:
    st.warning("No matching reports and vectors found.")
    st.stop()

reports = reports.reset_index(drop=True)
vectors = vectors.reset_index(drop=True)

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

search_text = st.text_input("Search Match")

if search_text:
    match_list = [
        m for m in match_list
        if search_text.lower() in m.lower()
    ]

if len(match_list) == 0:
    st.warning("No match found.")
    st.stop()

selected_match = st.selectbox(
    "Select Match",
    match_list
)

# =========================
# MATCH ROWS
# =========================

match_row = reports[
    reports["match"] == selected_match
].iloc[0]

vector_row = vectors[
    vectors["match"] == selected_match
].iloc[0]

# =========================
# NORMALIZATION
# =========================

season_avg = vectors[features].mean()

def safe_norm(value, avg):

    if avg == 0:
        return 0

    val = value / avg

    if val > 3:
        val = 3

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
# MATCH SCORE
# =========================

def compute_match_score(
    attack,
    progression,
    possession,
    defense,
    pressing,
    final_third,
    risk
):

    attack = min(attack, 2.5)
    progression = min(progression, 2.5)
    possession = min(possession, 2.5)
    defense = min(defense, 2.5)
    pressing = min(pressing, 2.5)
    final_third = min(final_third, 2.5)
    risk = min(risk, 2.5)

    positive_score = (
        attack * 0.24
        +
        progression * 0.16
        +
        possession * 0.13
        +
        defense * 0.16
        +
        pressing * 0.13
        +
        final_third * 0.18
    )

    risk_penalty = risk * 0.08

    raw_score = positive_score - risk_penalty

    intensity_boost = (
        attack
        +
        progression
        +
        pressing
        +
        final_third
    ) / 4

    raw_score = raw_score + (intensity_boost - 1) * 0.15

    normalized = (
        raw_score
        -
        0.45
    ) / (
        1.35
        -
        0.45
    )

    normalized = max(
        0,
        min(normalized, 1)
    )

    return round(
        normalized * 10,
        2
    )


team_score = compute_match_score(
    norm_attack,
    norm_progression,
    norm_possession,
    norm_defense,
    norm_pressing,
    norm_final,
    norm_risk
)

# opponent score is independent, not 10 - team_score

opponent_attack = safe_norm(
    season_avg["defensive_stability_index"],
    vector_row["defensive_stability_index"]
)

opponent_progression = safe_norm(
    season_avg["pressing_recovery_index"],
    vector_row["pressing_recovery_index"]
)

opponent_possession = safe_norm(
    season_avg["possession_security_index"],
    vector_row["possession_security_index"]
)

opponent_defense = safe_norm(
    season_avg["attacking_threat_index"],
    vector_row["attacking_threat_index"]
)

opponent_pressing = safe_norm(
    season_avg["progression_index"],
    vector_row["progression_index"]
)

opponent_final = safe_norm(
    season_avg["final_third_index"],
    vector_row["final_third_index"]
)

opponent_risk = safe_norm(
    vector_row["risk_index"],
    season_avg["risk_index"]
)

opponent_score = compute_match_score(
    opponent_attack,
    opponent_progression,
    opponent_possession,
    opponent_defense,
    opponent_pressing,
    opponent_final,
    opponent_risk
)

overall_score = round(
    (
        team_score
        +
        opponent_score
    ) / 2,
    2
)

# =========================
# MATCH OVERVIEW
# =========================

st.header("Match Overview")

cluster_id = int(match_row["cluster"])

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

st.caption(
    "Scores are calculated independently from tactical indicators. Opponent Score is not 10 minus Team Score."
)

# =========================
# SCORE BREAKDOWN
# =========================

st.subheader("Score Breakdown")

score_breakdown = pd.DataFrame({
    "Component": [
        "Attack",
        "Progression",
        "Possession",
        "Defense",
        "Pressing",
        "Final Third",
        "Risk"
    ],
    "Normalized Value": [
        norm_attack,
        norm_progression,
        norm_possession,
        norm_defense,
        norm_pressing,
        norm_final,
        norm_risk
    ]
})

fig_score_breakdown = px.bar(
    score_breakdown,
    x="Component",
    y="Normalized Value",
    title="Normalized Tactical Components"
)

st.plotly_chart(
    fig_score_breakdown,
    use_container_width=True
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
    line_close=True,
    title="Raw Tactical Vector"
)

fig.update_traces(
    fill="toself"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================
# SIMILAR MATCHES
# =========================

st.header("Most Similar Matches")

vector_matrix = vectors[features].reset_index(drop=True)

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

# =========================
# MATCH TAGS
# =========================

st.header("Match Tags")

tags = []

if norm_attack > 1.15:
    tags.append("Strong Attack")

if norm_defense < 0.85:
    tags.append("Weak Defense")

if norm_risk > 1.15:
    tags.append("High Risk Build-up")

if norm_progression > 1.15:
    tags.append("Strong Progression")

if norm_final > 1.15:
    tags.append("High Final Third Presence")

if norm_pressing > 1.15:
    tags.append("Strong Pressing / Recovery")

if norm_possession > 1.15:
    tags.append("Secure Possession")

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
    y="Strength",
    title="Match Strengths Relative to Season Average"
)

st.plotly_chart(
    fig_strength,
    use_container_width=True
)

# =========================
# TEAM PERFORMANCE SUMMARY
# =========================

st.header("Team Performance Summary")

summary_df = pd.DataFrame({
    "Metric": [
        "Attack",
        "Defense",
        "Possession",
        "Progression",
        "Pressing",
        "Final Third"
    ],
    "Score": [
        min(norm_attack * 5, 10),
        min(norm_defense * 5, 10),
        min(norm_possession * 5, 10),
        min(norm_progression * 5, 10),
        min(norm_pressing * 5, 10),
        min(norm_final * 5, 10)
    ]
})

fig_summary = px.bar(
    summary_df,
    x="Metric",
    y="Score",
    title="Team Performance Scores"
)

st.plotly_chart(
    fig_summary,
    use_container_width=True
)

# =========================
# METRIC COMPARISON VS SEASON
# =========================

st.header("Metric Comparison vs Season")

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

fig_compare = px.bar(
    comparison_df,
    x="Metric",
    y=[
        "Match Value",
        "Season Average"
    ],
    barmode="group",
    title="Selected Match vs Season Average"
)

st.plotly_chart(
    fig_compare,
    use_container_width=True
)

# =========================
# AI TACTICAL RECOMMENDATIONS
# =========================

st.header("AI Tactical Recommendations")

recommendations = []

if norm_risk > 1.15:
    recommendations.append(
        "Reduce build-up risk in defensive phase."
    )

if norm_progression < 0.9:
    recommendations.append(
        "Increase ball progression tempo."
    )

if norm_attack < 0.9:
    recommendations.append(
        "Improve attacking threat creation."
    )

if norm_defense < 0.9:
    recommendations.append(
        "Strengthen defensive compactness."
    )

if norm_pressing < 0.9:
    recommendations.append(
        "Increase pressing and recovery intensity."
    )

if norm_possession < 0.9:
    recommendations.append(
        "Improve possession security and reduce unnecessary losses."
    )

if norm_final < 0.9:
    recommendations.append(
        "Improve final-third presence."
    )

if len(recommendations) == 0:
    recommendations.append(
        "Stable tactical balance detected."
    )

for r in recommendations:
    st.write("-", r)

# =========================
# STRENGTHS AND WEAKNESSES
# =========================

st.header("Strengths and Weaknesses")

comparison_values = []

for f in features:

    diff = vector_row[f] - season_avg[f]

    comparison_values.append({
        "metric": feature_labels[f],
        "difference": diff
    })

diff_df = pd.DataFrame(comparison_values)

strengths = diff_df.sort_values(
    by="difference",
    ascending=False
)

weaknesses = diff_df.sort_values(
    by="difference",
    ascending=True
)

st.subheader("Top 3 Strengths")

for i in range(min(3, len(strengths))):
    st.write(
        "•",
        strengths.iloc[i]["metric"]
    )

st.subheader("Top 3 Weaknesses")

for i in range(min(3, len(weaknesses))):
    st.write(
        "•",
        weaknesses.iloc[i]["metric"]
    )
