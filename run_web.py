#!/usr/bin/env python3
"""
Simple script to run the web interface
"""

import sys
import os
import webbrowser
import time
from threading import Timer

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def open_browser():
    """Open browser after server starts"""
    time.sleep(2)
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
    
    # Import and run Flask app
    from app import app
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
