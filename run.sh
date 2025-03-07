#!/bin/bash
# This script keeps the bot running even if it crashes

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting Discord Role Bot with auto-restart..."

while true; do
  echo "Starting bot at $(date)"
  python rolebot.py
  
  EXIT_CODE=$?
  
  if [ $EXIT_CODE -eq 0 ]; then
    echo "Bot exited normally. Exiting loop."
    break
  else
    echo "Bot crashed with exit code $EXIT_CODE"
    echo "Restarting in 10 seconds..."
    sleep 10
  fi
done 