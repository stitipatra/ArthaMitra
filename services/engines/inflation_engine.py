def future_value(amount, years, inflation_rate=0.06):
    return round(amount * ((1 + inflation_rate) ** years))


def required_sip_for_goal(goal_amount, years, annual_return=0.12):
    monthly_rate = annual_return / 12
    months = years * 12

    if months == 0:
        return goal_amount

    if monthly_rate == 0:
        return round(goal_amount / months)

    sip = goal_amount / \
        ((((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate))
    return round(sip)


def run_inflation_engine(twin):
    customer = twin["customer"]

    goal_amount_today = customer["goal_amount"]
    years = customer["goal_years"]

    inflation_adjusted_goal = future_value(goal_amount_today, years)

    twin["future_values"] = {
        "inflation_rate": 6,
        "goal_amount_today": goal_amount_today,
        "inflation_adjusted_goal": inflation_adjusted_goal,
        "required_sip_today_goal": required_sip_for_goal(goal_amount_today, years),
        "required_sip_inflated_goal": required_sip_for_goal(inflation_adjusted_goal, years)
    }

    return twin
