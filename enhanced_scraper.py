#!/usr/bin/env python3
"""
Enhanced multi-source scraper for comprehensive business data collection
"""

import asyncio
import aiohttp
import json
import re
from typing import List, Dict, Any, Optional
from loguru import logger
import os
from database import DatabaseManager

class EnhancedBusinessScraper:
    """Enhanced scraper using multiple methods and sources"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_comprehensive(self, industry: str, location: str, radius_miles: int = 10) -> List[Dict[str, Any]]:
        """Comprehensive scraping using multiple methods"""
        all_businesses = []
        
        # Method 1: Google Places API - Nearby Search
        logger.info("🔍 Method 1: Google Places API - Nearby Search")
        nearby_businesses = await self._google_places_nearby(industry, location, radius_miles)
        all_businesses.extend(nearby_businesses)
        logger.info(f"Found {len(nearby_businesses)} businesses via Nearby Search")
        
        # Method 2: Google Places API - Text Search
        logger.info("🔍 Method 2: Google Places API - Text Search")
        text_businesses = await self._google_places_text_search(industry, location, radius_miles)
        all_businesses.extend(text_businesses)
        logger.info(f"Found {len(text_businesses)} businesses via Text Search")
        
        # Method 3: Google Places API - Autocomplete
        logger.info("🔍 Method 3: Google Places API - Autocomplete")
        autocomplete_businesses = await self._google_places_autocomplete(industry, location)
        all_businesses.extend(autocomplete_businesses)
        logger.info(f"Found {len(autocomplete_businesses)} businesses via Autocomplete")
        
        # Method 4: Multiple search terms
        logger.info("🔍 Method 4: Multiple search terms")
        multi_term_businesses = await self._multi_term_search(industry, location, radius_miles)
        all_businesses.extend(multi_term_businesses)
        logger.info(f"Found {len(multi_term_businesses)} businesses via Multi-term Search")
        
        # Remove duplicates
        unique_businesses = self._remove_duplicates(all_businesses)
        logger.info(f"Total unique businesses found: {len(unique_businesses)}")
        
        return unique_businesses
    
    async def _google_places_nearby(self, industry: str, location: str, radius_miles: int) -> List[Dict[str, Any]]:
        """Google Places API - Nearby Search"""
        coords = await self._get_coordinates(location)
        if not coords:
            return []
            
        radius_meters = radius_miles * 1609.34
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            'location': f"{coords['lat']},{coords['lng']}",
            'radius': radius_meters,
            'keyword': industry,
            'key': self.google_api_key
        }
        
        businesses = []
        next_page_token = None
        
        while True:
            try:
                async with self.session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if data['status'] == 'OK':
                        businesses.extend(data.get('results', []))
                        next_page_token = data.get('next_page_token')
                        if next_page_token:
                            params['pagetoken'] = next_page_token
                            await asyncio.sleep(2)  # Required delay for pagination
                        else:
                            break
                    else:
                        break
            except Exception as e:
                logger.error(f"Error in nearby search: {e}")
                break
                
        return await self._get_place_details_batch(businesses)
    
    async def _google_places_text_search(self, industry: str, location: str, radius_miles: int) -> List[Dict[str, Any]]:
        """Google Places API - Text Search"""
        coords = await self._get_coordinates(location)
        if not coords:
            return []
            
        radius_meters = radius_miles * 1609.34
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': f"{industry} in {location}",
            'location': f"{coords['lat']},{coords['lng']}",
            'radius': radius_meters,
            'key': self.google_api_key
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                if data['status'] == 'OK':
                    return await self._get_place_details_batch(data.get('results', []))
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            
        return []
    
    async def _google_places_autocomplete(self, industry: str, location: str) -> List[Dict[str, Any]]:
        """Google Places API - Autocomplete"""
        coords = await self._get_coordinates(location)
        if not coords:
            return []
            
        url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
        params = {
            'input': f"{industry} {location}",
            'location': f"{coords['lat']},{coords['lng']}",
            'radius': 50000,  # 50km radius
            'key': self.google_api_key
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                if data['status'] == 'OK':
                    # Get place details for autocomplete results
                    place_ids = [prediction['place_id'] for prediction in data.get('predictions', [])]
                    return await self._get_place_details_by_ids(place_ids)
        except Exception as e:
            logger.error(f"Error in autocomplete: {e}")
            
        return []
    
    async def _multi_term_search(self, industry: str, location: str, radius_miles: int) -> List[Dict[str, Any]]:
        """Search using multiple related terms"""
        # Generate multiple search terms based on industry
        search_terms = self._generate_search_terms(industry)
        all_businesses = []
        
        for term in search_terms:
            try:
                # Text search for each term
                coords = await self._get_coordinates(location)
                if not coords:
                    continue
                    
                radius_meters = radius_miles * 1609.34
                url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
                params = {
                    'query': f"{term} in {location}",
                    'location': f"{coords['lat']},{coords['lng']}",
                    'radius': radius_meters,
                    'key': self.google_api_key
                }
                
                async with self.session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if data['status'] == 'OK':
                        businesses = await self._get_place_details_batch(data.get('results', []))
                        all_businesses.extend(businesses)
                        
            except Exception as e:
                logger.error(f"Error in multi-term search for '{term}': {e}")
                continue
                
        return all_businesses
    
    def _generate_search_terms(self, industry: str) -> List[str]:
        """Generate multiple search terms for comprehensive coverage"""
        industry_lower = industry.lower()
        
        if 'cpcs' in industry_lower or 'cscs' in industry_lower:
            return [
                'CPCS training',
                'CSCS training',
                'construction training',
                'plant training',
                'operator training',
                'construction skills',
                'plant operator training',
                'construction certification',
                'plant certification',
                'construction courses',
                'plant courses',
                'construction education',
                'plant education',
                'construction qualifications',
                'plant qualifications'
            ]
        elif 'restaurant' in industry_lower or 'food' in industry_lower:
            return [
                'restaurant',
                'cafe',
                'diner',
                'eatery',
                'food',
                'dining',
                'bistro',
                'brasserie',
                'gastropub',
                'takeaway',
                'fast food',
                'fine dining'
            ]
        elif 'technology' in industry_lower or 'tech' in industry_lower:
            return [
                'technology',
                'tech',
                'IT',
                'software',
                'digital',
                'computer',
                'tech company',
                'software company',
                'IT services',
                'tech services',
                'digital services',
                'computer services'
            ]
        else:
            # Generic terms
            return [
                industry,
                f"{industry} company",
                f"{industry} services",
                f"{industry} business",
                f"{industry} center",
                f"{industry} centre"
            ]
    
    async def _get_coordinates(self, location: str) -> Optional[Dict[str, float]]:
        """Get coordinates for a location"""
        if not self.google_api_key:
            logger.error("Google API key not found")
            return None
            
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': location,
            'key': self.google_api_key
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                if data['status'] == 'OK' and data['results']:
                    location_data = data['results'][0]['geometry']['location']
                    return {'lat': location_data['lat'], 'lng': location_data['lng']}
                else:
                    logger.error(f"Geocoding failed: {data.get('status')} - {data.get('error_message', '')}")
        except Exception as e:
            logger.error(f"Error getting coordinates: {e}")
            
        return None
    
    async def _get_place_details_batch(self, places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get detailed information for a batch of places"""
        businesses = []
        
        for place in places:
            details = await self._get_place_details(place['place_id'])
            if details:
                businesses.append(details)
                
        return businesses
    
    async def _get_place_details_by_ids(self, place_ids: List[str]) -> List[Dict[str, Any]]:
        """Get place details by place IDs"""
        businesses = []
        
        for place_id in place_ids:
            details = await self._get_place_details(place_id)
            if details:
                businesses.append(details)
                
        return businesses
    
    async def _get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific place"""
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            'place_id': place_id,
            'fields': 'name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,place_id,types,opening_hours,geometry,email',
            'key': self.google_api_key
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                if data['status'] == 'OK':
                    result = data['result']
                    
                    # Extract business information
                    opening_hours = result.get('opening_hours', {})
                    opening_hours_str = ''
                    if opening_hours:
                        if 'weekday_text' in opening_hours:
                            opening_hours_str = '; '.join(opening_hours['weekday_text'])
                        elif 'raw' in opening_hours:
                            opening_hours_str = str(opening_hours['raw'])
                    
                    business = {
                        'name': result.get('name', ''),
                        'address': result.get('formatted_address', ''),
                        'phone': result.get('formatted_phone_number', ''),
                        'website': result.get('website', ''),
                        'rating': result.get('rating'),
                        'user_ratings_total': result.get('user_ratings_total', 0),
                        'place_id': place_id,
                        'types': json.dumps(result.get('types', [])),
                        'opening_hours': opening_hours_str,
                        'geometry': json.dumps(result.get('geometry', {}))
                    }
                    
                    # Extract email if available
                    business['email'] = self._extract_email_from_website(business['website'])
                    
                    return business
        except Exception as e:
            logger.error(f"Error getting place details for {place_id}: {e}")
            
        return None
    
    def _extract_email_from_website(self, website_url: str) -> str:
        """Extract email from website URL"""
        if not website_url:
            return ''
        match = re.search(r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', website_url)
        if match:
            return match.group(1)
        return ''
    
    def _remove_duplicates(self, businesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate businesses based on place_id"""
        seen = set()
        unique_businesses = []
        
        for business in businesses:
            place_id = business.get('place_id', '')
            if place_id and place_id not in seen:
                seen.add(place_id)
                unique_businesses.append(business)
                
        return unique_businesses

async def test_enhanced_scraper():
    """Test the enhanced scraper"""
    try:
        async with EnhancedBusinessScraper() as scraper:
            businesses = await scraper.scrape_comprehensive("CPCS training", "Manchester, UK", 25)
            
            print(f"\n🎉 Enhanced Scraper Results:")
            print(f"Found {len(businesses)} businesses")
            print("=" * 60)
            
            for i, business in enumerate(businesses[:10]):  # Show first 10
                print(f"{i+1}. {business.get('name')}")
                print(f"   📍 {business.get('address')}")
                if business.get('website'):
                    print(f"   🌐 {business.get('website')}")
                if business.get('phone'):
                    print(f"   📞 {business.get('phone')}")
                print(f"   🆔 {business.get('place_id')}")
                print("")
                
    except Exception as e:
        print(f"❌ Error testing enhanced scraper: {e}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_scraper())
