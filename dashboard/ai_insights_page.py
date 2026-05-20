"""
Dashboard page: AI Recommendations & Insights.
"""
import streamlit as st
from dashboard.components import render_section_header, render_recommendation_card, render_info_panel
from utils.recommendations import generate_recommendations, get_hashtag_recommendations
from utils.platform_config import get_platform_config
from utils.charts import bar_chart
import pandas as pd


def render(df, sentiment_dist, platform="Twitter / X"):
    cfg = get_platform_config(platform)

    render_section_header("🤖", "AI Recommendation Engine")
    st.caption(f"Data-driven recommendations to optimize your {platform} strategy.")

    recs = generate_recommendations(df, sentiment_dist, platform=platform)

    # Split by priority
    high = [r for r in recs if r["priority"] == "high"]
    medium = [r for r in recs if r["priority"] == "medium"]
    low = [r for r in recs if r["priority"] == "low"]

    if high:
        st.markdown("#### 🔴 High Priority")
        for r in high:
            render_recommendation_card(r)

    if medium:
        st.markdown("#### 🟡 Medium Priority")
        for r in medium:
            render_recommendation_card(r)

    if low:
        st.markdown("#### 🟢 Low Priority")
        for r in low:
            render_recommendation_card(r)

    # ── Hashtag Recommendations ──────────────────────────────────────
    render_section_header("#️⃣", "Hashtag Performance Analysis")
    hash_recs = get_hashtag_recommendations(df)
    if hash_recs:
        hdf = pd.DataFrame(hash_recs)
        fig = bar_chart(hdf, "hashtag", "avg_engagement", "Hashtag Performance Ranking")
        st.plotly_chart(fig, width="stretch")
        st.dataframe(hdf, width="stretch")
    else:
        render_info_panel("No Hashtag Data", "Add hashtags to your dataset for analysis.")

    # ── AI Generated Insights ────────────────────────────────────────
    render_section_header("💡", "AI-Generated Insights")
    total = len(df)
    viral = df["IsViral"].sum() if "IsViral" in df.columns else 0
    avg_eng = df["EngagementScore"].mean()
    top_cat = ""
    if "Category" in df.columns:
        top_cat = df.groupby("Category")["EngagementScore"].mean().idxmax()

    post_label = cfg["post_label"].lower()
    insights = [
        f"📌 You've analyzed **{total}** {post_label}s with an average engagement of **{avg_eng:,.0f}**.",
        f"🔥 **{viral}** {post_label}s ({viral/total*100:.1f}%) exceeded the viral threshold.",
    ]
    if top_cat:
        insights.append(f"📊 **{top_cat}** is your highest-performing content category.")

    pos = sentiment_dist.get("Positive", 0)
    tot = sum(sentiment_dist.values())
    if tot > 0:
        insights.append(f"😊 Positive sentiment ratio: **{pos/tot*100:.1f}%** — {'healthy' if pos/tot > 0.5 else 'needs improvement'}.")

    # Instagram-specific insights
    if "Saves" in df.columns and df["Saves"].sum() > 0:
        avg_saves = df["Saves"].mean()
        save_ratio = df["Saves"].sum() / max(df["Likes"].sum(), 1) * 100
        insights.append(f"🔖 Save-to-like ratio: **{save_ratio:.1f}%** — {'excellent content value!' if save_ratio > 5 else 'try creating more saveable content (tips, tutorials).'}")

    for i in insights:
        render_info_panel("", i)
