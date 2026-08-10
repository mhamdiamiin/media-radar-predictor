import streamlit as st
import plotly.express as px
import pandas as pd
from utils.db      import fetch_articles
from utils.helpers import format_date, score_badge, label_badge

st.title("🔗 Clusters thématiques")
st.divider()

articles = fetch_articles()
clustered = [a for a in articles if a.get("tendance", {}).get("cluster_id") not in [None, -1]]

if not clustered:
    st.info("Aucun cluster trouvé.")
else:
    cluster_map = {}
    for a in clustered:
        cid = a["tendance"]["cluster_id"]
        if cid not in cluster_map:
            cluster_map[cid] = []
        cluster_map[cid].append(a)

    cluster_options = {
        f"Cluster {cid} ({len(arts)} articles)": cid
        for cid, arts in sorted(cluster_map.items(), key=lambda x: len(x[1]), reverse=True)
    }

    selected = st.selectbox("Sélectionner un cluster", list(cluster_options.keys()))
    cid      = cluster_options[selected]
    arts     = cluster_map[cid]

    col1, col2, col3 = st.columns(3)
    scores = [a.get("tendance", {}).get("score", 0) for a in arts]
    col1.metric("Taille du cluster",  len(arts))
    col2.metric("Score moyen",        f"{sum(scores)/len(scores):.2f}")
    col3.metric("Score maximum",      f"{max(scores):.2f}")

    st.divider()

    for a in sorted(arts, key=lambda x: x.get("tendance", {}).get("score", 0), reverse=True):
        t = a.get("tendance", {})
        col1, col2, col3 = st.columns([5, 1, 1])
        with col1:
            st.markdown(f"**[{a.get('title','')}]({a.get('url','#')})**",
                       unsafe_allow_html=True)
            st.caption(f"📅 {format_date(a.get('published_at'))}")
        with col2:
            st.markdown(label_badge(t.get("label")), unsafe_allow_html=True)
        with col3:
            st.markdown(score_badge(t.get("score")), unsafe_allow_html=True)
        st.divider()

    st.subheader("Évolution des scores dans ce cluster")
    df = pd.DataFrame([{
        "Titre":   a.get("title","")[:40],
        "Score":   a.get("tendance",{}).get("score", 0),
        "Date":    a.get("published_at")
    } for a in arts]).sort_values("Date")

    fig = px.scatter(df, x="Date", y="Score", text="Titre",
                     color="Score", color_continuous_scale="RdYlGn",
                     size_max=12)
    fig.update_traces(textposition="top center", textfont_size=9)
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width='stretch')