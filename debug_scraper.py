#!/usr/bin/env python3
"""
Debug Google Maps scraper to see what elements we're actually finding
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

class DebugGoogleMapsScraper:
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
        
        logger.info("Debug Chrome driver setup completed")
        
    def search_businesses(self, query: str, location: str) -> List[Dict[str, Any]]:
        """Debug search to see what we're finding"""
        if not self.driver:
            self.setup_driver()
            
        search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}+{location.replace(' ', '+')}"
        logger.info(f"Searching: {query} in {location}")
        
        try:
            self.driver.get(search_url)
            time.sleep(8)
            
            # Handle popups
            self._handle_popups()
            
            time.sleep(5)
            
            # Try to find elements
            selectors_to_try = [
                "[data-result-index]",
                "[jsaction*='pane']",
                "[role='button']",
                ".Nv2PK",
                ".THOPZb",
                ".fontBodyMedium",
                ".fontHeadlineSmall",
                "[data-value]",
                ".qBF1Pd",
                ".fontTitleMedium",
                ".fontTitleLarge"
            ]
            
            for selector in selectors_to_try:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"\n=== FOUND {len(elements)} ELEMENTS WITH SELECTOR: {selector} ===")
                        
                        # Show first 10 elements
                        for i, element in enumerate(elements[:10]):
                            try:
                                text = element.text.strip()
                                tag = element.tag_name
                                classes = element.get_attribute('class')
                                
                                print(f"\nElement {i+1}:")
                                print(f"  Tag: {tag}")
                                print(f"  Classes: {classes}")
                                print(f"  Text: '{text}'")
                                print(f"  Text length: {len(text)}")
                                
                                # Check if it looks like a business
                                if text and len(text) > 3:
                                    skip_phrases = ['price', 'rating', 'cuisine', 'hours', 'all filters', 'show results']
                                    if not any(phrase in text.lower() for phrase in skip_phrases):
                                        print(f"  ✅ POTENTIAL BUSINESS: {text[:50]}...")
                                    else:
                                        print(f"  ❌ FILTERED OUT: {text[:50]}...")
                                
                            except Exception as e:
                                print(f"  Error getting element {i+1} info: {e}")
                        
                        break
                        
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {e}")
                    continue
            
            return []
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
    
    def _handle_popups(self):
        """Handle popups"""
        try:
            time.sleep(3)
            
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
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser driver closed")

# Test the debug scraper
if __name__ == "__main__":
    scraper = DebugGoogleMapsScraper()
    
    try:
        scraper.search_businesses("restaurants", "London, UK")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.close()
