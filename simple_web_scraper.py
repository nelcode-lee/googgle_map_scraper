#!/usr/bin/env python3
"""
Simple web scraper for Google Maps using Selenium - focused on finding specific businesses
"""

import time
import re
from typing import List, Dict, Any, Optional
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class SimpleWebScraper:
    """Simple web scraper for Google Maps using Selenium"""
    
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with simple options"""
        try:
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Chrome driver setup successfully")
            return True
        except Exception as e:
            logger.error(f"Error setting up Chrome driver: {e}")
            return False
    
    def search_specific_business(self, business_name: str, location: str) -> Optional[Dict[str, Any]]:
        """Search for a specific business by name"""
        if not self.driver:
            if not self.setup_driver():
                return None
        
        try:
            # Construct search URL for specific business
            search_query = f"{business_name} {location}"
            search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            logger.info(f"Searching for specific business: {search_query}")
            self.driver.get(search_url)
            time.sleep(5)
            
            # Handle cookie consent
            self._handle_cookie_consent()
            
            # Wait for results
            time.sleep(3)
            
            # Extract business data
            business_data = self._extract_business_from_page()
            
            if business_data:
                logger.info(f"Found business: {business_data.get('name')}")
                return business_data
            else:
                logger.warning(f"Business not found: {business_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error searching for specific business: {e}")
            return None
    
    def search_businesses_general(self, industry: str, location: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for businesses in general category"""
        if not self.driver:
            if not self.setup_driver():
                return []
        
        try:
            # Construct search URL
            search_query = f"{industry} in {location}"
            search_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            logger.info(f"Searching: {search_query}")
            self.driver.get(search_url)
            time.sleep(5)
            
            # Handle cookie consent
            self._handle_cookie_consent()
            
            # Wait for results to load
            self._wait_for_results()
            
            # Scroll to load more results
            self._scroll_for_more_results(max_results)
            
            # Extract business data
            businesses = self._extract_businesses_from_page()
            
            logger.info(f"Found {len(businesses)} businesses via web scraping")
            return businesses
            
        except Exception as e:
            logger.error(f"Error in general business search: {e}")
            return []
    
    def _handle_cookie_consent(self):
        """Handle cookie consent popup"""
        try:
            time.sleep(2)
            
            # Try different selectors for cookie consent
            consent_selectors = [
                "button[aria-label*='Accept all']",
                "button[aria-label*='Accept']",
                "button:contains('Accept all')",
                "button:contains('Accept')",
                "button:contains('I agree')",
                "button:contains('Agree')",
                "button:contains('Got it')"
            ]
            
            for selector in consent_selectors:
                try:
                    if selector.startswith("button:contains"):
                        # Use XPath for text-based selection
                        text_content = selector.split('contains(')[1].split(')')[0].strip("'")
                        xpath = f"//button[contains(text(), '{text_content}')]"
                        button = self.driver.find_element(By.XPATH, xpath)
                    else:
                        button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if button.is_displayed():
                        button.click()
                        logger.info("Clicked cookie consent button")
                        time.sleep(2)
                        break
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"Cookie consent handling: {e}")
    
    def _wait_for_results(self):
        """Wait for search results to load"""
        try:
            wait = WebDriverWait(self.driver, 15)
            
            # Wait for any result element
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[role='main'], .m6QErb, .Nv2PK")))
            logger.info("Results loaded")
                    
        except Exception as e:
            logger.debug(f"Results loading: {e}")
    
    def _scroll_for_more_results(self, max_results: int):
        """Scroll to load more results"""
        try:
            # Find the scrollable results container
            scrollable_element = None
            selectors = ["[role='main']", ".m6QErb", ".Nv2PK"]
            
            for selector in selectors:
                try:
                    scrollable_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not scrollable_element:
                logger.warning("Could not find scrollable element")
                return
            
            # Scroll multiple times to load more results
            for i in range(5):  # Scroll 5 times
                try:
                    # Scroll down
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 1000", scrollable_element)
                    time.sleep(2)
                    
                    # Check if we have enough results
                    current_results = len(self.driver.find_elements(By.CSS_SELECTOR, "[data-value='Directions'], .Nv2PK"))
                    if current_results >= max_results:
                        break
                        
                except Exception as e:
                    logger.debug(f"Scrolling error: {e}")
                    break
                    
        except Exception as e:
            logger.debug(f"Scrolling for results: {e}")
    
    def _extract_businesses_from_page(self) -> List[Dict[str, Any]]:
        """Extract business data from the page"""
        businesses = []
        
        try:
            # Find business result elements
            business_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-value='Directions'], .Nv2PK, .section-result")
            
            logger.info(f"Found {len(business_elements)} business elements")
            
            for element in business_elements:
                try:
                    business_data = self._extract_single_business(element)
                    if business_data and business_data.get('name'):
                        businesses.append(business_data)
                except Exception as e:
                    logger.debug(f"Error extracting business: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting business data: {e}")
        
        return businesses
    
    def _extract_business_from_page(self) -> Optional[Dict[str, Any]]:
        """Extract data from the main business on the page"""
        try:
            business = {}
            
            # Extract name
            name_selectors = [
                "h1",
                ".fontHeadlineSmall",
                ".fontHeadlineMedium",
                ".fontHeadlineLarge",
                ".section-result-title"
            ]
            
            name = self._extract_text_by_selectors(name_selectors)
            if not name:
                return None
            business['name'] = name.strip()
            
            # Extract address
            address_selectors = [
                ".fontBodyMedium",
                ".section-result-location",
                ".section-result-address"
            ]
            business['address'] = self._extract_text_by_selectors(address_selectors)
            
            # Extract rating
            rating_selectors = [
                ".fontDisplayLarge",
                ".section-star-display",
                "[role='img']"
            ]
            rating_text = self._extract_text_by_selectors(rating_selectors)
            if rating_text:
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    business['rating'] = float(rating_match.group(1))
            
            # Extract phone
            phone_selectors = [
                "[data-value*='phone']",
                ".section-result-phone"
            ]
            business['phone'] = self._extract_text_by_selectors(phone_selectors)
            
            # Extract website
            website_selectors = [
                "[data-value*='website']",
                ".section-result-website"
            ]
            business['website'] = self._extract_text_by_selectors(website_selectors)
            
            # Generate a simple place_id
            business['place_id'] = f"web_{hash(business['name'] + business.get('address', ''))}"
            business['types'] = "[]"
            business['geometry'] = "{}"
            business['opening_hours'] = ""
            business['email'] = ""
            
            return business
            
        except Exception as e:
            logger.debug(f"Error extracting single business: {e}")
            return None
    
    def _extract_single_business(self, element) -> Optional[Dict[str, Any]]:
        """Extract data from a single business element"""
        try:
            business = {}
            
            # Extract name
            name_selectors = [
                ".fontHeadlineSmall",
                ".fontHeadlineMedium",
                ".fontHeadlineLarge",
                "h3",
                ".section-result-title"
            ]
            
            name = self._extract_text_by_selectors_from_element(element, name_selectors)
            if not name:
                return None
            business['name'] = name.strip()
            
            # Extract address
            address_selectors = [
                ".fontBodyMedium",
                ".section-result-location",
                ".section-result-address"
            ]
            business['address'] = self._extract_text_by_selectors_from_element(element, address_selectors)
            
            # Extract rating
            rating_selectors = [
                ".fontDisplayLarge",
                ".section-star-display",
                "[role='img']"
            ]
            rating_text = self._extract_text_by_selectors_from_element(element, rating_selectors)
            if rating_text:
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    business['rating'] = float(rating_match.group(1))
            
            # Extract phone
            phone_selectors = [
                "[data-value*='phone']",
                ".section-result-phone"
            ]
            business['phone'] = self._extract_text_by_selectors_from_element(element, phone_selectors)
            
            # Extract website
            website_selectors = [
                "[data-value*='website']",
                ".section-result-website"
            ]
            business['website'] = self._extract_text_by_selectors_from_element(element, website_selectors)
            
            # Generate a simple place_id
            business['place_id'] = f"web_{hash(business['name'] + business.get('address', ''))}"
            business['types'] = "[]"
            business['geometry'] = "{}"
            business['opening_hours'] = ""
            business['email'] = ""
            
            return business
            
        except Exception as e:
            logger.debug(f"Error extracting single business: {e}")
            return None
    
    def _extract_text_by_selectors(self, selectors: List[str]) -> str:
        """Extract text using multiple selectors from the main page"""
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if text:
                        return text
            except:
                continue
        return ""
    
    def _extract_text_by_selectors_from_element(self, element, selectors: List[str]) -> str:
        """Extract text using multiple selectors from a specific element"""
        for selector in selectors:
            try:
                if selector.startswith("[") and "contains" in selector:
                    # Handle attribute-based selectors
                    attr_name = selector.split('[')[1].split('=')[0]
                    attr_value = selector.split('=')[1].split(']')[0].strip("'")
                    sub_elements = element.find_elements(By.CSS_SELECTOR, f"[{attr_name}*='{attr_value}']")
                else:
                    sub_elements = element.find_elements(By.CSS_SELECTOR, selector)
                
                for sub_element in sub_elements:
                    text = sub_element.text.strip()
                    if text:
                        return text
            except:
                continue
        return ""
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

def test_simple_web_scraper():
    """Test the simple web scraper"""
    scraper = SimpleWebScraper()
    try:
        # Test specific business search
        print("🔍 Testing specific business search...")
        business = scraper.search_specific_business("Operator Skills Hub", "Manchester")
        if business:
            print(f"✅ Found: {business.get('name')}")
            print(f"   📍 {business.get('address')}")
            if business.get('website'):
                print(f"   🌐 {business.get('website')}")
            if business.get('phone'):
                print(f"   📞 {business.get('phone')}")
        else:
            print("❌ Operator Skills Hub not found")
        
        # Test general search
        print("\n🔍 Testing general business search...")
        businesses = scraper.search_businesses_general("CPCS training", "Manchester, UK", 20)
        
        print(f"\n🎉 Found {len(businesses)} businesses:")
        print("=" * 60)
        
        for i, business in enumerate(businesses[:10]):  # Show first 10
            print(f"{i+1}. {business.get('name')}")
            print(f"   📍 {business.get('address')}")
            if business.get('website'):
                print(f"   🌐 {business.get('website')}")
            if business.get('phone'):
                print(f"   📞 {business.get('phone')}")
            if business.get('rating'):
                print(f"   ⭐ {business.get('rating')}")
            print("")
            
    except Exception as e:
        print(f"❌ Error testing simple web scraper: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    test_simple_web_scraper()
