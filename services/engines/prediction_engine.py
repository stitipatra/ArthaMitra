def simulate_sip(monthly_sip, years, annual_return=0.12):
    monthly_rate = annual_return / 12
    months = years * 12

    if monthly_rate == 0:
        return round(monthly_sip * months)

    return round(monthly_sip * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate))


def run_prediction_engine(twin):
    customer = twin["customer"]
    metrics = twin["metrics"]
    future_values = twin["future_values"]

    existing_sip = customer["existing_sip"]
    years = customer["goal_years"]

    projected_corpus = simulate_sip(existing_sip, years)
    target = future_values["inflation_adjusted_goal"]

    goal_gap = max(0, target - projected_corpus - metrics["investments"])

    if goal_gap == 0:
        goal_status = "On Track"
    elif projected_corpus + metrics["investments"] >= target * 0.7:
        goal_status = "Slightly Behind"
    else:
        goal_status = "At Risk"

    if metrics["debt_to_income"] > 40 or metrics["savings_rate"] < 5:
        stress_risk = "High"
    elif metrics["debt_to_income"] > 25 or metrics["savings_rate"] < 15:
        stress_risk = "Medium"
    else:
        stress_risk = "Low"

    twin["predictions"] = {
        "projected_corpus": projected_corpus,
        "goal_gap": round(goal_gap),
        "goal_status": goal_status,
        "financial_stress_risk": stress_risk,
        "emergency_depletion_risk": "High" if metrics["emergency_months"] < 3 else "Low"
    }

    return twin
