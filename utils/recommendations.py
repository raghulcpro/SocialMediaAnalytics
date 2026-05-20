"""
===============================================================================
 AI RECOMMENDATION ENGINE
 ────────────────────────
 Smart suggestions for social media strategy optimization.
 Platform-aware: adapts terminology for Twitter/X and Instagram.
===============================================================================
"""

import pandas as pd
import numpy as np


def generate_recommendations(df, sentiment_dist=None, platform="Twitter / X"):
    """Generate AI-powered recommendations from data analysis."""
    recs = []

    # Platform-aware labels
    from utils.platform_config import get_platform_config
    cfg = get_platform_config(platform)
    post_label = cfg["post_label"].lower()
    max_len = cfg["max_post_length"]

    if "Date" in df.columns:
        dt = df.copy()
        dt["Date"] = pd.to_datetime(dt["Date"], errors="coerce")
        dt["DayOfWeek"] = dt["Date"].dt.day_name()
        day_eng = dt.groupby("DayOfWeek")["EngagementScore"].mean()
        best = day_eng.idxmax()
        worst = day_eng.idxmin()
        recs.append({"icon": "🕐", "title": "Optimal Posting Day",
            "description": f"Highest engagement on **{best}**. Avoid **{worst}**.",
            "priority": "high", "category": "Timing"})

    if "Tweet" in df.columns:
        dt = df.copy()
        dt["Len"] = dt["Tweet"].str.len()
        # Platform-aware bucket sizes
        if max_len > 500:
            bins = [0, 100, 300, 500, 1000, max_len]
        else:
            bins = [0, 50, 100, 150, 200, max_len]
        dt["Bucket"] = pd.cut(dt["Len"], bins=bins)
        be = dt.groupby("Bucket", observed=True)["EngagementScore"].mean()
        if len(be) > 0:
            recs.append({"icon": "📝", "title": f"Ideal {post_label.title()} Length",
                "description": f"Posts with **{be.idxmax()}** chars perform best.",
                "priority": "high", "category": "Content"})

    if "Category" in df.columns:
        ce = df.groupby("Category")["EngagementScore"].mean().sort_values(ascending=False)
        if len(ce) > 0:
            top = ce.index[0]
            pct = ((ce.iloc[0] / ce.mean() - 1) * 100)
            recs.append({"icon": "📊", "title": "Best Content Category",
                "description": f"**{top}** generates **{pct:.0f}%** more engagement than average.",
                "priority": "high", "category": "Strategy"})

    if "Hashtags" in df.columns:
        dt = df.copy()
        dt["HC"] = dt["Hashtags"].str.count("#")
        corr = dt[["HC", "EngagementScore"]].corr().iloc[0, 1]
        recs.append({"icon": "#️⃣", "title": "Hashtag Strategy",
            "description": f"Hashtag correlation: **r={corr:.2f}**. Use 3-5 relevant hashtags.",
            "priority": "medium", "category": "Hashtags"})

    if sentiment_dist:
        total = sum(sentiment_dist.values())
        if total > 0:
            pp = sentiment_dist.get("Positive", 0) / total * 100
            np_ = sentiment_dist.get("Negative", 0) / total * 100
            if pp > 60:
                recs.append({"icon": "😊", "title": "Sentiment: Excellent",
                    "description": f"**{pp:.0f}%** positive content. Great for engagement.",
                    "priority": "low", "category": "Sentiment"})
            elif np_ > 40:
                recs.append({"icon": "⚠️", "title": "Sentiment Alert",
                    "description": f"**{np_:.0f}%** negative. Balance with positive content.",
                    "priority": "high", "category": "Sentiment"})

    if "EngagementRate" in df.columns:
        ar = df["EngagementRate"].mean()
        if ar < 2:
            recs.append({"icon": "📈", "title": "Boost Engagement",
                "description": f"Rate **{ar:.2f}%** is below 2% benchmark. Use CTAs and questions.",
                "priority": "high", "category": "Growth"})
        else:
            recs.append({"icon": "🚀", "title": "Strong Engagement",
                "description": f"Rate **{ar:.2f}%** is above average! Stay consistent.",
                "priority": "low", "category": "Growth"})

    if "IsViral" in df.columns:
        vr = df["IsViral"].mean() * 100
        recs.append({"icon": "🔥", "title": "Viral Rate",
            "description": f"**{vr:.0f}%** viral posts. {'Great!' if vr > 20 else 'Try trending topics.'}",
            "priority": "medium", "category": "Viral"})

    if "Replies" in df.columns:
        comments_label = cfg["comments_label"].lower()
        recs.append({"icon": "💬", "title": "Community Engagement",
            "description": f"Avg {comments_label}: **{df['Replies'].mean():.0f}**. Ask questions to boost.",
            "priority": "medium", "category": "Community"})

    # Instagram-specific: Saves insight
    if "Saves" in df.columns and df["Saves"].sum() > 0:
        avg_saves = df["Saves"].mean()
        recs.append({"icon": "🔖", "title": "Save Rate Analysis",
            "description": f"Avg saves: **{avg_saves:.0f}**. High saves = high-value content. Create more saveable posts (tips, tutorials, infographics).",
            "priority": "medium", "category": "Content"})

    return recs


def get_hashtag_recommendations(df):
    """Analyze hashtag performance and recommend optimal hashtags."""
    if "Hashtags" not in df.columns:
        return []
    data = []
    for _, row in df.iterrows():
        for tag in str(row.get("Hashtags", "")).split("#"):
            tag = tag.strip().lower()
            if tag:
                data.append({"tag": f"#{tag}", "engagement": row.get("EngagementScore", 0)})
    if not data:
        return []
    tdf = pd.DataFrame(data)
    stats = tdf.groupby("tag").agg(avg=("engagement", "mean"), count=("engagement", "count")).sort_values("avg", ascending=False)
    avg_all = stats["avg"].mean()
    return [{"hashtag": t, "avg_engagement": round(r["avg"], 0), "usage_count": int(r["count"]),
             "recommendation": "🟢 High" if r["avg"] > avg_all else "🟡 Average"}
            for t, r in stats.head(10).iterrows()]
