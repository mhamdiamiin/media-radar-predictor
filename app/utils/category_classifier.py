import os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

def classify_category(raw_category: str, description: str = "") -> str:
    """
    Pure Semantic Testing Mode.
    Hardcoded categories directly in the prompt to evaluate Mistral's zero-shot accuracy.
    """
    if not description:
        return "autre"

    # Define the exact target categories list locally for verification
    allowed_categories = [
        "sport", "politique", "international", "economie", "culture", 
        "tech", "societe", "sante", "justice", "divertissement"
    ]

    try:
        # Extract exactly the first 300 characters to keep token usage ultra-low
        short_description = description.strip()[:300]

        # Call the free-tier cloud model
        response = client.chat.complete(
            model="open-mistral-nemo",  
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un robot de classification de données médias ultra-strict. "
                        "Ton unique tâche est de lire un texte et de choisir le meilleur tag de classification.\n\n"
                        "Tu dois OBLIGATOIREMENT choisir un mot uniquement parmi cette liste exacte :\n"
                        "- sport\n"
                        "- politique\n"
                        "- international\n"
                        "- economie\n"
                        "- culture\n"
                        "- tech\n"
                        "- societe\n"
                        "- sante\n"
                        "- justice\n"
                        "- divertissement\n\n"
                        "RÈGLES CRITIQUES :\n"
                        "1. Ne réponds que par LE MOT EXACT choisi dans la liste.\n"
                        "2. Pas de phrases, pas de ponctuation, pas d'explications.\n"
                        "3. Si le texte ne correspond à absolument rien dans la liste, réponds par 'autre'."
                    )
                },
                {
                    "role": "user",
                    "content": f"Texte à classifier : {short_description}"
                }
            ],
            max_tokens=10,
            temperature=0.0  # Keep temperature at 0.0 for deterministic testing
        )

        predicted_category = response.choices[0].message.content.strip().lower()

        # Clean any accidental punctuation the model might return
        predicted_category = predicted_category.replace(".", "").replace(",", "")

        # Verify the model strictly returned one of your allowed strings
        if predicted_category in allowed_categories:
            return predicted_category
        elif predicted_category == "autre":
            return "autre"
        else:
            print(f"[mistral-test] Warning: Model returned an out-of-list label: '{predicted_category}'")
            return "autre"

    except Exception as e:
        print(f"[mistral-category] Error calling Cloud API: {e}")
        return "autre"