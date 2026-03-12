# risk_model.py
import numpy as np
import pandas as pd
from datetime import datetime
import json

COUNTRY_RISK_PROFILES = {
    # North America
    "US": {"base_risk":15,"economy_score":95,"stability":85,"region":"North America"},
    "CA": {"base_risk":12,"economy_score":88,"stability":90,"region":"North America"},
    "MX": {"base_risk":50,"economy_score":55,"stability":50,"region":"North America"},
    "GT": {"base_risk":55,"economy_score":35,"stability":40,"region":"Central America"},
    "BZ": {"base_risk":45,"economy_score":35,"stability":50,"region":"Central America"},
    "HN": {"base_risk":60,"economy_score":30,"stability":35,"region":"Central America"},
    "SV": {"base_risk":58,"economy_score":32,"stability":38,"region":"Central America"},
    "NI": {"base_risk":62,"economy_score":28,"stability":30,"region":"Central America"},
    "CR": {"base_risk":30,"economy_score":55,"stability":65,"region":"Central America"},
    "PA": {"base_risk":35,"economy_score":58,"stability":60,"region":"Central America"},
    "CU": {"base_risk":65,"economy_score":25,"stability":40,"region":"Caribbean"},
    "JM": {"base_risk":45,"economy_score":38,"stability":50,"region":"Caribbean"},
    "HT": {"base_risk":80,"economy_score":10,"stability":10,"region":"Caribbean"},
    "DO": {"base_risk":40,"economy_score":42,"stability":52,"region":"Caribbean"},
    "TT": {"base_risk":38,"economy_score":50,"stability":58,"region":"Caribbean"},
    "PR": {"base_risk":30,"economy_score":55,"stability":60,"region":"Caribbean"},
    "BS": {"base_risk":25,"economy_score":55,"stability":68,"region":"Caribbean"},

    # South America
    "CO": {"base_risk":45,"economy_score":52,"stability":48,"region":"South America"},
    "VE": {"base_risk":88,"economy_score":15,"stability":10,"region":"South America"},
    "GY": {"base_risk":42,"economy_score":45,"stability":52,"region":"South America"},
    "SR": {"base_risk":48,"economy_score":38,"stability":48,"region":"South America"},
    "BR": {"base_risk":40,"economy_score":60,"stability":55,"region":"South America"},
    "EC": {"base_risk":48,"economy_score":42,"stability":45,"region":"South America"},
    "PE": {"base_risk":42,"economy_score":50,"stability":50,"region":"South America"},
    "BO": {"base_risk":45,"economy_score":38,"stability":48,"region":"South America"},
    "PY": {"base_risk":42,"economy_score":40,"stability":50,"region":"South America"},
    "UY": {"base_risk":22,"economy_score":65,"stability":72,"region":"South America"},
    "AR": {"base_risk":65,"economy_score":35,"stability":40,"region":"South America"},
    "CL": {"base_risk":25,"economy_score":70,"stability":72,"region":"South America"},
    "GW": {"base_risk":65,"economy_score":15,"stability":20,"region":"West Africa"},
    "FK": {"base_risk":10,"economy_score":50,"stability":88,"region":"South America"},

    # Europe
    "GB": {"base_risk":22,"economy_score":82,"stability":80,"region":"Europe"},
    "IE": {"base_risk":18,"economy_score":82,"stability":85,"region":"Europe"},
    "IS": {"base_risk":10,"economy_score":80,"stability":92,"region":"Europe"},
    "NO": {"base_risk":10,"economy_score":88,"stability":93,"region":"Europe"},
    "SE": {"base_risk":12,"economy_score":86,"stability":90,"region":"Europe"},
    "FI": {"base_risk":12,"economy_score":84,"stability":90,"region":"Europe"},
    "DK": {"base_risk":12,"economy_score":85,"stability":91,"region":"Europe"},
    "DE": {"base_risk":20,"economy_score":88,"stability":85,"region":"Europe"},
    "NL": {"base_risk":18,"economy_score":84,"stability":86,"region":"Europe"},
    "BE": {"base_risk":20,"economy_score":80,"stability":78,"region":"Europe"},
    "LU": {"base_risk":12,"economy_score":88,"stability":90,"region":"Europe"},
    "FR": {"base_risk":25,"economy_score":80,"stability":75,"region":"Europe"},
    "ES": {"base_risk":25,"economy_score":72,"stability":72,"region":"Europe"},
    "PT": {"base_risk":22,"economy_score":68,"stability":75,"region":"Europe"},
    "IT": {"base_risk":28,"economy_score":72,"stability":68,"region":"Europe"},
    "CH": {"base_risk":10,"economy_score":90,"stability":94,"region":"Europe"},
    "AT": {"base_risk":15,"economy_score":82,"stability":86,"region":"Europe"},
    "PL": {"base_risk":30,"economy_score":68,"stability":68,"region":"Europe"},
    "CZ": {"base_risk":22,"economy_score":72,"stability":75,"region":"Europe"},
    "SK": {"base_risk":22,"economy_score":68,"stability":72,"region":"Europe"},
    "HU": {"base_risk":32,"economy_score":62,"stability":60,"region":"Europe"},
    "RO": {"base_risk":35,"economy_score":58,"stability":58,"region":"Europe"},
    "BG": {"base_risk":35,"economy_score":52,"stability":55,"region":"Europe"},
    "GR": {"base_risk":38,"economy_score":52,"stability":58,"region":"Europe"},
    "HR": {"base_risk":28,"economy_score":58,"stability":65,"region":"Europe"},
    "SI": {"base_risk":20,"economy_score":68,"stability":75,"region":"Europe"},
    "BA": {"base_risk":45,"economy_score":42,"stability":45,"region":"Europe"},
    "RS": {"base_risk":38,"economy_score":48,"stability":50,"region":"Europe"},
    "ME": {"base_risk":35,"economy_score":45,"stability":52,"region":"Europe"},
    "MK": {"base_risk":38,"economy_score":42,"stability":50,"region":"Europe"},
    "AL": {"base_risk":42,"economy_score":40,"stability":48,"region":"Europe"},
    "EE": {"base_risk":25,"economy_score":68,"stability":72,"region":"Europe"},
    "LV": {"base_risk":28,"economy_score":62,"stability":68,"region":"Europe"},
    "LT": {"base_risk":28,"economy_score":64,"stability":68,"region":"Europe"},
    "BY": {"base_risk":75,"economy_score":30,"stability":28,"region":"Europe"},
    "UA": {"base_risk":90,"economy_score":30,"stability":15,"region":"Europe"},
    "MD": {"base_risk":48,"economy_score":35,"stability":45,"region":"Europe"},
    "RU": {"base_risk":80,"economy_score":35,"stability":30,"region":"Europe"},
    "CY": {"base_risk":30,"economy_score":60,"stability":65,"region":"Europe"},
    "GL": {"base_risk":10,"economy_score":50,"stability":90,"region":"Europe"},

    # Middle East
    "TR": {"base_risk":60,"economy_score":50,"stability":45,"region":"Middle East"},
    "SY": {"base_risk":92,"economy_score":10,"stability":8,"region":"Middle East"},
    "LB": {"base_risk":82,"economy_score":15,"stability":12,"region":"Middle East"},
    "IL": {"base_risk":75,"economy_score":60,"stability":35,"region":"Middle East"},
    "PS": {"base_risk":95,"economy_score":10,"stability":5,"region":"Middle East"},
    "JO": {"base_risk":40,"economy_score":42,"stability":52,"region":"Middle East"},
    "IQ": {"base_risk":75,"economy_score":28,"stability":25,"region":"Middle East"},
    "IR": {"base_risk":85,"economy_score":25,"stability":25,"region":"Middle East"},
    "KW": {"base_risk":35,"economy_score":70,"stability":60,"region":"Middle East"},
    "SA": {"base_risk":55,"economy_score":65,"stability":50,"region":"Middle East"},
    "QA": {"base_risk":30,"economy_score":78,"stability":65,"region":"Middle East"},
    "AE": {"base_risk":25,"economy_score":80,"stability":70,"region":"Middle East"},
    "OM": {"base_risk":30,"economy_score":62,"stability":62,"region":"Middle East"},
    "YE": {"base_risk":92,"economy_score":8,"stability":5,"region":"Middle East"},

    # Asia
    "KP": {"base_risk":95,"economy_score":10,"stability":10,"region":"Asia"},
    "KR": {"base_risk":40,"economy_score":78,"stability":70,"region":"Asia"},
    "JP": {"base_risk":18,"economy_score":88,"stability":88,"region":"Asia"},
    "CN": {"base_risk":45,"economy_score":80,"stability":60,"region":"Asia"},
    "TW": {"base_risk":55,"economy_score":75,"stability":60,"region":"Asia"},
    "MN": {"base_risk":38,"economy_score":40,"stability":52,"region":"Asia"},
    "IN": {"base_risk":35,"economy_score":70,"stability":65,"region":"Asia"},
    "PK": {"base_risk":70,"economy_score":30,"stability":30,"region":"Asia"},
    "AF": {"base_risk":95,"economy_score":5,"stability":5,"region":"Asia"},
    "BD": {"base_risk":48,"economy_score":42,"stability":48,"region":"Asia"},
    "LK": {"base_risk":52,"economy_score":35,"stability":40,"region":"Asia"},
    "NP": {"base_risk":45,"economy_score":28,"stability":48,"region":"Asia"},
    "BT": {"base_risk":22,"economy_score":42,"stability":72,"region":"Asia"},
    "MM": {"base_risk":78,"economy_score":20,"stability":15,"region":"Asia"},
    "TH": {"base_risk":40,"economy_score":58,"stability":52,"region":"Asia"},
    "LA": {"base_risk":45,"economy_score":35,"stability":48,"region":"Asia"},
    "KH": {"base_risk":48,"economy_score":38,"stability":45,"region":"Asia"},
    "VN": {"base_risk":35,"economy_score":55,"stability":58,"region":"Asia"},
    "MY": {"base_risk":30,"economy_score":62,"stability":62,"region":"Asia"},
    "PH": {"base_risk":45,"economy_score":50,"stability":48,"region":"Asia"},
    "ID": {"base_risk":38,"economy_score":55,"stability":55,"region":"Asia"},
    "TL": {"base_risk":52,"economy_score":25,"stability":40,"region":"Asia"},
    "SB": {"base_risk":45,"economy_score":20,"stability":45,"region":"Asia"},
    "VU": {"base_risk":35,"economy_score":22,"stability":55,"region":"Asia"},
    "PG": {"base_risk":52,"economy_score":28,"stability":42,"region":"Asia"},
    "KZ": {"base_risk":42,"economy_score":52,"stability":50,"region":"Asia"},
    "KG": {"base_risk":50,"economy_score":28,"stability":42,"region":"Asia"},
    "TJ": {"base_risk":58,"economy_score":22,"stability":38,"region":"Asia"},
    "TM": {"base_risk":55,"economy_score":35,"stability":35,"region":"Asia"},
    "UZ": {"base_risk":48,"economy_score":38,"stability":45,"region":"Asia"},
    "AZ": {"base_risk":52,"economy_score":48,"stability":45,"region":"Asia"},
    "AM": {"base_risk":55,"economy_score":38,"stability":42,"region":"Asia"},
    "GE": {"base_risk":48,"economy_score":42,"stability":48,"region":"Asia"},
    "BN": {"base_risk":25,"economy_score":65,"stability":70,"region":"Asia"},

    # Africa
    "MA": {"base_risk":40,"economy_score":45,"stability":52,"region":"Africa"},
    "DZ": {"base_risk":48,"economy_score":42,"stability":45,"region":"Africa"},
    "TN": {"base_risk":42,"economy_score":42,"stability":50,"region":"Africa"},
    "LY": {"base_risk":78,"economy_score":18,"stability":12,"region":"Africa"},
    "EG": {"base_risk":52,"economy_score":40,"stability":42,"region":"Africa"},
    "SD": {"base_risk":78,"economy_score":12,"stability":12,"region":"Africa"},
    "SS": {"base_risk":88,"economy_score":8,"stability":8,"region":"Africa"},
    "ET": {"base_risk":60,"economy_score":30,"stability":35,"region":"Africa"},
    "ER": {"base_risk":68,"economy_score":15,"stability":25,"region":"Africa"},
    "DJ": {"base_risk":55,"economy_score":20,"stability":38,"region":"Africa"},
    "SO": {"base_risk":88,"economy_score":5,"stability":5,"region":"Africa"},
    "KE": {"base_risk":48,"economy_score":42,"stability":48,"region":"Africa"},
    "UG": {"base_risk":52,"economy_score":32,"stability":40,"region":"Africa"},
    "TZ": {"base_risk":42,"economy_score":35,"stability":52,"region":"Africa"},
    "RW": {"base_risk":38,"economy_score":38,"stability":55,"region":"Africa"},
    "BI": {"base_risk":65,"economy_score":12,"stability":22,"region":"Africa"},
    "MG": {"base_risk":52,"economy_score":18,"stability":38,"region":"Africa"},
    "MZ": {"base_risk":55,"economy_score":22,"stability":35,"region":"Africa"},
    "ZM": {"base_risk":48,"economy_score":28,"stability":45,"region":"Africa"},
    "ZW": {"base_risk":65,"economy_score":15,"stability":25,"region":"Africa"},
    "MW": {"base_risk":52,"economy_score":15,"stability":42,"region":"Africa"},
    "NA": {"base_risk":35,"economy_score":42,"stability":58,"region":"Africa"},
    "BW": {"base_risk":28,"economy_score":52,"stability":65,"region":"Africa"},
    "ZA": {"base_risk":55,"economy_score":45,"stability":45,"region":"Africa"},
    "SZ": {"base_risk":45,"economy_score":28,"stability":45,"region":"Africa"},
    "LS": {"base_risk":48,"economy_score":22,"stability":42,"region":"Africa"},
    "AO": {"base_risk":55,"economy_score":35,"stability":40,"region":"Africa"},
    "CD": {"base_risk":75,"economy_score":12,"stability":12,"region":"Africa"},
    "CG": {"base_risk":60,"economy_score":25,"stability":30,"region":"Africa"},
    "CF": {"base_risk":82,"economy_score":8,"stability":8,"region":"Africa"},
    "CM": {"base_risk":55,"economy_score":30,"stability":38,"region":"Africa"},
    "NG": {"base_risk":65,"economy_score":35,"stability":35,"region":"Africa"},
    "GH": {"base_risk":38,"economy_score":40,"stability":55,"region":"Africa"},
    "CI": {"base_risk":48,"economy_score":35,"stability":45,"region":"Africa"},
    "LR": {"base_risk":58,"economy_score":15,"stability":30,"region":"Africa"},
    "SL": {"base_risk":55,"economy_score":15,"stability":32,"region":"Africa"},
    "GN": {"base_risk":60,"economy_score":18,"stability":28,"region":"Africa"},
    "SN": {"base_risk":40,"economy_score":30,"stability":55,"region":"Africa"},
    "ML": {"base_risk":68,"economy_score":18,"stability":22,"region":"Africa"},
    "BF": {"base_risk":70,"economy_score":15,"stability":20,"region":"Africa"},
    "NE": {"base_risk":68,"economy_score":12,"stability":22,"region":"Africa"},
    "TD": {"base_risk":72,"economy_score":12,"stability":18,"region":"Africa"},
    "MR": {"base_risk":58,"economy_score":20,"stability":32,"region":"Africa"},
    "EH": {"base_risk":55,"economy_score":15,"stability":30,"region":"Africa"},
    "GA": {"base_risk":45,"economy_score":38,"stability":48,"region":"Africa"},
    "GQ": {"base_risk":55,"economy_score":35,"stability":35,"region":"Africa"},
    "TG": {"base_risk":50,"economy_score":22,"stability":40,"region":"Africa"},
    "BJ": {"base_risk":48,"economy_score":22,"stability":42,"region":"Africa"},
    "GM": {"base_risk":48,"economy_score":18,"stability":42,"region":"Africa"},

    # Oceania
    "AU": {"base_risk":15,"economy_score":85,"stability":88,"region":"Oceania"},
    "NZ": {"base_risk":10,"economy_score":80,"stability":92,"region":"Oceania"},
    "NC": {"base_risk":20,"economy_score":55,"stability":65,"region":"Oceania"},
    "FJ": {"base_risk":35,"economy_score":35,"stability":48,"region":"Oceania"},
    "TF": {"base_risk":5,"economy_score":50,"stability":95,"region":"Oceania"},
    "AQ": {"base_risk":5,"economy_score":50,"stability":98,"region":"Oceania"},
}

# Event type risk weights
EVENT_RISK_WEIGHTS = {
    "conflict":      25,
    "sanctions":     20,
    "election":      10,
    "economic":      12,
    "trade_war":     18,
    "coup":          30,
    "protest":       8,
    "natural":       5,
    "diplomatic":    6,
    "terrorism":     22,
    "neutral":       0,
}

# Sector impact matrix
SECTOR_IMPACT = {
    "conflict": {
        "Energy":        +15,
        "Defense":       +20,
        "Banking":       -10,
        "Technology":    -8,
        "Consumer":      -12,
        "Healthcare":    -5,
    },
    "sanctions": {
        "Energy":        +10,
        "Banking":       -15,
        "Technology":    -12,
        "Trade":         -20,
        "Consumer":      -8,
    },
    "trade_war": {
        "Technology":    -15,
        "Consumer":      -10,
        "Manufacturing": -18,
        "Agriculture":   -12,
        "Banking":       -8,
    },
    "economic": {
        "Banking":       -12,
        "Consumer":      -10,
        "Real Estate":   -8,
        "Technology":    -6,
    },
}

def compute_country_risk(country_code, news_articles=None, market_data=None):
    profile = COUNTRY_RISK_PROFILES.get(country_code, {
        "base_risk": 50, "economy_score": 50, "stability": 50, "region": "Unknown"
    })

    risk_score = profile["base_risk"]
    risk_factors = []

    if news_articles:
        country_news = [a for a in news_articles if a.get('country') == country_code]
        if country_news:
            avg_sentiment = sum(a.get('sentiment_score', 0) for a in country_news) / len(country_news)
            sentiment_adjustment = -avg_sentiment * 15
            risk_score += sentiment_adjustment
            if sentiment_adjustment > 0:
                risk_factors.append(f"Negative news sentiment (+{sentiment_adjustment:.1f})")
            for article in country_news:
                event_type = article.get('event_type', 'neutral')
                event_weight = EVENT_RISK_WEIGHTS.get(event_type, 0)
                risk_score += event_weight * 0.3
                if event_weight > 10:
                    risk_factors.append(f"{event_type.title()} event detected")

    if market_data:
        vix = market_data.get('^VIX', {}).get('price', 20)
        if vix > 30:
            risk_score += 10
            risk_factors.append(f"High VIX ({vix:.1f})")
        elif vix > 25:
            risk_score += 5
            risk_factors.append(f"Elevated VIX ({vix:.1f})")

    risk_score = round(min(max(risk_score, 0), 100), 1)

    if risk_score < 25:   level = "LOW"
    elif risk_score < 50: level = "MODERATE"
    elif risk_score < 75: level = "HIGH"
    else:                 level = "CRITICAL"

    if risk_score < 25:   color = "#00ff88"
    elif risk_score < 50: color = "#ffdd00"
    elif risk_score < 75: color = "#ff8800"
    else:                 color = "#ff2200"

    return {
        "country":      country_code,
        "risk_score":   risk_score,
        "level":        level,
        "color":        color,
        "base_risk":    profile["base_risk"],
        "region":       profile["region"],
        "risk_factors": risk_factors,
        "economy":      profile["economy_score"],
        "stability":    profile["stability"],
        "timestamp":    datetime.now().isoformat()
    }

def compute_all_country_risks(news_articles=None, market_data=None):
    risks = {}
    for country_code in COUNTRY_RISK_PROFILES:
        risks[country_code] = compute_country_risk(country_code, news_articles, market_data)
    return risks

def compute_sector_impacts(news_articles=None):
    sector_scores = {
        "Energy": 0, "Banking": 0, "Technology": 0,
        "Consumer": 0, "Defense": 0, "Healthcare": 0,
        "Manufacturing": 0, "Trade": 0
    }
    if news_articles:
        for article in news_articles:
            event_type = article.get('event_type', 'neutral')
            if event_type in SECTOR_IMPACT:
                for sector, impact in SECTOR_IMPACT[event_type].items():
                    if sector in sector_scores:
                        sector_scores[sector] += impact * 0.1
    result = []
    for sector, score in sector_scores.items():
        result.append({
            "sector": sector,
            "impact": round(score, 2),
            "direction": "positive" if score > 0 else "negative" if score < 0 else "neutral",
            "signal": "BUY" if score > 2 else "SELL" if score < -2 else "HOLD"
        })
    return sorted(result, key=lambda x: abs(x['impact']), reverse=True)

def compute_geopolitical_tension_index(country_risks):
    if not country_risks:
        return {"index": 50, "level": "MODERATE"}

    economic_weights = {
        "US": 0.25, "CN": 0.15, "DE": 0.08, "JP": 0.07,
        "GB": 0.06, "IN": 0.05, "RU": 0.04, "FR": 0.04,
    }

    weighted_sum = 0
    total_weight = 0
    for code, risk in country_risks.items():
        weight = economic_weights.get(code, 0.01)
        weighted_sum += risk['risk_score'] * weight
        total_weight += weight

    index = round(weighted_sum / total_weight if total_weight > 0 else 50, 1)

    if index < 25:   level = "CALM"
    elif index < 50: level = "TENSE"
    elif index < 75: level = "VOLATILE"
    else:            level = "CRISIS"

    return {
        "index": index,
        "level": level,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("Computing country risk scores...")
    risks = compute_all_country_risks()
    sorted_risks = sorted(risks.values(), key=lambda x: x['risk_score'], reverse=True)

    print(f"\nTotal countries: {len(risks)}")
    print("\nTop 10 Highest Risk Countries:")
    for r in sorted_risks[:10]:
        bar = "█" * int(r['risk_score'] / 5)
        print(f"  {r['country']:4} [{r['level']:8}] {r['risk_score']:5.1f} {bar}")

    print("\nBottom 5 Safest Countries:")
    for r in sorted_risks[-5:]:
        print(f"  {r['country']:4} [{r['level']:8}] {r['risk_score']:5.1f}")

    sectors = compute_sector_impacts()
    print("\nSector Impact Analysis:")
    for s in sectors[:5]:
        print(f"  {s['sector']:15} {s['signal']:4}  impact={s['impact']:+.2f}")

    tension = compute_geopolitical_tension_index(risks)
    print(f"\nGlobal Tension Index: {tension['index']} / 100  →  {tension['level']}")