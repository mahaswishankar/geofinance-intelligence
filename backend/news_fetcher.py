# =============================================================================
# GEOFINANCE INTELLIGENCE - NEWS FETCHER
# Fetches geopolitical news and categorizes by country/region
# =============================================================================

import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv('NEWS_API_KEY')
BASE_URL = "https://newsapi.org/v2/everything"

# ── Country/Region mappings ───────────────────────────────────
COUNTRY_KEYWORDS = {
    'US':     ['United States', 'Washington', 'Federal Reserve', 'Wall Street', 'Pentagon'],
    'CN':     ['China', 'Beijing', 'Chinese', 'PLA', 'CCP', 'Shanghai'],
    'RU':     ['Russia', 'Moscow', 'Putin', 'Kremlin', 'Russian'],
    'IN':     ['India', 'New Delhi', 'Modi', 'RBI', 'Indian'],
    'GB':     ['United Kingdom', 'London', 'Brexit', 'Bank of England'],
    'DE':     ['Germany', 'Berlin', 'Bundesbank', 'German'],
    'JP':     ['Japan', 'Tokyo', 'Bank of Japan', 'Japanese', 'Yen'],
    'SA':     ['Saudi Arabia', 'Riyadh', 'OPEC', 'Saudi'],
    'IR':     ['Iran', 'Tehran', 'Iranian', 'IRGC'],
    'IL':     ['Israel', 'Tel Aviv', 'Israeli', 'IDF'],
    'UA':     ['Ukraine', 'Kyiv', 'Ukrainian', 'Zelensky'],
    'KP':     ['North Korea', 'Kim Jong', 'Pyongyang', 'DPRK'],
    'BR':     ['Brazil', 'Brasilia', 'Brazilian', 'Lula'],
    'FR':     ['France', 'Paris', 'Macron', 'French'],
    'TR':     ['Turkey', 'Ankara', 'Erdogan', 'Turkish'],
}

# ── Event categories ──────────────────────────────────────────
EVENT_CATEGORIES = {
    'conflict':    ['war', 'attack', 'missile', 'military', 'troops', 'invasion', 'strike', 'bomb', 'combat', 'casualty'],
    'sanctions':   ['sanctions', 'embargo', 'ban', 'restriction', 'freeze', 'penalty', 'tariff'],
    'election':    ['election', 'vote', 'ballot', 'poll', 'democracy', 'referendum', 'campaign'],
    'trade':       ['trade', 'export', 'import', 'tariff', 'deal', 'agreement', 'commerce', 'supply chain'],
    'energy':      ['oil', 'gas', 'OPEC', 'energy', 'pipeline', 'crude', 'petroleum', 'LNG'],
    'finance':     ['GDP', 'inflation', 'interest rate', 'central bank', 'currency', 'recession', 'economy'],
    'diplomacy':   ['summit', 'treaty', 'alliance', 'UN', 'NATO', 'diplomatic', 'ambassador', 'negotiation'],
    'technology':  ['chip', 'semiconductor', 'AI', 'cyber', 'hack', 'tech war', 'data'],
}

def fetch_geopolitical_news(query="geopolitical risk finance markets", days_back=2, page_size=20):
    """Fetch news from NewsAPI"""
    try:
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        params = {
            'q': query,
            'from': from_date,
            'sortBy': 'relevancy',
            'pageSize': page_size,
            'language': 'en',
            'apiKey': NEWS_API_KEY
        }
        response = requests.get(BASE_URL, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            print(f"✅ Fetched {len(articles)} articles")
            return articles
        else:
            print(f"❌ NewsAPI error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return []

def fetch_country_news(country_code, page_size=5):
    """Fetch news for a specific country"""
    keywords = COUNTRY_KEYWORDS.get(country_code, [country_code])
    query = ' OR '.join([f'"{k}"' for k in keywords[:3]])
    return fetch_geopolitical_news(query=query, page_size=page_size)

def classify_event(text):
    """Classify news event into category"""
    text_lower = text.lower()
    scores = {}
    for category, keywords in EVENT_CATEGORIES.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        if score > 0:
            scores[category] = score
    if scores:
        return max(scores, key=scores.get)
    return 'general'

def detect_countries(text):
    """Detect which countries are mentioned in text"""
    text_lower = text.lower()
    detected = []
    for country_code, keywords in COUNTRY_KEYWORDS.items():
        if any(kw.lower() in text_lower for kw in keywords):
            detected.append(country_code)
    return detected if detected else ['GLOBAL']

def process_articles(articles):
    """Process raw articles into structured format"""
    processed = []
    for article in articles:
        if not article.get('title') or article['title'] == '[Removed]':
            continue
        text = f"{article.get('title', '')} {article.get('description', '')}"
        processed.append({
            'title':        article.get('title', ''),
            'description':  article.get('description', ''),
            'url':          article.get('url', ''),
            'source':       article.get('source', {}).get('name', 'Unknown'),
            'published_at': article.get('publishedAt', ''),
            'event_type':   classify_event(text),
            'countries':    detect_countries(text),
            'text':         text
        })
    return processed

def get_processed_news(query="geopolitical conflict sanctions war trade finance", page_size=30):
    """Main function — fetch + process news"""
    print("Fetching news...")
    articles = fetch_geopolitical_news(query=query, page_size=page_size)
    processed = process_articles(articles)
    print(f"✅ Processed {len(processed)} articles")
    return processed

if __name__ == "__main__":
    news = get_processed_news()
    for i, article in enumerate(news[:5]):
        print(f"\n--- Article {i+1} ---")
        print(f"Title:      {article['title']}")
        print(f"Source:     {article['source']}")
        print(f"Event Type: {article['event_type']}")
        print(f"Countries:  {article['countries']}")