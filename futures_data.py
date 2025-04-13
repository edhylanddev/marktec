import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of popular futures to track
POPULAR_FUTURES = [
    # Equity index futures
    'ES=F',  # S&P 500 E-mini
    'NQ=F',  # Nasdaq-100 E-mini
    'YM=F',  # Dow Jones E-mini
    'RTY=F',  # Russell 2000 E-mini
    # Commodity futures
    'GC=F',  # Gold
    'SI=F',  # Silver
    'HG=F',  # Copper
    'CL=F',  # Crude Oil WTI
    'NG=F',  # Natural Gas
    'ZC=F',  # Corn
    'ZS=F',  # Soybeans
    'ZW=F',  # Wheat
    'KC=F',  # Coffee
    'SB=F',  # Sugar
    'CT=F',  # Cotton
    'CC=F',  # Cocoa
    # Interest rate futures
    'ZN=F',  # 10-Year T-Note
    'ZB=F',  # Treasury Bond
    'ZF=F',  # 5-Year T-Note
    'ZT=F',  # 2-Year T-Note
]

def fetch_futures_data(ticker, period="1y", interval="1d"):
    """
    Fetch historical data for a given futures contract
    
    Args:
        ticker (str): The ticker symbol of the futures contract
        period (str): The time period to fetch data for (e.g., '1d', '1mo', '1y')
        interval (str): The interval between data points (e.g., '1m', '1h', '1d')
        
    Returns:
        pandas.DataFrame: Historical data for the futures contract
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

def get_futures_info(ticker):
    """
    Get information about a futures contract
    
    Args:
        ticker (str): The ticker symbol of the futures contract
        
    Returns:
        dict: Information about the futures contract
    """
    try:
        ticker_yf = yf.Ticker(ticker)
        info = ticker_yf.info
        
        # Extract relevant information
        futures_info = {
            'name': info.get('shortName', ticker),
            'symbol': info.get('symbol', ticker),
            'market_cap': info.get('marketCap', None),
            'open_interest': info.get('openInterest', None),
            'expiration_date': info.get('expirationDate', None),
            'price': info.get('regularMarketPrice', None),
            'volume': info.get('regularMarketVolume', None),
            'price_change_24h_pct': info.get('regularMarketChangePercent', None),
            'description': info.get('description', 'No description available')
        }
        
        return futures_info
    except Exception as e:
        logger.error(f"Error getting info for {ticker}: {e}")
        return {
            'name': ticker,
            'symbol': ticker,
            'error': str(e)
        }

def get_futures_top_gainers(threshold=3.0, limit=20):
    """
    Get futures contracts with price increase greater than threshold in the last 24 hours
    
    Args:
        threshold (float): The minimum percentage increase (default: 3.0%)
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of dictionaries containing information about top gainers
    """
    gainers = []
    
    logger.info(f"Fetching futures top gainers with threshold: {threshold}%")
    
    try:
        # Check all popular futures
        for ticker in POPULAR_FUTURES:
            try:
                logger.info(f"Checking {ticker} for top gainer status")
                futures_info = get_futures_info(ticker)
                price_change = futures_info.get('price_change_24h_pct', 0)
                
                # Log what we find for debugging
                logger.info(f"{ticker}: 24h change is {price_change}%")
                
                # Better handle None values and ensure proper comparison
                if price_change is not None and isinstance(price_change, (int, float)) and price_change > threshold:
                    logger.info(f"Adding {ticker} to top gainers with {price_change}% change")
                    gainers.append({
                        'symbol': ticker,
                        'name': futures_info.get('name', ticker),
                        'price_change_pct': price_change,
                        'current_price': futures_info.get('price', 0)
                    })
            except Exception as e:
                logger.warning(f"Error processing {ticker}: {e}")
                continue
                
        # Sort by price change percentage (descending)
        gainers.sort(key=lambda x: x['price_change_pct'], reverse=True)
        
        # Log the results
        logger.info(f"Found {len(gainers)} futures top gainers above {threshold}% threshold")
        if gainers:
            logger.info(f"Top futures gainer: {gainers[0]['symbol']} with {gainers[0]['price_change_pct']}% change")
        
        return gainers[:limit]
    except Exception as e:
        logger.error(f"Error getting futures top gainers: {e}")
        return []

def search_futures(query):
    """
    Search for futures contracts by name or symbol
    
    Args:
        query (str): The search query
        
    Returns:
        list: List of matching futures contracts
    """
    try:
        # This is a simplified search just using the predefined list
        query = query.lower()
        results = []
        
        for ticker in POPULAR_FUTURES:
            if query in ticker.lower():
                info = get_futures_info(ticker)
                if info:
                    results.append({
                        'symbol': ticker,
                        'name': info.get('name', ticker)
                    })
                    
        return results
    except Exception as e:
        logger.error(f"Error searching for futures contracts: {e}")
        return []

def get_open_interest(ticker):
    """
    Get open interest data for a futures contract
    
    Args:
        ticker (str): The ticker symbol of the futures contract
        
    Returns:
        dict: Information about open interest
    """
    try:
        ticker_yf = yf.Ticker(ticker)
        info = ticker_yf.info
        
        open_interest = info.get('openInterest', None)
        
        if open_interest is not None:
            return {
                'open_interest': open_interest,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            return {
                'open_interest': 'Data not available from Yahoo Finance',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    except Exception as e:
        logger.error(f"Error getting open interest for {ticker}: {e}")
        return {
            'open_interest': 'Data not available',
            'error': str(e)
        }

def get_commitment_of_traders(ticker):
    """
    Get commitment of traders (COT) data for a futures contract
    Note: This is a placeholder function as Yahoo Finance doesn't provide this data directly
    In a real application, this would need to be fetched from a different API
    
    Args:
        ticker (str): The ticker symbol of the futures contract
        
    Returns:
        dict: Information about COT
    """
    # Note: This is a placeholder as Yahoo Finance doesn't provide COT data
    # In a real application, you would need to fetch this from CFTC or another data provider
    return {
        'commercial_long': 'Data not available from Yahoo Finance',
        'commercial_short': 'Data not available from Yahoo Finance',
        'non_commercial_long': 'Data not available from Yahoo Finance',
        'non_commercial_short': 'Data not available from Yahoo Finance'
    }