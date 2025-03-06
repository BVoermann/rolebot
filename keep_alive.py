from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Creates and starts a Flask web server in a separate thread 
    to keep the bot running on Replit"""
    t = Thread(target=run)
    t.start() 