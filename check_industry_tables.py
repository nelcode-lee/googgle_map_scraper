#!/usr/bin/env python3
"""
Check industry tables in the database
"""

import asyncio
import os
from database import DatabaseManager

async def check_industry_tables():
    """Check what industry tables exist in the database"""
    try:
        db = DatabaseManager()
        await db.connect()
        
        async with db.pool.acquire() as conn:
            # Get all tables that start with 'industry_'
            result = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name LIKE 'industry_%'
                ORDER BY table_name
            """)
            
            print("🎯 Industry Tables Found:")
            print("=" * 40)
            
            if result:
                for row in result:
                    table_name = row['table_name']
                    # Get count of records in each table
                    count_result = await conn.fetchrow(f"SELECT COUNT(*) as count FROM {table_name}")
                    count = count_result['count']
                    print(f"📊 {table_name}: {count} businesses")
            else:
                print("❌ No industry tables found")
            
            # Also check the main businesses table
            main_count = await conn.fetchrow("SELECT COUNT(*) as count FROM businesses")
            print(f"\n📊 Main businesses table: {main_count['count']} businesses")
            
    except Exception as e:
        print(f"❌ Error checking industry tables: {e}")
    finally:
        if 'db' in locals():
            await db.close()

if __name__ == "__main__":
    asyncio.run(check_industry_tables())
