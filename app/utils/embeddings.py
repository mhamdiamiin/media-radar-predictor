from sentence_transformers import SentenceTransformer

_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        print("[nlp] Loading embedding model...")
        _embedding_model = SentenceTransformer(
            "paraphrase-multilingual-MiniLM-L12-v2"
        )
        print("[nlp] Embedding model loaded.")
    return _embedding_model


def generate_embedding(description: str) -> list:
    try:
        if not description or not description.strip():
            return []

        model = get_embedding_model()
        embedding = model.encode(description, convert_to_numpy=True)
        return embedding.tolist()  # MongoDB stores lists not numpy arrays

    except Exception as e:
        print(f"[embeddings] Error: {e}")
        return []