"""Test PostgreSQL connection and help diagnose issues."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import getpass


async def test_connection(db_url: str) -> bool:
    """Test a database connection."""
    try:
        engine = create_async_engine(db_url, pool_pre_ping=True)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


async def main():
    """Test PostgreSQL connection."""
    print("🔍 PostgreSQL Connection Tester")
    print("=" * 50)
    print()
    
    # Get credentials from user
    print("Please enter your PostgreSQL credentials:")
    host = input("Host (default: localhost): ").strip() or "localhost"
    port = input("Port (default: 5432): ").strip() or "5432"
    user = input("Username (default: postgres): ").strip() or "postgres"
    password = getpass.getpass("Password: ").strip()
    database = input("Database (default: postgres): ").strip() or "postgres"
    
    print()
    print(f"🔌 Testing connection to {user}@{host}:{port}/{database}...")
    
    # Test connection
    db_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
    
    if await test_connection(db_url):
        print()
        print("✅ Connection successful!")
        print()
        print("📝 Update your .env file with:")
        print(f"DATABASE_URL=postgresql+asyncpg://{user}:{password}@{host}:{port}/data_dictionary")
        print()
        
        # Try to create data_dictionary database
        create = input("Would you like to create 'data_dictionary' database? (y/N): ").strip().lower()
        if create == 'y':
            try:
                engine = create_async_engine(
                    f"postgresql+asyncpg://{user}:{password}@{host}:{port}/postgres",
                    isolation_level="AUTOCOMMIT"
                )
                async with engine.connect() as conn:
                    result = await conn.execute(
                        text("SELECT 1 FROM pg_database WHERE datname = 'data_dictionary'")
                    )
                    if result.scalar():
                        print("✅ Database 'data_dictionary' already exists")
                    else:
                        await conn.execute(text("CREATE DATABASE data_dictionary"))
                        print("✅ Database 'data_dictionary' created successfully")
                await engine.dispose()
            except Exception as e:
                print(f"❌ Failed to create database: {e}")
        
        return 0
    else:
        print()
        print("❌ Connection failed!")
        print()
        print("💡 Common solutions:")
        print("   1. Check if PostgreSQL is running: Get-Service postgresql*")
        print("   2. Try the default superuser password for your PostgreSQL installation")
        print("   3. Reset PostgreSQL password if needed")
        print("   4. Check pg_hba.conf for authentication settings")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
