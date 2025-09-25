# Contact Details Enhancement

## 📞 **Enhanced Contact Details Capture & Display**

Your Google Maps scraper now has comprehensive contact details tracking and display capabilities.

## 🗄️ **Database Schema**

The `businesses` table already includes contact detail fields:

```sql
CREATE TABLE businesses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    -- Contact Details
    phone VARCHAR(50),           -- Telephone number
    website VARCHAR(500),        -- Website URL
    email VARCHAR(255),          -- Email address
    -- Other fields...
);
```

## 📊 **Contact Details Captured**

### **From Google Maps:**
- **📞 Phone Numbers**: Extracted from business listings
- **🌐 Websites**: Direct website URLs
- **📧 Email Addresses**: When available in listings

### **Data Quality Features:**
- **Phone Validation**: UK phone number format validation
- **Website Cleaning**: URL normalization and validation
- **Email Extraction**: Pattern matching from various fields
- **Data Quality Scoring**: Contact details weighted in quality score

## 🎛️ **Web Interface Enhancements**

### **Contact Details Dashboard:**
- **Live Counters**: Real-time tracking of captured contact details
- **Phone Numbers**: Shows count of businesses with phone numbers
- **Websites**: Displays count of businesses with websites
- **Email Addresses**: Shows count of businesses with email addresses

### **Visual Indicators:**
- **📞 Phone Count**: Green counter for phone numbers
- **🌐 Website Count**: Blue counter for websites  
- **📧 Email Count**: Purple counter for email addresses

### **Sample Data Preview:**
- **Business Name**: Shows sample business name
- **Contact Details**: Displays phone, website, email
- **Address**: Shows business address
- **Industry**: Displays business category

## 🔧 **Technical Implementation**

### **Data Processing Pipeline:**
1. **Extraction**: Selenium scrapes contact details from Google Maps
2. **Cleaning**: Data processor validates and normalizes contact info
3. **Storage**: Contact details saved to Neon DB [[memory:7111442]]
4. **Display**: Web interface shows real-time statistics

### **Contact Details Validation:**
```python
# Phone number validation
def validate_phone_number(phone: str) -> bool:
    # UK phone number patterns
    patterns = [
        r'^\+44[1-9]\d{8,9}$',  # +44 format
        r'^0[1-9]\d{8,9}$',     # 0 format
        r'^[1-9]\d{8,9}$'       # Without country code
    ]

# Website URL validation
def validate_website_url(url: str) -> bool:
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'

# Email validation
def validate_email(email: str) -> bool:
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
```

### **Data Quality Scoring:**
Contact details are weighted in the quality score:
- **Phone Number**: 20% of total score
- **Website**: 15% of total score  
- **Email**: 10% of total score
- **Total Contact Weight**: 45% of quality score

## 📈 **Expected Capture Rates**

Based on typical business data availability:

- **📞 Phone Numbers**: ~80% of businesses
- **🌐 Websites**: ~60% of businesses
- **📧 Email Addresses**: ~30% of businesses

## 🎯 **Business Value**

### **Contact Details Provide:**
- **Direct Outreach**: Phone numbers for sales calls
- **Digital Marketing**: Websites for online presence analysis
- **Email Campaigns**: Email addresses for marketing
- **Lead Generation**: Complete contact profiles for prospects

### **Use Cases:**
- **Sales Teams**: Direct contact information for outreach
- **Marketing**: Email and website data for campaigns
- **Lead Scoring**: Quality scores based on contact completeness
- **CRM Integration**: Export to customer relationship management

## 🚀 **Usage**

### **View Contact Statistics:**
1. Start the web interface: `./run.sh web`
2. Navigate to http://localhost:5000
3. View contact details counters in the status panel
4. Monitor real-time capture rates during scraping

### **Export Contact Data:**
```python
# Export with contact details
from utils import ExportUtils
businesses = []  # Your scraped data
ExportUtils.to_csv(businesses, "businesses_with_contacts.csv")
```

### **Database Queries:**
```sql
-- Get businesses with phone numbers
SELECT name, phone, website, email 
FROM businesses 
WHERE phone IS NOT NULL;

-- Get contact completeness statistics
SELECT 
    COUNT(*) as total,
    COUNT(phone) as with_phone,
    COUNT(website) as with_website,
    COUNT(email) as with_email
FROM businesses;
```

## 🔍 **Monitoring & Analytics**

### **Real-time Tracking:**
- **Live Counters**: Updated every second during scraping
- **Progress Indicators**: Visual feedback on contact capture
- **Error Reporting**: Issues with contact data extraction

### **Quality Metrics:**
- **Completeness Rate**: Percentage of businesses with contact details
- **Validation Success**: Rate of valid contact information
- **Data Quality Score**: Overall business record quality

## 💡 **Best Practices**

### **For Maximum Contact Capture:**
1. **Enable Companies House Verification**: Provides additional contact data
2. **Use Multiple Search Terms**: Increases coverage of business listings
3. **Target Specific Industries**: Some industries have better contact data
4. **Regular Re-scraping**: Contact details change over time

### **Data Quality Tips:**
1. **Review Error Logs**: Check for extraction issues
2. **Validate Exports**: Verify contact data before use
3. **Update Regularly**: Re-scrape for fresh contact information
4. **Clean Data**: Use validation functions before processing

## 🔮 **Future Enhancements**

- **Social Media Links**: Capture social media profiles
- **Contact Person Names**: Extract contact person information
- **Business Hours**: More detailed opening hours
- **Contact Verification**: Validate contact details automatically
- **Lead Scoring**: Advanced scoring based on contact completeness

The enhanced contact details system makes your business scraper a powerful lead generation and contact management tool!
