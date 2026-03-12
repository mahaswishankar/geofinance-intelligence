# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time
from datetime import datetime

# from news_fetcher import fetch_finance_headlines, fetch_country_news
from news_fetcher import get_processed_news, fetch_geopolitical_news, fetch_country_news
from market_data import fetch_live_prices, compute_market_stress, fetch_historical
from sentiment import analyze_articles, compute_country_sentiment
from risk_model import (
    compute_all_country_risks,
    compute_sector_impacts,
    compute_geopolitical_tension_index,
    COUNTRY_RISK_PROFILES
)

app = Flask(__name__)
CORS(app)

# ─── In-memory cache ───────────────────────────────────────────
_cache = {
    "market":    {"data": None, "ts": 0},
    "news":      {"data": None, "ts": 0},
    "risk":      {"data": None, "ts": 0},
    "stress":    {"data": None, "ts": 0},
}
CACHE_TTL = {
    "market": 60,       # 1 min
    "news":   600,      # 10 min
    "risk":   300,      # 5 min
    "stress": 60,       # 1 min
}

def is_stale(key):
    return time.time() - _cache[key]["ts"] > CACHE_TTL[key]

def get_market():
    if is_stale("market") or not _cache["market"]["data"]:
        _cache["market"]["data"] = fetch_live_prices()
        _cache["market"]["ts"]   = time.time()
    return _cache["market"]["data"]

# def get_news():
#     if is_stale("news") or not _cache["news"]["data"]:
#         raw = fetch_finance_headlines(20)
#         _cache["news"]["data"] = analyze_articles(raw)
#         _cache["news"]["ts"]   = time.time()
#     return _cache["news"]["data"]

def get_news():
    if is_stale("news") or not _cache["news"]["data"]:
        raw = get_processed_news()
        _cache["news"]["data"] = raw  # already processed with event types
        _cache["news"]["ts"]   = time.time()
    return _cache["news"]["data"]


def get_risk():
    if is_stale("risk") or not _cache["risk"]["data"]:
        news    = get_news()
        market  = get_market()
        _cache["risk"]["data"] = compute_all_country_risks(news, market)
        _cache["risk"]["ts"]   = time.time()
    return _cache["risk"]["data"]

def get_stress():
    if is_stale("stress") or not _cache["stress"]["data"]:
        _cache["stress"]["data"] = compute_market_stress()
        _cache["stress"]["ts"]   = time.time()
    return _cache["stress"]["data"]

# ─── Routes ────────────────────────────────────────────────────

@app.route("/")
def index():
    return jsonify({
        "name":    "GeoFinance Intelligence Platform API",
        "version": "1.0.0",
        "status":  "operational",
        "endpoints": [
            "/api/market",
            "/api/market/history/<ticker>",
            "/api/news",
            "/api/risk",
            "/api/risk/<country>",
            "/api/stress",
            "/api/tension",
            "/api/sectors",
            "/api/dashboard",
        ]
    })

@app.route("/api/market")
def market():
    try:
        data = get_market()
        return jsonify({"status": "ok", "data": data, "count": len(data)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/market/history/<ticker>")
def market_history(ticker):
    try:
        days = request.args.get("days", 90, type=int)
        data = fetch_historical(ticker.upper(), days)
        return jsonify({"status": "ok", "ticker": ticker, "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/news")
def news():
    try:
        data = get_news()
        country = request.args.get("country")
        if country:
            data = [a for a in data if country.upper() in a.get("countries", [])]
        return jsonify({"status": "ok", "data": data, "count": len(data)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/risk")
def risk_all():
    try:
        data = get_risk()
        return jsonify({"status": "ok", "data": data, "count": len(data)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/risk/<country_code>")
def risk_country(country_code):
    try:
        data = get_risk()
        country = country_code.upper()
        if country not in data:
            return jsonify({"status": "error", "message": f"Country {country} not found"}), 404
        return jsonify({"status": "ok", "data": data[country]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/stress")
def stress():
    try:
        data = get_stress()
        return jsonify({"status": "ok", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/tension")
def tension():
    try:
        risks = get_risk()
        data  = compute_geopolitical_tension_index(risks)
        return jsonify({"status": "ok", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/sectors")
def sectors():
    try:
        news = get_news()
        data = compute_sector_impacts(news)
        return jsonify({"status": "ok", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/dashboard")
def dashboard():
    """Single endpoint — everything the frontend needs"""
    try:
        market  = get_market()
        news    = get_news()
        risks   = get_risk()
        stress  = get_stress()
        tension = compute_geopolitical_tension_index(risks)
        sectors = compute_sector_impacts(news)

        # Top movers
        movers = sorted(market.values(), key=lambda x: abs(x['change_pct']), reverse=True)[:5]

        # Top risk countries
        top_risks = sorted(risks.values(), key=lambda x: x['risk_score'], reverse=True)[:8]

        # Recent news (last 5)
        recent_news = sorted(news, key=lambda x: x.get('publishedAt',''), reverse=True)[:5]

        return jsonify({
            "status":       "ok",
            "timestamp":    datetime.now().isoformat(),
            "market": {
                "prices":   market,
                "movers":   movers,
                "stress":   stress,
            },
            "geopolitical": {
                "tension":    tension,
                "top_risks":  top_risks,
                "all_risks":  risks,
            },
            "news": {
                "recent":   recent_news,
                "total":    len(news),
            },
            "sectors":      sectors,
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ─── Run ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  GeoFinance Intelligence Platform API")
    print("  http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000, threaded=True)