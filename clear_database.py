#!/usr/bin/env python3
"""
Clear the database - remove all business records
"""

import asyncio
import os
from database import DatabaseManager

async def clear_database():
    """Clear all business records from the database"""
    try:
        db = DatabaseManager()
        await db.connect()
        
        # Get current count
        async with db.pool.acquire() as conn:
            count_result = await conn.fetchrow("SELECT COUNT(*) as count FROM businesses")
            current_count = count_result['count']
            print(f"Current businesses in database: {current_count}")
            
            if current_count == 0:
                print("Database is already empty!")
                return
            
            # Clear all businesses
            await conn.execute("DELETE FROM businesses")
            print(f"✅ Deleted {current_count} business records")
            
            # Reset the sequence
            await conn.execute("ALTER SEQUENCE businesses_id_seq RESTART WITH 1")
            print("✅ Reset ID sequence")
            
        print("🎉 Database cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
    finally:
        if 'db' in locals():
            await db.close()

if __name__ == "__main__":
    asyncio.run(clear_database())
