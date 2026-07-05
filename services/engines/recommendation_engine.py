def target_emergency_months(twin):
    customer = twin["customer"]
    metrics = twin["metrics"]
    persona = twin["persona"]["type"]

    months = 6

    if "Entrepreneurial" in persona:
        months = 12
    elif "Family" in persona:
        months = 8
    elif metrics["income"] >= 200000 and metrics["debt_to_income"] < 20:
        months = 5
    elif metrics["income"] < 60000:
        months = 7

    if customer.get("risk_preference") == "conservative":
        months += 1

    return months


def recommended_sip(twin):
    metrics = twin["metrics"]
    customer = twin["customer"]
    risk = customer.get("risk_preference", "moderate")

    income = metrics["income"]
    savings_rate = metrics["savings_rate"]

    if income < 60000:
        base_percent = 0.08
    elif income < 150000:
        base_percent = 0.15
    else:
        base_percent = 0.25

    if risk == "aggressive":
        base_percent += 0.05
    elif risk == "conservative":
        base_percent -= 0.04

    if savings_rate < 10:
        base_percent = min(base_percent, 0.08)

    return int(income * max(base_percent, 0.05))


def run_recommendation_engine(twin):
    customer = twin["customer"]
    metrics = twin["metrics"]
    future_values = twin["future_values"]

    emergency_target_months = target_emergency_months(twin)
    emergency_target_amount = int(
        metrics["expenses"] * emergency_target_months)

    sip_reco = recommended_sip(twin)
    sip_gap = max(0, sip_reco - customer["existing_sip"])

    insurance_target = int(metrics["income"] * 12 * 10)
    insurance_gap = max(0, insurance_target - customer["insurance_cover"])

    recommendations = []

    if metrics["emergency_months"] < emergency_target_months:
        recommendations.append({
            "category": "Emergency Fund",
            "title": "Build emergency fund",
            "detail": f"Target {emergency_target_months} months of expenses: ₹{emergency_target_amount:,}.",
            "impact": "Improves financial resilience"
        })

    if sip_gap > 0:
        recommendations.append({
            "category": "Investments",
            "title": "Increase monthly SIP",
            "detail": f"Increase SIP from ₹{customer['existing_sip']:,} to ₹{sip_reco:,}.",
            "impact": "Improves long-term goal readiness"
        })

    if insurance_gap > 0:
        recommendations.append({
            "category": "Insurance",
            "title": "Increase insurance cover",
            "detail": f"Recommended cover is ₹{insurance_target:,}. Current gap: ₹{insurance_gap:,}.",
            "impact": "Protects dependents and future goals"
        })

    if metrics["debt_to_income"] > 35:
        recommendations.append({
            "category": "Debt",
            "title": "Reduce debt burden",
            "detail": "Debt-to-income ratio is high. Avoid new loans until cash flow improves.",
            "impact": "Reduces financial stress risk"
        })

    recommendations.append({
        "category": "Goal Planning",
        "title": "Use inflation-adjusted goal planning",
        "detail": f"Your goal becomes ₹{future_values['inflation_adjusted_goal']:,} after inflation.",
        "impact": "Prevents under-saving for future goals"
    })

    twin["recommendations"] = recommendations
    twin["recommendation_summary"] = {
        "recommended_sip": sip_reco,
        "sip_gap": sip_gap,
        "emergency_target_months": emergency_target_months,
        "emergency_target_amount": emergency_target_amount,
        "insurance_target": insurance_target,
        "insurance_gap": insurance_gap
    }

    return twin
