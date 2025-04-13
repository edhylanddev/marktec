import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
import random 

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function for handling rate limiting
def fetch_with_retry(func, *args, max_attempts=5, initial_delay=1, **kwargs):
    """
    Execute a function with retry logic and exponential backoff
    
    Args:
        func: The function to execute
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        *args, **kwargs: Arguments to pass to the function
        
    Returns:
        The result of the function call
    """
    delay = initial_delay
    last_exception = None
    attemp_count = 0
    
    for attempt_count in range(max_attempts):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            # Check if it's a rate limit error (429)
            if "429" in str(e) or "Too Many Requests" in str(e):
                # Add jitter to avoid synchronized retries
                jitter = random.uniform(0, 0.5)
                sleep_time = delay + jitter
                logger.warning(f"Rate limit exceeded. Retrying in {sleep_time:.2f} seconds (attempt {attempt_count + 1}/{max_attempts})")
                time.sleep(sleep_time)
                # Exponential backoff
                delay *= 2
            else:
                # If it's not a rate limit error, don't retry
                break
    
    # If we've exhausted all attempts or hit a non-rate limit error
    if last_exception is not None:
        logger.error(f"Failed after {attempt_count + 1} attempts: {last_exception}")
        raise last_exception
    else:
        logger.error("Function failed without an exception")
        raise RuntimeError("Function failed for unknown reason")
        
# List of popular currency pairs to track
POPULAR_CURRENCIES = [
    # Major pairs
    'EURUSD=X',  # Euro/US Dollar
    'USDJPY=X',  # US Dollar/Japanese Yen
    'GBPUSD=X',  # British Pound/US Dollar
    'USDCHF=X',  # US Dollar/Swiss Franc
    'AUDUSD=X',  # Australian Dollar/US Dollar
    'USDCAD=X',  # US Dollar/Canadian Dollar
    'NZDUSD=X',  # New Zealand Dollar/US Dollar
    # Minor/Cross pairs
    'EURGBP=X',  # Euro/British Pound
    'EURJPY=X',  # Euro/Japanese Yen
    'EURCHF=X',  # Euro/Swiss Franc
    'GBPJPY=X',  # British Pound/Japanese Yen
    'CHFJPY=X',  # Swiss Franc/Japanese Yen
    'EURAUD=X',  # Euro/Australian Dollar
    'GBPCHF=X',  # British Pound/Swiss Franc
    # Exotic pairs
    'USDZAR=X',  # US Dollar/South African Rand
    'USDTRY=X',  # US Dollar/Turkish Lira
    'USDMXN=X',  # US Dollar/Mexican Peso
    'USDBRL=X',  # US Dollar/Brazilian Real
    'USDRUB=X',  # US Dollar/Russian Ruble
    'USDINR=X',  # US Dollar/Indian Rupee
]

def fetch_currency_data(ticker, period="1y", interval="1d"):
    """
    Fetch historical data for a given currency pair
    
    Args:
        ticker (str): The ticker symbol of the currency pair
        period (str): The time period to fetch data for (e.g., '1d', '1mo', '1y')
        interval (str): The interval between data points (e.g., '1m', '1h', '1d')
        
    Returns:
        pandas.DataFrame: Historical data for the currency pair
    """
    try:
        ticker_yf = yf.Ticker(ticker)
        df = ticker_yf.history(period=period, interval=interval)
        
        if df.empty:
            logger.error(f"No data retrieved for {ticker}")
            return None
            
        # Reset index to make Date a column
        df.reset_index(inplace=True)
        
        # Rename columns to standard names
        df.rename(columns={'Date': 'date', 'Open': 'open', 'High': 'high', 
                          'Low': 'low', 'Close': 'close', 'Volume': 'volume'}, 
                  inplace=True)
        
        return df
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {e}")
        return None

def get_currency_info(ticker):
    """
    Get information about a currency pair
    
    Args:
        ticker (str): The ticker symbol of the currency pair
        
    Returns:
        dict: Information about the currency pair
    """
    try:
        ticker_yf = yf.Ticker(ticker)
        info = ticker_yf.info
        
        # Format the currency name for display
        if '=' in ticker:
            base_currency = ticker.split('=')[0][:3]
            quote_currency = ticker.split('=')[0][3:]
            pair_name = f"{base_currency}/{quote_currency}"
        else:
            pair_name = ticker
        
        # Extract relevant information
        currency_info = {
            'name': info.get('shortName', pair_name),
            'symbol': info.get('symbol', ticker),
            'price': info.get('regularMarketPrice', None),
            'volume': info.get('regularMarketVolume', None),
            'price_change_24h_pct': info.get('regularMarketChangePercent', None),
            'bid': info.get('bid', None),
            'ask': info.get('ask', None),
            'day_range_low': info.get('regularMarketDayLow', None),
            'day_range_high': info.get('regularMarketDayHigh', None),
            'description': info.get('description', 'No description available')
        }
        
        return currency_info
    except Exception as e:
        logger.error(f"Error getting info for {ticker}: {e}")
        
        # Format the currency name for display even when there's an error
        if '=' in ticker:
            base_currency = ticker.split('=')[0][:3]
            quote_currency = ticker.split('=')[0][3:]
            pair_name = f"{base_currency}/{quote_currency}"
        else:
            pair_name = ticker
            
        return {
            'name': pair_name,
            'symbol': ticker,
            'error': str(e)
        }

def get_currency_top_gainers(threshold=3.0, limit=20):
    """
    Get currency pairs with price increase greater than threshold in the last 24 hours
    
    Args:
        threshold (float): The minimum percentage increase (default: 3.0%)
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of dictionaries containing information about top gainers
    """
    gainers = []
    
    logger.info(f"Fetching currency top gainers with threshold: {threshold}%")
    
    try:
        # Check all popular currency pairs
        for ticker in POPULAR_CURRENCIES:
            try:
                logger.info(f"Checking {ticker} for top gainer status")
                currency_info = get_currency_info(ticker)
                price_change = currency_info.get('price_change_24h_pct', 0)
                
                # Log what we find for debugging
                logger.info(f"{ticker}: 24h change is {price_change}%")
                
                # Better handle None values and ensure proper comparison
                if price_change is not None and isinstance(price_change, (int, float)) and price_change > threshold:
                    logger.info(f"Adding {ticker} to top gainers with {price_change}% change")
                    gainers.append({
                        'symbol': ticker,
                        'name': currency_info.get('name', ticker),
                        'price_change_pct': price_change,
                        'current_price': currency_info.get('price', 0)
                    })
            except Exception as e:
                logger.warning(f"Error processing {ticker}: {e}")
                continue
                
        # Sort by price change percentage (descending)
        gainers.sort(key=lambda x: x['price_change_pct'], reverse=True)
        
        # Log the results
        logger.info(f"Found {len(gainers)} currency top gainers above {threshold}% threshold")
        if gainers:
            logger.info(f"Top currency gainer: {gainers[0]['symbol']} with {gainers[0]['price_change_pct']}% change")
        
        return gainers[:limit]
    except Exception as e:
        logger.error(f"Error getting currency top gainers: {e}")
        return []

def search_currency(query):
    """
    Search for currency pairs by name or symbol
    
    Args:
        query (str): The search query
        
    Returns:
        list: List of matching currency pairs
    """
    try:
        # This is a simplified search just using the predefined list
        query = query.lower()
        results = []
        
        for ticker in POPULAR_CURRENCIES:
            # Extract currency codes for better matching
            if '=' in ticker:
                base_currency = ticker.split('=')[0][:3].lower()
                quote_currency = ticker.split('=')[0][3:].lower()
                
                if (query in base_currency or 
                    query in quote_currency or 
                    query in ticker.lower()):
                    
                    info = get_currency_info(ticker)
                    if info:
                        results.append({
                            'symbol': ticker,
                            'name': info.get('name', ticker)
                        })
            elif query in ticker.lower():
                info = get_currency_info(ticker)
                if info:
                    results.append({
                        'symbol': ticker,
                        'name': info.get('name', ticker)
                    })
                    
        return results
    except Exception as e:
        logger.error(f"Error searching for currency pairs: {e}")
        return []

def get_interest_rate_differential(ticker):
    """
    Get interest rate differential data for a currency pair
    Note: This is a placeholder function as Yahoo Finance doesn't provide this data directly
    In a real application, this would need to be fetched from a different API
    
    Args:
        ticker (str): The ticker symbol of the currency pair
        
    Returns:
        dict: Information about interest rate differential
    """
    # Note: This is a placeholder as Yahoo Finance doesn't provide interest rate differential data
    # In a real application, you would need to fetch this from a central bank or another data provider
    if '=' in ticker:
        base_currency = ticker.split('=')[0][:3]
        quote_currency = ticker.split('=')[0][3:]
        return {
            'base_currency_rate': f'{base_currency} interest rate data not available from Yahoo Finance',
            'quote_currency_rate': f'{quote_currency} interest rate data not available from Yahoo Finance',
            'differential': 'Data not available from Yahoo Finance'
        }
    else:
        return {
            'interest_rate_differential': 'Data not available from Yahoo Finance'
        }