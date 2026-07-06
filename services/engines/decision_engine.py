def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


ASSET_DECISION_WEIGHTS = {
    "house": {
        "affordability": 0.25,
        "liquidity": 0.25,
        "debt": 0.25,
        "goal_impact": 0.15,
        "stability": 0.10,
    },
    "commercial_property": {
        "affordability": 0.20,
        "liquidity": 0.25,
        "debt": 0.25,
        "goal_impact": 0.10,
        "stability": 0.20,
    },
    "car": {
        "affordability": 0.30,
        "liquidity": 0.20,
        "debt": 0.25,
        "goal_impact": 0.15,
        "stability": 0.10,
    },
    "bike": {
        "affordability": 0.35,
        "liquidity": 0.25,
        "debt": 0.20,
        "goal_impact": 0.10,
        "stability": 0.10,
    },
    "phone": {
        "affordability": 0.35,
        "liquidity": 0.40,
        "debt": 0.10,
        "goal_impact": 0.10,
        "stability": 0.05,
    },
    "laptop": {
        "affordability": 0.35,
        "liquidity": 0.35,
        "debt": 0.10,
        "goal_impact": 0.10,
        "stability": 0.10,
    },
    "electronics": {
        "affordability": 0.30,
        "liquidity": 0.40,
        "debt": 0.10,
        "goal_impact": 0.15,
        "stability": 0.05,
    },
    "vacation": {
        "affordability": 0.25,
        "liquidity": 0.40,
        "debt": 0.10,
        "goal_impact": 0.20,
        "stability": 0.05,
    },
    "wedding": {
        "affordability": 0.25,
        "liquidity": 0.30,
        "debt": 0.10,
        "goal_impact": 0.25,
        "stability": 0.10,
    },
    "education": {
        "affordability": 0.25,
        "liquidity": 0.20,
        "debt": 0.15,
        "goal_impact": 0.25,
        "stability": 0.15,
    },
    "business": {
        "affordability": 0.20,
        "liquidity": 0.30,
        "debt": 0.15,
        "goal_impact": 0.10,
        "stability": 0.25,
    },
    "friend_help": {
        "affordability": 0.25,
        "liquidity": 0.45,
        "debt": 0.10,
        "goal_impact": 0.15,
        "stability": 0.05,
    },
    "medical": {
        "affordability": 0.10,
        "liquidity": 0.45,
        "debt": 0.10,
        "goal_impact": 0.10,
        "stability": 0.25,
    },
    "renovation": {
        "affordability": 0.25,
        "liquidity": 0.35,
        "debt": 0.15,
        "goal_impact": 0.15,
        "stability": 0.10,
    },
    "jewellery": {
        "affordability": 0.25,
        "liquidity": 0.40,
        "debt": 0.10,
        "goal_impact": 0.20,
        "stability": 0.05,
    },
    "generic_purchase": {
        "affordability": 0.30,
        "liquidity": 0.30,
        "debt": 0.15,
        "goal_impact": 0.15,
        "stability": 0.10,
    },
}


def evaluate_purchase_decision(
    base_twin,
    simulated_twin,
    asset,
    purchase_amount,
    down_payment,
    estimated_emi,
    recurring_cost,
):
    base_metrics = base_twin["metrics"]
    sim_metrics = simulated_twin["metrics"]
    base_predictions = base_twin["predictions"]
    sim_predictions = simulated_twin["predictions"]

    scores = {
        "affordability": score_affordability(base_metrics, sim_metrics, estimated_emi, recurring_cost),
        "liquidity": score_liquidity(base_twin, simulated_twin, down_payment),
        "debt": score_debt(sim_metrics),
        "goal_impact": score_goal_impact(base_predictions, sim_predictions),
        "stability": score_stability(base_twin, simulated_twin),
    }

    weights = ASSET_DECISION_WEIGHTS.get(
        asset, ASSET_DECISION_WEIGHTS["generic_purchase"])

    overall_score = round(
        sum(scores[key]["score"] * weights[key] for key in weights)
    )

    verdict, impact_level = generate_verdict(overall_score, scores)

    return {
        "asset": asset,
        "purchase_amount": purchase_amount,
        "overall_score": overall_score,
        "verdict": verdict,
        "impact_level": impact_level,
        "component_scores": scores,
        "weights": weights,
        "summary": build_decision_summary(asset, overall_score, verdict, scores),
    }


def score_affordability(base_metrics, sim_metrics, estimated_emi, recurring_cost):
    income = sim_metrics["income"]
    disposable_after = sim_metrics["disposable_income"]

    monthly_commitment = estimated_emi + recurring_cost

    commitment_ratio = (monthly_commitment / income) * 100 if income else 100
    disposable_ratio = (disposable_after / income) * 100 if income else -100

    score = 100

    if commitment_ratio > 50:
        score -= 60
    elif commitment_ratio > 35:
        score -= 40
    elif commitment_ratio > 25:
        score -= 25
    elif commitment_ratio > 15:
        score -= 10

    if disposable_ratio < 0:
        score -= 50
    elif disposable_ratio < 10:
        score -= 30
    elif disposable_ratio < 20:
        score -= 15

    reasons = [
        f"New monthly commitment is {round(commitment_ratio, 1)}% of income.",
        f"Disposable income after decision is {round(disposable_ratio, 1)}% of income.",
    ]

    improvements = []
    if commitment_ratio > 30:
        improvements.append(
            "Increase down payment or choose a lower-cost option.")
    if disposable_ratio < 20:
        improvements.append("Preserve monthly cash flow before committing.")

    return {
        "score": round(clamp(score)),
        "reasons": reasons,
        "improvements": improvements or ["Affordability impact is manageable."]
    }


def score_liquidity(base_twin, simulated_twin, down_payment):
    base_metrics = base_twin["metrics"]
    sim_metrics = simulated_twin["metrics"]
    target_months = simulated_twin["recommendation_summary"]["emergency_target_months"]

    emergency_after = sim_metrics["emergency_months"]
    liquidity_drop = base_metrics["emergency_months"] - emergency_after

    score = 100

    if emergency_after < 1:
        score -= 70
    elif emergency_after < 3:
        score -= 50
    elif emergency_after < target_months:
        score -= 25

    if liquidity_drop > 4:
        score -= 25
    elif liquidity_drop > 2:
        score -= 15

    reasons = [
        f"Emergency fund after decision is {emergency_after} months.",
        f"Recommended emergency fund target is {target_months} months.",
        f"Emergency fund changes by {round(liquidity_drop, 1)} months."
    ]

    improvements = []
    if emergency_after < target_months:
        improvements.append("Build emergency fund before proceeding.")
    if down_payment > base_metrics["savings"] * 0.5:
        improvements.append(
            "Avoid using more than half of liquid savings upfront.")

    return {
        "score": round(clamp(score)),
        "reasons": reasons,
        "improvements": improvements or ["Liquidity remains healthy."]
    }


def score_debt(sim_metrics):
    dti = sim_metrics["debt_to_income"]

    score = 100

    if dti > 50:
        score -= 70
    elif dti > 40:
        score -= 50
    elif dti > 35:
        score -= 35
    elif dti > 25:
        score -= 15

    reasons = [
        f"Debt-to-income ratio after decision is {dti}%."
    ]

    improvements = []
    if dti > 35:
        improvements.append("Reduce EMI burden below 35% of income.")
    else:
        improvements.append("Debt level remains within a manageable range.")

    return {
        "score": round(clamp(score)),
        "reasons": reasons,
        "improvements": improvements
    }


def score_goal_impact(base_predictions, sim_predictions):
    base_gap = base_predictions["goal_gap"]
    sim_gap = sim_predictions["goal_gap"]

    additional_gap = sim_gap - base_gap

    score = 100

    if additional_gap > 2000000:
        score -= 50
    elif additional_gap > 1000000:
        score -= 35
    elif additional_gap > 500000:
        score -= 20
    elif additional_gap > 0:
        score -= 10

    if sim_predictions["goal_status"] == "At Risk":
        score -= 20
    elif sim_predictions["goal_status"] == "Slightly Behind":
        score -= 10

    reasons = [
        f"Goal gap changes by ₹{additional_gap:,.0f}.",
        f"Goal status changes from {base_predictions['goal_status']} to {sim_predictions['goal_status']}."
    ]

    improvements = []
    if additional_gap > 0:
        improvements.append(
            "Increase SIP or delay the purchase to protect long-term goals.")
    else:
        improvements.append("Goal impact appears limited.")

    return {
        "score": round(clamp(score)),
        "reasons": reasons,
        "improvements": improvements
    }


def score_stability(base_twin, simulated_twin):
    sim_metrics = simulated_twin["metrics"]
    sim_predictions = simulated_twin["predictions"]

    score = 100

    if sim_predictions["financial_stress_risk"] == "High":
        score -= 50
    elif sim_predictions["financial_stress_risk"] == "Medium":
        score -= 25

    if sim_metrics["insurance_adequacy"] < 5:
        score -= 15

    if sim_metrics["savings_rate"] < 10:
        score -= 20

    reasons = [
        f"Financial stress risk after decision is {sim_predictions['financial_stress_risk']}.",
        f"Savings rate after decision is {sim_metrics['savings_rate']}%.",
        f"Insurance adequacy is {sim_metrics['insurance_adequacy']}x annual income."
    ]

    improvements = []
    if sim_predictions["financial_stress_risk"] != "Low":
        improvements.append("Reduce fixed obligations before proceeding.")
    if sim_metrics["insurance_adequacy"] < 5:
        improvements.append(
            "Improve protection cover for financial stability.")

    return {
        "score": round(clamp(score)),
        "reasons": reasons,
        "improvements": improvements or ["Stability impact is acceptable."]
    }


def generate_verdict(overall_score, component_scores):
    liquidity_score = component_scores["liquidity"]["score"]
    debt_score = component_scores["debt"]["score"]
    affordability_score = component_scores["affordability"]["score"]

    if overall_score >= 85 and liquidity_score >= 70 and debt_score >= 70:
        return "Affordable", "Low"

    if overall_score >= 72 and affordability_score >= 65:
        return "Affordable with Caution", "Moderate"

    if overall_score >= 60:
        return "Needs Planning", "High"

    if overall_score >= 45:
        return "High Risk", "Critical"

    return "Not Recommended", "Critical"


def build_decision_summary(asset, overall_score, verdict, scores):
    weakest = min(scores.items(), key=lambda item: item[1]["score"])
    strongest = max(scores.items(), key=lambda item: item[1]["score"])

    return {
        "headline": f"{asset.replace('_', ' ').title()} decision score is {overall_score}/100.",
        "verdict": verdict,
        "strongest_factor": strongest[0].replace("_", " ").title(),
        "weakest_factor": weakest[0].replace("_", " ").title(),
        "main_reason": weakest[1]["reasons"][0] if weakest[1]["reasons"] else "No major risk detected.",
        "recommended_action": weakest[1]["improvements"][0] if weakest[1]["improvements"] else "Proceed with regular review."
    }
