# Google Maps Business Scraper with Companies House Integration

A comprehensive business intelligence tool that scrapes Google Maps for business data and cross-references with Companies House to build a verified database of UK businesses across specific industries.

## Features

- **Google Maps Scraping**: Extract detailed business information including contact details, ratings, location data
- **Companies House Integration**: Verify businesses and discover additional companies through official company records
- **Industry-Specific Targeting**: Pre-configured search strategies for different business sectors
- **Duplicate Detection**: Intelligent deduplication using name similarity and location matching
- **Data Quality Scoring**: Assess completeness and reliability of business records
- **Neon DB Storage**: Scalable PostgreSQL database storage optimised for business data
- **Rate Limiting**: Respectful scraping with configurable delays and concurrent request limits
- **Comprehensive Logging**: Detailed logging for monitoring and debugging

## Industry Support

Pre-configured support for:
- Restaurants & Hospitality
- Retail & E-commerce
- Professional Services
- Healthcare & Medical
- Automotive Services

## Installation

1. **Clone and setup**:
```bash
git clone <repository-url>
cd google_maps_scraper
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

3. **Setup database**:
- Create a Neon DB instance
- Update DATABASE_URL in .env
- Tables will be created automatically on first run

## Configuration

### Required API Keys

1. **Companies House API Key**:
   - Register at: https://developer.company-information.service.gov.uk/
   - Add to .env as COMPANIES_HOUSE_API_KEY

2. **Neon DB Connection**:
   - Create account at: https://neon.tech/
   - Add connection string to .env as DATABASE_URL

### Optional Configuration

- `GOOGLE_MAPS_API_KEY`: For enhanced location services (optional)
- `SCRAPING_DELAY_MIN/MAX`: Control scraping speed (default: 1-3 seconds)
- `CONCURRENT_REQUESTS`: Number of parallel requests (default: 3)

## Usage

### Basic Scraping

Scrape all businesses for a specific industry:
```bash
python main.py scrape restaurants
python main.py scrape retail
python main.py scrape professional_services
```

### Companies House Verification

Verify existing businesses against Companies House:
```bash
python main.py verify
```

### Company Discovery

Discover companies that might be missing from Google Maps:
```bash
python main.py discover restaurants
```

### Generate Reports

Generate comprehensive business intelligence reports:
```bash
python main.py report
```

## Database Schema

### businesses table
- Basic business information (name, address, contact)
- Google Maps data (ratings, reviews, place_id)
- Companies House data (company number, status, SIC codes)
- Location data (coordinates, postcode)
- Data quality metrics

### search_history table
- Track scraping activities
- Monitor search performance
- Prevent duplicate searches

### ch_verification_log table
- Companies House verification history
- Track match accuracy
- Store raw company data

## Data Processing Pipeline

1. **Extraction**: Scrape Google Maps using Selenium with stealth techniques
2. **Cleaning**: Normalise addresses, phone numbers, and business names
3. **Deduplication**: Remove duplicates using similarity algorithms
4. **Validation**: Ensure data quality and completeness
5. **Enrichment**: Add business categories and quality scores
6. **Verification**: Cross-reference with Companies House
7. **Storage**: Save to Neon DB with proper indexing

## Advanced Features

### Industry Configuration

Add new industries in `config.py`:
```python
"new_industry": {
    "search_terms": ["term1", "term2"],
    "sic_codes": ["12345", "67890"],
    "exclude_terms": ["unwanted"]
}
```

### Geographic Targeting

Modify `LOCATIONS` in `config.py` to target specific areas:
```python
LOCATIONS = [
    "London, UK",
    "Manchester, UK",
    # Add more locations
]
```

### Rate Limiting

Adjust scraping behaviour:
```python
SCRAPING_DELAY_MIN = 2  # Minimum delay between requests
SCRAPING_DELAY_MAX = 5  # Maximum delay between requests
CONCURRENT_REQUESTS = 2  # Reduce for slower scraping
```

## Data Quality & Accuracy

- **Duplicate Detection**: Jaccard similarity with location verification
- **Name Standardisation**: Consistent business name formatting
- **Address Validation**: UK postcode extraction and validation
- **Contact Verification**: Phone number and website cleaning
- **Match Scoring**: Companies House matches include confidence scores

## Compliance & Ethics

- **Rate Limiting**: Respectful scraping with delays
- **Terms of Service**: Complies with Google Maps usage guidelines
- **Data Protection**: Secure handling of business information
- **API Limits**: Stays within Companies House API quotas

## Monitoring & Logging

- Comprehensive logging with configurable levels
- Search history tracking
- Error monitoring and reporting
- Performance metrics collection

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**:
   - Ensure Chrome is installed
   - Check internet connectivity
   - Verify no VPN conflicts

2. **Database Connection**:
   - Verify Neon DB credentials
   - Check firewall settings
   - Confirm database exists

3. **API Rate Limits**:
   - Companies House: 600 requests per 5 minutes
   - Increase delays if hitting limits

4. **Missing Data**:
   - Some businesses may not have complete information
   - Check data quality scores
   - Verify search terms are appropriate

### Performance Optimisation

- Reduce concurrent requests for slower connections
- Increase delays for more reliable scraping
- Use specific location targeting for focused results
- Regular database maintenance for optimal performance

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure code follows style guidelines
5. Submit pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Disclaimer

This tool is for legitimate business intelligence purposes. Users are responsible for:
- Complying with all applicable laws and regulations
- Respecting website terms of service
- Ensuring appropriate use of collected data
- Maintaining data security and privacy standards

## Support

For issues and questions:
- Check existing GitHub issues
- Review troubleshooting guide
- Contact support with detailed error information
