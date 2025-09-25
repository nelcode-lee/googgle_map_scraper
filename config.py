import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # APIs
    COMPANIES_HOUSE_API_KEY = os.getenv("COMPANIES_HOUSE_API_KEY")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    
    # Scraping settings
    SCRAPING_DELAY_MIN = int(os.getenv("SCRAPING_DELAY_MIN", 1))
    SCRAPING_DELAY_MAX = int(os.getenv("SCRAPING_DELAY_MAX", 3))
    CONCURRENT_REQUESTS = int(os.getenv("CONCURRENT_REQUESTS", 3))
    USER_AGENT_ROTATION = os.getenv("USER_AGENT_ROTATION", "true").lower() == "true"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Industry configurations
    INDUSTRIES = {
        "restaurants": {
            "search_terms": ["restaurant", "cafe", "bistro", "diner", "eatery"],
            "sic_codes": ["56101", "56102", "56103"],
            "exclude_terms": ["fast food", "takeaway"]
        },
        "retail": {
            "search_terms": ["shop", "store", "retail", "boutique"],
            "sic_codes": ["47110", "47190", "47210"],
            "exclude_terms": ["online", "warehouse"]
        },
        "professional_services": {
            "search_terms": ["accountant", "lawyer", "solicitor", "consultant"],
            "sic_codes": ["69201", "69202", "70221"],
            "exclude_terms": []
        },
        "healthcare": {
            "search_terms": ["dentist", "clinic", "medical centre", "pharmacy"],
            "sic_codes": ["86220", "86230", "47730"],
            "exclude_terms": ["NHS", "hospital"]
        }
    }
    
    # Geographic areas for scraping
    LOCATIONS = [
        "London, UK",
        "Manchester, UK", 
        "Birmingham, UK",
        "Leeds, UK",
        "Glasgow, UK",
        "Liverpool, UK",
        "Newcastle, UK",
        "Sheffield, UK",
        "Bristol, UK",
        "Edinburgh, UK"
    ]
