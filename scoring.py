from .config import DUST_WEIGHTS
def weighted_score(scores): return round(sum(scores.get(k,0)*w for k,w in DUST_WEIGHTS.items())*10,1)
def verdict(score):
    return "Stark kaufen" if score>=85 else "Kaufen" if score>=75 else "Beobachten" if score>=65 else "Halten" if score>=55 else "Reduzieren" if score>=45 else "Verkaufen"
