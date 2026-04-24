import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("Best Starting XI Generator")

UCLUJ_TEAM_ID = 60374

# =========================
# LOAD DATA
# =========================

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

# =========================
# FORMATION SELECTOR
# =========================

st.header("Formation Settings")

formation_option = st.selectbox(
    "Select Tactical System",
    [
        "1-4-3-3",
        "1-4-2-3-1",
        "1-4-4-2"
    ]
)

# =========================
# POSITION GROUPING
# =========================

def categorize_position(pos):

    pos = pos.lower()

    if "goal" in pos:
        return "GK"

    if "back" in pos or "def" in pos:
        return "DEF"

    if "mid" in pos or "wing" in pos:
        return "MID"

    if "forward" in pos or "striker" in pos:
        return "ATT"

    return "MID"

ucluj_players["role"] = (
    ucluj_players["position"]
    .apply(categorize_position)
)

# =========================
# PLAYER GROUPING
# =========================

players_grouped = (
    ucluj_players
    .groupby(
        ["playerName", "position", "role"]
    )[metrics]
    .mean()
    .reset_index()
)

# =========================
# PERFORMANCE SCORE
# =========================

players_grouped["performance_score"] = (
    players_grouped["goals"] * 1.5 +
    players_grouped["assists"] * 1.2 +
    players_grouped["shots"] * 0.5 +
    players_grouped["passes"] * 0.05 +
    players_grouped["interceptions"] * 0.7 +
    players_grouped["recoveries"] * 0.7
)

# =========================
# FORMATION LOGIC
# =========================

if formation_option == "1-4-3-3":

    formation_roles = {
        "GK": 1,
        "DEF": 4,
        "MID": 3,
        "ATT": 3
    }

elif formation_option == "1-4-2-3-1":

    formation_roles = {
        "GK": 1,
        "DEF": 4,
        "MID": 2,
        "ATT": 4
    }

elif formation_option == "1-4-4-2":

    formation_roles = {
        "GK": 1,
        "DEF": 4,
        "MID": 4,
        "ATT": 2
    }

# =========================
# BUILD BEST XI
# =========================

best_xi_rows = []

for role in formation_roles:

    role_players = players_grouped[
        players_grouped["role"] == role
    ]

    role_players = role_players.sort_values(
        by="performance_score",
        ascending=False
    )

    selected = role_players.head(
        formation_roles[role]
    )

    best_xi_rows.append(selected)

best_xi = pd.concat(best_xi_rows)

# =========================
# DISPLAY TABLE
# =========================

st.header("Generated Best XI")

display_df = best_xi[
    [
        "playerName",
        "position",
        "role",
        "performance_score"
    ]
]

st.dataframe(display_df)

# =========================
# FIELD VISUALIZATION
# =========================

st.header("Formation View")

if formation_option == "1-4-3-3":

    formation_positions = [
        ("GK",(50,5)),

        ("DEF",(15,25)),
        ("DEF",(35,25)),
        ("DEF",(65,25)),
        ("DEF",(85,25)),

        ("MID",(25,50)),
        ("MID",(50,45)),
        ("MID",(75,50)),

        ("ATT",(25,75)),
        ("ATT",(50,80)),
        ("ATT",(75,75))
    ]

elif formation_option == "1-4-2-3-1":

    formation_positions = [
        ("GK",(50,5)),

        ("DEF",(15,25)),
        ("DEF",(35,25)),
        ("DEF",(65,25)),
        ("DEF",(85,25)),

        ("MID",(40,45)),
        ("MID",(60,45)),

        ("ATT",(25,65)),
        ("ATT",(50,70)),
        ("ATT",(75,65)),

        ("ATT",(50,85))
    ]

elif formation_option == "1-4-4-2":

    formation_positions = [
        ("GK",(50,5)),

        ("DEF",(15,25)),
        ("DEF",(35,25)),
        ("DEF",(65,25)),
        ("DEF",(85,25)),

        ("MID",(15,50)),
        ("MID",(40,50)),
        ("MID",(60,50)),
        ("MID",(85,50)),

        ("ATT",(40,80)),
        ("ATT",(60,80))
    ]

fig = go.Figure()

fig.add_shape(
    type="rect",
    x0=0,
    y0=0,
    x1=100,
    y1=100,
    line=dict(color="white")
)

fig.add_shape(
    type="line",
    x0=0,
    y0=50,
    x1=100,
    y1=50,
    line=dict(color="white")
)

fig.add_shape(
    type="circle",
    x0=40,
    y0=40,
    x1=60,
    y1=60,
    line=dict(color="white")
)

fig.update_layout(
    plot_bgcolor="green",
    paper_bgcolor="green",
    xaxis=dict(visible=False, range=[0,100]),
    yaxis=dict(visible=False, range=[0,100]),
    height=650
)

role_groups = {
    "GK": best_xi[best_xi["role"]=="GK"].reset_index(),
    "DEF": best_xi[best_xi["role"]=="DEF"].reset_index(),
    "MID": best_xi[best_xi["role"]=="MID"].reset_index(),
    "ATT": best_xi[best_xi["role"]=="ATT"].reset_index()
}

role_index = {
    "GK":0,
    "DEF":0,
    "MID":0,
    "ATT":0
}

for role,coord in formation_positions:

    if role_index[role] < len(role_groups[role]):

        player_name = role_groups[role].iloc[
            role_index[role]
        ]["playerName"]

        role_index[role]+=1

        x,y = coord

        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                text=[player_name],
                textposition="top center",
                marker=dict(size=18),
                showlegend=False
            )
        )

st.plotly_chart(fig)
# =========================
# BENCH PLAYERS
# =========================

st.header("Substitute Bench")

# eliminam jucatorii deja selectati in XI

selected_names = display_df["playerName"].tolist()

remaining_players = players_grouped[
    ~players_grouped["playerName"].isin(
        selected_names
    )
]

remaining_players = remaining_players.sort_values(
    by="performance_score",
    ascending=False
)

# selectam 7 rezerve

bench_players = remaining_players.head(7)

bench_display = bench_players[
    [
        "playerName",
        "position",
        "role",
        "performance_score"
    ]
]

st.dataframe(
    bench_display
)

# =========================
# EXPORT FULL SQUAD
# =========================

st.header("Export Full Squad")

full_squad = pd.concat([
    display_df,
    bench_display
])

csv_full = full_squad.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Full Squad (XI + Bench)",
    data=csv_full,
    file_name="full_squad_selection.csv",
    mime="text/csv"
)