import time
import logging
import requests
import os
import sys
from threading import Thread

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("replit_ping")

def get_replit_url():
    """Get the current Replit URL from environment variables"""
    # Try different environment variable names that Replit might use
    for var in ['REPL_SLUG', 'REPL_ID', 'REPLIT_URL']:
        if var in os.environ:
            username = os.environ.get('REPL_OWNER', 'user')
            slug = os.environ.get(var)
            return f"https://{slug}.{username}.repl.co"
    
    # If we can't determine the URL, use a default local URL
    return "http://localhost:8080"

def ping_self():
    """Ping the Replit instance to keep it alive"""
    url = get_replit_url()
    try:
        response = requests.get(f"{url}/health", timeout=10)
        logger.info(f"Self-ping successful: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Self-ping failed: {e}")
        return False

def start_self_pinger(interval_seconds=240):  # 4 minutes
    """Start a background thread that pings the Replit instance periodically"""
    def pinger_thread():
        while True:
            ping_self()
            time.sleep(interval_seconds)
    
    thread = Thread(target=pinger_thread, daemon=True)
    thread.start()
    logger.info(f"Self-pinger started with interval of {interval_seconds} seconds")
    return thread

if __name__ == "__main__":
    # If run directly, just ping once
    ping_self() 