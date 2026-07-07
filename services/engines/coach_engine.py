import re
from copy import deepcopy

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from services.financial_twin import build_financial_twin
from services.engines.report_engine import build_financial_report
from services.engines.simulation_engine import simulate_event
from services.engines.decision_engine import evaluate_purchase_decision

ASSET_LIBRARY = {
    "house": {
        "keywords": ["house", "home", "flat", "apartment", "property", "villa", "land", "plot"],
        "event_type": "home_purchase",
        "down_payment_percent": 0.20,
        "emi_factor": 0.009,
        "monthly_cost_percent": 0.001,
        "default_monthly_cost": 10000,
    },
    "commercial_property": {
        "keywords": ["commercial property", "shop", "office space", "warehouse"],
        "event_type": "home_purchase",
        "down_payment_percent": 0.30,
        "emi_factor": 0.010,
        "monthly_cost_percent": 0.002,
        "default_monthly_cost": 15000,
    },
    "car": {
        "keywords": ["car", "vehicle", "fortuner", "bmw", "audi", "mercedes", "suv", "sedan", "hatchback", "ev", "tesla"],
        "event_type": "car_purchase",
        "down_payment_percent": 0.20,
        "emi_factor": 0.022,
        "monthly_cost_percent": 0.004,
        "default_monthly_cost": 5000,
    },
    "bike": {
        "keywords": ["bike", "motorcycle", "scooter", "activa", "royal enfield", "harley", "ktm"],
        "event_type": "car_purchase",
        "down_payment_percent": 0.15,
        "emi_factor": 0.028,
        "monthly_cost_percent": 0.003,
        "default_monthly_cost": 1500,
    },
    "phone": {
        "keywords": ["phone", "iphone", "mobile", "smartphone", "samsung", "pixel", "oneplus"],
        "event_type": "vacation",
        "down_payment_percent": 1.00,
        "emi_factor": 0.00,
        "monthly_cost_percent": 0.00,
        "default_monthly_cost": 0,
    },
    "laptop": {
        "keywords": ["laptop", "macbook", "pc", "computer", "gaming laptop", "desktop"],
        "event_type": "vacation",
        "down_payment_percent": 1.00,
        "emi_factor": 0.00,
        "monthly_cost_percent": 0.00,
        "default_monthly_cost": 0,
    },
    "electronics": {
        "keywords": ["tv", "television", "camera", "playstation", "ps5", "xbox", "tablet", "ipad", "drone"],
        "event_type": "vacation",
        "down_payment_percent": 1.00,
        "emi_factor": 0.00,
        "monthly_cost_percent": 0.00,
        "default_monthly_cost": 0,
    },
    "vacation": {
        "keywords": ["vacation", "trip", "travel", "europe", "dubai", "goa", "holiday", "honeymoon", "world tour"],
        "event_type": "vacation",
        "down_payment_percent": 1.00,
        "emi_factor": 0.00,
        "monthly_cost_percent": 0.00,
        "default_monthly_cost": 0,
    },
    "wedding": {
        "keywords": ["wedding", "marriage", "engagement", "wedding expenses"],
        "event_type": "vacation",
        "down_payment_percent": 1.00,
        "emi_factor": 0.00,
        "monthly_cost_percent": 0.00,
        "default_monthly_cost": 0,
    },
    "education": {
        "keywords": ["mba", "masters", "ms", "college", "education", "degree", "course", "certification", "upskilling"],
        "event_type": "vacation",
        "down_payment_percent": 1.00,
        "emi_factor": 0.00,
        "monthly_cost_percent": 0.00,
        "default_monthly_cost": 0,
    },
    "business": {
        "keywords": ["startup", "business", "franchise", "equipment", "machinery", "inventory"],
        "event_type": "vacation",
        "down_payment_percent": 1.00,
        "emi_factor": 0.00,
        "monthly_cost_percent": 0.01,
        "default_monthly_cost": 10000,
    },
    "friend_help": {
        "keywords": ["friend", "lend", "loan to friend", "help friend", "family help", "help family", "relative"],
        "event_type": "friend_financial_help",
        "down_payment_percent": 1.00,
        "emi_factor": 0.00,
        "monthly_cost_percent": 0.00,
        "default_monthly_cost": 0,
    },
    "medical": {
        "keywords": ["hospital", "surgery", "medical", "disease", "illness", "treatment", "cancer", "emergency"],
        "event_type": "hospitalization",
        "down_payment_percent": 1.00,
        "emi_factor": 0.00,
        "monthly_cost_percent": 0.02,
        "default_monthly_cost": 5000,
    },
    "renovation": {
        "keywords": ["renovation", "interior", "furniture", "home decor", "modular kitchen"],
        "event_type": "vacation",
        "down_payment_percent": 1.00,
        "emi_factor": 0.00,
        "monthly_cost_percent": 0.00,
        "default_monthly_cost": 0,
    },
    "jewellery": {
        "keywords": ["jewellery", "gold jewellery", "diamond", "watch", "luxury watch"],
        "event_type": "vacation",
        "down_payment_percent": 1.00,
        "emi_factor": 0.00,
        "monthly_cost_percent": 0.00,
        "default_monthly_cost": 0,
    },
}


INTENT_EXAMPLES = {
    "purchase_affordability": [
        "Can I buy a car?",
        "Can I afford a house?",
        "Should I buy an iphone?",
        "Can I buy a bike?",
        "Can I take a home loan?",
        "Can I afford a vacation?",
        "Can I spend 2 lakh on a laptop?",
        "Should I help my friend with money?",
        "Can I pay for surgery?",
        "Can I spend on wedding?",
        "Can I start a business?",
    ],
    "sip_advice": [
        "How much SIP should I do?",
        "Should I increase my SIP?",
        "How much should I invest monthly?",
        "What SIP is recommended?",
        "Should I invest more every month?",
    ],
    "emergency_fund": [
        "Is my emergency fund enough?",
        "How much emergency fund do I need?",
        "Do I have enough savings for emergencies?",
        "What emergency corpus should I keep?",
    ],
    "insurance_gap": [
        "Do I need more insurance?",
        "Is my life cover enough?",
        "What is my insurance gap?",
        "How much term insurance should I have?",
        "Do I need health insurance?",
    ],
    "goal_readiness": [
        "Am I on track for my goal?",
        "Will I reach my goal?",
        "Will I miss my target?",
        "How much do I need for my goal?",
        "Am I on track for retirement?",
    ],
    "portfolio_advice": [
        "Is my portfolio good?",
        "How should I allocate investments?",
        "Is my portfolio diversified?",
        "Should I invest in equity or debt?",
        "Should I invest in gold?",
        "Should I invest in FD?",
    ],
    "loan_advice": [
        "Should I prepay my loan?",
        "Should I take a personal loan?",
        "Is my EMI too high?",
        "Should I reduce debt?",
        "Loan vs SIP?",
    ],
    "tax_advice": [
        "How can I save tax?",
        "Should I invest in ELSS?",
        "Old regime or new regime?",
        "Should I use NPS?",
        "How to plan 80C?",
    ],
    "financial_summary": [
        "Summarize my finances",
        "How am I doing financially?",
        "Give me a financial summary",
        "What should I focus on?",
    ],
    "life_event_help": [
        "What if I lose my job?",
        "What if I have a child?",
        "What if I get hospitalized?",
        "What if market crashes?",
        "What if inflation increases?",
    ],
}


def assessment_reliability(decision_score):
    if decision_score >= 80:
        return "High"
    if decision_score >= 60:
        return "Medium"
    return "Needs Review"


def format_decision_explainability(decision):
    summary = decision["summary"]
    component_scores = decision["component_scores"]

    strongest_key = summary["strongest_factor"].lower().replace(" ", "_")
    weakest_key = summary["weakest_factor"].lower().replace(" ", "_")

    strongest = component_scores.get(strongest_key)
    weakest = component_scores.get(weakest_key)

    strongest_reason = strongest["reasons"][0] if strongest else "Strong supporting factor detected."
    weakest_reason = weakest["reasons"][0] if weakest else summary["main_reason"]

    weakest_improvement = (
        weakest["improvements"][0]
        if weakest and weakest["improvements"]
        else summary["recommended_action"]
    )

    return (
        f"\n\n**Why this score?**\n\n"
        f"✅ Strongest factor: **{summary['strongest_factor']}**\n"
        f"- {strongest_reason}\n\n"
        f"⚠️ Weakest factor: **{summary['weakest_factor']}**\n"
        f"- {weakest_reason}\n\n"
        f"**Recommended next step:** {weakest_improvement}"
    )


def detect_intent(question):
    corpus = []
    labels = []

    for intent, examples in INTENT_EXAMPLES.items():
        for example in examples:
            corpus.append(example)
            labels.append(intent)

    corpus.append(question)

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(corpus)

    similarities = cosine_similarity(vectors[-1], vectors[:-1]).flatten()
    best_index = similarities.argmax()
    best_score = float(similarities[best_index])

    if best_score < 0.16:
        return "financial_summary", round(best_score, 2)

    return labels[best_index], round(best_score, 2)


def extract_amount(question):
    text = question.lower().replace(",", "")

    crore = re.search(r"(\d+(\.\d+)?)\s*(crore|crores|cr)", text)
    if crore:
        return int(float(crore.group(1)) * 10000000)

    lakh = re.search(r"(\d+(\.\d+)?)\s*(lakh|lakhs|lac|lacs)", text)
    if lakh:
        return int(float(lakh.group(1)) * 100000)

    thousand = re.search(r"(\d+(\.\d+)?)\s*(k|thousand)", text)
    if thousand:
        return int(float(thousand.group(1)) * 1000)

    rupee = re.search(r"₹?\s*(\d{5,})", text)
    if rupee:
        return int(rupee.group(1))

    return None


def extract_monthly_income(question):
    text = question.lower().replace(",", "")

    lpa = re.search(
        r"(\d+(\.\d+)?)\s*(lpa|lakh per annum|lakhs per annum)", text)
    if lpa:
        return int(float(lpa.group(1)) * 100000 / 12)

    monthly = re.search(r"(\d+(\.\d+)?)\s*(per month|monthly|pm)", text)
    if monthly:
        return int(float(monthly.group(1)))

    return None


def detect_asset(question):
    text = question.lower()

    for asset, config in ASSET_LIBRARY.items():
        for keyword in config["keywords"]:
            if keyword in text:
                return asset

    return "generic_purchase"


def get_asset_config(asset):
    if asset in ASSET_LIBRARY:
        return ASSET_LIBRARY[asset]

    return {
        "keywords": [],
        "event_type": "vacation",
        "down_payment_percent": 1.00,
        "emi_factor": 0.00,
        "monthly_cost_percent": 0.00,
        "default_monthly_cost": 0,
    }


def answer_with_context(question, twin, report, chat_context=None):
    chat_context = chat_context or {}

    intent, confidence = detect_intent(question)
    amount = extract_amount(question)
    future_income = extract_monthly_income(question)
    asset = detect_asset(question)

    if future_income and chat_context.get("last_purchase"):
        return answer_purchase_with_future_income(twin, chat_context, future_income, confidence)

    if intent == "purchase_affordability" or amount:
        answer, chat_context = answer_purchase_affordability(
            twin, report, asset, amount, confidence, chat_context
        )
        return answer, chat_context

    if intent == "sip_advice":
        chat_context["last_topic"] = "sip_advice"
        return answer_sip_advice(twin, report, confidence), chat_context

    if intent == "emergency_fund":
        chat_context["last_topic"] = "emergency_fund"
        return answer_emergency_fund(twin, confidence), chat_context

    if intent == "insurance_gap":
        chat_context["last_topic"] = "insurance_gap"
        return answer_insurance_gap(twin, confidence), chat_context

    if intent == "goal_readiness":
        chat_context["last_topic"] = "goal_readiness"
        return answer_goal_readiness(report, confidence), chat_context

    if intent == "portfolio_advice":
        chat_context["last_topic"] = "portfolio_advice"
        return answer_portfolio_advice(twin, confidence), chat_context

    if intent == "loan_advice":
        chat_context["last_topic"] = "loan_advice"
        return answer_loan_advice(twin, confidence), chat_context

    if intent == "tax_advice":
        chat_context["last_topic"] = "tax_advice"
        return answer_tax_advice(twin, confidence), chat_context

    if intent == "life_event_help":
        chat_context["last_topic"] = "life_event_help"
        return answer_life_event_help(twin, confidence), chat_context

    return answer_financial_summary(twin, report, confidence), chat_context


def answer_purchase_affordability(twin, report, asset, amount, confidence, chat_context):
    metrics = twin["metrics"]

    if not amount:
        chat_context["last_purchase"] = {"asset": asset}
        return (
            f"I can assess this using your Financial Digital Twin.\n\n"
            f"I detected the asset as **{asset.replace('_', ' ').title()}**. "
            f"Please mention the approximate price, for example: "
            f"'Can I buy a 15 lakh car?' or 'Can I buy a 1 crore house?'\n\n"
            f"Current context:\n"
            f"- Health Score: {twin['scores']['overall']}/100\n"
            f"- Emergency Fund: {metrics['emergency_months']} months\n"
            f"- Savings Rate: {metrics['savings_rate']}%\n"
            f"- Debt-to-Income: {metrics['debt_to_income']}%\n",
            chat_context
        )

    result = run_generic_purchase_simulation(twin, asset, amount)

    chat_context["last_topic"] = "purchase_affordability"
    chat_context["last_purchase"] = {"asset": asset, "amount": amount}

    return format_purchase_answer(asset, amount, result, confidence), chat_context


def answer_purchase_with_future_income(twin, chat_context, future_income, confidence):
    last_purchase = chat_context["last_purchase"]
    asset = last_purchase.get("asset", "generic_purchase")
    amount = last_purchase.get("amount")

    if not amount:
        return "I understood your future income, but I still need the purchase amount.", chat_context

    updated_customer = deepcopy(twin["customer"])
    updated_customer["monthly_income"] = future_income
    updated_customer["salary_history"][-1] = future_income

    updated_twin = build_financial_twin(updated_customer)
    result = run_generic_purchase_simulation(updated_twin, asset, amount)

    answer = (
        f"Assuming your income becomes approximately **₹{future_income:,}/month**, "
        f"I re-ran the same **{asset.replace('_', ' ').title()}** affordability simulation.\n\n"
        + format_purchase_answer(asset, amount, result, confidence)
    )

    return answer, chat_context


def run_generic_purchase_simulation(twin, asset, amount):
    config = get_asset_config(asset)

    down_payment = int(amount * config["down_payment_percent"])
    financed_amount = max(0, amount - down_payment)
    estimated_emi = int(financed_amount * config["emi_factor"])
    recurring_cost = max(
        int(amount * config["monthly_cost_percent"]),
        config["default_monthly_cost"]
    )

    result = simulate_event(
        customer=twin["customer"],
        event_type=config["event_type"],
        one_time_amount=down_payment,
        monthly_emi=estimated_emi,
        recurring_expense=recurring_cost
    )

    result["purchase_assumptions"] = {
        "asset": asset,
        "price": amount,
        "down_payment": down_payment,
        "financed_amount": financed_amount,
        "estimated_emi": estimated_emi,
        "recurring_cost": recurring_cost,
    }

    decision = evaluate_purchase_decision(
        base_twin=result["base_twin"],
        simulated_twin=result["simulated_twin"],
        asset=asset,
        purchase_amount=amount,
        down_payment=down_payment,
        estimated_emi=estimated_emi,
        recurring_cost=recurring_cost,
    )

    result["decision"] = decision

    return result


def format_purchase_answer(asset, amount, result, confidence):
    a = result["purchase_assumptions"]
    impact = result["impact"]
    sim = result["simulated_twin"]

    return (
        f"**{asset.replace('_', ' ').title()} Affordability Simulation**\n\n"
        f"Price considered: ₹{amount:,}\n\n"
        f"Assumptions:\n"
        f"- Upfront/down payment: ₹{a['down_payment']:,}\n"
        f"- Financed amount: ₹{a['financed_amount']:,}\n"
        f"- Estimated EMI: ₹{a['estimated_emi']:,}/month\n"
        f"- Additional monthly cost: ₹{a['recurring_cost']:,}/month\n\n"
        f"Before vs After:\n"
        f"- Health Score: {result['base_twin']['scores']['overall']} → {sim['scores']['overall']}\n"
        f"- Net Worth Change: ₹{impact['net_worth_change']:,}\n"
        f"- Emergency Fund: {result['base_twin']['metrics']['emergency_months']} months → {sim['metrics']['emergency_months']} months\n"
        f"- Goal Status: {impact['goal_status_before']} → {impact['goal_status_after']}\n"
        f"- Stress Risk: {impact['stress_risk_before']} → {impact['stress_risk_after']}\n\n"
        f"Decision Score: {result['decision']['overall_score']}/100\n"
        f"**Verdict:** {result['decision']['verdict']}\n"
        f"Impact Level: {result['decision']['impact_level']}\n"
        f"Assessment Reliability: {assessment_reliability(result['decision']['overall_score'])}"
        + format_decision_explainability(result["decision"])
    )


def answer_sip_advice(twin, report, confidence):
    summary = twin["recommendation_summary"]
    goal = report["goal_analysis"]

    return (
        f"**SIP Recommendation**\n\n"
        f"Recommended SIP: ₹{summary['recommended_sip']:,}/month\n"
        f"Current SIP gap: ₹{summary['sip_gap']:,}/month\n"
        f"Required SIP for goal: ₹{goal['required_sip_inflated']:,}/month\n"
        f"Primary focus: {report['executive_summary']['primary_focus']}\n"
    )


def answer_emergency_fund(twin, confidence):
    m = twin["metrics"]
    s = twin["recommendation_summary"]
    gap = max(0, s["emergency_target_amount"] - m["savings"])

    return (
        f"**Emergency Fund Analysis**\n\n"
        f"Current: {m['emergency_months']} months\n"
        f"Recommended: {s['emergency_target_months']} months\n"
        f"Target amount: ₹{s['emergency_target_amount']:,}\n"
        f"Gap: ₹{gap:,}\n"
    )


def answer_insurance_gap(twin, confidence):
    s = twin["recommendation_summary"]

    return (
        f"**Insurance Gap Analysis**\n\n"
        f"Recommended cover: ₹{s['insurance_target']:,}\n"
        f"Current gap: ₹{s['insurance_gap']:,}\n"
    )


def answer_goal_readiness(report, confidence):
    g = report["goal_analysis"]

    return (
        f"**Goal Readiness**\n\n"
        f"Goal: {g['goal'].replace('_', ' ').title()}\n"
        f"Inflation-adjusted value: ₹{g['inflation_adjusted_value']:,}\n"
        f"Required SIP: ₹{g['required_sip_inflated']:,}/month\n"
        f"Goal gap: ₹{g['goal_gap']:,}\n"
        f"Status: {g['goal_status']}\n"
    )


def answer_portfolio_advice(twin, confidence):
    investments = twin["customer"]["investments"]
    total = sum(investments.values()) or 1

    allocation = {
        asset: round((value / total) * 100, 1)
        for asset, value in investments.items()
    }

    return (
        f"**Portfolio Snapshot**\n\n"
        + "\n".join([f"- {asset.replace('_', ' ').title()}: {pct}%" for asset,
                    pct in allocation.items()])
        + f"\n\nPersona: {twin['persona']['type']}\n"
    )


def answer_loan_advice(twin, confidence):
    m = twin["metrics"]

    if m["debt_to_income"] > 35:
        verdict = "Your debt burden is high. Avoid new loans and prioritize repayment."
    elif m["debt_to_income"] > 20:
        verdict = "You can manage current debt, but new EMIs should be taken carefully."
    else:
        verdict = "Your current debt burden is manageable."

    return (
        f"**Loan Advisory**\n\n"
        f"Debt-to-income ratio: {m['debt_to_income']}%\n"
        f"Current EMI: ₹{m['emi']:,}/month\n"
        f"{verdict}\n"
    )


def answer_tax_advice(twin, confidence):
    m = twin["metrics"]

    return (
        f"**Tax Planning Guidance**\n\n"
        f"Based on monthly income of ₹{m['income']:,}, ArthaMitra recommends reviewing:\n"
        f"- ELSS / 80C options\n"
        f"- NPS if retirement planning is a priority\n"
        f"- HRA or home loan benefits if applicable\n"
        f"- Capital gains impact before large redemptions\n\n"
        f"This is a planning prompt, not tax filing advice.\n"
    )


def answer_life_event_help(twin, confidence):
    return (
        f"**Life Event Planning**\n\n"
        f"Detected event: {twin['life_events']['label']}\n"
        f"Recommended actions:\n"
        + "\n".join([f"- {action}" for action in twin["life_events"]["actions"]])
    )


def answer_financial_summary(twin, report, confidence):
    s = report["executive_summary"]

    return (
        f"**Financial Summary**\n\n"
        f"Health Score: {s['health_score']}/100 ({s['health_label']})\n"
        f"Persona: {report['customer']['persona']}\n"
        f"Net Worth: ₹{s['net_worth']:,}\n"
        f"Savings Rate: {s['savings_rate']}%\n"
        f"Stress Risk: {s['stress_risk']}\n\n"
        f"Primary focus: {s['primary_focus']}\n"
    )
