"""
Dashboard page: Sentiment Analysis — Deep-dive into sentiment metrics.
"""
import streamlit as st
import pandas as pd
from dashboard.components import render_section_header, render_metric_card, render_info_panel
from utils.charts import donut_chart, line_chart, bar_chart
from utils.sentiment import detect_toxicity


def render(df):
    render_section_header("🧠", "Sentiment Analysis Engine")
    st.caption("NLP-powered sentiment classification with mood analysis and toxicity detection.")

    # ── Sentiment Metrics ────────────────────────────────────────────
    sent = df["Sentiment"].value_counts()
    pos = sent.get("Positive", 0)
    neg = sent.get("Negative", 0)
    neu = sent.get("Neutral", 0)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("😊", str(pos), "Positive Posts")
    with c2:
        render_metric_card("😐", str(neu), "Neutral Posts")
    with c3:
        render_metric_card("😞", str(neg), "Negative Posts")
    with c4:
        avg_pol = df["Polarity"].mean() if "Polarity" in df.columns else 0
        render_metric_card("📊", f"{avg_pol:.3f}", "Avg Polarity")

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        fig = donut_chart(sent.index.tolist(), sent.values.tolist(), "Sentiment Breakdown")
        st.plotly_chart(fig, width="stretch")

    with col_b:
        # Sentiment by engagement
        if "Sentiment" in df.columns:
            se = df.groupby("Sentiment")["EngagementScore"].mean().reset_index()
            se.columns = ["Sentiment", "Avg Engagement"]
            fig = bar_chart(se, "Sentiment", "Avg Engagement", "Engagement by Sentiment", color="Sentiment")
            st.plotly_chart(fig, width="stretch")

    # ── Sentiment Trend ──────────────────────────────────────────────
    if "Date" in df.columns:
        render_section_header("📈", "Sentiment Trend Over Time")
        daily = df.groupby(["Date", "Sentiment"]).size().reset_index(name="Count")
        fig = line_chart(daily, "Date", "Count", "Daily Sentiment Trend", color="Sentiment")
        st.plotly_chart(fig, width="stretch")

    # ── Mood Analysis ────────────────────────────────────────────────
    if "Mood" in df.columns:
        render_section_header("🎭", "Mood Analysis")
        mood_counts = df["Mood"].value_counts().reset_index()
        mood_counts.columns = ["Mood", "Count"]
        fig = bar_chart(mood_counts, "Mood", "Count", "Content Mood Distribution")
        st.plotly_chart(fig, width="stretch")

    # ── Toxicity Detection ───────────────────────────────────────────
    render_section_header("🛡️", "Toxicity & Spam Detection")
    tox_results = df["Tweet"].apply(detect_toxicity)
    df_tox = pd.DataFrame(tox_results.tolist())
    toxic_count = df_tox["is_toxic"].sum()
    spam_count = df_tox["is_spam"].sum()

    c1, c2 = st.columns(2)
    with c1:
        render_metric_card("☠️", str(toxic_count), "Toxic Posts Detected")
    with c2:
        render_metric_card("🚫", str(spam_count), "Spam Posts Detected")

    flagged = df[df_tox["is_toxic"] | df_tox["is_spam"]]
    if len(flagged) > 0:
        st.dataframe(flagged[["Tweet", "Sentiment"]].reset_index(drop=True), width="stretch")
    else:
        render_info_panel("✅ All Clear", "No toxic or spam content detected in the dataset.")
