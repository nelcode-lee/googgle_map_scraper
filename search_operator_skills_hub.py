#!/usr/bin/env python3
"""
Direct search for Operator Skills Hub specifically
"""

from simple_web_scraper import SimpleWebScraper

def search_operator_skills_hub():
    """Search specifically for Operator Skills Hub"""
    scraper = SimpleWebScraper()
    try:
        print("🔍 Searching specifically for Operator Skills Hub...")
        
        # Try different search variations
        search_variations = [
            "Operator Skills Hub",
            "Operator Skills Hub Manchester",
            "Operator Skills Hub UK",
            "Operator Skills Hub training",
            "Operator Skills Hub CPCS",
            "Operator Skills Hub construction",
            "Skills Hub Manchester",
            "Skills Hub training Manchester",
            "Skills Hub CPCS Manchester"
        ]
        
        found_businesses = []
        
        for search_term in search_variations:
            print(f"\n🔍 Searching: '{search_term}'")
            try:
                business = scraper.search_specific_business(search_term, "Manchester")
                if business and business.get('name'):
                    print(f"✅ Found: {business.get('name')}")
                    print(f"   📍 {business.get('address')}")
                    if business.get('website'):
                        print(f"   🌐 {business.get('website')}")
                    if business.get('phone'):
                        print(f"   📞 {business.get('phone')}")
                    if business.get('rating'):
                        print(f"   ⭐ {business.get('rating')}")
                    found_businesses.append(business)
                else:
                    print("❌ Not found")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        if not found_businesses:
            print("\n🔍 Trying broader search...")
            try:
                businesses = scraper.search_businesses_general("Skills Hub", "Manchester, UK", 20)
                print(f"Found {len(businesses)} businesses with 'Skills Hub' in name:")
                for business in businesses:
                    if 'skills' in business.get('name', '').lower() and 'hub' in business.get('name', '').lower():
                        print(f"  - {business.get('name')}")
                        print(f"    📍 {business.get('address')}")
            except Exception as e:
                print(f"❌ Error in broader search: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    search_operator_skills_hub()
