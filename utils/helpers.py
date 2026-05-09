import streamlit as st


def fmt_pct(v: float) -> str:
    return f"{v * 100:.0f}%"


def hex_to_rgba(hex_color, alpha=0.15):
    hex_color = hex_color.lstrip("#")

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return f"rgba({r}, {g}, {b}, {alpha})"


def load_css():
    with open("assets/styles.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )


def section_title(title):
    st.markdown(
        f"<div class='sec-title'>{title}</div>",
        unsafe_allow_html=True
    )


def metric_card(title, value, subtitle=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def info_card(title, content):
    st.markdown(
        f"""
        <div class="diag-card">
            <h4>{title}</h4>
            <p>{content}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def action_item(text):
    st.markdown(
        f"""
        <div class="action-item">
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )