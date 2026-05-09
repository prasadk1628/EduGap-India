"""
InfraViz — School Infrastructure Dashboard
Industry-grade Streamlit app · UDISE+ Government School Data

Run:  streamlit run app.py
Deps: pip install streamlit pandas plotly
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# ─────────────────────────────────────────────────────────────────────────────
# 0 · PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InfraViz · School Infrastructure",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# 1 · CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
THRESHOLDS = {
    "infra_good":   0.95,
    "infra_avg":    0.85,
    "ptr_danger":   30,
    "ptr_warning":  25,
    "facility_ok":  0.80,
}

FACILITY_COLS  = ["electricity_ratio", "toilet_ratio", "water_ratio", "computer_ratio"]
FACILITY_NAMES = ["Electricity", "Toilets", "Water", "Computers"]

COL_LABELS = {
    "India/State/UT":    "State / UT",
    "infra_score":       "Infra Score",
    "PTR":               "Students / Teacher",
    "electricity_ratio": "Electricity",
    "toilet_ratio":      "Toilets",
    "water_ratio":       "Water",
    "computer_ratio":    "Computers",
    "infra_tier":        "Tier",
    "high_risk":         "High Risk",
    "teacher_risk":      "Teacher Risk",
}

# Colour tokens
G   = "#22C97A"   # good / green
W   = "#F5A623"   # warn / amber
D   = "#F0454A"   # danger / red
ACC = "#4F8EF7"   # accent blue
TIER_CLR = {"Poor": D, "Average": W, "Good": G}
CMP_PAL  = [ACC, W, G]

# ─────────────────────────────────────────────────────────────────────────────
# 2 · CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* App background */
.stApp { background: #0B0D11; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #131519 !important;
    border-right: 1px solid #2A2D35;
}
section[data-testid="stSidebar"] * {
    font-family: 'DM Sans', sans-serif !important;
}

/* Main content */
.main .block-container { font-family: 'DM Sans', sans-serif; padding-top: 1.5rem; }

/* Metrics */
div[data-testid="metric-container"] {
    background: #131519 !important;
    border: 1px solid #2A2D35 !important;
    border-radius: 10px !important;
    padding: 14px 18px !important;
}
div[data-testid="stMetricValue"] > div {
    font-family: 'DM Mono', monospace !important;
    font-size: 24px !important;
    font-weight: 600 !important;
    color: #E8EAF0 !important;
}
div[data-testid="stMetricLabel"] > div {
    font-size: 11px !important;
    color: #656B78 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Tabs */
div[data-testid="stTabs"] [role="tablist"] {
    background: #1A1D23;
    border-radius: 8px;
    padding: 3px;
    border: 1px solid #2A2D35;
}
div[data-testid="stTabs"] button[role="tab"] {
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    color: #9EA3B0;
    padding: 6px 14px;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: #131519;
    color: #E8EAF0;
}

/* Divider */
hr { border-color: #2A2D35 !important; }

/* Expander */
details { background: #131519; border: 1px solid #2A2D35 !important; border-radius: 8px !important; }
summary { color: #9EA3B0 !important; font-size: 13px !important; }

/* Download button */
div[data-testid="stDownloadButton"] > button {
    background: #1A1D23;
    border: 1px solid #2A2D35;
    color: #4F8EF7;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
}

/* Hide Streamlit chrome */
#MainMenu { visibility: hidden; }
footer     { visibility: hidden; }

/* Custom classes */
.brand-box { padding: 0 0 16px; border-bottom: 1px solid #2A2D35; margin-bottom: 16px; }
.brand-box h2 { font-size: 18px; font-weight: 700; color: #E8EAF0; margin: 4px 0 2px; }
.brand-box p  { font-size: 11px; color: #656B78; margin: 0; }

.sec-title {
    font-size: 12px; font-weight: 600; color: #656B78;
    text-transform: uppercase; letter-spacing: 0.07em;
    padding-bottom: 8px; border-bottom: 1px solid #2A2D35; margin-bottom: 14px;
}

.pill { display:inline-block; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.pill-good   { background:rgba(34,201,122,0.12); color:#22C97A; }
.pill-warn   { background:rgba(245,166,35,0.12);  color:#F5A623; }
.pill-danger { background:rgba(240,69,74,0.12);   color:#F0454A; }
.pill-info   { background:rgba(79,142,247,0.12);  color:#4F8EF7; }

.diag-card   { padding:12px 16px; border-radius:8px; margin-bottom:8px; font-size:13px; border-left:3px solid; }
.diag-warn   { background:rgba(245,166,35,0.08);  border-color:#F5A623; color:#F5A623; }
.diag-danger { background:rgba(240,69,74,0.08);   border-color:#F0454A; color:#F0454A; }
.diag-good   { background:rgba(34,201,122,0.08);  border-color:#22C97A; color:#22C97A; }
.diag-body   { color:#9EA3B0; margin-top:4px; font-size:12px; }

.action-item {
    display:flex; align-items:flex-start; gap:10px;
    padding:10px 14px; background:#1A1D23;
    border-radius:8px; margin-bottom:6px; font-size:13px; color:#E8EAF0;
    border:1px solid #2A2D35;
}
.action-num {
    background:rgba(79,142,247,0.15); color:#4F8EF7; min-width:20px; height:20px;
    border-radius:50%; display:flex; align-items:center; justify-content:center;
    font-size:10px; font-weight:700; flex-shrink:0; margin-top:1px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 3 · DATA
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    try:
        df = pd.read_csv("education_analysis_ready.csv")
    except FileNotFoundError:
        rows = [
            ("Andhra Pradesh",       0.91, 22.1, 0.95, 0.88, 0.93, 0.72),
            ("Arunachal Pradesh",    0.71, 18.4, 0.72, 0.61, 0.68, 0.41),
            ("Assam",                0.78, 32.5, 0.81, 0.71, 0.75, 0.44),
            ("Bihar",                0.67, 38.2, 0.68, 0.59, 0.64, 0.31),
            ("Chhattisgarh",         0.79, 28.7, 0.82, 0.72, 0.77, 0.48),
            ("Goa",                  0.97, 14.2, 0.98, 0.97, 0.98, 0.92),
            ("Gujarat",              0.93, 21.3, 0.96, 0.90, 0.94, 0.78),
            ("Haryana",              0.89, 24.6, 0.92, 0.85, 0.90, 0.71),
            ("Himachal Pradesh",     0.96, 13.8, 0.98, 0.95, 0.97, 0.88),
            ("Jharkhand",            0.74, 31.4, 0.76, 0.65, 0.71, 0.40),
            ("Karnataka",            0.92, 19.7, 0.95, 0.88, 0.92, 0.76),
            ("Kerala",               0.98, 17.6, 0.99, 0.98, 0.99, 0.95),
            ("Madhya Pradesh",       0.76, 34.1, 0.79, 0.68, 0.74, 0.43),
            ("Maharashtra",          0.94, 20.8, 0.97, 0.91, 0.95, 0.82),
            ("Manipur",              0.69, 22.9, 0.71, 0.62, 0.67, 0.38),
            ("Meghalaya",            0.72, 20.1, 0.74, 0.64, 0.70, 0.42),
            ("Mizoram",              0.80, 16.3, 0.83, 0.74, 0.79, 0.55),
            ("Nagaland",             0.73, 17.8, 0.75, 0.66, 0.71, 0.44),
            ("Odisha",               0.81, 27.3, 0.84, 0.74, 0.79, 0.51),
            ("Punjab",               0.90, 23.1, 0.93, 0.87, 0.91, 0.74),
            ("Rajasthan",            0.80, 29.8, 0.83, 0.73, 0.78, 0.49),
            ("Sikkim",               0.88, 12.4, 0.90, 0.84, 0.87, 0.70),
            ("Tamil Nadu",           0.95, 18.9, 0.97, 0.93, 0.96, 0.85),
            ("Telangana",            0.90, 21.5, 0.93, 0.87, 0.91, 0.73),
            ("Tripura",              0.82, 24.0, 0.85, 0.76, 0.81, 0.54),
            ("Uttar Pradesh",        0.72, 35.8, 0.74, 0.64, 0.70, 0.38),
            ("Uttarakhand",          0.87, 26.2, 0.90, 0.83, 0.88, 0.67),
            ("West Bengal",          0.83, 30.1, 0.86, 0.77, 0.82, 0.55),
            ("Andaman & Nicobar",    0.91, 14.6, 0.93, 0.88, 0.92, 0.74),
            ("Chandigarh",           0.96, 15.2, 0.98, 0.95, 0.97, 0.90),
            ("Dadra & NH and D&D",   0.85, 20.4, 0.88, 0.81, 0.85, 0.65),
            ("Delhi",                0.88, 28.4, 0.91, 0.85, 0.89, 0.72),
            ("Jammu & Kashmir",      0.83, 24.8, 0.86, 0.78, 0.83, 0.57),
            ("Ladakh",               0.79, 17.2, 0.82, 0.72, 0.78, 0.50),
            ("Lakshadweep",          0.93, 11.8, 0.95, 0.91, 0.94, 0.80),
            ("Puducherry",           0.95, 16.4, 0.97, 0.93, 0.96, 0.86),
        ]
        cols = ["India/State/UT", "infra_score", "PTR"] + FACILITY_COLS
        df = pd.DataFrame(rows, columns=cols)
        st.sidebar.warning(
            "Using demo data. Place `education_analysis_ready.csv` alongside app.py to use real data.",
            icon="⚠️",
        )

    if "high_risk" not in df.columns:
        df["high_risk"] = (
            (df["infra_score"] < df["infra_score"].median()) &
            (df["PTR"] > THRESHOLDS["ptr_warning"])
        )
    if "teacher_risk" not in df.columns:
        df["teacher_risk"] = df["PTR"] > THRESHOLDS["ptr_danger"]

    q33 = df["infra_score"].quantile(0.33)
    q66 = df["infra_score"].quantile(0.66)
    df["infra_tier"] = df["infra_score"].apply(
        lambda s: "Poor" if s < q33 else ("Average" if s < q66 else "Good")
    )
    df["state_mapped"] = df["India/State/UT"].replace({
        "Dadra & Nagar Haveli and Daman & Diu":
        "Dadra and Nagar Haveli and Daman and Diu"
    })
    return df


df      = load_data()
AVG_I   = df["infra_score"].mean()
AVG_P   = df["PTR"].mean()
NAT_FAC = df[FACILITY_COLS].mean()

# ─────────────────────────────────────────────────────────────────────────────
# 4 · PLOTLY HELPERS
# ─────────────────────────────────────────────────────────────────────────────
_BASE = dict(
    font_family="DM Sans, sans-serif",
    font_color="#9EA3B0",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=14, r=14, t=36, b=14),
)

def _theme(fig, h=400, legend=False):
    fig.update_layout(
        **_BASE, height=h, showlegend=legend,
        xaxis=dict(gridcolor="#1F222A", zerolinecolor="#1F222A", tickfont=dict(size=11)),
        yaxis=dict(gridcolor="#1F222A", zerolinecolor="#1F222A", tickfont=dict(size=11)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    )
    return fig


def _legend_top(fig):
    fig.update_layout(
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)", font=dict(size=11),
        )
    )
    return fig


def fmt_pct(v: float) -> str:
    return f"{v * 100:.0f}%"

def hex_to_rgba(hex_color, alpha=0.15):
    hex_color = hex_color.lstrip("#")

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return f"rgba({r}, {g}, {b}, {alpha})"

# ─────────────────────────────────────────────────────────────────────────────
# 5 · SIDEBAR
# key="page_radio" makes st.session_state track navigation reliably
# ─────────────────────────────────────────────────────────────────────────────
PAGES = [
    "📊 Overview",
    "🚨 Risk States",
    "🗺️ India Map",
    "🔍 State Deep-Dive",
    "⚖️ Compare States",
]

with st.sidebar:
    st.markdown("""
    <div class="brand-box">
      <div style="font-size:26px;line-height:1.3">🏫</div>
      <h2>InfraViz</h2>
      <p>UDISE+ · Government Schools</p>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        options=PAGES,
        key="page_radio",
        label_visibility="collapsed",
    )

    st.divider()

    n_risk = int(df["high_risk"].sum())
    c1, c2 = st.columns(2)
    c1.metric("States",    len(df))
    c2.metric("High-Risk", n_risk)
    st.caption(f"Avg Infra Score: **{AVG_I:.4f}**")
    st.caption(f"Avg PTR: **{AVG_P:.1f}** students / teacher")

# ─────────────────────────────────────────────────────────────────────────────
# 6 · PAGE: OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
if page == "📊 Overview":

    st.markdown('<p class="sec-title">National Overview · All States & UTs</p>',
                unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("States Assessed", len(df))
    k2.metric("Avg Infra Score", f"{AVG_I:.4f}",
              delta=f"{AVG_I - THRESHOLDS['infra_good']:+.4f} vs target",
              delta_color="inverse")
    k3.metric("High-Risk States", n_risk,
              delta="infra + overload", delta_color="off")
    k4.metric("Avg Students / Teacher", f"{AVG_P:.1f}",
              delta=f"{AVG_P - THRESHOLDS['ptr_warning']:+.1f} vs ideal",
              delta_color="inverse")

    st.divider()

    col_sc, col_do = st.columns([3, 2])

    with col_sc:
        st.markdown('<p class="sec-title">Infra Score vs. Teacher Load</p>',
                    unsafe_allow_html=True)
        fig = px.scatter(
            df, x="infra_score", y="PTR",
            color="infra_tier", color_discrete_map=TIER_CLR,
            hover_name="India/State/UT",
            hover_data={"infra_score": ":.4f", "PTR": ":.1f", "infra_tier": False},
            text="India/State/UT",
            labels={"infra_score": "Infra Score", "PTR": "Students / Teacher"},
        )
        fig.update_traces(
            textposition="top center",
            textfont=dict(size=8, color="#656B78"),
            marker=dict(size=9, opacity=0.85, line=dict(width=1, color="#0B0D11")),
        )
        fig.add_hline(y=THRESHOLDS["ptr_warning"], line_dash="dot",
                      line_color=W, line_width=1,
                      annotation_text=f"PTR warning ({THRESHOLDS['ptr_warning']})",
                      annotation_position="bottom right",
                      annotation_font=dict(size=10, color=W))
        fig.add_vline(x=THRESHOLDS["infra_avg"], line_dash="dot",
                      line_color=ACC, line_width=1,
                      annotation_text=f"Infra threshold ({THRESHOLDS['infra_avg']})",
                      annotation_position="top left",
                      annotation_font=dict(size=10, color=ACC))
        _theme(fig, h=380, legend=True)
        _legend_top(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col_do:
        st.markdown('<p class="sec-title">Tier Distribution</p>', unsafe_allow_html=True)
        tc = df["infra_tier"].value_counts().reindex(["Good","Average","Poor"]).fillna(0)
        fig2 = go.Figure(go.Pie(
            labels=tc.index, values=tc.values, hole=0.62,
            marker=dict(colors=[G, W, D], line=dict(color="#0B0D11", width=3)),
            hovertemplate="<b>%{label}</b><br>%{value} states · %{percent}<extra></extra>",
        ))
        fig2.add_annotation(
            text=f"<b>{len(df)}</b><br>States",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=15, color="#E8EAF0"),
        )
        _theme(fig2, h=380, legend=True)
        fig2.update_layout(legend=dict(orientation="v", x=0.72, y=0.5, font=dict(size=12)))
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    col_t, col_b = st.columns(2)

    with col_t:
        st.markdown('<p class="sec-title">🏆 Top 10 States — Infra Score</p>',
                    unsafe_allow_html=True)
        top10 = df.nlargest(10, "infra_score").sort_values("infra_score")
        fig3 = px.bar(
            top10, x="infra_score", y="India/State/UT", orientation="h",
            color="infra_score",
            color_continuous_scale=["#085041", "#1D9E75", "#9FE1CB"],
            range_color=[top10["infra_score"].min(), 1.0],
            text=top10["infra_score"].round(4),
            labels={"infra_score": "Score", "India/State/UT": ""},
        )
        fig3.update_traces(textposition="outside", textfont=dict(size=11, color="#E8EAF0"))
        _theme(fig3, h=360)
        fig3.update_layout(
            coloraxis_showscale=False,
            xaxis=dict(range=[top10["infra_score"].min() - 0.01, 1.04]),
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        st.markdown('<p class="sec-title">⚠️ Bottom 10 States — Infra Score</p>',
                    unsafe_allow_html=True)
        bot10 = df.nsmallest(10, "infra_score").sort_values("infra_score", ascending=False)
        fig4 = px.bar(
            bot10, x="infra_score", y="India/State/UT", orientation="h",
            color="infra_score",
            color_continuous_scale=["#501313", "#E24B4A", "#F7C1C1"],
            range_color=[0.5, bot10["infra_score"].max()],
            text=bot10["infra_score"].round(4),
            labels={"infra_score": "Score", "India/State/UT": ""},
        )
        fig4.update_traces(textposition="outside", textfont=dict(size=11, color="#E8EAF0"))
        _theme(fig4, h=360)
        fig4.update_layout(
            coloraxis_showscale=False,
            xaxis=dict(range=[0.60, bot10["infra_score"].max() + 0.04]),
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    st.markdown('<p class="sec-title">National Facility Coverage Heatmap</p>',
                unsafe_allow_html=True)
    hdf = df[["India/State/UT"] + FACILITY_COLS].set_index("India/State/UT").copy()
    hdf.columns = FACILITY_NAMES
    fig5 = go.Figure(go.Heatmap(
        z=hdf.values,
        x=hdf.columns.tolist(),
        y=hdf.index.tolist(),
        colorscale=[
            [0.0, "#501313"], [0.4, "#E24B4A"],
            [0.6, "#F5A623"], [0.8, "#1D9E75"], [1.0, "#9FE1CB"]
        ],
        zmin=0, zmax=1,
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1%}<extra></extra>",
        showscale=True,
        colorbar=dict(
            tickformat=".0%",
            tickfont=dict(size=10, color="#9EA3B0"),
            outlinewidth=0,
        ),
    ))
    _theme(fig5, h=max(380, len(df) * 14))
    fig5.update_layout(
        xaxis=dict(side="top", tickfont=dict(size=13, color="#E8EAF0")),
        yaxis=dict(tickfont=dict(size=10)),
        margin=dict(l=150, r=80, t=60, b=10),
    )
    st.plotly_chart(fig5, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# 7 · PAGE: RISK STATES
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🚨 Risk States":

    st.markdown('<p class="sec-title">Risk State Analysis</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "🔴 High Risk (Both Flags)",
        "🏚️ Poor Infrastructure",
        "👩‍🏫 Teacher Overload",
    ])

    with tab1:
        high_df = df[df["high_risk"]].sort_values("infra_score").copy()
        st.caption(
            f"Infrastructure below national median **and** PTR > {THRESHOLDS['ptr_warning']} — "
            f"**{len(high_df)} states** flagged."
        )

        col_a, col_b = st.columns([1.6, 1])

        with col_a:
            fig = px.scatter(
                high_df, x="infra_score", y="PTR",
                color="PTR",
                color_continuous_scale=["#F7C1C1", "#E24B4A", "#501313"],
                hover_name="India/State/UT",
                text="India/State/UT",
                size=[16] * len(high_df),
                labels={"infra_score": "Infra Score", "PTR": "Students / Teacher"},
            )
            fig.update_traces(
                textposition="top center",
                textfont=dict(size=9, color="#9EA3B0"),
                marker=dict(opacity=0.88, line=dict(width=1, color="#0B0D11")),
            )
            _theme(fig, h=340)
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            high_df["severity"] = (1 - high_df["infra_score"]) * high_df["PTR"]
            sdf = high_df.sort_values("severity", ascending=True)
            fig2 = px.bar(
                sdf, x="severity", y="India/State/UT", orientation="h",
                color="severity",
                color_continuous_scale=["#F7C1C1", "#E24B4A", "#501313"],
                labels={"severity": "Combined Risk Score", "India/State/UT": ""},
                text=sdf["severity"].round(2),
            )
            fig2.update_traces(textposition="outside", textfont=dict(size=10, color="#E8EAF0"))
            _theme(fig2, h=340)
            fig2.update_layout(
                coloraxis_showscale=False,
                title=dict(text="Severity Score (higher = worse)",
                           font=dict(size=11, color="#656B78"), x=0),
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<p class="sec-title">Flagged States Detail</p>', unsafe_allow_html=True)
        tbl = high_df[["India/State/UT", "infra_score", "PTR", "infra_tier"] + FACILITY_COLS].copy()
        tbl = tbl.rename(columns=COL_LABELS)
        tbl["Infra Score"] = tbl["Infra Score"].round(4)
        tbl["Students / Teacher"] = tbl["Students / Teacher"].round(1)
        for n in FACILITY_NAMES:
            if n in tbl.columns:
                tbl[n] = tbl[n].apply(fmt_pct)
        st.dataframe(tbl.reset_index(drop=True), use_container_width=True)

    with tab2:
        poor = df[df["infra_tier"] == "Poor"].sort_values("infra_score")
        st.caption(f"**{len(poor)} states** in the bottom tercile of infrastructure score.")

        fig = px.bar(
            poor, x="infra_score", y="India/State/UT", orientation="h",
            color="infra_score",
            color_continuous_scale=["#501313", "#E24B4A", "#F7C1C1"],
            text=poor["infra_score"].round(4),
            labels={"infra_score": "Infra Score", "India/State/UT": ""},
        )
        fig.update_traces(textposition="outside", textfont=dict(size=11, color="#E8EAF0"))
        fig.add_vline(
            x=df["infra_score"].median(), line_dash="dot", line_color=ACC, line_width=1,
            annotation_text="National median", annotation_position="top left",
            annotation_font=dict(size=10, color=ACC),
        )
        _theme(fig, h=max(300, len(poor) * 40))
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

        tbl2 = poor[["India/State/UT", "infra_score"] + FACILITY_COLS].rename(columns=COL_LABELS)
        tbl2["Infra Score"] = tbl2["Infra Score"].round(4)
        for n in FACILITY_NAMES:
            if n in tbl2.columns:
                tbl2[n] = tbl2[n].apply(fmt_pct)
        st.dataframe(tbl2.reset_index(drop=True), use_container_width=True)

    with tab3:
        teach = df[df["teacher_risk"]].sort_values("PTR", ascending=False)
        st.caption(
            f"**{len(teach)} states** with PTR above the danger threshold "
            f"of **{THRESHOLDS['ptr_danger']}**."
        )

        fig = px.bar(
            teach.sort_values("PTR"), x="PTR", y="India/State/UT", orientation="h",
            color="PTR",
            color_continuous_scale=["#FAEEDA", "#EF9F27", "#633806"],
            text=teach.sort_values("PTR")["PTR"].round(1),
            labels={"PTR": "Students / Teacher", "India/State/UT": ""},
        )
        fig.update_traces(textposition="outside", textfont=dict(size=11, color="#E8EAF0"))
        fig.add_vline(
            x=THRESHOLDS["ptr_danger"], line_dash="dot", line_color=D, line_width=1,
            annotation_text=f"Danger ({THRESHOLDS['ptr_danger']})",
            annotation_position="top left",
            annotation_font=dict(size=10, color=D),
        )
        _theme(fig, h=max(280, len(teach) * 46))
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# 8 · PAGE: INDIA MAP
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🗺️ India Map":

    st.markdown('<p class="sec-title">India Choropleth Map</p>', unsafe_allow_html=True)

    map_metric = st.selectbox(
        "Color map by",
        options=["infra_score", "PTR"] + FACILITY_COLS,
        format_func=lambda c: COL_LABELS.get(c, c),
        key="map_metric",
    )

    try:
        with open("india_states.geojson") as f:
            india_geo = json.load(f)

        scale = "RdYlGn" if map_metric != "PTR" else "YlOrRd_r"
        fig = px.choropleth(
            df,
            geojson=india_geo,
            featureidkey="properties.ST_NM",
            locations="state_mapped",
            color=map_metric,
            hover_name="India/State/UT",
            hover_data={"infra_score": ":.4f", "PTR": ":.1f", "state_mapped": False},
            color_continuous_scale=scale,
            labels={map_metric: COL_LABELS.get(map_metric, map_metric)},
            title=f"State-wise · {COL_LABELS.get(map_metric, map_metric)}",
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(
            **_BASE, height=640,
            coloraxis_colorbar=dict(
                tickfont=dict(size=10, color="#9EA3B0"), outlinewidth=0,
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

    except FileNotFoundError:
        st.info(
            "`india_states.geojson` not found — showing ranked bar chart. "
            "Place the GeoJSON file alongside `app.py` to enable the choropleth.",
            icon="🗺️",
        )
        sdf = df.sort_values(map_metric, ascending=True)
        is_inv = map_metric == "PTR"
        fb_scale = (
            [[0, "#22C97A"], [0.5, "#F5A623"], [1, "#501313"]] if is_inv else
            [[0, "#501313"], [0.5, "#F5A623"], [1, "#22C97A"]]
        )
        fig = px.bar(
            sdf, x=map_metric, y="India/State/UT", orientation="h",
            color=map_metric,
            color_continuous_scale=fb_scale,
            text=sdf[map_metric].round(3),
            labels={map_metric: COL_LABELS.get(map_metric, map_metric), "India/State/UT": ""},
        )
        fig.update_traces(textposition="outside", textfont=dict(size=10, color="#E8EAF0"))
        _theme(fig, h=max(520, len(df) * 16))
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# 9 · PAGE: STATE DEEP-DIVE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔍 State Deep-Dive":

    st.markdown('<p class="sec-title">State Deep-Dive</p>', unsafe_allow_html=True)

    col_sel, col_badge = st.columns([3, 2])
    with col_sel:
        state = st.selectbox(
            "Select a state",
            sorted(df["India/State/UT"].unique()),
            key="dd_state",
        )
    row = df[df["India/State/UT"] == state].iloc[0]

    with col_badge:
        st.markdown("<br>", unsafe_allow_html=True)
        if row["high_risk"]:
            st.markdown(
                '<span class="pill pill-danger" style="font-size:13px">⚠️ High-Risk State</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="pill pill-good" style="font-size:13px">✅ No Critical Flags</span>',
                unsafe_allow_html=True,
            )

    st.markdown("")

    k1, k2, k3, k4 = st.columns(4)
    di = row["infra_score"] - AVG_I
    dp = row["PTR"] - AVG_P
    k1.metric("Infra Score", f"{row['infra_score']:.4f}",
              delta=f"{di:+.4f} vs national",
              delta_color="normal" if di >= 0 else "inverse")
    k2.metric("Students / Teacher", f"{row['PTR']:.1f}",
              delta=f"{dp:+.1f} vs national",
              delta_color="inverse")
    k3.metric("Infra Tier", row["infra_tier"])
    k4.metric("Teacher Overload", "Yes ⚠️" if row["teacher_risk"] else "No ✅")

    st.divider()

    col_fac, col_rad = st.columns(2)

    with col_fac:
        st.markdown('<p class="sec-title">Facility Availability</p>', unsafe_allow_html=True)
        fvals = [row[c] for c in FACILITY_COLS]
        fstat = ["Below threshold" if v < THRESHOLDS["facility_ok"] else "OK" for v in fvals]
        fdf   = pd.DataFrame({"Facility": FACILITY_NAMES, "Value": fvals, "Status": fstat})

        fig = px.bar(
            fdf, x="Facility", y="Value",
            color="Status",
            color_discrete_map={"OK": G, "Below threshold": D},
            text=fdf["Value"].map(fmt_pct),
            range_y=[0, 1.12],
            labels={"Value": "Availability Ratio"},
        )
        fig.add_hline(
            y=THRESHOLDS["facility_ok"], line_dash="dot", line_color=W, line_width=1.5,
            annotation_text=f"Threshold ({THRESHOLDS['facility_ok']:.0%})",
            annotation_position="top right",
            annotation_font=dict(size=10, color=W),
        )
        fig.update_traces(textposition="outside", textfont=dict(size=12, color="#E8EAF0"))
        _theme(fig, h=340, legend=True)
        _legend_top(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col_rad:
        st.markdown(
            f'<p class="sec-title">{state} vs. National Average</p>',
            unsafe_allow_html=True,
        )
        svals = [row[c] for c in FACILITY_COLS]
        nvals = NAT_FAC[FACILITY_COLS].tolist()

        fig2 = go.Figure()
        fig2.add_trace(go.Scatterpolar(
            r=svals + [svals[0]], theta=FACILITY_NAMES + [FACILITY_NAMES[0]],
            fill="toself", name=state,
            line=dict(color=ACC, width=2), fillcolor=hex_to_rgba(ACC, 0.15),
        ))
        fig2.add_trace(go.Scatterpolar(
            r=nvals + [nvals[0]], theta=FACILITY_NAMES + [FACILITY_NAMES[0]],
            fill="toself", name="National Avg",
            line=dict(color="#656B78", width=1.5, dash="dot"),
            fillcolor="rgba(101,101,120,0.12)",
        ))
        fig2.update_layout(
            polar=dict(
                bgcolor="#131519",
                radialaxis=dict(
                    range=[0, 1], tickformat=".0%",
                    tickfont=dict(size=9, color="#656B78"),
                    gridcolor="#1F222A", linecolor="#1F222A",
                ),
                angularaxis=dict(
                    tickfont=dict(size=11, color="#E8EAF0"),
                    gridcolor="#1F222A", linecolor="#1F222A",
                ),
            ),
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.20, xanchor="center", x=0.5,
                bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#9EA3B0"),
            ),
            **_BASE,
            height=340,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    st.markdown('<p class="sec-title">📌 Diagnosis & Recommended Actions</p>',
                unsafe_allow_html=True)

    issues, actions = [], []
    if row["PTR"] > THRESHOLDS["ptr_danger"]:
        issues.append(("danger", "Critical teacher overload",
                        f"PTR of {row['PTR']:.1f} far exceeds the safe limit of {THRESHOLDS['ptr_danger']}."))
        actions.append("Recruit additional teachers urgently; consider split-shift scheduling.")
    elif row["PTR"] > THRESHOLDS["ptr_warning"]:
        issues.append(("warn", "Elevated teacher load",
                        f"PTR {row['PTR']:.1f} is above the warning threshold of {THRESHOLDS['ptr_warning']}."))
        actions.append("Plan incremental teacher hiring in the next budget cycle.")

    for c, name in zip(FACILITY_COLS, FACILITY_NAMES):
        if row[c] < THRESHOLDS["facility_ok"]:
            issues.append(("warn", f"{name} access low",
                            f"Only {row[c]:.0%} of schools covered — below the {THRESHOLDS['facility_ok']:.0%} threshold."))
            actions.append(f"Prioritise {name.lower()} infrastructure grants for {state}.")

    if not issues:
        st.markdown(
            '<div class="diag-card diag-good">✅ No critical issues detected.'
            '<div class="diag-body">Maintain current standards and monitor annually.</div></div>',
            unsafe_allow_html=True,
        )
    else:
        for lvl, title, body in issues:
            st.markdown(
                f'<div class="diag-card diag-{lvl}"><strong>{title}</strong>'
                f'<div class="diag-body">{body}</div></div>',
                unsafe_allow_html=True,
            )
        if actions:
            st.markdown("**Recommended actions:**")
            for i, a in enumerate(actions, 1):
                st.markdown(
                    f'<div class="action-item"><div class="action-num">{i}</div><div>{a}</div></div>',
                    unsafe_allow_html=True,
                )

    st.markdown("")
    with st.expander("📄 Raw data for this state"):
        st.dataframe(df[df["India/State/UT"] == state], use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# 10 · PAGE: COMPARE STATES
# ─────────────────────────────────────────────────────────────────────────────
elif page == "⚖️ Compare States":

    st.markdown('<p class="sec-title">State Comparison</p>', unsafe_allow_html=True)

    selected = st.multiselect(
        "Choose 2–3 states to compare",
        options=sorted(df["India/State/UT"].unique()),
        default=sorted(df["India/State/UT"].unique())[:2],
        max_selections=3,
        key="cmp_select",
    )

    if len(selected) < 2:
        st.info("Select at least 2 states to compare.", icon="ℹ️")
        st.stop()

    cmp = df[df["India/State/UT"].isin(selected)].reset_index(drop=True)
    pal = CMP_PAL[: len(selected)]

    st.divider()

    st.markdown('<p class="sec-title">Key Metrics</p>', unsafe_allow_html=True)
    disp = ["India/State/UT", "infra_score", "PTR", "infra_tier", "high_risk"]
    tbl  = cmp[disp].rename(columns=COL_LABELS)
    tbl["Infra Score"]          = tbl["Infra Score"].round(4)
    tbl["Students / Teacher"]   = tbl["Students / Teacher"].round(1)
    st.dataframe(tbl.set_index("State / UT"), use_container_width=True)

    st.divider()

    col_bar, col_rad = st.columns(2)

    with col_bar:
        st.markdown('<p class="sec-title">Facility Comparison</p>', unsafe_allow_html=True)
        melt = cmp.melt(
            id_vars="India/State/UT", value_vars=FACILITY_COLS,
            var_name="Facility", value_name="Ratio",
        )
        melt["Facility"] = melt["Facility"].map(dict(zip(FACILITY_COLS, FACILITY_NAMES)))
        melt["Pct"] = melt["Ratio"].apply(fmt_pct)

        fig = px.bar(
            melt, x="Facility", y="Ratio", color="India/State/UT",
            barmode="group", color_discrete_sequence=pal,
            text="Pct", range_y=[0, 1.14],
            labels={"Ratio": "Availability", "India/State/UT": "State"},
        )
        fig.add_hline(y=THRESHOLDS["facility_ok"], line_dash="dot",
                      line_color=W, line_width=1,
                      annotation_text="Threshold", annotation_position="top left",
                      annotation_font=dict(size=10, color=W))
        fig.update_traces(textposition="outside", textfont=dict(size=10, color="#E8EAF0"))
        _theme(fig, h=360, legend=True)
        _legend_top(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col_rad:
        st.markdown('<p class="sec-title">Radar Overview</p>', unsafe_allow_html=True)
        fig2 = go.Figure()
        for i, (_, r) in enumerate(cmp.iterrows()):
            vals = [r[c] for c in FACILITY_COLS]
            fig2.add_trace(go.Scatterpolar(
                r=vals + [vals[0]], theta=FACILITY_NAMES + [FACILITY_NAMES[0]],
                fill="toself", name=r["India/State/UT"],
                line=dict(color=pal[i], width=2), fillcolor=hex_to_rgba(pal[i], 0.15),
            ))
        fig2.update_layout(
            polar=dict(
                bgcolor="#131519",
                radialaxis=dict(
                    range=[0, 1], tickformat=".0%",
                    tickfont=dict(size=9, color="#656B78"),
                    gridcolor="#1F222A", linecolor="#1F222A",
                ),
                angularaxis=dict(
                    tickfont=dict(size=11, color="#E8EAF0"),
                    gridcolor="#1F222A", linecolor="#1F222A",
                ),
            ),
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.20, xanchor="center", x=0.5,
                bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#9EA3B0"),
            ),
            **_BASE,
            height=360,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    st.markdown('<p class="sec-title">Infra Score & PTR Side-by-Side</p>',
                unsafe_allow_html=True)
    col_is, col_pt = st.columns(2)

    with col_is:
        fig3 = go.Figure([
            go.Bar(
                name=r["India/State/UT"], x=[r["India/State/UT"]], y=[r["infra_score"]],
                marker_color=pal[i], text=f"{r['infra_score']:.4f}", textposition="outside",
            )
            for i, (_, r) in enumerate(cmp.iterrows())
        ])
        fig3.add_hline(y=THRESHOLDS["infra_good"], line_dash="dot",
                       line_color=ACC, line_width=1,
                       annotation_text="Target (0.95)", annotation_position="top right",
                       annotation_font=dict(size=10, color=ACC))
        _theme(fig3, h=280, legend=False)
        fig3.update_traces(textfont=dict(size=12, color="#E8EAF0"))
        fig3.update_layout(
            title=dict(text="Infra Score", font=dict(size=12, color="#656B78"), x=0),
            yaxis=dict(range=[0, 1.08]),
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_pt:
        fig4 = go.Figure([
            go.Bar(
                name=r["India/State/UT"], x=[r["India/State/UT"]], y=[r["PTR"]],
                marker_color=pal[i], text=f"{r['PTR']:.1f}", textposition="outside",
            )
            for i, (_, r) in enumerate(cmp.iterrows())
        ])
        fig4.add_hline(y=THRESHOLDS["ptr_warning"], line_dash="dot",
                       line_color=W, line_width=1,
                       annotation_text="Warning (25)", annotation_position="top right",
                       annotation_font=dict(size=10, color=W))
        fig4.add_hline(y=THRESHOLDS["ptr_danger"], line_dash="dot",
                       line_color=D, line_width=1,
                       annotation_text="Danger (30)", annotation_position="bottom right",
                       annotation_font=dict(size=10, color=D))
        _theme(fig4, h=280, legend=False)
        fig4.update_traces(textfont=dict(size=12, color="#E8EAF0"))
        fig4.update_layout(
            title=dict(text="Students / Teacher (PTR)",
                       font=dict(size=12, color="#656B78"), x=0),
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    dl_cols = disp + FACILITY_COLS
    csv = (
        cmp[dl_cols].rename(columns=COL_LABELS)
        .to_csv(index=False)
        .encode("utf-8")
    )
    st.download_button(
        "⬇️ Download comparison as CSV",
        data=csv, file_name="state_comparison.csv", mime="text/csv",
    )