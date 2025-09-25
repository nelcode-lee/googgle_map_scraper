#!/usr/bin/env python3
"""
Google Places API Scraper - Alternative to web scraping
This uses Google's official Places API which is much more reliable
"""

import asyncio
import aiohttp
import json
import time
from typing import List, Dict, Any, Optional
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()

class GooglePlacesScraper:
    """Scraper using Google Places API instead of web scraping"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY not found in environment variables")
        
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_places(self, query: str, location: str, radius: int = 5000) -> List[Dict[str, Any]]:
        """Search for places using Google Places API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        # First, get coordinates for the location
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        geocode_params = {
            'address': location,
            'key': self.api_key
        }
        
        try:
            async with self.session.get(geocode_url, params=geocode_params) as response:
                geocode_data = await response.json()
                
            if geocode_data['status'] != 'OK':
                logger.error(f"Geocoding failed: {geocode_data.get('error_message', 'Unknown error')}")
                return []
                
            location_coords = geocode_data['results'][0]['geometry']['location']
            lat = location_coords['lat']
            lng = location_coords['lng']
            
            logger.info(f"Searching for '{query}' near {location} ({lat}, {lng})")
            
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return []
        
        # Search for places
        places_url = f"{self.base_url}/textsearch/json"
        places_params = {
            'query': f"{query} in {location}",
            'location': f"{lat},{lng}",
            'radius': radius,
            'key': self.api_key
        }
        
        all_places = []
        next_page_token = None
        
        try:
            # Get first page of results
            async with self.session.get(places_url, params=places_params) as response:
                places_data = await response.json()
                
            if places_data['status'] != 'OK':
                logger.error(f"Places search failed: {places_data.get('error_message', 'Unknown error')}")
                return []
                
            all_places.extend(places_data['results'])
            next_page_token = places_data.get('next_page_token')
            
            # Get additional pages (up to 3 pages = 60 results)
            for page in range(2):
                if not next_page_token:
                    break
                    
                # Wait for next page token to become valid
                await asyncio.sleep(2)
                
                page_params = places_params.copy()
                page_params['pagetoken'] = next_page_token
                
                async with self.session.get(places_url, params=page_params) as response:
                    page_data = await response.json()
                    
                if page_data['status'] == 'OK':
                    all_places.extend(page_data['results'])
                    next_page_token = page_data.get('next_page_token')
                else:
                    break
                    
            logger.info(f"Found {len(all_places)} places")
            
        except Exception as e:
            logger.error(f"Places search error: {e}")
            return []
        
        # Get detailed information for each place
        businesses = []
        for place in all_places:
            business = await self._get_place_details(place['place_id'])
            if business:
                businesses.append(business)
                
        return businesses
    
    async def _get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific place"""
        details_url = f"{self.base_url}/details/json"
        details_params = {
            'place_id': place_id,
            'fields': 'name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,opening_hours,types,geometry',
            'key': self.api_key
        }
        
        try:
            async with self.session.get(details_url, params=details_params) as response:
                details_data = await response.json()
                
            if details_data['status'] != 'OK':
                return None
                
            result = details_data['result']
            
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
                'types': result.get('types', []),
                'opening_hours': opening_hours_str,
                'geometry': result.get('geometry', {})
            }
            
            # Extract email if available in website
            business['email'] = self._extract_email_from_website(business['website'])
            
            return business
            
        except Exception as e:
            logger.warning(f"Error getting details for place {place_id}: {e}")
            return None
    
    def _extract_email_from_website(self, website: str) -> str:
        """Extract email from website if possible"""
        if not website:
            return ''
        
        # This is a simple approach - in practice, you'd need to scrape the website
        # For now, we'll return empty string
        return ''
    
    async def search_industry(self, industry: str, locations: List[str]) -> List[Dict[str, Any]]:
        """Search for businesses in a specific industry across multiple locations"""
        all_businesses = []
        
        for location in locations:
            logger.info(f"Searching for {industry} in {location}")
            
            # Create search queries for the industry
            search_queries = self._generate_search_queries(industry)
            
            for query in search_queries:
                try:
                    businesses = await self.search_places(query, location)
                    
                    # Add metadata
                    for business in businesses:
                        business['industry'] = industry
                        business['search_term'] = query
                        business['search_location'] = location
                        business['google_place_id'] = business.get('place_id')
                    
                    all_businesses.extend(businesses)
                    logger.info(f"Found {len(businesses)} businesses for '{query}' in {location}")
                    
                    # Rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error searching {query} in {location}: {e}")
                    continue
        
        return all_businesses
    
    def _generate_search_queries(self, industry: str) -> List[str]:
        """Generate multiple search queries for an industry"""
        industry_lower = industry.lower()
        
        # Base queries
        queries = [industry_lower]
        
        # Add variations
        if 'restaurant' in industry_lower or 'food' in industry_lower:
            queries.extend(['restaurants', 'cafes', 'coffee shops', 'food places'])
        elif 'retail' in industry_lower or 'shop' in industry_lower:
            queries.extend(['shops', 'stores', 'retail stores', 'shopping'])
        elif 'healthcare' in industry_lower or 'medical' in industry_lower:
            queries.extend(['doctors', 'clinics', 'hospitals', 'medical centers'])
        elif 'professional' in industry_lower or 'services' in industry_lower:
            queries.extend(['professional services', 'consultants', 'advisors'])
        
        return queries[:3]  # Limit to 3 queries per industry


async def test_places_scraper():
    """Test the Places API scraper"""
    try:
        async with GooglePlacesScraper() as scraper:
            # Test with a simple search
            businesses = await scraper.search_places("cafes", "Manchester")
            
            print(f"\n🎉 Found {len(businesses)} businesses using Places API!")
            print("=" * 60)
            
            for i, business in enumerate(businesses[:5], 1):
                print(f"\n{i}. {business['name']}")
                print(f"   📍 {business['address']}")
                if business['phone']:
                    print(f"   📞 {business['phone']}")
                if business['website']:
                    print(f"   🌐 {business['website']}")
                if business['rating']:
                    print(f"   ⭐ {business['rating']}/5 ({business['user_ratings_total']} reviews)")
                print(f"   🆔 {business['place_id']}")
            
            if len(businesses) > 5:
                print(f"\n... and {len(businesses) - 5} more businesses")
                
    except Exception as e:
        print(f"❌ Error testing Places API scraper: {e}")


if __name__ == "__main__":
    asyncio.run(test_places_scraper())
