"""
===============================================================================
 DATA LOADER
 ───────────
 Handles loading, validation, and preprocessing of CSV datasets.
 Supports both built-in demo data and user-uploaded files.
 Supports multiple platforms (Twitter/X, Instagram).
===============================================================================
"""

import pandas as pd
import os
import io

from utils.platform_config import get_platform_config, DEFAULT_PLATFORM

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# Default files per platform
DEFAULT_FILES = {
    "Twitter / X": os.path.join(DATA_DIR, "tweets.csv"),
    "Instagram": os.path.join(DATA_DIR, "instagram_posts.csv"),
}


def load_dataset(uploaded_file=None, raw_csv_text=None, platform=None) -> pd.DataFrame:
    """Load dataset from uploaded file, raw text, or default CSV."""
    if platform is None:
        platform = DEFAULT_PLATFORM

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif raw_csv_text is not None and raw_csv_text.strip() != "":
        df = pd.read_csv(io.StringIO(raw_csv_text))
    else:
        default_file = DEFAULT_FILES.get(platform, DEFAULT_FILES[DEFAULT_PLATFORM])
        if os.path.exists(default_file):
            df = pd.read_csv(default_file)
        else:
            raise FileNotFoundError(
                f"No dataset found for {platform}. Upload a CSV or place the default file in data/"
            )

    df = _normalize_columns(df, platform)
    df = _validate_and_clean(df)
    return df


def _normalize_columns(df: pd.DataFrame, platform: str) -> pd.DataFrame:
    """Rename platform-native columns and fuzzy-match to internal standard names."""
    cfg = get_platform_config(platform)
    col_map = cfg.get("column_map", {})

    rename = {}
    
    # 1. Strict mapping from config
    for native_name, standard_name in col_map.items():
        if native_name != standard_name:
            for c in df.columns:
                if c.lower() == native_name.lower() and c != standard_name:
                    rename[c] = standard_name
                    break

    if rename:
        df = df.rename(columns=rename)
        
    # 2. Fuzzy/Synonym mapping for common messy uploads
    synonyms = {
        "Tweet": ["text", "content", "post", "body", "caption", "full_text", "message"],
        "Likes": ["favs", "favorites", "heart", "like", "favorite_count", "like_count"],
        "Retweets": ["rt", "shares", "repost", "reposts", "retweet_count", "share_count"],
        "Replies": ["comments", "responses", "reply_count", "comment_count"],
        "Views": ["impressions", "reach", "view_count", "impression_count", "reads"],
        "Date": ["timestamp", "time", "created_at", "date_published", "published"],
        "Category": ["topic", "niche", "subject", "tag"],
        "Hashtags": ["tags", "hash"]
    }
    
    rename_fuzzy = {}
    existing_cols = [c.lower() for c in df.columns]
    
    for standard_col, syn_list in synonyms.items():
        if standard_col.lower() not in existing_cols:
            # We are missing a standard column, try to find a synonym
            for c in df.columns:
                if c.lower() in syn_list and c not in rename_fuzzy:
                    rename_fuzzy[c] = standard_col
                    existing_cols.append(standard_col.lower()) # prevent double mapping
                    break
                    
    if rename_fuzzy:
        df = df.rename(columns=rename_fuzzy)

    return df


def _validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Validate required columns and clean data."""
    required = ["Tweet", "Likes", "Retweets"]
    for col in required:
        if col not in df.columns:
            # Try case-insensitive match
            for c in df.columns:
                if c.lower() == col.lower():
                    df.rename(columns={c: col}, inplace=True)
                    break

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    for col in ["Likes", "Retweets", "Replies", "Views", "Saves"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    if "Replies" not in df.columns:
        df["Replies"] = (df["Likes"] * 0.15).astype(int)
    if "Views" not in df.columns:
        df["Views"] = (df["Likes"] * 15 + df["Retweets"] * 25).astype(int)

    return df
