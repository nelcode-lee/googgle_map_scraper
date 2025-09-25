# Quick Start Guide

This guide will get you up and running with the Google Maps Business Scraper in minutes.

## Prerequisites

✅ **Already Set Up:**
- Python 3.13+ 
- Virtual environment (`venv/`)
- All dependencies installed
- Project structure created

## 1. Configure API Keys

Edit the `.env` file with your API credentials:

```bash
# Required: Get your Companies House API key
COMPANIES_HOUSE_API_KEY=your_actual_api_key_here

# Required: Set up your Neon DB connection
DATABASE_URL=postgresql://username:password@hostname:port/database_name

# Optional: Google Maps API key (for enhanced features)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

### Get API Keys:

1. **Companies House API**: 
   - Register at https://developer.company-information.service.gov.uk/
   - Free tier: 600 requests per 5 minutes

2. **Neon Database** [[memory:7111442]]:
   - Sign up at https://neon.tech/
   - Create a PostgreSQL database
   - Copy connection string to .env

## 2. Test the Setup

```bash
# Test configuration
source venv/bin/activate
python -c "import config; print('✅ Configuration loaded')"

# Test database connection (requires valid DATABASE_URL)
python -c "from database import DatabaseManager; print('✅ Database module ready')"
```

## 3. Your First Scrape

```bash
# Activate environment
source venv/bin/activate

# Scrape restaurants in UK cities
python main.py scrape restaurants

# Or use the convenience script
./run.sh scrape restaurants
```

## 4. Available Commands

```bash
# Scrape specific industries
./run.sh scrape restaurants      # Restaurants, cafes, bistros
./run.sh scrape retail          # Shops, stores, boutiques  
./run.sh scrape healthcare      # Clinics, dentists, pharmacies
./run.sh scrape professional_services # Accountants, lawyers, consultants

# Verify existing businesses with Companies House
./run.sh verify

# Generate reports
./run.sh report

# Run examples
python examples.py
```

## 5. What Gets Scraped

For each business, the scraper collects:

**From Google Maps:**
- Business name and address
- Phone number and website
- Google ratings and review count
- Opening hours and location coordinates
- Business category and attributes

**From Companies House:**
- Company registration number
- Company status (active/dissolved)
- SIC codes (business classification)
- Incorporation date
- Director information

## 6. Industry Configurations

Pre-configured industries with optimised search terms:

- **Restaurants**: restaurant, cafe, bistro, diner, eatery
- **Retail**: shop, store, retail, boutique  
- **Healthcare**: dentist, clinic, medical centre, pharmacy
- **Professional Services**: accountant, lawyer, solicitor, consultant

Each industry excludes irrelevant results (e.g., online-only businesses).

## 7. Geographic Coverage

Searches these major UK cities by default:
- London, Manchester, Birmingham, Leeds
- Glasgow, Liverpool, Newcastle, Sheffield
- Bristol, Edinburgh

Modify `Config.LOCATIONS` in `config.py` to target different areas.

## 8. Data Quality Features

- **Duplicate Detection**: Removes similar businesses using name/location matching
- **Data Validation**: Ensures phone numbers, postcodes, websites are properly formatted
- **Quality Scoring**: Each business gets a completeness score (0-1)
- **Address Standardisation**: Consistent postcode extraction and formatting

## 9. Output Formats

Export your data:

```python
# In Python
from utils import ExportUtils
businesses = []  # Your scraped data
ExportUtils.to_csv(businesses, "my_businesses.csv")
ExportUtils.to_json(businesses, "my_businesses.json")
```

## 10. Monitoring & Logs

- Logs saved to `scraper.log`
- Search history tracked in database
- Progress monitoring for long-running scrapes
- Error reporting and rate limit handling

## Common Issues & Solutions

**Import Errors:**
```bash
# If you get module import errors
source venv/bin/activate
pip install setuptools
```

**Chrome Driver Issues:**
- Install Google Chrome browser
- The scraper will download ChromeDriver automatically

**Database Connection:**
- Verify your Neon DB credentials in .env
- Check firewall settings
- Ensure database exists

**Rate Limiting:**
- Companies House: Max 600 requests per 5 minutes
- Increase delays in config.py if needed
- The scraper handles rate limits automatically

## Next Steps

1. **Customise Industries**: Add new business types in `config.py`
2. **Geographic Targeting**: Modify location lists for specific areas
3. **Advanced Queries**: Use the database directly for complex analysis
4. **Automation**: Set up scheduled scraping with cron jobs
5. **Integration**: Connect to your CRM or marketing tools

## Support

- Check `README.md` for detailed documentation
- Run `python examples.py` for usage examples
- Review `config.py` for all configuration options

Happy scraping! 🚀
