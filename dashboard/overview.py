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
from utils.platform_config import get_platform_config


def render(df, platform="Twitter / X"):
    cfg = get_platform_config(platform)
    render_hero(platform)

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
    has_saves = "Saves" in df.columns and df["Saves"].sum() > 0
    cols = st.columns(6 if has_saves else 5)

    with cols[0]:
        render_metric_card("📝", f"{len(df):,}", "Total Posts")
    with cols[1]:
        render_metric_card("❤️", f"{int(df['Likes'].sum()):,}", f"Total {cfg['reactions_label']}", "+12.4%", "up")
    with cols[2]:
        render_metric_card("🔁", f"{int(df['Retweets'].sum()):,}", f"Total {cfg['shares_label']}", "+8.7%", "up")
    with cols[3]:
        v = int(df["Views"].sum()) if "Views" in df.columns else 0
        render_metric_card("👁️", f"{v:,}", f"Total {cfg['impressions_label']}", "+15.2%", "up")
    with cols[4]:
        render_metric_card("⚡", f"{df['EngagementScore'].mean():,.0f}", "Avg Engagement")
    if has_saves:
        with cols[5]:
            render_metric_card("🔖", f"{int(df['Saves'].sum()):,}", "Total Saves")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row ───────────────────────────────────────────────────
    render_section_header("📊", "Analytics Overview")
    col_a, col_b = st.columns(2)

    with col_a:
        # Sentiment donut
        sent = df["Sentiment"].value_counts()
        fig = donut_chart(sent.index.tolist(), sent.values.tolist(), "Sentiment Distribution")
        st.plotly_chart(fig, width="stretch")

    with col_b:
        # Engagement over time
        if "Date" in df.columns:
            daily = df.groupby("Date")["EngagementScore"].sum().reset_index()
            daily.columns = ["Date", "Engagement"]
            fig = area_chart(daily, "Date", "Engagement", "Engagement Over Time")
            st.plotly_chart(fig, width="stretch")

    # ── Category Breakdown ───────────────────────────────────────────
    if "Category" in df.columns:
        cat = df.groupby("Category")["EngagementScore"].mean().reset_index()
        cat.columns = ["Category", "Avg Engagement"]
        cat = cat.sort_values("Avg Engagement", ascending=True)
        fig = bar_chart(cat, "Category", "Avg Engagement",
                        "Engagement by Category", horizontal=True)
        st.plotly_chart(fig, width="stretch")

    # ── Top Posts Table ──────────────────────────────────────────────
    render_section_header("🏆", f"Top Performing {cfg['post_label']}s")
    display_cols = ["Tweet", "Likes", "Retweets", "EngagementScore", "Sentiment", "ViralScore"]
    if has_saves:
        display_cols.insert(3, "Saves")
    top = df.nlargest(5, "EngagementScore")[display_cols].reset_index(drop=True)
    top.index = top.index + 1
    # Rename columns for display
    top = top.rename(columns={
        "Tweet": cfg["post_label"],
        "Retweets": cfg["shares_label"],
    })
    st.dataframe(top, width="stretch")
