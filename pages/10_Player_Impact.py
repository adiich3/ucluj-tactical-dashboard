import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

st.title("Player Impact Analysis")

# =========================
# CONSTANTS
# =========================

UCLUJ_TEAM_ID = 60374

metrics = [

    "goals",
    "assists",
    "shots",
    "passes",
    "interceptions",
    "recoveries"

]

# =========================
# LOAD MODEL (SAFE PATH)
# =========================

BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)

model_path = os.path.join(
    BASE_DIR,
    "player_impact_model.pkl"
)

if not os.path.exists(model_path):

    st.error(
        "player_impact_model.pkl not found in repository root."
    )

    st.stop()

model = joblib.load(
    model_path
)

# =========================
# LOAD DATA
# =========================

player_df = pd.read_csv(
    "player_stats.csv"
)

# =========================
# CLEAN MATCH NAMES
# =========================

def clean_match(col):

    return (

        col.astype(str)

        .str.replace(".json", "", regex=False)

        .str.replace("_players_stats", "", regex=False)

        .str.replace("_", " ")

        .str.replace("  ", " ")

        .str.strip()

    )

if "match" not in player_df.columns:

    st.error(
        "player_stats.csv must contain 'match' column."
    )

    st.stop()

player_df["match"] = clean_match(
    player_df["match"]
)

# =========================
# FILTER STRICT U CLUJ
# =========================

ucluj_players = player_df[

    player_df["teamId"]
    == UCLUJ_TEAM_ID

].copy()

if len(ucluj_players) == 0:

    st.error(
        "No Universitatea Cluj players found."
    )

    st.stop()

# =========================
# MATCH SELECT
# =========================

match_list = sorted(

    ucluj_players["match"]

    .dropna()

    .unique()

)

st.caption(
    f"U Cluj Matches Loaded: {len(match_list)}"
)

selected_match = st.selectbox(

    "Select Universitatea Cluj Match",

    match_list

)

match_players = ucluj_players[

    ucluj_players["match"]
    == selected_match

].copy()

if len(match_players) == 0:

    st.warning(
        "No players found for selected match."
    )

    st.stop()

# =========================
# BUILD TEAM VECTOR
# =========================

team_totals = match_players[
    metrics
].sum()

base_vector = np.array(
    team_totals.values
).reshape(1, -1)

base_score = model.predict(
    base_vector
)[0]

# =========================
# CALCULATE PLAYER IMPACT
# =========================

impact_rows = []

for _, player in match_players.iterrows():

    reduced_totals = team_totals.copy()

    for m in metrics:

        reduced_totals[m] -= player[m]

        if reduced_totals[m] < 0:
            reduced_totals[m] = 0

    reduced_vector = np.array(
        reduced_totals.values
    ).reshape(1, -1)

    reduced_score = model.predict(
        reduced_vector
    )[0]

    impact = base_score - reduced_score

    impact_rows.append({

        "playerName":
            player["playerName"],

        "position":
            player["position"],

        "impact_score":
            round(impact, 3)

    })

impact_df = pd.DataFrame(
    impact_rows
)

impact_df = impact_df.sort_values(

    by="impact_score",

    ascending=False

)

# =========================
# DISPLAY TABLE
# =========================

st.header("Player Impact Ranking")

st.dataframe(
    impact_df,
    use_container_width=True
)

# =========================
# TOP IMPACT PLAYERS
# =========================

st.header("Top Impact Players")

top_players = impact_df.head(5)

st.bar_chart(

    top_players.set_index(
        "playerName"
    )["impact_score"]

)

# =========================
# LOW IMPACT PLAYERS
# =========================

st.header("Low Impact Players")

low_players = impact_df.tail(5)

st.bar_chart(

    low_players.set_index(
        "playerName"
    )["impact_score"]

)

# =========================
# MOST CRITICAL PLAYER
# =========================

st.header("Most Critical Player")

best_player = impact_df.iloc[0]

st.metric(

    "Most Impactful Player",

    best_player["playerName"]

)

st.metric(

    "Impact Score",

    best_player["impact_score"]

)

# =========================
# MATCH SCORE INFO
# =========================

st.header("Match Tactical Impact")

st.metric(

    "Predicted Team Score",

    round(base_score, 2)

)
