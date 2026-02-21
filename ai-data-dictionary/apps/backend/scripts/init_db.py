"""Database initialization script - creates default admin user."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import AsyncSessionLocal, engine, Base
from src.models.user import User, UserRole
from src.utils.auth import PasswordHasher


async def create_tables():
    """Create all database tables."""
    print("📊 Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully")


async def create_default_user():
    """Create default admin user if no users exist."""
    async with AsyncSessionLocal() as session:
        # Check if any users exist
        result = await session.execute(select(User))
        existing_users = result.scalars().all()

        if existing_users:
            print(f"ℹ️  Users already exist ({len(existing_users)} found). Skipping user creation.")
            return

        print("👤 Creating default admin user...")

        # Create default admin user
        default_password = "admin123"  # Change this in production!
        hashed_password = PasswordHasher.hash_password(default_password)

        admin_user = User(
            email="admin@example.com",
            username="admin",
            password_hash=hashed_password,
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )

        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)

        print("✅ Default admin user created successfully")
        print(f"   📧 Email: admin@example.com")
        print(f"   🔑 Password: {default_password}")
        print(f"   ⚠️  Please change the password after first login!")


async def init_database():
    """Initialize database with tables and default data."""
    print("🚀 Initializing database...")
    print()

    try:
        # Create tables
        await create_tables()
        print()

        # Create default user
        await create_default_user()
        print()

        print("🎉 Database initialization completed successfully!")
        return 0

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(init_database())
    sys.exit(exit_code)
