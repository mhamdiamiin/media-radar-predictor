import os
import json
from mistralai import Mistral
from dotenv import load_dotenv
from app.config import SCORE_REVIEW_PROMPT

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))


def review_score(article: dict) -> dict:
    try:
        title        = article.get("title", "")
        description  = article.get("description", "")[:500]
        category     = article.get("category_normalized", "")
        score        = article.get("tendance", {}).get("score", 0)
        novelty      = article.get("_novelty", "inconnu")
        cluster_size = article.get("_cluster_size", 1)

        prompt = SCORE_REVIEW_PROMPT.format(
            title=title,
            description=description,
            category=category,
            score=score,
            novelty=novelty,
            cluster_size=cluster_size
        )

        response = client.chat.complete(
            model="open-mistral-nemo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.0
        )

        content = response.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()

        result        = json.loads(content)
        revised_score = float(result.get("revised_score", score))
        changed       = bool(result.get("changed", False))
        reason        = str(result.get("reason", ""))

        revised_score = round(max(0.0, min(1.0, revised_score)), 4)

        return {
            "revised_score": revised_score,
            "changed":       changed,
            "reason":        reason
        }

    except Exception as e:
        print(f"[agent] Error: {e}")
        return {
            "revised_score": article.get("tendance", {}).get("score", 0),
            "changed":       False,
            "reason":        "fallback — agent unavailable"
        }