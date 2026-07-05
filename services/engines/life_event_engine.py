LIFE_EVENT_LIBRARY = {
    "salary_increment": {
        "label": "Salary Increment",
        "severity": "Low",
        "actions": [
            "Increase SIP allocation",
            "Review tax-saving investments",
            "Avoid lifestyle inflation"
        ],
        "affects": ["recommendation_engine", "prediction_engine"]
    },
    "job_loss": {
        "label": "Job Loss",
        "severity": "Critical",
        "actions": [
            "Pause non-essential investments temporarily",
            "Use emergency fund carefully",
            "Avoid new debt",
            "Prioritize essential expenses"
        ],
        "affects": ["financial_engine", "prediction_engine", "recommendation_engine"]
    },
    "child_birth": {
        "label": "Child Birth",
        "severity": "High",
        "actions": [
            "Create child education goal",
            "Increase insurance cover",
            "Increase emergency fund target",
            "Start long-term SIP for child expenses"
        ],
        "affects": ["inflation_engine", "recommendation_engine", "prediction_engine"]
    },
    "child_school_admission": {
        "label": "Child School Admission",
        "severity": "Medium",
        "actions": [
            "Prioritize child education goal",
            "Increase insurance cover",
            "Maintain higher emergency fund"
        ],
        "affects": ["recommendation_engine", "prediction_engine"]
    },
    "hospitalization": {
        "label": "Hospitalization",
        "severity": "Critical",
        "actions": [
            "Check health insurance coverage",
            "Preserve emergency fund",
            "Temporarily reduce discretionary spending",
            "Avoid redeeming long-term investments unless necessary"
        ],
        "affects": ["financial_engine", "recommendation_engine", "confidence_engine"]
    },
    "critical_illness": {
        "label": "Critical Illness",
        "severity": "Critical",
        "actions": [
            "Reassess health and life insurance",
            "Increase liquidity buffer",
            "Pause aggressive investing temporarily",
            "Review dependents' financial protection"
        ],
        "affects": ["financial_engine", "prediction_engine", "recommendation_engine"]
    },
    "natural_disaster": {
        "label": "Natural Disaster",
        "severity": "Critical",
        "actions": [
            "Prioritize immediate liquidity",
            "Check home, vehicle, and health insurance claims",
            "Avoid high-risk investments temporarily",
            "Rebuild emergency fund after recovery"
        ],
        "affects": ["financial_engine", "recommendation_engine", "prediction_engine"]
    },
    "friend_financial_help": {
        "label": "Friend Financial Help",
        "severity": "Medium",
        "actions": [
            "Evaluate help amount against emergency fund",
            "Avoid using high-interest debt to lend money",
            "Set a repayment expectation if lending",
            "Protect essential goals before helping others financially"
        ],
        "affects": ["simulation_engine", "recommendation_engine"]
    },
    "car_purchase": {
        "label": "Car Purchase",
        "severity": "Medium",
        "actions": [
            "Check EMI affordability",
            "Assess impact on savings rate",
            "Evaluate effect on goal timeline",
            "Avoid reducing emergency fund below target"
        ],
        "affects": ["simulation_engine", "prediction_engine", "recommendation_engine"]
    },
    "home_purchase": {
        "label": "Home Purchase",
        "severity": "High",
        "actions": [
            "Plan down payment",
            "Check EMI-to-income ratio",
            "Preserve emergency fund",
            "Review insurance and tax benefits"
        ],
        "affects": ["inflation_engine", "prediction_engine", "recommendation_engine"]
    },
    "business_income_volatility": {
        "label": "Business Income Volatility",
        "severity": "High",
        "actions": [
            "Maintain larger emergency fund",
            "Avoid overexposure to illiquid investments",
            "Prioritize cash flow stability"
        ],
        "affects": ["financial_engine", "prediction_engine", "recommendation_engine"]
    },
    "market_crash": {
        "label": "Market Crash",
        "severity": "Medium",
        "actions": [
            "Avoid panic selling",
            "Rebalance portfolio gradually",
            "Continue SIPs if emergency fund is healthy",
            "Review equity exposure based on risk profile"
        ],
        "affects": ["prediction_engine", "recommendation_engine"]
    },
    "festival_spending": {
        "label": "Festival Spending",
        "severity": "Low",
        "actions": [
            "Set a temporary spending budget",
            "Avoid credit card rollover",
            "Protect monthly SIP commitments"
        ],
        "affects": ["behaviour_engine", "recommendation_engine"]
    },
    "quick_financial_assessment": {
        "label": "Quick Financial Assessment",
        "severity": "Low",
        "actions": [
            "Validate estimated expenses",
            "Create first financial plan",
            "Track spending for 3 months"
        ],
        "affects": ["financial_engine", "recommendation_engine"]
    },
    "advanced_financial_assessment": {
        "label": "Advanced Financial Assessment",
        "severity": "Low",
        "actions": [
            "Review full financial profile",
            "Optimize portfolio allocation",
            "Generate detailed action plan"
        ],
        "affects": ["recommendation_engine", "report_engine"]
    }
}


def run_life_event_engine(twin):
    customer = twin["customer"]
    event_key = customer.get("recent_life_event", "quick_financial_assessment")

    event = LIFE_EVENT_LIBRARY.get(
        event_key,
        {
            "label": event_key.replace("_", " ").title(),
            "severity": "Low",
            "actions": ["Continue periodic financial review"],
            "affects": ["recommendation_engine"]
        }
    )

    twin["life_events"] = {
        "detected_event": event_key,
        "label": event["label"],
        "severity": event["severity"],
        "actions": event["actions"],
        "affects": event["affects"],
        "available_events": list(LIFE_EVENT_LIBRARY.keys())
    }

    return twin
