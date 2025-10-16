from extension import db
from datetime import datetime
import json


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    short_description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    compare_price = db.Column(db.Numeric(10, 2))
    cost_price = db.Column(db.Numeric(10, 2))
    sku = db.Column(db.String(100), unique=True)
    barcode = db.Column(db.String(100))
    weight = db.Column(db.Numeric(8, 2))
    dimensions = db.Column(db.String(50))
    image_url = db.Column(db.String(255))
    gallery_images = db.Column(db.JSON)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    inventory_quantity = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Integer, default=5)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    tags = db.Column(db.JSON)
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)
    slug = db.Column(db.String(255), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    attributes = db.relationship('ProductAttribute', backref='product', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    wishlists = db.relationship('Wishlist', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True)

    def is_in_stock(self):
        return self.inventory_quantity > 0

    def is_low_stock(self):
        return 0 < self.inventory_quantity <= self.low_stock_threshold

    def get_average_rating(self):
        if not self.reviews:
            return 0
        approved_reviews = [r for r in self.reviews if r.is_approved]
        if not approved_reviews:
            return 0
        return sum(r.rating for r in approved_reviews) / len(approved_reviews)

    def get_review_count(self):
        return len([r for r in self.reviews if r.is_approved])

    def get_discount_percentage(self):
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0

    def is_new(self):
        # Consider product as new if created within last 30 days
        from datetime import timedelta
        return datetime.utcnow() - self.created_at < timedelta(days=30)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'short_description': self.short_description,
            'price': float(self.price),
            'compare_price': float(self.compare_price) if self.compare_price else None,
            'image_url': self.image_url,
            'category_id': self.category_id,
            'inventory_quantity': self.inventory_quantity,
            'is_featured': self.is_featured,
            'is_active': self.is_active,
            'slug': self.slug,
            'average_rating': self.get_average_rating(),
            'review_count': self.get_review_count(),
            'discount_percentage': self.get_discount_percentage(),
            'is_in_stock': self.is_in_stock(),
            'is_low_stock': self.is_low_stock()
        }


class ProductAttribute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    attribute_name = db.Column(db.String(100), nullable=False)
    attribute_value = db.Column(db.String(255), nullable=False)
    additional_price = db.Column(db.Numeric(10, 2), default=0)
    inventory = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)