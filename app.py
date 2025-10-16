from flask import Flask
from config import Config
from extension import db
from models.category import Category
from models.product import Product


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize SQLAlchemy with app
    db.init_app(app)

    # Context processor to make common data available to all templates
    @app.context_processor
    def inject_common_data():
        try:
            categories = Category.query.filter_by(is_active=True).all()
            featured_products = Product.query.filter_by(
                is_featured=True,
                is_active=True
            ).limit(4).all()
            new_arrivals = Product.query.filter_by(
                is_active=True
            ).order_by(Product.created_at.desc()).limit(4).all()

            return dict(
                categories=categories,
                featured_products=featured_products,
                new_arrivals=new_arrivals
            )
        except Exception as e:
            print(f"Context processor error: {e}")
            return dict(
                categories=[],
                featured_products=[],
                new_arrivals=[]
            )

    # Import and register blueprints AFTER db.init_app
    from routes.auth_routes import auth_bp
    from routes.shop_routes import shop_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(admin_bp)

    # Create tables inside app context
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)