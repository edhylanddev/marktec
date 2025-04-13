import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_support_resistance(df, window=10):
    """
    Calculate support and resistance levels
    
    Args:
        df (pandas.DataFrame): DataFrame with price data
        window (int): Window size for identifying local minima and maxima
    
    Returns:
        tuple: Lists of support and resistance levels
    """
    try:
        supports = []
        resistances = []
        
        # Find local minima for support levels
        for i in range(window, len(df) - window):
            if all(df['low'][i] <= df['low'][i-j] for j in range(1, window+1)) and \
               all(df['low'][i] <= df['low'][i+j] for j in range(1, window+1)):
                supports.append((df['date'][i], df['low'][i]))
        
        # Find local maxima for resistance levels
        for i in range(window, len(df) - window):
            if all(df['high'][i] >= df['high'][i-j] for j in range(1, window+1)) and \
               all(df['high'][i] >= df['high'][i+j] for j in range(1, window+1)):
                resistances.append((df['date'][i], df['high'][i]))
        
        return supports, resistances
    except Exception as e:
        logger.error(f"Error calculating support and resistance: {e}")
        return [], []

def calculate_fibonacci_retracement(df):
    """
    Calculate Fibonacci retracement levels
    
    Args:
        df (pandas.DataFrame): DataFrame with price data
    
    Returns:
        dict: Fibonacci retracement levels
    """
    try:
        # Get the lowest and highest price in the given period
        lowest_price = df['low'].min()
        highest_price = df['high'].max()
        price_diff = highest_price - lowest_price
        
        # Calculate Fibonacci retracement levels
        levels = {
            '0.0': highest_price,
            '0.236': highest_price - 0.236 * price_diff,
            '0.382': highest_price - 0.382 * price_diff,
            '0.5': highest_price - 0.5 * price_diff,
            '0.618': highest_price - 0.618 * price_diff,
            '0.786': highest_price - 0.786 * price_diff,
            '1.0': lowest_price
        }
        
        return levels
    except Exception as e:
        logger.error(f"Error calculating Fibonacci retracement: {e}")
        return {}

def identify_elliot_waves(df):
    """
    Identify Elliott Wave patterns in the price data
    Note: This is a simplified implementation
    
    Args:
        df (pandas.DataFrame): DataFrame with price data
    
    Returns:
        tuple: Lists of wave points and wave types
    """
    try:
        # This is a simplified implementation of Elliott Wave theory
        # A real implementation would be much more complex
        
        # Identify potential wave points using local minima and maxima
        waves = []
        wave_types = []
        
        # Get local extrema
        for i in range(5, len(df) - 5):
            # Local minimum
            if all(df['low'][i] <= df['low'][i-j] for j in range(1, 6)) and \
               all(df['low'][i] <= df['low'][i+j] for j in range(1, 6)):
                waves.append((df['date'][i], df['low'][i]))
                wave_types.append('min')
            
            # Local maximum
            if all(df['high'][i] >= df['high'][i-j] for j in range(1, 6)) and \
               all(df['high'][i] >= df['high'][i+j] for j in range(1, 6)):
                waves.append((df['date'][i], df['high'][i]))
                wave_types.append('max')
        
        return waves, wave_types
    except Exception as e:
        logger.error(f"Error identifying Elliott Waves: {e}")
        return [], []

def identify_abc_patterns(df):
    """
    Identify ABC correction patterns in the price data
    
    Args:
        df (pandas.DataFrame): DataFrame with price data
    
    Returns:
        list: List of potential ABC pattern points
    """
    try:
        # This is a simplified implementation to identify potential ABC correction patterns
        abc_patterns = []
        
        # Find local extrema
        extrema_dates = []
        extrema_prices = []
        extrema_types = []
        
        for i in range(5, len(df) - 5):
            # Local minimum
            if all(df['low'][i] <= df['low'][i-j] for j in range(1, 6)) and \
               all(df['low'][i] <= df['low'][i+j] for j in range(1, 6)):
                extrema_dates.append(df['date'][i])
                extrema_prices.append(df['low'][i])
                extrema_types.append('min')
            
            # Local maximum
            if all(df['high'][i] >= df['high'][i-j] for j in range(1, 6)) and \
               all(df['high'][i] >= df['high'][i+j] for j in range(1, 6)):
                extrema_dates.append(df['date'][i])
                extrema_prices.append(df['high'][i])
                extrema_types.append('max')
        
        # Look for potential ABC patterns
        # An ABC pattern typically consists of a down move (A), an up move (B), and a down move (C)
        for i in range(len(extrema_types) - 2):
            if extrema_types[i] == 'max' and extrema_types[i+1] == 'min' and extrema_types[i+2] == 'max':
                abc_patterns.append([
                    (extrema_dates[i], extrema_prices[i]),
                    (extrema_dates[i+1], extrema_prices[i+1]),
                    (extrema_dates[i+2], extrema_prices[i+2])
                ])
        
        return abc_patterns
    except Exception as e:
        logger.error(f"Error identifying ABC patterns: {e}")
        return []

def detect_signal_points(df, supports, resistances):
    """
    Detect buy and sell signal points based on price intersection with support and resistance lines
    
    Args:
        df (pandas.DataFrame): DataFrame with price data
        supports (list): List of support levels (date, price)
        resistances (list): List of resistance levels (date, price)
    
    Returns:
        tuple: Lists of buy and sell signal points
    """
    try:
        buy_signals = []
        sell_signals = []
        
        # Convert support and resistance points to more usable format
        support_prices = [(pd.to_datetime(date), price) for date, price in supports]
        resistance_prices = [(pd.to_datetime(date), price) for date, price in resistances]
        
        if not support_prices or not resistance_prices:
            return buy_signals, sell_signals
        
        # For each day's price data
        for i in range(1, len(df)):
            current_close = df['close'].iloc[i]
            previous_close = df['close'].iloc[i-1]
            current_date = df['date'].iloc[i]
            
            # Check for crossings of support lines (buy signals)
            for s_date, s_price in support_prices:
                # If price was below support and now crossed above it - buy signal
                if previous_close < s_price and current_close >= s_price:
                    buy_signals.append((current_date, current_close))
                    break
            
            # Check for crossings of resistance lines (sell signals)
            for r_date, r_price in resistance_prices:
                # If price was below resistance and now crossed above it - sell signal
                if previous_close < r_price and current_close >= r_price:
                    sell_signals.append((current_date, current_close))
                    break
                
        return buy_signals, sell_signals
    except Exception as e:
        logger.error(f"Error detecting signal points: {e}")
        return [], []

def create_chart(df, ticker, crypto_info, technical_indicators=True):
    """
    Create an interactive chart with technical indicators
    
    Args:
        df (pandas.DataFrame): DataFrame with price data
        ticker (str): Ticker symbol
        crypto_info (dict): Cryptocurrency information
        technical_indicators (bool): Whether to include technical indicators
    
    Returns:
        plotly.graph_objects.Figure: The chart figure
    """
    try:
        # Create a subplot with 2 rows
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.05, 
                           row_heights=[0.7, 0.3])
        
        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df['date'],
                open=df['open'], 
                high=df['high'],
                low=df['low'], 
                close=df['close'],
                name='Price'
            ),
            row=1, col=1
        )
        
        # Add volume bars
        fig.add_trace(
            go.Bar(
                x=df['date'],
                y=df['volume'],
                name='Volume',
                marker=dict(color='rgba(0, 0, 255, 0.5)')
            ),
            row=2, col=1
        )
        
        # Add technical indicators if requested
        if technical_indicators:
            try:
                # Add support and resistance levels
                supports, resistances = calculate_support_resistance(df)
                
                for date, price in supports:
                    fig.add_shape(
                        type="line",
                        x0=date, y0=price,
                        x1=df['date'].iloc[-1], y1=price,
                        line=dict(color="green", width=1, dash="dash"),
                        row=1, col=1
                    )
                
                for date, price in resistances:
                    fig.add_shape(
                        type="line",
                        x0=date, y0=price,
                        x1=df['date'].iloc[-1], y1=price,
                        line=dict(color="red", width=1, dash="dash"),
                        row=1, col=1
                    )
                
                # Add Fibonacci retracement levels
                fib_levels = calculate_fibonacci_retracement(df)
                for level, price in fib_levels.items():
                    fig.add_shape(
                        type="line",
                        x0=df['date'].iloc[0], y0=price,
                        x1=df['date'].iloc[-1], y1=price,
                        line=dict(color="purple", width=1, dash="dot"),
                        row=1, col=1
                    )
                    fig.add_annotation(
                        x=df['date'].iloc[0], y=price,
                        text=f"Fib {level}",
                        showarrow=False,
                        xanchor="left",
                        row=1, col=1
                    )
                
                # Add Elliott Wave patterns
                waves, wave_types = identify_elliot_waves(df)
                for i, ((date, price), wave_type) in enumerate(zip(waves, wave_types)):
                    fig.add_trace(
                        go.Scatter(
                            x=[date], y=[price],
                            mode='markers',
                            marker=dict(
                                symbol='circle',
                                size=8,
                                color='blue' if wave_type == 'min' else 'orange'
                            ),
                            name=f'Wave {i+1}'
                        ),
                        row=1, col=1
                    )
                
                # Add ABC correction patterns
                abc_patterns = identify_abc_patterns(df)
                for i, pattern in enumerate(abc_patterns):
                    a_date, a_price = pattern[0]
                    b_date, b_price = pattern[1]
                    c_date, c_price = pattern[2]
                    
                    fig.add_trace(
                        go.Scatter(
                            x=[a_date, b_date, c_date],
                            y=[a_price, b_price, c_price],
                            mode='lines+markers+text',
                            marker=dict(
                                symbol='circle',
                                size=10,
                                color='cyan'
                            ),
                            text=['A', 'B', 'C'],
                            textposition="top center",
                            name=f'ABC Pattern {i+1}'
                        ),
                        row=1, col=1
                    )
                
                # Detect and add buy/sell signals
                buy_signals, sell_signals = detect_signal_points(df, supports, resistances)
                
                # Add buy signals to chart
                if buy_signals:
                    buy_x = [date for date, _ in buy_signals]
                    buy_y = [price for _, price in buy_signals]
                    fig.add_trace(
                        go.Scatter(
                            x=buy_x,
                            y=buy_y,
                            mode='markers',
                            marker=dict(
                                symbol='triangle-up',
                                size=15,
                                color='green',
                                line=dict(width=2, color='darkgreen')
                            ),
                            name='Buy Signal'
                        ),
                        row=1, col=1
                    )
                
                # Add sell signals to chart
                if sell_signals:
                    sell_x = [date for date, _ in sell_signals]
                    sell_y = [price for _, price in sell_signals]
                    fig.add_trace(
                        go.Scatter(
                            x=sell_x,
                            y=sell_y,
                            mode='markers',
                            marker=dict(
                                symbol='triangle-down',
                                size=15,
                                color='red',
                                line=dict(width=2, color='darkred')
                            ),
                            name='Sell Signal'
                        ),
                        row=1, col=1
                    )
            except Exception as e:
                logger.error(f"Error adding technical indicators: {e}")
        
        # Update layout
        crypto_name = crypto_info.get('name', ticker)
        market_cap = crypto_info.get('market_cap', 'N/A')
        if market_cap and isinstance(market_cap, (int, float)):
            market_cap = f"${market_cap:,.0f}"
            
        circulating_supply = crypto_info.get('circulating_supply', 'N/A')
        if circulating_supply and isinstance(circulating_supply, (int, float)):
            circulating_supply = f"{circulating_supply:,.0f} coins"
        
        title = f"{crypto_name} ({ticker}) | Market Cap: {market_cap} | Supply: {circulating_supply}"
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            height=800,
            xaxis_rangeslider_visible=False
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error creating chart: {e}")
        # Return a simple error chart
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text=f"Error creating chart: {str(e)}",
            showarrow=False,
            font=dict(size=20)
        )
        return fig