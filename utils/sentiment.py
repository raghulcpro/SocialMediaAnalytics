"""
===============================================================================
 SENTIMENT ANALYSIS ENGINE
 ─────────────────────────
 Provides NLP-based sentiment classification using TextBlob.
 Classifies text into Positive / Negative / Neutral with confidence scores.
 Also performs mood analysis and toxic content detection.
===============================================================================
"""

from textblob import TextBlob
import re


# ── Toxic / spam keyword lists (simple heuristic-based detection) ────────────
TOXIC_KEYWORDS = [
    "scam", "fraud", "fake", "hate", "kill", "die", "stupid",
    "idiot", "loser", "trash", "garbage", "terrible", "awful",
    "worst", "disgusting", "horrible"
]

SPAM_KEYWORDS = [
    "click here", "free money", "earn now", "buy now", "limited offer",
    "act fast", "guarantee", "no risk", "winner", "congratulations",
    "airdrop", "giveaway link"
]


def get_sentiment(text: str) -> dict:
    """
    Analyze sentiment of a single text string.

    Returns a dictionary with:
        - label: "Positive", "Negative", or "Neutral"
        - polarity: float between -1.0 and 1.0
        - subjectivity: float between 0.0 (objective) and 1.0 (subjective)
        - confidence: percentage confidence of the classification
        - mood: detailed mood label (e.g., "Very Positive", "Slightly Negative")
    """
    blob = TextBlob(str(text))
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    # ── Classification ───────────────────────────────────────────────────
    if polarity > 0.3:
        label = "Positive"
    elif polarity > 0.05:
        label = "Positive"
    elif polarity < -0.3:
        label = "Negative"
    elif polarity < -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    # ── Confidence score (based on distance from 0) ──────────────────────
    confidence = min(abs(polarity) * 100 + 40, 99)

    # ── Mood mapping ─────────────────────────────────────────────────────
    mood = _get_mood(polarity)

    return {
        "label": label,
        "polarity": round(polarity, 4),
        "subjectivity": round(subjectivity, 4),
        "confidence": round(confidence, 1),
        "mood": mood,
    }


def _get_mood(polarity: float) -> str:
    """Map polarity to a human-readable mood label."""
    if polarity >= 0.6:
        return "🤩 Very Positive"
    elif polarity >= 0.3:
        return "😊 Positive"
    elif polarity >= 0.05:
        return "🙂 Slightly Positive"
    elif polarity >= -0.05:
        return "😐 Neutral"
    elif polarity >= -0.3:
        return "😕 Slightly Negative"
    elif polarity >= -0.6:
        return "😞 Negative"
    else:
        return "😡 Very Negative"


def detect_toxicity(text: str) -> dict:
    """
    Simple heuristic-based toxic content detection.
    Returns toxicity probability and matched keywords.
    """
    text_lower = text.lower()
    found_toxic = [kw for kw in TOXIC_KEYWORDS if kw in text_lower]
    found_spam = [kw for kw in SPAM_KEYWORDS if kw in text_lower]

    toxic_score = min(len(found_toxic) * 20 + (10 if found_toxic else 0), 100)
    spam_score = min(len(found_spam) * 25 + (10 if found_spam else 0), 100)

    return {
        "toxic_score": toxic_score,
        "spam_score": spam_score,
        "toxic_keywords": found_toxic,
        "spam_keywords": found_spam,
        "is_toxic": toxic_score >= 30,
        "is_spam": spam_score >= 30,
    }


def extract_keywords(text: str, top_n: int = 10) -> list:
    """Extract meaningful keywords from text (removes stopwords)."""
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "can", "shall",
        "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "and",
        "but", "or", "nor", "not", "so", "yet", "both", "either",
        "neither", "each", "every", "all", "any", "few", "more",
        "most", "other", "some", "such", "no", "only", "own", "same",
        "than", "too", "very", "just", "about", "up", "out", "this",
        "that", "it", "its", "i", "me", "my", "we", "our", "you",
        "your", "he", "him", "his", "she", "her", "they", "them",
        "their", "what", "which", "who", "whom", "when", "where",
        "why", "how", "if", "then", "because", "while", "although",
    }
    # Clean text: remove URLs, mentions, special chars
    clean = re.sub(r"http\S+|@\w+|#\w+", "", text.lower())
    clean = re.sub(r"[^a-z\s]", "", clean)
    words = [w for w in clean.split() if w not in stopwords and len(w) > 2]
    # Count frequency
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return sorted_words[:top_n]
