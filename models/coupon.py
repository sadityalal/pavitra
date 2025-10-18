# models/coupon.py
from extension import db
from datetime import datetime
import uuid


class Coupon(db.Model):
    __tablename__ = 'coupons'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    # Discount configuration (INR)
    discount_type = db.Column(db.String(20), default='percentage')
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    maximum_discount_amount = db.Column(db.Numeric(10, 2))
    minimum_order_amount = db.Column(db.Numeric(10, 2), default=0)

    # Usage limits
    usage_limit = db.Column(db.Integer)
    usage_limit_per_user = db.Column(db.Integer)
    used_count = db.Column(db.Integer, default=0)

    # Validity
    valid_from = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    # Applicability
    apply_to = db.Column(db.String(20), default='all_products')
    applicable_categories = db.Column(db.JSON)
    applicable_products = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    usages = db.relationship('CouponUsage', backref='coupon', lazy=True)

    def is_valid(self, user_id=None, cart_total=0):
        """Check if coupon is valid for use"""
        from datetime import datetime
        now = datetime.utcnow()

        if not self.is_active:
            return False, "Coupon is not active"

        if self.valid_from and now < self.valid_from:
            return False, "Coupon is not yet valid"

        if self.valid_until and now > self.valid_until:
            return False, "Coupon has expired"

        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, "Coupon usage limit reached"

        if cart_total < self.minimum_order_amount:
            return False, f"Minimum order amount is ₹{self.minimum_order_amount}"

        # Check per user limit
        if user_id and self.usage_limit_per_user:
            user_usage_count = CouponUsage.query.filter_by(
                coupon_id=self.id, user_id=user_id
            ).count()
            if user_usage_count >= self.usage_limit_per_user:
                return False, "Usage limit reached for this user"

        return True, "Valid coupon"

    def calculate_discount(self, cart_total):
        """Calculate discount amount"""
        if self.discount_type == 'percentage':
            discount = (cart_total * self.discount_value) / 100
            if self.maximum_discount_amount and discount > self.maximum_discount_amount:
                return float(self.maximum_discount_amount)
            return float(discount)
        elif self.discount_type == 'fixed_amount':
            return float(self.discount_value)
        else:  # free_shipping
            return 0

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'discount_type': self.discount_type,
            'discount_value': float(self.discount_value),
            'minimum_order_amount': float(self.minimum_order_amount) if self.minimum_order_amount else None,
            'maximum_discount_amount': float(self.maximum_discount_amount) if self.maximum_discount_amount else None,
            'is_active': self.is_active
        }


class CouponUsage(db.Model):
    __tablename__ = 'coupon_usage'

    id = db.Column(db.Integer, primary_key=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False)
    used_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='coupon_usages')