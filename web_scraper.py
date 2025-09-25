#!/usr/bin/env python3
"""
Web scraper for Google Maps using Selenium - alternative to Places API
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
import undetected_chromedriver as uc

class WebMapsScraper:
    """Web scraper for Google Maps using Selenium"""
    
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with stealth options"""
        try:
            options = uc.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            options.add_argument("--disable-javascript")
            options.add_argument("--window-size=1920,1080")
            
            self.driver = uc.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Chrome driver setup successfully")
            return True
        except Exception as e:
            logger.error(f"Error setting up Chrome driver: {e}")
            return False
    
    def search_businesses_web(self, industry: str, location: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Search for businesses using web scraping"""
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
            businesses = self._extract_business_data()
            
            logger.info(f"Found {len(businesses)} businesses via web scraping")
            return businesses
            
        except Exception as e:
            logger.error(f"Error in web scraping: {e}")
            return []
    
    def _handle_cookie_consent(self):
        """Handle cookie consent popup"""
        try:
            # Wait for popup and click accept
            wait = WebDriverWait(self.driver, 10)
            
            # Try different selectors for cookie consent
            consent_selectors = [
                "button[aria-label*='Accept all']",
                "button[aria-label*='Accept']",
                "button:contains('Accept all')",
                "button:contains('Accept')",
                "button:contains('I agree')",
                "button:contains('Agree')"
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
            
            # Wait for results container
            results_selectors = [
                "[role='main']",
                ".m6QErb",
                ".Nv2PK",
                ".section-scrollbox"
            ]
            
            for selector in results_selectors:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    logger.info("Results loaded")
                    break
                except TimeoutException:
                    continue
                    
        except Exception as e:
            logger.debug(f"Results loading: {e}")
    
    def _scroll_for_more_results(self, max_results: int):
        """Scroll to load more results"""
        try:
            # Find the scrollable results container
            scrollable_selectors = [
                "[role='main']",
                ".m6QErb",
                ".Nv2PK"
            ]
            
            scrollable_element = None
            for selector in scrollable_selectors:
                try:
                    scrollable_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not scrollable_element:
                logger.warning("Could not find scrollable element")
                return
            
            # Scroll multiple times to load more results
            for i in range(10):  # Scroll 10 times
                try:
                    # Scroll down
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 1000", scrollable_element)
                    time.sleep(2)
                    
                    # Check if we have enough results
                    current_results = len(self.driver.find_elements(By.CSS_SELECTOR, "[data-value='Directions']"))
                    if current_results >= max_results:
                        break
                        
                except Exception as e:
                    logger.debug(f"Scrolling error: {e}")
                    break
                    
        except Exception as e:
            logger.debug(f"Scrolling for results: {e}")
    
    def _extract_business_data(self) -> List[Dict[str, Any]]:
        """Extract business data from the page"""
        businesses = []
        
        try:
            # Find business result elements
            business_selectors = [
                "[data-value='Directions']",
                ".Nv2PK",
                ".section-result",
                ".section-result-content"
            ]
            
            business_elements = []
            for selector in business_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        business_elements = elements
                        break
                except:
                    continue
            
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
            
            name = self._extract_text_by_selectors(element, name_selectors)
            if not name:
                return None
            business['name'] = name.strip()
            
            # Extract address
            address_selectors = [
                ".fontBodyMedium",
                ".section-result-location",
                ".section-result-address"
            ]
            business['address'] = self._extract_text_by_selectors(element, address_selectors)
            
            # Extract rating
            rating_selectors = [
                ".fontDisplayLarge",
                ".section-star-display",
                "[role='img']"
            ]
            rating_text = self._extract_text_by_selectors(element, rating_selectors)
            if rating_text:
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    business['rating'] = float(rating_match.group(1))
            
            # Extract phone (if visible)
            phone_selectors = [
                "[data-value*='phone']",
                ".section-result-phone"
            ]
            business['phone'] = self._extract_text_by_selectors(element, phone_selectors)
            
            # Extract website (if visible)
            website_selectors = [
                "[data-value*='website']",
                ".section-result-website"
            ]
            business['website'] = self._extract_text_by_selectors(element, website_selectors)
            
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
    
    def _extract_text_by_selectors(self, element, selectors: List[str]) -> str:
        """Extract text using multiple selectors"""
        for selector in selectors:
            try:
                if selector.startswith("[") and "contains" in selector:
                    # Handle attribute-based selectors
                    attr_name = selector.split('[')[1].split('=')[0]
                    attr_value = selector.split('=')[1].split(']')[0].strip("'\"")
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

def test_web_scraper():
    """Test the web scraper"""
    scraper = WebMapsScraper()
    try:
        businesses = scraper.search_businesses_web("CPCS training", "Manchester, UK", 50)
        
        print(f"\n🎉 Web Scraper Results:")
        print(f"Found {len(businesses)} businesses")
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
        print(f"❌ Error testing web scraper: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    test_web_scraper()
