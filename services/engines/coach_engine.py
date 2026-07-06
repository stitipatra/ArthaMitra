import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


INTENT_EXAMPLES = {
    "car_affordability": [
        "Can I buy a car?",
        "Can I afford a car?",
        "Should I buy a vehicle?",
        "Is car loan affordable?",
        "Can I take auto loan?",
        "What happens if I buy a 15 lakh car?"
    ],
    "sip_advice": [
        "How much SIP should I do?",
        "Should I increase my SIP?",
        "How much should I invest monthly?",
        "Is my investment enough?",
        "What SIP is recommended?"
    ],
    "emergency_fund": [
        "Is my emergency fund enough?",
        "How much emergency fund do I need?",
        "Do I have enough savings for emergencies?",
        "What should my emergency corpus be?"
    ],
    "insurance_gap": [
        "Do I need more insurance?",
        "Is my life cover enough?",
        "What is my insurance gap?",
        "How much insurance should I have?"
    ],
    "goal_readiness": [
        "Am I on track for my goal?",
        "Will I reach my goal?",
        "Is my retirement goal on track?",
        "How much do I need for my goal?",
        "Will I miss my target?"
    ],
    "portfolio_advice": [
        "Is my portfolio good?",
        "How should I allocate investments?",
        "Should I invest in equity or debt?",
        "Is my portfolio diversified?",
        "What asset allocation is suitable?"
    ],
    "financial_summary": [
        "Summarize my finances",
        "How am I doing financially?",
        "Give me a financial summary",
        "What is my financial health?",
        "What should I focus on?"
    ],
    "life_event_help": [
        "What if I lose my job?",
        "What if I have a child?",
        "What if I help a friend with money?",
        "What if I get hospitalized?",
        "What if there is a medical emergency?"
    ]
}


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

    question_vector = vectors[-1]
    example_vectors = vectors[:-1]

    similarities = cosine_similarity(
        question_vector, example_vectors).flatten()

    best_index = similarities.argmax()
    best_score = similarities[best_index]

    if best_score < 0.18:
        return "financial_summary", round(float(best_score), 2)

    return labels[best_index], round(float(best_score), 2)


def extract_amount(question):
    text = question.lower().replace(",", "")

    lakh_match = re.search(r"(\d+(\.\d+)?)\s*(lakh|lakhs|lac|lacs)", text)
    if lakh_match:
        return int(float(lakh_match.group(1)) * 100000)

    crore_match = re.search(r"(\d+(\.\d+)?)\s*(crore|crores|cr)", text)
    if crore_match:
        return int(float(crore_match.group(1)) * 10000000)

    rupee_match = re.search(r"₹?\s*(\d{5,})", text)
    if rupee_match:
        return int(rupee_match.group(1))

    return None


def answer_financial_question(question, twin, report):
    intent, confidence = detect_intent(question)

    if intent == "car_affordability":
        return answer_car_affordability(question, twin, report, confidence)

    if intent == "sip_advice":
        return answer_sip_advice(twin, report, confidence)

    if intent == "emergency_fund":
        return answer_emergency_fund(twin, confidence)

    if intent == "insurance_gap":
        return answer_insurance_gap(twin, confidence)

    if intent == "goal_readiness":
        return answer_goal_readiness(report, confidence)

    if intent == "portfolio_advice":
        return answer_portfolio_advice(twin, confidence)

    if intent == "life_event_help":
        return answer_life_event_help(question, twin, confidence)

    return answer_financial_summary(twin, report, confidence)


def answer_car_affordability(question, twin, report, confidence):
    metrics = twin["metrics"]
    amount = extract_amount(question)

    if not amount:
        return (
            f"I can assess car affordability using your Financial Digital Twin.\n\n"
            f"Please mention the approximate car price, for example: "
            f"'Can I buy a 15 lakh car?'\n\n"
            f"Current context:\n"
            f"- Emergency fund: {metrics['emergency_months']} months\n"
            f"- Savings rate: {metrics['savings_rate']}%\n"
            f"- Debt-to-income ratio: {metrics['debt_to_income']}%\n"
            f"- Intent confidence: {confidence}"
        )

    estimated_down_payment = int(amount * 0.20)
    estimated_loan = amount - estimated_down_payment
    estimated_emi = int(estimated_loan * 0.022)

    new_debt_ratio = ((metrics["emi"] + estimated_emi) /
                      metrics["income"]) * 100 if metrics["income"] else 100
    remaining_savings = metrics["savings"] - estimated_down_payment
    emergency_after = remaining_savings / \
        metrics["expenses"] if metrics["expenses"] else 0

    if new_debt_ratio > 40 or emergency_after < 3:
        verdict = "Not recommended right now"
    elif new_debt_ratio > 30 or emergency_after < twin["recommendation_summary"]["emergency_target_months"]:
        verdict = "Proceed with caution"
    else:
        verdict = "Affordable"

    return (
        f"**Car Affordability Analysis**\n\n"
        f"Estimated car price: ₹{amount:,}\n"
        f"Assumed down payment: ₹{estimated_down_payment:,}\n"
        f"Estimated loan: ₹{estimated_loan:,}\n"
        f"Estimated EMI: ₹{estimated_emi:,}/month\n\n"
        f"Impact on your Financial Twin:\n"
        f"- Debt-to-income ratio may become {round(new_debt_ratio, 2)}%\n"
        f"- Emergency fund may reduce to {round(emergency_after, 1)} months\n"
        f"- Current goal status: {report['goal_analysis']['goal_status']}\n\n"
        f"**Verdict:** {verdict}\n\n"
        f"Intent confidence: {confidence}"
    )


def answer_sip_advice(twin, report, confidence):
    summary = twin["recommendation_summary"]
    goal = report["goal_analysis"]

    return (
        f"**SIP Recommendation**\n\n"
        f"Recommended SIP: ₹{summary['recommended_sip']:,}/month\n"
        f"Current SIP gap: ₹{summary['sip_gap']:,}/month\n\n"
        f"For your inflation-adjusted goal of ₹{goal['inflation_adjusted_value']:,}, "
        f"required SIP is ₹{goal['required_sip_inflated']:,}/month.\n\n"
        f"Primary focus: {report['executive_summary']['primary_focus']}\n"
        f"Intent confidence: {confidence}"
    )


def answer_emergency_fund(twin, confidence):
    metrics = twin["metrics"]
    summary = twin["recommendation_summary"]

    gap = max(0, summary["emergency_target_amount"] - metrics["savings"])

    return (
        f"**Emergency Fund Analysis**\n\n"
        f"Current emergency fund: {metrics['emergency_months']} months\n"
        f"Recommended target: {summary['emergency_target_months']} months\n"
        f"Target amount: ₹{summary['emergency_target_amount']:,}\n"
        f"Gap: ₹{gap:,}\n\n"
        f"Intent confidence: {confidence}"
    )


def answer_insurance_gap(twin, confidence):
    summary = twin["recommendation_summary"]

    return (
        f"**Insurance Gap Analysis**\n\n"
        f"Recommended cover: ₹{summary['insurance_target']:,}\n"
        f"Current insurance gap: ₹{summary['insurance_gap']:,}\n\n"
        f"If you have dependents, closing this gap should be prioritized before aggressive investing.\n"
        f"Intent confidence: {confidence}"
    )


def answer_goal_readiness(report, confidence):
    goal = report["goal_analysis"]

    return (
        f"**Goal Readiness**\n\n"
        f"Goal: {goal['goal'].replace('_', ' ').title()}\n"
        f"Today's value: ₹{goal['today_value']:,}\n"
        f"Inflation-adjusted value: ₹{goal['inflation_adjusted_value']:,}\n"
        f"Goal gap: ₹{goal['goal_gap']:,}\n"
        f"Goal status: {goal['goal_status']}\n\n"
        f"Required SIP: ₹{goal['required_sip_inflated']:,}/month\n"
        f"Intent confidence: {confidence}"
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
        f"Current allocation:\n"
        + "\n".join([f"- {asset.replace('_', ' ').title()}: {pct}%" for asset,
                    pct in allocation.items()])
        + f"\n\nFor your persona ({twin['persona']['type']}), portfolio allocation should balance liquidity, goal timeline and risk appetite.\n"
        f"Intent confidence: {confidence}"
    )


def answer_life_event_help(question, twin, confidence):
    return (
        f"**Life Event Planning**\n\n"
        f"ArthaMitra can simulate this using the Financial Digital Twin Simulator.\n\n"
        f"Current detected event: {twin['life_events']['label']}\n"
        f"Recommended actions:\n"
        + "\n".join([f"- {action}" for action in twin["life_events"]["actions"]])
        + f"\n\nIntent confidence: {confidence}"
    )


def answer_financial_summary(twin, report, confidence):
    summary = report["executive_summary"]

    return (
        f"**Financial Summary**\n\n"
        f"Health Score: {summary['health_score']}/100 ({summary['health_label']})\n"
        f"Persona: {report['customer']['persona']}\n"
        f"Net Worth: ₹{summary['net_worth']:,}\n"
        f"Savings Rate: {summary['savings_rate']}%\n"
        f"Stress Risk: {summary['stress_risk']}\n\n"
        f"Primary focus: {summary['primary_focus']}\n"
        f"Intent confidence: {confidence}"
    )
