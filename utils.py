import logging
import time
import threading
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataRefresher:
    """
    A class to handle periodic data refreshing
    """
    def __init__(self, refresh_interval=120):
        """
        Initialize the DataRefresher
        
        Args:
            refresh_interval (int): Refresh interval in seconds
        """
        self.refresh_interval = refresh_interval
        self.last_refresh_time = None
        self.refresh_callback = None
        self.is_running = False
        self.thread = None
        
    def start(self, callback):
        """
        Start the refresh timer
        
        Args:
            callback (callable): Function to call on refresh
        """
        self.refresh_callback = callback
        self.is_running = True
        self.last_refresh_time = datetime.now()
        
        # Start the refresh thread
        self.thread = threading.Thread(target=self._refresh_loop)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info(f"Data refresher started with interval: {self.refresh_interval} seconds")
        
    def _refresh_loop(self):
        """
        The main refresh loop
        """
        while self.is_running:
            time.sleep(1)  # Check every second
            
            current_time = datetime.now()
            elapsed = (current_time - self.last_refresh_time).total_seconds()
            
            if elapsed >= self.refresh_interval:
                try:
                    if self.refresh_callback:
                        self.refresh_callback()
                    self.last_refresh_time = current_time
                    logger.info(f"Data refreshed at {current_time}")
                except Exception as e:
                    logger.error(f"Error during data refresh: {e}")
    
    def stop(self):
        """
        Stop the refresh timer
        """
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)
        logger.info("Data refresher stopped")

def format_large_number(num):
    """
    Format large numbers in a readable way
    
    Args:
        num: The number to format
        
    Returns:
        str: Formatted number
    """
    if num is None:
        return "N/A"
    
    try:
        num = float(num)
        if num >= 1_000_000_000:
            return f"${num / 1_000_000_000:.2f}B"
        elif num >= 1_000_000:
            return f"${num / 1_000_000:.2f}M"
        elif num >= 1_000:
            return f"${num / 1_000:.2f}K"
        else:
            return f"${num:.2f}"
    except (ValueError, TypeError):
        return str(num)

def get_color_from_change(change):
    """
    Get color based on price change
    
    Args:
        change (float): Price change percentage
        
    Returns:
        str: Color code
    """
    if change is None:
        return "gray"
    
    try:
        change = float(change)
        if change > 0:
            return "green"
        elif change < 0:
            return "red"
        else:
            return "gray"
    except (ValueError, TypeError):
        return "gray"