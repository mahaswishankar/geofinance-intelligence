# sentiment.py
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import re
from datetime import datetime

# Global model (loaded once)
_sentiment_pipeline = None

def load_finbert():
    """Load FinBERT model (downloads once, cached after)"""
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        print("Loading FinBERT model...")
        model_name = "ProsusAI/finbert"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        _sentiment_pipeline = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            device=-1,  # CPU
            top_k=None  # return all scores
        )
        print("FinBERT loaded!")
    return _sentiment_pipeline

def clean_text(text):
    """Clean article text for analysis"""
    if not text:
        return ""
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    text = text.strip()
    return text[:512]  # FinBERT max tokens

def analyze_sentiment(text):
    """Run FinBERT on a single text, return sentiment + scores"""
    pipe = load_finbert()
    
    cleaned = clean_text(text)
    if not cleaned:
        return {"label": "neutral", "score": 0.0, "positive": 0.33, "negative": 0.33, "neutral": 0.34}
    
    try:
        results = pipe(cleaned)[0]
        scores = {r['label'].lower(): r['score'] for r in results}
        
        # Dominant label
        label = max(scores, key=scores.get)
        
        # Sentiment score: +1 fully positive, -1 fully negative
        sentiment_score = scores.get('positive', 0) - scores.get('negative', 0)
        
        return {
            "label":     label,
            "score":     round(sentiment_score, 3),
            "positive":  round(scores.get('positive', 0), 3),
            "negative":  round(scores.get('negative', 0), 3),
            "neutral":   round(scores.get('neutral', 0), 3),
        }
    except Exception as e:
        print(f"Sentiment error: {e}")
        return {"label": "neutral", "score": 0.0, "positive": 0.33, "negative": 0.33, "neutral": 0.34}

def analyze_articles(articles):
    """Batch analyze a list of articles"""
    load_finbert()  # ensure loaded
    
    enriched = []
    for article in articles:
        text = f"{article.get('title', '')} {article.get('description', '')}"
        sentiment = analyze_sentiment(text)
        
        enriched.append({
            **article,
            "sentiment":       sentiment["label"],
            "sentiment_score": sentiment["score"],
            "positive_prob":   sentiment["positive"],
            "negative_prob":   sentiment["negative"],
            "neutral_prob":    sentiment["neutral"],
            "analyzed_at":     datetime.now().isoformat()
        })
    
    return enriched

def compute_country_sentiment(articles, country_code):
    """Aggregate sentiment for a specific country"""
    country_articles = [a for a in articles if a.get('country') == country_code]
    
    if not country_articles:
        return {"country": country_code, "sentiment": "neutral", "score": 0.0, "article_count": 0}
    
    scores = [a.get('sentiment_score', 0) for a in country_articles]
    avg_score = sum(scores) / len(scores)
    
    if avg_score > 0.1:    label = "positive"
    elif avg_score < -0.1: label = "negative"
    else:                  label = "neutral"
    
    return {
        "country":       country_code,
        "sentiment":     label,
        "score":         round(avg_score, 3),
        "article_count": len(country_articles),
        "articles":      country_articles
    }

if __name__ == "__main__":
    print("Testing FinBERT sentiment analysis...")
    
    test_headlines = [
        "JPMorgan reports record profits as interest rates boost banking sector",
        "Markets crash as geopolitical tensions escalate in Eastern Europe",
        "Federal Reserve holds interest rates steady amid inflation concerns",
        "Oil prices surge following OPEC production cuts announcement",
        "China's economy shows signs of slowdown, analysts warn of recession risk"
    ]
    
    for headline in test_headlines:
        result = analyze_sentiment(headline)
        emoji = "🟢" if result['label'] == 'positive' else "🔴" if result['label'] == 'negative' else "🟡"
        print(f"{emoji} [{result['label']:8}] score={result['score']:+.3f} | {headline[:60]}...")