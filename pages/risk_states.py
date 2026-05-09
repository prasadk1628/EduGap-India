import streamlit as st

from utils.helpers import (
    section_title,
    info_card,
)

from utils.config import (
    COL_LABELS,
)


def render_risk_states(df):

    section_title("🚨 High Risk States")

    high_risk_df = df[
        df["high_risk"] == True
    ]

    st.dataframe(
        high_risk_df[
            [
                "India/State/UT",
                "infra_score",
                "PTR"
            ]
        ].rename(columns=COL_LABELS),
        use_container_width=True
    )

    st.markdown("---")

    section_title("⚠️ Teacher Overload States")

    teacher_risk_df = df[
        df["teacher_risk"] == True
    ]

    st.dataframe(
        teacher_risk_df[
            [
                "India/State/UT",
                "PTR"
            ]
        ].rename(columns=COL_LABELS),
        use_container_width=True
    )

    st.markdown("---")

    section_title("📌 Risk Interpretation")

    info_card(
        "What makes a state high-risk?",
        """
        High-risk states usually have:
        
        • Poor infrastructure coverage  
        • High student-to-teacher load  
        • Limited essential facilities  
        """
    )