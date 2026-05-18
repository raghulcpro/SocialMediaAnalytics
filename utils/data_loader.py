"""
===============================================================================
 DATA LOADER
 ───────────
 Handles loading, validation, and preprocessing of CSV datasets.
 Supports both built-in demo data and user-uploaded files.
===============================================================================
"""

import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DEFAULT_FILE = os.path.join(DATA_DIR, "tweets.csv")


def load_dataset(uploaded_file=None) -> pd.DataFrame:
    """Load dataset from uploaded file or default CSV."""
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif os.path.exists(DEFAULT_FILE):
        df = pd.read_csv(DEFAULT_FILE)
    else:
        raise FileNotFoundError("No dataset found. Upload a CSV or place tweets.csv in data/")

    df = _validate_and_clean(df)
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

    for col in ["Likes", "Retweets", "Replies", "Views"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    if "Replies" not in df.columns:
        df["Replies"] = (df["Likes"] * 0.15).astype(int)
    if "Views" not in df.columns:
        df["Views"] = (df["Likes"] * 15 + df["Retweets"] * 25).astype(int)

    return df
