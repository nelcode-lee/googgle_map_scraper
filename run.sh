#!/bin/bash

# Google Maps Business Scraper Quick Start Script

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup.py first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Please edit .env file with your API keys before running the scraper."
        exit 1
    else
        echo "Error: .env.example file not found."
        exit 1
    fi
fi

# Check for web interface command
if [ "$1" = "web" ]; then
    echo "🌐 Starting web interface..."
    python start_web_fixed.py
elif [ "$1" = "test" ]; then
    echo "🧪 Running API tests..."
    python test_api.py
else
    # Run the main script with provided arguments
    python main.py "$@"
fi
