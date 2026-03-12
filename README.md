# 🌍 GeoFinance Intelligence Platform

<div align="center">

![GeoFinance Banner](https://img.shields.io/badge/GeoFinance-Intelligence%20Platform-00d4ff?style=for-the-badge&logo=globe&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A real-time geopolitical risk & financial market analytics platform that maps global conflict zones, sanctions, and instability to live market movements — built for institutional-grade intelligence.**

[Features](#-features) • [Tech Stack](#-tech-stack) • [Installation](#-installation) • [Architecture](#-architecture) • [Screenshots](#-screenshots)

</div>

---

## 🎯 What It Does

GeoFinance Intelligence bridges **geopolitics and financial markets** in real time. It aggregates live news, scores country-level risk across 150+ nations, and surfaces how geopolitical events propagate into equity, commodity, forex, and crypto markets.

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

### 📊 Markets Dashboard
- **Live KPI strip** — JPM, GS, SPY, GLD, VIX with real-time price and % change
- **60-day price history** area chart for any ticker
- Market stress index and geo-tension index
- Full market grid: BAC, EEM, TLT, USO and more

### 📡 Live Intelligence Feed
- Real-time news ingestion via NewsAPI
- **FinBERT-style sentiment analysis** — BULLISH / BEARISH / NEUTRAL tags
- Event type classification (energy, sanctions, conflict, trade)
- Country entity extraction from news headlines

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python / Flask** | REST API server |
| **yfinance** | Live market data (prices, OHLCV history) |
| **NewsAPI** | Real-time global news ingestion |
| **VADER / TextBlob** | News sentiment analysis |
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
| **World Atlas TopoJSON** | Geographic country boundary data |
| **Country-Asset Mapping** | Geopolitical event → market asset correlation engine |
| **Sector Impact Engine** | Risk score propagation to 8 market sectors |

---

## 🏗️ Architecture

```
geofinance_intelligence/
│
├── backend/
│   ├── app.py              # Flask REST API — main entry point
│   ├── market_data.py      # yfinance integration, price fetching, stress index
│   ├── risk_model.py       # Geopolitical risk scoring engine (150+ countries)
│   ├── news_fetcher.py     # NewsAPI ingestion + country entity extraction
│   ├── sentiment.py        # Sentiment analysis pipeline (VADER + rules)
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

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/dashboard` | GET | Full dashboard data — market prices, risk scores, news, sectors |
| `/api/market/history/:ticker` | GET | OHLCV price history for any ticker (default: 60 days) |
| `/api/risk/:country` | GET | Individual country risk score and breakdown |
| `/api/news` | GET | Latest processed news with sentiment tags |

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- NewsAPI key (free at [newsapi.org](https://newsapi.org))

### 1. Clone the repository
```bash
git clone https://github.com/mahaswishankar/geofinance_intelligence.git
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

pip install flask flask-cors pandas numpy requests yfinance textblob vaderSentiment
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
# Server runs on http://localhost:5000
```

### 5. Frontend Setup
```bash
cd frontend/geofinance-app
npm install
npm start
# App runs on http://localhost:3000
```

---

## 📡 API Response Example

```json
// GET /api/dashboard
{
  "market": {
    "prices": {
      "JPM": { "price": 287.52, "change_pct": -0.42, "name": "JPMorgan Chase", "sector": "Banking" },
      "GLD": { "price": 476.24, "change_pct": -0.34 }
    },
    "stress": { "stress_index": 13, "level": "LOW" }
  },
  "geopolitical": {
    "tension": { "index": 45.4, "level": "TENSE" },
    "top_risks": [
      { "country": "RU", "risk_score": 100, "level": "CRITICAL", "region": "Europe" }
    ],
    "all_risks": { "RU": { "risk_score": 100, "economy": 35, "stability": 20 } }
  },
  "news": {
    "recent": [
      { "title": "...", "sentiment": "negative", "event_type": "energy", "countries": ["IR"] }
    ]
  }
}
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
    news_sentiment_signal  * 0.10
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
- [ ] Integrate **FinBERT** for more accurate financial sentiment
- [ ] Add portfolio impact calculator — "how does a Russia escalation affect my portfolio?"
- [ ] Historical backtesting — "what happened to oil when X conflict started?"
- [ ] Mobile responsive design

---

## 👤 Author

**Mahaswi Shankar**  
B.Tech CSE @ Bennett University (Times of India Group)  
Specializing in Financial ML, Big Data Analytics & Business Intelligence

[![GitHub](https://img.shields.io/badge/GitHub-mahaswishankar-181717?style=flat&logo=github)](https://github.com/mahaswishankar)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-mahaswishankar1-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/mahaswishankar1)

---



