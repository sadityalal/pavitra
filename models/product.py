# models/product.py
from extension import db
from datetime import datetime
import uuid
from sqlalchemy import event

# Association tables for many-to-many relationships
product_attribute_association = db.Table('product_attribute_association',
                                         db.Column('product_id', db.Integer, db.ForeignKey('products.id'),
                                                   primary_key=True),
                                         db.Column('attribute_value_id', db.Integer,
                                                   db.ForeignKey('product_attribute_values.id'), primary_key=True),
                                         db.Column('created_at', db.DateTime, default=datetime.utcnow)
                                         )

product_tag_relations = db.Table('product_tag_relations',
                                 db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
                                 db.Column('tag_id', db.Integer, db.ForeignKey('product_tags.id'), primary_key=True),
                                 db.Column('created_at', db.DateTime, default=datetime.utcnow)
                                 )


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    sku = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    short_description = db.Column(db.Text)
    description = db.Column(db.Text)
    specification = db.Column(db.JSON)

    # Indian Pricing (INR)
    base_price = db.Column(db.Numeric(12, 2), nullable=False)
    compare_price = db.Column(db.Numeric(12, 2))
    cost_price = db.Column(db.Numeric(12, 2))

    # Indian Taxation
    gst_rate = db.Column(db.Numeric(5, 2), default=18.00)
    hsn_code = db.Column(db.String(10))
    is_gst_inclusive = db.Column(db.Boolean, default=True)

    # Inventory Management
    track_inventory = db.Column(db.Boolean, default=True)
    stock_quantity = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Integer, default=5)
    allow_backorders = db.Column(db.Boolean, default=False)
    max_cart_quantity = db.Column(db.Integer, default=10)
    min_cart_quantity = db.Column(db.Integer, default=1)
    stock_status = db.Column(db.String(20), default='out_of_stock')

    # Product Type
    product_type = db.Column(db.String(20), default='simple')
    is_virtual = db.Column(db.Boolean, default=False)
    is_downloadable = db.Column(db.Boolean, default=False)

    # Shipping (Metric system for India)
    weight_grams = db.Column(db.Numeric(8, 2))
    length_cm = db.Column(db.Numeric(8, 2))
    width_cm = db.Column(db.Numeric(8, 2))
    height_cm = db.Column(db.Numeric(8, 2))

    # Media
    main_image_url = db.Column(db.String(500))
    image_gallery = db.Column(db.JSON)

    # Relations
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'))

    # Status & SEO
    status = db.Column(db.String(20), default='draft')
    is_featured = db.Column(db.Boolean, default=False)
    is_trending = db.Column(db.Boolean, default=False)
    is_bestseller = db.Column(db.Boolean, default=False)
    is_on_sale = db.Column(db.Boolean, default=False)

    # Indian e-commerce specific
    is_returnable = db.Column(db.Boolean, default=True)
    return_period_days = db.Column(db.Integer, default=10)
    warranty_period_months = db.Column(db.Integer, default=0)

    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)
    meta_keywords = db.Column(db.Text)

    # Analytics
    view_count = db.Column(db.Integer, default=0)
    wishlist_count = db.Column(db.Integer, default=0)
    total_sold = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # FIXED Relationships
    variations = db.relationship('ProductVariation', backref='product', lazy=True, cascade='all, delete-orphan')

    # Fixed attributes relationship using proper association table
    attribute_values = db.relationship('ProductAttributeValue',
                                       secondary=product_attribute_association,
                                       backref='products',
                                       lazy='dynamic')

    # Fixed tags relationship using proper association table
    tags = db.relationship('ProductTag',
                           secondary=product_tag_relations,
                           backref='products',
                           lazy='dynamic')

    reviews = db.relationship('Review', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    wishlists = db.relationship('Wishlist', backref='product', lazy=True)
    stock_movements = db.relationship('StockMovement', backref='product', lazy=True)

    def update_stock_status(self):
        """Update stock status based on current quantity"""
        if not self.track_inventory:
            self.stock_status = 'in_stock'
            return

        if self.stock_quantity <= 0:
            if self.allow_backorders:
                self.stock_status = 'on_backorder'
            else:
                self.stock_status = 'out_of_stock'
        elif self.stock_quantity <= self.low_stock_threshold:
            self.stock_status = 'low_stock'
        else:
            self.stock_status = 'in_stock'

    def add_stock(self, quantity, reason="Stock adjustment", performed_by=None, reference_type="adjustment",
                  reference_id=None):
        """Add stock to product"""
        if quantity <= 0:
            return False

        stock_before = self.stock_quantity
        self.stock_quantity += quantity
        self.update_stock_status()

        # Record stock movement
        from .stock import StockMovement
        movement = StockMovement(
            product_id=self.id,
            movement_type='purchase',
            quantity=quantity,
            stock_before=stock_before,
            stock_after=self.stock_quantity,
            reason=reason,
            performed_by=performed_by,
            reference_type=reference_type,
            reference_id=reference_id
        )
        db.session.add(movement)
        return True

    def reduce_stock(self, quantity, reason="Sale", performed_by=None, reference_type="order", reference_id=None):
        """Reduce stock from product"""
        if quantity <= 0:
            return False

        if self.stock_quantity < quantity and not self.allow_backorders:
            return False

        stock_before = self.stock_quantity
        self.stock_quantity = max(0, self.stock_quantity - quantity)
        self.total_sold += quantity
        self.update_stock_status()

        # Record stock movement
        from .stock import StockMovement
        movement = StockMovement(
            product_id=self.id,
            movement_type='sale',
            quantity=-quantity,
            stock_before=stock_before,
            stock_after=self.stock_quantity,
            reason=reason,
            performed_by=performed_by,
            reference_type=reference_type,
            reference_id=reference_id
        )
        db.session.add(movement)
        return True

    def is_in_stock(self):
        """Check if product is available for purchase"""
        if not self.track_inventory:
            return True
        return self.stock_status in ['in_stock', 'low_stock', 'on_backorder']

    def get_available_quantity(self):
        """Get available quantity for purchase"""
        if not self.track_inventory:
            return 999
        return self.stock_quantity

    def get_discount_percentage(self):
        """Calculate discount percentage"""
        if self.compare_price and self.compare_price > self.base_price:
            return int(((self.compare_price - self.base_price) / self.compare_price) * 100)
        return 0

    def get_average_rating(self):
        """Calculate average rating from approved reviews"""
        if not self.reviews:
            return 0
        approved_reviews = [r for r in self.reviews if r.status == 'approved']
        if not approved_reviews:
            return 0
        return sum(r.rating for r in approved_reviews) / len(approved_reviews)

    def get_review_count(self):
        """Get count of approved reviews"""
        return len([r for r in self.reviews if r.status == 'approved'])

    def get_attributes_dict(self):
        """Get product attributes as dictionary"""
        return {av.attribute.name: av.value for av in self.attribute_values}

    def add_attribute(self, attribute_value):
        """Add attribute value to product"""
        if attribute_value not in self.attribute_values:
            self.attribute_values.append(attribute_value)

    def remove_attribute(self, attribute_value):
        """Remove attribute value from product"""
        if attribute_value in self.attribute_values:
            self.attribute_values.remove(attribute_value)

    def add_tag(self, tag):
        """Add tag to product"""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        """Remove tag from product"""
        if tag in self.tags:
            self.tags.remove(tag)

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'slug': self.slug,
            'base_price': float(self.base_price),
            'compare_price': float(self.compare_price) if self.compare_price else None,
            'stock_quantity': self.stock_quantity,
            'stock_status': self.stock_status,
            'is_in_stock': self.is_in_stock(),
            'available_quantity': self.get_available_quantity(),
            'main_image_url': self.main_image_url,
            'is_featured': self.is_featured,
            'is_on_sale': self.is_on_sale,
            'discount_percentage': self.get_discount_percentage(),
            'average_rating': self.get_average_rating(),
            'review_count': self.get_review_count(),
            'category_id': self.category_id,
            'brand_id': self.brand_id,
            'attributes': self.get_attributes_dict(),
            'tags': [tag.name for tag in self.tags]
        }

    def get_main_image(self):
        """Get main product image URL with fallback"""
        from flask import url_for
        return self.main_image_url or url_for('static', filename='img/product/placeholder.jpg')

    def is_low_stock(self):
        """Check if product is low in stock"""
        if not self.track_inventory:
            return False
        return (self.stock_quantity > 0 and
                self.stock_quantity <= self.low_stock_threshold)

    # Template compatibility methods
    def get_image_url(self):
        """Alias for template compatibility"""
        return self.get_main_image()

    # Ensure these existing methods work properly
    def is_in_stock(self):
        """Check if product is available for purchase"""
        if not self.track_inventory:
            return True
        return self.stock_status in ['in_stock', 'low_stock', 'on_backorder']

    def get_discount_percentage(self):
        """Calculate discount percentage"""
        if self.compare_price and self.compare_price > self.base_price:
            discount = ((self.compare_price - self.base_price) / self.compare_price) * 100
            return int(round(discount))
        return 0

    def get_average_rating(self):
        """Calculate average rating from approved reviews"""
        if not self.reviews:
            return 0
        approved_reviews = [r for r in self.reviews if getattr(r, 'status', 'approved') == 'approved']
        if not approved_reviews:
            return 0
        return round(sum(r.rating for r in approved_reviews) / len(approved_reviews), 1)

    def get_review_count(self):
        """Get count of approved reviews"""
        if not self.reviews:
            return 0
        return len([r for r in self.reviews if getattr(r, 'status', 'approved') == 'approved'])

    @property
    def image_url(self):
        """Template compatibility - alias for main_image_url"""
        return self.main_image_url

    @property
    def price(self):
        """Template compatibility - alias for base_price"""
        return self.base_price

# @property
# def compare_price(self):
#     """Template compatibility - ensure it returns numeric value"""
#     return self.compare_price if self.compare_price else 0


class ProductAttribute(db.Model):
    __tablename__ = 'product_attributes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    type = db.Column(db.String(20), default='select')
    is_visible = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    values = db.relationship('ProductAttributeValue', backref='attribute', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'type': self.type,
            'values': [value.to_dict() for value in self.values]
        }


class ProductAttributeValue(db.Model):
    __tablename__ = 'product_attribute_values'

    id = db.Column(db.Integer, primary_key=True)
    attribute_id = db.Column(db.Integer, db.ForeignKey('product_attributes.id'), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    color_code = db.Column(db.String(7))
    image_url = db.Column(db.String(500))
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'attribute_id': self.attribute_id,
            'value': self.value,
            'color_code': self.color_code,
            'image_url': self.image_url
        }


class ProductVariation(db.Model):
    __tablename__ = 'product_variations'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=False)

    # Pricing (INR)
    price = db.Column(db.Numeric(12, 2))
    compare_price = db.Column(db.Numeric(12, 2))
    cost_price = db.Column(db.Numeric(12, 2))

    # Individual stock management
    stock_quantity = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Integer, default=5)
    allow_backorders = db.Column(db.Boolean, default=False)
    stock_status = db.Column(db.String(20), default='out_of_stock')

    # Physical attributes
    weight_grams = db.Column(db.Numeric(8, 2))
    length_cm = db.Column(db.Numeric(8, 2))
    width_cm = db.Column(db.Numeric(8, 2))
    height_cm = db.Column(db.Numeric(8, 2))

    image_url = db.Column(db.String(500))
    is_default = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    variation_attributes = db.relationship('VariationAttribute', backref='variation', lazy=True,
                                           cascade='all, delete-orphan')

    def update_stock_status(self):
        """Update variation stock status"""
        if self.stock_quantity <= 0:
            if self.allow_backorders:
                self.stock_status = 'on_backorder'
            else:
                self.stock_status = 'out_of_stock'
        elif self.stock_quantity <= self.low_stock_threshold:
            self.stock_status = 'low_stock'
        else:
            self.stock_status = 'in_stock'

    def is_in_stock(self):
        """Check if variation is in stock"""
        return self.stock_status in ['in_stock', 'low_stock', 'on_backorder']

    def get_attributes(self):
        """Get variation attributes as dictionary"""
        return {va.attribute.name: va.attribute_value.value for va in self.variation_attributes}

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'sku': self.sku,
            'price': float(self.price) if self.price else None,
            'stock_quantity': self.stock_quantity,
            'stock_status': self.stock_status,
            'is_in_stock': self.is_in_stock(),
            'image_url': self.image_url,
            'attributes': self.get_attributes()
        }


class VariationAttribute(db.Model):
    __tablename__ = 'variation_attributes'

    id = db.Column(db.Integer, primary_key=True)
    variation_id = db.Column(db.Integer, db.ForeignKey('product_variations.id'), nullable=False)
    attribute_id = db.Column(db.Integer, db.ForeignKey('product_attributes.id'), nullable=False)
    attribute_value_id = db.Column(db.Integer, db.ForeignKey('product_attribute_values.id'), nullable=False)

    # Relationships
    attribute = db.relationship('ProductAttribute')
    attribute_value = db.relationship('ProductAttributeValue')


class ProductTag(db.Model):
    __tablename__ = 'product_tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug
        }

