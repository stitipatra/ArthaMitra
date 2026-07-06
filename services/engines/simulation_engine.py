from copy import deepcopy
from services.financial_twin import build_financial_twin


EVENT_CONFIG = {
    "salary_increment": {"label": "Salary Increment", "description": "Increase monthly income."},
    "car_purchase": {"label": "Car Purchase", "description": "Down payment + EMI + running cost."},
    "home_purchase": {"label": "Home Purchase", "description": "Down payment + home loan EMI + maintenance."},
    "friend_financial_help": {"label": "Help a Friend", "description": "One-time financial help from savings."},
    "hospitalization": {"label": "Hospitalization", "description": "Medical expense + follow-up cost."},
    "child_birth": {"label": "Child Birth", "description": "One-time expense + recurring child cost."},
    "job_loss": {"label": "Job Loss", "description": "Temporary income loss."},
    "market_crash": {"label": "Market Crash", "description": "Equity portfolio decline."},
    "vacation": {"label": "Vacation", "description": "Large lifestyle expense."},
    "natural_disaster": {"label": "Natural Disaster", "description": "Emergency liquidity shock."},
}


def _refresh_histories(customer):
    customer["monthly_expense_history"][-1] = sum(
        customer["transactions"].values())
    customer["savings_balance_history"][-1] = customer["savings_balance"]
    customer["salary_history"][-1] = customer["monthly_income"]


def apply_event(customer, event_type, one_time_amount=0, monthly_emi=0, income_change=0, recurring_expense=0, market_fall_percent=25):
    updated = deepcopy(customer)
    updated["recent_life_event"] = event_type

    if event_type in ["car_purchase", "home_purchase"]:
        updated["savings_balance"] = max(
            0, updated["savings_balance"] - one_time_amount)
        updated["loan_emi"] += monthly_emi
        category = "vehicle_running_cost" if event_type == "car_purchase" else "home_maintenance"
        updated["transactions"][category] = updated["transactions"].get(
            category, 0) + recurring_expense

    elif event_type in ["friend_financial_help", "vacation", "natural_disaster"]:
        updated["savings_balance"] = max(
            0, updated["savings_balance"] - one_time_amount)

    elif event_type in ["hospitalization", "child_birth"]:
        updated["savings_balance"] = max(
            0, updated["savings_balance"] - one_time_amount)
        category = "medical_followup" if event_type == "hospitalization" else "child_expenses"
        updated["transactions"][category] = updated["transactions"].get(
            category, 0) + recurring_expense

    elif event_type == "salary_increment":
        updated["monthly_income"] = max(
            0, updated["monthly_income"] + income_change)

    elif event_type == "job_loss":
        updated["monthly_income"] = 0

    elif event_type == "market_crash":
        fall = market_fall_percent / 100
        for asset in ["mutual_funds", "stocks"]:
            if asset in updated["investments"]:
                updated["investments"][asset] = int(
                    updated["investments"][asset] * (1 - fall))

    _refresh_histories(updated)
    return updated


def simulate_event(customer, event_type, one_time_amount=0, monthly_emi=0, income_change=0, recurring_expense=0, market_fall_percent=25):
    simulated_customer = apply_event(
        customer,
        event_type,
        one_time_amount,
        monthly_emi,
        income_change,
        recurring_expense,
        market_fall_percent
    )

    base_twin = build_financial_twin(customer)
    simulated_twin = build_financial_twin(simulated_customer)

    return build_impact_result(event_type, base_twin, simulated_twin, simulated_customer)


def simulate_scenario_timeline(customer, events):
    timeline = []
    current_customer = deepcopy(customer)
    base_twin = build_financial_twin(customer)

    for index, event in enumerate(events, start=1):
        before_twin = build_financial_twin(current_customer)

        current_customer = apply_event(
            current_customer,
            event["event_type"],
            event.get("one_time_amount", 0),
            event.get("monthly_emi", 0),
            event.get("income_change", 0),
            event.get("recurring_expense", 0),
            event.get("market_fall_percent", 25)
        )

        after_twin = build_financial_twin(current_customer)

        timeline.append({
            "step": index,
            "event_type": event["event_type"],
            "event_label": EVENT_CONFIG[event["event_type"]]["label"],
            "before_score": before_twin["scores"]["overall"],
            "after_score": after_twin["scores"]["overall"],
            "score_change": after_twin["scores"]["overall"] - before_twin["scores"]["overall"],
            "net_worth_change": after_twin["metrics"]["net_worth"] - before_twin["metrics"]["net_worth"],
            "emergency_months": after_twin["metrics"]["emergency_months"],
            "goal_status": after_twin["predictions"]["goal_status"]
        })

    final_twin = build_financial_twin(current_customer)

    return {
        "base_twin": base_twin,
        "final_twin": final_twin,
        "final_customer": current_customer,
        "timeline": timeline,
        "total_impact": {
            "health_score_change": final_twin["scores"]["overall"] - base_twin["scores"]["overall"],
            "net_worth_change": final_twin["metrics"]["net_worth"] - base_twin["metrics"]["net_worth"],
            "emergency_months_change": round(final_twin["metrics"]["emergency_months"] - base_twin["metrics"]["emergency_months"], 1),
            "goal_gap_change": final_twin["predictions"]["goal_gap"] - base_twin["predictions"]["goal_gap"],
        }
    }


def build_impact_result(event_type, base_twin, simulated_twin, simulated_customer):
    health_change = simulated_twin["scores"]["overall"] - \
        base_twin["scores"]["overall"]
    emergency_change = round(
        simulated_twin["metrics"]["emergency_months"] - base_twin["metrics"]["emergency_months"], 1)
    goal_gap_change = simulated_twin["predictions"]["goal_gap"] - \
        base_twin["predictions"]["goal_gap"]

    if health_change <= -15 or simulated_twin["predictions"]["financial_stress_risk"] == "High":
        verdict = "Not Recommended"
        impact_level = "Critical"
    elif health_change <= -8 or emergency_change <= -2:
        verdict = "Delay or Proceed with Caution"
        impact_level = "High"
    elif health_change < 0 or goal_gap_change > 0:
        verdict = "Proceed with Caution"
        impact_level = "Moderate"
    else:
        verdict = "Proceed"
        impact_level = "Low"

    return {
        "event_type": event_type,
        "event_label": EVENT_CONFIG[event_type]["label"],
        "event_description": EVENT_CONFIG[event_type]["description"],
        "base_twin": base_twin,
        "simulated_twin": simulated_twin,
        "simulated_customer": simulated_customer,
        "impact_level": impact_level,
        "verdict": verdict,
        "impact": {
            "health_score_change": health_change,
            "net_worth_change": simulated_twin["metrics"]["net_worth"] - base_twin["metrics"]["net_worth"],
            "emergency_months_change": emergency_change,
            "savings_rate_change": round(simulated_twin["metrics"]["savings_rate"] - base_twin["metrics"]["savings_rate"], 2),
            "goal_gap_change": goal_gap_change,
            "stress_risk_before": base_twin["predictions"]["financial_stress_risk"],
            "stress_risk_after": simulated_twin["predictions"]["financial_stress_risk"],
            "goal_status_before": base_twin["predictions"]["goal_status"],
            "goal_status_after": simulated_twin["predictions"]["goal_status"]
        }
    }
