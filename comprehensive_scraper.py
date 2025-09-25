#!/usr/bin/env python3
"""
Comprehensive scraper combining multiple methods for maximum coverage
"""

import asyncio
import os
from typing import List, Dict, Any
from loguru import logger
from enhanced_scraper import EnhancedBusinessScraper
from web_scraper import WebMapsScraper
from database import DatabaseManager

class ComprehensiveScraper:
    """Comprehensive scraper using all available methods"""
    
    def __init__(self):
        self.db = DatabaseManager()
        
    async def scrape_and_save_comprehensive(self, industry: str, location: str, radius_miles: int = 10) -> Dict[str, Any]:
        """Comprehensive scraping using all methods"""
        all_businesses = []
        method_results = {}
        
        try:
            # Connect to database
            await self.db.connect()
            
            # Create industry-specific table
            table_name = await self.db.create_industry_table(industry)
            logger.info(f"Using industry table: {table_name}")
            
            # Method 1: Enhanced Places API
            logger.info("🚀 Method 1: Enhanced Places API")
            try:
                async with EnhancedBusinessScraper() as api_scraper:
                    api_businesses = await api_scraper.scrape_comprehensive(industry, location, radius_miles)
                method_results['api'] = len(api_businesses)
                all_businesses.extend(api_businesses)
                logger.info(f"API method found {len(api_businesses)} businesses")
            except Exception as e:
                logger.error(f"API method failed: {e}")
                method_results['api'] = 0
            
            # Method 2: Web Scraping
            logger.info("🚀 Method 2: Web Scraping")
            try:
                web_scraper = WebMapsScraper()
                web_businesses = web_scraper.search_businesses_web(industry, location, 100)
                web_scraper.close()
                method_results['web'] = len(web_businesses)
                all_businesses.extend(web_businesses)
                logger.info(f"Web method found {len(web_businesses)} businesses")
            except Exception as e:
                logger.error(f"Web method failed: {e}")
                method_results['web'] = 0
            
            # Method 3: Direct search for known businesses
            logger.info("🚀 Method 3: Direct Known Business Search")
            try:
                known_businesses = await self._search_known_businesses(industry, location)
                method_results['known'] = len(known_businesses)
                all_businesses.extend(known_businesses)
                logger.info(f"Known business search found {len(known_businesses)} businesses")
            except Exception as e:
                logger.error(f"Known business search failed: {e}")
                method_results['known'] = 0
            
            # Remove duplicates
            unique_businesses = self._remove_duplicates(all_businesses)
            logger.info(f"Total unique businesses found: {len(unique_businesses)}")
            
            # Save businesses to database
            saved_count = 0
            for business in unique_businesses:
                try:
                    # Clean the business data
                    import json
                    clean_business = {
                        'name': business.get('name', ''),
                        'address': business.get('address', ''),
                        'phone': business.get('phone', ''),
                        'website': business.get('website', ''),
                        'email': business.get('email', ''),
                        'google_rating': business.get('rating'),
                        'google_place_id': business.get('place_id', ''),
                        'industry': industry,
                        'search_term': industry,
                        'search_location': location,
                        'opening_hours': json.dumps({}),
                        'place_id': business.get('place_id', ''),
                        'types': json.dumps(business.get('types', [])),
                        'geometry': json.dumps(business.get('geometry', {}))
                    }
                    
                    # Only save if we have a name
                    if clean_business['name']:
                        # Save to main businesses table
                        await self.db.insert_business(clean_business)
                        # Save to industry-specific table
                        await self.db.insert_business_to_industry_table(clean_business, table_name)
                        saved_count += 1
                        logger.info(f"Saved: {clean_business['name']} to {table_name}")
                    
                except Exception as e:
                    logger.warning(f"Error saving business {business.get('name', 'Unknown')}: {e}")
                    continue
            
            return {
                "found": len(unique_businesses),
                "saved": saved_count,
                "table_name": table_name,
                "method_results": method_results,
                "errors": []
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive scrape_and_save: {e}")
            return {
                "found": 0,
                "saved": 0,
                "table_name": "",
                "method_results": method_results,
                "errors": [str(e)]
            }
    
    async def _search_known_businesses(self, industry: str, location: str) -> List[Dict[str, Any]]:
        """Search for known businesses that might not appear in general searches"""
        known_businesses = []
        
        # Known CPCS training centers
        if 'cpcs' in industry.lower() or 'cscs' in industry.lower():
            known_centers = [
                "Operator Skills Hub",
                "CITB",
                "Construction Industry Training Board",
                "NPORS",
                "IPAF",
                "Lantra",
                "CPCS Training",
                "CSCS Training",
                "Construction Training",
                "Plant Training"
            ]
            
            # Try to find these specific businesses
            for center_name in known_centers:
                try:
                    # Use Places API to search for specific business
                    async with EnhancedBusinessScraper() as scraper:
                        businesses = await scraper._google_places_text_search(f"{center_name} {location}", location, 50)
                        known_businesses.extend(businesses)
                except Exception as e:
                    logger.debug(f"Error searching for {center_name}: {e}")
                    continue
        
        return known_businesses
    
    def _remove_duplicates(self, businesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate businesses based on name and address similarity"""
        unique_businesses = []
        seen_names = set()
        
        for business in businesses:
            name = business.get('name', '').lower().strip()
            address = business.get('address', '').lower().strip()
            
            # Create a signature for duplicate detection
            signature = f"{name}_{address}"
            
            if signature not in seen_names and name:
                seen_names.add(signature)
                unique_businesses.append(business)
        
        return unique_businesses

async def test_comprehensive_scraper():
    """Test the comprehensive scraper"""
    try:
        scraper = ComprehensiveScraper()
        
        # Test with CPCS training in Manchester
        result = await scraper.scrape_and_save_comprehensive("CPCS training", "Manchester, UK", 25)
        
        print(f"\n🎉 Comprehensive Scraper Results:")
        print(f"Total businesses found: {result['found']}")
        print(f"Businesses saved: {result['saved']}")
        print(f"Industry table: {result['table_name']}")
        print(f"Method results: {result['method_results']}")
        if result['errors']:
            print(f"Errors: {result['errors']}")
        
    except Exception as e:
        print(f"❌ Error testing comprehensive scraper: {e}")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_scraper())