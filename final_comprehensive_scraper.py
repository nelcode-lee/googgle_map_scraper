#!/usr/bin/env python3
"""
Final comprehensive scraper combining all methods for maximum business coverage
"""

import asyncio
import os
import json
from typing import List, Dict, Any
from loguru import logger
from simple_web_scraper import SimpleWebScraper
from database import DatabaseManager

class FinalComprehensiveScraper:
    """Final comprehensive scraper using all available methods"""
    
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
            
            # Method 1: Web Scraping - General Search
            logger.info("🚀 Method 1: Web Scraping - General Search")
            try:
                web_scraper = SimpleWebScraper()
                web_businesses = web_scraper.search_businesses_general(industry, location, 100)
                web_scraper.close()
                method_results['web_general'] = len(web_businesses)
                all_businesses.extend(web_businesses)
                logger.info(f"Web general search found {len(web_businesses)} businesses")
            except Exception as e:
                logger.error(f"Web general search failed: {e}")
                method_results['web_general'] = 0
            
            # Method 2: Web Scraping - Multiple Search Terms
            logger.info("🚀 Method 2: Web Scraping - Multiple Search Terms")
            try:
                search_terms = self._generate_search_terms(industry)
                multi_term_businesses = []
                
                web_scraper = SimpleWebScraper()
                for term in search_terms[:5]:  # Limit to first 5 terms to avoid too many requests
                    try:
                        businesses = web_scraper.search_businesses_general(term, location, 30)
                        multi_term_businesses.extend(businesses)
                        logger.info(f"Found {len(businesses)} businesses for term: {term}")
                    except Exception as e:
                        logger.debug(f"Error searching for term '{term}': {e}")
                        continue
                
                web_scraper.close()
                method_results['web_multi_term'] = len(multi_term_businesses)
                all_businesses.extend(multi_term_businesses)
                logger.info(f"Web multi-term search found {len(multi_term_businesses)} businesses")
            except Exception as e:
                logger.error(f"Web multi-term search failed: {e}")
                method_results['web_multi_term'] = 0
            
            # Method 3: Specific Known Business Search
            logger.info("🚀 Method 3: Specific Known Business Search")
            try:
                known_businesses = await self._search_known_businesses(industry, location)
                method_results['known_businesses'] = len(known_businesses)
                all_businesses.extend(known_businesses)
                logger.info(f"Known business search found {len(known_businesses)} businesses")
            except Exception as e:
                logger.error(f"Known business search failed: {e}")
                method_results['known_businesses'] = 0
            
            # Method 4: Alternative Search Locations
            logger.info("🚀 Method 4: Alternative Search Locations")
            try:
                alt_location_businesses = await self._search_alternative_locations(industry, location)
                method_results['alt_locations'] = len(alt_location_businesses)
                all_businesses.extend(alt_location_businesses)
                logger.info(f"Alternative locations search found {len(alt_location_businesses)} businesses")
            except Exception as e:
                logger.error(f"Alternative locations search failed: {e}")
                method_results['alt_locations'] = 0
            
            # Remove duplicates
            unique_businesses = self._remove_duplicates(all_businesses)
            logger.info(f"Total unique businesses found: {len(unique_businesses)}")
            
            # Save businesses to database
            saved_count = 0
            for business in unique_businesses:
                try:
                    # Clean the business data
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
                'plant qualifications',
                'forklift training',
                'excavator training',
                'dumper training',
                'telehandler training',
                'crane training'
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
                "Plant Training",
                "Skills Hub",
                "Training Hub",
                "Construction Skills Hub"
            ]
            
            # Try to find these specific businesses
            web_scraper = SimpleWebScraper()
            for center_name in known_centers:
                try:
                    business = web_scraper.search_specific_business(center_name, location)
                    if business:
                        known_businesses.append(business)
                        logger.info(f"Found known business: {center_name}")
                except Exception as e:
                    logger.debug(f"Error searching for {center_name}: {e}")
                    continue
            web_scraper.close()
        
        return known_businesses
    
    async def _search_alternative_locations(self, industry: str, location: str) -> List[Dict[str, Any]]:
        """Search in alternative locations to find more businesses"""
        alt_locations = []
        
        # Generate alternative locations based on the main location
        if 'manchester' in location.lower():
            alt_locations = [
                "Manchester, UK",
                "Greater Manchester, UK",
                "Manchester City Centre, UK",
                "Manchester Airport, UK",
                "Salford, UK",
                "Stockport, UK",
                "Bolton, UK",
                "Bury, UK",
                "Rochdale, UK",
                "Oldham, UK"
            ]
        elif 'london' in location.lower():
            alt_locations = [
                "London, UK",
                "Central London, UK",
                "East London, UK",
                "West London, UK",
                "North London, UK",
                "South London, UK",
                "Greater London, UK"
            ]
        elif 'birmingham' in location.lower():
            alt_locations = [
                "Birmingham, UK",
                "Birmingham City Centre, UK",
                "West Midlands, UK",
                "Coventry, UK",
                "Wolverhampton, UK"
            ]
        else:
            # Generic alternatives
            alt_locations = [location]
        
        all_businesses = []
        web_scraper = SimpleWebScraper()
        
        for alt_location in alt_locations[:3]:  # Limit to first 3 alternative locations
            try:
                businesses = web_scraper.search_businesses_general(industry, alt_location, 20)
                all_businesses.extend(businesses)
                logger.info(f"Found {len(businesses)} businesses in {alt_location}")
            except Exception as e:
                logger.debug(f"Error searching in {alt_location}: {e}")
                continue
        
        web_scraper.close()
        return all_businesses
    
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

async def test_final_comprehensive_scraper():
    """Test the final comprehensive scraper"""
    try:
        scraper = FinalComprehensiveScraper()
        
        # Test with CPCS training in Manchester
        result = await scraper.scrape_and_save_comprehensive("CPCS training", "Manchester, UK", 25)
        
        print(f"\n🎉 Final Comprehensive Scraper Results:")
        print(f"Total businesses found: {result['found']}")
        print(f"Businesses saved: {result['saved']}")
        print(f"Industry table: {result['table_name']}")
        print(f"Method results: {result['method_results']}")
        if result['errors']:
            print(f"Errors: {result['errors']}")
        
    except Exception as e:
        print(f"❌ Error testing final comprehensive scraper: {e}")

if __name__ == "__main__":
    asyncio.run(test_final_comprehensive_scraper())
