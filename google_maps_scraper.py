import asyncio
import time
import random
import json
import re
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from fake_useragent import UserAgent
from loguru import logger
import undetected_chromedriver as uc
from config import Config

class GoogleMapsScraper:
    def __init__(self):
        self.driver = None
        self.ua = UserAgent() if Config.USER_AGENT_ROTATION else None
        
    def setup_driver(self):
        """Setup Chrome driver with stealth options"""
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-translate")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-prompt-on-repost")
        options.add_argument("--disable-domain-reliability")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-gpu-logging")
        options.add_argument("--silent")
        options.add_argument("--log-level=3")
        
        if Config.USER_AGENT_ROTATION and self.ua:
            options.add_argument(f"--user-agent={self.ua.random}")
        
        # Use undetected-chromedriver for better stealth
        self.driver = uc.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        
        # Set window size
        self.driver.set_window_size(1920, 1080)
        
        logger.info("Chrome driver setup completed")
        
    def _handle_cookie_consent(self):
        """Handle Google's cookie consent and upgrade popups with ultra-aggressive approach"""
        try:
            # Wait for popups to appear
            time.sleep(5)
            
            # Try multiple approaches to handle popups
            for attempt in range(5):  # Reduced attempts to prevent infinite loops
                try:
                    logger.info(f"Popup handling attempt {attempt + 1}")
                    
                    # Check if driver is still valid
                    try:
                        current_url = self.driver.current_url
                        logger.debug(f"Current URL: {current_url}")
                        # If we're not on Google Maps, we might be stuck in a popup
                        if 'google.com/maps' not in current_url:
                            logger.warning(f"Not on Google Maps page: {current_url}")
                            # Try to navigate back to Google Maps
                            self.driver.get("https://www.google.com/maps")
                            time.sleep(3)
                            return
                    except Exception as e:
                        logger.warning(f"Driver session invalid during popup handling: {e}")
                        return  # Exit if driver is invalid
                    
                    # Method 1: Look for all buttons and click relevant ones
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    logger.info(f"Found {len(buttons)} buttons on page")
                    
                    # If no buttons found, window might be closed
                    if len(buttons) == 0:
                        logger.warning("No buttons found, window might be closed")
                        break
                    
                    for i, button in enumerate(buttons):
                        try:
                            if button.is_displayed():
                                text = button.text.strip().lower()
                                logger.debug(f"Button {i}: '{text}'")
                                
                                # Look for "Go back to web" button first (most important)
                                if 'go back to web' in text:
                                    try:
                                        button.click()
                                        logger.info(f"Clicked 'Go back to web' button: '{button.text}'")
                                        time.sleep(3)
                                        return  # Exit after successful click
                                    except:
                                        try:
                                            self.driver.execute_script("arguments[0].click();", button)
                                            logger.info(f"JavaScript clicked 'Go back to web' button: '{button.text}'")
                                            time.sleep(3)
                                            return
                                        except:
                                            continue
                                # Look for cookie consent buttons
                                elif any(word in text for word in ['accept all', 'accept', 'reject all', 'reject']):
                                    try:
                                        button.click()
                                        logger.info(f"Clicked consent button: '{button.text}'")
                                        time.sleep(3)
                                        return  # Exit after successful click
                                    except:
                                        try:
                                            self.driver.execute_script("arguments[0].click();", button)
                                            logger.info(f"JavaScript clicked consent button: '{button.text}'")
                                            time.sleep(3)
                                            return
                                        except:
                                            continue
                                # Look for other upgrade popup buttons (but not "Continue" as it closes the window)
                                elif any(word in text for word in ['upgrade']) and 'continue' not in text:
                                    try:
                                        button.click()
                                        logger.info(f"Clicked upgrade popup button: '{button.text}'")
                                        time.sleep(3)
                                        return
                                    except:
                                        try:
                                            self.driver.execute_script("arguments[0].click();", button)
                                            logger.info(f"JavaScript clicked upgrade popup button: '{button.text}'")
                                            time.sleep(3)
                                            return
                                        except:
                                            continue
                        except Exception as e:
                            logger.debug(f"Error processing button {i}: {e}")
                            continue
                    
                    # Method 2: Use JavaScript to find and click buttons
                    js_script = """
                    var buttons = document.querySelectorAll('button');
                    var clicked = false;
                    for (var i = 0; i < buttons.length; i++) {
                        var button = buttons[i];
                        var text = button.textContent.toLowerCase();
                        // Prioritize "Go back to web" first
                        if (text.includes('go back to web')) {
                            button.click();
                            clicked = true;
                            return 'clicked: ' + button.textContent;
                        }
                    }
                    // Then try other buttons
                    for (var i = 0; i < buttons.length; i++) {
                        var button = buttons[i];
                        var text = button.textContent.toLowerCase();
                        if (text.includes('accept all') || text.includes('accept') || 
                            text.includes('reject all') || text.includes('reject') ||
                            (text.includes('upgrade') && !text.includes('continue'))) {
                            button.click();
                            clicked = true;
                            return 'clicked: ' + button.textContent;
                        }
                    }
                    return 'no popup button found';
                    """
                    result = self.driver.execute_script(js_script)
                    if 'clicked' in result:
                        logger.info(f"JavaScript found and clicked popup button: {result}")
                        time.sleep(3)
                        return
                    
                    # Method 3: Look for specific CSS selectors
                    popup_selectors = [
                        "button[aria-label*='Accept all']",
                        "button[aria-label*='Accept']",
                        "button[aria-label*='Reject all']",
                        "button[aria-label*='Reject']",
                        "button[aria-label*='Go back to web']",
                        "button[aria-label*='Continue']",
                        "button:contains('Accept all')",
                        "button:contains('Accept')",
                        "button:contains('Reject all')",
                        "button:contains('Reject')",
                        "button:contains('Go back to web')",
                        "button:contains('Continue')",
                        ".VfPpkd-LgbsSe[aria-label*='Accept all']",
                        ".VfPpkd-LgbsSe[aria-label*='Accept']",
                        ".VfPpkd-LgbsSe[aria-label*='Reject all']",
                        ".VfPpkd-LgbsSe[aria-label*='Reject']"
                    ]
                    
                    for selector in popup_selectors:
                        try:
                            button = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if button.is_displayed():
                                button.click()
                                logger.info(f"Clicked popup using selector: {selector}")
                                time.sleep(3)
                                return
                        except:
                            continue
                    
                    # Method 4: Look for specific text patterns in buttons
                    try:
                        for button in buttons:
                            if button.is_displayed():
                                text = button.text.strip().lower()
                                # Look for any button that might dismiss popups
                                if any(word in text for word in ['go back', 'back to web', 'dismiss', 'close', 'skip', 'no thanks']):
                                    button.click()
                                    logger.info(f"Clicked dismiss button: '{button.text}'")
                                    time.sleep(3)
                                    return
                    except:
                        pass
                    
                    # Method 5: Only click first button as last resort if it looks like a popup button
                    try:
                        visible_buttons = [b for b in buttons if b.is_displayed()]
                        if visible_buttons:
                            first_button = visible_buttons[0]
                            first_text = first_button.text.strip().lower()
                            # Only click if it looks like a popup button
                            if any(word in first_text for word in ['accept', 'reject', 'continue', 'go back', 'dismiss', 'close', 'ok', 'yes', 'no']):
                                first_button.click()
                                logger.info(f"Clicked first visible popup button: '{first_button.text}'")
                                time.sleep(3)
                                return
                            else:
                                logger.info(f"Skipping first button (not a popup button): '{first_button.text}'")
                    except:
                        pass
                    
                    # Wait a bit before trying again
                    time.sleep(2)
                    
                except Exception as e:
                    logger.debug(f"Attempt {attempt + 1} failed: {e}")
                    continue
                
        except Exception as e:
            logger.warning(f"Could not handle popups: {e}")
    
    def _handle_popups_simple(self):
        """Handle popups with a simpler, more robust approach"""
        try:
            time.sleep(3)
            
            # Try to click any visible button that might be a popup
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
                    # Handle popups before scrolling
                    self._handle_cookie_consent()
                    
                    results_panel = self.driver.find_element(By.CSS_SELECTOR, "[role='main']")
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 1000", results_panel)
                    time.sleep(2)
                except:
                    break
            
            # Wait for results to load
            time.sleep(3)
            
        except TimeoutException:
            logger.warning("Timeout waiting for results")
    
    def _find_business_elements(self):
        """Find business elements using improved method"""
        business_elements = []
        
        # Strategy 1: Look for elements with business-like text
        try:
            all_elements = self.driver.find_elements(By.CSS_SELECTOR, "*")
            for element in all_elements:
                try:
                    if element.is_displayed():
                        text = element.text.strip()
                        if (text and len(text) > 5 and len(text) < 100 and 
                            not any(word in text.lower() for word in ['price', 'rating', 'cuisine', 'hours', 'all filters', 'show results', 'directions', 'save', 'share', 'sign in', 'delivery', 'open', 'closes']) and
                            any(char.isalpha() for char in text) and  # Contains letters
                            not text.startswith('"') and  # Not a review quote
                            not text.startswith('⋅') and  # Not a time/status
                            not text.startswith('·')):  # Not an address marker
                            business_elements.append(element)
                except:
                    continue
        except:
            pass
        
        # Strategy 2: Look for specific selectors
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
    
    def _extract_all_text_data(self):
        """Extract all text data from the page"""
        all_text_data = []
        
        try:
            # Get all elements with text
            elements = self.driver.find_elements(By.CSS_SELECTOR, "*")
            
            for element in elements:
                try:
                    if element.is_displayed():
                        text = element.text.strip()
                        if text and len(text) > 2:
                            # Get element info
                            tag = element.tag_name
                            classes = element.get_attribute('class') or ''
                            element_id = element.get_attribute('id') or ''
                            
                            all_text_data.append({
                                'text': text,
                                'tag': tag,
                                'classes': classes,
                                'id': element_id,
                                'element': element
                            })
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting text data: {e}")
        
        logger.info(f"Extracted {len(all_text_data)} text elements")
        return all_text_data
    
    def _parse_text_to_businesses(self, all_text_data):
        """Parse all text data to find businesses"""
        businesses = []
        seen_names = set()
        
        # Group text by proximity and context
        business_groups = self._group_text_by_context(all_text_data)
        
        for group in business_groups:
            business_data = self._extract_business_from_group(group)
            if business_data and business_data.get('name') and business_data['name'] not in seen_names:
                businesses.append(business_data)
                seen_names.add(business_data['name'])
                logger.info(f"Parsed business: {business_data['name']}")
        
        return businesses
    
    def _group_text_by_context(self, all_text_data):
        """Group text elements by context to form business entries"""
        groups = []
        current_group = []
        
        # Sort by position (approximate)
        sorted_data = sorted(all_text_data, key=lambda x: self._get_element_position(x['element']))
        
        for item in sorted_data:
            text = item['text']
            
            # Skip obvious UI elements
            if self._is_ui_element(text):
                if current_group:
                    groups.append(current_group)
                    current_group = []
                continue
            
            # If this looks like a business name, start a new group
            if self._looks_like_business_name(text):
                if current_group:
                    groups.append(current_group)
                current_group = [item]
            else:
                # Add to current group
                current_group.append(item)
        
        # Add the last group
        if current_group:
            groups.append(current_group)
        
        # Filter groups to only include those with business names
        business_groups = []
        for group in groups:
            if any(self._looks_like_business_name(item['text']) for item in group):
                business_groups.append(group)
        
        logger.info(f"Created {len(business_groups)} business groups from {len(groups)} total groups")
        return business_groups
    
    def _is_ui_element(self, text):
        """Check if text is a UI element"""
        ui_indicators = [
            'price', 'rating', 'cuisine', 'hours', 'all filters', 'show results',
            'directions', 'save', 'share', 'more', 'less', 'view all', 'see all',
            'search', 'filter', 'sort', 'map', 'satellite', 'terrain',
            'traffic', 'transit', 'bicycling', 'street view', 'photos',
            'reviews', 'about', 'menu', 'order online', 'call', 'website',
            'sign in', 'delivery', 'open', 'closes', '⋅', '·', '"', '★',
            'reserve a table', 'dine-in', 'sponsored', 'recents', 'back to top',
            'get app', 'layers', 'privacy', 'send product feedback', 'united kingdom'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in ui_indicators) or len(text) < 3
    
    def _looks_like_business_name(self, text):
        """Check if text looks like a business name"""
        if not text or len(text) < 3 or len(text) > 100:
            return False
        
        # Skip if it's clearly not a business name
        if self._is_ui_element(text):
            return False
        
        # Skip if it starts with common non-business indicators
        if text.startswith(('⋅', '·', '"', '★', 'Open', 'Closes', 'Delivery', 'Reserve', 'Dine-in')):
            return False
        
        # Must contain letters
        if not any(char.isalpha() for char in text):
            return False
        
        # Check for business-like patterns
        business_indicators = [
            'restaurant', 'cafe', 'bar', 'pub', 'hotel', 'shop', 'store',
            'garage', 'clinic', 'salon', 'spa', 'gym', 'fitness', 'beauty',
            'automotive', 'repair', 'service', 'center', 'centre', 'ltd',
            'limited', 'inc', 'corp', 'company', 'co', 'group', 'plc',
            'table', 'kitchen', 'tavern', 'chophouse', 'eatery', 'dining'
        ]
        
        text_lower = text.lower()
        has_business_indicator = any(indicator in text_lower for indicator in business_indicators)
        
        # Either has business indicators or is a reasonable length with letters
        return has_business_indicator or (len(text) > 5 and len(text) < 50)
    
    def _get_element_position(self, element):
        """Get approximate position of element"""
        try:
            location = element.location
            return location['y'] * 1000 + location['x']  # Weight y more than x
        except:
            return 0
    
    def _extract_business_from_group(self, group):
        """Extract business data from a group of text elements"""
        business_data = {}
        
        # Find the business name (usually the first or most prominent text)
        business_name = None
        for item in group:
            if self._looks_like_business_name(item['text']):
                business_name = item['text']
                break
        
        if not business_name:
            return None
        
        business_data['name'] = business_name
        
        # Extract other information from the group
        all_text = ' '.join([item['text'] for item in group])
        
        # Look for rating
        rating_match = re.search(r'(\d+\.?\d*)\s*★', all_text)
        if not rating_match:
            rating_match = re.search(r'(\d+\.?\d*)\s*\*', all_text)
        if rating_match:
            try:
                business_data['google_rating'] = float(rating_match.group(1))
            except:
                pass
        
        # Look for address
        address_patterns = [
            r'\d+\s+[A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Way|Close|Drive|Dr|Place|Pl)',
            r'[A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Way|Close|Drive|Dr|Place|Pl)',
        ]
        
        for pattern in address_patterns:
            address_match = re.search(pattern, all_text)
            if address_match:
                business_data['address'] = address_match.group(0).strip()
                break
        
        # Look for phone number
        phone_match = re.search(r'(\+?[\d\s\-\(\)]{10,})', all_text)
        if phone_match:
            phone = phone_match.group(1).strip()
            if len(phone) >= 10:
                business_data['phone'] = phone
        
        # Look for website
        website_match = re.search(r'(https?://[^\s]+)', all_text)
        if website_match:
            business_data['website'] = website_match.group(1)
        
        # Generate place_id
        business_data['place_id'] = f"comp_{hash(business_name) % 100000}"
        
        return business_data
    
    def _extract_detailed_info(self, business_data: Dict[str, Any]):
        """Extract detailed business information from the detailed view"""
        try:
            # Extract rating
            try:
                rating_element = self.driver.find_element(By.CSS_SELECTOR, "[data-value='Ratings']")
                rating_text = rating_element.text
                if rating_text and rating_text.replace('.', '').isdigit():
                    business_data['google_rating'] = float(rating_text)
            except:
                pass
            
            # Extract address
            try:
                address_element = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='address']")
                business_data['address'] = address_element.text
            except:
                pass
            
            # Extract phone
            try:
                phone_element = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='phone']")
                business_data['phone'] = phone_element.text
            except:
                pass
            
            # Extract website
            try:
                website_element = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='authority']")
                business_data['website'] = website_element.get_attribute('href')
            except:
                pass
                
        except Exception as e:
            logger.debug(f"Could not extract detailed info: {e}")
        
    def search_businesses(self, query: str, location: str) -> List[Dict[str, Any]]:
        """Search for businesses using comprehensive text extraction approach"""
        if not self.driver:
            self.setup_driver()
        
        # Check if driver session is still valid
        try:
            self.driver.current_url
        except Exception:
            logger.warning("Driver session invalid, recreating...")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            self.driver = None
            self.setup_driver()
            
        # Clean and format the search query
        clean_query = query.strip().replace(' ', '+')
        clean_location = location.strip().replace(' ', '+')
        search_url = f"https://www.google.com/maps/search/{clean_query}+{clean_location}"
        logger.info(f"Searching: {query} in {location}")
        
        try:
            self.driver.get(search_url)
            time.sleep(10)  # Wait for page to load
            
            # Handle popups with timeout
            start_time = time.time()
            max_popup_time = 60  # Maximum 60 seconds for popup handling
            
            while time.time() - start_time < max_popup_time:
                try:
                    current_url = self.driver.current_url
                    if 'google.com/maps' in current_url:
                        # We're on Google Maps, try to handle any remaining popups
                        self._handle_cookie_consent()
                        time.sleep(2)
                        
                        # Check if we can see search results
                        try:
                            results = self.driver.find_elements(By.CSS_SELECTOR, "[role='main']")
                            if results:
                                logger.info("Found search results, popup handling complete")
                                break
                        except:
                            pass
                    else:
                        logger.warning(f"Redirected away from Google Maps: {current_url}")
                        self.driver.get(search_url)
                        time.sleep(5)
                except Exception as e:
                    logger.warning(f"Error during popup handling: {e}")
                    break
            
            # Wait for results and scroll to load more
            self._wait_and_scroll_for_results()
            
            # Extract all text data from the page
            all_text_data = self._extract_all_text_data()
            
            # Parse the text data to find businesses
            businesses = self._parse_text_to_businesses(all_text_data)
            
            logger.info(f"Found {len(businesses)} businesses for query: {query} in {location}")
            return businesses
            
        except TimeoutException:
            logger.error(f"Timeout waiting for results: {query} in {location}")
            return []
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
            
    def _scroll_results(self):
        """Scroll through results to load more businesses"""
        try:
            results_panel = self.driver.find_element(By.CSS_SELECTOR, "[role='main']")
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", results_panel)
            
            scroll_attempts = 0
            max_scrolls = 10
            
            while scroll_attempts < max_scrolls:
                # Scroll down
                self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", results_panel)
                time.sleep(random.uniform(2, 4))
                
                new_height = self.driver.execute_script("return arguments[0].scrollHeight", results_panel)
                
                if new_height == last_height:
                    break
                    
                last_height = new_height
                scroll_attempts += 1
                
        except Exception as e:
            logger.warning(f"Error during scrolling: {e}")
            
    def _extract_business_data(self, element) -> Optional[Dict[str, Any]]:
        """Extract business data from a search result element"""
        try:
            business_data = {}
            
            # Try to extract data directly from the element without clicking
            name = None
            
            # First try to get name from the element itself
            try:
                name = element.text.strip()
                # Filter out common non-business text
                if (name and len(name) > 2 and 
                    name not in ['Results', 'Show results', '', 'Price', 'Rating', 'Cuisine', 'Hours', 'All filters',
                                'Price\nRating\nCuisine\nHours\nAll filters', 'Price\n\nRating\n\nCuisine\n\nHours\n\nAll filters']):
                    business_data['name'] = name
                else:
                    name = None
            except:
                pass
            
            # If no name from element text, try to find child elements
            if not name:
                name_selectors = [
                    "h1", "h2", "h3", "h4",
                    "[data-attrid='title']",
                    ".fontHeadlineSmall",
                    ".fontBodyMedium",
                    ".fontBodyLarge",
                    ".fontTitleMedium",
                    ".fontTitleLarge"
                ]
                
                for selector in name_selectors:
                    try:
                        name_element = element.find_element(By.CSS_SELECTOR, selector)
                        name = name_element.text.strip()
                        if name and len(name) > 2:
                            business_data['name'] = name
                            break
                    except:
                        continue
            
            if not name or len(name) < 3:
                logger.warning("Could not extract business name")
                return None
                
            # Try to click for more details (optional)
            try:
                element.click()
                time.sleep(random.uniform(1, 2))
                
                # Extract additional details from the detailed view
                self._extract_detailed_info(business_data)
                
            except Exception as e:
                logger.debug(f"Could not click for details: {e}")
                # Continue with basic info only
                
            # Extract rating
            try:
                rating_element = self.driver.find_element(By.CSS_SELECTOR, "[data-value='Ratings']")
                rating_text = rating_element.text
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    business_data['rating'] = float(rating_match.group(1))
            except (NoSuchElementException, ValueError):
                business_data['rating'] = None
                
            # Extract review count
            try:
                review_element = self.driver.find_element(By.CSS_SELECTOR, "[data-value='Reviews']")
                review_text = review_element.text
                review_match = re.search(r'(\d+)', review_text.replace(',', ''))
                if review_match:
                    business_data['review_count'] = int(review_match.group(1))
            except (NoSuchElementException, ValueError):
                business_data['review_count'] = None
                
            # Extract address
            try:
                address_button = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='address']")
                business_data['address'] = address_button.get_attribute('aria-label').replace('Address: ', '')
            except NoSuchElementException:
                business_data['address'] = None
                
            # Extract phone
            try:
                phone_button = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id*='phone']")
                business_data['phone'] = phone_button.get_attribute('aria-label').replace('Phone: ', '')
            except NoSuchElementException:
                business_data['phone'] = None
                
            # Extract website
            try:
                website_button = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='authority']")
                business_data['website'] = website_button.get_attribute('href')
            except NoSuchElementException:
                business_data['website'] = None
                
            # Extract place ID from URL
            try:
                current_url = self.driver.current_url
                place_id_match = re.search(r'place/([^/]+)', current_url)
                if place_id_match:
                    business_data['place_id'] = place_id_match.group(1)
            except Exception:
                business_data['place_id'] = None
                
            # Extract coordinates
            try:
                coords_match = re.search(r'@(-?\d+\.?\d*),(-?\d+\.?\d*)', self.driver.current_url)
                if coords_match:
                    business_data['latitude'] = float(coords_match.group(1))
                    business_data['longitude'] = float(coords_match.group(2))
            except (ValueError, AttributeError):
                business_data['latitude'] = None
                business_data['longitude'] = None
                
            # Extract opening hours
            business_data['opening_hours'] = self._extract_opening_hours()
            
            return business_data
            
        except Exception as e:
            logger.warning(f"Error extracting business data: {e}")
            return None
            
    def _extract_opening_hours(self) -> Optional[Dict[str, str]]:
        """Extract opening hours information"""
        try:
            hours_button = self.driver.find_element(By.CSS_SELECTOR, "[data-item-id='oh']")
            hours_button.click()
            time.sleep(1)
            
            hours_elements = self.driver.find_elements(By.CSS_SELECTOR, "[role='table'] tr")
            hours_dict = {}
            
            for hour_element in hours_elements:
                day_cell = hour_element.find_element(By.TAG_NAME, "td")
                time_cell = hour_element.find_elements(By.TAG_NAME, "td")[1] if len(hour_element.find_elements(By.TAG_NAME, "td")) > 1 else None
                
                if day_cell and time_cell:
                    day = day_cell.text
                    time_text = time_cell.text
                    hours_dict[day] = time_text
                    
            return hours_dict if hours_dict else None
            
        except Exception:
            return None
            
    def get_business_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed business information using place ID"""
        try:
            detail_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
            self.driver.get(detail_url)
            time.sleep(random.uniform(2, 4))
            
            return self._extract_detailed_info()
            
        except Exception as e:
            logger.error(f"Error getting business details for place_id {place_id}: {e}")
            return None
            
        
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser driver closed")
            
    async def scrape_industry(self, industry: str, locations: List[str]) -> List[Dict[str, Any]]:
        """Scrape all businesses for a specific industry across multiple locations"""
        all_businesses = []
        industry_config = Config.INDUSTRIES.get(industry, {})
        search_terms = industry_config.get('search_terms', [industry])
        
        for location in locations:
            for search_term in search_terms:
                try:
                    businesses = self.search_businesses(search_term, location)
                    
                    # Filter out excluded terms
                    exclude_terms = industry_config.get('exclude_terms', [])
                    filtered_businesses = []
                    
                    for business in businesses:
                        business_name = business.get('name', '').lower()
                        if not any(exclude_term.lower() in business_name for exclude_term in exclude_terms):
                            business['industry'] = industry
                            business['search_term'] = search_term
                            business['search_location'] = location
                            filtered_businesses.append(business)
                    
                    all_businesses.extend(filtered_businesses)
                    
                    # Random delay between searches
                    await asyncio.sleep(random.uniform(Config.SCRAPING_DELAY_MIN, Config.SCRAPING_DELAY_MAX))
                    
                except Exception as e:
                    logger.error(f"Error scraping {search_term} in {location}: {e}")
                    continue
                    
        logger.info(f"Total businesses found for {industry}: {len(all_businesses)}")
        return all_businesses
