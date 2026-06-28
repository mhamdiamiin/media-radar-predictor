import spacy

_nlp_model = None

def get_nlp_model():
    global _nlp_model
    if _nlp_model is None:
        print("[nlp] Loading spaCy model...")
        _nlp_model = spacy.load("fr_core_news_md")
        print("[nlp] spaCy model loaded.")
    return _nlp_model


def extract_entities(title: str, description: str) -> list:
    try:
        combined = f"{title}. {description}"
        
        if not combined.strip():
            return []

        nlp = get_nlp_model()
        doc = nlp(combined[:1000])  # spaCy has token limits too

        entities = []
        seen = set()

        for ent in doc.ents:
            # Only keep relevant entity types
            if ent.label_ in ("PER", "ORG", "LOC", "GPE"):
                key = (ent.text.strip(), ent.label_)
                if key not in seen:
                    seen.add(key)
                    entities.append({
                        "text":  ent.text.strip(),
                        "label": ent.label_  # PER=person, ORG=org, LOC=location
                    })

        return entities

    except Exception as e:
        print(f"[entities] Error: {e}")
        return []