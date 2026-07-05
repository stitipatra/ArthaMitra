def run_persona_engine(twin):
    customer = twin["customer"]
    metrics = twin["metrics"]

    age = customer["age"]
    income = metrics["income"]
    savings_rate = metrics["savings_rate"]
    debt = metrics["debt_to_income"]
    goal = customer["investment_goal"]
    life_stage = customer["life_stage"]

    if "entrepreneur" in life_stage:
        persona = "Entrepreneurial Wealth Builder"
    elif goal == "early_retirement":
        persona = "FIRE Seeker"
    elif goal == "child_education":
        persona = "Family Planner"
    elif debt > 35:
        persona = "Debt Heavy Planner"
    elif income >= 200000:
        persona = "High Income Optimizer"
    elif age <= 30 and savings_rate >= 20:
        persona = "Young Wealth Builder"
    elif savings_rate < 10:
        persona = "Cash Flow Constrained"
    else:
        persona = "Balanced Investor"

    twin["persona"] = {
        "type": persona,
        "summary": f"{persona} profile based on income, age, goal, debt and cash flow."
    }

    return twin
