#!/usr/bin/env python3
"""
Example usage scripts for the Google Maps Business Scraper
"""

import asyncio
import json
from datetime import datetime
from config import Config
from main import BusinessScrapingOrchestrator
from utils import ExportUtils, ReportUtils

async def example_full_industry_scrape():
    """Example: Full industry scrape with Companies House verification"""
    print("Example: Full Industry Scrape")
    print("=" * 40)
    
    orchestrator = BusinessScrapingOrchestrator()
    
    try:
        await orchestrator.initialize()
        
        # Scrape restaurants in major UK cities
        industry = "restaurants"
        print(f"Scraping {industry} industry...")
        
        stats = await orchestrator.scrape_industry_comprehensive(
            industry=industry,
            verify_companies_house=True
        )
        
        print("\nScraping Results:")
        print(f"- Total businesses found: {stats['total_businesses_found']}")
        print(f"- Businesses saved: {stats['businesses_saved']}")
        print(f"- Companies House matches: {stats['companies_house_matches']}")
        print(f"- Duration: {stats['duration']:.2f} seconds")
        
        if stats.get('errors'):
            print(f"- Errors encountered: {len(stats['errors'])}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await orchestrator.cleanup()

async def example_verification_sweep():
    """Example: Run verification sweep on existing data"""
    print("Example: Verification Sweep")
    print("=" * 30)
    
    orchestrator = BusinessScrapingOrchestrator()
    
    try:
        await orchestrator.initialize()
        
        print("Running verification sweep for unverified businesses...")
        await orchestrator.run_verification_sweep()
        print("Verification sweep completed!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await orchestrator.cleanup()

async def example_multi_industry_scrape():
    """Example: Scrape multiple industries"""
    print("Example: Multi-Industry Scrape")
    print("=" * 35)
    
    orchestrator = BusinessScrapingOrchestrator()
    
    try:
        await orchestrator.initialize()
        
        # Define industries to scrape
        industries = ["restaurants", "retail", "healthcare"]
        
        all_stats = {}
        
        for industry in industries:
            print(f"\nScraping {industry}...")
            stats = await orchestrator.scrape_industry_comprehensive(
                industry=industry,
                verify_companies_house=True
            )
            all_stats[industry] = stats
            
            print(f"Completed {industry}: {stats['businesses_saved']} businesses saved")
            
        # Summary
        print("\n" + "=" * 50)
        print("MULTI-INDUSTRY SCRAPE SUMMARY")
        print("=" * 50)
        
        total_found = sum(stats['total_businesses_found'] for stats in all_stats.values())
        total_saved = sum(stats['businesses_saved'] for stats in all_stats.values())
        total_verified = sum(stats['companies_house_matches'] for stats in all_stats.values())
        
        print(f"Total businesses found: {total_found}")
        print(f"Total businesses saved: {total_saved}")
        print(f"Total Companies House matches: {total_verified}")
        
        for industry, stats in all_stats.items():
            print(f"\n{industry.title()}:")
            print(f"  Found: {stats['total_businesses_found']}")
            print(f"  Saved: {stats['businesses_saved']}")
            print(f"  Verified: {stats['companies_house_matches']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await orchestrator.cleanup()

def example_data_export():
    """Example: Export scraped data to various formats"""
    print("Example: Data Export")
    print("=" * 20)
    
    # This is a mock example - in real usage, you'd query the database
    sample_businesses = [
        {
            'name': 'The Corner Cafe',
            'address': '123 High Street, London, SW1A 1AA',
            'postcode': 'SW1A 1AA',
            'phone': '020 7123 4567',
            'website': 'https://cornercafe.co.uk',
            'email': 'info@cornercafe.co.uk',
            'industry': 'restaurants',
            'google_rating': 4.5,
            'google_reviews_count': 127,
            'latitude': 51.5074,
            'longitude': -0.1278,
            'companies_house_number': '12345678',
            'companies_house_status': 'active',
            'data_quality_score': 0.95
        },
        {
            'name': 'Tech Solutions Ltd',
            'address': '456 Business Park, Manchester, M1 1AA',
            'postcode': 'M1 1AA',
            'phone': '0161 123 4567',
            'website': 'https://techsolutions.co.uk',
            'industry': 'professional_services',
            'google_rating': 4.2,
            'google_reviews_count': 89,
            'latitude': 53.4808,
            'longitude': -2.2426,
            'companies_house_number': '87654321',
            'companies_house_status': 'active',
            'data_quality_score': 0.87
        }
    ]
    
    # Export to CSV
    csv_file = ExportUtils.to_csv(sample_businesses)
    print(f"Exported to CSV: {csv_file}")
    
    # Export to JSON
    json_file = ExportUtils.to_json(sample_businesses)
    print(f"Exported to JSON: {json_file}")
    
    # Generate report
    report = ReportUtils.generate_summary_report(sample_businesses)
    
    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"business_report_{timestamp}.txt"
    
    with open(report_file, 'w') as f:
        f.write(report)
        
    print(f"Generated report: {report_file}")
    print("\nReport preview:")
    print("-" * 30)
    print(report)

def example_custom_search():
    """Example: Custom search configuration"""
    print("Example: Custom Search Configuration")
    print("=" * 40)
    
    # Example of how to add a custom industry
    custom_industry = {
        "fitness": {
            "search_terms": ["gym", "fitness centre", "yoga studio", "pilates", "personal trainer"],
            "sic_codes": ["93110", "93120", "93130"],
            "exclude_terms": ["equipment", "online"]
        }
    }
    
    print("Custom industry configuration:")
    print(json.dumps(custom_industry, indent=2))
    
    print("\nTo use this configuration:")
    print("1. Add it to Config.INDUSTRIES in config.py")
    print("2. Run: python main.py scrape fitness")

async def example_targeted_location_scrape():
    """Example: Scrape specific locations only"""
    print("Example: Targeted Location Scrape")
    print("=" * 35)
    
    # This would require modifying the main scraper to accept custom locations
    custom_locations = [
        "Shoreditch, London, UK",
        "Canary Wharf, London, UK",
        "King's Cross, London, UK"
    ]
    
    print("Custom locations:")
    for location in custom_locations:
        print(f"- {location}")
        
    print("\nNote: To implement this, modify the scraper to accept custom location lists")
    print("instead of using the default Config.LOCATIONS")

def main():
    """Run example demonstrations"""
    examples = {
        "1": ("Full Industry Scrape", example_full_industry_scrape),
        "2": ("Verification Sweep", example_verification_sweep),
        "3": ("Multi-Industry Scrape", example_multi_industry_scrape),
        "4": ("Data Export", example_data_export),
        "5": ("Custom Search Config", example_custom_search),
        "6": ("Targeted Location Scrape", example_targeted_location_scrape)
    }
    
    print("Google Maps Scraper Examples")
    print("=" * 30)
    print("Choose an example to run:")
    print()
    
    for key, (title, _) in examples.items():
        print(f"{key}. {title}")
    
    print("0. Exit")
    print()
    
    try:
        choice = input("Enter your choice (0-6): ").strip()
        
        if choice == "0":
            print("Goodbye!")
            return
        elif choice in examples:
            title, func = examples[choice]
            print(f"\nRunning: {title}")
            print("=" * (len(title) + 10))
            
            if asyncio.iscoroutinefunction(func):
                asyncio.run(func())
            else:
                func()
        else:
            print("Invalid choice. Please try again.")
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error running example: {e}")

if __name__ == "__main__":
    main()
