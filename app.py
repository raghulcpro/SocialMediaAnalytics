"""
═══════════════════════════════════════════════════════════════════════════════
 ⚡ SOCIALPULSE AI — AI-Powered Social Media Intelligence Terminal
 ═══════════════════════════════════════════════════════════════════════════════
 A production-grade analytics platform with Binance-inspired UI.
 Built with: Python · Streamlit · Plotly · TextBlob · Scikit-learn
 ═══════════════════════════════════════════════════════════════════════════════
"""

import streamlit as st
import pandas as pd
import os

# ── Page Configuration ───────────────────────────────────────────────────
st.set_page_config(
    page_title="SocialPulse AI — Intelligence Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load Custom CSS ──────────────────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_path):
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Import Modules ───────────────────────────────────────────────────────
from utils.data_loader import load_dataset
from utils.sentiment import get_sentiment
from utils.analytics import (
    compute_engagement_metrics,
    detect_fake_engagement,
)
from dashboard import (
    overview,
    sentiment_page,
    engagement_page,
    ai_insights_page,
    influencer_page,
    dataset_page,
)

# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR — Premium Navigation
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 10px;">
        <span style="font-size:2.5rem;">⚡</span>
        <h2 style="color:#FCD535 !important;margin:8px 0 4px !important;
                   font-size:1.4rem !important;border:none !important;
                   padding:0 !important;">SocialPulse AI</h2>
        <p style="color:#848E9C;font-size:0.75rem;letter-spacing:2px;
                  text-transform:uppercase;margin:0;">Intelligence Terminal</p>
    </div>
    <hr style="border-color:#2B3139;margin:16px 0;">
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "🏠 Overview",
            "🧠 Sentiment Analysis",
            "⚡ Engagement & Viral",
            "🤖 AI Recommendations",
            "👑 Influencer & Trends",
            "📄 Dataset & Export",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<hr style='border-color:#2B3139;margin:16px 0;'>", unsafe_allow_html=True)

    # ── Data Source ──────────────────────────────────────────────────
    st.markdown("##### 📂 Data Source")
    data_source = st.radio(
        "Source", ["Default Dataset", "Upload CSV"],
        label_visibility="collapsed",
    )

    uploaded = None
    if data_source == "Upload CSV":
        uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

    st.markdown("""
    <hr style="border-color:#2B3139;margin:16px 0;">
    <div style="text-align:center;padding:10px 0;">
        <p style="color:#848E9C;font-size:0.7rem;margin:0;">
            Built with ❤️ using Python & Streamlit<br>
            © 2026 SocialPulse AI
        </p>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# DATA PIPELINE — Load → Analyze → Enrich
# ══════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="⚡ Loading data pipeline...")
def load_and_process(uploaded_file=None):
    """Full data pipeline: load → sentiment → engagement → fake detection."""
    df = load_dataset(uploaded_file)

    # Sentiment analysis
    sentiments = df["Tweet"].apply(get_sentiment)
    df["Sentiment"] = sentiments.apply(lambda x: x["label"])
    df["Polarity"] = sentiments.apply(lambda x: x["polarity"])
    df["Subjectivity"] = sentiments.apply(lambda x: x["subjectivity"])
    df["Confidence"] = sentiments.apply(lambda x: x["confidence"])
    df["Mood"] = sentiments.apply(lambda x: x["mood"])

    # Engagement metrics
    df = compute_engagement_metrics(df)

    # Fake engagement detection
    df = detect_fake_engagement(df)

    return df


# Load data
try:
    df = load_and_process(uploaded)
except Exception as e:
    st.error(f"❌ Data loading error: {e}")
    st.stop()

# Sentiment distribution (used by multiple pages)
sentiment_dist = df["Sentiment"].value_counts().to_dict()


# ══════════════════════════════════════════════════════════════════════════
# PAGE ROUTER
# ══════════════════════════════════════════════════════════════════════════
if "Overview" in page:
    overview.render(df)
elif "Sentiment" in page:
    sentiment_page.render(df)
elif "Engagement" in page:
    engagement_page.render(df)
elif "Recommendation" in page:
    ai_insights_page.render(df, sentiment_dist)
elif "Influencer" in page:
    influencer_page.render(df)
elif "Dataset" in page:
    dataset_page.render(df)