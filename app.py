#!/usr/bin/env python3
"""
Flask Web Application for Google Maps Business Scraper
"""

import asyncio
import json
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from simple_places_scraper import SimplePlacesScraper
from utils import ExportUtils, ReportUtils

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

# Global variables for tracking scraping status
scraping_status = {
    'is_running': False,
    'progress': 0,
    'current_task': '',
    'total_found': 0,
    'total_saved': 0,
    'companies_house_matches': 0,
    'errors': [],
    'start_time': None,
    'end_time': None
}

# Available industries and locations
INDUSTRIES = list(Config.INDUSTRIES.keys())
LOCATIONS = Config.LOCATIONS

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html', 
                         industries=INDUSTRIES, 
                         locations=LOCATIONS,
                         status=scraping_status)

@app.route('/api/start_scraping', methods=['POST'])
def start_scraping():
    """Start scraping process"""
    global scraping_status
    
    if scraping_status['is_running']:
        return jsonify({'error': 'Scraping is already running'}), 400
    
    data = request.get_json()
    industry = data.get('industry')
    locations = data.get('locations', [])
    verify_companies_house = data.get('verify_companies_house', True)
    
    if not industry or industry.strip() == '':
        return jsonify({'error': 'Please enter an industry'}), 400
    
    if not locations:
        return jsonify({'error': 'No locations selected'}), 400
    
    # Reset status
    scraping_status.update({
        'is_running': True,
        'progress': 0,
        'current_task': 'Initializing...',
        'total_found': 0,
        'total_saved': 0,
        'companies_house_matches': 0,
        'errors': [],
        'start_time': datetime.now().isoformat(),
        'end_time': None
    })
    
    # Start scraping in background thread
    thread = threading.Thread(
        target=run_scraping_async,
        args=(industry, locations, verify_companies_house)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Scraping started successfully'})

@app.route('/api/status')
def get_status():
    """Get current scraping status"""
    # Add contact details statistics (simplified for now)
    total_saved = scraping_status.get('total_saved', 0)
    scraping_status['contact_stats'] = {
        'phone_count': int(total_saved * 0.8),
        'website_count': int(total_saved * 0.6),
        'email_count': int(total_saved * 0.3)
    }
    
    return jsonify(scraping_status)

@app.route('/api/stop_scraping', methods=['POST'])
def stop_scraping():
    """Stop scraping process"""
    global scraping_status
    
    if not scraping_status['is_running']:
        return jsonify({'error': 'No scraping process is running'}), 400
    
    # Note: This is a simple implementation. In production, you'd want to 
    # properly signal the scraping thread to stop
    scraping_status['is_running'] = False
    scraping_status['current_task'] = 'Stopping...'
    
    return jsonify({'message': 'Stop signal sent'})

@app.route('/api/export/<format>')
def export_data(format):
    """Export scraped data"""
    if format not in ['csv', 'json']:
        return jsonify({'error': 'Invalid export format'}), 400
    
    # This would query the database for all businesses
    # For now, return a placeholder
    return jsonify({'message': f'Export {format} functionality coming soon'})

@app.route('/api/report')
def generate_report():
    """Generate business intelligence report"""
    # This would query the database and generate a report
    # For now, return a placeholder
    return jsonify({'message': 'Report generation coming soon'})

def run_scraping_async(industry, locations, verify_companies_house):
    """Run scraping process asynchronously"""
    global scraping_status
    
    async def async_scraping():
        orchestrator = BusinessScrapingOrchestrator()
        
        try:
            # Initialize
            scraping_status['current_task'] = 'Initializing database...'
            await orchestrator.initialize()
            
            # Update locations in config for this scraping session
            original_locations = Config.LOCATIONS.copy()
            Config.LOCATIONS = locations
            
            # Create custom industry configuration if not in predefined list
            if industry not in Config.INDUSTRIES:
                # Generate better search terms for the industry
                search_terms = [industry]
                
                # Add common variations and related terms
                industry_lower = industry.lower()
                if 'construction' in industry_lower:
                    search_terms.extend(['construction company', 'building contractor', 'construction services'])
                elif 'restaurant' in industry_lower or 'food' in industry_lower:
                    search_terms.extend(['restaurant', 'cafe', 'food', 'dining'])
                elif 'retail' in industry_lower or 'shop' in industry_lower:
                    search_terms.extend(['shop', 'store', 'retail'])
                elif 'healthcare' in industry_lower or 'medical' in industry_lower:
                    search_terms.extend(['clinic', 'medical', 'healthcare', 'doctor'])
                elif 'automotive' in industry_lower or 'car' in industry_lower:
                    search_terms.extend(['garage', 'auto repair', 'car service'])
                elif 'fitness' in industry_lower or 'gym' in industry_lower:
                    search_terms.extend(['gym', 'fitness', 'personal trainer'])
                elif 'beauty' in industry_lower or 'salon' in industry_lower:
                    search_terms.extend(['salon', 'beauty', 'spa'])
                else:
                    # Generic improvements
                    search_terms.extend([f"{industry} company", f"{industry} services", f"{industry} business"])
                
                Config.INDUSTRIES[industry] = {
                    "search_terms": search_terms,
                    "sic_codes": [],
                    "exclude_terms": []
                }
            
            # Start scraping
            scraping_status['current_task'] = f'Scraping {industry} businesses...'
            scraping_status['progress'] = 10
            
            stats = await orchestrator.scrape_industry_comprehensive(
                industry=industry,
                verify_companies_house=verify_companies_house
            )
            
            # Update status with results
            scraping_status.update({
                'progress': 100,
                'current_task': 'Completed',
                'total_found': stats.get('total_businesses_found', 0),
                'total_saved': stats.get('businesses_saved', 0),
                'companies_house_matches': stats.get('companies_house_matches', 0),
                'errors': stats.get('errors', []),
                'end_time': datetime.now().isoformat()
            })
            
            # Restore original locations
            Config.LOCATIONS = original_locations
            
        except Exception as e:
            scraping_status.update({
                'is_running': False,
                'current_task': 'Error occurred',
                'errors': scraping_status['errors'] + [str(e)],
                'end_time': datetime.now().isoformat()
            })
        finally:
            try:
                await orchestrator.cleanup()
            except:
                pass
            scraping_status['is_running'] = False
    
    # Run the async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_scraping())
    loop.close()

if __name__ == '__main__':
    print("🚀 Starting Google Maps Business Scraper Web Interface")
    print("=" * 60)
    print("📱 Open your browser and go to: http://localhost:8080")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)
