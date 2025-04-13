import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of popular cryptocurrencies to track
POPULAR_CRYPTOS = [
    # Major coins
    'BTC-USD', 'ETH-USD', 'USDT-USD', 'BNB-USD', 'XRP-USD',
    'ADA-USD', 'SOL-USD', 'DOGE-USD', 'DOT-USD', 'SHIB-USD',
    # Mid-cap coins 
    'AVAX-USD', 'MATIC-USD', 'LTC-USD', 'UNI7083-USD', 'LINK-USD',
    'ATOM-USD', 'XLM-USD', 'ALGO-USD', 'MANA-USD', 'AXS-USD',
    # Additional popular coins
    'TRX-USD', 'NEAR-USD', 'FTM-USD', 'SAND-USD',
    'CRO-USD', 'AAVE-USD', 'XTZ-USD', 'EOS-USD', 'EGLD-USD',
    'THETA-USD', 'ZEC-USD', 'HBAR-USD', 'XMR-USD', 'GRT-USD',
    'FIL-USD', 'ICP-USD', 'VET-USD', 'CAKE-USD', 'ONE-USD'
]

def fetch_crypto_data(ticker, period="1y", interval="1d"):
    """
    Fetch historical data for a given cryptocurrency
    
    Args:
        ticker (str): The ticker symbol of the cryptocurrency
        period (str): The time period to fetch data for (e.g., '1d', '1mo', '1y')
        interval (str): The interval between data points (e.g., '1m', '1h', '1d')
        
    Returns:
        pandas.DataFrame: Historical data for the cryptocurrency
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

def get_crypto_info(ticker):
    """
    Get information about a cryptocurrency
    
    Args:
        ticker (str): The ticker symbol of the cryptocurrency
        
    Returns:
        dict: Information about the cryptocurrency
    """
    try:
        ticker_yf = yf.Ticker(ticker)
        info = ticker_yf.info
        
        # Extract relevant information
        crypto_info = {
            'name': info.get('name', ticker),
            'symbol': info.get('symbol', ticker),
            'market_cap': info.get('marketCap', None),
            'circulating_supply': info.get('circulatingSupply', None),
            'total_supply': info.get('totalSupply', None),
            'max_supply': info.get('maxSupply', None),
            'price': info.get('regularMarketPrice', None),
            'volume': info.get('regularMarketVolume', None),
            'price_change_24h_pct': info.get('regularMarketChangePercent', None),
            'description': info.get('description', 'No description available')
        }
        
        return crypto_info
    except Exception as e:
        logger.error(f"Error getting info for {ticker}: {e}")
        return {
            'name': ticker,
            'symbol': ticker,
            'error': str(e)
        }

def get_top_gainers(threshold=3.0, limit=20):
    """
    Get cryptocurrencies with price increase greater than threshold in the last 24 hours
    
    Args:
        threshold (float): The minimum percentage increase (default: 3.0%)
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of dictionaries containing information about top gainers
    """
    gainers = []
    
    logger.info(f"Fetching top gainers with threshold: {threshold}%")
    
    try:
        # First try with popular cryptos
        for ticker in POPULAR_CRYPTOS:
            try:
                logger.info(f"Checking {ticker} for top gainer status")
                crypto_info = get_crypto_info(ticker)
                price_change = crypto_info.get('price_change_24h_pct', 0)
                
                # Log what we find for debugging
                logger.info(f"{ticker}: 24h change is {price_change}%")
                
                # Better handle None values and ensure proper comparison
                if price_change is not None and isinstance(price_change, (int, float)) and price_change > threshold:
                    logger.info(f"Adding {ticker} to top gainers with {price_change}% change")
                    gainers.append({
                        'symbol': ticker,
                        'name': crypto_info.get('name', ticker),
                        'price_change_pct': price_change,
                        'current_price': crypto_info.get('price', 0)
                    })
            except Exception as e:
                logger.warning(f"Error processing {ticker}: {e}")
                continue
                
        # Sort by price change percentage (descending)
        gainers.sort(key=lambda x: x['price_change_pct'], reverse=True)
        
        # Log the results
        logger.info(f"Found {len(gainers)} top gainers above {threshold}% threshold")
        if gainers:
            logger.info(f"Top gainer: {gainers[0]['symbol']} with {gainers[0]['price_change_pct']}% change")
        
        return gainers[:limit]
    except Exception as e:
        logger.error(f"Error getting top gainers: {e}")
        return []

def search_crypto(query):
    """
    Search for cryptocurrencies by name or symbol
    
    Args:
        query (str): The search query
        
    Returns:
        list: List of matching cryptocurrencies
    """
    try:
        # This is a simplified search just using the predefined list
        # A more comprehensive solution would use an API that offers search functionality
        query = query.lower()
        results = []
        
        for ticker in POPULAR_CRYPTOS:
            if query in ticker.lower():
                info = get_crypto_info(ticker)
                if info:
                    results.append({
                        'symbol': ticker,
                        'name': info.get('name', ticker)
                    })
                    
        return results
    except Exception as e:
        logger.error(f"Error searching for cryptocurrencies: {e}")
        return []

def get_long_short_positions(ticker):
    """
    Get long/short positions data for a cryptocurrency
    Note: This is a placeholder function as Yahoo Finance doesn't provide this data directly
    In a real application, this would need to be fetched from a different API
    
    Args:
        ticker (str): The ticker symbol of the cryptocurrency
        
    Returns:
        dict: Information about long/short positions
    """
    # Note: This is simulated data since we don't have access to real long/short position data
    # In a real application, you would need to subscribe to a specific data provider
    return {
        'long_positions_estimate': 'Data not available from Yahoo Finance',
        'short_positions_estimate': 'Data not available from Yahoo Finance'
    }

def get_dark_pool_volume(ticker):
    """
    Get dark pool volume data for a cryptocurrency
    Note: This is a placeholder function as Yahoo Finance doesn't provide this data directly
    In a real application, this would need to be fetched from a different API
    
    Args:
        ticker (str): The ticker symbol of the cryptocurrency
        
    Returns:
        dict: Information about dark pool volume
    """
    # Note: This is simulated data since we don't have access to real dark pool volume data
    # In a real application, you would need to subscribe to a specific data provider
    return {
        'dark_pool_volume_estimate': 'Data not available from Yahoo Finance'
    }
