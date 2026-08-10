import streamlit as st
import pandas as pd
from utils.db      import fetch_articles
from utils.helpers import format_date, score_badge, label_badge, sentiment_badge

st.title("📰 Explorateur d'articles")
st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    search = st.text_input("🔍 Rechercher par titre")
with col2:
    cat_filter = st.selectbox("Catégorie", ["Toutes", "sport", "politique",
                               "international", "economie", "culture",
                               "tech", "societe", "sante", "justice"])
with col3:
    label_filter = st.selectbox("Label", ["Tous", "trend", "fiddling", "mimic", "revisit"])

articles = fetch_articles()

filtered = articles
if search:
    filtered = [a for a in filtered if search.lower() in a.get("title", "").lower()]
if cat_filter != "Toutes":
    filtered = [a for a in filtered if a.get("category_normalized") == cat_filter]
if label_filter != "Tous":
    filtered = [a for a in filtered if a.get("tendance", {}).get("label") == label_filter]

st.caption(f"{len(filtered)} articles trouvés")
st.divider()

for a in filtered[:50]:
    tendance  = a.get("tendance", {})
    sentiment = a.get("nlp", {}).get("sentiment", {})
    col1, col2, col3, col4 = st.columns([5, 1, 1, 1])

    with col1:
        url = a.get("url", "#")
        st.markdown(f"**[{a.get('title','')}]({url})**", unsafe_allow_html=True)
        st.caption(f"📂 {a.get('category_normalized','')}  •  📅 {format_date(a.get('published_at'))}")
    with col2:
        st.markdown(label_badge(tendance.get("label")), unsafe_allow_html=True)
    with col3:
        st.markdown(score_badge(tendance.get("score")), unsafe_allow_html=True)
    with col4:
        st.markdown(sentiment_badge(sentiment.get("label")), unsafe_allow_html=True)

    st.divider()