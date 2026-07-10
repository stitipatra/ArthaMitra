def future_value_lumpsum(amount, annual_return, years):
    return amount * ((1 + annual_return) ** years)


def future_value_sip(monthly_sip, annual_return, years):
    monthly_return = annual_return / 12
    months = years * 12

    if monthly_return == 0:
        return monthly_sip * months

    return monthly_sip * (((1 + monthly_return) ** months - 1) / monthly_return)


def run_projection_engine(twin):
    customer = twin["customer"]
    metrics = twin["metrics"]

    years = customer["goal_years"]

    investments = customer["investments"]

    projection_assumptions = twin.get("projection_assumptions", {})

    assumptions = {
        "savings_interest": projection_assumptions.get("savings_interest", 0.035),
        "mutual_funds_cagr": projection_assumptions.get("mutual_funds_cagr", 0.12),
        "fixed_deposits_cagr": projection_assumptions.get("fixed_deposits_cagr", 0.065),
        "stocks_cagr": projection_assumptions.get("stocks_cagr", 0.10),
        "gold_cagr": projection_assumptions.get("gold_cagr", 0.07),
        "sip_cagr": projection_assumptions.get("sip_cagr", 0.12),
    }

    savings_future = future_value_lumpsum(
        metrics["savings"],
        assumptions["savings_interest"],
        years
    )

    mutual_funds_future = future_value_lumpsum(
        investments.get("mutual_funds", 0),
        assumptions["mutual_funds_cagr"],
        years
    )

    fixed_deposits_future = future_value_lumpsum(
        investments.get("fixed_deposits", 0),
        assumptions["fixed_deposits_cagr"],
        years
    )

    stocks_future = future_value_lumpsum(
        investments.get("stocks", 0),
        assumptions["stocks_cagr"],
        years
    )

    gold_future = future_value_lumpsum(
        investments.get("gold", 0),
        assumptions["gold_cagr"],
        years
    )

    sip_future = future_value_sip(
        customer["existing_sip"],
        assumptions["sip_cagr"],
        years
    )

    projected_assets = (
        savings_future
        + mutual_funds_future
        + fixed_deposits_future
        + stocks_future
        + gold_future
        + sip_future
    )

    projected_net_worth = projected_assets - metrics["credit_card_due"]

    current_assets = metrics["savings"] + metrics["investments"]

    growth_amount = projected_assets - current_assets
    growth_percent = (growth_amount / current_assets) * \
        100 if current_assets else 0

    goal_target = twin["future_values"]["inflation_adjusted_goal"]
    projected_goal_gap = max(0, goal_target - projected_assets)

    twin["projections"] = {
        "years": years,
        "assumptions": {
            "savings_interest_percent": assumptions["savings_interest"] * 100,
            "mutual_funds_cagr_percent": assumptions["mutual_funds_cagr"] * 100,
            "fixed_deposits_cagr_percent": assumptions["fixed_deposits_cagr"] * 100,
            "stocks_cagr_percent": assumptions["stocks_cagr"] * 100,
            "gold_cagr_percent": assumptions["gold_cagr"] * 100,
            "sip_cagr_percent": assumptions["sip_cagr"] * 100,
        },
        "projected_values": {
            "savings": round(savings_future),
            "mutual_funds": round(mutual_funds_future),
            "fixed_deposits": round(fixed_deposits_future),
            "stocks": round(stocks_future),
            "gold": round(gold_future),
            "sip_corpus": round(sip_future),
            "total_projected_assets": round(projected_assets),
            "projected_net_worth": round(projected_net_worth),
        },
        "growth": {
            "current_assets": round(current_assets),
            "growth_amount": round(growth_amount),
            "growth_percent": round(growth_percent, 2),
        },
        "goal_projection": {
            "inflation_adjusted_goal": round(goal_target),
            "projected_goal_gap": round(projected_goal_gap),
            "goal_covered_percent": round((projected_assets / goal_target) * 100, 2) if goal_target else 0,
        }
    }

    return twin
