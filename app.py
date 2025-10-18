# app.py
import datetime
from datetime import timedelta

from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_login import current_user, logout_user
from config import config
from extension import db, login_manager, migrate, csrf  # Import csrf
from models.user import User
import os


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Session timeout handling - AUTO LOGOUT AFTER 10 MINUTES INACTIVITY
    @app.before_request
    def before_request():
        """Handle session timeout using session storage - Auto logout after 10 minutes"""
        if current_user.is_authenticated:
            now = datetime.datetime.utcnow()
            last_activity_str = session.get('last_activity')

            # Check if we have last activity time
            if last_activity_str:
                try:
                    last_activity = datetime.datetime.fromisoformat(last_activity_str)
                    # Check session timeout (10 minutes)
                    if now - last_activity > timedelta(minutes=10):
                        logout_user()
                        session.clear()
                        flash('Your session has expired due to inactivity. Please login again.', 'info')
                        return redirect(url_for('auth.login'))
                except (ValueError, TypeError):
                    # If there's an issue with the stored time, treat as expired
                    logout_user()
                    session.clear()
                    flash('Your session has expired. Please login again.', 'info')
                    return redirect(url_for('auth.login'))

            # Update last activity time in session
            session['last_activity'] = now.isoformat()

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Remove the old CSRF context processor since Flask-WTF handles it
    # Keep your other context processors
    @app.context_processor
    def inject_global_vars():
        """Inject global variables into all templates"""
        from models.category import Category
        from models.product import Product
        from models.brand import Brand

        try:
            categories = Category.query.filter_by(is_active=True).all()
            featured_products = Product.query.filter_by(
                is_featured=True,
                status='active'
            ).limit(8).all()
            brands = Brand.query.filter_by(is_active=True).all()

            # Create site_settings fallback from config
            site_settings = {
                'free_shipping_threshold': str(app.config.get('FREE_SHIPPING_THRESHOLD', 999)),
                'return_period_days': str(app.config.get('RETURN_PERIOD_DAYS', 10)),
                'gst_number': '',
                'store_name': 'Pavitra Enterprises',
                'store_email': 'support@pavitraenterprises.com',
                'store_phone': '+91-9711317009',
                'currency': app.config.get('CURRENCY', 'INR'),
                'currency_symbol': app.config.get('CURRENCY_SYMBOL', '₹')
            }

        except Exception as e:
            print(f"Error loading global data: {e}")
            categories = []
            featured_products = []
            brands = []
            site_settings = {}

        return dict(
            categories=categories,
            featured_products=featured_products,
            brands=brands,
            currency_symbol='₹',
            site_settings=site_settings
        )

    @app.context_processor
    def inject_user_data():
        """Inject user-specific data"""
        from models.wishlist import Wishlist
        from models.cart import ShoppingCart

        wishlist_count = 0
        cart_count = 0

        if current_user.is_authenticated:
            wishlist_count = Wishlist.query.filter_by(user_id=current_user.id).count()
            cart_count = ShoppingCart.query.filter_by(user_id=current_user.id).count()
        else:
            # Session-based cart for guests
            if 'cart' in session:
                cart_count = sum(item.get('quantity', 0) for item in session['cart'])

        return dict(
            user_wishlist_count=wishlist_count,
            cart_count=cart_count
        )

    # Remove the old inject_csrf_token context processor
    # Flask-WTF automatically injects csrf_token into templates

    # Register blueprints
    register_blueprints(app)

    # Error handlers
    register_error_handlers(app)

    # CLI commands
    register_commands(app)

    return app


def register_blueprints(app):
    """Register all blueprints"""
    from routes.auth_routes import auth_bp
    from routes.shop_routes import shop_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(admin_bp)


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403


def register_commands(app):
    """Register CLI commands"""

    @app.cli.command('init-db')
    def init_db():
        """Initialize the database"""
        db.create_all()
        print("Database tables created successfully!")

    @app.cli.command('create-admin')
    def create_admin():
        """Create an admin user"""
        from werkzeug.security import generate_password_hash

        admin = User(
            email='admin@pavitra.com',
            first_name='Admin',
            last_name='User',
            phone='9876543210',
            country_code='+91',
            is_admin=True,
            email_verified=True
        )
        admin.set_password('admin123')

        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin@pavitra.com / admin123")

    @app.cli.command('seed-data')
    def seed_data():
        """Seed sample data"""
        from models.category import Category
        from models.brand import Brand
        from models.product import Product

        # Add sample categories
        categories = [
            Category(name='Electronics', name_hindi='इलेक्ट्रॉनिक्स', slug='electronics', is_featured=True),
            Category(name='Smartphones', name_hindi='स्मार्टफोन', slug='smartphones', parent_id=1),
            Category(name='Fashion', name_hindi='फैशन', slug='fashion', is_featured=True),
            Category(name='Home & Kitchen', name_hindi='घर और रसोई', slug='home-kitchen', is_featured=True),
        ]

        for category in categories:
            if not Category.query.filter_by(slug=category.slug).first():
                db.session.add(category)

        # Add sample brands
        brands = [
            Brand(name='Apple', slug='apple', is_indian_brand=False),
            Brand(name='Samsung', slug='samsung', is_indian_brand=False),
            Brand(name='Nike', slug='nike', is_indian_brand=False),
            Brand(name='Adidas', slug='adidas', is_indian_brand=False),
            Brand(name='Micromax', slug='micromax', is_indian_brand=True),
            Brand(name='Bata', slug='bata', is_indian_brand=True),
        ]

        for brand in brands:
            if not Brand.query.filter_by(slug=brand.slug).first():
                db.session.add(brand)

        db.session.commit()
        print("Sample data seeded successfully!")



if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        db.create_all()

    app.run(debug=True, host='0.0.0.0', port=5001)