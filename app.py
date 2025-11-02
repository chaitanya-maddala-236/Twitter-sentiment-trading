def calculate_strategy_returns(sentiment_df, top_n, start, end):
    """Calculate portfolio returns"""
    top_stocks = sentiment_df[sentiment_df['rank'] <= top_n].copy()
    
    if len(top_stocks) == 0:
        return None, None, None
    
    unique_tickers = top_stocks['ticker'].unique().tolist()
    
    try:
        prices = yf.download(unique_tickers, start=start, end=end, progress=False)['Adj Close']
        
        if isinstance(prices, pd.Series):
            prices = prices.to_frame(name=unique_tickers[0])
        
        # Handle both single and multiple ticker downloads
        if len(unique_tickers) == 1:
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
