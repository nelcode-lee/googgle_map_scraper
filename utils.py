import re
import json
import csv
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

class ExportUtils:
    """Utilities for exporting scraped data"""
    
    @staticmethod
    def to_csv(businesses: List[Dict[str, Any]], filename: str = None) -> str:
        """Export businesses to CSV format"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"businesses_export_{timestamp}.csv"
            
        fieldnames = [
            'name', 'address', 'postcode', 'phone', 'website', 'email',
            'industry', 'google_rating', 'google_reviews_count',
            'latitude', 'longitude', 'companies_house_number',
            'companies_house_status', 'data_quality_score'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for business in businesses:
                # Flatten the data for CSV
                row = {field: business.get(field, '') for field in fieldnames}
                writer.writerow(row)
                
        return filename
        
    @staticmethod
    def to_json(businesses: List[Dict[str, Any]], filename: str = None) -> str:
        """Export businesses to JSON format"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"businesses_export_{timestamp}.json"
            
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(businesses, jsonfile, indent=2, ensure_ascii=False, default=str)
            
        return filename

class ValidationUtils:
    """Utilities for data validation"""
    
    @staticmethod
    def validate_uk_postcode(postcode: str) -> bool:
        """Validate UK postcode format"""
        if not postcode:
            return False
            
        # UK postcode regex pattern
        pattern = r'^[A-Z]{1,2}[0-9R][0-9A-Z]?\s*[0-9][A-Z]{2}$'
        return bool(re.match(pattern, postcode.upper().strip()))
        
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate UK phone number format"""
        if not phone:
            return False
            
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # UK phone number patterns
        patterns = [
            r'^\+44[1-9]\d{8,9}$',  # +44 format
            r'^0[1-9]\d{8,9}$',     # 0 format
            r'^[1-9]\d{8,9}$'       # Without country code
        ]
        
        return any(re.match(pattern, cleaned) for pattern in patterns)
        
    @staticmethod
    def validate_website_url(url: str) -> bool:
        """Validate website URL format"""
        if not url:
            return False
            
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(url_pattern, url))
        
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        if not email:
            return False
            
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

class SearchUtils:
    """Utilities for search operations"""
    
    @staticmethod
    def generate_search_variations(business_type: str) -> List[str]:
        """Generate search term variations for a business type"""
        variations = [business_type]
        
        # Common variations
        plurals = {
            'restaurant': ['restaurants', 'dining', 'food'],
            'cafe': ['cafes', 'coffee shop', 'coffee shops'],
            'shop': ['shops', 'store', 'stores'],
            'salon': ['salons', 'beauty salon', 'hair salon'],
            'garage': ['garages', 'auto repair', 'car service']
        }
        
        if business_type in plurals:
            variations.extend(plurals[business_type])
            
        return variations
        
    @staticmethod
    def clean_search_query(query: str) -> str:
        """Clean and optimize search query"""
        # Remove special characters
        cleaned = re.sub(r'[^\w\s]', ' ', query)
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned

class GeographicUtils:
    """Utilities for geographic operations"""
    
    @staticmethod
    def is_valid_uk_coordinates(latitude: float, longitude: float) -> bool:
        """Check if coordinates are within UK bounds"""
        # Approximate UK boundaries
        uk_bounds = {
            'min_lat': 49.5,
            'max_lat': 61.0,
            'min_lng': -8.0,
            'max_lng': 2.0
        }
        
        return (uk_bounds['min_lat'] <= latitude <= uk_bounds['max_lat'] and
                uk_bounds['min_lng'] <= longitude <= uk_bounds['max_lng'])
                
    @staticmethod
    def extract_city_from_address(address: str) -> Optional[str]:
        """Extract city name from address"""
        if not address:
            return None
            
        # Common UK city patterns
        # This is a simplified version - you might want to use a proper geocoding service
        parts = address.split(',')
        
        if len(parts) >= 2:
            # Usually city is second to last before postcode
            potential_city = parts[-2].strip()
            
            # Remove postcode if present
            potential_city = re.sub(r'[A-Z]{1,2}[0-9R][0-9A-Z]?\s*[0-9][A-Z]{2}', '', potential_city).strip()
            
            if potential_city and len(potential_city) > 1:
                return potential_city
                
        return None

class StatisticsUtils:
    """Utilities for statistical analysis"""
    
    @staticmethod
    def calculate_business_density(businesses: List[Dict[str, Any]], area_type: str = 'postcode') -> Dict[str, int]:
        """Calculate business density by area"""
        density = {}
        
        for business in businesses:
            if area_type == 'postcode':
                key = business.get('postcode', 'Unknown')
                if key:
                    # Use postcode district (first part)
                    key = key.split()[0] if ' ' in key else key[:2]
            elif area_type == 'city':
                key = GeographicUtils.extract_city_from_address(business.get('address', ''))
                key = key or 'Unknown'
            else:
                key = business.get(area_type, 'Unknown')
                
            density[key] = density.get(key, 0) + 1
            
        return density
        
    @staticmethod
    def calculate_industry_distribution(businesses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of businesses by industry"""
        distribution = {}
        
        for business in businesses:
            industry = business.get('industry', 'Unknown')
            distribution[industry] = distribution.get(industry, 0) + 1
            
        return distribution
        
    @staticmethod
    def calculate_data_quality_metrics(businesses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall data quality metrics"""
        total = len(businesses)
        if total == 0:
            return {}
            
        metrics = {
            'total_businesses': total,
            'with_phone': sum(1 for b in businesses if b.get('phone')),
            'with_website': sum(1 for b in businesses if b.get('website')),
            'with_email': sum(1 for b in businesses if b.get('email')),
            'with_coordinates': sum(1 for b in businesses if b.get('latitude') and b.get('longitude')),
            'with_companies_house': sum(1 for b in businesses if b.get('companies_house_number')),
            'avg_data_quality_score': sum(b.get('data_quality_score', 0) for b in businesses) / total
        }
        
        # Calculate percentages
        for key in ['with_phone', 'with_website', 'with_email', 'with_coordinates', 'with_companies_house']:
            metrics[f'{key}_percentage'] = (metrics[key] / total) * 100
            
        return metrics

class ReportUtils:
    """Utilities for generating reports"""
    
    @staticmethod
    def generate_summary_report(businesses: List[Dict[str, Any]]) -> str:
        """Generate a summary report of scraped businesses"""
        stats = StatisticsUtils.calculate_data_quality_metrics(businesses)
        industry_dist = StatisticsUtils.calculate_industry_distribution(businesses)
        density = StatisticsUtils.calculate_business_density(businesses)
        
        report = []
        report.append("BUSINESS SCRAPING SUMMARY REPORT")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall statistics
        report.append("OVERALL STATISTICS")
        report.append("-" * 20)
        report.append(f"Total Businesses: {stats.get('total_businesses', 0)}")
        report.append(f"Average Data Quality Score: {stats.get('avg_data_quality_score', 0):.2f}")
        report.append("")
        
        # Contact information completeness
        report.append("CONTACT INFORMATION COMPLETENESS")
        report.append("-" * 35)
        report.append(f"With Phone: {stats.get('with_phone', 0)} ({stats.get('with_phone_percentage', 0):.1f}%)")
        report.append(f"With Website: {stats.get('with_website', 0)} ({stats.get('with_website_percentage', 0):.1f}%)")
        report.append(f"With Email: {stats.get('with_email', 0)} ({stats.get('with_email_percentage', 0):.1f}%)")
        report.append(f"With Coordinates: {stats.get('with_coordinates', 0)} ({stats.get('with_coordinates_percentage', 0):.1f}%)")
        report.append("")
        
        # Companies House verification
        report.append("COMPANIES HOUSE VERIFICATION")
        report.append("-" * 30)
        report.append(f"Verified: {stats.get('with_companies_house', 0)} ({stats.get('with_companies_house_percentage', 0):.1f}%)")
        report.append("")
        
        # Industry distribution
        report.append("INDUSTRY DISTRIBUTION")
        report.append("-" * 20)
        for industry, count in sorted(industry_dist.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats.get('total_businesses', 1)) * 100
            report.append(f"{industry}: {count} ({percentage:.1f}%)")
        report.append("")
        
        # Geographic distribution (top 10)
        report.append("GEOGRAPHIC DISTRIBUTION (Top 10)")
        report.append("-" * 35)
        sorted_density = sorted(density.items(), key=lambda x: x[1], reverse=True)[:10]
        for area, count in sorted_density:
            report.append(f"{area}: {count}")
        
        return "\n".join(report)
