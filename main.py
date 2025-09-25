import asyncio
import sys
from typing import List, Dict, Any
from loguru import logger
from datetime import datetime

from config import Config
from database import DatabaseManager
from google_maps_scraper import GoogleMapsScraper
from companies_house import CompaniesHouseAPI
from data_processor import DataProcessor

class BusinessScrapingOrchestrator:
    def __init__(self):
        self.db = DatabaseManager()
        self.scraper = GoogleMapsScraper()
        self.data_processor = DataProcessor()
        
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing Business Scraping Orchestrator...")
        await self.db.connect()
        logger.info("Orchestrator initialized successfully")
        
    async def scrape_industry_comprehensive(self, industry: str, verify_companies_house: bool = True) -> Dict[str, Any]:
        """Comprehensive industry scraping with Companies House verification"""
        logger.info(f"Starting comprehensive scraping for industry: {industry}")
        
        start_time = datetime.now()
        stats = {
            "industry": industry,
            "start_time": start_time,
            "total_businesses_found": 0,
            "businesses_saved": 0,
            "companies_house_matches": 0,
            "errors": []
        }
        
        try:
            # 1. Scrape Google Maps data
            logger.info(f"Phase 1: Scraping Google Maps for {industry}")
            try:
                businesses = await self.scraper.scrape_industry(industry, Config.LOCATIONS)
                stats["total_businesses_found"] = len(businesses)
            except Exception as e:
                logger.error(f"Error during scraping: {e}")
                stats["errors"].append(f"Scraping error: {str(e)}")
                return stats
            
            if not businesses:
                logger.warning(f"No businesses found for industry: {industry}")
                return stats
                
            # 2. Process and clean data
            logger.info("Phase 2: Processing and cleaning data")
            processed_businesses = await self.data_processor.process_businesses(businesses)
            
            # 3. Save to database
            logger.info("Phase 3: Saving businesses to database")
            saved_count = 0
            for business in processed_businesses:
                try:
                    business_id = await self.db.insert_business(business)
                    business['id'] = business_id
                    saved_count += 1
                except Exception as e:
                    logger.error(f"Error saving business {business.get('name')}: {e}")
                    stats["errors"].append(f"Save error: {business.get('name')} - {str(e)}")
                    
            stats["businesses_saved"] = saved_count
            
            # 4. Companies House verification
            if verify_companies_house:
                logger.info("Phase 4: Verifying with Companies House")
                ch_matches = await self._verify_with_companies_house(processed_businesses)
                stats["companies_house_matches"] = ch_matches
                
            # 5. Log search statistics
            for location in Config.LOCATIONS:
                industry_config = Config.INDUSTRIES.get(industry, {})
                for search_term in industry_config.get('search_terms', [industry]):
                    await self.db.log_search(industry, search_term, location, len(businesses))
                    
        except Exception as e:
            logger.error(f"Error in comprehensive scraping: {e}")
            stats["errors"].append(f"General error: {str(e)}")
            
        stats["end_time"] = datetime.now()
        stats["duration"] = (stats["end_time"] - stats["start_time"]).total_seconds()
        
        logger.info(f"Scraping completed for {industry}: {stats}")
        return stats
        
    async def _verify_with_companies_house(self, businesses: List[Dict[str, Any]]) -> int:
        """Verify businesses with Companies House"""
        matches = 0
        
        async with CompaniesHouseAPI() as ch_api:
            verified_businesses = await ch_api.bulk_verify_businesses(businesses)
            
            for business in verified_businesses:
                if business.get('companies_house_number'):
                    try:
                        await self.db.update_companies_house_data(
                            business['id'],
                            {
                                'company_number': business.get('companies_house_number'),
                                'company_status': business.get('companies_house_status'),
                                'date_of_creation': business.get('incorporation_date'),
                                'sic_codes': business.get('sic_codes', [])
                            }
                        )
                        matches += 1
                    except Exception as e:
                        logger.error(f"Error updating Companies House data: {e}")
                        
        return matches
        
    async def run_verification_sweep(self):
        """Run verification sweep for unverified businesses"""
        logger.info("Starting verification sweep for unverified businesses")
        
        unverified = await self.db.get_unverified_businesses(100)
        
        if not unverified:
            logger.info("No unverified businesses found")
            return
            
        async with CompaniesHouseAPI() as ch_api:
            for business in unverified:
                try:
                    company_match = await ch_api.find_matching_company(
                        business['name'], 
                        business.get('postcode')
                    )
                    
                    if company_match:
                        await self.db.update_companies_house_data(
                            business['id'],
                            {
                                'company_number': company_match.get('company_number'),
                                'company_status': company_match.get('company_status'),
                                'date_of_creation': company_match.get('date_of_creation'),
                                'sic_codes': [sic.get('code') for sic in company_match.get('sic_codes', [])]
                            }
                        )
                        logger.info(f"Verified: {business['name']} -> {company_match.get('company_number')}")
                        
                except Exception as e:
                    logger.error(f"Error verifying {business['name']}: {e}")
                    
                await asyncio.sleep(0.2)  # Rate limiting
                
    async def discover_missing_companies(self, industry: str):
        """Discover companies that might be missing from Google Maps data"""
        logger.info(f"Discovering missing companies for industry: {industry}")
        
        industry_config = Config.INDUSTRIES.get(industry, {})
        sic_codes = industry_config.get('sic_codes', [])
        
        if not sic_codes:
            logger.warning(f"No SIC codes configured for industry: {industry}")
            return
            
        async with CompaniesHouseAPI() as ch_api:
            discovered_companies = await ch_api.discover_companies_by_sic(sic_codes)
            
            # This would need additional implementation for SIC code discovery
            # as the basic Companies House API doesn't support this directly
            logger.info(f"Company discovery by SIC codes needs additional implementation")
            
    async def generate_report(self, industry: str = None) -> Dict[str, Any]:
        """Generate comprehensive report of scraped data"""
        logger.info("Generating comprehensive report")
        
        # This would query the database for statistics
        # Implementation would depend on specific reporting requirements
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_businesses": 0,
            "verified_businesses": 0,
            "by_industry": {},
            "by_location": {},
            "recent_activity": {}
        }
        
        return report
        
    async def cleanup(self):
        """Cleanup resources"""
        self.scraper.close()
        await self.db.close()
        logger.info("Cleanup completed")

async def main():
    """Main entry point"""
    orchestrator = BusinessScrapingOrchestrator()
    
    try:
        await orchestrator.initialize()
        
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == "scrape" and len(sys.argv) > 2:
                industry = sys.argv[2]
                if industry in Config.INDUSTRIES:
                    stats = await orchestrator.scrape_industry_comprehensive(industry)
                    print(f"Scraping completed: {stats}")
                else:
                    print(f"Unknown industry: {industry}")
                    print(f"Available industries: {list(Config.INDUSTRIES.keys())}")
                    
            elif command == "verify":
                await orchestrator.run_verification_sweep()
                
            elif command == "discover" and len(sys.argv) > 2:
                industry = sys.argv[2]
                await orchestrator.discover_missing_companies(industry)
                
            elif command == "report":
                report = await orchestrator.generate_report()
                print(f"Report: {report}")
                
            else:
                print("Unknown command or missing arguments")
                print("Usage:")
                print("  python main.py scrape <industry>")
                print("  python main.py verify")
                print("  python main.py discover <industry>")
                print("  python main.py report")
        else:
            print("No command specified")
            print("Available commands: scrape, verify, discover, report")
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        await orchestrator.cleanup()

if __name__ == "__main__":
    # Setup logging
    logger.add("scraper.log", rotation="10 MB", level=Config.LOG_LEVEL)
    
    # Run the main function
    asyncio.run(main())
