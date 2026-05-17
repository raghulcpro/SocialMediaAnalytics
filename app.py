import streamlit as st
import pandas as pd
import plotly.express as px
from textblob import TextBlob

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="SocialPulse AI",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# TITLE
# -----------------------------
st.title("📊 SocialPulse AI Dashboard")
st.markdown("AI-Powered Social Media Analytics Platform")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("tweets.csv")

# -----------------------------
# SENTIMENT ANALYSIS
# -----------------------------
def analyze_sentiment(tweet):

    analysis = TextBlob(tweet)

    polarity = analysis.sentiment.polarity

    if polarity > 0:
        return "Positive"

    elif polarity < 0:
        return "Negative"

    else:
        return "Neutral"

df["Sentiment"] = df["Tweet"].apply(analyze_sentiment)

# -----------------------------
# METRICS
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Posts", len(df))

with col2:
    st.metric("Total Likes", df["Likes"].sum())

with col3:
    st.metric("Total Retweets", df["Retweets"].sum())

# -----------------------------
# DATA TABLE
# -----------------------------
st.subheader("📄 Tweet Dataset")

st.dataframe(df)

# -----------------------------
# SENTIMENT COUNT
# -----------------------------
sentiment_count = df["Sentiment"].value_counts()

# -----------------------------
# PIE CHART
# -----------------------------
fig1 = px.pie(
    names=sentiment_count.index,
    values=sentiment_count.values,
    title="Sentiment Distribution"
)

st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# BAR CHART
# -----------------------------
fig2 = px.bar(
    df,
    x="Tweet",
    y="Likes",
    color="Sentiment",
    title="Likes Per Tweet"
)

st.plotly_chart(fig2, use_container_width=True)