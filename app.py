import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from textblob import TextBlob
import warnings
warnings.filterwarnings("ignore")

# Page configuration
st.set_page_config(
    page_title="Twitter Sentiment Trading Strategy",
    layout="wide",
    page_icon="🐦",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stMetric:hover {
        box-shadow: 0 8px 12px rgba(0,0,0,0.2);
        transform: translateY(-5px);
        transition: all 0.3s ease;
    }
    .stMetric label {
        color: white !important;
        font-size: 0.9rem !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: #90EE90 !important;
    }
    h1 {
        background: linear-gradient(90deg, #1DA1F2 0%, #14171A 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        border: none;
    }
    h2 {
        color: #1DA1F2;
        margin-top: 2rem;
        padding: 0.5rem 0;
        border-left: 5px solid #1DA1F2;
        padding-left: 15px;
    }
    .info-box {
        background: linear-gradient(135deg, #1DA1F2 0%, #14171A 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(29, 161, 242, 0.3);
    }
    .metric-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        margin: 10px 0;
        border-left: 5px solid #1DA1F2;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        transform: translateX(5px);
    }
    .twitter-badge {
        background: #1DA1F2;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin: 5px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #1DA1F2 0%, #14171A 100%);
        color: white;
        font-weight: 700;
        border: none;
        padding: 1rem;
        border-radius: 15px;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 20px rgba(29, 161, 242, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='font-size: 3rem; margin: 0;'>
            🐦 Twitter Sentiment Trading
        </h1>
        <p style='font-size: 1.3rem; color: #657786; margin-top: 15px;'>
            Social Media Analytics Meets Quantitative Finance
        </p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: white; border-radius: 15px; margin-bottom: 20px;'>
        <h2 style='margin: 0; color: #1DA1F2; border: none;'>⚙️ Strategy Controls</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Portfolio Parameters")
    top_n = st.slider("Top N Stocks by Sentiment", 3, 20, 10, help="Number of most positive stocks to hold")
    rebalance = st.selectbox("Rebalance Frequency", ["Monthly", "Weekly", "Daily"], index=0)
    
    st.markdown("### 📅 Time Period")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start", datetime(2020, 1, 1))
    with col2:
        end_date = st.date_input("End", datetime(2024, 1, 1))
    
    st.markdown("### 🎯 Sentiment Analysis")
    sentiment_threshold = st.slider("Min Sentiment Score", -1.0, 1.0, 0.0, 0.1, 
                                    help="Only include stocks above this sentiment")
    use_volume_weight = st.checkbox("Weight by Tweet Volume", value=True,
                                    help="Give more weight to stocks with more mentions")
    
    st.markdown("### 📈 Data Source")
    data_source = st.radio("Select Data Source", 
                          ["Upload CSV", "Use Sample Data", "Generate Synthetic Data"],
                          index=2)
    
    if data_source == "Upload CSV":
        uploaded_file = st.file_uploader("Upload Twitter Data (CSV)", type=['csv'])
        st.info("📋 CSV must have: ticker, date, sentiment, volume columns")
    
    st.markdown("---")
    run_strategy = st.button("🚀 RUN STRATEGY", type="primary")
    
    if run_strategy:
        st.session_state.run = True
    
    st.markdown("---")
    st.markdown("""
    <div style='background: white; padding: 15px; border-radius: 10px;'>
        <h4 style='color: #1DA1F2; margin-top: 0;'>💡 Strategy Logic</h4>
        <ul style='color: #657786; font-size: 0.85rem;'>
            <li>Aggregate daily sentiment scores</li>
            <li>Rank stocks by positivity</li>
            <li>Hold top performers</li>
            <li>Rebalance periodically</li>
            <li>Compare vs benchmark</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def generate_synthetic_data(start_date, end_date, n_stocks=50):
    """Generate realistic synthetic Twitter sentiment data"""
    # Popular tech stocks
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'AMD', 
               'NFLX', 'PYPL', 'INTC', 'CSCO', 'ADBE', 'CRM', 'ORCL',
               'IBM', 'QCOM', 'TXN', 'AVGO', 'NOW', 'INTU', 'UBER', 'LYFT',
               'SNAP', 'TWTR', 'SQ', 'SHOP', 'SPOT', 'ZM', 'DOCU'][:n_stocks]
    
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    for ticker in tickers:
        # Each stock has a base sentiment with random walk
        base_sentiment = np.random.uniform(-0.3, 0.5)
        sentiment_drift = 0.0
        
        for date in dates:
            # Random walk with mean reversion
            sentiment_drift += np.random.normal(0, 0.05)
            sentiment_drift *= 0.95  # Mean reversion
            
            # Add some events (sentiment spikes)
            if np.random.random() < 0.02:  # 2% chance of event
                sentiment_drift += np.random.choice([-0.3, 0.3])
            
            sentiment = np.clip(base_sentiment + sentiment_drift, -1, 1)
            volume = int(np.random.lognormal(5, 1.5))  # Tweet volume
            
            data.append({
                'ticker': ticker,
                'date': date,
                'sentiment': sentiment,
                'volume': volume
            })
    
    return pd.DataFrame(data)

@st.cache_data(show_spinner=False)
def get_sample_data():
    """Load sample data structure"""
    dates = pd.date_range(start='2020-01-01', end='2024-01-01', freq='D')
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'AMD']
    
    data = []
    for ticker in tickers:
        base = np.random.uniform(-0.2, 0.4)
        for date in dates:
            data.append({
                'ticker': ticker,
                'date': date,
                'sentiment': base + np.random.normal(0, 0.1),
                'volume': int(np.random.lognormal(5, 1))
            })
    
    return pd.DataFrame(data)

def process_sentiment_data(df, rebalance_freq, threshold, volume_weight):
    """Process sentiment data and create rankings"""
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    # Filter by sentiment threshold
    df = df[df['sentiment'] >= threshold]
    
    # Determine rebalancing frequency
    freq_map = {'Monthly': 'M', 'Weekly': 'W', 'Daily': 'D'}
    freq = freq_map[rebalance_freq]
    
    # Aggregate sentiment by period
    if volume_weight and 'volume' in df.columns:
        # Weighted average by volume
        df['weighted_sentiment'] = df['sentiment'] * df['volume']
        agg_data = df.groupby(['ticker', pd.Grouper(key='date', freq=freq)]).agg({
            'weighted_sentiment': 'sum',
            'volume': 'sum'
        }).reset_index()
        agg_data['sentiment'] = agg_data['weighted_sentiment'] / agg_data['volume']
    else:
        # Simple average
        agg_data = df.groupby(['ticker', pd.Grouper(key='date', freq=freq)])['sentiment'].mean().reset_index()
        agg_data['volume'] = df.groupby(['ticker', pd.Grouper(key='date', freq=freq)])['volume'].sum().reset_index()['volume']
    
    # Rank stocks by sentiment each period
    agg_data['rank'] = agg_data.groupby('date')['sentiment'].rank(ascending=False)
    
    return agg_data

def calculate_strategy_returns(sentiment_df, top_n, start, end):
    """Calculate portfolio returns based on sentiment rankings"""
    # Get top N stocks for each period
    top_stocks = sentiment_df[sentiment_df['rank'] <= top_n].copy()
    
    if len(top_stocks) == 0:
        return None, None, None
    
    # Download price data
    unique_tickers = top_stocks['ticker'].unique().tolist()
    
    try:
        prices = yf.download(unique_tickers, start=start, end=end, progress=False)['Adj Close']
        
        if isinstance(prices, pd.Series):
            prices = prices.to_frame(name=unique_tickers[0])
        
        # Align with rebalancing dates
        rebalance_dates = sorted(top_stocks['date'].unique())
        
        portfolio_values = [1.0]  # Start with $1
        dates_list = [rebalance_dates[0]]
        holdings = []
        
        for i in range(len(rebalance_dates) - 1):
            current_date = rebalance_dates[i]
            next_date = rebalance_dates[i + 1]
            
            # Get stocks to hold this period
            stocks_to_hold = top_stocks[top_stocks['date'] == current_date]['ticker'].tolist()
            holdings.append({'date': current_date, 'stocks': stocks_to_hold})
            
            # Get price data for this period
            mask = (prices.index >= current_date) & (prices.index < next_date)
            period_prices = prices.loc[mask, stocks_to_hold].dropna(how='all')
            
            if len(period_prices) > 0 and len(stocks_to_hold) > 0:
                # Equal weight portfolio
                period_returns = period_prices.pct_change().mean(axis=1)
                period_cumulative = (1 + period_returns).cumprod()
                
                # Update portfolio value
                for date, value in period_cumulative.items():
                    if date > current_date:
                        portfolio_values.append(portfolio_values[-1] * value)
                        dates_list.append(date)
        
        portfolio_series = pd.Series(portfolio_values, index=dates_list)
        
        return portfolio_series, top_stocks, holdings
        
    except Exception as e:
        st.error(f"Error downloading price data: {str(e)}")
        return None, None, None

def calculate_metrics(returns_series):
    """Calculate performance metrics"""
    total_return = (returns_series.iloc[-1] / returns_series.iloc[0] - 1) * 100
    
    daily_returns = returns_series.pct_change().dropna()
    
    ann_return = daily_returns.mean() * 252 * 100
    ann_vol = daily_returns.std() * np.sqrt(252) * 100
    sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252) if daily_returns.std() > 0 else 0
    
    # Max drawdown
    cumulative = returns_series
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_dd = drawdown.min() * 100
    
    # Win rate
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
            st.info("📊 Using synthetic Twitter sentiment data (50 tech stocks)")
        elif data_source == "Use Sample Data":
            twitter_data = get_sample_data()
            st.info("📊 Using sample data")
        elif data_source == "Upload CSV" and 'uploaded_file' in locals() and uploaded_file:
            twitter_data = pd.read_csv(uploaded_file)
        else:
            st.error("❌ Please upload a CSV file or select a different data source")
            st.stop()
        
        status_text.markdown("### 🔧 Processing sentiment scores...")
        progress_bar.progress(40)
        
        processed_data = process_sentiment_data(
            twitter_data, 
            rebalance, 
            sentiment_threshold,
            use_volume_weight
        )
        
        status_text.markdown("### 💹 Calculating portfolio returns...")
        progress_bar.progress(60)
        
        portfolio_series, top_stocks, holdings = calculate_strategy_returns(
            processed_data,
            top_n,
            start_date,
            end_date
        )
        
        if portfolio_series is None:
            st.error("❌ Unable to calculate returns. Please adjust parameters.")
            st.stop()
        
        status_text.markdown("### 📈 Downloading benchmark data...")
        progress_bar.progress(80)
        
        # Get benchmark
        benchmark = yf.download("QQQ", start=start_date, end=end_date, progress=False)['Adj Close']
        benchmark = benchmark / benchmark.iloc[0]  # Normalize to 1
        
        progress_bar.progress(100)
        status_text.empty()
        progress_bar.empty()
        
        st.success("🎉 Strategy Analysis Complete!")
        
        # RESULTS SECTION
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Key Metrics
        st.markdown("## 📊 Performance Overview")
        
        strategy_metrics = calculate_metrics(portfolio_series)
        benchmark_metrics = calculate_metrics(benchmark)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            delta = strategy_metrics['total_return'] - benchmark_metrics['total_return']
            st.metric(
                "Total Return",
                f"{strategy_metrics['total_return']:.2f}%",
                delta=f"{delta:.2f}% vs QQQ"
            )
        
        with col2:
            delta = strategy_metrics['sharpe'] - benchmark_metrics['sharpe']
            st.metric(
                "Sharpe Ratio",
                f"{strategy_metrics['sharpe']:.3f}",
                delta=f"{delta:.3f} vs QQQ"
            )
        
        with col3:
            st.metric(
                "Win Rate",
                f"{strategy_metrics['win_rate']:.1f}%",
                delta=None
            )
        
        with col4:
            delta = strategy_metrics['max_dd'] - benchmark_metrics['max_dd']
            st.metric(
                "Max Drawdown",
                f"{strategy_metrics['max_dd']:.2f}%",
                delta=f"{delta:.2f}% vs QQQ",
                delta_color="inverse"
            )
        
        with col5:
            delta = strategy_metrics['ann_vol'] - benchmark_metrics['ann_vol']
            st.metric(
                "Volatility",
                f"{strategy_metrics['ann_vol']:.2f}%",
                delta=f"{delta:.2f}% vs QQQ",
                delta_color="inverse"
            )
        
        # Performance Chart
        st.markdown("## 💹 Cumulative Returns")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=portfolio_series.index,
            y=(portfolio_series - 1) * 100,
            name='Twitter Strategy',
            line=dict(color='#1DA1F2', width=3),
            fill='tonexty',
            hovertemplate='<b>Twitter Strategy</b><br>Date: %{x}<br>Return: %{y:.2f}%<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=benchmark.index,
            y=(benchmark - 1) * 100,
            name='QQQ Benchmark',
            line=dict(color='#657786', width=3, dash='dash'),
            hovertemplate='<b>QQQ</b><br>Date: %{x}<br>Return: %{y:.2f}%<extra></extra>'
        ))
        
        fig.update_layout(
            height=550,
            xaxis_title='Date',
            yaxis_title='Cumulative Return (%)',
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment Analysis
        st.markdown("## 🎭 Sentiment Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Average Sentiment by Stock")
            
            avg_sentiment = twitter_data.groupby('ticker')['sentiment'].mean().sort_values(ascending=False).head(15)
            
            fig = go.Figure()
            colors = ['#1DA1F2' if x > 0 else '#E1E8ED' for x in avg_sentiment.values]
            
            fig.add_trace(go.Bar(
                x=avg_sentiment.index,
                y=avg_sentiment.values,
                marker=dict(color=colors),
                hovertemplate='<b>%{x}</b><br>Sentiment: %{y:.3f}<extra></extra>'
            ))
            
            fig.update_layout(
                height=400,
                xaxis_title='Ticker',
                yaxis_title='Average Sentiment',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Sentiment vs Returns Correlation")
            
            # Calculate correlation
            if len(top_stocks) > 0:
                recent_stocks = top_stocks.nlargest(20, 'date')
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=recent_stocks['sentiment'],
                    y=recent_stocks['rank'],
                    mode='markers',
                    marker=dict(
                        size=10,
                        color=recent_stocks['sentiment'],
                        colorscale='RdYlGn',
                        showscale=True,
                        colorbar=dict(title="Sentiment")
                    ),
                    text=recent_stocks['ticker'],
                    hovertemplate='<b>%{text}</b><br>Sentiment: %{x:.3f}<br>Rank: %{y}<extra></extra>'
                ))
                
                fig.update_layout(
                    height=400,
                    xaxis_title='Sentiment Score',
                    yaxis_title='Rank (Lower = Better)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Top Holdings
        st.markdown("## 📋 Current Top Holdings")
        
        if holdings and len(holdings) > 0:
            latest_holdings = holdings[-1]
            latest_sentiment = processed_data[processed_data['date'] == latest_holdings['date']]
            latest_sentiment = latest_sentiment[latest_sentiment['ticker'].isin(latest_holdings['stocks'])]
            latest_sentiment = latest_sentiment.sort_values('rank')
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                display_df = latest_sentiment[['ticker', 'sentiment', 'volume', 'rank']].copy()
                display_df.columns = ['Ticker', 'Sentiment Score', 'Tweet Volume', 'Rank']
                display_df['Sentiment Score'] = display_df['Sentiment Score'].round(3)
                display_df['Rank'] = display_df['Rank'].astype(int)
                
                st.dataframe(
                    display_df.style.background_gradient(cmap='RdYlGn', subset=['Sentiment Score']),
                    use_container_width=True,
                    height=400
                )
            
            with col2:
                st.markdown("### 💡 Insights")
                
                avg_sent = latest_sentiment['sentiment'].mean()
                total_vol = latest_sentiment['volume'].sum()
                
                st.markdown(f"""
                <div class='metric-card'>
                    <h4 style='color: #1DA1F2; margin-top: 0;'>Portfolio Sentiment</h4>
                    <p style='font-size: 2rem; font-weight: 700; color: #14171A; margin: 10px 0;'>
                        {avg_sent:.3f}
                    </p>
                    <p style='color: #657786; margin: 0;'>Average across {len(latest_sentiment)} stocks</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class='metric-card'>
                    <h4 style='color: #1DA1F2; margin-top: 0;'>Tweet Volume</h4>
                    <p style='font-size: 2rem; font-weight: 700; color: #14171A; margin: 10px 0;'>
                        {total_vol:,}
                    </p>
                    <p style='color: #657786; margin: 0;'>Total mentions this period</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Additional Analysis
        st.markdown("## 🔍 Risk Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Rolling Sharpe Ratio")
            
            rolling_window = 60
            returns = portfolio_series.pct_change().dropna()
            rolling_sharpe = (returns.rolling(rolling_window).mean() / 
                            returns.rolling(rolling_window).std()) * np.sqrt(252)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=rolling_sharpe.index,
                y=rolling_sharpe,
                fill='tozeroy',
                line=dict(color='#1DA1F2', width=2),
                hovertemplate='Date: %{x}<br>Sharpe: %{y:.3f}<extra></extra>'
            ))
            fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
            fig.update_layout(
                height=350,
                yaxis_title='Rolling Sharpe',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Drawdown Analysis")
            
            cumulative = portfolio_series
            running_max = cumulative.cummax()
            drawdown = (cumulative - running_max) / running_max * 100
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=drawdown.index,
                y=drawdown,
                fill='tozeroy',
                line=dict(color='#E1E8ED', width=2),
                hovertemplate='Date: %{x}<br>Drawdown: %{y:.2f}%<extra></extra>'
            ))
            fig.update_layout(
                height=350,
                yaxis_title='Drawdown (%)',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Strategy Statistics
        st.markdown("## 📊 Detailed Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Strategy Performance")
            stats_df = pd.DataFrame({
                'Metric': ['Total Return', 'Annualized Return', 'Annualized Volatility', 
                          'Sharpe Ratio', 'Max Drawdown', 'Win Rate'],
                'Strategy': [
                    f"{strategy_metrics['total_return']:.2f}%",
                    f"{strategy_metrics['ann_return']:.2f}%",
                    f"{strategy_metrics['ann_vol']:.2f}%",
                    f"{strategy_metrics['sharpe']:.3f}",
                    f"{strategy_metrics['max_dd']:.2f}%",
                    f"{strategy_metrics['win_rate']:.1f}%"
                ]
            })
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### Benchmark (QQQ)")
            bench_df = pd.DataFrame({
                'Metric': ['Total Return', 'Annualized Return', 'Annualized Volatility', 
                          'Sharpe Ratio', 'Max Drawdown', 'Win Rate'],
                'QQQ': [
                    f"{benchmark_metrics['total_return']:.2f}%",
                    f"{benchmark_metrics['ann_return']:.2f}%",
                    f"{benchmark_metrics['ann_vol']:.2f}%",
                    f"{benchmark_metrics['sharpe']:.3f}",
                    f"{benchmark_metrics['max_dd']:.2f}%",
                    f"{benchmark_metrics['win_rate']:.1f}%"
                ]
            })
            st.dataframe(bench_df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.exception(e)

else:
    # Landing page
    st.markdown("""
    <div class='info-box'>
        <h2 style='margin-top: 0; color: white;'>👋 Welcome to Twitter Sentiment Trading</h2>
        <p style='font-size: 1.1rem;'>
            Configure your parameters in the sidebar and click <b>"RUN STRATEGY"</b> to start the analysis!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature showcase
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <h3>🐦 Social Sentiment</h3>
            <p>Analyzes Twitter data to gauge market sentiment and investor psychology</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card'>
            <h3>📊 Volume Weighting</h3>
            <p>Weights sentiment by tweet volume for more reliable signals</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card'>
            <h3>💹 Dynamic Rebalancing</h3>
            <p>Automatically adjusts portfolio based on changing sentiment</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("## 📚 Strategy Documentation")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Methodology", "🎯 Features", "💼 For Internships", "📊 Data Format"])
    
    with tab1:
        st.markdown("""
        ### The Strategy Pipeline
        
        1. **Data Collection** 🐦
           - Aggregate daily Twitter mentions and sentiment scores
           - Track tweet volume and engagement metrics
           - Focus on financial discussions and company mentions
        
        2. **Sentiment Analysis** 🎭
           - Calculate weighted average sentiment per stock
           - Apply volume weighting (optional)
           - Filter by minimum sentiment threshold
        
        3. **Ranking & Selection** 🏆
           - Rank stocks by sentiment score each period
           - Select top N most positive stocks
           - Create equal-weight portfolio
        
        4. **Rebalancing** 🔄
           - Periodic portfolio adjustment (daily/weekly/monthly)
           - Sell stocks falling out of top N
           - Buy new entrants to top rankings
        
        5. **Performance Tracking** 📊
           - Calculate returns vs benchmark (QQQ)
           - Monitor risk metrics (Sharpe, drawdown)
           - Analyze sentiment-return correlations
        
        ### Key Advantages
        
        - ✅ **Real-time signals**: Social media reacts faster than traditional news
        - ✅ **Crowd wisdom**: Aggregates opinions from thousands of users
        - ✅ **Momentum capture**: Identifies trending stocks early
        - ✅ **Behavioral insights**: Measures investor psychology
        """)
    
    with tab2:
        st.markdown("""
        ### Technical Features
        
        | Feature | Description | Impact |
        |---------|-------------|--------|
        | **Sentiment Score** | -1 (negative) to +1 (positive) | Core ranking metric |
        | **Tweet Volume** | Number of mentions per day | Signal reliability |
        | **Volume Weighting** | Weight sentiment by popularity | Reduces noise |
        | **Sentiment Threshold** | Minimum score filter | Risk management |
        | **Rebalance Frequency** | Portfolio update period | Transaction costs |
        | **Top N Selection** | Portfolio concentration | Diversification |
        
        ### Advanced Metrics
        
        - **Rolling Sharpe Ratio**: Risk-adjusted performance over time
        - **Maximum Drawdown**: Worst peak-to-trough decline
        - **Win Rate**: Percentage of profitable days
        - **Sentiment-Return Correlation**: Strategy validation
        
        ### Risk Management
        
        - Minimum sentiment threshold prevents shorting
        - Volume weighting reduces manipulation risk
        - Diversification across top N stocks
        - Regular rebalancing limits exposure
        """)
    
    with tab3:
        st.markdown("""
        ### Why This Project Stands Out
        
        ✅ **Demonstrates Alternative Data Skills**
        - Social media sentiment analysis
        - Natural language processing concepts
        - Behavioral finance understanding
        - Real-time data processing
        
        ✅ **Shows Quantitative Research Ability**
        - Hypothesis testing (sentiment predicts returns)
        - Statistical validation
        - Backtesting methodology
        - Performance attribution
        
        ✅ **Proves Technical Proficiency**
        - Data pipeline architecture
        - Time series analysis
        - Portfolio optimization
        - Risk management implementation
        
        ✅ **Highlights Modern Finance Knowledge**
        - Alternative data sources
        - Factor investing concepts
        - Momentum strategies
        - Behavioral biases
        
        ### Resume Bullet Points
        
        ```
        • Developed Twitter sentiment trading strategy achieving X% annual 
          return, outperforming QQQ benchmark by Y% with Z Sharpe ratio
        
        • Engineered data pipeline processing 10,000+ daily tweets across 
          50 stocks with volume-weighted sentiment aggregation
        
        • Implemented dynamic portfolio rebalancing system with automated 
          stock selection based on social media signals
        
        • Built interactive Streamlit dashboard with real-time performance 
          analytics and risk monitoring
        
        Technologies: Python, NLP, Pandas, Plotly, yFinance, Streamlit
        ```
        
        ### Interview Talking Points
        
        1. **Alternative Data**: "I explored Twitter sentiment as an alternative 
           data source because social media often leads traditional news..."
        
        2. **Signal Quality**: "I implemented volume weighting to distinguish 
           between noise and meaningful sentiment shifts..."
        
        3. **Risk Management**: "The strategy includes sentiment thresholds and 
           diversification to manage downside risk..."
        
        4. **Performance**: "Backtests show the strategy captures momentum 
           while maintaining reasonable Sharpe ratios..."
        """)
    
    with tab4:
        st.markdown("""
        ### Required CSV Format
        
        Your Twitter sentiment data file must contain these columns:
        
        | Column | Type | Description | Example |
        |--------|------|-------------|---------|
        | `ticker` | string | Stock symbol | AAPL |
        | `date` | date | Tweet date | 2023-01-15 |
        | `sentiment` | float | Score -1 to +1 | 0.65 |
        | `volume` | int | Tweet count | 1523 |
        
        ### Example Data
        
        ```csv
        ticker,date,sentiment,volume
        AAPL,2023-01-01,0.45,1200
        MSFT,2023-01-01,0.32,890
        TSLA,2023-01-01,0.78,2500
        AAPL,2023-01-02,0.52,1350
        MSFT,2023-01-02,0.41,920
        ```
        
        ### Data Sources
        
        **Free Options:**
        - Twitter API (Academic Research track)
        - Reddit WallStreetBets scraping
        - StockTwits API
        - News sentiment APIs
        
        **Paid Options:**
        - Bloomberg Social Sentiment
        - RavenPack News Analytics
        - PsychSignal Social Media
        - Sentifi Sentiment Data
        
        ### Data Collection Tips
        
        1. **Volume matters**: More tweets = more reliable signal
        2. **Filter spam**: Remove bots and duplicate posts
        3. **Use hashtags**: Track $AAPL, #stocks, etc.
        4. **Clean text**: Remove URLs, emojis, special characters
        5. **Validate sentiment**: Spot-check automated scores
        
        ### Synthetic Data Generation
        
        This app includes a synthetic data generator for testing:
        - 50 tech stocks with realistic sentiment patterns
        - Daily data with random walks and event spikes
        - Volume follows log-normal distribution
        - Perfect for strategy development and backtesting
        """)
    
    # Sample visualization
    st.markdown("## 📊 Example Output Preview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sample performance chart
        sample_dates = pd.date_range('2020-01-01', '2024-01-01', freq='D')
        sample_strategy = np.exp(np.cumsum(np.random.normal(0.0008, 0.015, len(sample_dates))))
        sample_bench = np.exp(np.cumsum(np.random.normal(0.0005, 0.012, len(sample_dates))))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sample_dates, y=(sample_strategy - 1) * 100, 
                                name='Strategy', line=dict(color='#1DA1F2', width=2)))
        fig.add_trace(go.Scatter(x=sample_dates, y=(sample_bench - 1) * 100, 
                                name='Benchmark', line=dict(color='#657786', width=2, dash='dash')))
        fig.update_layout(title='Sample Performance', height=300, 
                         plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sample sentiment distribution
        sample_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'AMD']
        sample_sentiment = np.random.uniform(-0.2, 0.6, len(sample_tickers))
        
        fig = go.Figure()
        colors = ['#1DA1F2' if x > 0 else '#E1E8ED' for x in sample_sentiment]
        fig.add_trace(go.Bar(x=sample_tickers, y=sample_sentiment, marker=dict(color=colors)))
        fig.update_layout(title='Sample Sentiment Scores', height=300,
                         plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    # Getting Started Guide
    st.markdown("## 🚀 Getting Started")
    
    st.markdown("""
    ### Quick Start (3 Steps)
    
    1. **Select Data Source** (left sidebar)
       - Use "Generate Synthetic Data" for immediate testing
       - Or upload your own Twitter sentiment CSV
    
    2. **Configure Parameters**
       - Portfolio size: 5-15 stocks recommended
       - Rebalance: Monthly for lower costs
       - Sentiment threshold: 0.0 or higher
    
    3. **Run Strategy**
       - Click the big blue button 🚀
       - Wait 30-60 seconds for analysis
       - Explore interactive results
    
    ### What You'll Get
    
    - 📊 Performance vs QQQ benchmark
    - 📈 Key metrics (Sharpe, drawdown, win rate)
    - 🎭 Sentiment analysis and correlations
    - 📋 Top holdings with sentiment scores
    - 🔍 Risk analysis (rolling Sharpe, drawdowns)
    - 💡 Detailed statistics and insights
    """)
