def run_confidence_engine(twin):
    metrics = twin["metrics"]
    recommendations = twin["recommendations"]

    scored = []

    for rec in recommendations:
        confidence = 80
        reasons = []

        if metrics["salary_growth"] >= 5:
            confidence += 5
            reasons.append("Positive income trend")

        if metrics["disposable_income"] > 0:
            confidence += 5
            reasons.append("Positive disposable income")

        if metrics["savings_growth"] >= 10:
            confidence += 5
            reasons.append("Savings balance is improving")

        if metrics["debt_to_income"] > 40:
            confidence -= 10
            reasons.append("High debt burden reduces flexibility")

        confidence = max(50, min(98, confidence))

        scored.append({
            **rec,
            "confidence": confidence,
            "confidence_reasons": reasons or ["Based on current financial profile"]
        })

    twin["recommendations"] = scored
    twin["confidence"] = {
        "average_confidence": round(sum(r["confidence"] for r in scored) / len(scored)) if scored else 0
    }

    return twin
