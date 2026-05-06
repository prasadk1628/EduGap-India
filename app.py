import streamlit as st
import pandas as pd
import plotly.express as px
import json

# ---------------------------
# LOAD DATA
# ---------------------------
df = pd.read_csv("education_analysis_ready.csv")

column_labels = {
    "India/State/UT": "State / UT",
    "infra_score": "Infrastructure Score",
    "PTR": "Students per Teacher",
    "electricity_ratio": "Electricity Access",
    "toilet_ratio": "Toilet Access",
    "water_ratio": "Water Access",
    "computer_ratio": "Computer Access"
}

st.set_page_config(page_title="School Infrastructure Dashboard", layout="wide")

st.title("📊 Government School Infrastructure Dashboard")

# ---------------------------
# SECTION 1: OVERVIEW
# ---------------------------
st.header("🏫 Overall Infrastructure Performance")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Performing States")
    top_states = df.sort_values(by="infra_score", ascending=False).head(10)
    st.bar_chart(top_states.set_index("India/State/UT")["infra_score"])

with col2:
    st.subheader("Worst Performing States")
    worst_states = df.sort_values(by="infra_score", ascending=True).head(10)
    st.bar_chart(worst_states.set_index("India/State/UT")["infra_score"])


# ---------------------------
# SECTION 1.2: Infrastructure Map (India)
# ---------------------------

st.header("🗺️ Infrastructure Map (India)")

# Load GeoJSON - using local file (complete, 36 states)
with open("india_states.geojson") as f:
    india_geojson = json.load(f)

q1 = df["infra_score"].quantile(0.33)
q2 = df["infra_score"].quantile(0.66)

def categorize(score):
    if score < q1:
        return "Poor"
    elif score < q2:
        return "Average"
    else:
        return "Good"

df["infra_category"] = df["infra_score"].apply(categorize)

# Only one mismatch needed
state_mapping = {
    "Dadra & Nagar Haveli and Daman & Diu": "Dadra and Nagar Haveli and Daman and Diu"
}

df["state_mapped"] = df["India/State/UT"].replace(state_mapping)

fig = px.choropleth(
    df,
    geojson=india_geojson,
    featureidkey="properties.ST_NM",
    locations="state_mapped",
    color="infra_category",
    hover_name="India/State/UT",
    color_discrete_map={
        "Poor": "red",
        "Average": "yellow",
        "Good": "green"
    },
    title="State-wise Infrastructure Quality"
)
fig.update_geos(fitbounds="locations", visible=False)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# SECTION 1.3: Top 5 States Needing Immediate Attention
# ---------------------------

st.header("📉 Lowest Infrastructure States (Top 5)")

worst_states = df.sort_values(by="infra_score").head(5)

st.dataframe(
    worst_states[["India/State/UT", "infra_score", "PTR"]],
    use_container_width=True
)

# ---------------------------
# SECTION 2: HIGH RISK STATES
# ---------------------------
st.header("🚨 Critical Risk States (Infra + Teacher Issues)")

high_risk = df[df["high_risk"] == True]

st.dataframe(
    high_risk[["India/State/UT", "infra_score", "PTR"]]
    .rename(columns=column_labels),
    use_container_width=True
)

st.markdown(
"""
**High-risk states are those where:**
- Infrastructure is below average  
- Teachers are overloaded  

These regions need immediate attention.
"""
)

# ---------------------------
# SECTION 2.1: Teacher Overload Risk (High PTR)
# ---------------------------
st.header("👨‍🏫 Teacher Overload Risk (High PTR)")

teacher_risk_df = df[df["teacher_risk"] == True]

st.dataframe(
    teacher_risk_df[["India/State/UT", "PTR"]],
    use_container_width=True
)

st.markdown("""
States listed here have a high number of students per teacher.
Even if infrastructure is adequate, teaching quality may be affected due to overload.
""")

# ---------------------------
# SECTION 3: STATE ANALYSIS
# ---------------------------
st.header("🔍 State-Level Analysis")

state = st.selectbox("Select a State", df["India/State/UT"].unique())
filtered_df = df[df["India/State/UT"] == state]

ptr = filtered_df["PTR"].values[0]
infra = filtered_df["infra_score"].values[0]
electricity = filtered_df["electricity_ratio"].values[0]

# KPI Cards
st.subheader("📌 Key Indicators")

c1, c2, c3 = st.columns(3)

c1.metric("👨‍🏫 Students per Teacher", f"{ptr:.1f}")
c2.metric("🏫 Infrastructure Score", f"{infra:.2f}")
c3.metric("⚡ Electricity Access", f"{electricity:.2%}")

with st.expander("📊 View Detailed Data"):
    st.dataframe(filtered_df, use_container_width=True)

# ---------------------------
# SECTION 3.1: INFRA BREAKDOWN
# ---------------------------
st.subheader("🔍 Infrastructure Breakdown")

electricity = filtered_df["electricity_ratio"].values[0]
toilet = filtered_df["toilet_ratio"].values[0]
water = filtered_df["water_ratio"].values[0]
computer = filtered_df["computer_ratio"].values[0]

breakdown_df = pd.DataFrame({
    "Metric": [
        "Electricity Access",
        "Toilet Access",
        "Water Access",
        "Computer Access"
    ],
    "Value": [
        electricity,
        toilet,
        water,
        computer
    ]
})

st.bar_chart(breakdown_df.set_index("Metric"))

# Explanation
st.subheader("🧠 What is the main issue?")

if electricity < 0.8:
    st.write("⚠️ Electricity access is low. Schools may lack reliable power.")

if toilet < 0.8:
    st.write("⚠️ Toilet access is low. This can affect hygiene and attendance.")

if electricity >= 0.8 and toilet >= 0.8:
    st.write("✅ Basic infrastructure is reasonably available.")

# ---------------------------
# SECTION 4: EXPLANATION
# ---------------------------
st.subheader("🧠 What this means")

# Teacher load explanation
if ptr > 30:
    st.write("🚨 Classrooms are overcrowded. Teachers may struggle to give individual attention.")
elif ptr > 20:
    st.write("⚠️ Slightly high student load. Learning quality may be affected.")
else:
    st.write("✅ Student-teacher balance is healthy.")

# Infrastructure explanation
if infra < 0.85:
    st.write("🚨 Schools lack basic facilities like electricity or toilets.")
elif infra < 0.95:
    st.write("⚠️ Infrastructure is average. Some improvements are needed.")
else:
    st.write("✅ Most schools have adequate facilities.")

# ---------------------------
# SECTION 4.1: Suggested Actions
# ---------------------------
st.subheader("📌 Suggested Actions")

if infra < 0.85 and ptr > 25:
    st.write("🚨 Urgent Action Needed:")
    st.write("- Improve basic infrastructure immediately")
    st.write("- Recruit more teachers to reduce overload")

elif ptr > 25:
    st.write("⚠️ Teacher Shortage Focus:")
    st.write("- Hire more teachers")
    st.write("- Reduce classroom burden")

elif infra < 0.95:
    st.write("⚠️ Infrastructure Improvement Needed:")
    st.write("- Upgrade facilities like electricity and toilets")
    st.write("- Focus on quality of school environment")

else:
    st.write("✅ System is performing well:")
    st.write("- Maintain current standards")
    st.write("- Monitor regularly for consistency")


    