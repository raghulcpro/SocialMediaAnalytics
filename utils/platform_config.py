"""
===============================================================================
 PLATFORM CONFIGURATION
 ──────────────────────
 Centralized mapping of platform-specific terminology, icons, and column names.
 All dashboard pages import from here instead of hardcoding Twitter terms.
===============================================================================
"""

PLATFORMS = {
    "Twitter / X": {
        "icon": "🐦",
        "post_label": "Tweet",
        "shares_label": "Retweets",
        "comments_label": "Replies",
        "impressions_label": "Views",
        "reactions_label": "Likes",
        "extra_metrics": [],
        "max_post_length": 280,
        "grok_prompt": (
            "Fetch 30 recent tweets from @username. Format strictly as a raw CSV "
            "inside a single code block. Use columns: "
            "Date,Tweet,Likes,Retweets,Replies,Views,Username,Hashtags,Category. "
            "Enclose Tweet text in double quotes. No other text."
        ),
        # Column mapping: platform-native name → internal standard name
        "column_map": {
            "Tweet": "Tweet",
            "Retweets": "Retweets",
            "Replies": "Replies",
            "Views": "Views",
            "Likes": "Likes",
        },
    },
    "Instagram": {
        "icon": "📸",
        "post_label": "Caption",
        "shares_label": "Shares",
        "comments_label": "Comments",
        "impressions_label": "Reach",
        "reactions_label": "Likes",
        "extra_metrics": ["Saves", "Followers"],
        "max_post_length": 2200,
        "grok_prompt": (
            "Fetch 30 recent Instagram posts from @username. Format strictly as a "
            "raw CSV inside a single code block. Use columns: "
            "Date,Caption,Likes,Comments,Shares,Saves,Reach,Username,Hashtags,Category. "
            "Enclose Caption text in double quotes. No other text."
        ),
        # Column mapping: platform-native name → internal standard name
        "column_map": {
            "Caption": "Tweet",
            "Comments": "Replies",
            "Shares": "Retweets",
            "Reach": "Views",
            "Likes": "Likes",
        },
    },
}

DEFAULT_PLATFORM = "Twitter / X"


def get_platform_config(platform: str = None) -> dict:
    """Get the configuration dict for a given platform."""
    if platform is None:
        platform = DEFAULT_PLATFORM
    return PLATFORMS.get(platform, PLATFORMS[DEFAULT_PLATFORM])


def get_label(platform: str, key: str) -> str:
    """Get a display label for a platform metric.

    Keys: post_label, shares_label, comments_label, impressions_label, reactions_label
    """
    cfg = get_platform_config(platform)
    return cfg.get(key, key)
