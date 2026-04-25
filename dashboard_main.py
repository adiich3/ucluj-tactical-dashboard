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

if all_reports is not None:

    total_matches = all_reports["match"].nunique()

    ucluj_matches = ucluj_reports[
        "match"
    ].nunique()

    avg_score = None

    if vectors is not None:

        if "attacking_threat_index" in vectors.columns:

            avg_score = round(
                vectors[
                    "attacking_threat_index"
                ].mean(),
                2
            )

    col1, col2, col3 = st.columns(3)

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

        if avg_score is not None:

            st.metric(
                "Average Attack Index",
                avg_score
            )

        else:

            st.metric(
                "Average Attack Index",
                "N/A"
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
