from services.engines.financial_engine import run_financial_engine
from services.engines.persona_engine import run_persona_engine
from services.engines.behaviour_engine import run_behaviour_engine
from services.engines.life_event_engine import run_life_event_engine
from services.engines.inflation_engine import run_inflation_engine
from services.engines.prediction_engine import run_prediction_engine
from services.engines.recommendation_engine import run_recommendation_engine
from services.engines.confidence_engine import run_confidence_engine


def build_financial_twin(customer):
    twin = {
        "customer": customer,
        "metrics": {},
        "scores": {},
        "persona": {},
        "behaviour": {},
        "life_events": {},
        "future_values": {},
        "predictions": {},
        "recommendations": [],
        "recommendation_summary": {},
        "confidence": {}
    }

    for engine in [
        run_financial_engine,
        run_persona_engine,
        run_behaviour_engine,
        run_life_event_engine,
        run_inflation_engine,
        run_prediction_engine,
        run_recommendation_engine,
        run_confidence_engine,
    ]:
        twin = engine(twin)

    return twin
