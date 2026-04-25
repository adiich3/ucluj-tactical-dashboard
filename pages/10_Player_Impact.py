import streamlit as st
import pandas as pd
import numpy as np
import joblib

st.title("Player Impact Analysis")

UCLUJ_TEAM_ID = 60374

# =========================
# LOAD DATA
# =========================

player_df = pd.read_csv(
    "player_stats.csv"
)

vectors = pd.read_csv(
    "ucluj_match_vectors.csv"
)

model = joblib.load(
    "player_impact_model.pkl"
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

        .str.strip()

    )

player_df["match"] = clean_match(
    player_df["match"]
)

vectors["match"] = clean_match(
    vectors["match"]
)

# =========================
# FILTER U CLUJ
# =========================

ucluj_players = player_df[

    player_df["teamId"]
    == UCLUJ_TEAM_ID

].copy()

# =========================
# MATCH SELECT
# =========================

match_list = sorted(

    ucluj_players["match"]
    .dropna()
    .unique()

)

selected_match = st.selectbox(

    "Select Match",

    match_list

)

match_players = ucluj_players[

    ucluj_players["match"]
    == selected_match

].copy()

metrics = [

    "goals",
    "assists",
    "shots",
    "passes",
    "interceptions",
    "recoveries"

]

# =========================
# BASE MATCH VECTOR
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
# PLAYER IMPACT
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
# DISPLAY RESULTS
# =========================

st.header("Player Impact Ranking")

st.dataframe(
    impact_df
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