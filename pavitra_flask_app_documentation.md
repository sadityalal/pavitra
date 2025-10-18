# Pavitra E-commerce Flask Application Documentation

## 📋 Project Overview

**Project Name:** Pavitra Enterprises E-commerce Platform  
**Technology Stack:** Flask, MySQL, Bootstrap 5, jQuery  
**Focus:** Indian E-commerce with International Support  
**Currency:** Indian Rupees (₹)  
**Database:** MySQL with 23 tables  

---

## 🗂️ Project Structure

```
pavitra_ecommerce/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── extension.py           # Flask extensions initialization
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── models/                # Database models
│   ├── __init__.py
│   ├── user.py
│   ├── address.py
│   ├── category.py
│   ├── brand.py
│   ├── product.py
│   ├── stock.py
│   ├── order.py
│   ├── wishlist.py
│   ├── cart.py
│   ├── review.py
│   └── coupon.py
├── routes/                # Flask blueprints
│   ├── __init__.py
│   ├── auth_routes.py
│   ├── shop_routes.py
│   └── admin_routes.py
├── templates/             # Jinja2 templates
│   ├── base.html
│   ├── auth/
│   ├── shop/
│   ├── admin/
│   └── errors/
├── static/                # Static files
│   ├── css/
│   ├── js/
│   └── images/
└── migrations/            # Database migrations (auto-generated)
```

---

## 🗄️ Database Schema Summary

### Core Tables (23 Tables)

#### 1. User Management
- `users` - Customer and admin accounts  
- `user_addresses` - Multiple shipping/billing addresses  

#### 2. Product Catalog
- `categories` - Hierarchical product categories  
- `brands` - Product brands with Indian origin tracking  
- `products` - Main product information  
- `product_attributes` - Size, color, storage options  
- `product_attribute_values` - Specific attribute values  
- `product_variations` - Product variants with individual pricing/stock  
- `variation_attributes` - Links variations to attributes  
- `product_tags` & `product_tag_relations` - Product tagging system  

#### 3. Inventory Management
- `stock_movements` - Complete audit trail of stock changes  
- `stock_alerts` - Low stock and out-of-stock notifications  

#### 4. Order Management
- `orders` - Complete order information  
- `order_items` - Individual items in orders  

#### 5. Customer Engagement
- `product_reviews` - Customer reviews and ratings  
- `review_helpfulness` - Review voting system  
- `wishlists` - Customer wishlists  
- `shopping_cart` - Persistent shopping cart  

#### 6. Marketing & Promotions
- `coupons` - Discount codes and promotions  
- `coupon_usage` - Coupon usage tracking  
- `banners` - Promotional banners  
- `newsletter_subscriptions` - Email marketing list  

#### 7. System Configuration
- `site_settings` - Dynamic configuration storage  
- `indian_states` - Indian states for address management  

---

## 🇮🇳 Indian Market Features

### Currency & Pricing
- All prices in Indian Rupees (₹)  
- GST compliant pricing (tax-inclusive)  
- HSN code support for products  
- Indian number formatting  

### Address System
- Indian state and city management  
- Landmark field for easy delivery  
- Postal code validation ready  
- Multiple address types (home/work/other)  

### Payment Methods
- UPI integration support  
- Net Banking  
- Credit/Debit Cards  
- Cash on Delivery (COD)  
- Digital Wallets  

### Product Standards
- Weight in grams  
- Dimensions in centimeters  
- Indian clothing sizes  
- Return policy management (10 days default)  
- Warranty period tracking  

### Taxation
- GST rate per product/category  
- GST invoice generation  
- HSN code compliance  
- Tax-inclusive pricing  

---

## 🔧 Installation & Setup

### 1. Prerequisites

```bash
# Required software
- Python 3.8+
- MySQL 5.7+
- pip (Python package manager)
```

### 2. Database Setup

```sql
CREATE DATABASE pavitra_ecommerce;

-- Run SQL script to create all 23 tables with sample data
```

### 3. Environment Configuration

```bash
# .env file
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=mysql+pymysql://username:password@localhost/pavitra_ecommerce
FLASK_ENV=development
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Initialize Application

```bash
flask init-db
flask create-admin
flask seed-data
flask run
```

---

## 🚀 Key Features Implemented

### User Management
✅ User registration and authentication  
✅ International phone support (+91 for India)  
✅ Multiple shipping addresses  
✅ Admin and customer roles  
✅ Email and phone verification ready  

### Product Management
✅ Simple and variable products  
✅ Product variations (size, color, etc.)  
✅ Inventory tracking  
✅ Category hierarchy  
✅ Brand management  
✅ Product images and galleries  

### Inventory System
✅ Real-time stock tracking  
✅ Low stock alerts  
✅ Stock movement audit trail  
✅ Backorder support  
✅ Automatic stock status updates  

### Shopping Experience
✅ Product catalog with filters  
✅ Product search  
✅ Shopping cart (session + DB)  
✅ Wishlist functionality  
✅ Product reviews and ratings  

### Order Management
✅ Full order workflow  
✅ Multiple payment methods  
✅ GST invoices  
✅ Order tracking  
✅ Customer order history  

### Admin Features
✅ Dashboard with analytics  
✅ Product & order management  
✅ Stock & user management  

### Marketing Features
✅ Coupons and discounts  
✅ Banners and promotions  
✅ Newsletter subscriptions  

---

## 🔌 API Endpoints

### Authentication
- `POST /register`
- `POST /login`
- `GET /logout`

### Shop Routes
- `GET /`
- `GET /products`
- `GET /product/<slug>`
- `GET /categories`
- `GET /category/<slug>`

### Admin Routes (Admin access required)
- `GET /admin/`
- `GET /admin/products`
- `GET /admin/orders`

### API Utility Endpoints
- `GET /api/cart-count`
- `GET /api/wishlist-count`

---

## 🎨 Template Structure

### Base Template (`base.html`)
- Bootstrap 5 responsive design  
- Navigation with user login state  
- Flash messages  
- Cart count indicator  
- Footer section  

### Auth Templates
- `auth/login.html`  
- `auth/register.html`  

### Shop Templates
- `shop/index.html`  
- `shop/products.html`  
- `shop/product_detail.html`  
- `shop/categories.html`  
- `shop/category_detail.html`  

### Admin Templates
- `admin/dashboard.html`  
- `admin/products.html`  
- `admin/orders.html`  

### Error Templates
- `errors/404.html`  
- `errors/500.html`  
- `errors/403.html`  

---

## ⚙️ Configuration Settings

### config.py

```python
SECRET_KEY = 'your-secret-key'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:pass@localhost/db'
CURRENCY = 'INR'
CURRENCY_SYMBOL = '₹'
DEFAULT_COUNTRY = 'India'
DEFAULT_COUNTRY_CODE = '+91'
DEFAULT_GST_RATE = 18.0
FREE_SHIPPING_THRESHOLD = 999.00
RETURN_PERIOD_DAYS = 10
PAYMENT_METHODS = [
    'cash_on_delivery', 'upi', 'credit_card', 'debit_card', 'netbanking', 'wallet'
]
```

### .env

```env
SECRET_KEY=your-production-secret-key
DATABASE_URL=mysql+pymysql://user:pass@localhost/pavitra_ecommerce
FLASK_ENV=production
```

---

## 📊 Sample Data

### Default Admin
- Email: `admin@pavitra.com`  
- Password: `admin123`  
- Phone: `+91 9876543210`  

### Sample Categories
- Electronics, Smartphones, Fashion, Home & Kitchen  

### Sample Brands
- International: Apple, Samsung, Nike, Adidas, Sony  
- Indian: Micromax, Bata  

### Sample Products
- iPhone 14 Pro - ₹89,900  
- Samsung Galaxy S23 - ₹74,900  
- MacBook Air M2 - ₹1,14,900  
- Nike Air Max 270 - ₹12,999  
- Bata Formal Shoes - ₹2,999  

### Sample Coupons
- `WELCOME10` - 10% off  
- `FREESHIP` - Free shipping  
- `SAVE500` - ₹500 off  

---

## 🛠️ Development Commands

```bash
flask init-db
flask create-admin
flask seed-data
flask run
flask run --port 5001
flask db migrate -m "Migration message"
flask db upgrade
flask db downgrade
```

---

## 🔒 Security Features

- Password hashing (Werkzeug)  
- CSRF protection  
- SQL injection prevention (ORM)  
- XSS protection (templates)  
- Flask-Login session management  
- Admin route protection  

---

## 📈 Scalability Features

- Modular blueprints  
- Connection pooling  
- Caching ready  
- CDN support  
- API-first architecture  

---

## 🔄 Workflow Examples

### Product Purchase Flow
1. Browse → `/products`  
2. View → `/product/<slug>`  
3. Add to cart → `/add-to-cart`  
4. Checkout → `/checkout`  
5. Place order → `/checkout`  
6. Admin processes → `/admin/orders`  

### Stock Management Flow
1. Low stock alert  
2. Admin adds stock  
3. Stock movement logged  
4. Status auto-updated  

---

## 🚨 Error Handling

- 404 - Page not found  
- 500 - Server error  
- 403 - Forbidden access  
- Form validation errors  
- Database constraint errors  
- File upload errors  
