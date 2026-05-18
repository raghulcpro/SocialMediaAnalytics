import streamlit as st
import pandas as pd
import plotly.express as px
from textblob import TextBlob

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="SocialPulse AI",
    page_icon="🚀",
    layout="wide"
)

# -----------------------------------
# CUSTOM CSS
# -----------------------------------
# -----------------------------------
# BINANCE STYLE CSS
# -----------------------------------

st.markdown("""
<style>

/* Main App */
.stApp {
    background-color: #0B0E11;
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #161A1E;
    border-right: 1px solid #2B3139;
}

/* Sidebar Text */
section[data-testid="stSidebar"] * {
    color: white;
}

/* Metric Cards */
[data-testid="stMetric"] {
    background: #1E2329;
    border: 1px solid #2B3139;
    padding: 20px;
    border-radius: 15px;
}

/* Titles */
h1 {
    color: #FCD535;
}

/* Data Table */
[data-testid="stDataFrame"] {
    border: 1px solid #2B3139;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Go To",
    ["Dashboard", "Dataset", "Analytics"]
)

# -----------------------------------
# LOAD DATA
# -----------------------------------
df = pd.read_csv("tweets.csv")

# -----------------------------------
# SENTIMENT FUNCTION
# -----------------------------------
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

# -----------------------------------
# ENGAGEMENT SCORE
# -----------------------------------
df["EngagementScore"] = (
    df["Likes"] +
    df["Retweets"]
)

# -----------------------------------
# VIRAL SCORE
# -----------------------------------
average_engagement = df["EngagementScore"].mean()

df["Viral"] = df["EngagementScore"].apply(
    lambda x: "🔥 Viral"
    if x > average_engagement
    else "Normal"
)

# -----------------------------------
# DASHBOARD PAGE
# -----------------------------------
if page == "Dashboard":

    st.title("🚀 SocialPulse AI")

    st.markdown(
        "### AI-Powered Social Media Analytics Dashboard"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Posts",
            len(df)
        )

    with col2:
        st.metric(
            "Total Likes",
            df["Likes"].sum()
        )

    with col3:
        st.metric(
            "Total Retweets",
            df["Retweets"].sum()
        )

    with col4:
        st.metric(
            "Avg Engagement",
            round(df["EngagementScore"].mean(), 2)
        )

    st.divider()

    # PIE CHART
    sentiment_count = df["Sentiment"].value_counts()

    fig1 = px.pie(
        names=sentiment_count.index,
        values=sentiment_count.values,
        title="Sentiment Distribution",
        hole=0.5
    )

    st.plotly_chart(fig1, use_container_width=True)

    # BAR CHART
    fig2 = px.bar(
        df,
        x="Tweet",
        y="EngagementScore",
        color="Sentiment",
        title="Post Engagement"
    )

    st.plotly_chart(fig2, use_container_width=True)



# -----------------------------------
# DATASET PAGE
# -----------------------------------
elif page == "Dataset":

    st.title("📄 Dataset")

    st.dataframe(df)

# -----------------------------------
# ANALYTICS PAGE
# -----------------------------------
elif page == "Analytics":

    st.title("📈 AI Analytics")

    viral_posts = df[df["Viral"] == "🔥 Viral"]

    st.subheader("🔥 Viral Posts")

    st.dataframe(viral_posts)

    st.subheader("🤖 AI Suggestions")

    st.success(
        "Post more positive content for higher engagement."
    )

    st.info(
        "Posts with high engagement have viral potential."
    )

    st.warning(
        "Negative posts received lower engagement."
    )