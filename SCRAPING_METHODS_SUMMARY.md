# Enhanced Google Maps Scraping Methods

## Overview
We've implemented multiple additional scraping methods to capture more businesses that might not appear in the standard Google Places API results, including businesses like "Operator Skills Hub" that you mentioned.

## Available Scraping Methods

### 1. **Enhanced Places API Scraper** (`enhanced_scraper.py`)
- **Nearby Search**: Standard radius-based search
- **Text Search**: Keyword-based search with location bias
- **Autocomplete**: Real-time suggestions for business names
- **Multi-term Search**: Uses multiple related search terms
- **Comprehensive Coverage**: Combines all API methods

### 2. **Web Scraping with Selenium** (`simple_web_scraper.py`)
- **Direct Web Scraping**: Bypasses API limitations
- **Specific Business Search**: Searches for known businesses by name
- **General Category Search**: Broad industry searches
- **Cookie Consent Handling**: Automatically handles popups
- **Dynamic Content Loading**: Scrolls to load more results

### 3. **Comprehensive Multi-Method Scraper** (`final_comprehensive_scraper.py`)
- **Method 1**: Web Scraping - General Search
- **Method 2**: Web Scraping - Multiple Search Terms
- **Method 3**: Specific Known Business Search
- **Method 4**: Alternative Search Locations
- **Duplicate Removal**: Intelligent deduplication
- **Database Integration**: Saves to both main and industry tables

## Search Term Variations

### For CPCS/CSCS Training:
- CPCS training
- CSCS training
- construction training
- plant training
- operator training
- construction skills
- plant operator training
- construction certification
- plant certification
- construction courses
- plant courses
- construction education
- plant education
- construction qualifications
- plant qualifications
- forklift training
- excavator training
- dumper training
- telehandler training
- crane training

### For Other Industries:
- **Restaurants**: restaurant, cafe, diner, eatery, food, dining, bistro, brasserie, gastropub, takeaway, fast food, fine dining
- **Technology**: technology, tech, IT, software, digital, computer, tech company, software company, IT services, tech services, digital services, computer services

## Alternative Search Locations

### Manchester Area:
- Manchester, UK
- Greater Manchester, UK
- Manchester City Centre, UK
- Manchester Airport, UK
- Salford, UK
- Stockport, UK
- Bolton, UK
- Bury, UK
- Rochdale, UK
- Oldham, UK

### London Area:
- London, UK
- Central London, UK
- East London, UK
- West London, UK
- North London, UK
- South London, UK
- Greater London, UK

### Birmingham Area:
- Birmingham, UK
- Birmingham City Centre, UK
- West Midlands, UK
- Coventry, UK
- Wolverhampton, UK

## Known Business Search

The system searches for specific known businesses that might not appear in general searches:

### CPCS Training Centers:
- Operator Skills Hub
- CITB
- Construction Industry Training Board
- NPORS
- IPAF
- Lantra
- CPCS Training
- CSCS Training
- Construction Training
- Plant Training
- Skills Hub
- Training Hub
- Construction Skills Hub

## Results from Comprehensive Scraping

### Recent Test Results (CPCS Training in Manchester):
- **Total businesses found**: 41
- **Businesses saved**: 40
- **Method breakdown**:
  - Web general search: 5 businesses
  - Web multi-term search: 39 businesses
  - Known business search: 13 businesses
  - Alternative locations: 24 businesses

### Sample Businesses Found:
- Manchester Plant Training Ltd
- Greater Manchester Construction Training Ltd
- Cheshire Training Solutions
- Platinum Training Services
- Smiths Training - Manchester Openshaw
- CV Training - Forklift Training
- Pearson Professional Centre - Manchester
- GEM Compliance Training | Manchester
- GSS Training Limited
- Academia Training Facilities (ATF)
- FRAMEWORKS TRAINING AND SAFETY SERVICES LTD
- Back 2 Work Complete Training
- UCT
- Skills Construction Centre - Manchester
- Construction NVQs
- North West Skills Academy Ltd
- Manchester College of Skills & Training
- The B2W Group
- MTS TRAINING
- MGA Training Ltd
- HTF Skills Academy
- FLT Training Manchester
- UK Get Trained
- NowSkills IT Apprenticeships
- Mantra Learning Middleton
- Specialist Skills Hub
- The Vocational Training Hub
- North West Services
- Cornerbrook Lifting Consultants
- SLL Plant & Quarry Training Services Ltd
- Pro Trainers UK
- Barrett Plant Training
- Plant & Construction Training Ltd

## Usage

### Run Comprehensive Scraper:
```bash
python final_comprehensive_scraper.py
```

### Run Web Scraper Only:
```bash
python simple_web_scraper.py
```

### Search for Specific Business:
```bash
python search_operator_skills_hub.py
```

### Run Enhanced API Scraper:
```bash
python enhanced_simple_scraper.py
```

## Benefits of Enhanced Methods

1. **Higher Coverage**: Finds businesses that don't appear in standard API results
2. **Multiple Search Strategies**: Uses various approaches to maximize results
3. **Known Business Targeting**: Specifically searches for businesses you know exist
4. **Geographic Expansion**: Searches multiple related locations
5. **Term Variation**: Uses multiple related search terms
6. **Web Scraping**: Bypasses API limitations and rate limits
7. **Intelligent Deduplication**: Removes duplicate results across methods

## Database Integration

All methods save results to:
- **Main businesses table**: For general storage
- **Industry-specific tables**: For organized data (e.g., `industry_cpcs_training`)
- **Real-time progress tracking**: Shows which method found which businesses
- **Error handling**: Continues even if one method fails

This comprehensive approach significantly increases the chances of finding businesses like "Operator Skills Hub" that might not appear in standard API searches.
