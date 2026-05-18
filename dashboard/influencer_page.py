"""
Dashboard page: Influencer Scoring & Trends.
"""
import streamlit as st
import pandas as pd
from dashboard.components import render_section_header, render_metric_card, render_score_badge
from utils.analytics import compute_influencer_score, detect_trends
from utils.charts import radar_chart, bar_chart, line_chart


def render(df):
    render_section_header("👑", "Influencer Scoring System")

    # ── Per-user scoring ─────────────────────────────────────────────
    if "Username" in df.columns:
        users = df["Username"].unique().tolist()
        sel = st.selectbox("Select Profile", users, key="inf_sel")
        result = compute_influencer_score(df, sel)
    else:
        result = compute_influencer_score(df)
        sel = "All Posts"

    score = result["score"]
    bd = result["breakdown"]

    col1, col2 = st.columns([1, 2])
    with col1:
        render_score_badge(score)
        st.markdown(f"<p style='text-align:center;color:#848E9C;'>Influencer Score for<br><b style='color:#FCD535;'>{sel}</b></p>", unsafe_allow_html=True)

        for k, v in bd.items():
            st.progress(v / 100, text=f"{k}: {v}")

    with col2:
        if bd:
            cats = list(bd.keys())
            vals = list(bd.values())
            fig = radar_chart(cats, vals, f"Profile Radar — {sel}")
            st.plotly_chart(fig, use_container_width=True)

    # ── User Comparison ──────────────────────────────────────────────
    if "Username" in df.columns and len(users) > 1:
        render_section_header("⚔️", "Profile Comparison")
        c1, c2 = st.columns(2)
        with c1:
            u1 = st.selectbox("Profile A", users, index=0, key="cmp1")
        with c2:
            u2 = st.selectbox("Profile B", users, index=min(1, len(users)-1), key="cmp2")

        s1 = compute_influencer_score(df, u1)
        s2 = compute_influencer_score(df, u2)

        cols = st.columns(2)
        with cols[0]:
            render_metric_card("👤", str(s1["score"]), f"{u1} Score")
        with cols[1]:
            render_metric_card("👤", str(s2["score"]), f"{u2} Score")

        if s1["breakdown"] and s2["breakdown"]:
            cats = list(s1["breakdown"].keys())
            cmp_df = pd.DataFrame({
                "Metric": cats,
                u1: [s1["breakdown"][c] for c in cats],
                u2: [s2["breakdown"][c] for c in cats],
            })
            st.dataframe(cmp_df, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════
    # TREND DETECTION
    # ══════════════════════════════════════════════════════════════════
    render_section_header("📈", "Trend Detection")
    trends = detect_trends(df)

    # Trending hashtags
    if trends["hashtags"]:
        st.markdown("##### 🔖 Trending Hashtags")
        hdf = pd.DataFrame(trends["hashtags"], columns=["Hashtag", "Mentions"])
        fig = bar_chart(hdf.head(10), "Hashtag", "Mentions", "Top Trending Hashtags")
        st.plotly_chart(fig, use_container_width=True)

    # Category performance
    if trends["categories"]:
        st.markdown("##### 📂 Category Performance")
        cdf = pd.DataFrame(trends["categories"], columns=["Category", "Avg Engagement"])
        fig = bar_chart(cdf, "Category", "Avg Engagement", "Category Engagement Ranking")
        st.plotly_chart(fig, use_container_width=True)

    # Engagement spikes
    if trends["engagement_spikes"]:
        st.markdown("##### ⚡ Engagement Spikes")
        sdf = pd.DataFrame(trends["engagement_spikes"])
        for _, spike in sdf.iterrows():
            st.markdown(f"- **{spike['date']}**: Engagement score **{spike['score']:,.0f}** (1.5x above average)")
