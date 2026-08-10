import streamlit as st
from pymongo import MongoClient
from bson import ObjectId
from utils.db      import fetch_alerts, get_collections
from utils.helpers import format_date, score_badge
import os
from dotenv import load_dotenv

load_dotenv()

st.title("🚨 Alertes en cours")
st.caption("Articles détectés comme tendances par le système")
st.divider()

def mark_as_seen(alert_id):
    _, alerts = get_collections()
    alerts.update_one(
        {"_id": alert_id},
        {"$set": {"seen": True}}
    )
    st.cache_data.clear()

alerts = fetch_alerts()

if not alerts:
    st.info("Aucune alerte pour le moment.")
else:
    unseen = [a for a in alerts if not a.get("seen", False)]
    
    col1, col2 = st.columns(2)
    col1.metric("Total alertes",   len(alerts))
    col2.metric("Non vues",        len(unseen))
    
    st.divider()

    filter_seen = st.radio(
        "Filtrer",
        ["Toutes", "Non vues", "Vues"],
        horizontal=True
    )

    if filter_seen == "Non vues":
        alerts = [a for a in alerts if not a.get("seen", False)]
    elif filter_seen == "Vues":
        alerts = [a for a in alerts if a.get("seen", False)]

    st.divider()

    for alert in alerts:
        seen      = alert.get("seen", False)
        score     = alert.get("score", 0)
        title     = alert.get("title", "")
        cat       = alert.get("category", "")
        url       = alert.get("url", "#")
        pub       = format_date(alert.get("published_at"))
        alerted   = format_date(alert.get("alerted_at"))
        image_url = alert.get("image_url", "")
        alert_id  = alert.get("_id")

        with st.container():
            col_img, col_content, col_action = st.columns([1.5, 6, 1.5])

            with col_img:
                if image_url:
                    # Utilisez use_container_width maintenant que Streamlit est réinstallé proprement
                    st.image(image_url, width='stretch', output_format="JPEG")
                else:
                    st.markdown(
                        '<div style="background:var(--secondary-background-color);'
                        'height:80px;border-radius:8px;display:flex;'
                        'align-items:center;justify-content:center;'
                        'color:gray;font-size:12px;">Pas d\'image</div>',
                        unsafe_allow_html=True
                    )

            with col_content:
                st.markdown(f"### [{title}]({url})")
                st.caption(
                    f"📂 {cat}  •  "
                    f"📅 Publié: {pub}  •  "
                    f"🔔 Alerté: {alerted}"
                )
                st.markdown(score_badge(score), unsafe_allow_html=True)

            with col_action:
                if seen:
                    st.success("✅ Vue")
                else:
                    if st.button("Marquer vue", key=str(alert_id)):
                        mark_as_seen(alert_id)
                        st.rerun()

            st.divider()