"""Create PostgreSQL database if it doesn't exist."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def create_database():
    """Create the data_dictionary database if it doesn't exist."""
    # Connect to postgres database (default database)
    default_db_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    
    print("🔌 Connecting to PostgreSQL...")
    
    try:
        engine = create_async_engine(default_db_url, isolation_level="AUTOCOMMIT")
        
        async with engine.connect() as conn:
            # Check if database exists
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = 'data_dictionary'")
            )
            exists = result.scalar()
            
            if exists:
                print("✅ Database 'data_dictionary' already exists")
            else:
                print("📊 Creating database 'data_dictionary'...")
                await conn.execute(text("CREATE DATABASE data_dictionary"))
                print("✅ Database 'data_dictionary' created successfully")
        
        await engine.dispose()
        return 0
        
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        print("\n💡 Possible solutions:")
        print("   1. Check if PostgreSQL is running")
        print("   2. Verify the postgres user password (default: 'postgres')")
        print("   3. Update DATABASE_URL in .env file with correct credentials")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(create_database())
    sys.exit(exit_code)
