#!/bin/bash
# Script for running the Discord bot on Render.com

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting Discord Role Bot..."
python rolebot.py 