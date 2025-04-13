import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import logging

# Import local modules for crypto
from crypto_data import (
    fetch_crypto_data, get_crypto_info, get_top_gainers,
    search_crypto, get_long_short_positions, get_dark_pool_volume,
    POPULAR_CRYPTOS
)

# Import local modules for futures
from futures_data import (
    fetch_futures_data, get_futures_info, get_futures_top_gainers,
    search_futures, get_open_interest, get_commitment_of_traders,
    POPULAR_FUTURES
)

# Import local modules for currencies
from currency_data import (
    fetch_currency_data, get_currency_info, get_currency_top_gainers,
    search_currency, get_interest_rate_differential,
    POPULAR_CURRENCIES
)

from technical_analysis import create_chart
from utils import DataRefresher, format_large_number, get_color_from_change

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(
    page_title="Market Technical Analysis",
    page_icon="📈",
    layout="wide"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    
    # General settings
    st.session_state.last_refresh = datetime.now()
    st.session_state.refresh_interval = 120  # 2 minutes in seconds
    
    # Tab selection
    st.session_state.current_tab = "Cryptocurrencies"
    
    # Crypto state
    st.session_state.crypto_ticker_index = 0
    st.session_state.crypto_search_results = []
    st.session_state.crypto_df = None
    st.session_state.crypto_info = None
    st.session_state.crypto_top_gainers = []
    
    # Futures state
    st.session_state.futures_ticker_index = 0
    st.session_state.futures_search_results = []
    st.session_state.futures_df = None
    st.session_state.futures_info = None
    st.session_state.futures_top_gainers = []
    
    # Currency state
    st.session_state.currency_ticker_index = 0
    st.session_state.currency_search_results = []
    st.session_state.currency_df = None
    st.session_state.currency_info = None
    st.session_state.currency_top_gainers = []

# Function to refresh all data based on current tab
def refresh_data():
    try:
        st.session_state.last_refresh = datetime.now()
        
        # Refresh data based on current tab
        if st.session_state.current_tab == "Cryptocurrencies":
            refresh_crypto_data()
        elif st.session_state.current_tab == "Futures":
            refresh_futures_data()
        elif st.session_state.current_tab == "Currencies":
            refresh_currency_data()
            
        # Request a rerun to update the UI
        st.rerun()
    except Exception as e:
        logger.error(f"Error refreshing data: {e}")

# Function to refresh cryptocurrency data
def refresh_crypto_data():
    try:
        ticker = get_current_crypto_ticker()
        
        # Refresh current crypto data
        st.session_state.crypto_df = fetch_crypto_data(ticker)
        st.session_state.crypto_info = get_crypto_info(ticker)
        
        # Refresh top gainers
        st.session_state.crypto_top_gainers = get_top_gainers()
    except Exception as e:
        logger.error(f"Error refreshing crypto data: {e}")

# Function to refresh futures data
def refresh_futures_data():
    try:
        ticker = get_current_futures_ticker()
        
        # Refresh current futures data
        st.session_state.futures_df = fetch_futures_data(ticker)
        st.session_state.futures_info = get_futures_info(ticker)
        
        # Refresh top gainers
        st.session_state.futures_top_gainers = get_futures_top_gainers()
    except Exception as e:
        logger.error(f"Error refreshing futures data: {e}")

# Function to refresh currency data
def refresh_currency_data():
    try:
        ticker = get_current_currency_ticker()
        
        # Refresh current currency data
        st.session_state.currency_df = fetch_currency_data(ticker)
        st.session_state.currency_info = get_currency_info(ticker)
        
        # Refresh top gainers
        st.session_state.currency_top_gainers = get_currency_top_gainers()
    except Exception as e:
        logger.error(f"Error refreshing currency data: {e}")

# Helper functions to get current tickers
def get_current_crypto_ticker():
    if st.session_state.crypto_search_results:
        # If there are search results, use the current result
        return st.session_state.crypto_search_results[st.session_state.crypto_ticker_index]['symbol']
    else:
        # Otherwise use the default list
        return POPULAR_CRYPTOS[st.session_state.crypto_ticker_index % len(POPULAR_CRYPTOS)]

def get_current_futures_ticker():
    if st.session_state.futures_search_results:
        # If there are search results, use the current result
        return st.session_state.futures_search_results[st.session_state.futures_ticker_index]['symbol']
    else:
        # Otherwise use the default list
        return POPULAR_FUTURES[st.session_state.futures_ticker_index % len(POPULAR_FUTURES)]

def get_current_currency_ticker():
    if st.session_state.currency_search_results:
        # If there are search results, use the current result
        return st.session_state.currency_search_results[st.session_state.currency_ticker_index]['symbol']
    else:
        # Otherwise use the default list
        return POPULAR_CURRENCIES[st.session_state.currency_ticker_index % len(POPULAR_CURRENCIES)]

# Initialize data refresher
refresher = DataRefresher(st.session_state.refresh_interval)
refresher.start(refresh_data)

# Title and tab selection
st.title("Market Technical Analysis")

# Create tabs for different asset classes
tab1, tab2, tab3 = st.tabs(["Cryptocurrencies", "Futures", "Currencies"])

# Set the current tab based on which tab is clicked
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Cryptocurrencies"

# Function to create top gainers marquee
def create_top_gainers_marquee(gainers, asset_type="cryptocurrencies"):
    if gainers:
        # Display number of gainers found
        st.caption(f"Found {len(gainers)} {asset_type} with >3% gains in the last 24 hours")
        
        # Create a horizontal scrolling effect with HTML/CSS with improved styling
        marquee_html = """
        <div style="overflow-x: auto; white-space: nowrap; padding: 15px 0; 
                    background-color: rgba(0, 100, 0, 0.05); border-radius: 10px; border: 1px solid #ddd;">
        """
        
        for gainer in gainers:
            symbol = gainer.get('symbol', 'N/A')
            name = gainer.get('name', symbol)
            price_change = gainer.get('price_change_pct', 0)
            current_price = gainer.get('current_price', 0)
            
            # Format the price and change
            price_str = f"${current_price:.2f}" if isinstance(current_price, (int, float)) else str(current_price)
            change_str = f"+{price_change:.2f}%" if isinstance(price_change, (int, float)) else str(price_change)
            color = "green" if isinstance(price_change, (int, float)) and price_change > 0 else "red"
            
            # Enhanced styling for each item
            marquee_html += f"""
            <span style="display: inline-block; margin-right: 30px; padding: 8px 15px; 
                        background-color: rgba(255,255,255,0.8); border-radius: 5px; 
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <strong>{symbol}</strong> ({name}): {price_str} 
                <span style="color: {color}; font-weight: bold;">{change_str}</span>
            </span>
            """
        
        marquee_html += """
        <div style="text-align: center; font-size: 10px; margin-top: 5px; color: #666;">
            Scroll horizontally to see more ➡️
        </div>
        </div>
        """
        st.markdown(marquee_html, unsafe_allow_html=True)
    else:
        # More descriptive message when no gainers are found
        st.warning(f"No {asset_type} with gains above 3% in the last 24 hours were found. Market might be down today or data might be temporarily unavailable.")

# Set refresh interval in sidebar for all tabs
with st.sidebar:
    st.title("Settings")
    refresh_interval = st.slider("Refresh Interval (seconds)", 
                            min_value=30, max_value=300, 
                            value=st.session_state.refresh_interval, 
                            step=30)
    
    if refresh_interval != st.session_state.refresh_interval:
        st.session_state.refresh_interval = refresh_interval
        refresher.stop()
        refresher = DataRefresher(refresh_interval)
        refresher.start(refresh_data)
    
    st.caption(f"Last data refresh: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")

# Content for Cryptocurrencies tab
with tab1:
    st.session_state.current_tab = "Cryptocurrencies"
    st.markdown("### Cryptocurrency Analysis")
    st.markdown("Comprehensive technical analysis for cryptocurrencies with real-time data from Yahoo Finance.")
    
    # Search and navigation controls
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_query = st.text_input("Search cryptocurrencies by ticker or name", key="crypto_search_input")
        if search_query:
            results = search_crypto(search_query)
            if results:
                st.session_state.crypto_search_results = results
                st.session_state.crypto_ticker_index = 0
                refresh_crypto_data()
            else:
                st.warning(f"No results found for '{search_query}'")
    
    with col2:
        if st.button("◀ Previous", key="crypto_prev"):
            if st.session_state.crypto_search_results:
                st.session_state.crypto_ticker_index = (st.session_state.crypto_ticker_index - 1) % len(st.session_state.crypto_search_results)
            else:
                st.session_state.crypto_ticker_index = (st.session_state.crypto_ticker_index - 1) % len(POPULAR_CRYPTOS)
            refresh_crypto_data()
    
    with col3:
        if st.button("Next ▶", key="crypto_next"):
            if st.session_state.crypto_search_results:
                st.session_state.crypto_ticker_index = (st.session_state.crypto_ticker_index + 1) % len(st.session_state.crypto_search_results)
            else:
                st.session_state.crypto_ticker_index = (st.session_state.crypto_ticker_index + 1) % len(POPULAR_CRYPTOS)
            refresh_crypto_data()
    
    # Get current ticker
    current_crypto = get_current_crypto_ticker()
    
    # Fetch data if not already in session state
    if 'crypto_df' not in st.session_state or st.session_state.crypto_df is None:
        st.session_state.crypto_df = fetch_crypto_data(current_crypto)
        
    if 'crypto_info' not in st.session_state or st.session_state.crypto_info is None:
        st.session_state.crypto_info = get_crypto_info(current_crypto)
    
    if 'crypto_top_gainers' not in st.session_state or not st.session_state.crypto_top_gainers:
        st.session_state.crypto_top_gainers = get_top_gainers()
    
    # Display data
    if st.session_state.crypto_df is not None:
        # Create main chart
        chart = create_chart(
            st.session_state.crypto_df, 
            current_crypto, 
            st.session_state.crypto_info
        )
        st.plotly_chart(chart, use_container_width=True)
        
        # Add explanation of signals
        st.info("""
        **Trading Signals:**
        - **🟢 Buy Signal (Green Triangle Up)**: Appears when price crosses above a support level, indicating a potential buying opportunity
        - **🔴 Sell Signal (Red Triangle Down)**: Appears when price crosses above a resistance level, indicating a potential selling opportunity
        
        Support and resistance levels are shown as horizontal dashed lines (green for support, red for resistance).
        """)
        
        # Display additional market data
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Market Information")
            
            market_cap = st.session_state.crypto_info.get('market_cap', 'N/A')
            if market_cap and isinstance(market_cap, (int, float)):
                market_cap = format_large_number(market_cap)
                
            circulating_supply = st.session_state.crypto_info.get('circulating_supply', 'N/A')
            if circulating_supply and isinstance(circulating_supply, (int, float)):
                circulating_supply = f"{circulating_supply:,.0f} coins"
                
            price = st.session_state.crypto_info.get('price', 'N/A')
            if price and isinstance(price, (int, float)):
                price = f"${price:,.2f}"
                
            price_change = st.session_state.crypto_info.get('price_change_24h_pct', 'N/A')
            if price_change and isinstance(price_change, (int, float)):
                price_change = f"{price_change:.2f}%"
            
            market_data = {
                "Current Price": price,
                "24h Change": price_change,
                "Market Cap": market_cap,
                "Circulating Supply": circulating_supply,
                "Total Supply": st.session_state.crypto_info.get('total_supply', 'N/A'),
                "Max Supply": st.session_state.crypto_info.get('max_supply', 'N/A')
            }
            
            for key, value in market_data.items():
                st.write(f"**{key}:** {value}")
        
        with col2:
            st.subheader("Position Data")
            
            # Get long/short data
            position_data = get_long_short_positions(current_crypto)
            
            st.write(f"**Long Positions:** {position_data.get('long_positions_estimate', 'N/A')}")
            st.write(f"**Short Positions:** {position_data.get('short_positions_estimate', 'N/A')}")
            
            # Dark pool volume
            st.subheader("Dark Pool Volume")
            dark_pool_data = get_dark_pool_volume(current_crypto)
            st.write(f"**Dark Pool Volume:** {dark_pool_data.get('dark_pool_volume_estimate', 'N/A')}")
        
    else:
        st.error(f"Failed to fetch data for {current_crypto}. Please try another cryptocurrency.")
    
    # Create the scrolling marquee for top gainers
    st.markdown("---")
    st.subheader("🔥 Top Crypto Gainers (>3% in 24h) 🔥")
    create_top_gainers_marquee(st.session_state.crypto_top_gainers, "cryptocurrencies")

# Content for Futures tab
with tab2:
    st.session_state.current_tab = "Futures"
    st.markdown("### Futures Analysis")
    st.markdown("Comprehensive technical analysis for futures contracts with real-time data from Yahoo Finance.")
    
    # Search and navigation controls for futures
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_query = st.text_input("Search futures by ticker or name", key="futures_search_input")
        if search_query:
            results = search_futures(search_query)
            if results:
                st.session_state.futures_search_results = results
                st.session_state.futures_ticker_index = 0
                refresh_futures_data()
            else:
                st.warning(f"No results found for '{search_query}'")
    
    with col2:
        if st.button("◀ Previous", key="futures_prev"):
            if st.session_state.futures_search_results:
                st.session_state.futures_ticker_index = (st.session_state.futures_ticker_index - 1) % len(st.session_state.futures_search_results)
            else:
                st.session_state.futures_ticker_index = (st.session_state.futures_ticker_index - 1) % len(POPULAR_FUTURES)
            refresh_futures_data()
    
    with col3:
        if st.button("Next ▶", key="futures_next"):
            if st.session_state.futures_search_results:
                st.session_state.futures_ticker_index = (st.session_state.futures_ticker_index + 1) % len(st.session_state.futures_search_results)
            else:
                st.session_state.futures_ticker_index = (st.session_state.futures_ticker_index + 1) % len(POPULAR_FUTURES)
            refresh_futures_data()
    
    # Get current futures ticker
    current_futures = get_current_futures_ticker()
    
    # Fetch futures data if not already in session state
    if 'futures_df' not in st.session_state or st.session_state.futures_df is None:
        st.session_state.futures_df = fetch_futures_data(current_futures)
        
    if 'futures_info' not in st.session_state or st.session_state.futures_info is None:
        st.session_state.futures_info = get_futures_info(current_futures)
    
    if 'futures_top_gainers' not in st.session_state or not st.session_state.futures_top_gainers:
        st.session_state.futures_top_gainers = get_futures_top_gainers()
    
    # Display futures data
    if st.session_state.futures_df is not None:
        # Create main chart for futures
        chart = create_chart(
            st.session_state.futures_df, 
            current_futures, 
            st.session_state.futures_info
        )
        st.plotly_chart(chart, use_container_width=True)
        
        # Add explanation of signals for futures
        st.info("""
        **Trading Signals:**
        - **🟢 Buy Signal (Green Triangle Up)**: Appears when price crosses above a support level, indicating a potential buying opportunity
        - **🔴 Sell Signal (Red Triangle Down)**: Appears when price crosses above a resistance level, indicating a potential selling opportunity
        
        Support and resistance levels are shown as horizontal dashed lines (green for support, red for resistance).
        """)
        
        # Display additional futures market data
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Contract Information")
            
            price = st.session_state.futures_info.get('price', 'N/A')
            if price and isinstance(price, (int, float)):
                price = f"${price:,.2f}"
                
            price_change = st.session_state.futures_info.get('price_change_24h_pct', 'N/A')
            if price_change and isinstance(price_change, (int, float)):
                price_change = f"{price_change:.2f}%"
            
            expiration = st.session_state.futures_info.get('expiration_date', 'N/A')
            
            futures_data = {
                "Current Price": price,
                "24h Change": price_change,
                "Expiration Date": expiration,
                "Volume": st.session_state.futures_info.get('volume', 'N/A')
            }
            
            for key, value in futures_data.items():
                st.write(f"**{key}:** {value}")
        
        with col2:
            st.subheader("Open Interest")
            
            # Get open interest data
            open_interest_data = get_open_interest(current_futures)
            st.write(f"**Open Interest:** {open_interest_data.get('open_interest', 'N/A')}")
            
            # COT data
            st.subheader("Commitment of Traders")
            cot_data = get_commitment_of_traders(current_futures)
            st.write(f"**Commercial Long:** {cot_data.get('commercial_long', 'N/A')}")
            st.write(f"**Commercial Short:** {cot_data.get('commercial_short', 'N/A')}")
            st.write(f"**Non-Commercial Long:** {cot_data.get('non_commercial_long', 'N/A')}")
            st.write(f"**Non-Commercial Short:** {cot_data.get('non_commercial_short', 'N/A')}")
        
    else:
        st.error(f"Failed to fetch data for {current_futures}. Please try another futures contract.")
    
    # Create the scrolling marquee for futures top gainers
    st.markdown("---")
    st.subheader("🔥 Top Futures Gainers (>3% in 24h) 🔥")
    create_top_gainers_marquee(st.session_state.futures_top_gainers, "futures contracts")

# Content for Currencies tab
with tab3:
    st.session_state.current_tab = "Currencies"
    st.markdown("### Currency Analysis")
    st.markdown("Comprehensive technical analysis for currency pairs with real-time data from Yahoo Finance.")
    
    # Search and navigation controls for currencies
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_query = st.text_input("Search currency pairs by ticker or name", key="currency_search_input")
        if search_query:
            results = search_currency(search_query)
            if results:
                st.session_state.currency_search_results = results
                st.session_state.currency_ticker_index = 0
                refresh_currency_data()
            else:
                st.warning(f"No results found for '{search_query}'")
    
    with col2:
        if st.button("◀ Previous", key="currency_prev"):
            if st.session_state.currency_search_results:
                st.session_state.currency_ticker_index = (st.session_state.currency_ticker_index - 1) % len(st.session_state.currency_search_results)
            else:
                st.session_state.currency_ticker_index = (st.session_state.currency_ticker_index - 1) % len(POPULAR_CURRENCIES)
            refresh_currency_data()
    
    with col3:
        if st.button("Next ▶", key="currency_next"):
            if st.session_state.currency_search_results:
                st.session_state.currency_ticker_index = (st.session_state.currency_ticker_index + 1) % len(st.session_state.currency_search_results)
            else:
                st.session_state.currency_ticker_index = (st.session_state.currency_ticker_index + 1) % len(POPULAR_CURRENCIES)
            refresh_currency_data()
    
    # Get current currency ticker
    current_currency = get_current_currency_ticker()
    
    # Fetch currency data if not already in session state
    if 'currency_df' not in st.session_state or st.session_state.currency_df is None:
        st.session_state.currency_df = fetch_currency_data(current_currency)
        
    if 'currency_info' not in st.session_state or st.session_state.currency_info is None:
        st.session_state.currency_info = get_currency_info(current_currency)
    
    if 'currency_top_gainers' not in st.session_state or not st.session_state.currency_top_gainers:
        st.session_state.currency_top_gainers = get_currency_top_gainers()
    
    # Display currency data
    if st.session_state.currency_df is not None:
        # Create main chart for currency
        chart = create_chart(
            st.session_state.currency_df, 
            current_currency, 
            st.session_state.currency_info
        )
        st.plotly_chart(chart, use_container_width=True)
        
        # Add explanation of signals for currency
        st.info("""
        **Trading Signals:**
        - **🟢 Buy Signal (Green Triangle Up)**: Appears when price crosses above a support level, indicating a potential buying opportunity
        - **🔴 Sell Signal (Red Triangle Down)**: Appears when price crosses above a resistance level, indicating a potential selling opportunity
        
        Support and resistance levels are shown as horizontal dashed lines (green for support, red for resistance).
        """)
        
        # Display additional currency market data
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Market Information")
            
            price = st.session_state.currency_info.get('price', 'N/A')
            if price and isinstance(price, (int, float)):
                price = f"{price:.4f}"
                
            price_change = st.session_state.currency_info.get('price_change_24h_pct', 'N/A')
            if price_change and isinstance(price_change, (int, float)):
                price_change = f"{price_change:.2f}%"
            
            bid = st.session_state.currency_info.get('bid', 'N/A')
            if bid and isinstance(bid, (int, float)):
                bid = f"{bid:.4f}"
                
            ask = st.session_state.currency_info.get('ask', 'N/A')
            if ask and isinstance(ask, (int, float)):
                ask = f"{ask:.4f}"
                
            day_low = st.session_state.currency_info.get('day_range_low', 'N/A')
            if day_low and isinstance(day_low, (int, float)):
                day_low = f"{day_low:.4f}"
                
            day_high = st.session_state.currency_info.get('day_range_high', 'N/A')
            if day_high and isinstance(day_high, (int, float)):
                day_high = f"{day_high:.4f}"
            
            currency_data = {
                "Current Rate": price,
                "24h Change": price_change,
                "Bid": bid,
                "Ask": ask,
                "Day Range": f"{day_low} - {day_high}" if day_low != 'N/A' and day_high != 'N/A' else 'N/A'
            }
            
            for key, value in currency_data.items():
                st.write(f"**{key}:** {value}")
        
        with col2:
            st.subheader("Interest Rate Differential")
            
            # Get interest rate differential data
            interest_data = get_interest_rate_differential(current_currency)
            if '=' in current_currency:
                base_currency = current_currency.split('=')[0][:3]
                quote_currency = current_currency.split('=')[0][3:]
                st.write(f"**{base_currency} Interest Rate:** {interest_data.get('base_currency_rate', 'N/A')}")
                st.write(f"**{quote_currency} Interest Rate:** {interest_data.get('quote_currency_rate', 'N/A')}")
                st.write(f"**Interest Rate Differential:** {interest_data.get('differential', 'N/A')}")
            else:
                st.write(f"**Interest Rate Differential:** {interest_data.get('interest_rate_differential', 'N/A')}")
        
    else:
        st.error(f"Failed to fetch data for {current_currency}. Please try another currency pair.")
    
    # Create the scrolling marquee for currency top gainers
    st.markdown("---")
    st.subheader("🔥 Top Currency Gainers (>3% in 24h) 🔥")
    create_top_gainers_marquee(st.session_state.currency_top_gainers, "currency pairs")

# Footer with disclaimer
st.markdown("---")
st.caption("""
**Disclaimer:** This application is for informational purposes only and does not constitute financial advice. 
Trading cryptocurrencies involves risk. Please do your own research before making any investment decisions.
""")
