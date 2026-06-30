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