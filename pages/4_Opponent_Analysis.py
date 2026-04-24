import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Opponent Analysis")

UCLUJ_TEAM_ID = 60374

# =========================
# LOAD DATA
# =========================

# întâi încarci fișierul

player_df = pd.read_csv("player_stats.csv")

# apoi filtrezi U Cluj

ucluj_players = player_df[
    player_df["teamId"] == UCLUJ_TEAM_ID
].copy()

# apoi adversarii

opponent_players = player_df[
    player_df["teamId"] != UCLUJ_TEAM_ID
].copy(
st.write("Total players:", len(player_df))
st.write("Opponent players:", len(opponent_players))