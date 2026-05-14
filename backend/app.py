# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time
from datetime import datetime

from news_fetcher import get_processed_news, fetch_geopolitical_news, fetch_country_news
from market_data import fetch_live_prices, compute_market_stress, fetch_historical
from sentiment import analyze_articles, compute_country_sentiment
from risk_model import (
    compute_all_country_risks,
    compute_sector_impacts,
    compute_geopolitical_tension_index,
    COUNTRY_RISK_PROFILES
)
from geo_analysis import (
    proximity_risk_analysis,
    geospatial_summary,
    classify_geospatial_features,
    wkt_to_geojson,
    geojson_to_wkt
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

def get_news():
    if is_stale("news") or not _cache["news"]["data"]:
        raw = get_processed_news()
        _cache["news"]["data"] = raw
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
        "version": "1.1.0",
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
            "/api/geo/proximity",
            "/api/geo/summary",
            "/api/geo/features",
            "/api/geo/convert",
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

        movers      = sorted(market.values(), key=lambda x: abs(x['change_pct']), reverse=True)[:5]
        top_risks   = sorted(risks.values(), key=lambda x: x['risk_score'], reverse=True)[:8]
        recent_news = sorted(news, key=lambda x: x.get('publishedAt', ''), reverse=True)[:5]

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

# ─── Geospatial Routes ─────────────────────────────────────────

@app.route("/api/geo/proximity")
def geo_proximity():
    """
    Geopolitical contagion analysis — find all countries within radius_km
    of an origin country, ranked by combined proximity and risk score.

    Query params:
        country   (str)   ISO-2 code, e.g. UA, RU, CN  [default: US]
        radius_km (float) search radius in kilometres   [default: 2000]

    Example: /api/geo/proximity?country=UA&radius_km=1500
    """
    try:
        origin    = request.args.get("country", "US").upper()
        radius_km = request.args.get("radius_km", 2000, type=float)
        risks     = get_risk()
        data      = proximity_risk_analysis(origin, radius_km, risks)
        return jsonify({"status": "ok", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/geo/summary")
def geo_summary():
    """
    High-level geospatial risk summary — global avg risk, spatial lag,
    high-risk country count, and top spatial risk index scores.
    """
    try:
        risks = get_risk()
        data  = geospatial_summary(risks)
        return jsonify({"status": "ok", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/geo/features")
def geo_features():
    """
    ML-ready geospatial feature set — each country as a spatial feature vector
    with geometry (WKT + GeoJSON), risk score, sentiment, spatial lag, and
    nearest high-risk country distance.
    """
    try:
        risks = get_risk()
        data  = classify_geospatial_features(risks)
        return jsonify({"status": "ok", "data": data, "count": len(data)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/geo/convert", methods=["POST"])
def geo_convert():
    """
    Geometry format conversion between WKT and GeoJSON.

    POST body (JSON):
        { "wkt": "POINT (77.21 28.61)" }          → returns GeoJSON geometry
        { "geojson": { "type": "Point", ... } }   → returns WKT string
    """
    try:
        body = request.get_json(force=True)
        if not body:
            return jsonify({"status": "error", "message": "Request body required"}), 400

        if "wkt" in body:
            result = wkt_to_geojson(body["wkt"])
            return jsonify({"status": "ok", "geojson": result})
        elif "geojson" in body:
            result = geojson_to_wkt(body["geojson"])
            return jsonify({"status": "ok", "wkt": result})
        else:
            return jsonify({"status": "error", "message": "Provide either 'wkt' or 'geojson' key"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ─── Run ───────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  GeoFinance Intelligence Platform API v1.1")
    print("  http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000, threaded=True)