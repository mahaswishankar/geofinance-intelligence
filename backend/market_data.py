# market_data.py
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

TICKERS = {
    "JPM":   {"name": "JPMorgan Chase",    "sector": "Banking"},
    "GS":    {"name": "Goldman Sachs",     "sector": "Banking"},
    "BAC":   {"name": "Bank of America",   "sector": "Banking"},
    "SPY":   {"name": "S&P 500 ETF",       "sector": "Index"},
    "GLD":   {"name": "Gold ETF",          "sector": "Commodity"},
    "USO":   {"name": "Oil ETF",           "sector": "Commodity"},
    "DX-Y.NYB": {"name": "US Dollar Index","sector": "Currency"},
    "^VIX":  {"name": "Volatility Index",  "sector": "Risk"},
    "TLT":   {"name": "20Y Treasury ETF",  "sector": "Bonds"},
    "EEM":   {"name": "Emerging Markets",  "sector": "Index"},
}

def fetch_live_prices():
    """Fetch current price + daily change for all tickers"""
    results = {}
    
    for ticker, meta in TICKERS.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            
            if hist.empty:
                continue
            
            current_price = float(hist['Close'].iloc[-1])
            prev_price    = float(hist['Close'].iloc[-2])
            change_pct    = ((current_price - prev_price) / prev_price) * 100
            volume        = float(hist['Volume'].iloc[-1])
            
            # 5-day volatility
            returns = hist['Close'].pct_change().dropna()
            volatility = float(returns.std() * np.sqrt(252) * 100)
            
            results[ticker] = {
                "ticker":       ticker,
                "name":         meta["name"],
                "sector":       meta["sector"],
                "price":        round(current_price, 2),
                "change_pct":   round(change_pct, 2),
                "volume":       int(volume),
                "volatility":   round(volatility, 2),
                "direction":    "up" if change_pct > 0 else "down",
                "timestamp":    datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
    
    return results

def fetch_historical(ticker, days=90):
    """Fetch historical OHLCV for charting"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=f"{days}d")
        
        if hist.empty:
            return []
        
        data = []
        for date, row in hist.iterrows():
            data.append({
                "date":   date.strftime("%Y-%m-%d"),
                "open":   round(float(row['Open']), 2),
                "high":   round(float(row['High']), 2),
                "low":    round(float(row['Low']), 2),
                "close":  round(float(row['Close']), 2),
                "volume": int(row['Volume'])
            })
        return data
    except Exception as e:
        print(f"Error fetching history for {ticker}: {e}")
        return []

def compute_market_stress():
    """Compute a Market Stress Index from VIX + bonds + dollar"""
    try:
        prices = fetch_live_prices()
        
        vix_level  = prices.get("^VIX", {}).get("price", 20)
        gold_chg   = prices.get("GLD",  {}).get("change_pct", 0)
        spy_chg    = prices.get("SPY",  {}).get("change_pct", 0)
        tlt_chg    = prices.get("TLT",  {}).get("change_pct", 0)

        # Stress formula: high VIX + gold rising + equities falling = stress
        stress = (
            min(vix_level / 80 * 100, 100) * 0.4 +
            max(-spy_chg * 5, 0)            * 0.3 +
            max(gold_chg * 3, 0)            * 0.2 +
            max(tlt_chg * 2, 0)             * 0.1
        )
        stress = round(min(max(stress, 0), 100), 1)

        if stress < 25:   level = "LOW"
        elif stress < 50: level = "MODERATE"
        elif stress < 75: level = "HIGH"
        else:             level = "EXTREME"

        return {
            "stress_index": stress,
            "level":        level,
            "vix":          vix_level,
            "components": {
                "vix_contribution":    round(min(vix_level / 80 * 100, 100) * 0.4, 1),
                "equity_contribution": round(max(-spy_chg * 5, 0) * 0.3, 1),
                "gold_contribution":   round(max(gold_chg * 3, 0) * 0.2, 1),
                "bonds_contribution":  round(max(tlt_chg * 2, 0) * 0.1, 1),
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error computing stress: {e}")
        return {"stress_index": 0, "level": "UNKNOWN"}

if __name__ == "__main__":
    print("Fetching live market prices...")
    prices = fetch_live_prices()
    for ticker, data in prices.items():
        arrow = "▲" if data['direction'] == 'up' else "▼"
        print(f"  {ticker:12} ${data['price']:>8.2f}  {arrow} {data['change_pct']:+.2f}%  Vol: {data['volatility']:.1f}%")

    print("\nComputing Market Stress Index...")
    stress = compute_market_stress()
    print(f"  Stress Index: {stress['stress_index']} / 100  →  {stress['level']}")
    print(f"  VIX: {stress['vix']}")