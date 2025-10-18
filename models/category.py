# models/category.py
from extension import db
from datetime import datetime
import uuid


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    name_hindi = db.Column(db.String(255))
    slug = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    description_hindi = db.Column(db.Text)
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    image_url = db.Column(db.String(500))
    banner_url = db.Column(db.String(500))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)

    # Indian tax information
    gst_slab = db.Column(db.Numeric(5, 2), default=18.00)
    hsn_code = db.Column(db.String(10))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Self-referential relationship for parent-child categories
    parent = db.relationship('Category', remote_side=[id], backref='children')

    # Relationships
    products = db.relationship('Product', backref='category', lazy=True)

    def get_product_count(self):
        """Get active products count in this category"""
        from .product import Product
        return Product.query.filter_by(category_id=self.id, status='active').count()

    def get_featured_products(self, limit=8):
        """Get featured products from this category"""
        from .product import Product
        return Product.query.filter_by(
            category_id=self.id,
            is_featured=True,
            status='active'
        ).limit(limit).all()

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'name_hindi': self.name_hindi,
            'slug': self.slug,
            'description': self.description,
            'image_url': self.image_url,
            'parent_id': self.parent_id,
            'product_count': self.get_product_count(),
            'is_featured': self.is_featured
        }