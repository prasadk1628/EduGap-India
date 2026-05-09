import pandas as pd
import streamlit as st

from utils.helpers import (
    section_title,
    metric_card,
    info_card,
    action_item,
    fmt_pct,
)

from utils.config import (
    FACILITY_COLS,
    FACILITY_NAMES,
    THRESHOLDS,
    ACC,
    W,
    D,
)

from utils.plots import (
    infra_breakdown_chart,
)


def render_state_deepdive(df):

    section_title("🔎 State Deep Dive")

    state = st.selectbox(
        "Select a State / UT",
        sorted(df["India/State/UT"].unique())
    )

    filtered_df = df[
        df["India/State/UT"] == state
    ]

    row = filtered_df.iloc[0]

    # KPIs
    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card(
            "Infrastructure Score",
            f"{row['infra_score']:.2f}"
        )

    with c2:
        metric_card(
            "Students / Teacher",
            f"{row['PTR']:.1f}"
        )

    with c3:
        metric_card(
            "Electricity Access",
            fmt_pct(row["electricity_ratio"])
        )

    st.markdown("---")

    # Facility Breakdown
    section_title("🏫 Facility Availability")

    breakdown_df = pd.DataFrame({
        "Metric": FACILITY_NAMES,
        "Value": [
            row[col]
            for col in FACILITY_COLS
        ]
    })

    fig = infra_breakdown_chart(
        breakdown_df
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("---")

    # Diagnosis
    section_title("🧠 Diagnosis & Interpretation")

    issues = []

    if row["infra_score"] < THRESHOLDS["infra_avg"]:
        issues.append(
            "Infrastructure quality is below the national comfort level."
        )

    if row["PTR"] > THRESHOLDS["ptr_danger"]:
        issues.append(
            "Teachers may be overloaded due to high classroom pressure."
        )

    if row["electricity_ratio"] < THRESHOLDS["facility_ok"]:
        issues.append(
            "Electricity access remains limited in several schools."
        )

    if row["water_ratio"] < THRESHOLDS["facility_ok"]:
        issues.append(
            "Water availability needs improvement."
        )

    if row["computer_ratio"] < THRESHOLDS["facility_ok"]:
        issues.append(
            "Computer infrastructure remains insufficient."
        )

    if not issues:
        issues.append(
            "Infrastructure and teacher balance are relatively stable."
        )

    for issue in issues:
        info_card(
            "Observation",
            issue
        )

    st.markdown("---")

    # Recommended Actions
    section_title("📌 Suggested Actions")

    if row["PTR"] > THRESHOLDS["ptr_danger"]:
        action_item(
            "Recruit additional teachers to reduce classroom overload."
        )

    if row["infra_score"] < THRESHOLDS["infra_avg"]:
        action_item(
            "Increase infrastructure funding for essential facilities."
        )

    if row["computer_ratio"] < THRESHOLDS["facility_ok"]:
        action_item(
            "Improve digital learning infrastructure in schools."
        )

    if row["water_ratio"] < THRESHOLDS["facility_ok"]:
        action_item(
            "Strengthen drinking water access across schools."
        )

    if row["infra_score"] >= THRESHOLDS["infra_good"]:
        action_item(
            "Maintain current infrastructure standards through regular monitoring."
        )