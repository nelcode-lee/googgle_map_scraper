import asyncio
import asyncpg
from typing import List, Dict, Any, Optional
from loguru import logger
from datetime import datetime
from config import Config

class DatabaseManager:
    def __init__(self):
        self.pool = None
        
    async def connect(self):
        """Establish database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(Config.DATABASE_URL)
            logger.info("Database connection pool created successfully")
            await self.create_tables()
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            raise
    
    async def create_tables(self):
        """Create necessary database tables"""
        async with self.pool.acquire() as conn:
            # Businesses table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS businesses (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(500) NOT NULL,
                    google_place_id VARCHAR(255) UNIQUE,
                    companies_house_number VARCHAR(50),
                    address TEXT,
                    postcode VARCHAR(20),
                    phone VARCHAR(50),
                    website VARCHAR(500),
                    email VARCHAR(255),
                    industry VARCHAR(100),
                    sic_codes TEXT[],
                    google_rating DECIMAL(3,2),
                    google_reviews_count INTEGER,
                    latitude DECIMAL(10,8),
                    longitude DECIMAL(11,8),
                    opening_hours JSONB,
                    status VARCHAR(50) DEFAULT 'active',
                    companies_house_status VARCHAR(50),
                    incorporation_date DATE,
                    last_verified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Search history table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id SERIAL PRIMARY KEY,
                    industry VARCHAR(100),
                    search_term VARCHAR(255),
                    location VARCHAR(255),
                    results_count INTEGER,
                    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Companies House verification table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS ch_verification_log (
                    id SERIAL PRIMARY KEY,
                    business_id INTEGER REFERENCES businesses(id),
                    company_number VARCHAR(50),
                    verification_status VARCHAR(50),
                    verification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    raw_data JSONB
                );
            """)
            
            # Create indexes
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_businesses_place_id ON businesses(google_place_id);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_businesses_company_number ON businesses(companies_house_number);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_businesses_postcode ON businesses(postcode);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_businesses_industry ON businesses(industry);")
            
            logger.info("Database tables created successfully")
    
    async def create_industry_table(self, industry: str) -> str:
        """Create a new table for a specific industry"""
        import re
        # Clean industry name to be a valid table name
        clean_industry = re.sub(r'[^a-zA-Z0-9_]', '_', industry.lower())
        table_name = f"industry_{clean_industry}"
        
        async with self.pool.acquire() as conn:
            # Create industry-specific table
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    address TEXT,
                    phone VARCHAR(50),
                    website TEXT,
                    email VARCHAR(255),
                    google_rating DECIMAL(3,2),
                    google_place_id VARCHAR(255),
                    industry VARCHAR(100),
                    search_term VARCHAR(100),
                    search_location VARCHAR(100),
                    postcode VARCHAR(20),
                    opening_hours JSONB,
                    place_id VARCHAR(255),
                    types TEXT,
                    geometry TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for the industry table
            await conn.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{table_name}_search_location 
                ON {table_name}(search_location)
            """)
            
            logger.info(f"Industry table '{table_name}' created successfully")
            return table_name
    
    async def insert_business_to_industry_table(self, business: Dict[str, Any], table_name: str) -> None:
        """Insert business data into industry-specific table"""
        async with self.pool.acquire() as conn:
            await conn.execute(f"""
                INSERT INTO {table_name} (
                    name, address, phone, website, email, google_rating, 
                    google_place_id, industry, search_term, search_location, 
                    postcode, opening_hours, place_id, types, geometry
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
                )
            """, 
                business.get('name', ''),
                business.get('address', ''),
                business.get('phone', ''),
                business.get('website', ''),
                business.get('email', ''),
                business.get('google_rating'),
                business.get('google_place_id', ''),
                business.get('industry', ''),
                business.get('search_term', ''),
                business.get('search_location', ''),
                business.get('postcode', ''),
                business.get('opening_hours', '{}'),
                business.get('place_id', ''),
                business.get('types', '[]'),
                business.get('geometry', '{}')
            )
    
    async def insert_business(self, business_data: Dict[str, Any]) -> int:
        """Insert a new business record"""
        async with self.pool.acquire() as conn:
            query = """
                INSERT INTO businesses (
                    name, google_place_id, address, postcode, phone, website, 
                    email, industry, google_rating, google_reviews_count,
                    latitude, longitude, opening_hours
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                ON CONFLICT (google_place_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    address = EXCLUDED.address,
                    postcode = EXCLUDED.postcode,
                    phone = EXCLUDED.phone,
                    website = EXCLUDED.website,
                    email = EXCLUDED.email,
                    google_rating = EXCLUDED.google_rating,
                    google_reviews_count = EXCLUDED.google_reviews_count,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id;
            """
            
            business_id = await conn.fetchval(
                query,
                business_data.get('name'),
                business_data.get('google_place_id'),
                business_data.get('address'),
                business_data.get('postcode'),
                business_data.get('phone'),
                business_data.get('website'),
                business_data.get('email'),
                business_data.get('industry'),
                business_data.get('google_rating'),
                business_data.get('google_reviews_count'),
                business_data.get('latitude'),
                business_data.get('longitude'),
                business_data.get('opening_hours')
            )
            
            return business_id
    
    async def update_companies_house_data(self, business_id: int, ch_data: Dict[str, Any]):
        """Update business with Companies House data"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE businesses SET
                    companies_house_number = $2,
                    companies_house_status = $3,
                    incorporation_date = $4,
                    sic_codes = $5,
                    last_verified = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = $1
            """, business_id, ch_data.get('company_number'), 
                ch_data.get('company_status'), ch_data.get('date_of_creation'),
                ch_data.get('sic_codes', []))
    
    async def get_unverified_businesses(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get businesses that haven't been verified with Companies House"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, name, postcode, companies_house_number
                FROM businesses 
                WHERE companies_house_number IS NULL 
                   OR last_verified < NOW() - INTERVAL '30 days'
                LIMIT $1
            """, limit)
            
            return [dict(row) for row in rows]
    
    async def get_contact_statistics(self) -> Dict[str, int]:
        """Get contact details statistics"""
        async with self.pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_businesses,
                    COUNT(phone) as phone_count,
                    COUNT(website) as website_count,
                    COUNT(email) as email_count
                FROM businesses
            """)
            
            return {
                'total_businesses': stats['total_businesses'] or 0,
                'phone_count': stats['phone_count'] or 0,
                'website_count': stats['website_count'] or 0,
                'email_count': stats['email_count'] or 0
            }
    
    async def get_sample_business(self) -> Optional[Dict[str, Any]]:
        """Get a sample business record for preview"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT name, industry, phone, website, email, address, google_rating
                FROM businesses 
                WHERE name IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 1
            """)
            
            return dict(row) if row else None
    
    async def log_search(self, industry: str, search_term: str, location: str, results_count: int):
        """Log search history"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO search_history (industry, search_term, location, results_count)
                VALUES ($1, $2, $3, $4)
            """, industry, search_term, location, results_count)
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
