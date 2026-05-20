"""
═══════════════════════════════════════════════════════════════════════════════
 ⚡ SOCIALPULSE AI — AI-Powered Social Media Intelligence Terminal
 ═══════════════════════════════════════════════════════════════════════════════
 A production-grade analytics platform with Binance-inspired UI.
 Built with: Python · Streamlit · Plotly · TextBlob · Scikit-learn
 Supports: Twitter/X · Instagram
 ═══════════════════════════════════════════════════════════════════════════════
"""

import streamlit as st
import pandas as pd
import os

# ── Page Configuration ───────────────────────────────────────────────────
st.set_page_config(
    page_title="SocialPulse AI — Intelligence Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# ── Load Custom CSS ──────────────────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_path):
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Import Modules ───────────────────────────────────────────────────────
from utils.data_loader import load_dataset
from utils.sentiment import get_sentiment
from utils.analytics import (
    compute_engagement_metrics,
    detect_fake_engagement,
)
from utils.platform_config import PLATFORMS, get_platform_config
from dashboard import (
    overview,
    sentiment_page,
    engagement_page,
    ai_insights_page,
    influencer_page,
    dataset_page,
)

# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR — Modern Navigation & Data Source
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Header
    st.markdown("""
    <div style="text-align:center;padding:20px 0 15px;border-bottom:2px solid rgba(252,213,53,0.2);margin-bottom:20px;">
        <div style="font-size:2.2rem;margin-bottom:8px;">⚡</div>
        <div style="font-size:1.3rem;font-weight:800;background:linear-gradient(135deg,#FCD535 0%,#F0B90B 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:4px;">SocialPulse</div>
        <div style="font-size:0.65rem;color:#B7BDC6;letter-spacing:2px;text-transform:uppercase;font-weight:600;">Intelligence Hub</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Platform Selector ────────────────────────────────────────────
    st.markdown("<div style='color:#FCD535;font-weight:800;font-size:0.7rem;text-transform:uppercase;letter-spacing:1.5px;padding:10px 0;'>🌐 PLATFORM</div>", unsafe_allow_html=True)

    platform_options = list(PLATFORMS.keys())
    platform = st.radio(
        "Platform",
        platform_options,
        label_visibility="collapsed",
        key="platform_select",
        horizontal=True,
    )
    st.session_state["platform"] = platform
    cfg = get_platform_config(platform)

    st.markdown(f"""
    <div style="text-align:center;padding:8px;margin:8px 0;border-radius:8px;background:rgba(252,213,53,0.08);border:1px solid rgba(252,213,53,0.15);">
        <span style="font-size:1.4rem;">{cfg['icon']}</span>
        <span style="color:#EAECEF;font-size:0.85rem;font-weight:600;margin-left:6px;">{platform}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#2B3139;margin:15px 0;'>", unsafe_allow_html=True)

    # Navigation Radio
    st.markdown("<div style='color:#FCD535;font-weight:800;font-size:0.7rem;text-transform:uppercase;letter-spacing:1.5px;padding:10px 0;'>CORE</div>", unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "🏠 Overview",
            "🧠 Sentiment Analysis",
            "⚡ Engagement & Viral",
            "🤖 AI Recommendations",
            "👑 Influencer & Trends",
            "📄 Dataset & Export",
        ],
        label_visibility="collapsed",
        key="main_nav"
    )

    st.markdown("<hr style='border-color:#2B3139;margin:20px 0;'>", unsafe_allow_html=True)

    # ── Data Source ──────────────────────────────────────────────────
    st.markdown("<div style='color:#FCD535;font-weight:800;font-size:0.7rem;text-transform:uppercase;letter-spacing:1.5px;padding:10px 0;'>📂 DATA SOURCE</div>", unsafe_allow_html=True)
    data_source = st.radio(
        "Source", ["Default Dataset", "Upload CSV", "Paste Raw CSV (Grok)"],
        label_visibility="collapsed",
        key="data_source"
    )

    uploaded = None
    raw_csv_text = None
    if data_source == "Upload CSV":
        uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
    elif data_source == "Paste Raw CSV (Grok)":
        with st.expander("🤖 How to get data from Grok?"):
            st.markdown(f"""
            **1. Paste this into Grok:**
            ```text
            {cfg['grok_prompt']}
            ```
            **2. Copy the CSV block and paste it below.**
            """)
        raw_csv_text = st.text_area(
            "Paste Raw CSV Data Here:", height=150,
            placeholder=f"Date,{cfg['post_label']},{cfg['reactions_label']},{cfg['shares_label']},{cfg['comments_label']},{cfg['impressions_label']},Username\n2026-05-18,\"Example post\",100,20,5,500,@user"
        )

    # ── Platform Data Guide ─────────────────────────────────────────
    st.markdown("<hr style='border-color:#2B3139;margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#FCD535;font-weight:800;font-size:0.7rem;text-transform:uppercase;letter-spacing:1.5px;padding:10px 0;'>{cfg['icon']} HOW TO GET {platform.upper()} DATA</div>", unsafe_allow_html=True)

    if platform == "Twitter / X":
        with st.expander("⚡ Use Grok (Best Method)", expanded=False):
            st.markdown("""
**Grok has real-time access to X/Twitter data!**

**Step 1** — Go to [grok.com](https://grok.com) or use Grok inside the X app

**Step 2** — Paste this prompt:
```
Fetch 30 recent tweets from @username.
Format strictly as a raw CSV inside a single
code block. Use columns:
Date,Tweet,Likes,Retweets,Replies,Views,
Username,Hashtags,Category.
Enclose Tweet text in double quotes.
No other text.
```

**Step 3** — Copy the CSV output

**Step 4** — Select **"Paste Raw CSV (Grok)"** in
Data Source above and paste it in! 🚀

> ✅ **Why Grok?** It has direct access to real-time
> X/Twitter data, so numbers are accurate and up-to-date.
            """)

        with st.expander("📥 Download X Archive (Your Account)", expanded=False):
            st.markdown("""
**To export your own X/Twitter data:**

**Step 1** — Go to [x.com](https://x.com) → Click **More** (left sidebar)

**Step 2** — Click **Settings and Support** → **Settings and Privacy**

**Step 3** — Click **Your Account** → **Download an archive of your data**

**Step 4** — Verify your identity (password + 2FA)

**Step 5** — Click **Request Archive**

**Step 6** — X will email you when ready (usually **24–48 hours**)

**Step 7** — Download the `.zip`, extract it, and find your tweets in the `data/` folder

> 💡 **Tip:** The archive is in JSON format. Paste the
> tweet data into ChatGPT and ask:
> *"Convert this to CSV with columns: Date, Tweet,
> Likes, Retweets, Replies, Views, Username"*
            """)

        with st.expander("📊 X Analytics Dashboard", expanded=False):
            st.markdown("""
**For content creators & business accounts:**

**Step 1** — Go to [analytics.x.com](https://analytics.x.com)

**Step 2** — Sign in with your X account

**Step 3** — Navigate to **Tweets** tab

**Step 4** — Set the date range you want to analyze

**Step 5** — Click **Export data** (top-right button)

**Step 6** — You'll get a `.csv` file — upload it directly! ✨

> 🎯 This gives you the **most accurate** engagement
> data since it comes directly from X's own analytics.
> Works best for **your own account**.
            """)

        with st.expander("🤖 Use ChatGPT / Gemini", expanded=False):
            st.markdown("""
**Alternative if you don't have Grok:**

Paste this into ChatGPT or Gemini:
```
Give me 20 sample tweets about [your topic].
Format as CSV with columns:
Date,Tweet,Likes,Retweets,Replies,Views,
Username,Hashtags,Category.
Use realistic engagement numbers.
Wrap Tweet in double quotes. Only output CSV.
```

> ⚠️ Note: ChatGPT/Gemini **don't have real-time**
> X access, so numbers will be simulated/estimated.
> For real data, use **Grok** or **X Analytics**.
            """)

    elif platform == "Instagram":
        with st.expander("📱 Export from Instagram App", expanded=False):
            st.markdown("""
**Step 1** — Open the **Instagram app** on your phone

**Step 2** — Go to your **Profile** → tap the **☰ Menu** (top-right)

**Step 3** — Tap **⚙️ Settings and Privacy**

**Step 4** — Scroll down to **Your Activity** section → tap **Download Your Information**

**Step 5** — Tap **Request a Download**
- Select **Some of your information**
- Check ✅ **Posts** and ✅ **Content interactions**
- Choose format: **JSON** (or HTML)
- Choose date range and tap **Submit Request**

**Step 6** — Wait for Instagram to email you (usually **5 min – 48 hours**)

**Step 7** — Download the `.zip` file from the email, extract it, and find your posts data inside

> 💡 **Tip:** Convert the JSON to CSV by pasting it into
> ChatGPT/Grok and asking:
> *"Convert to CSV with columns: Date, Caption, Likes,
> Comments, Shares, Saves, Reach, Username"*
            """)

        with st.expander("🌐 Export from Instagram Web", expanded=False):
            st.markdown("""
**Step 1** — Go to [instagram.com](https://instagram.com) on your browser

**Step 2** — Click your **Profile picture** (bottom-left) → **Settings**

**Step 3** — Click **See more in Accounts Center** → **Your information and permissions**

**Step 4** — Click **Download your information** → **Request a download**

**Step 5** — Select your **Instagram account** → Choose **Some of your information**
- Check ✅ **Posts** and ✅ **Content interactions**

**Step 6** — Choose **Format: JSON** → **Date Range: All time** → **Submit Request**

**Step 7** — You'll receive an email with a download link within minutes to 48 hours
            """)

        with st.expander("📊 Instagram Insights (Business/Creator)", expanded=False):
            st.markdown("""
**For Business or Creator accounts only:**

**Step 1** — Open Instagram → Go to your **Profile**

**Step 2** — Tap **Professional Dashboard** (or **Insights**)

**Step 3** — Browse through **Content**, **Activity**, and **Audience** tabs

**Step 4** — Note down metrics for each post manually, or take screenshots

**Step 5** — Enter the data into a spreadsheet with columns:
`Date, Caption, Likes, Comments, Shares, Saves, Reach, Username`

**Step 6** — Save as `.csv` and upload it here! 📤

> 💡 **Pro Tip:** Instagram Insights only shows data for
> the **last 90 days**. Export regularly to build history.
            """)

        with st.expander("⚡ Quick Alternative (Recommended)", expanded=False):
            st.markdown("""
**Fastest method — Use ChatGPT or Grok:**

Paste this prompt:
```
Look up the Instagram account @username.
Give me their last 20 posts as a CSV with
columns: Date, Caption, Likes, Comments,
Shares, Saves, Reach, Username, Hashtags,
Category.
Wrap Caption in double quotes. Only output CSV.
```

Then **copy the CSV** and paste it in the
**"Paste Raw CSV"** section above! 🚀

> ⚠️ Note: AI tools give estimated/approximate
> numbers since Instagram data isn't fully public.
> For exact data, use the official export methods.
            """)


# ══════════════════════════════════════════════════════════════════════════
# DATA PIPELINE — Load → Analyze → Enrich
# ══════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="⚡ Loading data pipeline...")
def load_and_process(uploaded_file=None, raw_csv_text=None, platform="Twitter / X"):
    """Full data pipeline: load → sentiment → engagement → fake detection."""
    df = load_dataset(uploaded_file, raw_csv_text, platform=platform)

    plat_cfg = get_platform_config(platform)

    # Sentiment analysis
    sentiments = df["Tweet"].apply(get_sentiment)
    df["Sentiment"] = sentiments.apply(lambda x: x["label"])
    df["Polarity"] = sentiments.apply(lambda x: x["polarity"])
    df["Subjectivity"] = sentiments.apply(lambda x: x["subjectivity"])
    df["Confidence"] = sentiments.apply(lambda x: x["confidence"])
    df["Mood"] = sentiments.apply(lambda x: x["mood"])

    # Engagement metrics (platform-aware max length)
    df = compute_engagement_metrics(df, max_post_length=plat_cfg["max_post_length"])

    # Fake engagement detection
    df = detect_fake_engagement(df)

    return df


# Load data
try:
    df = load_and_process(uploaded, raw_csv_text, platform=platform)
except Exception as e:
    st.error(f"❌ Data loading error: {e}")
    st.stop()

# Sentiment distribution (used by multiple pages)
sentiment_dist = df["Sentiment"].value_counts().to_dict()


# ══════════════════════════════════════════════════════════════════════════
# PAGE ROUTER
# ══════════════════════════════════════════════════════════════════════════
if "Overview" in page:
    overview.render(df, platform)
elif "Sentiment" in page:
    sentiment_page.render(df, platform)
elif "Engagement" in page:
    engagement_page.render(df, platform)
elif "Recommendation" in page:
    ai_insights_page.render(df, sentiment_dist, platform)
elif "Influencer" in page:
    influencer_page.render(df)
elif "Dataset" in page:
    dataset_page.render(df, platform)