import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# ============================================================
# SECTION 0 — PAGE CONFIG (must be first Streamlit call)
# ============================================================
st.set_page_config(
    page_title="School Infrastructure Dashboard",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# SECTION 1 — GLOBAL THRESHOLDS (tune here, nowhere else)
# ============================================================
THRESHOLDS = {
    "infra_good":      0.95,   # infra_score above this → good
    "infra_avg":       0.85,   # between avg and good → average
    "ptr_danger":      30,     # students/teacher → overloaded
    "ptr_warning":     25,     # students/teacher → moderate
    "facility_ok":     0.80,   # any facility ratio below this → flagged
}

COLUMN_LABELS = {
    "India/State/UT":    "State / UT",
    "infra_score":       "Infra Score",
    "PTR":               "Students / Teacher",
    "electricity_ratio": "Electricity",
    "toilet_ratio":      "Toilets",
    "water_ratio":       "Water",
    "computer_ratio":    "Computers",
}

# ============================================================
# SECTION 2 — DATA LOADING & DERIVED COLUMNS
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv("education_analysis_ready.csv")

    # --- Derive risk flags if they're missing from the CSV ---
    if "high_risk" not in df.columns:
        df["high_risk"] = (
            (df["infra_score"] < df["infra_score"].median()) &
            (df["PTR"] > THRESHOLDS["ptr_warning"])
        )

    if "teacher_risk" not in df.columns:
        df["teacher_risk"] = df["PTR"] > THRESHOLDS["ptr_danger"]

    # --- Infra tier labels (derived from quantiles, not hardcoded) ---
    q33 = df["infra_score"].quantile(0.33)
    q66 = df["infra_score"].quantile(0.66)

    def _tier(score):
        if score < q33:
            return "Poor"
        elif score < q66:
            return "Average"
        return "Good"

    df["infra_tier"] = df["infra_score"].apply(_tier)

    # --- Name mapping for choropleth join ---
    df["state_mapped"] = df["India/State/UT"].replace({
        "Dadra & Nagar Haveli and Daman & Diu":
        "Dadra and Nagar Haveli and Daman and Diu"
    })

    return df


df = load_data()

FACILITY_COLS = ["electricity_ratio", "toilet_ratio", "water_ratio", "computer_ratio"]
FACILITY_NAMES = ["Electricity", "Toilets", "Water", "Computers"]

# ============================================================
# SECTION 3 — SHARED PLOTLY THEME
# ============================================================
PLOTLY_LAYOUT = dict(
    font_family="monospace",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=40, b=20),
    colorway=["#1D9E75", "#EF9F27", "#E24B4A", "#378ADD", "#7F77DD"],
)

TIER_COLORS = {"Poor": "#E24B4A", "Average": "#EF9F27", "Good": "#1D9E75"}

# ============================================================
# SECTION 4 — SIDEBAR NAVIGATION
# ============================================================
with st.sidebar:
    st.markdown("### 🏫 Infra Dashboard")
    st.caption("UDISE+ · Government Schools")
    st.divider()

    page = st.radio(
        "Navigate",
        options=[
            "📊 Overview",
            "🚨 Risk States",
            "🗺️ India Map",
            "🔍 State Deep-Dive",
            "⚖️ Compare States",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption(f"States assessed: **{len(df)}**")
    st.caption(f"High-risk states: **{df['high_risk'].sum()}**")

# ============================================================
# SECTION 5 — PAGE: OVERVIEW
# ============================================================
if page == "📊 Overview":
    st.title("📊 Overview")

    # --- 5.1 National KPI cards ---
    avg_infra  = df["infra_score"].mean()
    avg_ptr    = df["PTR"].mean()
    n_highrisk = int(df["high_risk"].sum())
    n_states   = len(df)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("States Assessed",     n_states)
    k2.metric("Avg Infra Score",      f"{avg_infra:.2f}",
              delta=f"{avg_infra - THRESHOLDS['infra_good']:.2f} vs target",
              delta_color="inverse")
    k3.metric("High-Risk States",     n_highrisk,
              delta="infra + overload", delta_color="off")
    k4.metric("Avg Students / Teacher", f"{avg_ptr:.1f}",
              delta=f"{avg_ptr - THRESHOLDS['ptr_warning']:.1f} vs ideal",
              delta_color="inverse")

    st.divider()

    # --- 5.2 Scatter: Infra Score vs PTR (the "quadrant" view) ---
    st.subheader("Infrastructure Score vs. Teacher Load")
    st.caption(
        "Each dot is a state. The dashed lines mark risk thresholds. "
        "Bottom-left quadrant = worst of both worlds."
    )

    scatter_fig = px.scatter(
        df,
        x="infra_score",
        y="PTR",
        color="infra_tier",
        color_discrete_map=TIER_COLORS,
        hover_name="India/State/UT",
        hover_data={"infra_score": ":.2f", "PTR": ":.1f", "infra_tier": False},
        text="India/State/UT",
        labels={"infra_score": "Infra Score", "PTR": "Students / Teacher"},
    )
    scatter_fig.update_traces(
        textposition="top center",
        textfont_size=9,
        marker_size=9,
    )
    scatter_fig.add_hline(
        y=THRESHOLDS["ptr_warning"],
        line_dash="dash", line_color="#888",
        annotation_text=f"PTR threshold ({THRESHOLDS['ptr_warning']})",
        annotation_position="bottom right",
    )
    scatter_fig.add_vline(
        x=THRESHOLDS["infra_avg"],
        line_dash="dash", line_color="#888",
        annotation_text=f"Infra threshold ({THRESHOLDS['infra_avg']})",
        annotation_position="top left",
    )
    scatter_fig.update_layout(**PLOTLY_LAYOUT, height=480)
    st.plotly_chart(scatter_fig, use_container_width=True)

    st.divider()

    # --- 5.3 Top 10 vs Bottom 10 horizontal bars ---
    col_top, col_bot = st.columns(2)

    with col_top:
        st.subheader("🏆 Top 10 States")
        top10 = df.nlargest(10, "infra_score").sort_values("infra_score")
        fig_top = px.bar(
            top10, x="infra_score", y="India/State/UT",
            orientation="h",
            color="infra_score",
            color_continuous_scale=["#9FE1CB", "#1D9E75", "#085041"],
            range_color=[top10["infra_score"].min(), 1.0],
            labels={"infra_score": "Score", "India/State/UT": ""},
            text=top10["infra_score"].round(2),
        )
        fig_top.update_traces(textposition="outside")
        fig_top.update_layout(**PLOTLY_LAYOUT, height=360,
                              coloraxis_showscale=False)
        st.plotly_chart(fig_top, use_container_width=True)

    with col_bot:
        st.subheader("⚠️ Bottom 10 States")
        bot10 = df.nsmallest(10, "infra_score").sort_values("infra_score", ascending=False)
        fig_bot = px.bar(
            bot10, x="infra_score", y="India/State/UT",
            orientation="h",
            color="infra_score",
            color_continuous_scale=["#501313", "#E24B4A", "#F7C1C1"],
            range_color=[0.5, bot10["infra_score"].max()],
            labels={"infra_score": "Score", "India/State/UT": ""},
            text=bot10["infra_score"].round(2),
        )
        fig_bot.update_traces(textposition="outside")
        fig_bot.update_layout(**PLOTLY_LAYOUT, height=360,
                              coloraxis_showscale=False)
        st.plotly_chart(fig_bot, use_container_width=True)

# ============================================================
# SECTION 6 — PAGE: RISK STATES
# ============================================================
elif page == "🚨 Risk States":
    st.title("🚨 Risk States")

    tab_both, tab_infra, tab_teacher = st.tabs([
        "🔴 High Risk (Both)",
        "🏚️ Poor Infrastructure",
        "👨‍🏫 Teacher Overload",
    ])

    # --- 6.1 High risk = bad infra AND overloaded teachers ---
    with tab_both:
        st.markdown(
            "States where **both** infrastructure is below median "
            f"**and** PTR exceeds {THRESHOLDS['ptr_warning']}."
        )
        high_risk_df = df[df["high_risk"]].sort_values("infra_score")

        fig_risk = px.scatter(
            high_risk_df,
            x="infra_score", y="PTR",
            size=[14] * len(high_risk_df),
            color="infra_score",
            color_continuous_scale=["#501313", "#E24B4A"],
            hover_name="India/State/UT",
            text="India/State/UT",
            labels={"infra_score": "Infra Score", "PTR": "Students / Teacher"},
        )
        fig_risk.update_traces(textposition="top center", textfont_size=10)
        fig_risk.update_layout(**PLOTLY_LAYOUT, height=380,
                               coloraxis_showscale=False)
        st.plotly_chart(fig_risk, use_container_width=True)

        st.dataframe(
            high_risk_df[["India/State/UT", "infra_score", "PTR", "infra_tier"]]
            .rename(columns=COLUMN_LABELS)
            .reset_index(drop=True),
            use_container_width=True,
        )

    # --- 6.2 Poor infrastructure only ---
    with tab_infra:
        poor_df = df[df["infra_tier"] == "Poor"].sort_values("infra_score")
        st.markdown(f"**{len(poor_df)} states** in the bottom tercile of infrastructure.")
        st.dataframe(
            poor_df[["India/State/UT", "infra_score"] + FACILITY_COLS]
            .rename(columns=COLUMN_LABELS)
            .reset_index(drop=True),
            use_container_width=True,
        )

    # --- 6.3 Teacher overload only ---
    with tab_teacher:
        teacher_df = df[df["teacher_risk"]].sort_values("PTR", ascending=False)
        st.markdown(
            f"**{len(teacher_df)} states** with PTR above "
            f"{THRESHOLDS['ptr_danger']} (danger threshold)."
        )
        fig_ptr = px.bar(
            teacher_df.sort_values("PTR"),
            x="PTR", y="India/State/UT",
            orientation="h",
            color="PTR",
            color_continuous_scale=["#FAEEDA", "#EF9F27", "#633806"],
            labels={"PTR": "Students / Teacher", "India/State/UT": ""},
            text=teacher_df.sort_values("PTR")["PTR"].round(1),
        )
        fig_ptr.update_traces(textposition="outside")
        fig_ptr.update_layout(**PLOTLY_LAYOUT, height=380,
                              coloraxis_showscale=False)
        st.plotly_chart(fig_ptr, use_container_width=True)

# ============================================================
# SECTION 7 — PAGE: INDIA MAP
# ============================================================
elif page == "🗺️ India Map":
    st.title("🗺️ India Map")
    st.caption("Choropleth of state-wise infrastructure tier.")

    try:
        with open("india_states.geojson") as f:
            india_geojson = json.load(f)

        map_metric = st.selectbox(
            "Color map by",
            options=["infra_score", "PTR"] + FACILITY_COLS,
            format_func=lambda c: COLUMN_LABELS.get(c, c),
        )

        fig_map = px.choropleth(
            df,
            geojson=india_geojson,
            featureidkey="properties.ST_NM",
            locations="state_mapped",
            color=map_metric,
            hover_name="India/State/UT",
            hover_data={
                "infra_score": ":.2f",
                "PTR": ":.1f",
                "state_mapped": False,
            },
            color_continuous_scale=(
                "RdYlGn" if map_metric == "infra_score"
                else "YlOrRd_r"
            ),
            labels={map_metric: COLUMN_LABELS.get(map_metric, map_metric)},
            title=f"State-wise · {COLUMN_LABELS.get(map_metric, map_metric)}",
        )
        fig_map.update_geos(fitbounds="locations", visible=False)
        fig_map.update_layout(**PLOTLY_LAYOUT, height=600)
        st.plotly_chart(fig_map, use_container_width=True)

    except FileNotFoundError:
        st.error(
            "`india_states.geojson` not found in the working directory. "
            "Place the GeoJSON file alongside this script to enable the map."
        )

# ============================================================
# SECTION 8 — PAGE: STATE DEEP-DIVE
# ============================================================
elif page == "🔍 State Deep-Dive":
    st.title("🔍 State Deep-Dive")

    state = st.selectbox("Select a state", sorted(df["India/State/UT"].unique()))
    row = df[df["India/State/UT"] == state].iloc[0]

    infra   = row["infra_score"]
    ptr     = row["PTR"]
    tier    = row["infra_tier"]

    # --- 8.1 KPI strip ---
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Infra Score", f"{infra:.2f}",
              delta=f"{infra - df['infra_score'].mean():.2f} vs national avg")
    k2.metric("Students / Teacher", f"{ptr:.1f}",
              delta=f"{ptr - df['PTR'].mean():.1f} vs national avg",
              delta_color="inverse")
    k3.metric("Infra Tier", tier)
    k4.metric("High Risk", "Yes ⚠️" if row["high_risk"] else "No ✅")

    st.divider()

    # --- 8.2 Facility breakdown bar ---
    st.subheader("Facility Availability")

    facility_vals = [row[c] for c in FACILITY_COLS]
    facility_df = pd.DataFrame({
        "Facility": FACILITY_NAMES,
        "Value":    facility_vals,
        "Status":   ["Below threshold" if v < THRESHOLDS["facility_ok"] else "OK"
                     for v in facility_vals],
    })

    fig_fac = px.bar(
        facility_df,
        x="Facility", y="Value",
        color="Status",
        color_discrete_map={"OK": "#1D9E75", "Below threshold": "#E24B4A"},
        text=facility_df["Value"].map(lambda v: f"{v:.0%}"),
        range_y=[0, 1.05],
        labels={"Value": "Availability Ratio"},
    )
    fig_fac.add_hline(
        y=THRESHOLDS["facility_ok"],
        line_dash="dash", line_color="#888",
        annotation_text=f"Threshold ({THRESHOLDS['facility_ok']:.0%})",
        annotation_position="top right",
    )
    fig_fac.update_traces(textposition="outside")
    fig_fac.update_layout(**PLOTLY_LAYOUT, height=360, showlegend=True)
    st.plotly_chart(fig_fac, use_container_width=True)

    # --- 8.3 Radar: this state vs national average ---
    st.subheader(f"{state} vs. National Average")

    national_avg = df[FACILITY_COLS].mean()
    state_vals   = [row[c] for c in FACILITY_COLS]
    nat_vals     = national_avg[FACILITY_COLS].tolist()

    radar_fig = go.Figure()
    radar_fig.add_trace(go.Scatterpolar(
        r=state_vals + [state_vals[0]],
        theta=FACILITY_NAMES + [FACILITY_NAMES[0]],
        fill="toself",
        name=state,
        line_color="#1D9E75",
        fillcolor="rgba(29,158,117,0.2)",
    ))
    radar_fig.add_trace(go.Scatterpolar(
        r=nat_vals + [nat_vals[0]],
        theta=FACILITY_NAMES + [FACILITY_NAMES[0]],
        fill="toself",
        name="National Avg",
        line_color="#888",
        fillcolor="rgba(136,136,136,0.1)",
        line_dash="dash",
    ))
    radar_fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 1], tickformat=".0%")),
        **PLOTLY_LAYOUT,
        height=380,
    )
    st.plotly_chart(radar_fig, use_container_width=True)

    # --- 8.4 Diagnosis & actions ---
    st.subheader("📌 Diagnosis & Suggested Actions")

    issues = []
    actions = []

    if ptr > THRESHOLDS["ptr_danger"]:
        issues.append(f"🚨 **Critical teacher overload** — PTR of {ptr:.1f} far exceeds safe limit.")
        actions.append("Recruit additional teachers urgently; consider split-shift scheduling.")
    elif ptr > THRESHOLDS["ptr_warning"]:
        issues.append(f"⚠️ **Elevated teacher load** — PTR {ptr:.1f} is above the warning threshold.")
        actions.append("Plan incremental teacher hiring in the next budget cycle.")

    for col, name in zip(FACILITY_COLS, FACILITY_NAMES):
        val = row[col]
        if val < THRESHOLDS["facility_ok"]:
            issues.append(f"⚠️ **{name} access low** — only {val:.0%} of schools covered.")
            actions.append(f"Prioritise {name.lower()} infrastructure grants for {state}.")

    if not issues:
        st.success("✅ No critical issues detected. Maintain current standards and monitor annually.")
    else:
        for issue in issues:
            st.warning(issue)
        st.markdown("**Recommended actions:**")
        for i, action in enumerate(actions, 1):
            st.markdown(f"{i}. {action}")

    with st.expander("📄 Raw data for this state"):
        st.dataframe(df[df["India/State/UT"] == state], use_container_width=True)

# ============================================================
# SECTION 9 — PAGE: COMPARE STATES
# ============================================================
elif page == "⚖️ Compare States":
    st.title("⚖️ Compare States")
    st.caption("Select 2–3 states to compare side by side on all key metrics.")

    selected = st.multiselect(
        "Choose states to compare",
        options=sorted(df["India/State/UT"].unique()),
        default=sorted(df["India/State/UT"].unique())[:2],
        max_selections=3,
    )

    if len(selected) < 2:
        st.info("Select at least 2 states to compare.")
        st.stop()

    cmp_df = df[df["India/State/UT"].isin(selected)]

    # --- 9.1 Side-by-side KPI table ---
    st.subheader("Key Metrics")
    display_cols = ["India/State/UT", "infra_score", "PTR", "infra_tier", "high_risk"]
    st.dataframe(
        cmp_df[display_cols].rename(columns=COLUMN_LABELS).set_index("State / UT"),
        use_container_width=True,
    )

    st.divider()

    # --- 9.2 Grouped bar: all facilities ---
    st.subheader("Facility Comparison")

    melt_df = cmp_df.melt(
        id_vars="India/State/UT",
        value_vars=FACILITY_COLS,
        var_name="Facility",
        value_name="Ratio",
    )
    melt_df["Facility"] = melt_df["Facility"].map(
        dict(zip(FACILITY_COLS, FACILITY_NAMES))
    )

    fig_cmp = px.bar(
        melt_df,
        x="Facility", y="Ratio",
        color="India/State/UT",
        barmode="group",
        text=melt_df["Ratio"].map(lambda v: f"{v:.0%}"),
        range_y=[0, 1.1],
        labels={"Ratio": "Availability", "India/State/UT": "State"},
    )
    fig_cmp.add_hline(
        y=THRESHOLDS["facility_ok"],
        line_dash="dash", line_color="#888",
        annotation_text="Threshold",
    )
    fig_cmp.update_traces(textposition="outside")
    fig_cmp.update_layout(**PLOTLY_LAYOUT, height=400)
    st.plotly_chart(fig_cmp, use_container_width=True)

    # --- 9.3 Radar overlay ---
    st.subheader("Radar Overview")

    radar_cmp = go.Figure()
    palette = ["#1D9E75", "#EF9F27", "#378ADD"]

    for i, (_, row) in enumerate(cmp_df.iterrows()):
        vals = [row[c] for c in FACILITY_COLS]
        radar_cmp.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=FACILITY_NAMES + [FACILITY_NAMES[0]],
            fill="toself",
            name=row["India/State/UT"],
            line_color=palette[i % len(palette)],
            fillcolor=palette[i % len(palette)].replace("#", "rgba(").rstrip(")") + ",0.15)",
        ))

    radar_cmp.update_layout(
        polar=dict(radialaxis=dict(range=[0, 1], tickformat=".0%")),
        **PLOTLY_LAYOUT,
        height=420,
    )
    st.plotly_chart(radar_cmp, use_container_width=True)

    # --- 9.4 CSV download ---
    st.divider()
    csv_bytes = (
        cmp_df[display_cols + FACILITY_COLS]
        .rename(columns=COLUMN_LABELS)
        .to_csv(index=False)
        .encode("utf-8")
    )
    st.download_button(
        label="⬇️ Download comparison as CSV",
        data=csv_bytes,
        file_name="state_comparison.csv",
        mime="text/csv",
    )