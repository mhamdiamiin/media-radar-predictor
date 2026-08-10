SITEMAP_URL = "https://www.mosaiquefm.net/fr/sitemap/news.xml"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36"
}

SITEMAP_NS = {
    "ns":    "http://www.sitemaps.org/schemas/sitemap/0.9",
    "image": "http://www.google.com/schemas/sitemap-image/1.1",
}

MONGODB_URL = "mongodb://localhost:27017/"
DB_NAME = "media_radar"
COLLECTION_NAME = "articles"

REQUEST_TIMEOUT = 10
RATE_LIMIT_DELAY = 1.5

CATEGORY_MAP = {
    "coupe-du-monde-2026":               "sport",
    "football":                          "sport",
    "actualites-sport-tunisie":          "sport",
    "sports-individuels-tunisie":        "sport",
    "mercato":                           "sport",
    "handball":                          "sport",
    "basket-ball":                       "sport",
    "national-tunisie":                  "politique",
    "actualite-regional-tunisie":        "politique",
    "actualites-internationales":        "international",
    "actualite-high-tech-tunisie-monde": "tech",
    "actualite-culturel-tunisie":        "culture",
    "communiques-de-presse-tunisie":     "communique",
    "actualite-midi-show":               "divertissement",
}

SLUG_KEYWORDS = {
    "sport":         ["coupe", "mondial", "football", "sport", "match",
                      "tournoi", "handball", "basket", "tennis", "athletisme",
                      "natation", "cyclisme", "rugby", "volley", "mercato"],
    "politique":     ["national", "tunisie", "regional", "gouvernement",
                      "parlement", "election", "ministre", "president",
                      "politique", "senat", "municipal"],
    "international": ["international", "monde", "mondial", "etranger",
                      "europe", "afrique", "asie", "amerique", "moyen-orient"],
    "economie":      ["economie", "finance", "bourse", "banque", "investissement",
                      "budget", "fiscalite", "commerce", "entreprise"],
    "tech":          ["tech", "high-tech", "numerique", "digital", "intelligence",
                      "artificielle", "startup", "innovation", "internet"],
    "culture":       ["culture", "culturel", "art", "cinema", "musique",
                      "theatre", "litterature", "patrimoine"],
    "sante":         ["sante", "medical", "hopital", "maladie", "covid",
                      "vaccin", "medecin", "pharmacie"],
    "justice":       ["justice", "tribunal", "jugement", "prison", "crime",
                      "police", "securite", "terrorisme"],
    "societe":       ["societe", "social", "education", "ecole", "universite",
                      "famille", "jeunesse", "femme", "enfant"],
    "divertissement":["divertissement", "show", "spectacle", "humour",
                      "celebrity", "people", "midi"]
}

CLUSTER_SIMILARITY_THRESHOLD = 0.80  # cosine similarity to join existing cluster
MIMIC_WINDOW_DAYS = 7
REVISIT_WINDOW_DAYS = 30

TREND_THRESHOLD    = 0.55
FIDDLING_THRESHOLD = 0.65   # same value — below this = fiddling

ALERT_THRESHOLD = 0.65

GOOGLE_TRENDS_TIMEFRAME = "now 1-d"   # last 24 hours
GOOGLE_TRENDS_GEO       = "TN"        # Tunisia

SCORE_REVIEW_PROMPT = """
Tu es un expert en analyse des tendances médiatiques tunisiennes.

Un système automatique a attribué un score de tendance à cet article publié par Mosaique FM.
Ce score représente la probabilité que l'article devienne viral auprès du grand public tunisien (0 = jamais viral, 1 = certainement viral).

Ton rôle est de revoir ce score et de le corriger si nécessaire.

Titre: {title}
Description: {description}
Catégorie: {category}
Score actuel: {score}
Nouveauté du sujet: {novelty}
Taille du cluster: {cluster_size}

Critères pour AUGMENTER le score:
- Événement choquant ou historique (record battu, élimination surprise, catastrophe, première fois)
- Forte réaction émotionnelle attendue du public tunisien
- Implique l'équipe nationale tunisienne ou une star mondiale connue en Tunisie
- Sujet complètement nouveau jamais vu dans les actualités récentes
- Résultat inattendu qui va à l'encontre des prévisions

Critères pour BAISSER le score:
- Programme ou calendrier de matchs (aucune valeur informationnelle forte)
- Nomination administrative interne à un club local
- Compétition que le public tunisien ne suit pas
- Article de routine sans surprise ni émotion
- Résultat attendu sans aucun élément choquant
- IMPORTANT: Si le sujet a déjà été largement couvert (cluster_size > 3), 
  cet article n'apporte rien de nouveau — baisser significativement le score
- IMPORTANT: Si novelty = "ancien sujet", le topic existait déjà — ce n'est pas une tendance émergente

Réponds UNIQUEMENT avec ce format JSON exact:
{{
    "revised_score": 0.0-1.0,
    "changed": true/false,
    "reason": "une phrase courte expliquant ton ajustement"
}}
"""