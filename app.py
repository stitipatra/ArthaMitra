import streamlit as st
import pandas as pd
import plotly.express as px

from utils.helpers import load_customers, format_currency
from services.financial_twin import build_financial_twin
from services.engines.prediction_engine import simulate_sip
from services.engines.simulation_engine import (
    simulate_event,
    simulate_scenario_timeline,
    EVENT_CONFIG
)
from services.engines.report_engine import build_financial_report, export_report_pdf
from services.engines.coach_engine import answer_with_context

st.set_page_config(
    page_title="ArthaMitra",
    page_icon="💰",
    layout="wide"
)

st.title("💰 ArthaMitra")
st.caption(
    "Your AI Financial Relationship Manager — powered by a Financial Digital Twin")

customers = load_customers()

if "current_customer" not in st.session_state:
    st.session_state.current_customer = customers[0]
    st.session_state.current_customer_source = "Demo Customer"


if "elite_unlocked" not in st.session_state:
    st.session_state.elite_unlocked = False


st.sidebar.markdown("## ArthaMitra")
st.sidebar.caption("AI Financial Relationship Manager")

mode = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Demo Customer",
        "⚡ Quick Assessment",
        "👑 ArthaMitra Elite",
        "📄 AI Wealth Report",
        "🤖 AI Wealth Coach"
    ]
)

elite_locked_pages = ["📄 AI Wealth Report", "🤖 AI Wealth Coach"]

if mode in elite_locked_pages and not st.session_state.elite_unlocked:
    st.warning("🔒 This feature is available with ArthaMitra Elite.")
    st.info("Unlock Elite access from the sidebar to continue.")
    st.stop()


def estimate_quick_profile(
    name,
    age,
    city,
    occupation,
    monthly_income,
    savings_balance,
    existing_investments,
    loan_emi,
    financial_goal,
    goal_amount,
    goal_years,
    risk_preference,
    life_event
):
    city_rent_factor = {
        "Bengaluru": 0.26,
        "Mumbai": 0.32,
        "Delhi": 0.27,
        "Hyderabad": 0.24,
        "Pune": 0.23,
        "Chennai": 0.22,
        "Other": 0.20
    }

    rent = int(monthly_income * city_rent_factor.get(city, 0.22))
    groceries = int(monthly_income * 0.10)
    dining = int(monthly_income * 0.08)
    shopping = int(monthly_income * 0.07)
    travel = int(monthly_income * 0.05)
    utilities = int(monthly_income * 0.04)

    mutual_funds = int(existing_investments * 0.45)
    fixed_deposits = int(existing_investments * 0.30)
    stocks = int(existing_investments * 0.15)
    gold = int(existing_investments * 0.10)

    insurance_cover = int(monthly_income * 12 * 5)

    monthly_expense = rent + groceries + dining + shopping + travel + utilities

    return {
        "customer_id": f"QUICK_{name}_{age}_{monthly_income}_{savings_balance}_{goal_amount}",
        "name": name,
        "age": age,
        "city": city,
        "occupation": occupation,
        "life_stage": "quick_assessment_user",
        "monthly_income": monthly_income,
        "salary_history": [
            int(monthly_income * 0.92),
            int(monthly_income * 0.94),
            int(monthly_income * 0.96),
            int(monthly_income * 0.98),
            monthly_income,
            monthly_income
        ],
        "monthly_expense_history": [monthly_expense] * 6,
        "savings_balance": savings_balance,
        "savings_balance_history": [
            int(savings_balance * 0.75),
            int(savings_balance * 0.80),
            int(savings_balance * 0.85),
            int(savings_balance * 0.90),
            int(savings_balance * 0.95),
            savings_balance
        ],
        "existing_sip": int(monthly_income * 0.05),
        "loan_emi": loan_emi,
        "credit_card_due": int(monthly_income * 0.10),
        "insurance_cover": insurance_cover,
        "risk_preference": risk_preference,
        "investment_goal": financial_goal,
        "goal_amount": goal_amount,
        "goal_years": goal_years,
        "recent_life_event": life_event,
        "transactions": {
            "rent": rent,
            "groceries": groceries,
            "dining": dining,
            "shopping": shopping,
            "travel": travel,
            "utilities": utilities
        },
        "investments": {
            "mutual_funds": mutual_funds,
            "fixed_deposits": fixed_deposits,
            "stocks": stocks,
            "gold": gold
        }
    }


if mode == "👑 ArthaMitra Elite":
    st.title("👑 ArthaMitra Elite")
    st.caption(
        "Advanced AI-powered financial intelligence for priority banking customers")

    if not st.session_state.elite_unlocked:
        st.markdown("""
        ### 🔒 Unlock Elite Access

        Get access to:

        - 📄 AI Wealth Report Generator
        - 🤖 AI Wealth Coach
        - 📊 Advanced Portfolio Intelligence
        - 💰 Tax Planning Insights
        - 🛡 Insurance Gap Detection
        - 📈 Retirement & Goal Simulation
        """)

        access_code = st.text_input("Enter Elite Access Code", type="password")

        if st.button("Unlock Elite Experience"):
            if access_code == "ARTHA2026":
                st.session_state.elite_unlocked = True
                st.success(
                    "✅ Elite Access Activated. Welcome to ArthaMitra Elite.")
                st.rerun()
            else:
                st.error("Invalid access code. Demo code: ARTHA2026")

        st.stop()

    st.success("✅ ArthaMitra Elite is active.")

    st.markdown("""
    ### Elite Services Enabled

    - AI Wealth Report
    - AI Wealth Coach
    - Portfolio Optimization
    - Insurance Advisory
    - Tax Planning
    - Goal Intelligence
    """)

    if st.button("Lock Elite Access"):
        st.session_state.elite_unlocked = False
        st.rerun()

    st.stop()


if mode == "🏠 Demo Customer":
    customer_names = [customer["name"] for customer in customers]
    selected_name = st.sidebar.selectbox("Select Customer", customer_names)
    customer = next(c for c in customers if c["name"] == selected_name)

    st.session_state.current_customer = customer
    st.session_state.current_customer_source = "Demo Customer"

    st.sidebar.info(
        f"Active profile switched to demo customer: {customer['name']}."
    )

elif mode == "⚡ Quick Assessment":
    st.sidebar.markdown("### Quick Financial Assessment")

    name = st.sidebar.text_input("Name", "Demo User")
    age = st.sidebar.number_input("Age", 18, 70, 26)

    city = st.sidebar.selectbox(
        "City",
        ["Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Pune", "Chennai", "Other"]
    )

    occupation = st.sidebar.text_input("Occupation", "Software Engineer")

    monthly_income = st.sidebar.number_input(
        "Monthly Income",
        min_value=10000,
        max_value=1000000,
        value=85000,
        step=5000
    )

    savings_balance = st.sidebar.number_input(
        "Current Savings Balance",
        min_value=0,
        max_value=10000000,
        value=250000,
        step=10000
    )

    existing_investments = st.sidebar.number_input(
        "Existing Investments",
        min_value=0,
        max_value=50000000,
        value=250000,
        step=10000
    )

    loan_emi = st.sidebar.number_input(
        "Monthly Loan EMI",
        min_value=0,
        max_value=500000,
        value=0,
        step=1000
    )

    financial_goal = st.sidebar.selectbox(
        "Financial Goal",
        [
            "wealth_creation",
            "child_education",
            "home_purchase",
            "early_retirement",
            "emergency_fund"
        ]
    )

    goal_amount = st.sidebar.number_input(
        "Goal Amount",
        min_value=100000,
        max_value=100000000,
        value=2500000,
        step=100000
    )

    goal_years = st.sidebar.number_input(
        "Goal Timeline in Years",
        min_value=1,
        max_value=40,
        value=7
    )

    risk_preference = st.sidebar.selectbox(
        "Risk Preference",
        ["conservative", "moderate", "aggressive"],
        index=1
    )

    life_event = st.sidebar.selectbox(
        "Recent Life Event",
        [
            "quick_financial_assessment",
            "salary_increment",
            "job_loss",
            "child_birth",
            "child_school_admission",
            "hospitalization",
            "critical_illness",
            "natural_disaster",
            "friend_financial_help",
            "car_purchase",
            "home_purchase",
            "business_income_volatility",
            "market_crash",
            "festival_spending"
        ]
    )

    customer = estimate_quick_profile(
        name,
        age,
        city,
        occupation,
        monthly_income,
        savings_balance,
        existing_investments,
        loan_emi,
        financial_goal,
        goal_amount,
        goal_years,
        risk_preference,
        life_event
    )

    st.session_state.current_customer = customer
    st.session_state.current_customer_source = "Quick Assessment"

    st.sidebar.success(
        f"Active profile set to {customer['name']}. "
        "Open AI Wealth Report or AI Wealth Coach to use this profile."
    )

elif mode == "📄 AI Wealth Report":
    st.title("📄 AI Wealth Report")
    st.caption(
        "Structured financial intelligence generated from the Financial Digital Twin.")

    report_customer = st.session_state.current_customer

    st.info(
        f"Generating report for **{report_customer['name']}** "
        f"from **{st.session_state.current_customer_source}**."
    )

    report_twin = build_financial_twin(report_customer)

    report = build_financial_report(report_twin)

    st.subheader("Executive Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Health Score",
        f"{report['executive_summary']['health_score']}/100",
        report["executive_summary"]["health_label"]
    )

    col2.metric(
        "Goal Status",
        report["executive_summary"]["goal_status"]
    )

    col3.metric(
        "Stress Risk",
        report["executive_summary"]["stress_risk"]
    )

    st.info(
        f"**Primary Focus:** {report['executive_summary']['primary_focus']}")

    st.subheader("Financial DNA")

    dna_df = pd.DataFrame({
        "Dimension": report["financial_dna"].keys(),
        "Score": report["financial_dna"].values()
    })

    fig = px.bar(dna_df, x="Dimension", y="Score",
                 text="Score", range_y=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Goal Analysis")

    goal = report["goal_analysis"]

    st.write(
        f"Goal: **{goal['goal'].replace('_', ' ').title()}**"
    )

    g1, g2, g3 = st.columns(3)

    g1.metric("Today's Goal Value", format_currency(goal["today_value"]))
    g2.metric("Inflation Adjusted Value", format_currency(
        goal["inflation_adjusted_value"]))
    g3.metric("Goal Gap", format_currency(goal["goal_gap"]))

    st.write(
        f"Required SIP for inflation-adjusted goal: "
        f"**{format_currency(goal['required_sip_inflated'])}/month**"
    )

    st.subheader("Recommendations")

    for rec in report["recommendations"]:
        st.success(
            f"**{rec['title']}**\n\n"
            f"{rec['detail']}\n\n"
            f"Impact: {rec['impact']}\n\n"
            f"Confidence: {rec['confidence']}%"
        )

    st.subheader("90-Day Action Plan")

    for phase, actions in report["action_plan"].items():
        st.markdown(f"### {phase.replace('_', ' ').title()}")
        for action in actions:
            st.write(f"- {action}")

    st.stop()

elif mode == "🤖 AI Wealth Coach":
    st.title("🤖 AI Wealth Coach")
    st.caption("Ask questions grounded in the Financial Digital Twin.")

    st.info(
        """
        🧠 **AI Explanation Mode**

        • Financial calculations are performed by **ArthaMitra's Financial Digital Twin**.

        • Recommendations are generated by our deterministic **Decision Engine**.

        • AI is used only to explain insights in natural language.

        • Every recommendation is transparent, explainable, and grounded in your financial data.
        """
    )

    if "coach_sessions" not in st.session_state:
        st.session_state.coach_sessions = {}

    coach_customer = st.session_state.current_customer

    active_customer_key = coach_customer["customer_id"]

    if active_customer_key not in st.session_state.coach_sessions:
        st.session_state.coach_sessions[active_customer_key] = {
            "messages": [],
            "context": {}
        }

    current_chat = st.session_state.coach_sessions[active_customer_key]

    st.info(
        f"Coaching **{coach_customer['name']}** "
        f"from **{st.session_state.current_customer_source}** profile."
    )

    coach_twin = build_financial_twin(coach_customer)
    coach_report = build_financial_report(coach_twin)

    col1, col2, col3 = st.columns(3)
    col1.metric("Health Score", f"{coach_twin['scores']['overall']}/100")
    col2.metric("Persona", coach_twin["persona"]["type"])
    col3.metric("Goal Status", coach_twin["predictions"]["goal_status"])

    st.markdown("### Conversation")

    for msg in current_chat["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

    question = st.chat_input(
        "Ask ArthaMitra something like: Can I buy a 15 lakh car?")

    if question:
        current_chat["messages"].append({
            "role": "user",
            "content": question
        })

        answer, updated_context = answer_with_context(
            question,
            coach_twin,
            coach_report,
            current_chat["context"]
        )

        current_chat["context"] = updated_context

        current_chat["messages"].append({
            "role": "assistant",
            "content": answer
        })

        st.rerun()

    if st.button("Clear Coach Conversation"):
        current_chat["messages"] = []
        current_chat["context"] = {}
        st.rerun()

    st.stop()


twin = build_financial_twin(customer)

features = twin["metrics"]
component_scores = twin["scores"]["components"]
financial_dna = twin["scores"]["financial_dna"]
overall_score = twin["scores"]["overall"]
health_label = twin["scores"]["label"]
risk_profile = twin["persona"]["type"]
recommendation_summary = twin["recommendation_summary"]
current_report = build_financial_report(twin)


st.sidebar.markdown("### Customer Profile")
st.sidebar.write(f"**Name:** {customer['name']}")
st.sidebar.write(f"**Age:** {customer['age']}")
st.sidebar.write(f"**City:** {customer['city']}")
st.sidebar.write(f"**Occupation:** {customer['occupation']}")
st.sidebar.write(
    f"**Life Stage:** {customer['life_stage'].replace('_', ' ').title()}")
st.sidebar.write(f"**Life Event:** {twin['life_events']['label']}")


col1, col2, col3, col4 = st.columns([1, 1.7, 1.2, 1.2])

col1.metric("Health Score", f"{overall_score}/100", health_label)
with col2:
    st.markdown(
        """
        <div style="
            font-size:16px;
            color:#111827;
            margin-bottom:6px;
        ">
            Financial Persona
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="
            background:#E8F8EF;
            border:1px solid #D0EEDB;
            border-radius:12px;
            padding:8px 16px;
            height:48px;
            display:flex;
            align-items:center;
            gap:14px;
            white-space:nowrap;
            margin-top:-2px;
        ">
            <span style="font-size:22px;">👤</span>
            <span style="
                font-size:19px;
                font-weight:600;
                color:#15803D;
            ">
                {risk_profile}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
col3.metric("Net Worth", format_currency(features["net_worth"]))
col4.metric("Savings Rate", f"{features['savings_rate']}%")


st.divider()

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Financial Snapshot")

    snapshot_df = pd.DataFrame({
        "Metric": [
            "Monthly Income",
            "Monthly Expenses",
            "Loan EMI",
            "Credit Card Due",
            "Savings Balance",
            "Total Investments",
            "Disposable Income"
        ],
        "Amount": [
            features["income"],
            features["expenses"],
            features["emi"],
            features["credit_card_due"],
            features["savings"],
            features["investments"],
            features["disposable_income"]
        ]
    })

    fig = px.bar(snapshot_df, x="Metric", y="Amount", text="Amount")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Spending Breakdown")

    txn_df = pd.DataFrame({
        "Category": customer["transactions"].keys(),
        "Amount": customer["transactions"].values()
    })

    fig = px.pie(txn_df, names="Category", values="Amount")
    st.plotly_chart(fig, use_container_width=True)


st.divider()

st.subheader("Financial Health Components")

score_df = pd.DataFrame({
    "Component": component_scores.keys(),
    "Score": component_scores.values()
})

fig = px.bar(score_df, x="Component", y="Score",
             text="Score", range_y=[0, 100])
st.plotly_chart(fig, use_container_width=True)


st.subheader("Financial DNA")

dna_df = pd.DataFrame({
    "Dimension": financial_dna.keys(),
    "Score": financial_dna.values()
})

fig = px.bar(dna_df, x="Dimension", y="Score", text="Score", range_y=[0, 100])
st.plotly_chart(fig, use_container_width=True)


st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Behaviour & Life Event Insights")

    for signal in twin["behaviour"]["signals"]:
        st.info(f"**Behaviour Signal:** {signal}")

    st.warning(
        f"**Life Event:** {twin['life_events']['label']} "
        f"({twin['life_events']['severity']} severity)"
    )

    for action in twin["life_events"]["actions"]:
        st.info(f"Recommended action: {action}")

with col_b:
    st.subheader("Personalized Recommendations")

    for rec in twin["recommendations"]:
        st.success(
            f"**{rec['title']}**\n\n"
            f"{rec['detail']}\n\n"
            f"Impact: {rec['impact']}\n\n"
            f"Confidence: {rec['confidence']}%"
        )


st.divider()

left2, right2 = st.columns(2)

with left2:
    st.subheader("Current Investment Portfolio")

    portfolio_df = pd.DataFrame({
        "Asset": customer["investments"].keys(),
        "Amount": customer["investments"].values()
    })

    fig = px.pie(portfolio_df, names="Asset", values="Amount")
    st.plotly_chart(fig, use_container_width=True)

with right2:
    st.subheader("Prediction Summary")

    st.metric("Goal Status", twin["predictions"]["goal_status"])
    st.metric("Projected Corpus", format_currency(
        twin["predictions"]["projected_corpus"]))
    st.metric("Goal Gap", format_currency(twin["predictions"]["goal_gap"]))
    st.metric("Financial Stress Risk",
              twin["predictions"]["financial_stress_risk"])


st.divider()

st.subheader("Inflation-Aware Goal Planner")

goal_col1, goal_col2, goal_col3 = st.columns(3)

goal_col1.metric("Goal", customer["investment_goal"].replace("_", " ").title())
goal_col2.metric("Today's Target", format_currency(
    twin["future_values"]["goal_amount_today"]))
goal_col3.metric("Inflation-Adjusted Target",
                 format_currency(twin["future_values"]["inflation_adjusted_goal"]))

st.write(
    f"Assuming **{twin['future_values']['inflation_rate']}% inflation**, "
    f"{customer['name']}'s goal grows from "
    f"**{format_currency(twin['future_values']['goal_amount_today'])}** to "
    f"**{format_currency(twin['future_values']['inflation_adjusted_goal'])}** "
    f"over {customer['goal_years']} years."
)

st.write(
    f"Required SIP for today's goal: "
    f"**{format_currency(twin['future_values']['required_sip_today_goal'])}/month**"
)

st.write(
    f"Required SIP for inflation-adjusted goal: "
    f"**{format_currency(twin['future_values']['required_sip_inflated_goal'])}/month**"
)


st.divider()

st.subheader("What-if SIP Simulator")

sim_col1, sim_col2, sim_col3 = st.columns(3)

monthly_sip = sim_col1.slider(
    "Monthly SIP",
    min_value=1000,
    max_value=100000,
    value=max(1000, recommendation_summary["recommended_sip"]),
    step=1000
)

years = sim_col2.slider(
    "Investment Duration",
    min_value=1,
    max_value=30,
    value=customer["goal_years"]
)

annual_return_percent = sim_col3.slider(
    "Expected Annual Return (%)",
    min_value=6,
    max_value=18,
    value=12
)

future_value = simulate_sip(monthly_sip, years, annual_return_percent / 100)
invested = monthly_sip * years * 12
gains = future_value - invested

sim1, sim2, sim3 = st.columns(3)

sim1.metric("Total Invested", format_currency(invested))
sim2.metric("Estimated Corpus", format_currency(future_value))
sim3.metric("Estimated Gains", format_currency(gains))

st.divider()

st.subheader("Financial Digital Twin Simulator")
st.caption(
    "Simulate one decision or stack multiple life events into a future scenario timeline.")

tab1, tab2 = st.tabs(["Single Decision", "Scenario Timeline"])

with tab1:
    event_col1, event_col2 = st.columns([1, 2])

    simulation_event = event_col1.selectbox(
        "Choose Life Event",
        list(EVENT_CONFIG.keys()),
        format_func=lambda event: EVENT_CONFIG[event]["label"],
        key="single_simulation_event"
    )

    event_col2.info(EVENT_CONFIG[simulation_event]["description"])

    input_col1, input_col2, input_col3 = st.columns(3)

    one_time_amount = input_col1.number_input(
        "One-time Amount / Down Payment",
        min_value=0,
        max_value=10000000,
        value=500000,
        step=50000,
        key="single_one_time_amount"
    )

    monthly_emi = input_col2.number_input(
        "Monthly EMI",
        min_value=0,
        max_value=1000000,
        value=15000,
        step=5000,
        key="single_monthly_emi"
    )

    recurring_expense = input_col3.number_input(
        "New Monthly Expense",
        min_value=0,
        max_value=500000,
        value=5000,
        step=1000,
        key="single_recurring_expense"
    )

    extra_col1, extra_col2 = st.columns(2)

    income_change = extra_col1.number_input(
        "Monthly Income Change",
        min_value=0,
        max_value=1000000,
        value=20000,
        step=5000,
        key="single_income_change"
    )

    market_fall_percent = extra_col2.slider(
        "Market Fall (%)",
        min_value=5,
        max_value=60,
        value=25,
        step=5,
        key="single_market_fall_percent"
    )

    if st.button("Run Single Decision Simulation", key="run_single_simulation"):
        result = simulate_event(
            customer=customer,
            event_type=simulation_event,
            one_time_amount=one_time_amount,
            monthly_emi=monthly_emi,
            income_change=income_change,
            recurring_expense=recurring_expense,
            market_fall_percent=market_fall_percent
        )

        impact = result["impact"]
        simulated_twin = result["simulated_twin"]

        st.markdown(f"### Verdict: {result['verdict']}")
        st.write(f"Impact Level: **{result['impact_level']}**")

        before_after_df = pd.DataFrame({
            "Metric": ["Health Score", "Net Worth", "Emergency Fund Months", "Goal Gap"],
            "Before": [
                result["base_twin"]["scores"]["overall"],
                result["base_twin"]["metrics"]["net_worth"],
                result["base_twin"]["metrics"]["emergency_months"],
                result["base_twin"]["predictions"]["goal_gap"]
            ],
            "After": [
                simulated_twin["scores"]["overall"],
                simulated_twin["metrics"]["net_worth"],
                simulated_twin["metrics"]["emergency_months"],
                simulated_twin["predictions"]["goal_gap"]
            ],
            "Change": [
                impact["health_score_change"],
                impact["net_worth_change"],
                impact["emergency_months_change"],
                impact["goal_gap_change"]
            ]
        })

        st.dataframe(before_after_df, use_container_width=True)

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Health Score", simulated_twin["scores"]["overall"], impact["health_score_change"])
        c2.metric("Net Worth", format_currency(
            simulated_twin["metrics"]["net_worth"]), format_currency(impact["net_worth_change"]))
        c3.metric("Emergency Fund",
                  f"{simulated_twin['metrics']['emergency_months']} months", f"{impact['emergency_months_change']} months")
        c4.metric("Goal Gap", format_currency(
            simulated_twin["predictions"]["goal_gap"]), format_currency(impact["goal_gap_change"]))

        st.markdown("### Updated Recommendations")

        for rec in simulated_twin["recommendations"][:4]:
            st.success(
                f"**{rec['title']}**\n\n"
                f"{rec['detail']}\n\n"
                f"Confidence: {rec['confidence']}%"
            )

with tab2:
    st.markdown("### Scenario Timeline")
    st.caption(
        "Stack multiple future events and see cumulative impact on the Financial Digital Twin.")

    scenario_count = st.slider(
        "Number of future events",
        min_value=1,
        max_value=5,
        value=3,
        key="scenario_count"
    )

    scenario_events = []

    for i in range(scenario_count):
        st.markdown(f"#### Step {i + 1}")

        c1, c2, c3 = st.columns(3)

        event_type = c1.selectbox(
            "Event",
            list(EVENT_CONFIG.keys()),
            format_func=lambda event: EVENT_CONFIG[event]["label"],
            key=f"scenario_event_{i}"
        )

        amount = c2.number_input(
            "One-time Amount",
            min_value=0,
            max_value=10000000,
            value=300000,
            step=50000,
            key=f"scenario_amount_{i}"
        )

        emi_or_income = c3.number_input(
            "EMI / Income Change",
            min_value=0,
            max_value=1000000,
            value=10000,
            step=5000,
            key=f"scenario_emi_income_{i}"
        )

        c4, c5 = st.columns(2)

        recurring = c4.number_input(
            "Recurring Monthly Expense",
            min_value=0,
            max_value=500000,
            value=3000,
            step=1000,
            key=f"scenario_recurring_{i}"
        )

        market_fall = c5.slider(
            "Market Fall %",
            min_value=5,
            max_value=60,
            value=25,
            step=5,
            key=f"scenario_market_fall_{i}"
        )

        scenario_events.append({
            "event_type": event_type,
            "one_time_amount": amount,
            "monthly_emi": emi_or_income if event_type in ["car_purchase", "home_purchase"] else 0,
            "income_change": emi_or_income if event_type == "salary_increment" else 0,
            "recurring_expense": recurring,
            "market_fall_percent": market_fall
        })

    if st.button("Run Scenario Timeline", key="run_scenario_timeline"):
        scenario_result = simulate_scenario_timeline(customer, scenario_events)

        base_twin = scenario_result["base_twin"]
        final_twin = scenario_result["final_twin"]
        total_impact = scenario_result["total_impact"]

        st.markdown("### Cumulative Scenario Impact")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Final Health Score",
                  final_twin["scores"]["overall"], total_impact["health_score_change"])
        c2.metric("Final Net Worth", format_currency(
            final_twin["metrics"]["net_worth"]), format_currency(total_impact["net_worth_change"]))
        c3.metric("Emergency Fund", f"{final_twin['metrics']['emergency_months']} months",
                  f"{total_impact['emergency_months_change']} months")
        c4.metric("Goal Gap", format_currency(
            final_twin["predictions"]["goal_gap"]), format_currency(total_impact["goal_gap_change"]))

        st.markdown("### Financial Journey Timeline")

        for step in scenario_result["timeline"]:
            with st.container(border=True):
                st.markdown(
                    f"### Step {step['step']}: {step['event_label']}"
                )

                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "Health Score",
                    step["after_score"],
                    step["score_change"]
                )

                c2.metric(
                    "Net Worth",
                    format_currency(step["after_net_worth"]),
                    format_currency(step["net_worth_change"])
                )

                c3.metric(
                    "Emergency Fund",
                    f"{step['after_emergency_months']} months",
                    f"{step['emergency_months_change']} months"
                )

                c4.metric(
                    "Goal Gap",
                    format_currency(step["after_goal_gap"]),
                    format_currency(step["goal_gap_change"])
                )

                s1, s2 = st.columns(2)

                s1.info(
                    f"Goal Status: **{step['before_goal_status']} → {step['after_goal_status']}**"
                )

                s2.warning(
                    f"Stress Risk: **{step['before_stress_risk']} → {step['after_stress_risk']}**"
                )

        fig = px.line(
            timeline_df,
            x="step",
            y="after_score",
            markers=True,
            text="event_label",
            title="Financial Health Score Across Scenario Timeline"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Final Advisor Summary")

        st.info(
            f"Starting health score was **{base_twin['scores']['overall']}**. "
            f"After the full scenario timeline, it becomes **{final_twin['scores']['overall']}**."
        )

        st.warning(
            f"Emergency fund changes from **{base_twin['metrics']['emergency_months']} months** "
            f"to **{final_twin['metrics']['emergency_months']} months**."
        )

        st.success(
            f"Final goal status: **{final_twin['predictions']['goal_status']}**."
        )

st.divider()

st.subheader("ArthaMitra Advisor")

top_recommendation = twin["recommendations"][0] if twin["recommendations"] else None

advisor_response = f"""
Hi {customer['name']}, I created your Financial Digital Twin.

Your Financial Health Score is **{overall_score}/100**, classified as **{health_label}**.  
Your financial persona is **{twin['persona']['type']}**.

Your current emergency fund covers **{features['emergency_months']} months**, while your recommended target is **{recommendation_summary['emergency_target_months']} months**.

Your inflation-adjusted goal is **{format_currency(twin['future_values']['inflation_adjusted_goal'])}**, and your current goal status is **{twin['predictions']['goal_status']}**.

Your detected life event is **{twin['life_events']['label']}**, so I have adjusted recommendations based on that context.
"""

if top_recommendation:
    advisor_response += f"""

My top recommendation is **{top_recommendation['title']}**:  
{top_recommendation['detail']}

Confidence: **{top_recommendation['confidence']}%**
"""

st.chat_message("assistant").write(advisor_response)


st.divider()

st.subheader("Generate Financial Report")
st.caption(
    "Generate a structured report from the currently active Financial Digital Twin.")

if st.button("Generate Current Twin Report", key="generate_current_twin_report"):
    report = build_financial_report(twin)

    st.success("Financial report generated from current Financial Digital Twin.")

    st.markdown("### Executive Summary")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Health Score",
        f"{report['executive_summary']['health_score']}/100",
        report["executive_summary"]["health_label"]
    )

    c2.metric(
        "Goal Status",
        report["executive_summary"]["goal_status"]
    )

    c3.metric(
        "Stress Risk",
        report["executive_summary"]["stress_risk"]
    )

    st.info(
        f"**Primary Focus:** {report['executive_summary']['primary_focus']}")

    st.markdown("### Action Plan")

    for phase, actions in report["action_plan"].items():
        st.markdown(f"**{phase.replace('_', ' ').title()}**")
        for action in actions:
            st.write(f"- {action}")

    pdf_path = export_report_pdf(report)

    with open(pdf_path, "rb") as file:
        st.download_button(
            label="Download Financial Report PDF",
            data=file,
            file_name=pdf_path.split("\\")[-1],
            mime="application/pdf"
        )
