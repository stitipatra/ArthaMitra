def run_behaviour_engine(twin):
    metrics = twin["metrics"]
    customer = twin["customer"]

    signals = []

    if metrics["salary_growth"] > 8:
        signals.append("Salary growth detected")

    if metrics["expense_growth"] > 8:
        signals.append("Lifestyle inflation risk detected")

    if metrics["savings_growth"] > 15:
        signals.append("Strong savings discipline")

    dining = customer["transactions"].get("dining", 0)
    shopping = customer["transactions"].get("shopping", 0)

    if dining > metrics["income"] * 0.10:
        signals.append("Dining spend is elevated")

    if shopping > metrics["income"] * 0.12:
        signals.append("Shopping spend is elevated")

    if not signals:
        signals.append("Stable financial behaviour")

    twin["behaviour"] = {
        "signals": signals,
        "salary_growth": metrics["salary_growth"],
        "expense_growth": metrics["expense_growth"],
        "savings_growth": metrics["savings_growth"]
    }

    return twin
