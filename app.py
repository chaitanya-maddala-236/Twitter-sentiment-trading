import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# Page configuration
st.set_page_config(
    page_title="Twitter Sentiment Trading",
    layout="wide",
    page_icon="🐦",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Same beautiful centered design
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main .block-container {
        max-width: 1400px;
        padding-left: 5rem;
        padding-right: 5rem;
        padding-top: 2rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #1DA1F2 0%, #14171A 100%);
    }
    
    .main-content {
        background: white;
        border-radius: 30px;
        padding: 3rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        margin: 2rem auto;
    }
    
    .hero {
        text-align: center;
        padding: 3rem 2rem 2rem 2rem;
        margin-bottom: 3rem;
    }
    
    .hero h1 {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #1DA1F2 0%, #14171A 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }
    
    .hero p {
        font-size: 1.4rem;
        color: #666;
        margin-top: 1rem;
        font-weight: 500;
    }
    
    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1DA1F2;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #1DA1F2;
    }
    
    .stMetric {
        background: linear-gradient(135deg, #1DA1F2 0%, #14171A 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 20px rgba(29, 161, 242, 0.3);
        transition: transform 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-5px);
    }
    
    .stMetric label {
        color: rgba(255,255,255,0.9) !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #1DA1F2 0%, #14171A 100%);
        color: white;
        font-weight: 700;
        border: none;
        padding: 1.2rem 3rem;
        border-radius: 50px;
        font-size: 1.3rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(29, 161, 242, 0.4);
        margin-top: 1rem;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(29, 161, 242, 0.6);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: #f8f9fa;
        border-radius: 15px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1DA1F2 0%, #14171A 100%);
        color: white;
    }
    
    .info-box {
        background: linear-gradient(135deg, #1DA1F2 0%, #14171A 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(29, 161, 242, 0.3);
    }
    
    .info-box h3 {
        margin-top: 0;
        color: white;
        font-size: 1.5rem;
    }
    
    .feature-card {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        border-color: #1DA1F2;
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(29, 161, 242, 0.2);
    }
    
    .feature-card h3 {
        color: #1DA1F2;
        font-size: 1.3rem;
        margin-bottom: 1rem;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #1DA1F2 0%, #14171A 100%);
    }
    
    .streamlit-expanderHeader {
        background: #f8f9fa;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.1rem;
        color: #1DA1F2;
    }
</style>
""", unsafe_allow_html=True)

# Main content wrapper
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Hero
st.markdown("""
<div class='hero'>
    <h1>🐦 Twitter Sentiment Trading</h1>
    <p>Social Media Analytics Meets Quantitative Finance</p>
</div>
""", unsafe_allow_html=True)

# Control Panel
st.markdown('<p class="section-title">⚙️ Configure Your Strategy</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Basic Settings", "⚙️ Advanced Settings", "📁 Data Management"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        top_n = st.slider("💼 Portfolio Size", 3, 20, 10, help="Top N stocks by sentiment")
        rebalance = st.selectbox("🔄 Rebalance Frequency", ["Monthly", "Weekly", "Daily"], index=0)
        start_date = st.date_input("📅 Start Date", datetime(2020, 1, 1))
    
    with col2:
        sentiment_threshold = st.slider("🎯 Min Sentiment Score", -1.0, 1.0, 0.0, 0.1)
        use_volume_weight = st.checkbox("📊 Weight by Tweet Volume", value=True)
        end_date = st.date_input("📅 End Date", datetime(2024, 1, 1))

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        min_mentions = st.slider("Minimum Tweet Volume", 10, 1000, 100)
    with col2:
        sentiment_decay = st.slider("Sentiment Decay Factor", 0.0, 1.0, 0.95)

with tab3:
    data_source = st.radio("📁 Data Source", 
                          ["Generate Synthetic Data", "Upload CSV", "Use Sample Data"],
                          index=0)
    
    if data_source == "Upload CSV":
        uploaded_file = st.file_uploader("Upload Twitter sentiment CSV", type=['csv'])
        st.info("📋 CSV must have: ticker, date, sentiment, volume columns")
        
        if uploaded_file:
            try:
                uploaded_data = pd.read_csv(uploaded_file)
                st.success(f"✅ Loaded {len(uploaded_data)} records")
                with st.expander("👀 Preview Data"):
                    st.dataframe(uploaded_data.head(10), use_container_width=True)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        st.info("📊 Will generate realistic synthetic Twitter sentiment data")

# Big action button
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run_strategy = st.button("🚀 RUN STRATEGY NOW", use_container_width=True)

if run_strategy:
    st.session_state.run = True

# Functions
@st.cache_data(show_spinner=False)
def generate_synthetic_data(start_date, end_date, n_stocks=50):
    """Generate realistic synthetic Twitter sentiment data"""
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'AMD', 
               'NFLX', 'PYPL', 'INTC', 'CSCO', 'ADBE', 'CRM', 'ORCL',
               'IBM', 'QCOM', 'TXN', 'AVGO', 'NOW', 'INTU', 'UBER', 'LYFT',
               'SNAP', 'TWTR', 'SQ', 'SHOP', 'SPOT', 'ZM', 'DOCU'][:n_stocks]
    
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    data = []
    
    for ticker in tickers:
        base_sentiment = np.random.uniform(-0.3, 0.5)
        sentiment_drift = 0.0
        
        for date in dates:
            sentiment_drift += np.random.normal(0, 0.05)
            sentiment_drift *= 0.95
            
            if np.random.random() < 0.02:
                sentiment_drift += np.random.choice([-0.3, 0.3])
            
            sentiment = np.clip(base_sentiment + sentiment_drift, -1, 1)
            volume = int(np.random.lognormal(5, 1.5))
            
            data.append({
                'ticker': ticker,
                'date': date,
                'sentiment': sentiment,
                'volume': volume
            })
    
    return pd.DataFrame(data)

def process_sentiment_data(df, rebalance_freq, threshold, volume_weight):
    """Process sentiment data"""
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['sentiment'] >= threshold]
    
    freq_map = {'Monthly': 'M', 'Weekly': 'W', 'Daily': 'D'}
    freq = freq_map[rebalance_freq]
    
    if volume_weight and 'volume' in df.columns:
        df['weighted_sentiment'] = df['sentiment'] * df['volume']
        agg_data = df.groupby(['ticker', pd.Grouper(key='date', freq=freq)]).agg({
            'weighted_sentiment': 'sum',
            'volume': 'sum'
        }).reset_index()
        agg_data['sentiment'] = agg_data['weighted_sentiment'] / agg_data['volume']
    else:
        agg_data = df.groupby(['ticker', pd.Grouper(key='date', freq=freq)])['sentiment'].mean().reset_index()
        agg_data['volume'] = df.groupby(['ticker', pd.Grouper(key='date', freq=freq)])['volume'].sum().reset_index()['volume']
    
    agg_data['rank'] = agg_data.groupby('date')['sentiment'].rank(ascending=False)
    return agg_data

def calculate_strategy_returns(sentiment_df, top_n, start, end):
    """Calculate portfolio returns"""
    top_stocks = sentiment_df[sentiment_df['rank'] <= top_n].copy()
    
    if len(top_stocks) == 0:
        return None, None, None
    
    unique_tickers = top_stocks['ticker'].unique().tolist()
    
    try:
        # Download price data
        raw_prices = yf.download(unique_tickers, start=start, end=end, progress=False)
        
        # Handle different yfinance return formats
        if isinstance(raw_prices, pd.Series):
            prices = raw_prices.to_frame(name=unique_tickers[0])
        elif isinstance(raw_prices.columns, pd.MultiIndex):
            # MultiIndex columns - extract 'Adj Close'
            if 'Adj Close' in raw_prices.columns.get_level_values(0):
                prices = raw_prices['Adj Close']
            else:
                prices = raw_prices['Close']
        else:
            # Single level columns
            prices = raw_prices
        
        # Ensure it's a DataFrame
        if isinstance(prices, pd.Series):
            prices = prices.to_frame(name=unique_tickers[0])
        
        # Handle single ticker case
        if len(unique_tickers) == 1 and len(prices.columns) == 1:
            prices.columns = [unique_tickers[0]]
        
        # Ensure all tickers we need are available in prices
        available_tickers = [t for t in unique_tickers if t in prices.columns]
        
        if len(available_tickers) == 0:
            st.warning("⚠️ No price data available for selected stocks")
            return None, None, None
        
        # Filter top_stocks to only include tickers with price data
        top_stocks = top_stocks[top_stocks['ticker'].isin(available_tickers)]
        
        rebalance_dates = sorted(top_stocks['date'].unique())
        portfolio_values = [1.0]
        dates_list = [rebalance_dates[0]]
        holdings = []
        
        for i in range(len(rebalance_dates) - 1):
            current_date = rebalance_dates[i]
            next_date = rebalance_dates[i + 1]
            
            stocks_to_hold = top_stocks[top_stocks['date'] == current_date]['ticker'].tolist()
            # Only keep stocks that have price data
            stocks_to_hold = [s for s in stocks_to_hold if s in available_tickers]
            
            if len(stocks_to_hold) == 0:
                continue
                
            holdings.append({'date': current_date, 'stocks': stocks_to_hold})
            
            mask = (prices.index >= current_date) & (prices.index < next_date)
            period_prices = prices.loc[mask, stocks_to_hold].dropna(how='all')
            
            if len(period_prices) > 0 and len(stocks_to_hold) > 0:
                period_returns = period_prices.pct_change().mean(axis=1)
                period_cumulative = (1 + period_returns).cumprod()
                
                for date, value in period_cumulative.items():
                    if date > current_date:
                        portfolio_values.append(portfolio_values[-1] * value)
                        dates_list.append(date)
        
        portfolio_series = pd.Series(portfolio_values, index=dates_list)
        return portfolio_series, top_stocks, holdings
        
    except Exception as e:
        st.error(f"Error downloading price data: {str(e)}")
        st.info("💡 Tip: Try using fewer stocks or a shorter date range")
        return None, None, None

def calculate_metrics(returns_series):
    """Calculate metrics"""
    total_return = (returns_series.iloc[-1] / returns_series.iloc[0] - 1) * 100
    daily_returns = returns_series.pct_change().dropna()
    ann_return = daily_returns.mean() * 252 * 100
    ann_vol = daily_returns.std() * np.sqrt(252) * 100
    sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252) if daily_returns.std() > 0 else 0
    
    cumulative = returns_series
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_dd = drawdown.min() * 100
    
    win_rate = (daily_returns > 0).sum() / len(daily_returns) * 100
    
    return {
        'total_return': total_return,
        'ann_return': ann_return,
        'ann_vol': ann_vol,
        'sharpe': sharpe,
        'max_dd': max_dd,
        'win_rate': win_rate
    }

# Main execution
if 'run' in st.session_state and st.session_state.run:
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Load data
        status_text.markdown("### 📊 Loading sentiment data...")
        progress_bar.progress(20)
        
        if data_source == "Generate Synthetic Data":
            twitter_data = generate_synthetic_data(start_date, end_date)
        elif data_source == "Upload CSV" and 'uploaded_data' in locals():
            twitter_data = uploaded_data
        else:
            twitter_data = generate_synthetic_data(start_date, end_date, n_stocks=30)
        
        status_text.markdown("### 🔧 Processing sentiment...")
        progress_bar.progress(40)
        
        processed_data = process_sentiment_data(twitter_data, rebalance, sentiment_threshold, use_volume_weight)
        
        status_text.markdown("### 💹 Calculating returns...")
        progress_bar.progress(60)
        
        portfolio_series, top_stocks, holdings = calculate_strategy_returns(processed_data, top_n, start_date, end_date)
        
        if portfolio_series is None:
            st.error("❌ Unable to calculate returns")
            st.stop()
        
        status_text.markdown("### 📈 Downloading benchmark...")
        progress_bar.progress(80)
        
        benchmark = yf.download("QQQ", start=start_date, end=end_date, progress=False)['Adj Close']
        if len(benchmark) == 0:
            st.error("❌ Unable to download benchmark data")
            st.stop()
        benchmark = benchmark / benchmark.iloc[0]
        
        progress_bar.progress(100)
        status_text.empty()
        progress_bar.empty()
        
        st.success("🎉 Strategy Analysis Complete!")
        
        # RESULTS
        st.markdown('<p class="section-title">📊 Performance Overview</p>', unsafe_allow_html=True)
        
        strategy_metrics = calculate_metrics(portfolio_series)
        benchmark_metrics = calculate_metrics(benchmark)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            delta = strategy_metrics['total_return'] - benchmark_metrics['total_return']
            st.metric("Total Return", f"{strategy_metrics['total_return']:.2f}%", delta=f"{delta:.2f}% vs QQQ")
        
        with col2:
            delta = strategy_metrics['sharpe'] - benchmark_metrics['sharpe']
            st.metric("Sharpe Ratio", f"{strategy_metrics['sharpe']:.3f}", delta=f"{delta:.3f} vs QQQ")
        
        with col3:
            st.metric("Win Rate", f"{strategy_metrics['win_rate']:.1f}%")
        
        with col4:
            delta = strategy_metrics['max_dd'] - benchmark_metrics['max_dd']
            st.metric("Max Drawdown", f"{strategy_metrics['max_dd']:.2f}%", delta=f"{delta:.2f}% vs QQQ", delta_color="inverse")
        
        with col5:
            st.metric("Volatility", f"{strategy_metrics['ann_vol']:.2f}%")
        
        # Performance Chart
        st.markdown('<p class="section-title">💹 Cumulative Returns</p>', unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=portfolio_series.index, y=(portfolio_series - 1) * 100,
                                name='Twitter Strategy', line=dict(color='#1DA1F2', width=3), fill='tonexty'))
        fig.add_trace(go.Scatter(x=benchmark.index, y=(benchmark - 1) * 100,
                                name='QQQ Benchmark', line=dict(color='#657786', width=3, dash='dash')))
        fig.update_layout(height=550, xaxis_title='Date', yaxis_title='Return (%)',
                         hovermode='x unified', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Top Sentiments")
            avg_sentiment = twitter_data.groupby('ticker')['sentiment'].mean().sort_values(ascending=False).head(15)
            fig = go.Figure()
            colors = ['#1DA1F2' if x > 0 else '#E1E8ED' for x in avg_sentiment.values]
            fig.add_trace(go.Bar(x=avg_sentiment.index, y=avg_sentiment.values, marker=dict(color=colors)))
            fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📋 Current Holdings")
            if holdings:
                latest_holdings = holdings[-1]
                latest_sentiment = processed_data[processed_data['date'] == latest_holdings['date']]
                latest_sentiment = latest_sentiment[latest_sentiment['ticker'].isin(latest_holdings['stocks'])]
                display_df = latest_sentiment[['ticker', 'sentiment', 'volume', 'rank']].sort_values('rank')
                display_df.columns = ['Ticker', 'Sentiment', 'Volume', 'Rank']
                st.dataframe(display_df.style.background_gradient(cmap='RdYlGn', subset=['Sentiment']),
                           use_container_width=True, height=400)
        
        # Download
        st.markdown("### 📥 Download Results")
        col1, col2 = st.columns(2)
        with col1:
            results_csv = pd.DataFrame({
                'Date': portfolio_series.index,
                'Strategy Return': (portfolio_series - 1) * 100
            }).to_csv(index=False)
            st.download_button("📈 Download Returns CSV", results_csv, "returns.csv", "text/csv")
        with col2:
            sentiment_csv = twitter_data.to_csv(index=False)
            st.download_button("💾 Download Sentiment Data", sentiment_csv, "sentiment.csv", "text/csv")
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        with st.expander("🔍 See details"):
            st.exception(e)

else:
    # Landing page
    st.markdown("""
    <div class='info-box'>
        <h3>🚀 Ready to Start?</h3>
        <p style='font-size: 1.1rem; margin-bottom: 0;'>
            Configure your strategy above and click <b>"RUN STRATEGY NOW"</b>!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🐦 Social Sentiment</h3>
            <p>Analyzes Twitter data to gauge market sentiment and investor psychology</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Volume Weighting</h3>
            <p>Weights sentiment by tweet volume for more reliable signals</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>💹 Dynamic Rebalancing</h3>
            <p>Automatically adjusts portfolio based on changing sentiment</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
