"""
===============================================================================
 ANALYTICS ENGINE
 ────────────────
 Core computation module for engagement metrics, viral prediction,
 trend detection, influencer scoring, and fake engagement detection.
===============================================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime


def compute_engagement_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute comprehensive engagement metrics for each post.
    
    Metrics calculated:
        - EngagementScore: weighted sum of likes, retweets, replies
        - EngagementRate: engagement relative to views (%)
        - ViralScore: probability of going viral (0-100)
        - QualityScore: content quality heuristic (0-100)
    """
    df = df.copy()

    # ── Engagement Score (weighted) ──────────────────────────────────────
    df["EngagementScore"] = (
        df["Likes"] * 1.0 +
        df["Retweets"] * 2.0 +
        df.get("Replies", pd.Series(0, index=df.index)) * 1.5
    )

    # ── Engagement Rate (% of views) ────────────────────────────────────
    if "Views" in df.columns:
        df["EngagementRate"] = np.where(
            df["Views"] > 0,
            ((df["Likes"] + df["Retweets"] + df.get("Replies", 0)) / df["Views"]) * 100,
            0
        )
    else:
        df["EngagementRate"] = 0

    # ── Viral Score ──────────────────────────────────────────────────────
    avg_engagement = df["EngagementScore"].mean()
    std_engagement = df["EngagementScore"].std()
    if std_engagement == 0:
        std_engagement = 1

    df["ViralScore"] = np.clip(
        ((df["EngagementScore"] - avg_engagement) / std_engagement * 20 + 50),
        0, 100
    ).round(1)

    df["IsViral"] = df["ViralScore"] >= 65

    # ── Quality Score ────────────────────────────────────────────────────
    if "Tweet" in df.columns:
        tweet_lengths = df["Tweet"].str.len()
        has_hashtags = df["Tweet"].str.contains("#", na=False).astype(int)
        has_url = df["Tweet"].str.contains("http", na=False).astype(int)

        df["QualityScore"] = np.clip(
            (tweet_lengths / 280 * 30) +
            (has_hashtags * 15) +
            (has_url * 10) +
            (df["ViralScore"] * 0.45),
            0, 100
        ).round(1)
    else:
        df["QualityScore"] = 50

    return df


def compute_influencer_score(df: pd.DataFrame, username: str = None) -> dict:
    """
    Calculate a comprehensive influencer score (0-100) based on:
        - Engagement consistency
        - Content quality
        - Audience interaction
        - Growth signals
        - Sentiment health
    """
    if username and "Username" in df.columns:
        user_df = df[df["Username"] == username]
    else:
        user_df = df

    if len(user_df) == 0:
        return {"score": 0, "breakdown": {}}

    # ── Sub-scores ───────────────────────────────────────────────────────
    # 1. Engagement consistency (std deviation - lower = more consistent)
    eng_std = user_df["EngagementScore"].std()
    eng_mean = user_df["EngagementScore"].mean()
    consistency = max(0, 100 - (eng_std / max(eng_mean, 1) * 50))

    # 2. Average engagement rate
    avg_rate = user_df["EngagementRate"].mean() if "EngagementRate" in user_df.columns else 0
    engagement = min(avg_rate * 10, 100)

    # 3. Content quality
    quality = user_df["QualityScore"].mean() if "QualityScore" in user_df.columns else 50

    # 4. Viral hit rate
    viral_rate = (user_df["IsViral"].sum() / len(user_df)) * 100 if "IsViral" in user_df.columns else 0

    # 5. Post volume / activity
    activity = min(len(user_df) * 5, 100)

    # ── Weighted final score ─────────────────────────────────────────────
    final = (
        consistency * 0.20 +
        engagement * 0.30 +
        quality * 0.20 +
        viral_rate * 0.20 +
        activity * 0.10
    )

    return {
        "score": round(min(final, 100), 1),
        "breakdown": {
            "Consistency": round(consistency, 1),
            "Engagement": round(engagement, 1),
            "Quality": round(quality, 1),
            "Viral Rate": round(viral_rate, 1),
            "Activity": round(activity, 1),
        }
    }


def detect_trends(df: pd.DataFrame) -> dict:
    """
    Detect trending hashtags, keywords, and engagement spikes.
    """
    trends = {
        "hashtags": [],
        "categories": [],
        "engagement_spikes": [],
    }

    # ── Trending hashtags ────────────────────────────────────────────────
    if "Hashtags" in df.columns:
        all_tags = []
        for tags in df["Hashtags"].dropna():
            all_tags.extend([t.strip().lower() for t in str(tags).split("#") if t.strip()])
        tag_freq = {}
        for t in all_tags:
            tag_freq[t] = tag_freq.get(t, 0) + 1
        trends["hashtags"] = sorted(tag_freq.items(), key=lambda x: x[1], reverse=True)[:15]

    # ── Trending categories ──────────────────────────────────────────────
    if "Category" in df.columns:
        cat_engagement = df.groupby("Category")["EngagementScore"].mean().sort_values(ascending=False)
        trends["categories"] = list(cat_engagement.items())

    # ── Engagement spikes ────────────────────────────────────────────────
    if "Date" in df.columns:
        df_temp = df.copy()
        df_temp["Date"] = pd.to_datetime(df_temp["Date"], errors="coerce")
        daily = df_temp.groupby("Date")["EngagementScore"].sum().reset_index()
        if len(daily) > 1:
            avg = daily["EngagementScore"].mean()
            spikes = daily[daily["EngagementScore"] > avg * 1.5]
            trends["engagement_spikes"] = list(
                spikes.apply(lambda r: {"date": str(r["Date"].date()), "score": r["EngagementScore"]}, axis=1)
            )

    return trends


def detect_fake_engagement(df: pd.DataFrame) -> pd.DataFrame:
    """
    Heuristic-based fake engagement detection.
    Flags posts with suspicious like-to-retweet ratios or engagement patterns.
    """
    df = df.copy()

    # ── Ratio analysis ───────────────────────────────────────────────────
    df["LikeRetweetRatio"] = np.where(
        df["Retweets"] > 0,
        df["Likes"] / df["Retweets"],
        df["Likes"]
    )

    avg_ratio = df["LikeRetweetRatio"].mean()
    std_ratio = df["LikeRetweetRatio"].std()

    # Flag outliers (ratio too high or too low = suspicious)
    df["SuspiciousEngagement"] = (
        (df["LikeRetweetRatio"] > avg_ratio + 2 * std_ratio) |
        (df["LikeRetweetRatio"] < avg_ratio - 2 * std_ratio)
    )

    # ── Engagement-to-view ratio check ───────────────────────────────────
    if "Views" in df.columns:
        df["ViewEngagementRatio"] = np.where(
            df["Views"] > 0,
            df["EngagementScore"] / df["Views"],
            0
        )
        avg_ver = df["ViewEngagementRatio"].mean()
        std_ver = df["ViewEngagementRatio"].std()
        df["SuspiciousEngagement"] = df["SuspiciousEngagement"] | (
            df["ViewEngagementRatio"] > avg_ver + 2.5 * std_ver
        )

    df["FakeScore"] = np.where(df["SuspiciousEngagement"], "⚠️ Suspicious", "✅ Authentic")

    return df


def get_posting_time_analysis(df: pd.DataFrame) -> dict:
    """Analyze best posting times based on engagement patterns."""
    if "Date" not in df.columns:
        return {}

    df_temp = df.copy()
    df_temp["Date"] = pd.to_datetime(df_temp["Date"], errors="coerce")
    df_temp["DayOfWeek"] = df_temp["Date"].dt.day_name()
    df_temp["DayNum"] = df_temp["Date"].dt.dayofweek

    day_engagement = df_temp.groupby(["DayOfWeek", "DayNum"]).agg(
        avg_engagement=("EngagementScore", "mean"),
        total_posts=("EngagementScore", "count"),
    ).reset_index().sort_values("DayNum")

    best_day = day_engagement.loc[day_engagement["avg_engagement"].idxmax(), "DayOfWeek"]

    return {
        "daily_data": day_engagement,
        "best_day": best_day,
    }
