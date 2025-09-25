#!/usr/bin/env python3
"""
Alternative Google Maps scraper using different selectors and approach
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

class AlternativeGoogleMapsScraper:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with different options"""
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
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Use undetected-chromedriver
        self.driver = uc.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("Alternative Chrome driver setup completed")
        
    def search_businesses(self, query: str, location: str) -> List[Dict[str, Any]]:
        """Search for businesses using alternative approach"""
        if not self.driver:
            self.setup_driver()
            
        # Use a different search approach
        search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}+{location.replace(' ', '+')}"
        logger.info(f"Searching: {query} in {location}")
        
        try:
            self.driver.get(search_url)
            time.sleep(8)  # Wait longer for page to load
            
            # Handle popups
            self._handle_all_popups()
            
            # Wait for results
            time.sleep(5)
            
            businesses = []
            
            # Try multiple different approaches to find businesses
            business_elements = []
            
            # Approach 1: Look for specific business-related selectors
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
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        business_elements.extend(elements)
                        break
                except:
                    continue
            
            # Approach 2: If no elements found, try to find any clickable elements
            if not business_elements:
                try:
                    all_clickable = self.driver.find_elements(By.CSS_SELECTOR, "*[onclick], *[jsaction], button, a")
                    business_elements = all_clickable
                    logger.info(f"Found {len(business_elements)} clickable elements")
                except:
                    pass
            
            # Approach 3: Get all elements and filter
            if not business_elements:
                try:
                    all_elements = self.driver.find_elements(By.CSS_SELECTOR, "*")
                    business_elements = [elem for elem in all_elements if elem.is_displayed()][:50]
                    logger.info(f"Found {len(business_elements)} visible elements")
                except:
                    pass
            
            # Extract data from found elements
            for i, element in enumerate(business_elements[:20]):  # Limit to first 20
                try:
                    business_data = self._extract_alternative_business_data(element, i)
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
    
    def _handle_all_popups(self):
        """Handle all possible popups"""
        try:
            # Wait for popups to appear
            time.sleep(3)
            
            # Try multiple times to handle popups
            for attempt in range(3):
                try:
                    # Find all buttons
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    
                    for button in buttons:
                        try:
                            if button.is_displayed():
                                text = button.text.lower()
                                if any(word in text for word in ['accept', 'continue', 'agree', 'ok', 'go back to web', 'upgrade']):
                                    button.click()
                                    logger.info(f"Clicked popup button: {button.text}")
                                    time.sleep(2)
                                    break
                        except:
                            continue
                    
                    # Also try JavaScript approach
                    js_script = """
                    var buttons = document.querySelectorAll('button');
                    for (var i = 0; i < buttons.length; i++) {
                        var button = buttons[i];
                        var text = button.textContent.toLowerCase();
                        if (text.includes('accept') || text.includes('continue') || text.includes('agree') || text.includes('ok') || text.includes('go back to web')) {
                            button.click();
                            return 'clicked: ' + button.textContent;
                        }
                    }
                    return 'no button found';
                    """
                    result = self.driver.execute_script(js_script)
                    if 'clicked' in result:
                        logger.info(f"JavaScript clicked button: {result}")
                        time.sleep(2)
                    
                except Exception as e:
                    logger.debug(f"Popup handling attempt {attempt + 1} failed: {e}")
                
                time.sleep(1)
                    
        except Exception as e:
            logger.debug(f"Could not handle popups: {e}")
    
    def _extract_alternative_business_data(self, element, index: int) -> Optional[Dict[str, Any]]:
        """Extract business data using alternative approach"""
        try:
            business_data = {}
            
            # Get the text content
            text = element.text.strip()
            
            # Skip if empty or too short
            if not text or len(text) < 3:
                return None
            
            # Skip common UI elements
            skip_phrases = [
                'price', 'rating', 'cuisine', 'hours', 'all filters', 'show results',
                'directions', 'save', 'share', 'more', 'less', 'view all', 'see all',
                'search', 'filter', 'sort', 'map', 'satellite', 'terrain',
                'traffic', 'transit', 'bicycling', 'street view', 'photos',
                'reviews', 'photos', 'about', 'menu', 'order online',
                'call', 'website', 'directions', 'save', 'share'
            ]
            
            # Check if text contains skip phrases
            text_lower = text.lower()
            if any(phrase in text_lower for phrase in skip_phrases):
                return None
            
            # Try to extract business name
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            if not lines:
                return None
            
            # Use the first line as business name
            name = lines[0]
            
            # Skip if name is too short or looks like UI text
            if len(name) < 3 or name.lower() in skip_phrases:
                return None
            
            business_data['name'] = name
            
            # Try to extract rating from text
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
            business_data['place_id'] = f"alt_{index}_{hash(name) % 10000}"
            
            return business_data
            
        except Exception as e:
            logger.debug(f"Error extracting business data: {e}")
            return None
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser driver closed")

# Test the alternative scraper
if __name__ == "__main__":
    scraper = AlternativeGoogleMapsScraper()
    
    try:
        businesses = scraper.search_businesses("restaurants", "London, UK")
        
        print(f"\n🎯 Alternative Scraper Results:")
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
