#!/usr/bin/env python3
"""
Simple Flask Web Application using Google Places API
"""

import asyncio
import json
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_places_scraper import SimplePlacesScraper

app = Flask(__name__)
CORS(app, origins=['http://localhost:8080', 'http://127.0.0.1:8080'])

# Add security headers and cache control
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    # Prevent caching to ensure updates are loaded
    response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')
    response.headers.add('Pragma', 'no-cache')
    response.headers.add('Expires', '0')
    return response

# Global variables for scraping status
scraping_status = {
    'is_running': False,
    'progress': 0,
    'current_industry': '',
    'current_location': '',
    'total_found': 0,
    'total_saved': 0,
    'errors': [],
    'start_time': None,
    'end_time': None
}

# Initialize the simple places scraper
scraper = SimplePlacesScraper()

@app.route('/')
def index():
    """Main page"""
    industries = [
        'restaurants', 'retail', 'healthcare', 'professional_services',
        'automotive', 'beauty_wellness', 'fitness_sports', 'education',
        'technology', 'real_estate', 'entertainment', 'travel_tourism'
    ]
    
    locations = [
        'London, UK', 'Manchester, UK', 'Birmingham, UK', 'Leeds, UK',
        'Glasgow, UK', 'Liverpool, UK', 'Newcastle, UK', 'Sheffield, UK',
        'Bristol, UK', 'Nottingham, UK', 'Leicester, UK', 'Edinburgh, UK'
    ]
    
    radius_options = [
        {'value': 1, 'label': '1 mile'},
        {'value': 2, 'label': '2 miles'},
        {'value': 5, 'label': '5 miles'},
        {'value': 10, 'label': '10 miles'},
        {'value': 15, 'label': '15 miles'},
        {'value': 25, 'label': '25 miles'},
        {'value': 50, 'label': '50 miles'}
    ]
    
    return render_template('index.html', industries=industries, locations=locations, radius_options=radius_options)

@app.route('/api/status')
def get_status():
    """Get current scraping status"""
    return jsonify(scraping_status)

@app.route('/api/start_scraping', methods=['POST'])
def start_scraping():
    """Start the scraping process"""
    global scraping_status
    
    data = request.get_json()
    industry = data.get('industry', '').strip()
    locations = data.get('locations', [])
    radius_miles = data.get('radius', 5)  # Default to 5 miles
    
    if not industry or not locations:
        return jsonify({
            'success': False,
            'error': 'Industry and at least one location are required'
        }), 400
    
    if scraping_status['is_running']:
        return jsonify({
            'success': False,
            'error': 'Scraping is already in progress'
        }), 400
    
    # Start scraping in a separate thread
    def run_scraping():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Update status
            scraping_status['is_running'] = True
            scraping_status['progress'] = 10
            scraping_status['current_industry'] = industry
            scraping_status['current_location'] = ', '.join(locations)
            scraping_status['start_time'] = datetime.now().isoformat()
            scraping_status['errors'] = []
            
            # Run the scraping using Places API for each location
            total_found = 0
            total_saved = 0
            all_errors = []
            
            for i, location in enumerate(locations):
                try:
                    # Update progress
                    progress = 10 + (i * 80 // len(locations))
                    scraping_status['progress'] = progress
                    scraping_status['current_location'] = location
                    
                    result = loop.run_until_complete(
                        scraper.scrape_and_save(industry, location, radius_miles)
                    )
                    
                    total_found += result.get('found', 0)
                    total_saved += result.get('saved', 0)
                    all_errors.extend(result.get('errors', []))
                    
                except Exception as e:
                    all_errors.append(f"Error in {location}: {str(e)}")
            
            # Final result
            result = {
                'found': total_found,
                'saved': total_saved,
                'table_name': f"industry_{industry.lower().replace(' ', '_')}",
                'errors': all_errors
            }
            
            # Update final status
            scraping_status['progress'] = 100
            scraping_status['total_found'] = result.get('found', 0)
            scraping_status['total_saved'] = result.get('saved', 0)
            scraping_status['table_name'] = result.get('table_name', '')
            scraping_status['errors'] = result.get('errors', [])
            scraping_status['end_time'] = datetime.now().isoformat()
            scraping_status['is_running'] = False
            
        except Exception as e:
            scraping_status['errors'].append(str(e))
            scraping_status['is_running'] = False
            scraping_status['end_time'] = datetime.now().isoformat()
        finally:
            loop.close()
    
    # Start the scraping thread
    scraping_thread = threading.Thread(target=run_scraping)
    scraping_thread.daemon = True
    scraping_thread.start()
    
    return jsonify({
        'success': True,
        'message': f'Scraping started for {industry} in {", ".join(locations)} within {radius_miles} miles using Places API',
        'status': scraping_status
    })

@app.route('/api/stop_scraping', methods=['POST'])
def stop_scraping():
    """Stop the scraping process"""
    global scraping_status
    
    if not scraping_status['is_running']:
        return jsonify({
            'success': False,
            'error': 'No scraping in progress'
        }), 400
    
    scraping_status['is_running'] = False
    scraping_status['end_time'] = datetime.now().isoformat()
    
    return jsonify({
        'success': True,
        'message': 'Scraping stopped',
        'status': scraping_status
    })

if __name__ == '__main__':
    print("🚀 Starting Google Maps Business Scraper Web Interface (Places API)")
    print("=" * 70)
    print("📱 Open your browser and go to: http://localhost:8080")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)
