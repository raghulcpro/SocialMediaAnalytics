"""
Dashboard page: AI Recommendations & Insights.
"""
import streamlit as st
from dashboard.components import render_section_header, render_recommendation_card, render_info_panel, render_metric_card
from utils.recommendations import generate_recommendations, get_hashtag_recommendations
from utils.platform_config import get_platform_config
from utils.charts import bar_chart
import pandas as pd
from utils.analytics import grade_draft_hook, discover_semantic_whitespace, extract_golden_phrases

def render(df, sentiment_dist, platform="Twitter / X"):
    cfg = get_platform_config(platform)
    post_label = cfg["post_label"].lower()

    render_section_header("🤖", "AI Recommendation Engine")
    st.caption(f"Data-driven recommendations to optimize your {platform} strategy.")

    # ── Viral Hook Grader (Predictive Draft Analyzer) ───────────────
    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header("✍️", "Viral Hook Grader (Predictive A/B Testing)")
    st.markdown(f"Draft your next {post_label} and our AI will predict its engagement score and provide structural feedback based on your historical viral hits.")
    
    draft_text = st.text_area(f"Draft your next {post_label} here:", height=120, placeholder="e.g. Just launched my new Python course! 🚀 #coding")
    
    if st.button("Predict Virality"):
        if draft_text.strip():
            with st.spinner("Analyzing structural linguistics..."):
                result = grade_draft_hook(draft_text, df)
                
                c1, c2 = st.columns([1, 2])
                with c1:
                    render_metric_card("🎯", f"{result['score']}/100", "Predicted Virality Score")
                    render_metric_card("📈", f"{result['prediction']:,.0f}", "Projected Engagement")
                with c2:
                    st.markdown("#### AI Feedback")
                    for fb in result["feedback"]:
                        st.markdown(fb)
        else:
            st.warning("Please enter some text to analyze.")

    # ── Semantic Gap Discovery ───────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header("🌌", "Content Whitespace Discovery")
    st.markdown("Topics your audience highly engages with, but you rarely post about.")
    
    with st.spinner("Calculating semantic gaps..."):
        gaps = discover_semantic_whitespace(df)
        
    if gaps:
        for g in gaps:
            kw_str = ", ".join(g["keywords"])
            st.markdown(f"""
            <div style="padding:15px;border-left:4px solid #FCD535;background:rgba(252,213,53,0.05);margin-bottom:10px;">
                <h4 style="margin:0;color:#FCD535;">Topic: {kw_str}</h4>
                <p style="margin:5px 0 0 0;font-size:0.9rem;">
                    <strong>Engagement:</strong> {g['avg_engagement']:,.0f} (High) &nbsp;|&nbsp; 
                    <strong>Post Frequency:</strong> {g['frequency']} (Low)
                </p>
                <p style="margin:5px 0 0 0;font-style:italic;color:#848E9C;">
                    Action: You've barely posted about this, but it performs incredibly well. Write a post about this today!
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No clear semantic gaps found. Try analyzing a larger dataset.")

    # ── Golden Phrase Extraction ──────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header("🗝️", "Viral 'Golden Phrases'")
    st.markdown("Exact 2-to-3 word phrases that appear strictly in your top 20% most viral posts.")
    
    with st.spinner("Extracting n-grams..."):
        phrases = extract_golden_phrases(df)
        
    if phrases:
        p_cols = st.columns(len(phrases))
        for i, (phrase, count) in enumerate(phrases):
            with p_cols[i % len(p_cols)]:
                st.markdown(f"""
                <div style="text-align:center;padding:10px;border-radius:8px;background:#1E2329;border:1px solid #2B3139;margin-bottom:10px;">
                    <div style="font-size:1.1rem;font-weight:700;color:#EAECEF;">"{phrase}"</div>
                    <div style="font-size:0.8rem;color:#848E9C;">Used {count} times in viral hits</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Not enough data to extract significant golden phrases.")


    # ── Basic Recommendations (Legacy) ───────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    render_section_header("📜", "Basic Tactical Advice")
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
