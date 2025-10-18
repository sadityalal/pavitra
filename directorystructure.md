# 🛍️ Pavitra E-commerce Flask Application

## 📋 Overview

**Project Name:** Pavitra E-commerce Platform  
**Framework:** Flask (Python 3.12)  
**Database:** MySQL  
**Frontend:** Bootstrap 5, SCSS, JavaScript  
**Focus:** Scalable e-commerce platform supporting Indian and international customers.  

---

## 🗂️ Directory Structure

```bash

pavitra/
├── app.py # Main Flask application entry point
├── config.py # App configuration (database, secret keys, etc.)
├── extension.py # Flask extensions (SQLAlchemy, Migrate, etc.)
├── requirements.txt # Python dependencies
├── test.py # Utility or testing script
├── update_routes_helper.sh # Helper script to manage routes
├── Database.md # Database schema documentation
├── pavitra_ecommerce_db_documentation.md # In-depth DB documentation
├── pavitra_flask_app_documentation.md # Flask app architecture documentation
│
├── migration_scripts/
│ ├── pavitra.sql # Initial database schema
│ ├── 004_add_history_payment_tables.sql # Migration script for new tables
│
├── models/ # SQLAlchemy models
│ ├── user.py, product.py, order.py, payment.py, etc.
│ ├── order_history.py, wishlist.py, stock.py, coupon.py
│ └── init.py # Model imports
│
├── routes/ # Flask Blueprints and route logic
│ ├── shop_routes.py # Public-facing routes (home, products, etc.)
│ ├── auth_routes.py # Authentication routes (login, register)
│ └── admin_routes.py # Admin dashboard, CRUD operations
│
├── templates/ # HTML templates (Jinja2)
│ ├── base.html # Main template layout
│ ├── index.html # Homepage
│ ├── admin/ # Admin panel templates
│ ├── auth/ # Login & Register
│ ├── shop/ # Front-facing store templates
│ ├── checkout/ # Checkout, Payment, Confirmation
│ ├── static_pages/ # FAQ, Privacy, Return, Shipping
│ └── errors/ # 403, 404, 500 error pages
│
├── static/ # Static assets
│ ├── css/ # Stylesheets (admin_base.css, main.css)
│ ├── js/ # JavaScript (cart.js, checkout.js, admin scripts)
│ ├── img/ # All product, team, testimonial, and logo images
│ ├── scss/ # SCSS source files
│ ├── uploads/ # Dynamic image uploads by admins
│ └── vendor/ # Third-party libraries (Bootstrap, AOS, Swiper, etc.)
│
└── pycache/ # Compiled Python cache files

```



---

## ⚙️ Key Components

### 1. **App Initialization (`app.py`)**
- Creates Flask app instance.
- Loads config from `config.py`.
- Registers blueprints (`shop`, `auth`, `admin`).
- Initializes extensions from `extension.py`.

### 2. **Configuration (`config.py`)**
- Contains environment variables, DB credentials, and app settings.
- Follows environment-based configuration pattern (Dev/Prod).

### 3. **Database & Models (`models/`)**
- Defines ORM models using SQLAlchemy.
- Handles relationships between users, products, orders, reviews, and payments.

### 4. **Routing (`routes/`)**
- Split into modular blueprints:
  - `shop_routes.py`: Customer-facing routes.
  - `auth_routes.py`: User login and registration.
  - `admin_routes.py`: Backend management routes.

### 5. **Templates (`templates/`)**
- Uses Jinja2 templating engine.
- Organized into subfolders (admin, auth, shop, etc.).
- Common `base.html` extends across all pages.

### 6. **Static Assets (`static/`)**
- Follows standard Flask convention.
- Organized by type (CSS, JS, Images, SCSS, Vendor).
- Includes modern libraries like AOS, Swiper, and Bootstrap.

### 7. **Database Migration Scripts (`migration_scripts/`)**
- Stores schema creation and updates.
- Used for consistent database evolution and rollback support.

---

## 🧩 Supporting Files

| File | Purpose |
|------|----------|
| `requirements.txt` | Lists all Python dependencies |
| `Database.md` | Database table relationships and ER design |
| `pavitra_flask_app_documentation.md` | In-depth Flask architecture |
| `update_routes_helper.sh` | Route maintenance helper script |
| `test.py` | Script for route or model validation |

---

## 🧠 Development Notes

- **Blueprint-based architecture** keeps routes modular.
- **SQLAlchemy ORM** for easy DB operations.
- **Bootstrap 5 + Custom JS** for responsive frontend.
- **Vendor libraries** for animations, sliders, and counters.
- **Error pages** (403, 404, 500) ensure better user experience.
- **Separation of concerns** between backend logic and frontend assets.

---

## 🧾 Future Enhancements

- Add **Celery + Redis** for async tasks (e.g., email, reports).
- Implement **Elasticsearch** for product search.
- Add **payment gateway integration** (Stripe, Razorpay).
- Include **Docker setup** for environment portability.
- Integrate **CI/CD pipeline** (GitHub Actions or Jenkins).

---

## 📦 Summary

| Category | Description |
|-----------|--------------|
| **Framework** | Flask (Python 3.12) |
| **Database** | MySQL |
| **Frontend** | Bootstrap 5, jQuery, SCSS |
| **Architecture** | Modular Blueprints |
| **Total Files** | 248 |
| **Directories** | 45 |
| **Focus** | Scalable, maintainable e-commerce solution |

---

📘 *Generated: Pavitra E-commerce Flask Project Documentation – 2025*


