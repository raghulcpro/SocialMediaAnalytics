"""
Dashboard page: Overview / Home — Hero metrics, ticker, sentiment donut, engagement charts.
"""
import streamlit as st
import pandas as pd
from dashboard.components import (
    render_hero, render_metric_card, render_section_header,
    render_ticker, render_info_panel
)
from utils.charts import donut_chart, area_chart, bar_chart


def render(df):
    render_hero()

    # ── Live Ticker ──────────────────────────────────────────────────
    total_eng = int(df["EngagementScore"].sum())
    avg_rate = df["EngagementRate"].mean() if "EngagementRate" in df.columns else 0
    viral_pct = (df["IsViral"].sum() / len(df) * 100) if "IsViral" in df.columns else 0
    render_ticker([
        {"label": "📊 Total Engagement", "value": f"{total_eng:,}", "direction": "up"},
        {"label": "📈 Avg Rate", "value": f"{avg_rate:.2f}%", "direction": "up"},
        {"label": "🔥 Viral Rate", "value": f"{viral_pct:.1f}%", "direction": "up"},
        {"label": "📝 Total Posts", "value": str(len(df)), "direction": "neutral"},
    ])
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Hero Metric Cards ────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric_card("📝", f"{len(df):,}", "Total Posts")
    with c2:
        render_metric_card("❤️", f"{int(df['Likes'].sum()):,}", "Total Likes", "+12.4%", "up")
    with c3:
        render_metric_card("🔁", f"{int(df['Retweets'].sum()):,}", "Retweets", "+8.7%", "up")
    with c4:
        v = int(df["Views"].sum()) if "Views" in df.columns else 0
        render_metric_card("👁️", f"{v:,}", "Total Views", "+15.2%", "up")
    with c5:
        render_metric_card("⚡", f"{df['EngagementScore'].mean():,.0f}", "Avg Engagement")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row ───────────────────────────────────────────────────
    render_section_header("📊", "Analytics Overview")
    col_a, col_b = st.columns(2)

    with col_a:
        # Sentiment donut
        sent = df["Sentiment"].value_counts()
        fig = donut_chart(sent.index.tolist(), sent.values.tolist(), "Sentiment Distribution")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        # Engagement over time
        if "Date" in df.columns:
            daily = df.groupby("Date")["EngagementScore"].sum().reset_index()
            daily.columns = ["Date", "Engagement"]
            fig = area_chart(daily, "Date", "Engagement", "Engagement Over Time")
            st.plotly_chart(fig, use_container_width=True)

    # ── Category Breakdown ───────────────────────────────────────────
    if "Category" in df.columns:
        cat = df.groupby("Category")["EngagementScore"].mean().reset_index()
        cat.columns = ["Category", "Avg Engagement"]
        cat = cat.sort_values("Avg Engagement", ascending=True)
        fig = bar_chart(cat, "Category", "Avg Engagement",
                        "Engagement by Category", horizontal=True)
        st.plotly_chart(fig, use_container_width=True)

    # ── Top Posts Table ──────────────────────────────────────────────
    render_section_header("🏆", "Top Performing Posts")
    top = df.nlargest(5, "EngagementScore")[
        ["Tweet", "Likes", "Retweets", "EngagementScore", "Sentiment", "ViralScore"]
    ].reset_index(drop=True)
    top.index = top.index + 1
    st.dataframe(top, use_container_width=True)
