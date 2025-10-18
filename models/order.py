# models/order.py
from extension import db
from datetime import datetime
import uuid
import random
import string


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Indian Pricing (INR)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    shipping_amount = db.Column(db.Numeric(12, 2), default=0)
    tax_amount = db.Column(db.Numeric(12, 2), default=0)
    discount_amount = db.Column(db.Numeric(12, 2), default=0)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)

    # Status
    status = db.Column(db.String(20), default='pending')
    payment_status = db.Column(db.String(20), default='pending')

    # Indian Payment Methods
    payment_method = db.Column(db.String(100))
    payment_gateway = db.Column(db.String(100))
    transaction_id = db.Column(db.String(255))
    upi_id = db.Column(db.String(255))

    # Shipping
    shipping_method = db.Column(db.String(100))
    tracking_number = db.Column(db.String(100))
    shipping_address = db.Column(db.JSON)
    billing_address = db.Column(db.JSON)

    # Customer info
    customer_note = db.Column(db.Text)
    admin_note = db.Column(db.Text)

    # Indian order specifics
    is_gst_invoice = db.Column(db.Boolean, default=True)
    gst_number = db.Column(db.String(15))

    # Timestamps
    paid_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)

    estimated_delivery = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    coupon_usages = db.relationship('CouponUsage', backref='order', lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.order_number:
            self.order_number = self.generate_order_number()

    def generate_order_number(self):
        """Generate unique order number"""
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f'ORD-{timestamp}-{random_str}'

    def get_item_count(self):
        """Get total items count in order"""
        return sum(item.quantity for item in self.items)

    def can_be_cancelled(self):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'confirmed']

    def calculate_totals(self):
        """Recalculate order totals"""
        self.subtotal = sum(item.total_price for item in self.items)
        # Apply tax, shipping, discounts
        self.total_amount = self.subtotal + self.shipping_amount + self.tax_amount - self.discount_amount

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount),
            'status': self.status,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'item_count': self.get_item_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'estimated_delivery': self.estimated_delivery.isoformat() if self.estimated_delivery else None
        }


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    variation_id = db.Column(db.Integer, db.ForeignKey('product_variations.id'))

    product_name = db.Column(db.String(255), nullable=False)
    product_sku = db.Column(db.String(100), nullable=False)
    product_image = db.Column(db.String(500))

    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(12, 2), nullable=False)

    # GST details
    gst_rate = db.Column(db.Numeric(5, 2), default=18.00)
    gst_amount = db.Column(db.Numeric(10, 2), default=0)

    variation_attributes = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def calculate_gst(self):
        """Calculate GST amount for this item"""
        self.gst_amount = (self.total_price * self.gst_rate) / 100

    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'product_sku': self.product_sku,
            'unit_price': float(self.unit_price),
            'quantity': self.quantity,
            'total_price': float(self.total_price),
            'product_image': self.product_image
        }