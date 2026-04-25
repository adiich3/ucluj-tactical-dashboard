import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.title("Training Load AI Dashboard")

# =========================
# LOAD DATA
# =========================

try:

    df = pd.read_csv(
        "training_load_clean.csv"
    )

    weekly_df = pd.read_csv(
        "weekly_training_load.csv"
    )

except Exception as e:

    st.error("Training dataset not found.")
    st.stop()

# =========================
# CHECK REQUIRED COLUMNS
# =========================

required_cols = [
    "Players",
    "Total Load",
    "Load Intensity",
    "Fatigue Score"
]

for col in required_cols:

    if col not in df.columns:

        st.error(f"Missing column: {col}")
        st.stop()

# =========================
# PLAYER SUMMARY
# =========================

st.header("Player Load Overview")

player_summary = (

    df

    .groupby("Players")[

        [
            "Total Load",
            "Load Intensity",
            "Fatigue Score"
        ]

    ]

    .mean()

    .reset_index()

)

player_summary = player_summary.sort_values(

    by="Total Load",
    ascending=False

)

st.dataframe(
    player_summary,
    use_container_width=True
)

# =========================
# TOP LOAD PLAYERS
# =========================

st.header("Top Training Load Players")

top_players = player_summary.head(10)

fig_top = px.bar(

    top_players,

    x="Players",

    y="Total Load",

    title="Top Players by Training Load"

)

st.plotly_chart(
    fig_top,
    use_container_width=True
)

# =========================
# FATIGUE RISK
# =========================

st.header("Fatigue Risk Detection")

high_fatigue = player_summary[

    player_summary["Fatigue Score"] > 7

]

if len(high_fatigue) > 0:

    st.warning(
        "Players with high fatigue detected"
    )

    st.dataframe(
        high_fatigue,
        use_container_width=True
    )

else:

    st.success(
        "No high fatigue players detected"
    )

# =========================
# WEEKLY LOAD TREND
# =========================

st.header("Weekly Load Trend")

if "Week Calendar" in weekly_df.columns:

    fig_weekly = px.line(

        weekly_df,

        x="Week Calendar",

        y="Total Load",

        title="Weekly Training Load"

    )

    st.plotly_chart(
        fig_weekly,
        use_container_width=True
    )

# =========================
# INDIVIDUAL PLAYER VIEW
# =========================

st.header("Individual Player Load")

player_list = sorted(

    df["Players"]

    .dropna()

    .unique()

)

selected_player = st.selectbox(

    "Select Player",

    player_list

)

player_data = df[

    df["Players"] == selected_player

]

if "Sessions" in player_data.columns:

    fig_player = px.line(

        player_data,

        x="Sessions",

        y="Total Load",

        title="Player Load per Session"

    )

    st.plotly_chart(
        fig_player,
        use_container_width=True
    )

# =========================
# AI INJURY RISK
# =========================

st.header("AI Injury Risk Indicator")

def calculate_injury_risk(row):

    fatigue = row["Fatigue Score"]
    intensity = row["Load Intensity"]
    load = row["Total Load"]

    risk = (

        fatigue * 0.5 +

        intensity * 0.3 +

        load * 0.2

    )

    return risk

player_summary["Injury Risk Score"] = (

    player_summary.apply(

        calculate_injury_risk,

        axis=1

    )

)

def risk_level(score):

    if score > 7:
        return "HIGH"

    elif score > 4:
        return "MEDIUM"

    else:
        return "LOW"

player_summary["Risk Level"] = (

    player_summary["Injury Risk Score"]

    .apply(risk_level)

)

risk_df = player_summary.sort_values(

    by="Injury Risk Score",

    ascending=False

)

st.subheader("Player Injury Risk Ranking")

st.dataframe(

    risk_df[

        [

            "Players",

            "Injury Risk Score",

            "Risk Level"

        ]

    ],

    use_container_width=True

)

# =========================
# HIGH SPEED LOAD
# =========================

if "Speed Zones (m) [25.0, 50.0]" in df.columns:

    st.header("High Speed Load Leaders")

    speed_summary = (

        df

        .groupby("Players")[

            "Speed Zones (m) [25.0, 50.0]"

        ]

        .mean()

        .reset_index()

    )

    speed_summary = speed_summary.sort_values(

        by="Speed Zones (m) [25.0, 50.0]",

        ascending=False

    )

    fig_speed = px.bar(

        speed_summary.head(10),

        x="Players",

        y="Speed Zones (m) [25.0, 50.0]",

        title="Top High Speed Players"

    )

    st.plotly_chart(
        fig_speed,
        use_container_width=True
    )

# =========================
# EXPORT
# =========================

st.header("Export Training Report")

csv = player_summary.to_csv(
    index=False
).encode("utf-8")

st.download_button(

    label="Download Training Load Report",

    data=csv,

    file_name="training_load_report.csv",

    mime="text/csv"

)
