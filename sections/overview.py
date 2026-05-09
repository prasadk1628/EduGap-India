import streamlit as st
import pandas as pd

from utils.helpers import (
    section_title,
    metric_card,
)

from utils.config import (
    THRESHOLDS,
    FACILITY_COLS,
    FACILITY_NAMES,
)

from utils.plots import (
    infra_breakdown_chart,
)


def render_overview(df):

    # Hero Section
    st.markdown(
        """
        <div style="
            padding: 28px;
            border-radius: 18px;
            background: linear-gradient(135deg, #111827, #1F2937);
            border: 1px solid #2D333B;
            margin-bottom: 25px;
        ">
    
        <h1 style="
            color: white;
            margin-bottom: 10px;
            font-size: 42px;
        ">
            📊 InfraViz India
        </h1>
    
        <p style="
            color: #D1D5DB;
            font-size: 18px;
            line-height: 1.7;
            max-width: 900px;
        ">
            A national analytics dashboard for understanding the condition of
            government school infrastructure across Indian states using
            UDISE+ education data.
    
            The platform highlights infrastructure gaps, teacher overload,
            and facility availability to support data-driven educational insights.
        </p>
    
        </div>
        """,
        unsafe_allow_html=True
    )

    section_title("📊 National Overview")

    # KPIs
    c1, c2, c3 = st.columns(3)

    avg_infra = df["infra_score"].mean()
    avg_ptr = df["PTR"].mean()
    high_risk = df["high_risk"].sum()

    with c1:
        metric_card(
            "Avg Infra Score",
            f"{avg_infra:.2f}"
        )

    with c2:
        metric_card(
            "High Risk States",
            f"{high_risk}"
        )

    with c3:
        metric_card(
            "Avg Students / Teacher",
            f"{avg_ptr:.1f}"
        )

    st.markdown("---")

    # Facility Overview
    section_title("🏫 National Facility Availability")

    facility_vals = [
        df[col].mean()
        for col in FACILITY_COLS
    ]

    breakdown_df = pd.DataFrame({
        "Metric": FACILITY_NAMES,
        "Value": facility_vals
    })

    fig = infra_breakdown_chart(
        breakdown_df
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # Infra Distribution
    section_title("📈 Infrastructure Distribution")

    st.bar_chart(
        df.set_index("India/State/UT")[
            "infra_score"
        ]
    )

    st.markdown(
        """
        Higher infrastructure scores indicate
        better availability of essential
        school facilities.
        """
    )