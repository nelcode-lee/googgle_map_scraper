#!/usr/bin/env python3
"""
Main scraper using Google Places API instead of web scraping
This is much more reliable and doesn't have popup issues
"""

import asyncio
import os
from typing import List, Dict, Any
from loguru import logger
from places_api_scraper import GooglePlacesScraper
from data_processor import DataProcessor
from database import DatabaseManager
from config import Config

class PlacesMainScraper:
    """Main scraper using Google Places API"""
    
    def __init__(self):
        self.places_scraper = None
        self.data_processor = DataProcessor()
        self.db = DatabaseManager()
        
    async def scrape_industry(self, industry: str, locations: List[str]) -> List[Dict[str, Any]]:
        """Scrape businesses for an industry using Places API"""
        try:
            async with GooglePlacesScraper() as scraper:
                self.places_scraper = scraper
                
                # Generate search queries for the industry
                search_queries = self._generate_search_queries(industry)
                
                all_businesses = []
                
                for location in locations:
                    logger.info(f"Searching for {industry} in {location}")
                    
                    for query in search_queries:
                        try:
                            businesses = await scraper.search_places(query, location)
                            
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
                
        except Exception as e:
            logger.error(f"Error in scrape_industry: {e}")
            return []
    
    def _generate_search_queries(self, industry: str) -> List[str]:
        """Generate multiple search queries for an industry"""
        industry_lower = industry.lower()
        
        # Base queries
        queries = [industry_lower]
        
        # Add variations based on industry
        if 'restaurant' in industry_lower or 'food' in industry_lower:
            queries.extend(['restaurants', 'cafes', 'coffee shops'])
        elif 'retail' in industry_lower or 'shop' in industry_lower:
            queries.extend(['shops', 'stores', 'retail stores'])
        elif 'healthcare' in industry_lower or 'medical' in industry_lower:
            queries.extend(['doctors', 'clinics', 'hospitals'])
        elif 'professional' in industry_lower or 'services' in industry_lower:
            queries.extend(['professional services', 'consultants'])
        
        return queries[:3]  # Limit to 3 queries per industry
    
    async def process_and_save_businesses(self, businesses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process and save businesses to database"""
        if not businesses:
            return {"saved": 0, "errors": []}
        
        try:
            # Connect to database
            await self.db.connect()
            # Process the data
            logger.info(f"Processing {len(businesses)} businesses...")
            processed_businesses = await self.data_processor.process_businesses(businesses)
            
            if not processed_businesses:
                logger.warning("No businesses after processing")
                return {"saved": 0, "errors": ["No businesses after processing"]}
            
            # Save to database
            logger.info(f"Saving {len(processed_businesses)} businesses to database...")
            saved_count = 0
            for business in processed_businesses:
                try:
                    await self.db.insert_business(business)
                    saved_count += 1
                except Exception as e:
                    logger.warning(f"Error saving business {business.get('name', 'Unknown')}: {e}")
                    continue
            
            logger.info(f"Successfully saved {saved_count} businesses")
            return {"saved": saved_count, "errors": []}
            
        except Exception as e:
            logger.error(f"Error processing and saving businesses: {e}")
            return {"saved": 0, "errors": [str(e)]}
    
    async def scrape_industry_comprehensive(self, industry: str, locations: List[str]) -> Dict[str, Any]:
        """Comprehensive scraping with processing and saving"""
        stats = {
            "industry": industry,
            "total_businesses_found": 0,
            "businesses_saved": 0,
            "errors": []
        }
        
        try:
            # 1. Scrape businesses
            logger.info(f"Phase 1: Scraping {industry} businesses using Places API")
            businesses = await self.scrape_industry(industry, locations)
            stats["total_businesses_found"] = len(businesses)
            
            if not businesses:
                logger.warning(f"No businesses found for industry: {industry}")
                return stats
            
            # 2. Process and save
            logger.info(f"Phase 2: Processing and saving {len(businesses)} businesses")
            save_result = await self.process_and_save_businesses(businesses)
            stats["businesses_saved"] = save_result["saved"]
            stats["errors"].extend(save_result["errors"])
            
            logger.info(f"✅ Scraping complete: {stats['businesses_saved']} businesses saved")
            return stats
            
        except Exception as e:
            logger.error(f"Error in comprehensive scraping: {e}")
            stats["errors"].append(str(e))
            return stats


async def test_places_main_scraper():
    """Test the Places API main scraper"""
    try:
        scraper = PlacesMainScraper()
        
        # Test with a simple industry
        result = await scraper.scrape_industry_comprehensive(
            "cafes", 
            ["Manchester"]
        )
        
        print(f"\n🎉 Scraping Results:")
        print(f"Industry: {result['industry']}")
        print(f"Businesses found: {result['total_businesses_found']}")
        print(f"Businesses saved: {result['businesses_saved']}")
        if result['errors']:
            print(f"Errors: {result['errors']}")
        
    except Exception as e:
        print(f"❌ Error testing Places main scraper: {e}")


if __name__ == "__main__":
    asyncio.run(test_places_main_scraper())
