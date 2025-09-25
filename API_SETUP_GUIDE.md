# API Setup Guide

## Companies House API Key Setup

### Step 1: Register for API Access
1. Visit: https://developer.company-information.service.gov.uk/
2. Click "Get started" or "Register"
3. Create account with your email
4. Verify your email address

### Step 2: Create Application
1. Go to "My applications" in your dashboard
2. Click "Create application"
3. Fill in:
   - **Application name**: `Google Maps Business Scraper`
   - **Description**: `Business intelligence tool for scraping and verifying UK companies`
   - **Application URL**: `http://localhost` (for testing)

### Step 3: Get Your API Key
- Your API key will look like: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
- Copy this key immediately (you won't be able to see it again)

### Step 4: Update .env File
Edit your `.env` file and replace `your_companies_house_api_key_here` with your actual API key:

```bash
# Companies House API Key
COMPANIES_HOUSE_API_KEY=a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

## API Rate Limits

**Companies House API Limits:**
- **Free tier**: 600 requests per 5 minutes
- **Burst limit**: 10 requests per second
- **Daily limit**: 1,000,000 requests per day

The scraper automatically handles rate limiting and will pause when limits are reached.

## API Endpoints Used

Based on your API reference document, the scraper uses these endpoints:

1. **Search Companies**: `GET /search/companies`
   - Find companies by name and location
   - Used for business verification

2. **Company Details**: `GET /company/{companyNumber}`
   - Get detailed company information
   - Extract SIC codes, status, incorporation date

3. **Company Officers**: `GET /company/{company_number}/officers`
   - Get director and officer information
   - Additional business intelligence data

## Testing Your API Key

Once you have your API key, test it:

```bash
# Activate virtual environment
source venv/bin/activate

# Test API connection
python -c "
from companies_house import CompaniesHouseAPI
import asyncio

async def test_api():
    async with CompaniesHouseAPI() as api:
        companies = await api.search_companies('test company')
        print(f'API working! Found {len(companies)} companies')
        return len(companies) > 0

result = asyncio.run(test_api())
print('✅ API key is working!' if result else '❌ API key test failed')
"
```

## Troubleshooting

**Common Issues:**

1. **Invalid API Key Error**:
   - Double-check you copied the key correctly
   - Ensure no extra spaces or characters
   - Verify the key is from the correct application

2. **Rate Limit Exceeded**:
   - Wait 5 minutes before trying again
   - Reduce `CONCURRENT_REQUESTS` in .env
   - Increase `SCRAPING_DELAY_MIN` and `SCRAPING_DELAY_MAX`

3. **Authentication Failed**:
   - Check your API key format
   - Ensure the key is active in your Companies House dashboard
   - Try regenerating the key if needed

## Next Steps

1. Get your API key from Companies House
2. Update the `.env` file with your key
3. Test the connection using the test script above
4. Start scraping with: `./run.sh scrape restaurants`

## Additional Resources

- **Companies House API Docs**: https://developer.company-information.service.gov.uk/api/docs
- **API Status**: https://status.companieshouse.gov.uk/
- **Support**: https://developer.company-information.service.gov.uk/support
