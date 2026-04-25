# =========================
# MATCH OVERVIEW + TEAM SCORES
# =========================

season_avg = vectors[features].mean()

def safe_norm(value, avg):

    if avg == 0:
        return 0

    val = value / avg

    # limitare valori extreme
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
# TEAM SCORE CALCULATION
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

# clamp
if raw_team_score < 0:
    raw_team_score = 0

if raw_team_score > 2:
    raw_team_score = 2

team_score = round(
    raw_team_score * 5,
    2
)

# =========================
# OPPONENT SCORE (simulat din medie)
# =========================

# pentru moment calculăm opponent ca diferență față de medie

opponent_score = round(
    10 - team_score,
    2
)

# =========================
# OVERALL MATCH SCORE
# =========================

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

st.write(
    "Match:",
    selected_match
)

st.write(
    "Cluster Type:",
    cluster_label
)

# =========================
# QUALITY LABEL
# =========================

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
# SHOW SCORES
# =========================

st.subheader("Match Scores")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        label="Team Score",
        value=f"{team_score} / 10"
    )

with col2:

    st.metric(
        label="Opponent Score",
        value=f"{opponent_score} / 10"
    )

with col3:

    st.metric(
        label="Overall Match Score",
        value=f"{overall_score} / 10"
    )