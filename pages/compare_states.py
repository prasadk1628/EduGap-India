import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils.helpers import (
    section_title,
    metric_card,
    fmt_pct,
    hex_to_rgba,
)

from utils.config import (
    FACILITY_COLS,
    FACILITY_NAMES,
    CMP_PAL,
)

from utils.plots import (
    compare_radar_chart,
)


def render_compare_states(df):

    section_title("⚖️ Compare States")

    selected_states = st.multiselect(
        "Select States",
        sorted(df["India/State/UT"].unique()),
        default=sorted(df["India/State/UT"].unique())[:2]
    )

    if len(selected_states) < 2:
        st.warning(
            "Please select at least two states."
        )
        return

    compare_df = df[
        df["India/State/UT"].isin(selected_states)
    ]

    st.markdown("---")

    # KPI Comparison
    section_title("📊 KPI Comparison")

    cols = st.columns(len(selected_states))

    for i, (_, row) in enumerate(compare_df.iterrows()):

        with cols[i]:

            metric_card(
                row["India/State/UT"],
                f"{row['infra_score']:.2f}",
                f"PTR: {row['PTR']:.1f}"
            )

    st.markdown("---")

    # Facility Comparison Table
    section_title("🏫 Facility Comparison")

    table_df = compare_df[
        ["India/State/UT"] + FACILITY_COLS
    ].copy()

    table_df.columns = [
        "State / UT"
    ] + FACILITY_NAMES

    st.dataframe(
        table_df,
        use_container_width=True
    )

    st.markdown("---")

    # Radar Chart
    section_title("🕸️ Radar Comparison")

    states_data = {}

    for _, row in compare_df.iterrows():

        states_data[
            row["India/State/UT"]
        ] = [
            row[col]
            for col in FACILITY_COLS
        ]

    fig = compare_radar_chart(
        states_data,
        FACILITY_NAMES
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("---")

    # Grouped Bar Comparison
    section_title("📈 Grouped Comparison")

    fig2 = go.Figure()

    for i, (_, row) in enumerate(compare_df.iterrows()):

        fig2.add_trace(
            go.Bar(
                name=row["India/State/UT"],
                x=FACILITY_NAMES,
                y=[
                    row[col]
                    for col in FACILITY_COLS
                ],
                marker_color=CMP_PAL[
                    i % len(CMP_PAL)
                ]
            )
        )

    fig2.update_layout(
        barmode="group",
        height=450,
        yaxis=dict(range=[0, 1]),
        xaxis_title="Facilities",
        yaxis_title="Availability Ratio"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.markdown("---")

    # Export
    section_title("⬇️ Export Comparison")

    csv = compare_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download Comparison CSV",
        csv,
        file_name="state_comparison.csv",
        mime="text/csv"
    )