def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def run_financial_engine(twin):
    customer = twin["customer"]

    income = customer["monthly_income"]
    expenses = sum(customer["transactions"].values())
    emi = customer["loan_emi"]
    savings = customer["savings_balance"]
    investments = sum(customer["investments"].values())
    credit_card_due = customer["credit_card_due"]

    disposable_income = income - expenses - emi
    net_worth = savings + investments - credit_card_due

    savings_rate = disposable_income / income if income else 0
    debt_to_income = emi / income if income else 0
    emergency_months = savings / expenses if expenses else 0
    investment_ratio = investments / max(savings + investments, 1)
    insurance_adequacy = customer["insurance_cover"] / \
        (income * 12) if income else 0
    goal_readiness = investments / \
        customer["goal_amount"] if customer["goal_amount"] else 0

    salary_history = customer["salary_history"]
    expense_history = customer["monthly_expense_history"]
    savings_history = customer["savings_balance_history"]

    salary_growth = (salary_history[-1] - salary_history[0]) / \
        salary_history[0] if salary_history[0] else 0
    expense_growth = (expense_history[-1] - expense_history[0]) / \
        expense_history[0] if expense_history[0] else 0
    savings_growth = (savings_history[-1] - savings_history[0]) / \
        savings_history[0] if savings_history[0] else 0

    savings_score = clamp(savings_rate * 250)
    emergency_score = clamp((emergency_months / 6) * 100)
    debt_score = clamp(100 - (debt_to_income * 200))
    insurance_score = clamp((insurance_adequacy / 10) * 100)
    investment_score = clamp(investment_ratio * 100)
    goal_score = clamp(goal_readiness * 200)
    cash_flow_score = 100 if disposable_income > 0 else 35
    behaviour_score = clamp(60 + savings_growth * 80 -
                            max(expense_growth, 0) * 40)

    overall = round(
        savings_score * 0.18
        + emergency_score * 0.16
        + debt_score * 0.14
        + insurance_score * 0.12
        + investment_score * 0.14
        + goal_score * 0.10
        + cash_flow_score * 0.10
        + behaviour_score * 0.06
    )

    label = "Excellent" if overall >= 80 else "Good" if overall >= 65 else "Moderate" if overall >= 50 else "Needs Attention"

    twin["metrics"] = {
        "income": income,
        "expenses": expenses,
        "emi": emi,
        "savings": savings,
        "investments": investments,
        "credit_card_due": credit_card_due,
        "disposable_income": disposable_income,
        "net_worth": net_worth,
        "savings_rate": round(savings_rate * 100, 2),
        "debt_to_income": round(debt_to_income * 100, 2),
        "emergency_months": round(emergency_months, 1),
        "investment_ratio": round(investment_ratio * 100, 2),
        "insurance_adequacy": round(insurance_adequacy, 2),
        "goal_readiness": round(goal_readiness * 100, 2),
        "salary_growth": round(salary_growth * 100, 2),
        "expense_growth": round(expense_growth * 100, 2),
        "savings_growth": round(savings_growth * 100, 2)
    }

    twin["scores"] = {
        "overall": overall,
        "label": label,
        "components": {
            "Savings": round(savings_score),
            "Emergency Fund": round(emergency_score),
            "Debt": round(debt_score),
            "Insurance": round(insurance_score),
            "Investments": round(investment_score),
            "Goal Readiness": round(goal_score),
            "Cash Flow": round(cash_flow_score),
            "Behaviour": round(behaviour_score)
        },
        "financial_dna": {
            "Financial Health": overall,
            "Investment Readiness": round((investment_score + cash_flow_score + savings_score) / 3),
            "Risk Stability": round((debt_score + emergency_score + insurance_score) / 3),
            "Goal Readiness": round(goal_score),
            "Behaviour Score": round(behaviour_score)
        }
    }

    return twin
