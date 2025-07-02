import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.stock_data import get_stock_data, get_stock_info, yahoo_search_stocks
from utils.charts import create_line_chart, create_candlestick_chart, add_moving_averages
from utils.settings_manager import load_user_favourites, save_user_favourites

username = st.session_state['username']

if "favourite_stocks" not in st.session_state:
    st.session_state.favourite_stocks = load_user_favourites(username)

# Page configuration
st.set_page_config(
    page_title="Dashboard - Stock Dashboard",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication check
if not st.session_state.get("authentication_status"):
    st.error("Please log in to access the dashboard")
    if st.button("Go to Login"):
        st.switch_page("main.py")
    st.stop()

# Dashboard CSS
st.markdown("""
<style>
    .main .block-container {
        max-width: 1200px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .stDataFrame {
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "favourite_stocks" not in st.session_state:
    st.session_state.favourite_stocks = []

if "selected_stock_from_search" not in st.session_state:
    st.session_state.selected_stock_from_search = None

if "selected_stock_from_favourites" not in st.session_state:
    st.session_state.selected_stock_from_favourites = None

# Initialize theme state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Dashboard header
st.title("Stock Visualization Dashboard")
st.markdown(f"Welcome back, **{st.session_state['name']}**!")

# Sidebar
with st.sidebar:
    st.markdown(f"**Username:** {st.session_state['username']}")
    st.markdown("---")
    st.title("Stock Search & Controls")
    
    # Search functionality
    search_query = st.text_input(
        "Search by company name or ticker",
        placeholder="e.g., Apple, Reliance, AAPL, RELIANCE.NS",
        key="stock_search_input"
    )
    
    selected_stock = None
    
    # Handle search results
    if search_query and len(search_query) >= 2:
        with st.spinner("Searching..."):
            suggestions = yahoo_search_stocks(search_query)
    
        if suggestions:
            display_options = ["Select a stock..."]
            stock_mapping = {"Select a stock...": None}
            
            for suggestion in suggestions:
                name = suggestion['name'][:40] + "..." if len(suggestion['name']) > 40 else suggestion['name']
                display_text = f"{name} ({suggestion['symbol']}) - {suggestion['exchange']}"
                display_options.append(display_text)
                stock_mapping[display_text] = suggestion['symbol']
            
            if display_options:
                selected_option = st.selectbox(
                    "Select from suggestions:",
                    options=display_options,
                    key="search_selectbox"
                )
                
                if selected_option != "Select a stock...":
                    selected_stock = stock_mapping.get(selected_option)
                    st.session_state.selected_stock_from_search = selected_stock
        else:
            st.info("No results found. Try a different search term.")
    
    # Use the selected stock from search if available
    if st.session_state.selected_stock_from_search:
        selected_stock = st.session_state.selected_stock_from_search
    
    # Favourites Section
    st.markdown("---")
    st.markdown("### Favourite Stocks")

    # Add to favourites button
    if selected_stock and selected_stock not in st.session_state.favourite_stocks:
        add_button_key = f"add_fav_{selected_stock}_{len(st.session_state.favourite_stocks)}"
        if st.button(f"Add {selected_stock} to Favourites", key=add_button_key):
            st.session_state.favourite_stocks.append(selected_stock)
            save_user_favourites(username, st.session_state.favourite_stocks)
            st.success(f"Added {selected_stock} to favourites!")

    # Display favourite stocks for quick access
    if st.session_state.favourite_stocks:
        # Quick select from favourites
        st.markdown("**Quick Select:**")
        fav_choice = st.selectbox(
            "Choose from favourites",
            ["Select from favourites..."] + st.session_state.favourite_stocks,
            key="fav_selectbox"
        )
        
        if fav_choice != "Select from favourites...":
            selected_stock = fav_choice
            st.session_state.selected_stock_from_favourites = fav_choice
            # Clear search selection when using favourites
            st.session_state.selected_stock_from_search = None
        
        # Remove from favourites option
        st.markdown("**Manage Favourites:**")
        stock_to_remove = st.selectbox(
            "Remove from favourites",
            ["Select to remove..."] + st.session_state.favourite_stocks,
            key="remove_fav_selectbox"
        )
        
        if stock_to_remove != "Select to remove...":
            remove_button_key = f"remove_fav_{stock_to_remove}"
            if st.button(f"Remove {stock_to_remove}", key=remove_button_key):
                st.session_state.favourite_stocks.remove(stock_to_remove)
                save_user_favourites(username, st.session_state.favourite_stocks)
                st.success(f"Removed {stock_to_remove} from favourites!")
                if st.session_state.selected_stock_from_favourites == stock_to_remove:
                    st.session_state.selected_stock_from_favourites = None
    else:
        st.info("No favourites yet. Search and add stocks to your favourites for quick access!")

    # Use favourites selection if available
    if st.session_state.selected_stock_from_favourites:
        selected_stock = st.session_state.selected_stock_from_favourites

    # Controls with default values (no user preferences)
    st.markdown("---")
    time_periods = {
        '1 Week': '1wk',
        '1 Month': '1mo',
        '3 Months': '3mo',
        '6 Months': '6mo',
        '1 Year': '1y',
        '2 Years': '2y'
    }
    
    # Use default values instead of user settings
    selected_period = st.selectbox(
        "Select Time Period", 
        list(time_periods.keys()),
        index=1  # Default to 1 Month
    )
    
    # Use default chart type
    chart_options = ["Line Chart", "Candlestick Chart"]
    chart_type = st.radio(
        "Chart Type", 
        chart_options,
        index=0  # Default to Line Chart
    )
    
    # Use default moving averages setting
    show_ma = st.checkbox(
        "Show Moving Averages (20 & 50 day)",
        value=False  # Default to False
    )
    
    # RESTORED Theme toggle
    st.markdown("---")
    st.markdown("### Theme Settings")

    def toggle_theme():
        st.session_state.dark_mode = not st.session_state.dark_mode
        
        if st.session_state.dark_mode:
            st._config.set_option('theme.base', 'dark')
            st._config.set_option('theme.backgroundColor', '#0E1117')
            st._config.set_option('theme.secondaryBackgroundColor', '#262730')
            st._config.set_option('theme.textColor', '#FAFAFA')
            st._config.set_option('theme.primaryColor', '#FF6B6B')
        else:
            st._config.set_option('theme.base', 'light')
            st._config.set_option('theme.backgroundColor', '#FFFFFF')
            st._config.set_option('theme.secondaryBackgroundColor', '#F0F2F6')
            st._config.set_option('theme.textColor', '#262730')
            st._config.set_option('theme.primaryColor', '#1f77b4')

    theme_text = "Dark Mode" if not st.session_state.dark_mode else "Light Mode"

    if st.button(theme_text, key="simple_theme_toggle", use_container_width=True):
        toggle_theme()
        st.rerun()

    st.caption(f"Current: {'Dark' if st.session_state.dark_mode else 'Light'} Theme")

    st.markdown("---")
    if st.button("Profile", use_container_width=True):
        st.switch_page("pages/profile.py")
    
    if st.button("Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.logout_flag = True
        st.session_state.manual_navigation = True
        st.switch_page("main.py")

# Main content
if selected_stock:
    # Stock info display
    with st.spinner(f"Loading data for {selected_stock}..."):
        stock_info = get_stock_info(selected_stock)
    
    if stock_info:
        st.subheader(f"{stock_info['name']} ({selected_stock})")
        
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
            if change > 0:
                st.success(f"Up {change:.2f} ({change_percent:.2f}%)")
            elif change < 0:
                st.error(f"Down {change:.2f} ({change_percent:.2f}%)")
            else:
                st.info("No Change")
    
    # Chart display
    with st.spinner("Loading chart data..."):
        stock_data = get_stock_data(selected_stock, time_periods[selected_period])
    
    if stock_data is not None and not stock_data.empty:
        st.subheader(f"{selected_stock} - {selected_period} Chart")
        
        if chart_type == "Line Chart":
            fig = create_line_chart(stock_data, selected_stock)
            if show_ma:
                fig = add_moving_averages(fig, stock_data.copy(), selected_stock)
        else:
            fig = create_candlestick_chart(stock_data, selected_stock)
            if show_ma:
                fig = add_moving_averages(fig, stock_data.copy(), selected_stock)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistics
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Period Statistics")
            period_high = stock_data['High'].max()
            period_low = stock_data['Low'].min()
            avg_volume = stock_data['Volume'].mean()
            
            st.write(f"**Period High:** {currency_symbol}{period_high:.2f}")
            st.write(f"**Period Low:** {currency_symbol}{period_low:.2f}")
            st.write(f"**Average Volume:** {avg_volume:,.0f}")
        
        with col2:
            st.subheader("Recent Performance")
            recent_data = stock_data.tail(10)
            
            st.dataframe(
                recent_data[['Open', 'High', 'Low', 'Close', 'Volume']].round(2),
                use_container_width=True,
                height=400
            )
        
        if st.checkbox("Show Complete Historical Data"):
            st.subheader("Complete Historical Data")
            st.dataframe(
                stock_data[['Open', 'High', 'Low', 'Close', 'Volume']].round(2),
                use_container_width=True,
                height=500
            )
    else:
        st.error(f"Could not fetch data for {selected_stock}. Please check the ticker symbol.")

else:
    st.info("Use the search bar in the sidebar to find and analyze stocks")
    
    st.markdown("""
    ### Features:
    - **Smart Search**: Search stocks by company name or ticker
    - **Global Markets**: Support for US, Indian, and international stocks
    - **Multi-Currency**: Automatic currency detection
    - **Multiple Chart Types**: Line charts and candlestick charts
    - **Technical Analysis**: Moving averages and trend indicators
    - **Flexible Time Periods**: From 1 week to 2 years
    - **Favourites**: Save frequently viewed stocks for quick access
    """)
