from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from datetime import datetime
import os


def build_financial_report(twin):
    customer = twin["customer"]
    metrics = twin["metrics"]
    scores = twin["scores"]
    future = twin["future_values"]
    predictions = twin["predictions"]

    report = {
        "customer": {
            "name": customer["name"],
            "age": customer["age"],
            "city": customer["city"],
            "occupation": customer["occupation"],
            "persona": twin["persona"]["type"],
        },
        "executive_summary": {
            "health_score": scores["overall"],
            "health_label": scores["label"],
            "net_worth": metrics["net_worth"],
            "savings_rate": metrics["savings_rate"],
            "stress_risk": predictions["financial_stress_risk"],
            "goal_status": predictions["goal_status"],
            "primary_focus": get_primary_focus(twin),
        },
        "financial_dna": scores["financial_dna"],
        "metrics": metrics,
        "goal_analysis": {
            "goal": customer["investment_goal"],
            "today_value": future["goal_amount_today"],
            "inflation_adjusted_value": future["inflation_adjusted_goal"],
            "required_sip_today": future["required_sip_today_goal"],
            "required_sip_inflated": future["required_sip_inflated_goal"],
            "goal_gap": predictions["goal_gap"],
            "goal_status": predictions["goal_status"],
        },
        "behaviour": twin["behaviour"],
        "life_events": twin["life_events"],
        "recommendations": twin["recommendations"],
        "action_plan": build_action_plan(twin),
    }

    return report


def get_primary_focus(twin):
    metrics = twin["metrics"]
    summary = twin["recommendation_summary"]
    predictions = twin["predictions"]

    if metrics["emergency_months"] < summary["emergency_target_months"]:
        return "Build emergency fund before taking more investment risk."

    if summary["insurance_gap"] > 0:
        return "Improve protection by increasing insurance coverage."

    if predictions["goal_status"] != "On Track":
        return "Increase goal-focused investments to close the future shortfall."

    if metrics["savings_rate"] < 15:
        return "Improve monthly savings rate by reducing discretionary expenses."

    return "Continue disciplined investing and review portfolio allocation quarterly."


def build_action_plan(twin):
    summary = twin["recommendation_summary"]

    return {
        "next_30_days": [
            "Validate income, expense and investment data.",
            f"Set emergency fund target to {summary['emergency_target_months']} months of expenses.",
            "Avoid unnecessary high-interest debt.",
        ],
        "next_90_days": [
            f"Move towards recommended SIP of ₹{summary['recommended_sip']:,}/month.",
            "Review insurance cover and close protection gaps.",
            "Track savings rate and discretionary spending trends.",
        ],
        "next_12_months": [
            "Rebalance portfolio based on risk profile and goal timeline.",
            "Review inflation-adjusted goals every quarter.",
            "Regenerate ArthaMitra report after major life events.",
        ],
    }


def export_report_pdf(report):
    os.makedirs("reports", exist_ok=True)

    file_name = f"arthamitra_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join("reports", file_name)

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(
        Paragraph("ArthaMitra Financial Wealth Report", styles["Title"]))
    story.append(Spacer(1, 12))

    customer = report["customer"]
    summary = report["executive_summary"]

    story.append(
        Paragraph(f"Customer: {customer['name']}", styles["Heading2"]))
    story.append(
        Paragraph(f"Persona: {customer['persona']}", styles["Normal"]))
    story.append(Spacer(1, 12))

    summary_data = [
        ["Metric", "Value"],
        ["Health Score", f"{summary['health_score']}/100"],
        ["Health Label", summary["health_label"]],
        ["Net Worth", f"₹{summary['net_worth']:,}"],
        ["Savings Rate", f"{summary['savings_rate']}%"],
        ["Stress Risk", summary["stress_risk"]],
        ["Goal Status", summary["goal_status"]],
        ["Primary Focus", summary["primary_focus"]],
    ]

    story.append(_pdf_table(summary_data))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Financial DNA", styles["Heading2"]))

    dna_data = [["Dimension", "Score"]]
    for key, value in report["financial_dna"].items():
        dna_data.append([key, f"{value}/100"])

    story.append(_pdf_table(dna_data))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Goal Analysis", styles["Heading2"]))
    goal = report["goal_analysis"]

    goal_data = [
        ["Goal", goal["goal"].replace("_", " ").title()],
        ["Today's Value", f"₹{goal['today_value']:,}"],
        ["Inflation Adjusted Value", f"₹{goal['inflation_adjusted_value']:,}"],
        ["Required SIP", f"₹{goal['required_sip_inflated']:,}/month"],
        ["Goal Gap", f"₹{goal['goal_gap']:,}"],
        ["Goal Status", goal["goal_status"]],
    ]

    story.append(_pdf_table(goal_data))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Recommendations", styles["Heading2"]))

    reco_data = [["Category", "Recommendation", "Confidence"]]
    for rec in report["recommendations"]:
        reco_data.append([
            rec["category"],
            f"{rec['title']} - {rec['detail']}",
            f"{rec['confidence']}%"
        ])

    story.append(_pdf_table(reco_data))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Action Plan", styles["Heading2"]))

    for phase, actions in report["action_plan"].items():
        story.append(Paragraph(phase.replace(
            "_", " ").title(), styles["Heading3"]))
        for action in actions:
            story.append(Paragraph(f"• {action}", styles["Normal"]))
        story.append(Spacer(1, 8))

    doc.build(story)

    return file_path


def _pdf_table(data):
    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCFCE7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    return table
