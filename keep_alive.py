from flask import Flask
from threading import Thread
import logging
import os
import time

# Configure basic logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("keep_alive")

# Create Flask app with minimal footprint
app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/')
def home():
    # Return a simple page with timestamp to confirm it's working
    return f"I'm alive! Timestamp: {time.time()}"

@app.route('/health')
def health():
    # Health check endpoint for monitoring
    memory_usage = os.popen('ps -o rss= -p ' + str(os.getpid())).read().strip()
    try:
        memory_usage_mb = round(int(memory_usage) / 1024, 2)
        return {
            "status": "healthy",
            "memory_usage_mb": memory_usage_mb,
            "timestamp": time.time()
        }
    except:
        return {
            "status": "healthy",
            "timestamp": time.time()
        }

def run():
    try:
        # Run with minimal resource usage
        logger.info("Starting keep_alive server...")
        app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Error in keep_alive server: {e}")

def keep_alive():
    """
    Creates and starts a Flask web server in a separate thread 
    to keep the bot running on Replit.
    
    This implementation is designed to use minimal resources.
    """
    # Create daemon thread so it doesn't block bot shutdown
    t = Thread(target=run, daemon=True)
    t.start()
    logger.info("Keep alive thread started")
    return t 