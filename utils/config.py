THRESHOLDS = {
    "infra_good": 0.95,
    "infra_avg": 0.85,
    "ptr_danger": 30,
    "ptr_warning": 25,
    "facility_ok": 0.80,
}

FACILITY_COLS = [
    "electricity_ratio",
    "toilet_ratio",
    "water_ratio",
    "computer_ratio",
]

FACILITY_NAMES = [
    "Electricity",
    "Toilets",
    "Water",
    "Computers",
]

COL_LABELS = {
    "India/State/UT": "State / UT",
    "infra_score": "Infrastructure Score",
    "PTR": "Students per Teacher",
    "electricity_ratio": "Electricity Access",
    "toilet_ratio": "Toilet Access",
    "water_ratio": "Water Access",
    "computer_ratio": "Computer Access",
    "infra_tier": "Infrastructure Tier",
    "high_risk": "High Risk",
    "teacher_risk": "Teacher Risk",
}

# Theme Colors
G = "#22C97A"      # Green
W = "#F5A623"      # Warning Yellow
D = "#F0454A"      # Danger Red
ACC = "#4F8EF7"    # Accent Blue

# Tier Colors
TIER_CLR = {
    "Poor": D,
    "Average": W,
    "Good": G,
}

# Compare State Palette
CMP_PAL = [
    ACC,
    W,
    G,
]