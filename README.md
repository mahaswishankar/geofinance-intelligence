# 🌍 GeoFinance Intelligence Platform

<div align="center">

![GeoFinance Banner](https://img.shields.io/badge/GeoFinance-Intelligence%20Platform-00d4ff?style=for-the-badge&logo=globe&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-1.1-139C5A?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A real-time geopolitical risk & financial market analytics platform that maps global conflict zones, sanctions, and instability to live market movements — built for institutional-grade intelligence.**

[Features](#-features) • [Tech Stack](#-tech-stack) • [Installation](#-installation) • [Architecture](#-architecture) • [Geospatial Analysis](#-geospatial-analysis-module) • [Screenshots](#-screenshots)

</div>

---

## 🎯 What It Does

GeoFinance Intelligence bridges **geopolitics and financial markets** in real time. It aggregates live news, scores country-level risk across 150+ nations using **FinBERT transformer-based sentiment analysis**, performs **spatial proximity and contagion modelling** via GeoPandas/Shapely, and surfaces how geopolitical events propagate into equity, commodity, forex, and crypto markets.

Built as a production-grade full-stack data science project targeting financial analytics roles.

---

## ✨ Features

### 🌐 Earth Pulse — Interactive 3D Globe
- **Photorealistic 3D globe** rendered on HTML5 Canvas using d3-geo orthographic projection
- Deep space background with **350 twinkling stars** and animated great-circle orbital arcs
- **Multi-layer 3D lighting** — specular highlight, directional shadow, edge curvature darkening
- Countries **color-coded by real-time geopolitical risk score** (green → red)
- Drag to rotate, click any country → instantly loads market impact panel
- **Floating AI Signals panel** with live BUY/SELL/HOLD signals, confidence scores, and AI analysis

### 🗺️ Geo Map — Country-to-Market Intelligence
- Full-screen **interactive flat world map** (react-simple-maps + TopoJSON)
- Click any country → see the **correlated financial asset** (Russia → Oil, Ukraine → Gold, US → S&P 500)
- **30-day price history** with toggle between Candlestick and Area chart views
- **Sector exposure bars** — Energy, Defense, Finance impact driven by risk score
- Asset selector across GLD, USO, SPY, EEM

### ⚡ AI Signals — Trade Intelligence Engine
- **6 active AI-generated signals** across asset classes: Commodities, Equities, Forex, Crypto, Defense
- Each signal includes: confidence %, bullish/bearish strength, volatility tag, triggering geopolitical event
- Full **trade setup** — entry, stop loss, target, risk/reward ratio, ATR, max P&L
- Win rate analysis and reliability scoring
- Filter by asset class, search by ticker

### 🧠 FinBERT Sentiment Pipeline (Live)
- **ProsusAI/finbert** transformer model loaded via HuggingFace — production sentiment classification
- Processes news headlines and descriptions into **positive / negative / neutral** probability distributions
- Sentiment score computed as `P(positive) − P(negative)` — feeds directly into country risk model
- Batch processing with CPU inference, 512-token truncation, graceful fallback on errors
- Country-level sentiment aggregation across all news articles per ISO-2 code

### 📊 Markets Dashboard
- **Live KPI strip** — JPM, GS, SPY, GLD, VIX with real-time price and % change
- **60-day price history** area chart for any ticker
- Market stress index and geo-tension index
- Full market grid: BAC, EEM, TLT, USO and more

### 📡 Live Intelligence Feed
- Real-time news ingestion via NewsAPI
- FinBERT sentiment tags — BULLISH / BEARISH / NEUTRAL with probability scores
- Event type classification (energy, sanctions, conflict, trade)
- Country entity extraction from news headlines

---

## 🗺️ Geospatial Analysis Module

`backend/geo_analysis.py` extends the platform with a dedicated spatial intelligence layer built on **GeoPandas** and **Shapely**. This module engineers geographic features for ML pipelines and models geopolitical risk as a spatially-distributed phenomenon.

### Core Capabilities

**Proximity & Contagion Modelling**
```python
# Find all countries within 1500km of Ukraine, ranked by contagion risk
result = proximity_risk_analysis("UA", 1500, country_risks)
# Returns: nearby countries with distance_km, bearing, proximity_weight, contagion_score
# Contagion score = risk_score × proximity_decay_weight
```

**Spatial Feature Engineering**
```python
# Generate ML-ready feature vectors for each country
features = classify_geospatial_features(country_risks)
# Each feature includes:
#   geometry_wkt       — Point geometry in WKT format
#   geometry_geojson   — GeoJSON Point geometry
#   risk_score         — Country risk (0–100)
#   neighbor_avg_risk  — Spatial lag: avg risk of countries within 2000km
#   nearest_high_risk_km — Proximity to nearest critical-risk country
#   is_high_risk       — Binary label (risk_score ≥ 70)
```

**Geometry Format Conversion**
```python
# WKT ↔ GeoJSON round-trip conversion
wkt  = geojson_to_wkt({"type": "Point", "coordinates": [77.21, 28.61]})
# → "POINT (77.21 28.61)"
geoj = wkt_to_geojson("POINT (77.21 28.61)")
# → {"type": "Point", "coordinates": [77.21, 28.61]}
```

**High-Risk Zone Polygon**
```python
# Dissolve all high-risk country geometries into a unified Shapely polygon
zone = high_risk_zone_polygon(country_risks, threshold=70.0)
# Uses unary_union — returns GeoJSON feature with avg_risk_score and country_count
```

**Haversine Distance**
```python
# Great-circle distance between any two coordinates
dist = haversine_distance(-0.12, 51.51, 139.69, 35.68)  # London → Tokyo
# → 9558.4 km
```

### Spatial API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/geo/proximity` | GET | Contagion analysis — countries within `radius_km` of `country`, ranked by proximity-weighted risk |
| `/api/geo/summary` | GET | Global spatial risk summary — avg risk, spatial lag, high-risk zones, top spatial risk index |
| `/api/geo/features` | GET | ML-ready geospatial feature vectors for all countries (WKT + GeoJSON + spatial lag) |
| `/api/geo/convert` | POST | Geometry format conversion — WKT → GeoJSON or GeoJSON → WKT |

**Example — Proximity Analysis:**
```bash
GET /api/geo/proximity?country=UA&radius_km=1500
```
```json
{
  "origin": { "iso2": "UA", "risk_score": 90, "centroid": [31.17, 48.38] },
  "radius_km": 1500,
  "country_count": 2,
  "nearby_countries": [
    {
      "iso2": "PL", "distance_km": 941.7, "bearing_deg": 299.2,
      "risk_score": 30, "proximity_weight": 0.372, "contagion_score": 11.17
    },
    {
      "iso2": "TR", "distance_km": 1097.0, "bearing_deg": 161.2,
      "risk_score": 60, "proximity_weight": 0.269, "contagion_score": 16.12
    }
  ],
  "avg_contagion_score": 13.64
}
```

**Example — Geometry Conversion:**
```bash
POST /api/geo/convert
Content-Type: application/json
{ "wkt": "POINT (77.21 28.61)" }
```
```json
{ "status": "ok", "geojson": { "type": "Point", "coordinates": [77.21, 28.61] } }
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python / Flask** | REST API server |
| **FinBERT (ProsusAI)** | Transformer-based financial news sentiment analysis |
| **GeoPandas 1.1** | Spatial joins, GeoDataFrame operations, geometry processing |
| **Shapely 2.1** | Geometric operations — Point, Polygon, unary_union, WKT/GeoJSON |
| **yfinance** | Live market data (prices, OHLCV history) |
| **NewsAPI** | Real-time global news ingestion |
| **Pandas / NumPy** | Data processing and risk calculations |
| **Flask-CORS** | Cross-origin API access |

### Frontend
| Technology | Purpose |
|---|---|
| **React 18** | UI framework |
| **d3-geo + TopoJSON** | 3D globe rendering (orthographic projection) |
| **react-simple-maps** | 2D interactive world map |
| **Recharts** | Area charts, bar/candlestick charts |
| **Axios** | API communication |
| **HTML5 Canvas** | Custom globe renderer with WebGL-style shading |

### Data & Intelligence
| Technology | Purpose |
|---|---|
| **Custom Risk Model** | 150+ country geopolitical risk scores (0–100) |
| **Geospatial Feature Engine** | Spatial lag, proximity decay, contagion scoring |
| **World Atlas TopoJSON** | Geographic country boundary data |
| **Country-Asset Mapping** | Geopolitical event → market asset correlation engine |
| **Sector Impact Engine** | Risk score propagation to 8 market sectors |

---

## 🏗️ Architecture

```
geofinance_intelligence/
│
├── backend/
│   ├── app.py              # Flask REST API v1.1 — all endpoints
│   ├── geo_analysis.py     # Geospatial analysis — GeoPandas/Shapely spatial ops
│   ├── market_data.py      # yfinance integration, price fetching, stress index
│   ├── risk_model.py       # Geopolitical risk scoring engine (150+ countries)
│   ├── news_fetcher.py     # NewsAPI ingestion + country entity extraction
│   ├── sentiment.py        # FinBERT sentiment pipeline (ProsusAI/finbert)
│   ├── requirements.txt    # Python dependencies
│   └── data/               # Static reference data
│
├── frontend/geofinance-app/
│   ├── src/
│   │   ├── App.js          # Main React app — all 3 tabs + globe
│   │   ├── App.css         # Global styles
│   │   └── index.js        # React entry point
│   ├── public/
│   └── package.json
│
├── models/                 # Saved model artifacts
├── outputs/                # Data exports
└── venv/                   # Python virtual environment
```

### Full API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/dashboard` | GET | Full dashboard — market prices, risk scores, news, sectors |
| `/api/market` | GET | Live market prices for all tracked tickers |
| `/api/market/history/:ticker` | GET | OHLCV price history (default: 90 days) |
| `/api/risk` | GET | All country risk scores |
| `/api/risk/:country` | GET | Individual country risk breakdown |
| `/api/news` | GET | Latest news with FinBERT sentiment tags |
| `/api/stress` | GET | Market stress index |
| `/api/tension` | GET | GDP-weighted geopolitical tension index |
| `/api/sectors` | GET | Sector impact scores across 8 market sectors |
| `/api/geo/proximity` | GET | Spatial contagion analysis — proximity-weighted risk propagation |
| `/api/geo/summary` | GET | Global geospatial risk summary with spatial lag |
| `/api/geo/features` | GET | ML-ready geospatial feature vectors (WKT + GeoJSON) |
| `/api/geo/convert` | POST | WKT ↔ GeoJSON geometry format conversion |

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- NewsAPI key (free at [newsapi.org](https://newsapi.org))

### 1. Clone the repository
```bash
git clone https://github.com/mahaswishankar/geofinance-intelligence.git
cd geofinance_intelligence
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the `backend/` directory:
```env
NEWS_API_KEY=your_newsapi_key_here
```

### 4. Start the Backend
```bash
cd backend
python app.py
# API runs on http://localhost:5000
```

### 5. Frontend Setup
```bash
cd frontend/geofinance-app
npm install
npm start
# App runs on http://localhost:3000
```

---

## 🧠 Risk Scoring Model

The geopolitical risk engine scores 150+ countries across multiple dimensions:

```python
risk_score = weighted_average(
    political_stability    * 0.30,
    economic_vulnerability * 0.25,
    conflict_index         * 0.25,
    sanctions_exposure     * 0.10,
    news_sentiment_signal  * 0.10   # FinBERT score × −15 adjustment
)
```

**Score Thresholds:**
- 🟢 `0–25` — LOW risk
- 🟡 `25–50` — MODERATE risk
- 🟠 `50–75` — HIGH risk
- 🔴 `75–100` — CRITICAL risk

---

## 📈 Country → Asset Correlation Map

| Country/Region | Correlated Asset | Rationale |
|---|---|---|
| Russia, Saudi Arabia, Iran, Iraq | **USO** (Crude Oil) | Oil supply shock risk |
| Ukraine, Israel, Syria | **GLD** (Gold) | Safe haven demand |
| US, Germany, UK, Japan | **SPY** (S&P 500) | Systemic market risk |
| China, India, Indonesia | **EEM** (Emerging Markets) | EM contagion risk |

---

## 🔮 Roadmap

- [ ] Deploy backend to **Render** + frontend to **Vercel**
- [ ] Add WebSocket support for real-time price streaming
- [ ] Historical backtesting — "what happened to oil when X conflict started?"
- [ ] Portfolio impact calculator — "how does a Russia escalation affect my holdings?"
- [ ] Mobile responsive design
- [ ] Extend geospatial layer with full Natural Earth boundary geometries

---

## 👤 Author

**Mahaswi Shankar**
B.Tech CSE @ Bennett University (Times of India Group)
Specializing in Financial ML, Geospatial Data Science & Business Intelligence

[![GitHub](https://img.shields.io/badge/GitHub-mahaswishankar-181717?style=flat&logo=github)](https://github.com/mahaswishankar)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-mahaswishankar1-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/mahaswishankar1)
