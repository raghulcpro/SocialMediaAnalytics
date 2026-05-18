# ⚡ SocialPulse AI — Social Media Intelligence Terminal

> AI-powered social media analytics platform with Binance-inspired dark UI.  
> Sentiment analysis · Viral prediction · Influencer scoring · Smart recommendations

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-FCD535)

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **Sentiment Engine** | NLP-powered positive/negative/neutral classification with mood analysis |
| **Engagement Analytics** | Likes, retweets, replies, views, engagement rate scoring |
| **Viral Prediction** | AI-based viral probability scoring (0-100) |
| **Influencer Score** | Multi-factor scoring: consistency, engagement, quality, viral rate |
| **AI Recommendations** | Smart suggestions for posting time, content, hashtags |
| **Trend Detection** | Trending hashtags, categories, engagement spikes |
| **Fake Detection** | Heuristic-based suspicious engagement flagging |
| **Toxicity Detection** | Toxic/spam content identification |
| **Profile Comparison** | Side-by-side influencer comparison |
| **Export** | CSV and JSON report downloads |

## 📦 Installation

```bash
pip install -r requirements.txt
python -m textblob.download_corpora
```

## ▶️ Run

```bash
streamlit run app.py
```

## 📂 Project Structure

```
SocialMediaAnalytics/
├── app.py                    # Main Streamlit application
├── style.css                 # Binance-inspired premium CSS
├── requirements.txt          # Python dependencies
├── data/
│   └── tweets.csv            # Sample dataset (50 tweets)
├── utils/
│   ├── sentiment.py          # Sentiment & toxicity analysis
│   ├── analytics.py          # Engagement & viral scoring
│   ├── recommendations.py    # AI recommendation engine
│   ├── charts.py             # Plotly chart factory (dark theme)
│   └── data_loader.py        # CSV loading & validation
├── dashboard/
│   ├── components.py         # Reusable UI components
│   ├── overview.py           # Home dashboard page
│   ├── sentiment_page.py     # Sentiment analysis page
│   ├── engagement_page.py    # Engagement & viral page
│   ├── ai_insights_page.py   # AI recommendations page
│   ├── influencer_page.py    # Influencer scoring page
│   └── dataset_page.py       # Dataset explorer & export
├── models/
│   └── __init__.py
└── assets/
```

## 🎨 Design

- **Matte Black** background (#0B0E11)
- **Binance Yellow** accent (#FCD535)
- **Glassmorphism** dark cards
- **Neon glow** hover effects
- **Smooth animations**
- **Inter + JetBrains Mono** typography

## 📊 Dataset Format

CSV with columns: `Date, Tweet, Likes, Retweets, Replies, Views, Username, Hashtags, Category`

## 📜 License

MIT License — built for portfolios, interviews, and production use.
