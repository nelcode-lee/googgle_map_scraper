#!/usr/bin/env python3
"""
Enhanced simple scraper using comprehensive multi-method approach
"""

import asyncio
import os
from typing import List, Dict, Any
from loguru import logger
from enhanced_scraper import EnhancedBusinessScraper
from database import DatabaseManager

class EnhancedSimpleScraper:
    """Enhanced scraper using multiple Google Places API methods"""
    
    def __init__(self):
        self.db = DatabaseManager()
        
    async def scrape_and_save(self, industry: str, location: str, radius_miles: int = 10) -> Dict[str, Any]:
        """Scrape businesses using comprehensive methods and save to database"""
        try:
            # Connect to database
            await self.db.connect()
            
            # Create industry-specific table
            table_name = await self.db.create_industry_table(industry)
            logger.info(f"Using industry table: {table_name}")
            
            # Use enhanced scraper for comprehensive results
            async with EnhancedBusinessScraper() as scraper:
                businesses = await scraper.scrape_comprehensive(industry, location, radius_miles)
            
            logger.info(f"Found {len(businesses)} businesses using enhanced methods")
            
            # Save businesses to both main table and industry table
            saved_count = 0
            for business in businesses:
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
                        'opening_hours': json.dumps({}),  # Empty JSON object for opening hours
                        'place_id': business.get('place_id', ''),
                        'types': json.dumps(business.get('types', [])),  # Convert list to JSON string
                        'geometry': json.dumps(business.get('geometry', {}))  # Convert dict to JSON string
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
                "found": len(businesses),
                "saved": saved_count,
                "table_name": table_name,
                "errors": []
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced scrape_and_save: {e}")
            return {
                "found": 0,
                "saved": 0,
                "table_name": "",
                "errors": [str(e)]
            }

async def test_enhanced_simple_scraper():
    """Test the enhanced simple scraper"""
    try:
        scraper = EnhancedSimpleScraper()
        
        # Test with CPCS training in Manchester
        result = await scraper.scrape_and_save("CPCS training", "Manchester, UK", 25)
        
        print(f"\n🎉 Enhanced Simple Scraper Results:")
        print(f"Businesses found: {result['found']}")
        print(f"Businesses saved: {result['saved']}")
        print(f"Industry table: {result['table_name']}")
        if result['errors']:
            print(f"Errors: {result['errors']}")
        
    except Exception as e:
        print(f"❌ Error testing enhanced simple scraper: {e}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_simple_scraper())
