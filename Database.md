Pavitra E-commerce Database Documentation

📋 Database Overview

Database Name: pavitra_ecommerce
Total Tables: 23
Focus: Indian E-commerce with International Support
Currency: Indian Rupees (₹)
Language Support: English + Hindi (ready for localization)

🗂️ Table Structure & Relationships

1. User Management 👥

users Table

Purpose: Store customer and admin user information
Key Fields:

email, password_hash - Authentication
phone, country_code - International phone support (+91 for India)
is_admin - Role management
email_verified, phone_verified - Security
Relations: Orders, Reviews, Wishlists, Addresses
user_addresses Table

Purpose: Multiple shipping/billing addresses per user
Key Fields:

address_type - shipping/billing
country, state, city, postal_code - Indian address format
landmark - Indian address specific
is_default - Primary address flag
2. Product Catalog 🛍️

categories Table

Purpose: Hierarchical product categorization
Key Fields:

name, name_hindi - Bilingual support
parent_id - Unlimited subcategories
gst_slab, hsn_code - Indian tax compliance
is_featured - Homepage display
brands Table

Purpose: Product brand management
Key Fields:

is_indian_brand - Local brand identification
brand_origin_country - International brands
products Table

Purpose: Core product information
Key Fields:

base_price, compare_price - INR pricing
gst_rate, hsn_code - Tax compliance
stock_quantity, stock_status - Inventory management
weight_grams, dimensions_cm - Metric system
is_returnable, warranty_period - Indian e-commerce standards
Product Variations System

product_attributes - Size, Color, Storage, etc.
product_attribute_values - Specific values (S, M, L, Black, White, etc.)
product_variations - Individual SKU, price, stock per variation
variation_attributes - Links variations to attributes
3. Inventory Management 📦

stock_movements Table

Purpose: Complete audit trail of all stock changes
Key Fields:

movement_type - purchase/sale/return/adjustment
quantity, stock_before, stock_after - Change tracking
reason, performed_by - Accountability
stock_alerts Table

Purpose: Automatic low stock notifications
Key Fields:

alert_type - low_stock/out_of_stock
current_stock, threshold - Alert triggers
is_resolved - Alert management
4. Order Management 💳

orders Table

Purpose: Complete order processing
Key Fields:

order_number - Unique identifier (ORD-20241201-ABC123)
total_amount - Final amount in INR
payment_method - UPI/Card/NetBanking/Cash on Delivery
status, payment_status - Workflow tracking
gst_number - Business customer support
shipping_address, billing_address - JSON stored addresses
order_items Table

Purpose: Individual items in each order
Key Fields:

unit_price, total_price - INR pricing
gst_rate, gst_amount - Item-level taxation
variation_attributes - Size/color choices
5. Customer Engagement ❤️

product_reviews Table

Purpose: Customer reviews and ratings
Key Fields:

rating (1-5 stars), title, comment
is_verified_purchase - Authenticity
status - Moderation system
review_images - Visual feedback
wishlists Table

Purpose: Customer wishlist functionality
Relations: Users ↔ Products
shopping_cart Table

Purpose: Persistent cart for logged-in users
Key Fields: user_id, product_id, variation_id, quantity
6. Marketing & Promotions 🎯

coupons Table

Purpose: Discount and promotion management
Key Fields:

discount_type - percentage/fixed_amount/free_shipping
discount_value - Amount in INR or percentage
minimum_order_amount - INR threshold
valid_from, valid_until - Date ranges
usage_limit - Campaign control
banners Table

Purpose: Homepage and promotional banners
Key Fields:

banner_type - hero/slider/category banners
target_url - Navigation links
is_active - Display control
7. System Configuration ⚙️

site_settings Table

Purpose: Dynamic configuration storage
Key Fields:

currency_symbol - '₹'
free_shipping_threshold - '999.00'
gst_number - Business registration
return_period_days - '10'
newsletter_subscriptions Table

Purpose: Email marketing list
Key Fields: email, is_active
indian_states Table

Purpose: Indian state dropdowns for addresses
Key Fields: state_name, state_code, is_union_territory
🔗 Key Relationships Diagram

text
Users
  │
  ├── User Addresses (1-to-Many)
  ├── Orders (1-to-Many)
  ├── Reviews (1-to-Many)
  ├── Wishlists (1-to-Many)
  └── Shopping Cart (1-to-Many)

Categories
  │
  └── Products (1-to-Many)

Products
  │
  ├── Product Variations (1-to-Many)
  ├── Order Items (1-to-Many)
  ├── Reviews (1-to-Many)
  ├── Wishlists (1-to-Many)
  └── Stock Movements (1-to-Many)

Orders
  │
  └── Order Items (1-to-Many)

Coupons
  │
  └── Coupon Usage (1-to-Many)
🇮🇳 Indian Market Specific Features

Pricing & Taxation

All prices in Indian Rupees (₹)
GST compliant with HSN codes
Tax-inclusive pricing display
Item-level GST calculation
Address System

Indian state and city management
Landmark field for easy delivery
Postal code validation ready
Multiple address types
Payment Methods

UPI integration support
Net Banking
Credit/Debit Cards
Cash on Delivery (COD)
Digital Wallets
Product Standards

Weight in grams
Dimensions in centimeters
Indian clothing sizes
Return policy management
Warranty period tracking
Localization Ready

Hindi name fields
Indian festival promotions
Local brand identification
Regional shipping rules
📊 Sample Data Included

Users

Admin: admin@pavitra.com (+91-9876543210)
Ready for customer registration
Categories (7)

Electronics, Smartphones, Laptops
Fashion, Men's Fashion, Women's Fashion
Home & Kitchen
Brands (7)

International: Apple, Samsung, Nike, Adidas, Sony
Indian: Micromax, Bata
Products (5)

iPhone 14 Pro - ₹89,900
Samsung Galaxy S23 - ₹74,900
MacBook Air M2 - ₹1,14,900
Nike Air Max 270 - ₹12,999
Bata Formal Shoes - ₹2,999
Coupons (3)

WELCOME10 - 10% off
FREESHIP - Free shipping
SAVE500 - ₹500 off