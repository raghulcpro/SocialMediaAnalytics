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
# SIDEBAR — Modern Navigation & Data Source
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Header
    st.markdown("""
    <div style="text-align:center;padding:20px 0 15px;border-bottom:2px solid rgba(252,213,53,0.2);margin-bottom:20px;">
        <div style="font-size:2.2rem;margin-bottom:8px;">⚡</div>
        <div style="font-size:1.3rem;font-weight:800;color:#FCD535;margin-bottom:4px;">SocialPulse</div>
        <div style="font-size:0.65rem;color:#B7BDC6;letter-spacing:2px;text-transform:uppercase;font-weight:600;">Intelligence Hub</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation Radio
    st.markdown("<div style='color:#FCD535;font-weight:800;font-size:0.75rem;text-transform:uppercase;letter-spacing:1.5px;padding:15px 0 10px;'>📊 NAVIGATION</div>", unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
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

    st.markdown("<div style='margin:15px 0;border-top:1px solid rgba(252,213,53,0.2);'></div>", unsafe_allow_html=True)

    # ── Data Source ──────────────────────────────────────────────────
    st.markdown("<div style='color:#FCD535;font-weight:800;font-size:0.75rem;text-transform:uppercase;letter-spacing:1.5px;padding:10px 0;'>📂 DATA SOURCE</div>", unsafe_allow_html=True)
    data_source = st.radio(
        "Source",
        ["Default Dataset", "Upload CSV", "Paste Raw CSV (Grok)"],
        label_visibility="collapsed",
    )

    uploaded = None
    raw_csv_text = None
    if data_source == "Upload CSV":
        uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
    elif data_source == "Paste Raw CSV (Grok)":
        with st.expander("🤖 How to get data from Grok?"):
            st.markdown("""
            **1. Paste this into Grok:**
            ```text
            Fetch 30 recent tweets from @username. Format strictly as a raw CSV inside a single code block. Use columns: Date,Tweet,Likes,Retweets,Replies,Views,Username. Enclose Tweet text in double quotes. No other text.
            ```
            **2. Copy the CSV block and paste it below.**
            """)
        raw_csv_text = st.text_area("Paste Raw CSV Data Here:", height=150, placeholder="Date,Tweet,Likes,Retweets,Replies,Views,Username\n2026-05-18,\"Example tweet\",100,20,5,500,@user")

    st.markdown("<div style='margin-top:20px;border-top:1px solid rgba(252,213,53,0.1);padding-top:15px;text-align:center;'>", unsafe_allow_html=True)
    st.caption("Built with ❤️ using Python & Streamlit © 2026 SocialPulse AI")
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# DATA PIPELINE — Load → Analyze → Enrich
# ══════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="⚡ Loading data pipeline...")
def load_and_process(uploaded_file=None, raw_csv_text=None):
    """Full data pipeline: load → sentiment → engagement → fake detection."""
    df = load_dataset(uploaded_file, raw_csv_text)

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
    df = load_and_process(uploaded, raw_csv_text)
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
