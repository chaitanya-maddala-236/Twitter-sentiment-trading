# 🐦 Twitter Sentiment Trading Strategy

Alternative data trading system that uses Twitter sentiment to predict stock returns and construct portfolios.

## 🎯 Key Features

- **Social Sentiment Analysis**: Aggregates Twitter mentions and sentiment scores
- **Volume Weighting**: Weights signals by tweet volume for reliability
- **Dynamic Rebalancing**: Adjusts portfolio based on changing sentiment
- **Risk Management**: Threshold filters and diversification
- **Synthetic Data**: Built-in generator for testing without real data

## 📊 Performance Highlights

- Outperforms QQQ benchmark by X%
- Sharpe Ratio: X.XX
- Maximum Drawdown: XX%
- Win Rate: XX%

*(Run the app to get actual results)*

## 🚀 Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run twitter_sentiment_app.py

# Open browser to http://localhost:8501
```

## 📈 Strategy Logic

1. Collect Twitter sentiment data (daily)
2. Aggregate and weight by volume
3. Rank stocks by positivity
4. Hold top N performers
5. Rebalance periodically
6. Compare vs benchmark

## 🎨 Screenshots

![Dashboard](screenshots/dashboard.png)
![Performance](screenshots/performance.png)

## 📦 Tech Stack

- **Python 3.10+**
- **Streamlit** - Interactive UI
- **Plotly** - Data visualization
- **Pandas** - Data processing
- **yFinance** - Market data
- **TextBlob** - Sentiment analysis

## 📊 Data Format

CSV with columns: `ticker`, `date`, `sentiment`, `volume`
```csv
ticker,date,sentiment,volume
AAPL,2023-01-01,0.45,1200
MSFT,2023-01-01,0.32,890
```

## 🔬 Methodology

Uses volume-weighted sentiment aggregation to identify stocks with positive social media buzz, then constructs equal-weight portfolios that rebalance based on changing sentiment signals.

## 📚 Research Basis

This strategy is inspired by academic research on social media sentiment as a predictor of stock returns:
- Bollen et al. (2011) - Twitter mood predicts stock market
- Sprenger et al. (2014) - Tweets and stock returns
- Bartov et al. (2018) - Social media sentiment and earnings

## 💼 For Recruiters

This project demonstrates:
- ✅ Alternative data analysis
- ✅ Behavioral finance understanding
- ✅ Quantitative backtesting
- ✅ Risk management implementation
- ✅ Production-ready code
