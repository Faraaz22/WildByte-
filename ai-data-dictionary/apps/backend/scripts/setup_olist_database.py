"""
Script to set up Olist Brazilian E-commerce database with sample data.

This script creates the Olist database schema and inserts sample data
for testing the AI Data Dictionary platform.

Based on: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from datetime import datetime, timedelta
import random


# Database connection settings - read from environment or use defaults
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

POSTGRES_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
OLIST_DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/olist_ecommerce"
OLIST_DB_NAME = "olist_ecommerce"


async def create_database(engine: AsyncEngine) -> bool:
    """Create the olist_ecommerce database if it doesn't exist."""
    try:
        async with engine.connect() as conn:
            # Check if database exists
            result = await conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{OLIST_DB_NAME}'")
            )
            exists = result.scalar()
            
            if exists:
                print(f"✅ Database '{OLIST_DB_NAME}' already exists")
                return True
            else:
                print(f"📊 Creating database '{OLIST_DB_NAME}'...")
                await conn.execute(text(f"CREATE DATABASE {OLIST_DB_NAME}"))
                print(f"✅ Database '{OLIST_DB_NAME}' created successfully")
                return True
                
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False


async def create_schemas(engine: AsyncEngine):
    """Create all Olist database schemas."""
    
    print("\n📋 Creating database schemas...")
    
    # Create tables in order (respecting foreign key dependencies)
    schemas = [
        # Customers table
        """
        CREATE TABLE IF NOT EXISTS olist_customers (
            customer_id VARCHAR(255) PRIMARY KEY,
            customer_unique_id VARCHAR(255) NOT NULL,
            customer_zip_code_prefix VARCHAR(10),
            customer_city VARCHAR(255),
            customer_state CHAR(2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Geolocation table
        """
        CREATE TABLE IF NOT EXISTS olist_geolocation (
            id SERIAL PRIMARY KEY,
            geolocation_zip_code_prefix VARCHAR(10) NOT NULL,
            geolocation_lat DECIMAL(10, 8),
            geolocation_lng DECIMAL(11, 8),
            geolocation_city VARCHAR(255),
            geolocation_state CHAR(2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Orders table
        """
        CREATE TABLE IF NOT EXISTS olist_orders (
            order_id VARCHAR(255) PRIMARY KEY,
            customer_id VARCHAR(255) NOT NULL,
            order_status VARCHAR(50) NOT NULL,
            order_purchase_timestamp TIMESTAMP NOT NULL,
            order_approved_at TIMESTAMP,
            order_delivered_carrier_date TIMESTAMP,
            order_delivered_customer_date TIMESTAMP,
            order_estimated_delivery_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES olist_customers(customer_id) ON DELETE CASCADE
        )
        """,
        
        # Product category translation table
        """
        CREATE TABLE IF NOT EXISTS olist_product_category_translation (
            product_category_name VARCHAR(255) PRIMARY KEY,
            product_category_name_english VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Products table
        """
        CREATE TABLE IF NOT EXISTS olist_products (
            product_id VARCHAR(255) PRIMARY KEY,
            product_category_name VARCHAR(255),
            product_name_length INTEGER,
            product_description_length INTEGER,
            product_photos_qty INTEGER,
            product_weight_g INTEGER,
            product_length_cm INTEGER,
            product_height_cm INTEGER,
            product_width_cm INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_category_name) 
                REFERENCES olist_product_category_translation(product_category_name)
        )
        """,
        
        # Sellers table
        """
        CREATE TABLE IF NOT EXISTS olist_sellers (
            seller_id VARCHAR(255) PRIMARY KEY,
            seller_zip_code_prefix VARCHAR(10),
            seller_city VARCHAR(255),
            seller_state CHAR(2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Order items table
        """
        CREATE TABLE IF NOT EXISTS olist_order_items (
            id SERIAL PRIMARY KEY,
            order_id VARCHAR(255) NOT NULL,
            order_item_id INTEGER NOT NULL,
            product_id VARCHAR(255) NOT NULL,
            seller_id VARCHAR(255) NOT NULL,
            shipping_limit_date TIMESTAMP,
            price DECIMAL(10, 2) NOT NULL,
            freight_value DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES olist_orders(order_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES olist_products(product_id),
            FOREIGN KEY (seller_id) REFERENCES olist_sellers(seller_id),
            UNIQUE (order_id, order_item_id)
        )
        """,
        
        # Order payments table
        """
        CREATE TABLE IF NOT EXISTS olist_order_payments (
            id SERIAL PRIMARY KEY,
            order_id VARCHAR(255) NOT NULL,
            payment_sequential INTEGER NOT NULL,
            payment_type VARCHAR(50) NOT NULL,
            payment_installments INTEGER,
            payment_value DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES olist_orders(order_id) ON DELETE CASCADE
        )
        """,
        
        # Order reviews table
        """
        CREATE TABLE IF NOT EXISTS olist_order_reviews (
            id SERIAL PRIMARY KEY,
            review_id VARCHAR(255) NOT NULL UNIQUE,
            order_id VARCHAR(255) NOT NULL,
            review_score INTEGER CHECK (review_score BETWEEN 1 AND 5),
            review_comment_title TEXT,
            review_comment_message TEXT,
            review_creation_date TIMESTAMP,
            review_answer_timestamp TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES olist_orders(order_id) ON DELETE CASCADE
        )
        """,
    ]
    
    async with engine.begin() as conn:
        for i, schema_sql in enumerate(schemas, 1):
            try:
                await conn.execute(text(schema_sql))
                table_name = schema_sql.split("IF NOT EXISTS")[1].split("(")[0].strip()
                print(f"  ✅ Created table: {table_name}")
            except Exception as e:
                print(f"  ❌ Failed to create table #{i}: {e}")
                raise
    
    print("✅ All schemas created successfully!")


async def insert_sample_data(engine: AsyncEngine):
    """Insert sample data for testing."""
    
    print("\n📝 Inserting sample data...")
    
    # Sample data for testing
    base_time = datetime.now() - timedelta(days=30)
    
    sample_data = [
        # Product categories
        """
        INSERT INTO olist_product_category_translation (product_category_name, product_category_name_english)
        VALUES 
            ('cama_mesa_banho', 'bed_bath_table'),
            ('beleza_saude', 'health_beauty'),
            ('esporte_lazer', 'sports_leisure'),
            ('informatica_acessorios', 'computers_accessories'),
            ('moveis_decoracao', 'furniture_decor')
        ON CONFLICT (product_category_name) DO NOTHING
        """,
        
        # Customers
        f"""
        INSERT INTO olist_customers (customer_id, customer_unique_id, customer_zip_code_prefix, customer_city, customer_state)
        VALUES 
            ('cust001', 'unique001', '01310', 'sao paulo', 'SP'),
            ('cust002', 'unique002', '22041', 'rio de janeiro', 'RJ'),
            ('cust003', 'unique003', '30130', 'belo horizonte', 'MG'),
            ('cust004', 'unique004', '80020', 'curitiba', 'PR'),
            ('cust005', 'unique005', '90010', 'porto alegre', 'RS')
        ON CONFLICT (customer_id) DO NOTHING
        """,
        
        # Sellers
        f"""
        INSERT INTO olist_sellers (seller_id, seller_zip_code_prefix, seller_city, seller_state)
        VALUES 
            ('seller001', '01310', 'sao paulo', 'SP'),
            ('seller002', '22041', 'rio de janeiro', 'RJ'),
            ('seller003', '30130', 'belo horizonte', 'MG')
        ON CONFLICT (seller_id) DO NOTHING
        """,
        
        # Products
        """
        INSERT INTO olist_products (product_id, product_category_name, product_name_length, product_description_length, 
                                   product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm)
        VALUES 
            ('prod001', 'cama_mesa_banho', 50, 500, 3, 1000, 30, 10, 20),
            ('prod002', 'beleza_saude', 40, 450, 2, 500, 15, 8, 10),
            ('prod003', 'esporte_lazer', 60, 600, 4, 2000, 50, 20, 30),
            ('prod004', 'informatica_acessorios', 55, 550, 3, 300, 20, 5, 15),
            ('prod005', 'moveis_decoracao', 70, 700, 5, 15000, 100, 80, 60)
        ON CONFLICT (product_id) DO NOTHING
        """,
        
        # Orders
        f"""
        INSERT INTO olist_orders (order_id, customer_id, order_status, order_purchase_timestamp, 
                                 order_approved_at, order_delivered_carrier_date, 
                                 order_delivered_customer_date, order_estimated_delivery_date)
        VALUES 
            ('order001', 'cust001', 'delivered', '{base_time}', '{base_time + timedelta(hours=2)}', 
             '{base_time + timedelta(days=1)}', '{base_time + timedelta(days=5)}', '{base_time + timedelta(days=7)}'),
            ('order002', 'cust002', 'delivered', '{base_time + timedelta(days=1)}', '{base_time + timedelta(days=1, hours=3)}',
             '{base_time + timedelta(days=2)}', '{base_time + timedelta(days=6)}', '{base_time + timedelta(days=8)}'),
            ('order003', 'cust003', 'shipped', '{base_time + timedelta(days=2)}', '{base_time + timedelta(days=2, hours=4)}',
             '{base_time + timedelta(days=3)}', NULL, '{base_time + timedelta(days=9)}'),
            ('order004', 'cust004', 'processing', '{base_time + timedelta(days=3)}', '{base_time + timedelta(days=3, hours=1)}',
             NULL, NULL, '{base_time + timedelta(days=10)}'),
            ('order005', 'cust005', 'delivered', '{base_time + timedelta(days=4)}', '{base_time + timedelta(days=4, hours=2)}',
             '{base_time + timedelta(days=5)}', '{base_time + timedelta(days=9)}', '{base_time + timedelta(days=11)}')
        ON CONFLICT (order_id) DO NOTHING
        """,
        
        # Order items
        f"""
        INSERT INTO olist_order_items (order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value)
        VALUES 
            ('order001', 1, 'prod001', 'seller001', '{base_time + timedelta(days=1)}', 89.90, 15.50),
            ('order002', 1, 'prod002', 'seller002', '{base_time + timedelta(days=2)}', 45.00, 12.00),
            ('order003', 1, 'prod003', 'seller001', '{base_time + timedelta(days=3)}', 199.90, 25.00),
            ('order004', 1, 'prod004', 'seller003', '{base_time + timedelta(days=4)}', 129.00, 18.50),
            ('order005', 1, 'prod005', 'seller002', '{base_time + timedelta(days=5)}', 899.00, 85.00),
            ('order005', 2, 'prod001', 'seller001', '{base_time + timedelta(days=5)}', 89.90, 15.50)
        ON CONFLICT (order_id, order_item_id) DO NOTHING
        """,
        
        # Order payments
        """
        INSERT INTO olist_order_payments (order_id, payment_sequential, payment_type, payment_installments, payment_value)
        VALUES 
            ('order001', 1, 'credit_card', 3, 105.40),
            ('order002', 1, 'credit_card', 1, 57.00),
            ('order003', 1, 'boleto', 1, 224.90),
            ('order004', 1, 'credit_card', 6, 147.50),
            ('order005', 1, 'credit_card', 12, 989.40)
        ON CONFLICT DO NOTHING
        """,
        
        # Order reviews
        f"""
        INSERT INTO olist_order_reviews (review_id, order_id, review_score, review_comment_title, 
                                        review_comment_message, review_creation_date, review_answer_timestamp)
        VALUES 
            ('review001', 'order001', 5, 'Excelente!', 'Produto chegou rápido e em perfeito estado', 
             '{base_time + timedelta(days=6)}', '{base_time + timedelta(days=7)}'),
            ('review002', 'order002', 4, 'Bom produto', 'Atendeu as expectativas', 
             '{base_time + timedelta(days=7)}', '{base_time + timedelta(days=8)}'),
            ('review003', 'order005', 5, 'Perfeito!', 'Móvel lindo, entrega rápida', 
             '{base_time + timedelta(days=10)}', '{base_time + timedelta(days=11)}')
        ON CONFLICT (review_id) DO NOTHING
        """,
        
        # Geolocation sample
        """
        INSERT INTO olist_geolocation (geolocation_zip_code_prefix, geolocation_lat, geolocation_lng, 
                                      geolocation_city, geolocation_state)
        VALUES 
            ('01310', -23.5629, -46.6544, 'sao paulo', 'SP'),
            ('22041', -22.9068, -43.1729, 'rio de janeiro', 'RJ'),
            ('30130', -19.9167, -43.9345, 'belo horizonte', 'MG'),
            ('80020', -25.4284, -49.2733, 'curitiba', 'PR'),
            ('90010', -30.0346, -51.2177, 'porto alegre', 'RS')
        ON CONFLICT DO NOTHING
        """,
    ]
    
    async with engine.begin() as conn:
        for i, data_sql in enumerate(sample_data, 1):
            try:
                result = await conn.execute(text(data_sql))
                print(f"  ✅ Inserted sample data batch {i}")
            except Exception as e:
                print(f"  ❌ Failed to insert sample data batch {i}: {e}")
                raise
    
    print("✅ Sample data inserted successfully!")


async def create_indexes(engine: AsyncEngine):
    """Create indexes for better query performance."""
    
    print("\n🔍 Creating indexes...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_customers_state ON olist_customers(customer_state)",
        "CREATE INDEX IF NOT EXISTS idx_customers_city ON olist_customers(customer_city)",
        "CREATE INDEX IF NOT EXISTS idx_orders_customer ON olist_orders(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_orders_status ON olist_orders(order_status)",
        "CREATE INDEX IF NOT EXISTS idx_orders_purchase_date ON olist_orders(order_purchase_timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_order_items_order ON olist_order_items(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_order_items_product ON olist_order_items(product_id)",
        "CREATE INDEX IF NOT EXISTS idx_order_items_seller ON olist_order_items(seller_id)",
        "CREATE INDEX IF NOT EXISTS idx_products_category ON olist_products(product_category_name)",
        "CREATE INDEX IF NOT EXISTS idx_sellers_state ON olist_sellers(seller_state)",
        "CREATE INDEX IF NOT EXISTS idx_payments_order ON olist_order_payments(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_order ON olist_order_reviews(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_geolocation_zip ON olist_geolocation(geolocation_zip_code_prefix)",
    ]
    
    async with engine.begin() as conn:
        for index_sql in indexes:
            try:
                await conn.execute(text(index_sql))
                index_name = index_sql.split("INDEX")[1].split("ON")[0].strip()
                print(f"  ✅ Created index: {index_name}")
            except Exception as e:
                print(f"  ⚠️  Index creation warning: {e}")
    
    print("✅ Indexes created successfully!")


async def get_statistics(engine: AsyncEngine):
    """Get table statistics."""
    
    print("\n📊 Database Statistics:")
    print("=" * 60)
    
    tables = [
        "olist_customers",
        "olist_geolocation",
        "olist_orders",
        "olist_order_items",
        "olist_order_payments",
        "olist_order_reviews",
        "olist_products",
        "olist_sellers",
        "olist_product_category_translation",
    ]
    
    async with engine.connect() as conn:
        for table in tables:
            try:
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  {table:40}: {count:>5} rows")
            except Exception as e:
                print(f"  {table:40}: Error - {e}")
    
    print("=" * 60)


async def main():
    """Main execution function."""
    print("🚀 Olist Brazilian E-commerce Database Setup")
    print("=" * 60)
    print(f"\n🔑 Using credentials:")
    print(f"   User: {DB_USER}")
    print(f"   Host: {DB_HOST}:{DB_PORT}")
    print(f"   Target DB: {OLIST_DB_NAME}")
    print(f"\n💡 Tip: Set DB_PASSWORD environment variable if needed")
    print(f"   Example: $env:DB_PASSWORD='your_password'; python scripts\\setup_olist_database.py")
    
    # Step 1: Create database
    print("\n📍 Step 1: Create Database")
    postgres_engine = create_async_engine(POSTGRES_URL, isolation_level="AUTOCOMMIT")
    
    if not await create_database(postgres_engine):
        await postgres_engine.dispose()
        print("\n❌ Failed to create database. Please check:")
        print("   1. PostgreSQL is running")
        print("   2. Credentials are correct")
        print("   3. User has CREATE DATABASE privileges")
        return 1
    
    await postgres_engine.dispose()
    
    # Step 2: Create schemas
    print("\n📍 Step 2: Create Schemas")
    olist_engine = create_async_engine(OLIST_DB_URL, echo=False)
    
    try:
        await create_schemas(olist_engine)
        
        # Step 3: Insert sample data
        print("\n📍 Step 3: Insert Sample Data")
        await insert_sample_data(olist_engine)
        
        # Step 4: Create indexes
        print("\n📍 Step 4: Create Indexes")
        await create_indexes(olist_engine)
        
        # Step 5: Show statistics
        print("\n📍 Step 5: Statistics")
        await get_statistics(olist_engine)
        
        print("\n" + "=" * 60)
        print("✅ Setup completed successfully!")
        print("=" * 60)
        print("\n📝 Next Steps:")
        print("1. Go to http://localhost:3000/databases")
        print("2. Click 'Add Database'")
        print("3. Fill in the connection details:")
        print(f"   - Name: Olist E-commerce")
        print(f"   - Type: PostgreSQL")
        print(f"   - Host: localhost")
        print(f"   - Port: 5432")
        print(f"   - Database: {OLIST_DB_NAME}")
        print(f"   - Username: postgres")
        print(f"   - Password: postgres")
        print("4. Test the connection")
        print("5. Save the connection")
        print("\n🎉 Your database is ready to use!")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        await olist_engine.dispose()
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
