import streamlit as st
import plotly.express as px
import pandas as pd
from collections import Counter
from utils.db import fetch_articles

st.title("📊 Analytiques")
st.divider()

articles = fetch_articles()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Sentiment par catégorie")
    rows = []
    for a in articles:
        cat           = a.get("category_normalized", "autre")
        nlp           = a.get("nlp") or {}
        sentiment_obj = nlp.get("sentiment") or {}
        sentiment     = sentiment_obj.get("label", "neutral") or "neutral"
        rows.append({"Catégorie": cat, "Sentiment": sentiment})
    if rows:
        df = pd.DataFrame(rows)
        fig = px.histogram(df, x="Catégorie", color="Sentiment",
                          barmode="group",
                          color_discrete_map={
                              "positive": "#16a34a",
                              "negative": "#dc2626",
                              "neutral":  "#6b7280"
                          })
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width='stretch')

with col_right:
    st.subheader("Score moyen par catégorie")
    cat_scores = {}
    cat_counts = {}
    for a in articles:
        cat   = a.get("category_normalized", "autre")
        score = a.get("tendance", {}).get("score", 0)
        if score:
            cat_scores[cat] = cat_scores.get(cat, 0) + score
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
    avg_scores = {cat: cat_scores[cat]/cat_counts[cat] for cat in cat_scores}
    df_avg = pd.DataFrame(list(avg_scores.items()), columns=["Catégorie", "Score moyen"])
    df_avg = df_avg.sort_values("Score moyen", ascending=True)
    fig2 = px.bar(df_avg, x="Score moyen", y="Catégorie", orientation="h",
                  color="Score moyen", color_continuous_scale="RdYlGn")
    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, width='stretch')

st.divider()

st.subheader("Top 20 mots-clés")
all_keywords = []
for a in articles:
    all_keywords.extend(a.get("nlp", {}).get("keywords", []))
if all_keywords:
    kw_counts  = Counter(all_keywords).most_common(20)
    df_kw      = pd.DataFrame(kw_counts, columns=["Mot-clé", "Fréquence"])
    df_kw      = df_kw.sort_values("Fréquence", ascending=True)
    fig3       = px.bar(df_kw, x="Fréquence", y="Mot-clé", orientation="h")
    fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig3, width='stretch')

st.divider()

st.subheader("Entités les plus mentionnées")
entity_types = {"PER": "Personnes", "ORG": "Organisations", "LOC": "Lieux", "GPE": "Pays"}

cols = st.columns(2)
for i, (etype, label) in enumerate(entity_types.items()):
    entities = []
    for a in articles:
        for e in a.get("nlp", {}).get("entities", []):
            if e.get("label") == etype:
                entities.append(e.get("text", ""))
    if entities:
        counts = Counter(entities).most_common(10)
        df_ent = pd.DataFrame(counts, columns=[label, "Mentions"])
        df_ent = df_ent.sort_values("Mentions", ascending=True)
        fig    = px.bar(df_ent, x="Mentions", y=label, orientation="h",
                       title=label)
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",
                         paper_bgcolor="rgba(0,0,0,0)")
        cols[i % 2].plotly_chart(fig, width='stretch')