-- =============================================
-- Pavitra E-commerce Database Setup (India Focus + International)
-- Complete SQL Script with Sample Data
-- =============================================

-- Create database
CREATE DATABASE IF NOT EXISTS pavitra;
USE pavitra;

-- =============================================
-- 1. USERS & AUTHENTICATION TABLES (INTERNATIONAL)
-- =============================================

-- Users table with international support
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT (UUID()),
    email VARCHAR(255) UNIQUE NOT NULL,# extension.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

# Login manager configuration
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    
    -- International phone format: +[country code][number]
    phone VARCHAR(20),
    country_code VARCHAR(5) DEFAULT '+91', -- Default to India
    phone_verified BOOLEAN DEFAULT FALSE,
    
    avatar_url VARCHAR(500),
    email_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP NULL,
    
    -- Additional international fields
    date_of_birth DATE,
    gender ENUM('male', 'female', 'other') NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_email (email),
    INDEX idx_uuid (uuid),
    INDEX idx_active (is_active),
    INDEX idx_phone (phone)
);

-- Enhanced user addresses for international support
CREATE TABLE user_addresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    address_type ENUM('shipping', 'billing') DEFAULT 'shipping',
    
    -- International name format
    full_name VARCHAR(200) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    country_code VARCHAR(5) DEFAULT '+91',
    
    -- Address fields
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    landmark VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'India',
    postal_code VARCHAR(20) NOT NULL,
    
    -- Address classification for India
    address_type_detail ENUM('home', 'work', 'other') DEFAULT 'home',
    is_default BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_address_type (address_type),
    INDEX idx_country (country)
);

-- =============================================
-- 2. CATEGORIES & BRANDS (INDIAN MARKET FOCUS)
-- =============================================

-- Categories hierarchy with Indian market focus
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    name_hindi VARCHAR(255), -- Hindi name for localization
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    description_hindi TEXT,
    meta_title VARCHAR(255),
    meta_description TEXT,
    parent_id INT NULL,
    image_url VARCHAR(500),
    banner_url VARCHAR(500),
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    
    -- Indian market specific
    gst_slab DECIMAL(5,2) DEFAULT 18.00, -- Default GST rate for category
    hsn_code VARCHAR(10), -- HSN code for taxation
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_id) REFERENCES categories(id),
    INDEX idx_slug (slug),
    INDEX idx_parent (parent_id),
    INDEX idx_active (is_active),
    INDEX idx_featured (is_featured)
);

-- Brands with Indian presence
CREATE TABLE brands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    logo_url VARCHAR(500),
    website_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    
    -- Indian market info
    is_indian_brand BOOLEAN DEFAULT FALSE,
    brand_origin_country VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_slug (slug),
    INDEX idx_active (is_active)
);

-- =============================================
-- 3. PRODUCTS & INVENTORY MANAGEMENT (INDIAN PRICING)
-- =============================================

-- Products master table with Indian pricing
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT (UUID()),
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    short_description TEXT,
    description LONGTEXT,
    specification JSON,
    
    -- Indian Pricing (in INR)
    base_price DECIMAL(12,2) NOT NULL, -- INR
    compare_price DECIMAL(12,2), -- MRP in INR
    cost_price DECIMAL(12,2), -- Cost in INR
    
    -- Indian Taxation
    gst_rate DECIMAL(5,2) DEFAULT 18.00, -- GST percentage
    hsn_code VARCHAR(10), -- HSN code
    is_gst_inclusive BOOLEAN DEFAULT TRUE, -- Whether price includes GST
    
    -- Enhanced Inventory Management
    track_inventory BOOLEAN DEFAULT TRUE,
    stock_quantity INT DEFAULT 0,
    low_stock_threshold INT DEFAULT 5,
    allow_backorders BOOLEAN DEFAULT FALSE,
    max_cart_quantity INT DEFAULT 10,
    min_cart_quantity INT DEFAULT 1,
    
    -- Stock Status (automatically updated)
    stock_status ENUM('in_stock', 'low_stock', 'out_of_stock', 'on_backorder') DEFAULT 'out_of_stock',
    
    -- Product type
    product_type ENUM('simple', 'variable', 'digital') DEFAULT 'simple',
    is_virtual BOOLEAN DEFAULT FALSE,
    is_downloadable BOOLEAN DEFAULT FALSE,
    
    -- Shipping (weight in grams for India)
    weight_grams DECIMAL(8,2), -- Weight in grams
    length_cm DECIMAL(8,2), -- Dimensions in cm
    width_cm DECIMAL(8,2),
    height_cm DECIMAL(8,2),
    
    -- Media
    main_image_url VARCHAR(500),
    image_gallery JSON,
    
    -- Relations
    category_id INT NOT NULL,
    brand_id INT,
    
    -- Status & SEO
    status ENUM('draft', 'active', 'inactive', 'archived') DEFAULT 'draft',
    is_featured BOOLEAN DEFAULT FALSE,
    is_trending BOOLEAN DEFAULT FALSE,
    is_bestseller BOOLEAN DEFAULT FALSE,
    is_on_sale BOOLEAN DEFAULT FALSE,
    
    -- Indian e-commerce specific
    is_returnable BOOLEAN DEFAULT TRUE,
    return_period_days INT DEFAULT 10, -- Default return period
    warranty_period_months INT DEFAULT 0,
    
    meta_title VARCHAR(255),
    meta_description TEXT,
    meta_keywords TEXT,
    
    -- Analytics
    view_count INT DEFAULT 0,
    wishlist_count INT DEFAULT 0,
    total_sold INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (brand_id) REFERENCES brands(id),
    
    INDEX idx_slug (slug),
    INDEX idx_sku (sku),
    INDEX idx_category (category_id),
    INDEX idx_brand (brand_id),
    INDEX idx_status (status),
    INDEX idx_featured (is_featured),
    INDEX idx_stock_status (stock_status),
    INDEX idx_on_sale (is_on_sale),
    INDEX idx_trending (is_trending)
);

-- Product attributes (sizes specific to Indian market)
CREATE TABLE product_attributes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    type ENUM('color', 'size', 'text', 'select') DEFAULT 'select',
    is_visible BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_slug (slug)
);

-- Product attribute values with Indian sizes
CREATE TABLE product_attribute_values (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attribute_id INT NOT NULL,
    value VARCHAR(255) NOT NULL,
    color_code VARCHAR(7),
    image_url VARCHAR(500),
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (attribute_id) REFERENCES product_attributes(id) ON DELETE CASCADE,
    INDEX idx_attribute (attribute_id)
);

-- Product variations with Indian pricing
CREATE TABLE product_variations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    
    -- Pricing (INR)
    price DECIMAL(12,2),
    compare_price DECIMAL(12,2),
    cost_price DECIMAL(12,2),
    
    -- Individual stock management
    stock_quantity INT DEFAULT 0,
    low_stock_threshold INT DEFAULT 5,
    allow_backorders BOOLEAN DEFAULT FALSE,
    stock_status ENUM('in_stock', 'low_stock', 'out_of_stock', 'on_backorder') DEFAULT 'out_of_stock',
    
    -- Physical attributes (in grams and cm)
    weight_grams DECIMAL(8,2),
    length_cm DECIMAL(8,2),
    width_cm DECIMAL(8,2),
    height_cm DECIMAL(8,2),
    
    image_url VARCHAR(500),
    is_default BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    
    INDEX idx_product (product_id),
    INDEX idx_sku (sku),
    INDEX idx_stock_status (stock_status)
);

-- Variation attribute combinations
CREATE TABLE variation_attributes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    variation_id INT NOT NULL,
    attribute_id INT NOT NULL,
    attribute_value_id INT NOT NULL,
    FOREIGN KEY (variation_id) REFERENCES product_variations(id) ON DELETE CASCADE,
    FOREIGN KEY (attribute_id) REFERENCES product_attributes(id),
    FOREIGN KEY (attribute_value_id) REFERENCES product_attribute_values(id),
    UNIQUE KEY unique_variation_attribute (variation_id, attribute_id),
    INDEX idx_variation (variation_id)
);

-- Product tags
CREATE TABLE product_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_slug (slug)
);

-- Product-tag relationships
CREATE TABLE product_tag_relations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    tag_id INT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES product_tags(id) ON DELETE CASCADE,
    UNIQUE KEY unique_product_tag (product_id, tag_id),
    INDEX idx_product (product_id),
    INDEX idx_tag (tag_id)
);

-- =============================================
-- 4. STOCK MANAGEMENT & INVENTORY TRACKING
-- =============================================

-- Stock management table (for tracking inventory changes)
CREATE TABLE stock_movements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    variation_id INT NULL,
    
    -- Movement type: purchase, sale, return, adjustment, damage, etc.
    movement_type ENUM(
        'purchase', 
        'sale', 
        'return', 
        'adjustment', 
        'damage', 
        'transfer_in', 
        'transfer_out'
    ) NOT NULL,
    
    quantity INT NOT NULL,
    stock_before INT NOT NULL,
    stock_after INT NOT NULL,
    
    -- Reference information
    reference_type ENUM('order', 'purchase_order', 'adjustment', 'other') DEFAULT 'other',
    reference_id INT NULL,
    
    -- Reason for adjustment
    reason TEXT,
    
    -- Performed by
    performed_by INT NULL, -- User ID who made the change
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (variation_id) REFERENCES product_variations(id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by) REFERENCES users(id),
    
    INDEX idx_product (product_id),
    INDEX idx_movement_type (movement_type),
    INDEX idx_performed_at (performed_at)
);

-- Stock alerts (low stock notifications)
CREATE TABLE stock_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    variation_id INT NULL,
    
    alert_type ENUM('low_stock', 'out_of_stock', 'over_stock') DEFAULT 'low_stock',
    current_stock INT NOT NULL,
    threshold INT NOT NULL,
    
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP NULL,
    resolved_by INT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (variation_id) REFERENCES product_variations(id) ON DELETE CASCADE,
    FOREIGN KEY (resolved_by) REFERENCES users(id),
    
    INDEX idx_product (product_id),
    INDEX idx_resolved (is_resolved)
);

-- =============================================
-- 5. ORDERS & PAYMENTS (INDIAN PAYMENT METHODS)
-- =============================================

-- Orders table with Indian payment support
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT (UUID()),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    
    -- Indian Pricing (INR)
    subtotal DECIMAL(12,2) NOT NULL, -- Before tax and shipping
    shipping_amount DECIMAL(12,2) DEFAULT 0,
    tax_amount DECIMAL(12,2) DEFAULT 0, -- GST amount
    discount_amount DECIMAL(12,2) DEFAULT 0,
    total_amount DECIMAL(12,2) NOT NULL, -- Final amount in INR
    
    -- Status
    status ENUM('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded') DEFAULT 'pending',
    payment_status ENUM('pending', 'paid', 'failed', 'refunded', 'partially_refunded') DEFAULT 'pending',
    
    -- Indian Payment Methods
    payment_method ENUM('credit_card', 'debit_card', 'upi', 'netbanking', 'cash_on_delivery', 'wallet') DEFAULT 'cash_on_delivery',
    payment_gateway VARCHAR(100),
    transaction_id VARCHAR(255),
    upi_id VARCHAR(255), -- For UPI payments
    
    -- Shipping
    shipping_method VARCHAR(100),
    tracking_number VARCHAR(100),
    shipping_address JSON,
    billing_address JSON,
    
    -- Customer info
    customer_note TEXT,
    admin_note TEXT,
    
    -- Indian order specifics
    is_gst_invoice BOOLEAN DEFAULT TRUE,
    gst_number VARCHAR(15), -- Customer GST number if provided
    
    -- Timestamps
    paid_at TIMESTAMP NULL,
    shipped_at TIMESTAMP NULL,
    delivered_at TIMESTAMP NULL,
    cancelled_at TIMESTAMP NULL,
    
    estimated_delivery DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    
    INDEX idx_order_number (order_number),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_payment_status (payment_status),
    INDEX idx_created_at (created_at)
);

-- Order items with Indian pricing
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    variation_id INT NULL,
    
    product_name VARCHAR(255) NOT NULL,
    product_sku VARCHAR(100) NOT NULL,
    product_image VARCHAR(500),
    
    unit_price DECIMAL(12,2) NOT NULL, -- INR
    quantity INT NOT NULL,
    total_price DECIMAL(12,2) NOT NULL, -- INR
    
    -- GST details per item
    gst_rate DECIMAL(5,2) DEFAULT 18.00,
    gst_amount DECIMAL(10,2) DEFAULT 0,
    
    -- Variation attributes
    variation_attributes JSON,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (variation_id) REFERENCES product_variations(id),
    
    INDEX idx_order (order_id),
    INDEX idx_product (product_id)
);

-- =============================================
-- 6. REVIEWS & RATINGS
-- =============================================

-- Product reviews
CREATE TABLE product_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT (UUID()),
    product_id INT NOT NULL,
    user_id INT NOT NULL,
    order_item_id INT NULL,
    
    rating TINYINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT,
    
    -- Media
    review_images JSON,
    
    -- Status
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    
    -- Helpfulness
    helpful_count INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (order_item_id) REFERENCES order_items(id),
    
    UNIQUE KEY unique_product_user (product_id, user_id),
    INDEX idx_product (product_id),
    INDEX idx_status (status),
    INDEX idx_rating (rating)
);

-- Review helpfulness
CREATE TABLE review_helpfulness (
    id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT NOT NULL,
    user_id INT NOT NULL,
    is_helpful BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES product_reviews(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_review_user (review_id, user_id)
);

-- =============================================
-- 7. WISHLIST & CART
-- =============================================

-- Wishlist
CREATE TABLE wishlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_product (user_id, product_id),
    INDEX idx_user (user_id)
);

-- Shopping cart (for logged-in users)
CREATE TABLE shopping_cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    variation_id INT NULL,
    quantity INT NOT NULL DEFAULT 1,
    cart_data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (variation_id) REFERENCES product_variations(id),
    UNIQUE KEY unique_user_product_variation (user_id, product_id, variation_id),
    INDEX idx_user (user_id)
);

-- =============================================
-- 8. DISCOUNTS & PROMOTIONS (INDIAN CURRENCY)
-- =============================================

-- Coupons with INR discounts
CREATE TABLE coupons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Discount configuration (INR)
    discount_type ENUM('percentage', 'fixed_amount', 'free_shipping') DEFAULT 'percentage',
    discount_value DECIMAL(10,2) NOT NULL, -- Percentage or fixed amount in INR
    maximum_discount_amount DECIMAL(10,2), -- Maximum cap in INR
    minimum_order_amount DECIMAL(10,2) DEFAULT 0, -- Minimum order in INR
    
    -- Usage limits
    usage_limit INT,
    usage_limit_per_user INT,
    used_count INT DEFAULT 0,
    
    -- Validity
    valid_from TIMESTAMP NULL,
    valid_until TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Applicability
    apply_to ENUM('all_products', 'specific_categories', 'specific_products') DEFAULT 'all_products',
    applicable_categories JSON,
    applicable_products JSON,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_code (code),
    INDEX idx_active (is_active)
);

-- Coupon usage tracking
CREATE TABLE coupon_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    coupon_id INT NOT NULL,
    user_id INT NOT NULL,
    order_id INT NOT NULL,
    discount_amount DECIMAL(10,2) NOT NULL, -- Actual discount applied in INR
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (coupon_id) REFERENCES coupons(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    INDEX idx_coupon_user (coupon_id, user_id)
);

-- =============================================
-- 9. ADDITIONAL TABLES (INDIAN FOCUS)
-- =============================================

-- Site settings for Indian e-commerce
CREATE TABLE site_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(255) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_setting_key (setting_key)
);

-- Banners & promotions
CREATE TABLE banners (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    image_url VARCHAR(500) NOT NULL,
    target_url VARCHAR(500),
    banner_type ENUM('home_hero', 'home_slider', 'category_banner', 'sidebar_banner') DEFAULT 'home_slider',
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    start_date TIMESTAMP NULL,
    end_date TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_banner_type (banner_type),
    INDEX idx_active (is_active)
);

-- Newsletter subscriptions
CREATE TABLE newsletter_subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email)
);

-- Indian states and cities for address management
CREATE TABLE indian_states (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state_name VARCHAR(100) NOT NULL,
    state_code VARCHAR(10) NOT NULL,
    is_union_territory BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_state_code (state_code)
);

-- =============================================
-- SAMPLE DATA INSERTION (INDIAN MARKET)
-- =============================================

-- Insert admin user with Indian phone
INSERT INTO users (email, password_hash, first_name, last_name, phone, country_code, is_admin, email_verified) VALUES
('admin@pavitra.com', '$2b$12$LQv3c1yqBWVHxkd0L8k7Oe7M7M7M7M7M7M7M7M7M7M7M7M7M7M7M', 'Admin', 'User', '9876543210', '+91', TRUE, TRUE);

-- Insert sample Indian categories
INSERT INTO categories (name, name_hindi, slug, description, is_featured, gst_slab, hsn_code, image_url) VALUES
('Electronics', 'इलेक्ट्रॉनिक्स', 'electronics', 'Latest electronic gadgets and devices', TRUE, 18.00, '8517', '/static/img/categories/electronics.jpg'),
('Smartphones', 'स्मार्टफोन', 'smartphones', 'Mobile phones and accessories', FALSE, 18.00, '8517', '/static/img/categories/smartphones.jpg'),
('Laptops', 'लैपटॉप', 'laptops', 'Laptops and computers', FALSE, 18.00, '8471', '/static/img/categories/laptops.jpg'),
('Fashion', 'फैशन', 'fashion', 'Clothing and accessories', TRUE, 12.00, '61', '/static/img/categories/fashion.jpg'),
('Men''s Fashion', 'पुरुषों का फैशन', 'mens-fashion', 'Men clothing and accessories', FALSE, 12.00, '61', '/static/img/categories/mens-fashion.jpg'),
('Women''s Fashion', 'महिलाओं का फैशन', 'womens-fashion', 'Women clothing and accessories', FALSE, 12.00, '62', '/static/img/categories/womens-fashion.jpg'),
('Home & Kitchen', 'घर और रसोई', 'home-kitchen', 'Home appliances and kitchen items', TRUE, 18.00, '8516', '/static/img/categories/home-kitchen.jpg');

-- Update parent IDs for subcategories
UPDATE categories SET parent_id = 1 WHERE slug IN ('smartphones', 'laptops');
UPDATE categories SET parent_id = 4 WHERE slug IN ('mens-fashion', 'womens-fashion');

-- Insert brands with Indian origin info
INSERT INTO brands (name, slug, description, is_indian_brand, brand_origin_country) VALUES
('Apple', 'apple', 'Premium technology products', FALSE, 'USA'),
('Samsung', 'samsung', 'Innovative electronics and appliances', FALSE, 'South Korea'),
('Nike', 'nike', 'Athletic shoes and apparel', FALSE, 'USA'),
('Adidas', 'adidas', 'Sports shoes and clothing', FALSE, 'Germany'),
('Sony', 'sony', 'Electronics and entertainment', FALSE, 'Japan'),
('Micromax', 'micromax', 'Indian smartphone brand', TRUE, 'India'),
('Bata', 'bata', 'Footwear and accessories', TRUE, 'India');

-- Insert sample products with Indian pricing (INR)
INSERT INTO products (sku, name, slug, short_description, description, base_price, compare_price, category_id, brand_id, stock_quantity, low_stock_threshold, status, is_featured, is_on_sale, gst_rate, weight_grams, main_image_url) VALUES
('IPHONE14-128', 'iPhone 14 Pro', 'iphone-14-pro', 'Latest iPhone with advanced features', 'The most advanced iPhone with Dynamic Island, Always-On display, and the best battery life ever.', 89900.00, 99900.00, 2, 1, 50, 5, 'active', TRUE, FALSE, 18.00, 206, '/static/img/product/iphone14-pro.jpg'),
('SAMSUNG-S23', 'Samsung Galaxy S23', 'samsung-galaxy-s23', 'Powerful Android smartphone', 'Experience the ultimate Android smartphone with advanced camera and performance.', 74900.00, 84900.00, 2, 2, 30, 5, 'active', TRUE, TRUE, 18.00, 168, '/static/img/products/galaxy-s23.jpg'),
('MACBOOK-AIR', 'MacBook Air M2', 'macbook-air-m2', 'Powerful and lightweight laptop', 'Supercharged by M2 chip, MacBook Air delivers incredible performance in an ultra-portable design.', 114900.00, 129900.00, 3, 1, 25, 3, 'active', TRUE, FALSE, 18.00, 1270, '/static/img/product/macbook-air.jpg'),
('NIKE-AIRMAX', 'Nike Air Max 270', 'nike-air-max-270', 'Comfortable running shoes', 'The Nike Air Max 270 delivers comfortable all-day wear with revolutionary Air Max cushioning.', 12999.00, 14999.00, 5, 3, 100, 10, 'active', FALSE, TRUE, 12.00, 800, '/static/img/product/nike-airmax.jpg'),
('BATA-SHOES', 'Bata Formal Shoes', 'bata-formal-shoes', 'Comfortable formal shoes for men', 'Premium quality formal shoes perfect for office wear and special occasions.', 2999.00, 3999.00, 5, 7, 75, 8, 'active', FALSE, FALSE, 12.00, 600, '/static/img/product/bata-shoes.jpg');

-- Update stock status based on quantities
UPDATE products SET stock_status = 
    CASE 
        WHEN stock_quantity <= 0 THEN 'out_of_stock'
        WHEN stock_quantity <= low_stock_threshold THEN 'low_stock'
        ELSE 'in_stock'
    END;

-- Insert product attributes with Indian sizes
INSERT INTO product_attributes (name, slug, type) VALUES
('Color', 'color', 'color'),
('Size', 'size', 'select'),
('Storage', 'storage', 'select'),
('Memory', 'memory', 'select'),
('Indian Size', 'indian-size', 'select');

-- Insert attribute values with Indian sizes
INSERT INTO product_attribute_values (attribute_id, value, color_code) VALUES
(1, 'Black', '#000000'),
(1, 'White', '#FFFFFF'),
(1, 'Blue', '#0000FF'),
(1, 'Red', '#FF0000'),
(2, 'Small', NULL),
(2, 'Medium', NULL),
(2, 'Large', NULL),
(2, 'X-Large', NULL),
(3, '128GB', NULL),
(3, '256GB', NULL),
(3, '512GB', NULL),
(4, '8GB', NULL),
(4, '16GB', NULL),
(5, '28', NULL),  -- Indian clothing sizes
(5, '30', NULL),
(5, '32', NULL),
(5, '34', NULL),
(5, '36', NULL),
(5, '38', NULL);

-- Insert sample coupons with INR discounts
INSERT INTO coupons (code, name, description, discount_type, discount_value, minimum_order_amount, usage_limit, valid_from, valid_until) VALUES
('WELCOME10', 'Welcome Discount', '10% off on first order', 'percentage', 10.00, 1000.00, 1000, NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY)),
('FREESHIP', 'Free Shipping', 'Free shipping on all orders', 'free_shipping', 0.00, 0.00, NULL, NOW(), DATE_ADD(NOW(), INTERVAL 60 DAY)),
('SAVE500', 'Festive Sale', '₹500 off on orders above ₹3000', 'fixed_amount', 500.00, 3000.00, 500, NOW(), DATE_ADD(NOW(), INTERVAL 15 DAY));

-- Insert Indian site settings
INSERT INTO site_settings (setting_key, setting_value, setting_type) VALUES
('store_name', 'Pavitra Enterprises', 'string'),
('store_email', 'info@pavitra.com', 'string'),
('store_phone', '+91-9876543210', 'string'),
('store_address', '123 Business Street, Mumbai, Maharashtra 400001', 'string'),
('free_shipping_threshold', '999.00', 'number'),
('tax_rate', '18.0', 'number'),
('currency', 'INR', 'string'),
('currency_symbol', '₹', 'string'),
('default_country', 'India', 'string'),
('default_country_code', '+91', 'string'),
('gst_number', '07AABCU9603R1ZM', 'string'),
('return_period_days', '10', 'number');

-- Insert sample banners with Indian festivals
INSERT INTO banners (title, description, image_url, target_url, banner_type, sort_order) VALUES
('Diwali Sale', 'Up to 50% off on electronics and fashion', '/static/img/banners/diwali-sale.jpg', '/category/electronics', 'home_hero', 1),
('New Arrivals', 'Check out our latest products', '/static/img/banners/new-arrivals.jpg', '/search?q=new', 'home_slider', 2),
('Free Shipping', 'Free shipping on orders over ₹999', '/static/img/banners/free-shipping.jpg', '/shipping-info', 'home_slider', 3);

-- Insert Indian states
INSERT INTO indian_states (state_name, state_code, is_union_territory) VALUES
('Maharashtra', 'MH', FALSE),
('Delhi', 'DL', FALSE),
('Karnataka', 'KA', FALSE),
('Tamil Nadu', 'TN', FALSE),
('Uttar Pradesh', 'UP', FALSE),
('Gujarat', 'GJ', FALSE),
('West Bengal', 'WB', FALSE),
('Rajasthan', 'RJ', FALSE);

-- =============================================
-- DATABASE DOCUMENTATION (INDIA FOCUS)
-- =============================================

/*
PAVITRA E-COMMERCE DATABASE DOCUMENTATION (INDIA)
=================================================

KEY INDIAN FEATURES IMPLEMENTED:
1. INDIAN CURRENCY (INR) - All prices in Indian Rupees
2. GST COMPLIANCE - GST rates, HSN codes, GST invoices
3. INDIAN PHONE FORMATS - +91 country code, 10-digit numbers
4. INDIAN ADDRESS SYSTEM - States, cities, postal codes
5. LOCALIZED SIZES - Indian clothing and shoe sizes
6. INDIAN PAYMENT METHODS - UPI, Net Banking, Cash on Delivery
7. LOCALIZED CATEGORIES - Hindi names and descriptions
8. INDIAN BRANDS IDENTIFICATION - Mark Indian brands
9. METRIC SYSTEM - Weight in grams, dimensions in cm
10. INDIAN FESTIVAL READY - Diwali sales, festive banners

INTERNATIONAL SUPPORT:
- Country codes for phone numbers
- International address formats
- Multi-currency ready (can be extended)
- International brand origins

STOCK MANAGEMENT:
- Automatic stock status (In Stock, Low Stock, Out of Stock)
- GST-inclusive pricing
- Weight in grams for shipping calculations
- Return policies as per Indian e-commerce standards

SAMPLE DATA INCLUDED:
- Admin user with Indian phone number
- Indian categories with GST rates and HSN codes
- Mixed international and Indian brands
- Products with Indian pricing (₹)
- Indian payment methods
- Indian states for address management

NEXT STEPS:
1. Run this SQL script in your MySQL database
2. Update Flask app to use Indian currency (₹)
3. Implement GST calculation in order processing
4. Add UPI payment gateway integration
5. Create Hindi language support (optional)

ADMIN ACCESS:
Email: admin@pavitra.com
Phone: +91-9876543210

CURRENCY: All prices in Indian Rupees (₹)
*/