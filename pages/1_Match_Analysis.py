# =========================
# PLAYER BASED TEAM SCORES (FULL SYSTEM)
# =========================

UCLUJ_TEAM_ID = 60374

# gasim jucatorii din meci

match_players = player_df[
    player_df["match"]
    .str.contains(
        selected_match.split(",")[0],
        case=False,
        na=False
    )
].copy()

# eliminam banca

if "minutesOnField" in match_players.columns:

    match_players = match_players[
        match_players["minutesOnField"] > 0
    ]

ucluj_players = match_players[
    match_players["teamId"]
    == UCLUJ_TEAM_ID
]

opponent_players = match_players[
    match_players["teamId"]
    != UCLUJ_TEAM_ID
]

# =========================
# SEASON BASELINE
# =========================

season_means = player_df[
    [
        "goals",
        "assists",
        "shots",
        "passes",
        "interceptions",
        "recoveries"
    ]
].mean()

def safe_ratio(val, avg):

    if avg == 0:
        return 0

    r = val / avg

    if r > 2:
        r = 2

    if r < 0:
        r = 0

    return r

def compute_team_scores(players):

    if len(players) == 0:

        return {

            "attack": 0,
            "defense": 0,
            "possession": 0,
            "control": 0,
            "overall": 0

        }

    totals = players[
        [
            "goals",
            "assists",
            "shots",
            "passes",
            "interceptions",
            "recoveries"
        ]
    ].sum()

    # =========================
    # COMPONENTS
    # =========================

    attack = (

        safe_ratio(
            totals["goals"],
            season_means["goals"]
        )

        +

        safe_ratio(
            totals["shots"],
            season_means["shots"]
        )

    ) / 2

    defense = (

        safe_ratio(
            totals["interceptions"],
            season_means["interceptions"]
        )

        +

        safe_ratio(
            totals["recoveries"],
            season_means["recoveries"]
        )

    ) / 2

    possession = safe_ratio(
        totals["passes"],
        season_means["passes"]
    )

    control = safe_ratio(
        totals["assists"],
        season_means["assists"]
    )

    # =========================
    # OVERALL
    # =========================

    overall_raw = (

        0.30 * attack +

        0.30 * defense +

        0.20 * possession +

        0.20 * control

    )

    def scale(x):

        val = x * 5

        if val > 10:
            val = 10

        return round(val, 2)

    return {

        "attack": scale(attack),

        "defense": scale(defense),

        "possession": scale(possession),

        "control": scale(control),

        "overall": scale(overall_raw)

    }

ucluj_scores = compute_team_scores(
    ucluj_players
)

opponent_scores = compute_team_scores(
    opponent_players
)

team_score = ucluj_scores["overall"]

opponent_score = opponent_scores["overall"]

overall_score = round(
    (team_score + opponent_score) / 2,
    2
)

# =========================
# SCORE DISPLAY
# =========================

st.subheader("Match Scores")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "U Cluj Score",
        f"{team_score} / 10"
    )

with col2:

    st.metric(
        "Opponent Score",
        f"{opponent_score} / 10"
    )

with col3:

    st.metric(
        "Overall Match Score",
        f"{overall_score} / 10"
    )

# =========================
# COMPONENT SCORES
# =========================

st.header("Team Component Scores")

ucluj_df = pd.DataFrame({

    "Metric": [
        "Attack",
        "Defense",
        "Possession",
        "Control"
    ],

    "Score": [

        ucluj_scores["attack"],
        ucluj_scores["defense"],
        ucluj_scores["possession"],
        ucluj_scores["control"]

    ]

})

fig_team = px.bar(
    ucluj_df,
    x="Metric",
    y="Score",
    title="U Cluj Tactical Components"
)

st.plotly_chart(fig_team)

# =========================
# OPPONENT COMPONENTS
# =========================

st.header("Opponent Component Scores")

opp_df = pd.DataFrame({

    "Metric": [
        "Attack",
        "Defense",
        "Possession",
        "Control"
    ],

    "Score": [

        opponent_scores["attack"],
        opponent_scores["defense"],
        opponent_scores["possession"],
        opponent_scores["control"]

    ]

})

fig_opp = px.bar(
    opp_df,
    x="Metric",
    y="Score",
    title="Opponent Tactical Components"
)

st.plotly_chart(fig_opp)

# =========================
# MATCH QUALITY
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