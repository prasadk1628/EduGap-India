import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    df = pd.read_csv(
        "data/processed/education_analysis_ready.csv"
    )

    return df
