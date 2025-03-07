import time
import logging
import requests
import os
import sys
import re
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
    """Get the current Replit URL from environment variables or webserver log"""
    # Method 1: Try to get from a webserver log
    try:
        with open('webserver.log', 'r') as f:
            for line in f:
                if 'Running on http://' in line and 'Running on http://127.0.0.1' not in line and 'Running on http://0.0.0.0' not in line:
                    # Extract the URL from the log
                    match = re.search(r'Running on (http://[^ ]+)', line)
                    if match:
                        url = match.group(1)
                        logger.info(f"Found URL in logs: {url}")
                        return url
    except:
        pass
    
    # Method 2: Check directly in Flask's werkzeug logs
    try:
        for line in sys.stdout.buffer:  # Try to read from stdout buffer
            line_str = line.decode('utf-8', errors='ignore')
            if 'Running on http://' in line_str and 'Running on http://127.0.0.1' not in line_str and 'Running on http://0.0.0.0' not in line_str:
                # Extract the URL from the log
                match = re.search(r'Running on (http://[^ ]+)', line_str)
                if match:
                    url = match.group(1)
                    logger.info(f"Found URL in stdout: {url}")
                    return url
    except:
        pass
    
    # Method 3: Use a hardcoded URL based on Replit's new format
    # Extract username from environment
    username = os.environ.get('REPL_OWNER', 'unknown')
    slug = os.environ.get('REPL_SLUG', 'unknown')
    
    if username != 'unknown' and slug != 'unknown':
        url = f"https://{slug}.{username}.repl.co"
        logger.info(f"Using constructed URL: {url}")
        return url
    
    # Method 4: Try Replit's newer URL format with ID
    replit_id = os.environ.get('REPL_ID', '')
    if replit_id:
        # This follows the pattern seen in your error message
        url = f"https://{slug}.{username}.repl.co"
        logger.info(f"Using ID-based URL: {url}")
        return url
    
    # Fallback to localhost if nothing else works
    logger.warning("Couldn't determine Replit URL, using localhost:8080")
    return "http://localhost:8080"

def ping_self():
    """Ping the Replit instance to keep it alive"""
    url = get_replit_url()
    try:
        response = requests.get(f"{url}", timeout=10)  # Try root URL first
        logger.info(f"Self-ping successful to root URL: {response.status_code}")
        
        # Also try health endpoint
        try:
            health_response = requests.get(f"{url}/health", timeout=5)
            logger.info(f"Health endpoint ping: {health_response.status_code}")
        except:
            logger.info("Health endpoint not responsive, but root URL is working")
            
        return True
    except Exception as e:
        logger.error(f"Self-ping failed: {e}")
        # Try with HTTP if HTTPS failed
        if url.startswith("https://"):
            try:
                http_url = url.replace("https://", "http://")
                response = requests.get(http_url, timeout=10)
                logger.info(f"Self-ping successful with HTTP: {response.status_code}")
                return True
            except Exception as e2:
                logger.error(f"HTTP fallback also failed: {e2}")
        return False

def write_url_to_file():
    """Writes the URL to a file for UptimeRobot setup"""
    url = get_replit_url()
    try:
        with open('replit_url.txt', 'w') as f:
            f.write(f"Your Replit URL: {url}\n")
            f.write(f"UptimeRobot URL: {url}/health\n")
            f.write("\nCopy these URLs for setting up UptimeRobot.")
        logger.info(f"Wrote URL information to replit_url.txt")
    except Exception as e:
        logger.error(f"Failed to write URL to file: {e}")

def start_self_pinger(interval_seconds=240):  # 4 minutes
    """Start a background thread that pings the Replit instance periodically"""
    # First, write the URL to a file for reference
    write_url_to_file()
    
    def pinger_thread():
        while True:
            ping_self()
            time.sleep(interval_seconds)
    
    thread = Thread(target=pinger_thread, daemon=True)
    thread.start()
    logger.info(f"Self-pinger started with interval of {interval_seconds} seconds")
    return thread

if __name__ == "__main__":
    # If run directly, just ping once and print the URL
    url = get_replit_url()
    print(f"Detected Replit URL: {url}")
    print(f"Health endpoint: {url}/health")
    ping_self() 