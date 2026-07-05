import streamlit as st
import pandas as pd
import plotly.express as px

from utils.helpers import load_customers, format_currency
from services.financial_twin import build_financial_twin
from services.engines.prediction_engine import simulate_sip


st.set_page_config(
    page_title="ArthaMitra",
    page_icon="💰",
    layout="wide"
)

st.title("💰 ArthaMitra")
st.caption(
    "Your AI Financial Relationship Manager — powered by a Financial Digital Twin")

customers = load_customers()


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
        "customer_id": "QUICK",
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

elif mode == "📄 AI Wealth Report":
    st.title("📄 AI Wealth Report")
    st.info("PDF report generation will be added next. Elite access is working.")
    st.stop()

elif mode == "🤖 AI Wealth Coach":
    st.title("🤖 AI Wealth Coach")
    st.info("Interactive coach will be added next. Elite access is working.")
    st.stop()


twin = build_financial_twin(customer)

features = twin["metrics"]
component_scores = twin["scores"]["components"]
financial_dna = twin["scores"]["financial_dna"]
overall_score = twin["scores"]["overall"]
health_label = twin["scores"]["label"]
risk_profile = twin["persona"]["type"]
recommendation_summary = twin["recommendation_summary"]


st.sidebar.markdown("### Customer Profile")
st.sidebar.write(f"**Name:** {customer['name']}")
st.sidebar.write(f"**Age:** {customer['age']}")
st.sidebar.write(f"**City:** {customer['city']}")
st.sidebar.write(f"**Occupation:** {customer['occupation']}")
st.sidebar.write(
    f"**Life Stage:** {customer['life_stage'].replace('_', ' ').title()}")
st.sidebar.write(f"**Life Event:** {twin['life_events']['label']}")


col1, col2, col3, col4 = st.columns(4)

col1.metric("Health Score", f"{overall_score}/100", health_label)
col2.metric("Financial Persona", risk_profile)
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
