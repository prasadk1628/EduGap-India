import streamlit as st

from utils.config import *
from utils.helpers import *
from utils.data_loader import load_data

from sections.overview import render_overview
from sections.india_map import render_india_map
from sections.risk_states import render_risk_states
from sections.state_deepdive import render_state_deepdive
from sections.compare_states import render_compare_states


# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InfraViz",
    page_icon="📊",
    layout="wide"
)


# ─────────────────────────────────────────────────────────────────────────────
# LOAD CSS
# ─────────────────────────────────────────────────────────────────────────────
load_css()


# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
df = load_data()


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.title("📊 InfraViz")

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "India Map",
        "Risk States",
        "State Deep Dive",
        "Compare States"
    ]
)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE ROUTING
# ─────────────────────────────────────────────────────────────────────────────
if page == "Overview":
    render_overview(df)

elif page == "India Map":
    render_india_map(df)

elif page == "Risk States":
    render_risk_states(df)

elif page == "State Deep Dive":
    render_state_deepdive(df)

elif page == "Compare States":
    render_compare_states(df)