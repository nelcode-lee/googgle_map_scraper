#!/usr/bin/env python3
"""
Working Google Maps scraper that waits for actual business listings
"""

import time
import random
import re
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
from loguru import logger

class WorkingGoogleMapsScraper:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver"""
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--window-size=1920,1080")
        
        self.driver = uc.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("Working Chrome driver setup completed")
        
    def search_businesses(self, query: str, location: str) -> List[Dict[str, Any]]:
        """Search for businesses with proper waiting"""
        if not self.driver:
            self.setup_driver()
            
        search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}+{location.replace(' ', '+')}"
        logger.info(f"Searching: {query} in {location}")
        
        try:
            self.driver.get(search_url)
            time.sleep(8)
            
            # Handle popups
            self._handle_popups()
            
            # Wait for the page to fully load
            time.sleep(5)
            
            businesses = []
            
            # Wait for business listings to appear and scroll to load more
            self._wait_and_scroll_for_results()
            
            # Try to find business listings using multiple approaches
            business_elements = self._find_business_elements()
            
            if not business_elements:
                logger.warning("No business elements found")
                return []
            
            logger.info(f"Found {len(business_elements)} potential business elements")
            
            # Extract data from elements
            for i, element in enumerate(business_elements):
                try:
                    business_data = self._extract_business_data(element, i)
                    if business_data and business_data.get('name'):
                        businesses.append(business_data)
                        logger.info(f"Extracted business {len(businesses)}: {business_data['name']}")
                except Exception as e:
                    logger.debug(f"Error extracting business {i}: {e}")
                    continue
                    
            logger.info(f"Found {len(businesses)} businesses total")
            return businesses
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
    
    def _handle_popups(self):
        """Handle popups"""
        try:
            time.sleep(3)
            
            # Try multiple times to handle popups
            for attempt in range(3):
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    try:
                        if button.is_displayed():
                            text = button.text.lower()
                            if any(word in text for word in ['accept', 'continue', 'agree', 'ok', 'go back to web']):
                                button.click()
                                logger.info(f"Clicked popup button: {button.text}")
                                time.sleep(2)
                                break
                    except:
                        continue
                time.sleep(1)
                    
        except Exception as e:
            logger.debug(f"Could not handle popups: {e}")
    
    def _wait_and_scroll_for_results(self):
        """Wait for results and scroll to load more"""
        try:
            # Wait for the main results area
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='main']"))
            )
            
            # Scroll down to load more results
            for i in range(5):
                try:
                    # Scroll the results panel
                    results_panel = self.driver.find_element(By.CSS_SELECTOR, "[role='main']")
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 1000", results_panel)
                    time.sleep(2)
                except:
                    break
            
            # Wait a bit more for results to load
            time.sleep(3)
            
        except TimeoutException:
            logger.warning("Timeout waiting for results")
    
    def _find_business_elements(self):
        """Find business elements using multiple strategies"""
        business_elements = []
        
        # Strategy 1: Look for elements with business-like text
        try:
            all_elements = self.driver.find_elements(By.CSS_SELECTOR, "*")
            for element in all_elements:
                try:
                    if element.is_displayed():
                        text = element.text.strip()
                        if (text and len(text) > 5 and len(text) < 100 and 
                            not any(word in text.lower() for word in ['price', 'rating', 'cuisine', 'hours', 'all filters', 'show results', 'directions', 'save', 'share']) and
                            any(char.isalpha() for char in text)):  # Contains letters
                            business_elements.append(element)
                except:
                    continue
        except:
            pass
        
        # Strategy 2: Look for specific selectors that might contain businesses
        selectors_to_try = [
            "[data-result-index]",
            "[jsaction*='pane']",
            ".Nv2PK",
            ".THOPZb",
            ".fontBodyMedium",
            ".fontHeadlineSmall",
            ".fontTitleMedium"
        ]
        
        for selector in selectors_to_try:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    try:
                        if element.is_displayed() and element not in business_elements:
                            text = element.text.strip()
                            if text and len(text) > 3 and len(text) < 200:
                                business_elements.append(element)
                    except:
                        continue
            except:
                continue
        
        # Remove duplicates and limit
        business_elements = list(set(business_elements))[:20]
        
        return business_elements
    
    def _extract_business_data(self, element, index: int) -> Optional[Dict[str, Any]]:
        """Extract business data from element"""
        try:
            business_data = {}
            
            text = element.text.strip()
            
            if not text or len(text) < 3:
                return None
            
            # Skip common UI elements
            skip_phrases = [
                'price', 'rating', 'cuisine', 'hours', 'all filters', 'show results',
                'directions', 'save', 'share', 'more', 'less', 'view all', 'see all',
                'search', 'filter', 'sort', 'map', 'satellite', 'terrain',
                'traffic', 'transit', 'bicycling', 'street view', 'photos',
                'reviews', 'about', 'menu', 'order online', 'call', 'website'
            ]
            
            if any(phrase in text.lower() for phrase in skip_phrases):
                return None
            
            # Extract business name (first line)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            if not lines:
                return None
            
            name = lines[0]
            
            if len(name) < 3:
                return None
            
            business_data['name'] = name
            
            # Try to extract rating
            for line in lines:
                if re.search(r'\d+\.?\d*\s*\*', line) or '★' in line:
                    rating_match = re.search(r'(\d+\.?\d*)', line)
                    if rating_match:
                        try:
                            business_data['google_rating'] = float(rating_match.group(1))
                        except:
                            pass
                    break
            
            # Try to extract address
            for line in lines[1:]:
                if any(word in line.lower() for word in ['street', 'road', 'avenue', 'lane', 'way', 'close', 'drive', 'place']):
                    business_data['address'] = line
                    break
            
            # Generate place_id
            business_data['place_id'] = f"working_{index}_{hash(name) % 10000}"
            
            return business_data
            
        except Exception as e:
            logger.debug(f"Error extracting business data: {e}")
            return None
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser driver closed")

# Test the working scraper
if __name__ == "__main__":
    scraper = WorkingGoogleMapsScraper()
    
    try:
        businesses = scraper.search_businesses("restaurants", "London, UK")
        
        print(f"\n🎯 Working Scraper Results:")
        print(f"Found {len(businesses)} businesses")
        
        for i, business in enumerate(businesses[:5], 1):
            print(f"{i}. {business.get('name', 'Unknown')}")
            if business.get('google_rating'):
                print(f"   Rating: {business['google_rating']}")
            if business.get('address'):
                print(f"   Address: {business['address']}")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.close()
