from transformers import pipeline as hf_pipeline

_sentiment_pipeline = None

def get_sentiment_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        print("[nlp] Loading sentiment model...")
        _sentiment_pipeline = hf_pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
            top_k=1
        )
        print("[nlp] Sentiment model loaded.")
    return _sentiment_pipeline


def analyze_sentiment(text: str) -> dict:
    if not text or not text.strip():
        return {"label": "neutral", "score": 0.0}
    
    try:
        model = get_sentiment_pipeline()
        # Model accepts max 512 tokens — truncate safely
        truncated = text[:1000]
        result = model(truncated)[0][0]
        return {
            "label": result["label"].lower(),  # positive / negative / neutral
            "score": round(result["score"], 4)
        }
    except Exception as e:
        print(f"[sentiment] Error: {e}")
        return {"label": "neutral", "score": 0.0}