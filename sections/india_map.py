import json
import streamlit as st
import plotly.express as px

from utils.helpers import (
    section_title,
)

from utils.config import (
    THRESHOLDS,
)


def render_india_map(df):

    section_title("🗺️ India Choropleth Map")

    # ---------------------------
    # METRIC SELECTION
    # ---------------------------
    metric_options = {
        "Infra Score": "infra_score",
        "Students / Teacher": "PTR",
        "Electricity": "electricity_ratio",
        "Toilets": "toilet_ratio",
        "Water": "water_ratio",
        "Computers": "computer_ratio",
    }

    selected_metric = st.selectbox(
        "Color map by",
        list(metric_options.keys())
    )

    metric_col = metric_options[selected_metric]

    # ---------------------------
    # LOAD GEOJSON
    # ---------------------------
    with open("assets/india_states.geojson") as f:
        india_geojson = json.load(f)

    # ---------------------------
    # STATE NAME FIX
    # ---------------------------
    state_mapping = {
        "Dadra & Nagar Haveli and Daman & Diu":
        "Dadra and Nagar Haveli and Daman and Diu"
    }

    df["state_mapped"] = df[
        "India/State/UT"
    ].replace(state_mapping)

    # ---------------------------
    # COLOR SCALE
    # ---------------------------
    if metric_col == "PTR":

        color_scale = "Reds"

    else:

        color_scale = "RdYlGn"

    # ---------------------------
    # MAP
    # ---------------------------
    fig = px.choropleth(
        df,
        geojson=india_geojson,
        featureidkey="properties.ST_NM",
        locations="state_mapped",
        color=metric_col,
        hover_name="India/State/UT",
        color_continuous_scale=color_scale,
        title=f"{selected_metric} Across India"
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig.update_layout(
        height=650,
        margin=dict(l=0, r=0, t=50, b=0)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ---------------------------
    # Analytical Summary
    # ---------------------------
    st.markdown("---")

    section_title("🧠 Analytical Summary")

    best_state = df.loc[
        df[metric_col].idxmax(),
        "India/State/UT"
    ]

    worst_state = df.loc[
        df[metric_col].idxmin(),
        "India/State/UT"
    ]

    avg_value = df[metric_col].mean()

    st.markdown(
        f"""
        ### 📊 Key Observations

        - **Best Performing State:** `{best_state}`
        - **Lowest Performing State:** `{worst_state}`
        - **National Average:** `{avg_value:.2f}`

        """
    )

    # Metric-specific interpretation
    if metric_col == "PTR":

        st.info(
            """
            Higher PTR values indicate heavier classroom pressure on teachers.
            Extremely high PTR may negatively affect learning quality and
            student attention.
            """
        )

    elif metric_col == "infra_score":

        st.info(
            """
            Infrastructure score represents the overall availability of
            essential school facilities across states.
            Higher scores indicate stronger infrastructure coverage.
            """
        )

    elif metric_col == "electricity_ratio":

        st.info(
            """
            Electricity availability is critical for digital learning,
            classroom operations, and basic school functionality.
            """
        )

    elif metric_col == "computer_ratio":

        st.info(
            """
            Computer facility access reflects digital infrastructure readiness
            and technology accessibility in schools.
            """
        )

    elif metric_col == "water_ratio":

        st.info(
            """
            Drinking water access is a fundamental infrastructure requirement
            for school safety and hygiene.
            """
        )

    elif metric_col == "toilet_ratio":

        st.info(
            """
            Functional sanitation facilities directly affect hygiene,
            attendance, and student well-being.
            """
        )

    # ---------------------------
    # INTERPRETATION
    # ---------------------------
    st.markdown("---")

    section_title("📌 Map Interpretation")

    if metric_col == "PTR":

        st.markdown(
            """
            - Darker red regions indicate higher student-teacher pressure  
            - High PTR values may affect teaching quality and classroom attention  
            """
        )

    else:

        st.markdown(
            """
            - Green regions indicate better infrastructure availability  
            - Red/orange regions indicate weaker facility coverage  
            """
        )