from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

_kw_model = None

def get_kw_model():
    global _kw_model
    if _kw_model is None:
        print("[nlp] Loading keyword model...")
        _kw_model = KeyBERT(
            model=SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        )
        print("[nlp] Keyword model loaded.")
    return _kw_model


def extract_keywords(title: str, description: str, tags: list) -> list:
    try:
        # Combine all text sources
        tags_text = " ".join(tags) if tags else ""
        combined = f"{title}. {description}. {tags_text}"
        
        if not combined.strip():
            return []

        model = get_kw_model()
        keywords = model.extract_keywords(
            combined,
            keyphrase_ngram_range=(1, 2),  # single words and bigrams
            stop_words=None,               # no stopwords — model handles it
            top_n=10
        )
        # Return just the keyword strings, not the scores
        return [kw[0] for kw in keywords]
    
    except Exception as e:
        print(f"[keywords] Error: {e}")
        return []