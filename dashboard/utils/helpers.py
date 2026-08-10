from datetime import timezone, timedelta

TZ_TUNISIA = timezone(timedelta(hours=1))

def format_date(dt):
    if not dt:
        return "—"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(TZ_TUNISIA).strftime("%d/%m/%Y %H:%M")

def score_badge(score):
    if score is None:
        return "—"
    if score >= 0.80:
        color = "#16a34a"   # green
    elif score >= 0.65:
        color = "#d97706"   # orange
    else:
        color = "#6b7280"   # gray
    return f'<span style="background:{color};color:white;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:500">{score:.2f}</span>'

def label_badge(label):
    colors = {
        "trend":    ("#16a34a", "Tendance"),
        "fiddling": ("#d97706", "Éphémère"),
        "mimic":    ("#6b7280", "Mimique"),
        "revisit":  ("#2563eb", "Retour"),
    }
    if not label or label not in colors:
        return "—"
    color, text = colors[label]
    return f'<span style="background:{color};color:white;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:500">{text}</span>'

def sentiment_badge(label):
    colors = {
        "positive": ("#16a34a", "Positif"),
        "negative": ("#dc2626", "Négatif"),
        "neutral":  ("#6b7280", "Neutre"),
    }
    if not label or label not in colors:
        return "—"
    color, text = colors[label]
    return f'<span style="background:{color};color:white;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:500">{text}</span>'