"""
Dashboard page: Engagement & Viral Analytics.
"""
import streamlit as st
import pandas as pd
import numpy as np
from dashboard.components import render_section_header, render_metric_card
from utils.charts import scatter_chart, bar_chart, heatmap_chart, gauge_chart


def render(df):
    render_section_header("⚡", "Engagement Analytics")

    # ── Key Metrics ──────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("📊", f"{df['EngagementRate'].mean():.2f}%", "Avg Engagement Rate")
    with c2:
        render_metric_card("🔥", str(df["IsViral"].sum()), "Viral Posts")
    with c3:
        render_metric_card("⭐", f"{df['QualityScore'].mean():.1f}", "Avg Quality Score")
    with c4:
        render_metric_card("💬", f"{df['Replies'].mean():.0f}", "Avg Replies")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Engagement Scatter ───────────────────────────────────────────
    render_section_header("🔬", "Engagement Analysis")
    col_a, col_b = st.columns(2)
    with col_a:
        fig = scatter_chart(df, "Likes", "Retweets", size="EngagementScore",
                            color="Sentiment", title="Likes vs Retweets (bubble = engagement)")
        st.plotly_chart(fig, width="stretch")
    with col_b:
        fig = scatter_chart(df, "EngagementScore", "ViralScore",
                            color="Sentiment", title="Engagement vs Viral Score")
        st.plotly_chart(fig, width="stretch")

    # ── Viral Prediction ─────────────────────────────────────────────
    render_section_header("🚀", "Viral Prediction System")
    viral_df = df.nlargest(10, "ViralScore")[
        ["Tweet", "ViralScore", "EngagementScore", "Likes", "Retweets", "Sentiment"]
    ].reset_index(drop=True)
    viral_df.index = viral_df.index + 1

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
            st.dataframe(suspicious[["Tweet", "Likes", "Retweets", "LikeRetweetRatio", "FakeScore"]].reset_index(drop=True), width="stretch")
