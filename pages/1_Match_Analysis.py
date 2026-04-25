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
    y="Strength",
    title="Tactical Strength Breakdown"
)

st.plotly_chart(fig_strength)

# =========================
# METRIC COMPARISON
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

    barmode="group"
)

st.plotly_chart(fig_compare)

# =========================
# AI RECOMMENDATIONS
# =========================

st.header("AI Tactical Recommendations")

recommendations = []

if norm_risk > 1:
    recommendations.append(
        "Reduce build-up risk in defensive zones"
    )

if norm_progression < 1:
    recommendations.append(
        "Increase ball progression tempo"
    )

if norm_attack < 1:
    recommendations.append(
        "Improve attacking threat creation"
    )

if norm_defense < 1:
    recommendations.append(
        "Strengthen defensive organization"
    )

if norm_pressing < 1:
    recommendations.append(
        "Increase pressing recovery intensity"
    )

if len(recommendations) == 0:

    recommendations.append(
        "Stable tactical balance detected"
    )

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

        "metric":
            feature_labels[f],

        "difference":
            diff
    })

diff_df = pd.DataFrame(
    comparison_values
)

# Strengths

strengths = diff_df.sort_values(
    by="difference",
    ascending=False
)

st.subheader("Top 3 Strengths")

for i in range(3):

    st.write(
        "•",
        strengths.iloc[i]["metric"]
    )

# Weaknesses

weaknesses = diff_df.sort_values(
    by="difference",
    ascending=True
)

st.subheader("Top 3 Weaknesses")

for i in range(3):

    st.write(
        "•",
        weaknesses.iloc[i]["metric"]
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
        "Progression"
    ],

    "Score": [
        attack_score,
        defense_score,
        possession_score,
        progression_score
    ]
})

fig_summary = px.bar(

    summary_df,
    x="Metric",
    y="Score",
    title="Team Tactical Components"
)

st.plotly_chart(fig_summary)