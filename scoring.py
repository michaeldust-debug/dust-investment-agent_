from config import DUST_WEIGHTS

def weighted_score(scores: dict[str, float]) -> float:
    total = sum(scores.get(key, 0.0) * weight for key, weight in DUST_WEIGHTS.items())
    return round(total * 10, 1)

def verdict(score: float) -> str:
    if score >= 85: return "Stark kaufen"
    if score >= 75: return "Kaufen"
    if score >= 65: return "Beobachten"
    if score >= 55: return "Halten"
    if score >= 45: return "Reduzieren"
    return "Verkaufen"
