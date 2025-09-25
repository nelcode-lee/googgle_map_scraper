#!/usr/bin/env python3
"""
Start the web interface for Google Maps Business Scraper
"""

import os
import sys
import webbrowser
import time
from threading import Timer

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:8080')

def main():
    print("🌐 Starting Google Maps Business Scraper Web Interface")
    print("=" * 60)
    print("📱 The web interface will open in your browser")
    print("🔗 URL: http://localhost:8080")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Open browser in background
    Timer(1, open_browser).start()
    
    # Start Flask app
    from app import app
    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
