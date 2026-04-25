import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="U Cluj Tactical Dashboard",
    layout="wide"
)

st.title("U Cluj Tactical Analysis Dashboard")

st.markdown(
"""
Central tactical hub for match, player, and team performance analysis.
"""
)

# =========================
# LOAD DATA
# =========================

try:

    all_reports = pd.read_csv(
        "all_match_reports.csv"
    )

    ucluj_reports = pd.read_csv(
        "ucluj_match_reports.csv"
    )

    vectors = pd.read_csv(
        "ucluj_match_vectors.csv"
    )

except:

    st.warning(
        "Data files not found. Upload datasets to enable dashboard overview."
    )

    all_reports = None
    ucluj_reports = None
    vectors = None

# =========================
# QUICK STATS
# =========================

st.header("Dataset Overview")

if all_reports is not None and vectors is not None:

    total_matches = all_reports["match"].nunique()

    ucluj_matches = ucluj_reports[
        "match"
    ].nunique()

    # recalcul scor mediu real

    feature_list = [
        "progression_index",
        "risk_index",
        "final_third_index",
        "defensive_stability_index",
        "pressing_recovery_index",
        "possession_security_index",
        "attacking_threat_index"
    ]

    season_avg = vectors[
        feature_list
    ].mean()

    scores = []

    for _, row in vectors.iterrows():

        norm_attack = row["attacking_threat_index"] / season_avg["attacking_threat_index"]
        norm_progression = row["progression_index"] / season_avg["progression_index"]
        norm_possession = row["possession_security_index"] / season_avg["possession_security_index"]
        norm_defense = row["defensive_stability_index"] / season_avg["defensive_stability_index"]
        norm_pressing = row["pressing_recovery_index"] / season_avg["pressing_recovery_index"]
        norm_final = row["final_third_index"] / season_avg["final_third_index"]
        norm_risk = row["risk_index"] / season_avg["risk_index"]

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
        score = score * 5

        scores.append(score)

    avg_score = round(sum(scores) / len(scores), 2)
    best_score = round(max(scores), 2)
    worst_score = round(min(scores), 2)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "Total Matches",
            total_matches
        )

    with col2:

        st.metric(
            "U Cluj Matches",
            ucluj_matches
        )

    with col3:

        st.metric(
            "Average Match Score",
            avg_score
        )

    with col4:

        st.metric(
            "Best Match Score",
            best_score
        )

    with col5:

        st.metric(
            "Worst Match Score",
            worst_score
        )

else:

    st.info(
        "Dataset statistics unavailable."
    )
# =========================
# MODULE NAVIGATION
# =========================

st.header("Analysis Modules")

col1, col2, col3 = st.columns(3)

with col1:

    st.subheader("Match Analysis")

    st.markdown(
    """
    Tactical match evaluation  
    Match scoring  
    Tactical radar  
    Similar match detection  
    """
    )

with col2:

    st.subheader("Player Analysis")

    st.markdown(
    """
    Player performance metrics  
    Progress tracking  
    Radar comparisons  
    Top contributors  
    """
    )

with col3:

    st.subheader("Team Overview")

    st.markdown(
    """
    Tactical identity  
    Team-level metrics  
    Performance trends  
    Strength distribution  
    """
    )

col4, col5 = st.columns(2)

with col4:

    st.subheader("Opponent Analysis")

    st.markdown(
    """
    Opponent scouting  
    Threat detection  
    Tactical comparison  
    """
    )

with col5:

    st.subheader("Best Starting XI")

    st.markdown(
    """
    Optimal lineup selection  
    Position-based evaluation  
    Performance ranking  
    """
    )

# =========================
# PROJECT DESCRIPTION
# =========================

st.header("System Purpose")

st.markdown(
"""
This tactical system analyzes match performance using structured statistical indicators.

The platform supports:

Match-level tactical evaluation  
Player performance tracking  
Opponent scouting  
Team identity analysis  
Optimal lineup selection  

All outputs are generated from structured match datasets and statistical models.
"""
)
