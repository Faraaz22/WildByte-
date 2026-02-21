# PowerShell Setup Script for Olist E-commerce Database
# This script uses psql CLI directly to avoid Python password issues

param(
    [string]$PostgresUser = "postgres",
    [string]$PostgresHost = "localhost",
    [int]$PostgresPort = 5432,
    [string]$PostgresDb = "data_dictionary",
    [string]$PostgresPassword = ""
)

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "Setting up Olist E-commerce Database" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Connection: $PostgresUser@$PostgresHost:$PostgresPort/$PostgresDb" -ForegroundColor Yellow
Write-Host ""

# SQL Script Content
$sqlScript = @"
-- Create Olist Schema
CREATE SCHEMA IF NOT EXISTS olist;
SET search_path TO olist;

-- 1. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(36) PRIMARY KEY,
    customer_zip_code_prefix VARCHAR(5),
    customer_city VARCHAR(100),
    customer_state VARCHAR(2)
);

-- 2. Orders Table
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL REFERENCES customers(customer_id),
    order_status VARCHAR(20),
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP
);

-- 3. Order Items Table
CREATE TABLE IF NOT EXISTS order_items (
    order_id VARCHAR(36) NOT NULL REFERENCES orders(order_id),
    order_item_id INTEGER,
    product_id VARCHAR(36),
    seller_id VARCHAR(36),
    shipping_limit_date TIMESTAMP,
    price DECIMAL(10, 2),
    freight_value DECIMAL(10, 2),
    PRIMARY KEY (order_id, order_item_id)
);

-- 4. Order Payments Table
CREATE TABLE IF NOT EXISTS order_payments (
    order_id VARCHAR(36) NOT NULL REFERENCES orders(order_id),
    payment_sequential INTEGER,
    payment_type VARCHAR(20),
    payment_installments INTEGER,
    payment_value DECIMAL(10, 2),
    PRIMARY KEY (order_id, payment_sequential)
);

-- 5. Order Reviews Table
CREATE TABLE IF NOT EXISTS order_reviews (
    review_id VARCHAR(36) PRIMARY KEY,
    order_id VARCHAR(36) NOT NULL REFERENCES orders(order_id),
    review_score INTEGER,
    review_comment_title VARCHAR(255),
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP
);

-- 6. Products Table
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(36) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name_length INTEGER,
    product_description_length INTEGER,
    product_photos_qty INTEGER,
    product_weight_g DECIMAL(10, 2),
    product_length_cm DECIMAL(10, 2),
    product_height_cm DECIMAL(10, 2),
    product_width_cm DECIMAL(10, 2)
);

-- 7. Sellers Table
CREATE TABLE IF NOT EXISTS sellers (
    seller_id VARCHAR(36) PRIMARY KEY,
    seller_zip_code_prefix VARCHAR(5),
    seller_city VARCHAR(100),
    seller_state VARCHAR(2)
);

-- 8. Product Category Translation Table
CREATE TABLE IF NOT EXISTS product_category_name_translation (
    product_category_name VARCHAR(100) PRIMARY KEY,
    product_category_name_english VARCHAR(100)
);

-- 9. Geolocation Table
CREATE TABLE IF NOT EXISTS geolocation (
    geolocation_zip_code_prefix VARCHAR(5) PRIMARY KEY,
    geolocation_lat DECIMAL(10, 6),
    geolocation_lng DECIMAL(10, 6),
    geolocation_city VARCHAR(100),
    geolocation_state VARCHAR(2)
);

-- Insert Sample Data

-- Sample Customers
INSERT INTO customers (customer_id, customer_zip_code_prefix, customer_city, customer_state)
VALUES
    ('c1', '01310', 'São Paulo', 'SP'),
    ('c2', '20040020', 'Rio de Janeiro', 'RJ'),
    ('c3', '30150371', 'Belo Horizonte', 'MG'),
    ('c4', '50030130', 'Recife', 'PE'),
    ('c5', '40015903', 'Salvador', 'BA')
ON CONFLICT DO NOTHING;

-- Sample Orders
INSERT INTO orders (order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date)
VALUES
    ('o1', 'c1', 'delivered', '2024-01-15 10:00:00', '2024-01-15 10:30:00', '2024-01-16 14:00:00', '2024-01-17 10:00:00'),
    ('o2', 'c2', 'delivered', '2024-01-16 11:00:00', '2024-01-16 11:30:00', '2024-01-17 15:00:00', '2024-01-18 10:00:00'),
    ('o3', 'c3', 'processing', '2024-01-17 12:00:00', '2024-01-17 12:30:00', NULL, NULL),
    ('o4', 'c4', 'approved', '2024-01-18 13:00:00', '2024-01-18 13:30:00', NULL, NULL),
    ('o5', 'c5', 'canceled', '2024-01-19 14:00:00', NULL, NULL, NULL)
ON CONFLICT DO NOTHING;

-- Sample Order Items
INSERT INTO order_items (order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value)
VALUES
    ('o1', 1, 'p1', 's1', '2024-01-20 23:59:00', 99.90, 10.50),
    ('o1', 2, 'p2', 's2', '2024-01-20 23:59:00', 149.90, 15.00),
    ('o2', 1, 'p3', 's1', '2024-01-21 23:59:00', 199.90, 20.00),
    ('o3', 1, 'p4', 's3', '2024-01-22 23:59:00', 299.90, 25.50),
    ('o4', 1, 'p5', 's2', '2024-01-23 23:59:00', 79.90, 8.00),
    ('o5', 1, 'p1', 's1', '2024-01-24 23:59:00', 99.90, 10.50)
ON CONFLICT DO NOTHING;

-- Sample Order Payments
INSERT INTO order_payments (order_id, payment_sequential, payment_type, payment_installments, payment_value)
VALUES
    ('o1', 1, 'credit_card', 1, 110.40),
    ('o2', 1, 'credit_card', 2, 169.90),
    ('o3', 1, 'debit_card', 1, 219.90),
    ('o4', 1, 'boleto', 0, 325.40),
    ('o5', 1, 'credit_card', 3, 110.40)
ON CONFLICT DO NOTHING;

-- Sample Order Reviews
INSERT INTO order_reviews (review_id, order_id, review_score, review_comment_title, review_comment_message, review_creation_date, review_answer_timestamp)
VALUES
    ('r1', 'o1', 5, 'Excellent product', 'Great quality and fast delivery!', '2024-01-18 10:00:00', '2024-01-18 11:00:00'),
    ('r2', 'o2', 4, 'Good product', 'Good product, could be better packaging', '2024-01-19 10:00:00', '2024-01-19 11:00:00'),
    ('r3', 'o3', 3, 'Average', 'Product is okay, delivery was slow', '2024-01-20 10:00:00', NULL)
ON CONFLICT DO NOTHING;

-- Sample Products
INSERT INTO products (product_id, product_category_name, product_name_length, product_description_length, product_photos_qty, product_weight_g, product_length_cm, product_height_cm, product_width_cm)
VALUES
    ('p1', 'electronics', 20, 150, 5, 500, 10, 5, 8),
    ('p2', 'furniture', 25, 200, 3, 5000, 100, 50, 40),
    ('p3', 'books', 15, 100, 2, 300, 20, 15, 2),
    ('p4', 'sports', 18, 120, 4, 400, 30, 10, 20),
    ('p5', 'home', 22, 180, 3, 700, 50, 30, 25)
ON CONFLICT DO NOTHING;

-- Sample Sellers
INSERT INTO sellers (seller_id, seller_zip_code_prefix, seller_city, seller_state)
VALUES
    ('s1', '01310', 'São Paulo', 'SP'),
    ('s2', '20040020', 'Rio de Janeiro', 'RJ'),
    ('s3', '30150371', 'Belo Horizonte', 'MG')
ON CONFLICT DO NOTHING;

-- Sample Product Categories
INSERT INTO product_category_name_translation (product_category_name, product_category_name_english)
VALUES
    ('electronics', 'Electronics'),
    ('furniture', 'Furniture'),
    ('books', 'Books'),
    ('sports', 'Sports'),
    ('home', 'Home & Garden')
ON CONFLICT DO NOTHING;

-- Sample Geolocation
INSERT INTO geolocation (geolocation_zip_code_prefix, geolocation_lat, geolocation_lng, geolocation_city, geolocation_state)
VALUES
    ('01310', -23.550520, -46.633309, 'São Paulo', 'SP'),
    ('20040020', -22.897496, -43.109137, 'Rio de Janeiro', 'RJ'),
    ('30150371', -19.885330, -43.948118, 'Belo Horizonte', 'MG'),
    ('50030130', -8.047911, -34.877083, 'Recife', 'PE'),
    ('40015903', -12.971942, -38.510716, 'Salvador', 'BA')
ON CONFLICT DO NOTHING;

-- Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_purchase_timestamp ON orders(order_purchase_timestamp);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_order_items_seller_id ON order_items(seller_id);
CREATE INDEX IF NOT EXISTS idx_order_payments_order_id ON order_payments(order_id);
CREATE INDEX IF NOT EXISTS idx_order_reviews_order_id ON order_reviews(order_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(product_category_name);
CREATE INDEX IF NOT EXISTS idx_sellers_state ON sellers(seller_state);
CREATE INDEX IF NOT EXISTS idx_customers_state ON customers(customer_state);
CREATE INDEX IF NOT EXISTS idx_geolocation_state ON geolocation(geolocation_state);
CREATE INDEX IF NOT EXISTS idx_geolocation_city ON geolocation(geolocation_city);

-- Print Summary Statistics
SELECT 'Schema Created' AS status, 'olist' AS schema_name WHERE EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'olist');
SELECT COUNT(*) AS customers FROM customers;
SELECT COUNT(*) AS orders FROM orders;
SELECT COUNT(*) AS order_items FROM order_items;
SELECT COUNT(*) AS order_payments FROM order_payments;
SELECT COUNT(*) AS order_reviews FROM order_reviews;
SELECT COUNT(*) AS products FROM products;
SELECT COUNT(*) AS sellers FROM sellers;
SELECT COUNT(*) AS product_categories FROM product_category_name_translation;
SELECT COUNT(*) AS geolocation_records FROM geolocation;
"@

# Write SQL to temporary file
$sqlFilePath = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), "olist_setup_$([DateTime]::Now.Ticks).sql")
Set-Content -Path $sqlFilePath -Value $sqlScript

Write-Host "Running SQL setup script..." -ForegroundColor Yellow
Write-Host ""

# Build psql command
$psqlArgs = @(
    "-h", $PostgresHost
    "-p", $PostgresPort
    "-U", $PostgresUser
    "-d", $PostgresDb
    "-f", $sqlFilePath
)

# Set password if provided
if ($PostgresPassword) {
    $env:PGPASSWORD = $PostgresPassword
}

# Execute psql
try {
    & psql @psqlArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "===========================================" -ForegroundColor Green
        Write-Host "✅ Olist Database Setup Complete!" -ForegroundColor Green
        Write-Host "===========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Schema: olist" -ForegroundColor Cyan
        Write-Host "Tables: 9" -ForegroundColor Cyan
        Write-Host "Sample Records: 52" -ForegroundColor Cyan
        Write-Host "Indexes: 13" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "===========================================" -ForegroundColor Red
        Write-Host "❌ Setup failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        Write-Host "===========================================" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}
catch {
    Write-Host "❌ Error running psql: $_" -ForegroundColor Red
    exit 1
}
finally {
    # Clean up
    if (Test-Path $sqlFilePath) {
        Remove-Item $sqlFilePath -Force
    }
    if ($PostgresPassword) {
        Remove-Item env:PGPASSWORD -ErrorAction SilentlyContinue
    }
}
