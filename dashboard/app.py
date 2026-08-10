import streamlit as st
import plotly.express as px
import pandas as pd
from utils.db      import fetch_stats, fetch_articles
from utils.helpers import format_date

st.set_page_config(
    page_title="TanitWeb — Media Radar",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown(
    """
    <style>
        /* Cache la navigation native automatique de Streamlit */
        div[data-testid="stSidebarNav"] {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Configuration pour masquer la navigation automatique native (Streamlit >= 1.28)
# Si vous avez une version plus ancienne, configurez-le dans votre fichier .streamlit/config.toml :
# [client]
# showSidebarNavigation = false

# Barre latérale ultra-simple — Liens uniquement
with st.sidebar:
    st.page_link("app.py",               label="🏠  Accueil")
    st.page_link("pages/1_alertes.py",   label="🚨  Alertes")
    st.page_link("pages/2_articles.py",  label="📰  Articles")
    st.page_link("pages/3_clusters.py",  label="🔗  Clusters")
    st.page_link("pages/4_analytics.py", label="📊  Analytiques")

st.title("🏠 Tableau de bord — EcoTrend")
st.caption("Plateforme intelligente de détection précoce des tendances médiatiques")
st.divider()

stats = fetch_stats()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total articles",   stats["total"])
col2.metric("Tendances",        stats["trend"])
col3.metric("Éphémères",       stats["fiddling"])
col4.metric("Mimiques",        stats["mimic"])
col5.metric("🚨 Alertes",      stats["alerts"],
            delta=f"{stats['unseen']} non vues")

st.divider()

st.subheader("Répartition par catégorie")
articles = fetch_articles()

if articles:
    cats = {}
    for a in articles:
        cat      = a.get("category_normalized", "autre")
        cats[cat] = cats.get(cat, 0) + 1

    df_cats = pd.DataFrame(
        list(cats.items()),
        columns=["Catégorie", "Articles"]
    ).sort_values("Articles", ascending=False)

    fig = px.bar(
        df_cats, x="Catégorie", y="Articles",
        color="Articles",
        color_continuous_scale="Blues"
    )
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, width="stretch")

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Distribution des labels")
    df_labels = pd.DataFrame([
        {"Label": "Tendance",  "Count": stats["trend"]},
        {"Label": "Éphémère",  "Count": stats["fiddling"]},
        {"Label": "Mimique",   "Count": stats["mimic"]},
    ])
    fig2 = px.pie(
        df_labels, names="Label", values="Count",
        color_discrete_sequence=["#16a34a", "#d97706", "#6b7280"]
    )
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig2, width="stretch")

with col_right:
    st.subheader("Articles publiés par jour")
    from datetime import datetime, timezone, timedelta
    days = {}
    for a in articles:
        pub = a.get("published_at")
        if pub:
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            day = pub.strftime("%d/%m")
            days[day] = days.get(day, 0) + 1

    if days:
        df_days = pd.DataFrame(
            list(days.items()),
            columns=["Jour", "Articles"]
        )
        fig3 = px.line(df_days, x="Jour", y="Articles", markers=True)
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig3, width="stretch")