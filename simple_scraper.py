#!/usr/bin/env python3
"""
Simple Google Maps scraper using a more reliable approach
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

class SimpleGoogleMapsScraper:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with minimal options for stability"""
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
        
        # Use undetected-chromedriver
        self.driver = uc.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("Simple Chrome driver setup completed")
        
    def search_businesses(self, query: str, location: str) -> List[Dict[str, Any]]:
        """Search for businesses using a simpler approach"""
        if not self.driver:
            self.setup_driver()
            
        # Use a simpler search URL
        search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}+{location.replace(' ', '+')}"
        logger.info(f"Searching: {query} in {location}")
        
        try:
            self.driver.get(search_url)
            time.sleep(5)
            
            # Handle any popups
            self._handle_popups()
            
            # Wait for results
            time.sleep(3)
            
            businesses = []
            
            # Try to find business listings using a different approach
            # Look for the main results container
            try:
                # Wait for the results to load
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[role='main']"))
                )
                
                # Get all clickable elements that might be businesses
                business_elements = self.driver.find_elements(By.CSS_SELECTOR, "[role='button']")
                
                logger.info(f"Found {len(business_elements)} potential business elements")
                
                # Filter and extract data from elements
                for i, element in enumerate(business_elements[:10]):  # Limit to first 10
                    try:
                        business_data = self._extract_simple_business_data(element, i)
                        if business_data and business_data.get('name'):
                            businesses.append(business_data)
                            logger.info(f"Extracted business {len(businesses)}: {business_data['name']}")
                    except Exception as e:
                        logger.debug(f"Error extracting business {i}: {e}")
                        continue
                        
            except TimeoutException:
                logger.warning("Timeout waiting for results")
                return []
                
            logger.info(f"Found {len(businesses)} businesses total")
            return businesses
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
    
    def _handle_popups(self):
        """Handle various popups that might appear"""
        try:
            # Wait a bit for popups to appear
            time.sleep(2)
            
            # Try to find and click any visible buttons
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
                    
        except Exception as e:
            logger.debug(f"Could not handle popups: {e}")
    
    def _extract_simple_business_data(self, element, index: int) -> Optional[Dict[str, Any]]:
        """Extract business data using a simpler approach"""
        try:
            business_data = {}
            
            # Get the text content of the element
            text = element.text.strip()
            
            # Skip if it's clearly not a business (filters, UI elements, etc.)
            if not text or len(text) < 3:
                return None
                
            # Skip common UI elements
            skip_words = ['price', 'rating', 'cuisine', 'hours', 'all filters', 'show results', 
                         'directions', 'save', 'share', 'more', 'less', 'view all', 'see all']
            
            if any(word in text.lower() for word in skip_words):
                return None
            
            # Try to extract a business name (first line of text)
            lines = text.split('\n')
            name = lines[0].strip() if lines else text
            
            # Skip if name is too short or looks like UI text
            if len(name) < 3 or name.lower() in skip_words:
                return None
                
            business_data['name'] = name
            
            # Try to extract additional info from the text
            if len(lines) > 1:
                # Look for rating
                for line in lines[1:]:
                    if re.search(r'\d+\.?\d*\s*\*', line) or '★' in line:
                        rating_match = re.search(r'(\d+\.?\d*)', line)
                        if rating_match:
                            business_data['google_rating'] = float(rating_match.group(1))
                        break
                
                # Look for address (usually contains common address words)
                for line in lines[1:]:
                    if any(word in line.lower() for word in ['street', 'road', 'avenue', 'lane', 'way', 'close', 'drive']):
                        business_data['address'] = line.strip()
                        break
            
            # Generate a simple place_id
            business_data['place_id'] = f"simple_{index}_{hash(name) % 10000}"
            
            return business_data
            
        except Exception as e:
            logger.debug(f"Error extracting business data: {e}")
            return None
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser driver closed")

# Test the simple scraper
if __name__ == "__main__":
    scraper = SimpleGoogleMapsScraper()
    
    try:
        businesses = scraper.search_businesses("restaurants", "London, UK")
        
        print(f"\n🎯 Simple Scraper Results:")
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
