# models/brand.py
from extension import db
from datetime import datetime
import uuid


class Brand(db.Model):
    __tablename__ = 'brands'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(500))
    website_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    # Indian market info
    is_indian_brand = db.Column(db.Boolean, default=False)
    brand_origin_country = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = db.relationship('Product', backref='brand', lazy=True)

    def get_product_count(self):
        """Get active products count for this brand"""
        from .product import Product
        return Product.query.filter_by(brand_id=self.id, status='active').count()

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'logo_url': self.logo_url,
            'is_indian_brand': self.is_indian_brand,
            'product_count': self.get_product_count()
        }