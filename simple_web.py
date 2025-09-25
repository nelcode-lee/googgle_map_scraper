#!/usr/bin/env python3
"""
Simple web server for testing
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
    webbrowser.open('http://localhost:8081')

def main():
    print("🌐 Starting Simple Web Server")
    print("=" * 40)
    print("📱 The web interface will open in your browser")
    print("🔗 URL: http://localhost:8081")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 40)
    
    # Open browser in background
    Timer(1, open_browser).start()
    
    # Import and run Flask app
    from app import app
    app.run(host='0.0.0.0', port=8081, debug=True, threaded=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
