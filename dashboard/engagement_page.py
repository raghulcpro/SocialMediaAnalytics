"""
Dashboard page: Engagement & Viral Analytics.
"""
import streamlit as st
import pandas as pd
import numpy as np
from dashboard.components import render_section_header, render_metric_card
from utils.charts import scatter_chart, bar_chart, heatmap_chart, gauge_chart
from utils.platform_config import get_platform_config


def render(df, platform="Twitter / X"):
    cfg = get_platform_config(platform)
    render_section_header("⚡", "Engagement Analytics")

    # ── Key Metrics ──────────────────────────────────────────────────
    has_saves = "Saves" in df.columns and df["Saves"].sum() > 0
    cols = st.columns(5 if has_saves else 4)

    with cols[0]:
        render_metric_card("📊", f"{df['EngagementRate'].mean():.2f}%", "Avg Engagement Rate")
    with cols[1]:
        render_metric_card("🔥", str(df["IsViral"].sum()), "Viral Posts")
    with cols[2]:
        render_metric_card("⭐", f"{df['QualityScore'].mean():.1f}", "Avg Quality Score")
    with cols[3]:
        render_metric_card("💬", f"{df['Replies'].mean():.0f}", f"Avg {cfg['comments_label']}")
    if has_saves:
        with cols[4]:
            render_metric_card("🔖", f"{df['Saves'].mean():.0f}", "Avg Saves")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Engagement Scatter ───────────────────────────────────────────
    render_section_header("🔬", "Engagement Analysis")
    col_a, col_b = st.columns(2)
    with col_a:
        fig = scatter_chart(df, "Likes", "Retweets", size="EngagementScore",
                            color="Sentiment",
                            title=f"{cfg['reactions_label']} vs {cfg['shares_label']} (bubble = engagement)")
        st.plotly_chart(fig, width="stretch")
    with col_b:
        fig = scatter_chart(df, "EngagementScore", "ViralScore",
                            color="Sentiment", title="Engagement vs Viral Score")
        st.plotly_chart(fig, width="stretch")

    # ── Viral Prediction ─────────────────────────────────────────────
    render_section_header("🚀", "Viral Prediction System")
    display_cols = ["Tweet", "ViralScore", "EngagementScore", "Likes", "Retweets", "Sentiment"]
    if has_saves:
        display_cols.insert(4, "Saves")
    viral_df = df.nlargest(10, "ViralScore")[display_cols].reset_index(drop=True)
    viral_df.index = viral_df.index + 1
    # Rename for display
    viral_df = viral_df.rename(columns={
        "Tweet": cfg["post_label"],
        "Retweets": cfg["shares_label"],
    })

    col1, col2 = st.columns([1, 2])
    with col1:
        avg_viral = df["ViralScore"].mean()
        fig = gauge_chart(round(avg_viral, 1), "Avg Viral Probability", 100)
        st.plotly_chart(fig, width="stretch")
    with col2:
        st.markdown("##### 🏆 Top Viral Candidates")
        st.dataframe(viral_df, width="stretch")

    # ── Engagement Heatmap ───────────────────────────────────────────
    if "Date" in df.columns:
        render_section_header("🗓️", "Engagement Heatmap")
        dft = df.copy()
        dft["Date"] = pd.to_datetime(dft["Date"], errors="coerce")
        dft["DayOfWeek"] = dft["Date"].dt.day_name()
        dft["WeekNum"] = dft["Date"].dt.isocalendar().week.astype(int)

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        avail_days = [d for d in days if d in dft["DayOfWeek"].values]
        weeks = sorted(dft["WeekNum"].unique())

        heat_data = []
        for day in avail_days:
            row = []
            for week in weeks:
                val = dft[(dft["DayOfWeek"] == day) & (dft["WeekNum"] == week)]["EngagementScore"].sum()
                row.append(val)
            heat_data.append(row)

        fig = heatmap_chart(heat_data, [f"W{w}" for w in weeks], avail_days, "Weekly Engagement Heatmap")
        st.plotly_chart(fig, width="stretch")

    # ── Fake Engagement Detection ────────────────────────────────────
    if "FakeScore" in df.columns:
        render_section_header("🕵️", "Fake Engagement Detection")
        suspicious = df[df["FakeScore"] == "⚠️ Suspicious"]
        c1, c2 = st.columns(2)
        with c1:
            render_metric_card("⚠️", str(len(suspicious)), "Suspicious Posts")
        with c2:
            render_metric_card("✅", str(len(df) - len(suspicious)), "Authentic Posts")

        if len(suspicious) > 0:
            fake_display = suspicious[["Tweet", "Likes", "Retweets", "LikeRetweetRatio", "FakeScore"]].reset_index(drop=True)
            fake_display = fake_display.rename(columns={
                "Tweet": cfg["post_label"],
                "Retweets": cfg["shares_label"],
            })
            st.dataframe(fake_display, width="stretch")
