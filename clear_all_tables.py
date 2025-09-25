#!/usr/bin/env python3
"""
Clear all database tables - main businesses table and all industry tables
"""

import asyncio
import os
from database import DatabaseManager

async def clear_all_tables():
    """Clear all business records from all tables"""
    try:
        db = DatabaseManager()
        await db.connect()
        
        async with db.pool.acquire() as conn:
            # Get all industry tables
            industry_tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name LIKE 'industry_%'
                ORDER BY table_name
            """)
            
            print("🧹 Clearing all database tables...")
            print("=" * 50)
            
            # Clear main businesses table
            main_count = await conn.fetchrow("SELECT COUNT(*) as count FROM businesses")
            if main_count['count'] > 0:
                await conn.execute("DELETE FROM businesses")
                await conn.execute("ALTER SEQUENCE businesses_id_seq RESTART WITH 1")
                print(f"✅ Cleared main businesses table: {main_count['count']} records")
            else:
                print("✅ Main businesses table already empty")
            
            # Clear all industry tables
            total_cleared = 0
            for table in industry_tables:
                table_name = table['table_name']
                count_result = await conn.fetchrow(f"SELECT COUNT(*) as count FROM {table_name}")
                count = count_result['count']
                
                if count > 0:
                    await conn.execute(f"DELETE FROM {table_name}")
                    await conn.execute(f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1")
                    print(f"✅ Cleared {table_name}: {count} records")
                    total_cleared += count
                else:
                    print(f"✅ {table_name} already empty")
            
            print("=" * 50)
            print(f"🎉 Database completely cleared!")
            print(f"📊 Total records cleared: {main_count['count'] + total_cleared}")
            print(f"🗂️  Industry tables cleared: {len(industry_tables)}")
            
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
    finally:
        if 'db' in locals():
            await db.close()

if __name__ == "__main__":
    asyncio.run(clear_all_tables())
