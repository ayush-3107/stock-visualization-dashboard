import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.stock_data import get_stock_data, get_stock_info, yahoo_search_stocks
from utils.charts import create_line_chart, create_candlestick_chart, add_moving_averages

# Check authentication
if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
    st.error('Please login first')
    if st.button('Go to Login'):
        st.switch_page("main.py")
    st.stop()

st.set_page_config(page_title="Stock Dashboard", layout="wide")

# Dashboard header
st.title("📈 Stock Visualization Dashboard")
st.markdown(f"Welcome back, **{st.session_state['name']}**!")

# Sidebar
st.sidebar.title("Stock Search & Controls")

# Search input
search_query = st.sidebar.text_input(
    "🔍 Search by company name or ticker",
    placeholder="e.g., Apple, Reliance, AAPL, RELIANCE.NS"
)

selected_stock = None

# Search functionality
if search_query and len(search_query) >= 2:
    with st.sidebar:
        with st.spinner("Searching..."):
            suggestions = yahoo_search_stocks(search_query)
    
    if suggestions:
        # Create display options
        display_options = []
        stock_mapping = {}
        
        for suggestion in suggestions:
            name = suggestion['name'][:40] + "..." if len(suggestion['name']) > 40 else suggestion['name']
            display_text = f"{name} ({suggestion['symbol']}) - {suggestion['exchange']}"
            display_options.append(display_text)
            stock_mapping[display_text] = suggestion['symbol']
        
        # Show suggestions in selectbox
        if display_options:
            selected_option = st.sidebar.selectbox(
                "Select from suggestions:",
                options=display_options,
                key="stock_selector"
            )
            selected_stock = stock_mapping.get(selected_option)
    else:
        st.sidebar.info("No results found. Try a different search term.")

# Manual ticker input as fallback
st.sidebar.markdown("---")
st.sidebar.write("**Or enter ticker directly:**")
manual_ticker = st.sidebar.text_input(
    "Enter stock ticker",
    placeholder="AAPL, RELIANCE.NS, TCS.NS"
).upper()

# Use manual ticker if no search selection
if not selected_stock and manual_ticker:
    selected_stock = manual_ticker

# Time period selection
st.sidebar.markdown("---")
time_periods = {
    '1 Week': '1wk',
    '1 Month': '1mo',
    '3 Months': '3mo',
    '6 Months': '6mo',
    '1 Year': '1y',
    '3 Years': '3y',
    '5 Years': '5y',
    'Max': 'max',
}
selected_period = st.sidebar.selectbox("📅 Select Time Period", list(time_periods.keys()))

# Chart type selection
chart_type = st.sidebar.radio("📊 Chart Type", ["Line Chart", "Candlestick Chart"])

# Technical indicators
show_ma = st.sidebar.checkbox("Show Moving Averages (20 & 50 day)")

# # Popular stocks suggestions
# st.sidebar.markdown("---")
# st.sidebar.write("**Quick Access:**")
# popular_stocks = {
#     "🇺🇸 US Stocks": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"],
#     "🇮🇳 Indian Stocks": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
# }

# for category, stocks in popular_stocks.items():
#     st.sidebar.write(f"**{category}:**")
#     cols = st.sidebar.columns(len(stocks))
#     for i, stock in enumerate(stocks):
#         if cols[i].button(stock, key=f"quick_{stock}"):
#             selected_stock = stock
#             st.rerun()

# Main dashboard content
if selected_stock:
    # Get stock info
    with st.spinner(f"Loading data for {selected_stock}..."):
        stock_info = get_stock_info(selected_stock)
    
    if stock_info:
        # Display basic info
        st.subheader(f"📊 {stock_info['name']} ({selected_stock})")
        
        col1, col2, col3, col4 = st.columns(4)
        
        currency_symbol = stock_info.get('currency_symbol', '$')
        current_price = stock_info['current_price']
        previous_close = stock_info['previous_close']
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100 if previous_close > 0 else 0
        
        with col1:
            st.metric(
                "Current Price", 
                f"{currency_symbol}{current_price:.2f}", 
                f"{change:.2f} ({change_percent:.2f}%)"
            )
        with col2:
            st.metric("Previous Close", f"{currency_symbol}{previous_close:.2f}")
        with col3:
            market_cap = stock_info['market_cap']
            if market_cap > 1e12:
                market_cap_display = f"{currency_symbol}{market_cap/1e12:.2f}T"
            elif market_cap > 1e9:
                market_cap_display = f"{currency_symbol}{market_cap/1e9:.2f}B"
            elif market_cap > 1e6:
                market_cap_display = f"{currency_symbol}{market_cap/1e6:.2f}M"
            else:
                market_cap_display = f"{currency_symbol}{market_cap:.0f}"
            st.metric("Market Cap", market_cap_display)
        with col4:
            # Color coding for change
            if change > 0:
                st.success(f"📈 +{change:.2f} ({change_percent:.2f}%)")
            elif change < 0:
                st.error(f"📉 {change:.2f} ({change_percent:.2f}%)")
            else:
                st.info("📊 No Change")
    
    # Get historical data
    with st.spinner("Loading chart data..."):
        stock_data = get_stock_data(selected_stock, time_periods[selected_period])
    
    if stock_data is not None and not stock_data.empty:
        # Display chart
        st.subheader(f"📈 {selected_stock} - {selected_period} Chart")
        
        if chart_type == "Line Chart":
            fig = create_line_chart(stock_data, selected_stock)
            if show_ma:
                fig = add_moving_averages(fig, stock_data.copy(), selected_stock)
        else:
            fig = create_candlestick_chart(stock_data, selected_stock)
            if show_ma:
                fig = add_moving_averages(fig, stock_data.copy(), selected_stock)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Period Statistics")
            period_high = stock_data['High'].max()
            period_low = stock_data['Low'].min()
            avg_volume = stock_data['Volume'].mean()
            
            st.write(f"**Period High:** {currency_symbol}{period_high:.2f}")
            st.write(f"**Period Low:** {currency_symbol}{period_low:.2f}")
            st.write(f"**Average Volume:** {avg_volume:,.0f}")
        
        with col2:
            st.subheader("📈 Recent Performance")
            recent_data = stock_data.tail(5)
            st.dataframe(
                recent_data[['Open', 'High', 'Low', 'Close', 'Volume']].round(2),
                use_container_width=True
            )
        
        # Display full data table
        if st.checkbox("Show Complete Historical Data"):
            st.subheader("📋 Complete Historical Data")
            st.dataframe(
                stock_data[['Open', 'High', 'Low', 'Close', 'Volume']].round(2),
                use_container_width=True
            )
    else:
        st.error(f"Could not fetch data for {selected_stock}. Please check the ticker symbol.")

else:
    # Welcome screen
    st.info("👆 Use the search bar in the sidebar to find and analyze stocks")
    
    st.markdown("""
    ### 🚀 Features:
    - **🔍 Smart Search**: Search stocks by company name or ticker
    - **🌍 Global Markets**: Support for US, Indian, and international stocks
    - **💱 Multi-Currency**: Automatic currency detection (₹, $, £, etc.)
    - **📊 Multiple Chart Types**: Line charts and candlestick charts
    - **📈 Technical Analysis**: Moving averages and trend indicators
    - **⏰ Flexible Time Periods**: From 1 week to 2 years
    
    ### 📝 How to Use:
    1. **Search** for a company by name (e.g., "Apple", "Reliance")
    2. **Select** from the suggestions or enter ticker directly
    3. **Customize** time period and chart type
    4. **Analyze** with technical indicators
    
    ### 💡 Examples:
    - **US Stocks**: AAPL, GOOGL, MSFT, TSLA
    - **Indian Stocks**: RELIANCE.NS, TCS.NS, INFY.NS
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Tip**: Indian stocks end with .NS (NSE) or .BO (BSE)")
