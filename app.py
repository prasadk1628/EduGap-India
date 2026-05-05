import streamlit as st
import pandas as pd

# ---------------------------
# LOAD DATA
# ---------------------------
df = pd.read_csv("education_analysis_ready.csv")

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
# SECTION 2: HIGH RISK STATES
# ---------------------------
st.header("🚨 High-Risk States (Need Attention)")

high_risk = df[df["high_risk"] == True]

st.dataframe(
    high_risk[["India/State/UT", "infra_score", "PTR"]],
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
# SECTION 2.1: 👨‍🏫 Teacher Overload Risk (High PTR)
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

ptr = filtered_df["PTR"].values[0]
infra = filtered_df["infra_score"].values[0]

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

# ---------------------------
# SECTION 5: RAW DETAILS (OPTIONAL)
# ---------------------------

