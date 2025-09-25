import re
import json
from typing import List, Dict, Any, Optional
from loguru import logger
import asyncio

class DataProcessor:
    def __init__(self):
        self.duplicate_threshold = 0.8
        
    async def process_businesses(self, businesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and clean business data"""
        logger.info(f"Processing {len(businesses)} businesses")
        
        # 1. Clean individual business records
        cleaned_businesses = []
        for business in businesses:
            cleaned = self._clean_business_record(business)
            if cleaned:
                cleaned_businesses.append(cleaned)
                
        # 2. Remove duplicates
        deduplicated = self._remove_duplicates(cleaned_businesses)
        
        # 3. Validate and enrich data
        validated = []
        for business in deduplicated:
            if self._validate_business_record(business):
                enriched = await self._enrich_business_data(business)
                validated.append(enriched)
                
        logger.info(f"Processed: {len(businesses)} -> {len(validated)} businesses")
        return validated
        
    def _clean_business_record(self, business: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Clean individual business record"""
        try:
            cleaned = {}
            
            # Clean name - handle None values
            name = business.get('name') or ''
            if isinstance(name, str):
                name = name.strip()
            else:
                name = ''
            if not name:
                return None
            cleaned['name'] = self._clean_business_name(name)
            
            # Clean address - handle None values
            address = business.get('address') or ''
            if isinstance(address, str):
                address = address.strip()
            else:
                address = ''
            if address:
                cleaned['address'] = self._clean_address(address)
                cleaned['postcode'] = self._extract_postcode(address)
            
            # Clean phone - handle None values
            phone = business.get('phone') or ''
            if isinstance(phone, str):
                phone = phone.strip()
            else:
                phone = ''
            if phone:
                cleaned['phone'] = self._clean_phone_number(phone)
                
            # Clean website - handle None values
            website = business.get('website') or ''
            if isinstance(website, str):
                website = website.strip()
            else:
                website = ''
            if website:
                cleaned['website'] = self._clean_website_url(website)
                
            # Extract email if present in any field
            email = self._extract_email(business)
            if email:
                cleaned['email'] = email
                
            # Clean ratings
            rating = business.get('rating')
            if rating is not None:
                try:
                    cleaned['google_rating'] = float(rating)
                except (ValueError, TypeError):
                    cleaned['google_rating'] = None
                    
            # Clean review count
            review_count = business.get('review_count')
            if review_count is not None:
                try:
                    cleaned['google_reviews_count'] = int(review_count)
                except (ValueError, TypeError):
                    cleaned['google_reviews_count'] = None
                    
            # Clean coordinates
            lat = business.get('latitude')
            lng = business.get('longitude')
            if lat is not None and lng is not None:
                try:
                    cleaned['latitude'] = float(lat)
                    cleaned['longitude'] = float(lng)
                except (ValueError, TypeError):
                    pass
                    
            # Copy other fields
            for field in ['place_id', 'industry', 'search_term', 'search_location', 'opening_hours']:
                if field in business and business[field] is not None:
                    cleaned[field] = business[field]
                    
            # Set google_place_id
            cleaned['google_place_id'] = business.get('place_id')
            
            return cleaned
            
        except Exception as e:
            logger.warning(f"Error cleaning business record: {e}")
            return None
            
    def _clean_business_name(self, name: str) -> str:
        """Clean business name"""
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove common unwanted characters at the end
        name = re.sub(r'[·•\-\s]+$', '', name)
        
        # Title case for better consistency
        return name.title()
        
    def _clean_address(self, address: str) -> str:
        """Clean address"""
        # Remove extra whitespace and normalize
        address = re.sub(r'\s+', ' ', address).strip()
        
        # Remove "Address: " prefix if present
        address = re.sub(r'^Address:\s*', '', address, flags=re.IGNORECASE)
        
        return address
        
    def _extract_postcode(self, address: str) -> Optional[str]:
        """Extract UK postcode from address"""
        if not address or not isinstance(address, str):
            return None
            
        # UK postcode pattern
        postcode_pattern = r'([A-Z]{1,2}[0-9R][0-9A-Z]?\s*[0-9][A-Z]{2})'
        match = re.search(postcode_pattern, address.upper())
        
        if match:
            postcode = match.group(1)
            if postcode and isinstance(postcode, str):
                # Format with space
                if len(postcode.replace(' ', '')) > 3:
                    postcode = postcode.replace(' ', '')
                    postcode = postcode[:-3] + ' ' + postcode[-3:]
                return postcode
            
        return None
        
    def _clean_phone_number(self, phone: str) -> str:
        """Clean phone number"""
        if not phone or not isinstance(phone, str):
            return ''
            
        # Remove "Phone: " prefix
        phone = re.sub(r'^Phone:\s*', '', phone, flags=re.IGNORECASE)
        
        # Remove extra spaces and normalize
        phone = re.sub(r'\s+', ' ', phone).strip()
        
        # UK phone number formatting
        phone = re.sub(r'[^\d\+\s\(\)\-]', '', phone)
        
        return phone
        
    def _clean_website_url(self, website: str) -> str:
        """Clean website URL"""
        if not website or not isinstance(website, str):
            return ''
            
        website = website.strip()
        
        # Add protocol if missing
        if website and not website.startswith(('http://', 'https://')):
            website = 'https://' + website
            
        # Remove query parameters and fragments for cleaner URLs
        website = re.sub(r'[?#].*$', '', website)
        
        return website
        
    def _extract_email(self, business: Dict[str, Any]) -> Optional[str]:
        """Extract email from any business field"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Check all text fields for email
        text_fields = ['name', 'address', 'phone', 'website']
        for field in text_fields:
            value = business.get(field, '')
            if isinstance(value, str):
                match = re.search(email_pattern, value)
                if match:
                    return match.group(0).lower()
                    
        return None
        
    def _remove_duplicates(self, businesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate businesses based on similarity"""
        unique_businesses = []
        seen_signatures = set()
        
        for business in businesses:
            # Create signature for duplicate detection
            signature = self._create_business_signature(business)
            
            if signature not in seen_signatures:
                # Check for similar businesses
                is_duplicate = False
                for existing in unique_businesses:
                    if self._are_similar_businesses(business, existing):
                        is_duplicate = True
                        break
                        
                if not is_duplicate:
                    unique_businesses.append(business)
                    seen_signatures.add(signature)
                    
        logger.info(f"Duplicate removal: {len(businesses)} -> {len(unique_businesses)}")
        return unique_businesses
        
    def _create_business_signature(self, business: Dict[str, Any]) -> str:
        """Create a signature for duplicate detection"""
        name = business.get('name') or ''
        if isinstance(name, str):
            name = name.lower()
        else:
            name = ''
            
        postcode = business.get('postcode') or ''
        if isinstance(postcode, str):
            postcode = postcode.replace(' ', '').lower()
        else:
            postcode = ''
        
        # Remove common business words for better matching
        name_words = re.sub(r'\b(ltd|limited|plc|llp|restaurant|cafe|shop|store)\b', '', name)
        name_clean = re.sub(r'[^\w]', '', name_words)
        
        return f"{name_clean}_{postcode}"
        
    def _are_similar_businesses(self, business1: Dict[str, Any], business2: Dict[str, Any]) -> bool:
        """Check if two businesses are similar (potential duplicates)"""
        # Name similarity
        name1 = business1.get('name') or ''
        name2 = business2.get('name') or ''
        if isinstance(name1, str):
            name1 = name1.lower()
        else:
            name1 = ''
        if isinstance(name2, str):
            name2 = name2.lower()
        else:
            name2 = ''
        name_similarity = self._calculate_similarity(name1, name2)
        
        # Location similarity
        location_similarity = 0
        
        # Same postcode = high location similarity
        postcode1 = business1.get('postcode') or ''
        postcode2 = business2.get('postcode') or ''
        if postcode1 and postcode2 and postcode1 == postcode2:
            location_similarity = 0.9
            
        # Coordinate similarity
        lat1, lng1 = business1.get('latitude'), business1.get('longitude')
        lat2, lng2 = business2.get('latitude'), business2.get('longitude')
        
        if all([lat1, lng1, lat2, lng2]):
            distance = self._calculate_distance(lat1, lng1, lat2, lng2)
            if distance < 0.1:  # Within 100 meters
                location_similarity = max(location_similarity, 0.8)
                
        # Combined similarity score
        combined_score = (name_similarity * 0.7) + (location_similarity * 0.3)
        
        return combined_score > self.duplicate_threshold
        
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using Jaccard index"""
        if not str1 or not str2:
            return 0.0
            
        set1 = set(str1.split())
        set2 = set(str2.split())
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union) if union else 0.0
        
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates in km"""
        import math
        
        R = 6371  # Earth's radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlng/2) * math.sin(dlng/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
        
    def _validate_business_record(self, business: Dict[str, Any]) -> bool:
        """Validate business record has minimum required data"""
        # Must have name
        if not business.get('name'):
            return False
            
        # Must have some location information
        has_location = any([
            business.get('address'),
            business.get('postcode'),
            (business.get('latitude') and business.get('longitude'))
        ])
        
        if not has_location:
            return False
            
        # Name must be reasonable length
        name = business.get('name', '')
        if len(name) < 2 or len(name) > 200:
            return False
            
        return True
        
    async def _enrich_business_data(self, business: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich business data with additional processing"""
        enriched = business.copy()
        
        # Infer business category from name if not present
        if not enriched.get('category'):
            enriched['category'] = self._infer_business_category(business.get('name', ''))
            
        # Clean and structure opening hours
        opening_hours = business.get('opening_hours')
        if opening_hours:
            enriched['opening_hours'] = self._structure_opening_hours(opening_hours)
            
        # Add data quality score
        enriched['data_quality_score'] = self._calculate_data_quality_score(business)
        
        return enriched
        
    def _infer_business_category(self, name: str) -> Optional[str]:
        """Infer business category from name"""
        name_lower = name.lower()
        
        category_keywords = {
            'restaurant': ['restaurant', 'bistro', 'diner', 'eatery', 'grill'],
            'cafe': ['cafe', 'coffee', 'espresso', 'barista'],
            'retail': ['shop', 'store', 'boutique', 'emporium'],
            'healthcare': ['clinic', 'medical', 'dental', 'pharmacy', 'doctor'],
            'professional': ['solicitor', 'accountant', 'consultant', 'advisor'],
            'automotive': ['garage', 'motors', 'automotive', 'car']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in name_lower for keyword in keywords):
                return category
                
        return None
        
    def _structure_opening_hours(self, hours_data) -> Optional[Dict[str, str]]:
        """Structure opening hours data"""
        if isinstance(hours_data, dict):
            return hours_data
        elif isinstance(hours_data, str):
            # Parse string format if needed
            return {"raw": hours_data}
        
        return None
        
    def _calculate_data_quality_score(self, business: Dict[str, Any]) -> float:
        """Calculate data quality score (0-1)"""
        score = 0.0
        max_score = 0.0
        
        # Essential fields
        if business.get('name'):
            score += 0.25
        max_score += 0.25
        
        if business.get('address'):
            score += 0.15
        max_score += 0.15
        
        # Contact information (weighted higher for business value)
        if business.get('phone'):
            score += 0.2
        max_score += 0.2
        
        if business.get('website'):
            score += 0.15
        max_score += 0.15
        
        if business.get('email'):
            score += 0.1
        max_score += 0.1
        
        # Location data
        if business.get('latitude') and business.get('longitude'):
            score += 0.05
        max_score += 0.05
        
        # Reviews and ratings
        if business.get('google_rating'):
            score += 0.05
        max_score += 0.05
        
        if business.get('google_reviews_count'):
            score += 0.05
        max_score += 0.05
        
        return score / max_score if max_score > 0 else 0.0
