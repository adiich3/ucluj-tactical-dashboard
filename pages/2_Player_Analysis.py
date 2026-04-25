import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.title("Player Analysis")

UCLUJ_TEAM_ID = 60374

player_df = pd.read_csv("player_stats.csv")

ucluj_players = player_df[
    player_df["teamId"] == UCLUJ_TEAM_ID
].copy()

metrics = [
    "goals",
    "assists",
    "shots",
    "passes",
    "interceptions",
    "recoveries"
]

metric_labels = {
    "goals": "Goals",
    "assists": "Assists",
    "shots": "Shots",
    "passes": "Passing",
    "interceptions": "Interceptions",
    "recoveries": "Recoveries"
}

# =========================
# FILTERS
# =========================

st.header("Filters")

positions = sorted(
    ucluj_players["position"]
    .dropna()
    .unique()
)

selected_position = st.selectbox(
    "Select Position",
    ["All"] + positions
)

analysis_mode = st.radio(
    "Select Analysis Type",
    [
        "Overall Player Analysis",
        "Single Match Player Analysis"
    ]
)

base_players = ucluj_players.copy()

if analysis_mode == "Single Match Player Analysis":

    if "match" in ucluj_players.columns:

        match_list = sorted(
            ucluj_players["match"]
            .dropna()
            .unique()
        )

        selected_match = st.selectbox(
            "Select Match",
            match_list
        )

        base_players = ucluj_players[
            ucluj_players["match"] == selected_match
        ].copy()

    else:

        st.warning(
            "The dataset does not contain a 'match' column."
        )

if selected_position != "All":

    filtered_players = base_players[
        base_players["position"] == selected_position
    ].copy()

else:

    filtered_players = base_players.copy()

if len(filtered_players) == 0:

    st.warning("No players found for the selected filters.")
    st.stop()

# =========================
# SINGLE MATCH SUMMARY
# =========================

if analysis_mode == "Single Match Player Analysis":

    st.header("Selected Match Player Overview")

    display_columns = [
        "playerName",
        "position",
        "goals",
        "assists",
        "shots",
        "passes",
        "interceptions",
        "recoveries"
    ]

    available_columns = [
        col for col in display_columns
        if col in filtered_players.columns
    ]

    st.dataframe(
        filtered_players[available_columns]
    )

    st.subheader("Best Players in This Match")

    match_players = filtered_players.copy()

    match_players["performance_score"] = (
        match_players["goals"] * 4
        +
        match_players["assists"] * 3
        +
        match_players["shots"] * 1
        +
        match_players["passes"] * 0.03
        +
        match_players["interceptions"] * 1.5
        +
        match_players["recoveries"] * 1.2
    )

    best_match_players = (
        match_players
        .sort_values(
            by="performance_score",
            ascending=False
        )
        .head(5)
    )

    st.dataframe(
        best_match_players[
            [
                "playerName",
                "position",
                "performance_score",
                "goals",
                "assists",
                "shots",
                "passes",
                "interceptions",
                "recoveries"
            ]
        ]
    )

    fig_match = px.bar(
        best_match_players,
        x="playerName",
        y="performance_score",
        color="position",
        title="Top Player Performance in Selected Match"
    )

    st.plotly_chart(
        fig_match,
        use_container_width=True
    )

# =========================
# TOP PLAYER METRICS
# =========================

st.header("Top Player Contributions")

top_goals = (
    filtered_players
    .groupby("playerName")["goals"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

st.subheader("Top Goal Scorers")
st.dataframe(top_goals)

top_assists = (
    filtered_players
    .groupby("playerName")["assists"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

st.subheader("Top Assist Providers")
st.dataframe(top_assists)

top_defensive = (
    filtered_players
    .groupby("playerName")["interceptions"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .reset_index()
)

st.subheader("Top Defensive Players")
st.dataframe(top_defensive)

# =========================
# NORMALIZE DATA
# =========================

norm_players = filtered_players.copy()

for m in metrics:

    max_val = norm_players[m].max()

    if max_val > 0:

        norm_players[m] = (
            norm_players[m] /
            max_val
        )

# =========================
# PLAYER PROGRESSION
# =========================

if analysis_mode == "Overall Player Analysis":

    progression_rows = []

    for player in norm_players["playerName"].unique():

        p_data = norm_players[
            norm_players["playerName"] == player
        ].copy()

        if len(p_data) < 4:
            continue

        if "match" not in p_data.columns:
            continue

        p_data = p_data.sort_values(
            by="match"
        )

        half = len(p_data) // 2

        first_half = p_data.iloc[:half]
        second_half = p_data.iloc[-half:]

        change_total = 0

        for m in metrics:

            change_total += (
                second_half[m].mean()
                -
                first_half[m].mean()
            )

        progression_rows.append({
            "playerName": player,
            "position": p_data["position"].iloc[0],
            "progress_score": round(
                change_total,
                3
            )
        })

    progression_df = pd.DataFrame(
        progression_rows
    )

    if len(progression_df) > 0:

        progression_df = progression_df.sort_values(
            by="progress_score",
            ascending=False
        )

        st.header("Player Progression")

        st.subheader("Top Improving")

        st.dataframe(
            progression_df.head(5)
        )

        st.subheader("Top Regressing")

        st.dataframe(
            progression_df.tail(5)
        )

        st.header("Export Data")

        csv = progression_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Progression Report",
            data=csv,
            file_name="player_progression_report.csv",
            mime="text/csv"
        )

# =========================
# PLAYER RADAR
# =========================

st.header("Player Radar")

player_list = sorted(
    filtered_players["playerName"]
    .dropna()
    .unique()
)

selected_player = st.selectbox(
    "Select Player",
    player_list,
    key="radar_player"
)

player_summary = (
    filtered_players
    .groupby("playerName")[metrics]
    .mean()
    .reset_index()
)

norm_summary = player_summary.copy()

for m in metrics:

    max_val = norm_summary[m].max()

    if max_val > 0:

        norm_summary[m] = (
            norm_summary[m] /
            max_val
        )

selected_row = norm_summary[
    norm_summary["playerName"] == selected_player
]

radar_values = []

for m in metrics:

    radar_values.append(
        selected_row[m].values[0]
    )

radar_df = pd.DataFrame({

    "Metric": [
        metric_labels[m] for m in metrics
    ],

    "Value": radar_values

})

fig_radar = px.line_polar(
    radar_df,
    r="Value",
    theta="Metric",
    line_close=True
)

fig_radar.update_traces(
    fill="toself"
)

st.plotly_chart(
    fig_radar,
    use_container_width=True
)

# =========================
# PLAYER COMPARISON
# =========================

st.header("Player Comparison")

col1, col2 = st.columns(2)

with col1:

    player_1 = st.selectbox(
        "Select Player 1",
        player_list,
        key="player1"
    )

with col2:

    player_2 = st.selectbox(
        "Select Player 2",
        player_list,
        index=1 if len(player_list) > 1 else 0,
        key="player2"
    )

player1_data = filtered_players[
    filtered_players["playerName"] == player_1
]

player2_data = filtered_players[
    filtered_players["playerName"] == player_2
]

p1_values = []
p2_values = []

for m in metrics:

    p1_values.append(
        player1_data[m].mean()
    )

    p2_values.append(
        player2_data[m].mean()
    )

radar_compare_df = pd.DataFrame({
    "Metric": metrics * 2,
    "Value": p1_values + p2_values,
    "Player": (
        [player_1] * len(metrics)
        +
        [player_2] * len(metrics)
    )
})

fig_compare = px.line_polar(
    radar_compare_df,
    r="Value",
    theta="Metric",
    color="Player",
    line_close=True
)

fig_compare.update_traces(
    fill="toself"
)

st.plotly_chart(
    fig_compare,
    use_container_width=True
)

st.subheader("Metric Comparison Table")

comparison_table = pd.DataFrame({
    "Metric": metrics,
    player_1: p1_values,
    player_2: p2_values
})

st.dataframe(comparison_table)
