import asyncio
import aiohttp
import re
from typing import List, Dict, Any, Optional
from loguru import logger
from ratelimit import limits, sleep_and_retry
from backoff import on_exception, expo
from config import Config

class CompaniesHouseAPI:
    def __init__(self):
        self.base_url = "https://api.company-information.service.gov.uk"
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Basic {Config.COMPANIES_HOUSE_API_KEY}:",
                "Content-Type": "application/json"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    @sleep_and_retry
    @limits(calls=600, period=300)  # 600 calls per 5 minutes (API limit)
    async def search_companies(self, query: str, items_per_page: int = 20) -> List[Dict[str, Any]]:
        """Search for companies by name"""
        try:
            url = f"{self.base_url}/search/companies"
            params = {
                "q": query,
                "items_per_page": items_per_page
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("items", [])
                elif response.status == 429:
                    logger.warning("Rate limit hit, waiting...")
                    await asyncio.sleep(60)
                    return await self.search_companies(query, items_per_page)
                else:
                    logger.error(f"Companies House search failed: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching companies: {e}")
            return []
            
    @sleep_and_retry
    @limits(calls=600, period=300)
    async def get_company_details(self, company_number: str) -> Optional[Dict[str, Any]]:
        """Get detailed company information"""
        try:
            url = f"{self.base_url}/company/{company_number}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    logger.warning("Rate limit hit, waiting...")
                    await asyncio.sleep(60)
                    return await self.get_company_details(company_number)
                else:
                    logger.error(f"Company details fetch failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting company details: {e}")
            return None
            
    @sleep_and_retry
    @limits(calls=600, period=300)
    async def get_company_officers(self, company_number: str) -> List[Dict[str, Any]]:
        """Get company officers"""
        try:
            url = f"{self.base_url}/company/{company_number}/officers"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("items", [])
                else:
                    logger.error(f"Officers fetch failed: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting company officers: {e}")
            return []
            
    async def find_matching_company(self, business_name: str, postcode: str = None) -> Optional[Dict[str, Any]]:
        """Find the best matching company for a business"""
        # Clean business name for search
        cleaned_name = self._clean_business_name(business_name)
        
        # Search for companies
        companies = await self.search_companies(cleaned_name)
        
        if not companies:
            return None
            
        # Score and rank matches
        best_match = self._find_best_match(business_name, companies, postcode)
        
        if best_match:
            # Get detailed information
            company_details = await self.get_company_details(best_match["company_number"])
            if company_details:
                return {
                    **best_match,
                    **company_details,
                    "match_score": best_match.get("match_score", 0)
                }
                
        return None
        
    def _clean_business_name(self, name: str) -> str:
        """Clean business name for better search results"""
        # Remove common business suffixes/prefixes
        suffixes_to_remove = [
            r'\s+ltd\.?$', r'\s+limited$', r'\s+plc$', r'\s+llp$', 
            r'\s+partnership$', r'\s+& co\.?$', r'\s+inc\.?$',
            r'\s+restaurant$', r'\s+cafe$', r'\s+shop$', r'\s+store$'
        ]
        
        cleaned = name.lower()
        for suffix in suffixes_to_remove:
            cleaned = re.sub(suffix, '', cleaned, flags=re.IGNORECASE)
            
        # Remove special characters
        cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
        
    def _find_best_match(self, business_name: str, companies: List[Dict], postcode: str = None) -> Optional[Dict[str, Any]]:
        """Find the best matching company from search results"""
        if not companies:
            return None
            
        scored_companies = []
        business_name_lower = business_name.lower()
        
        for company in companies:
            company_name = company.get("title", "").lower()
            address = company.get("address_snippet", "").lower()
            
            # Calculate name similarity score
            name_score = self._calculate_similarity(business_name_lower, company_name)
            
            # Bonus for postcode match
            postcode_score = 0
            if postcode and postcode.lower().replace(" ", "") in address.replace(" ", ""):
                postcode_score = 0.3
                
            # Penalty for dissolved companies
            status_penalty = 0
            if company.get("company_status") == "dissolved":
                status_penalty = -0.5
                
            total_score = name_score + postcode_score + status_penalty
            
            scored_companies.append({
                **company,
                "match_score": total_score
            })
            
        # Sort by score and return best match if score is good enough
        scored_companies.sort(key=lambda x: x["match_score"], reverse=True)
        
        if scored_companies and scored_companies[0]["match_score"] > 0.6:
            return scored_companies[0]
            
        return None
        
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using Jaccard similarity"""
        set1 = set(str1.split())
        set2 = set(str2.split())
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        if len(union) == 0:
            return 0.0
            
        return len(intersection) / len(union)
        
    async def bulk_verify_businesses(self, businesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Verify multiple businesses against Companies House"""
        verified_businesses = []
        
        for business in businesses:
            try:
                business_name = business.get("name")
                postcode = self._extract_postcode(business.get("address", ""))
                
                if not business_name:
                    continue
                    
                company_match = await self.find_matching_company(business_name, postcode)
                
                if company_match:
                    business.update({
                        "companies_house_number": company_match.get("company_number"),
                        "companies_house_status": company_match.get("company_status"),
                        "incorporation_date": company_match.get("date_of_creation"),
                        "sic_codes": [sic.get("code") for sic in company_match.get("sic_codes", [])],
                        "company_type": company_match.get("type"),
                        "match_score": company_match.get("match_score")
                    })
                    
                verified_businesses.append(business)
                
                # Rate limiting delay
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error verifying business {business.get('name')}: {e}")
                verified_businesses.append(business)
                continue
                
        return verified_businesses
        
    def _extract_postcode(self, address: str) -> Optional[str]:
        """Extract UK postcode from address"""
        if not address:
            return None
            
        # UK postcode regex
        postcode_pattern = r'([A-Z]{1,2}[0-9R][0-9A-Z]?\s*[0-9][A-Z]{2})'
        match = re.search(postcode_pattern, address.upper())
        
        return match.group(1) if match else None
        
    async def discover_companies_by_sic(self, sic_codes: List[str], location: str = None) -> List[Dict[str, Any]]:
        """Discover companies by SIC codes (this would require additional API endpoints or web scraping)"""
        # Note: Companies House API doesn't directly support SIC code search
        # This would need to be implemented using their bulk data downloads
        # or additional web scraping of Companies House website
        
        logger.info(f"SIC code discovery not implemented in basic API - would require bulk data processing")
        return []
