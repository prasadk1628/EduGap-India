# 🏫 InfraViz India — Government School Infrastructure Intelligence Dashboard

> **An interactive analytics dashboard that reveals infrastructure gaps, teacher overload risks, and facility disparities across Indian states using UDISE+ data.**

InfraViz India is an end-to-end education analytics project built on **UDISE+ 2023–24** data to compare school infrastructure quality across Indian states and union territories.

It helps answer questions such as:

* Which states have the weakest infrastructure coverage?
* Where are teacher overload risks highest?
* Which facilities are most inconsistent across regions?
* Which states should receive priority intervention?

[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/prasadk1628/EduGap-India)
[![Live Dashboard](https://img.shields.io/badge/Streamlit-Live%20Dashboard-brightgreen)](#)

---

## 📌 Problem Statement

India’s public school system is large and diverse, but infrastructure quality is not evenly distributed.

Some schools still face gaps in:

* electricity access
* sanitation facilities
* drinking water availability
* computer access
* teacher availability

Raw education data alone is difficult to interpret at scale. InfraViz India transforms it into an interactive dashboard for identifying infrastructure weaknesses and priority states.

---

## 🎯 Project Objectives

This project was designed to:

* analyze school infrastructure quality across India
* identify high-risk states with infrastructure and teacher issues
* compare states across key education indicators
* measure facility availability ratios
* support data-driven education planning
* provide an interactive state-level deep dive

---

## 📂 Dataset

| Property     | Detail                                      |
| ------------ | ------------------------------------------- |
| **Dataset**  | UDISE+ 2023–24                              |
| **Coverage** | Indian states and union territories         |
| **Source**   | Ministry of Education, Government of India  |
| **Type**     | School infrastructure and education metrics |

---

## 🧹 Data Cleaning & Processing

### Cleaning Steps

* removed invalid rows
* standardized state names
* renamed columns for readability
* fixed inconsistent formatting
* converted numeric fields into usable analytical formats

### Engineered Metrics

| Metric              | Description                            |
| ------------------- | -------------------------------------- |
| `infra_score`       | Composite infrastructure quality score |
| `PTR`               | Student-to-Teacher Ratio               |
| `electricity_ratio` | Functional electricity availability    |
| `water_ratio`       | Drinking water availability            |
| `computer_ratio`    | Computer facility availability         |
| `toilet_ratio`      | Functional toilet availability         |

---

## 🧠 Scoring Methodology

InfraViz India uses normalized facility availability ratios to estimate infrastructure quality.

### Score Factors

* electricity access
* toilet availability
* drinking water access
* computer facilities

States are classified into:

* 🟢 Good
* 🟡 Average
* 🔴 Poor

based on percentile thresholds.

---

## 🚨 Risk Classification Logic

States are marked high-risk when:

* infrastructure quality falls below threshold levels
* student-to-teacher ratio becomes critically high

This helps surface regions that need urgent educational attention.

---

## 📊 Dashboard Sections

| Section               | Purpose                                  |
| --------------------- | ---------------------------------------- |
| **National Overview** | Summary KPIs and facility distribution   |
| **India Map**         | State-wise infrastructure quality        |
| **Risk States**       | Critical infrastructure and PTR analysis |
| **State Deep Dive**   | Detailed state diagnosis                 |
| **Compare States**    | Multi-state comparison view              |

---

## 📈 Key Insights

* Infrastructure quality is uneven across states.
* Teacher overload remains a major issue in some regions.
* Computer access is still inconsistent despite improvements in basic facilities.
* Weak water and electricity access are strongly associated with poor infrastructure scores.

---

## 🛠️ Tech Stack

| Tool          | Purpose                    |
| ------------- | -------------------------- |
| **Python**    | Core development           |
| **Pandas**    | Data cleaning and analysis |
| **Streamlit** | Interactive dashboard      |
| **Plotly**    | Visualizations             |
| **GeoJSON**   | India mapping              |

---

## 📸 Dashboard Preview

Add screenshots here once exported:

* National Overview
* Infrastructure Map
* State Deep Dive
* Compare States

---

## 📁 Project Structure

```bash
EduGap-India/
├── app.py
├── assets/
│   ├── styles.css
│   └── india_states.geojson
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── utils/
│   ├── config.py
│   ├── helpers.py
│   ├── data_loader.py
│   └── plots.py
├── pages/
│   ├── overview.py
│   ├── india_map.py
│   ├── risk_states.py
│   ├── state_deepdive.py
│   └── compare_states.py
└── README.md
```

---

## ▶️ Run Locally

```bash
git clone https://github.com/prasadk1628/EduGap-India.git
cd EduGap-India
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔮 Future Improvements

* historical trend analysis
* district-level analysis
* predictive infrastructure scoring
* time-series education tracking
* policy recommendation engine
* real-time education analytics integration

---

## 👤 Author

**Vara Prasad K**
Aspiring Data Analyst | Python · SQL · Streamlit

GitHub: https://github.com/prasadk1628
LinkedIn: https://www.linkedin.com/in/vara-prasad-kavali/
