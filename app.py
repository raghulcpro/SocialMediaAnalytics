import pandas as pd
from textblob import TextBlob

# Load CSV data
df = pd.read_csv("tweets.csv")

# Function for sentiment analysis
def analyze_sentiment(tweet):

    analysis = TextBlob(tweet)

    polarity = analysis.sentiment.polarity

    if polarity > 0:
        return "Positive"

    elif polarity < 0:
        return "Negative"

    else:
        return "Neutral"

# Apply sentiment analysis
df["Sentiment"] = df["Tweet"].apply(analyze_sentiment)

# Print result
print(df)