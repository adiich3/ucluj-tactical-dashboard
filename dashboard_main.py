import streamlit as st

st.set_page_config(
    page_title="U Cluj Tactical Dashboard",
    layout="wide"
)

st.title("U Cluj Tactical Analysis Dashboard")

st.markdown(
"""
Select a module from the sidebar.

Available Modules:

Match Analysis  
Player Analysis  
Team Overview  
Opponent Analysis  
Best Starting XI  

Each page provides detailed tactical insights based on match data.
"""
)