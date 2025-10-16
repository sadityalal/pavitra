from extension import db
from datetime import datetime


class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    discount_type = db.Column(db.String(20), default='percentage')  # percentage or fixed
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    minimum_amount = db.Column(db.Numeric(10, 2), default=0)
    maximum_discount = db.Column(db.Numeric(10, 2))
    usage_limit = db.Column(db.Integer)
    used_count = db.Column(db.Integer, default=0)
    valid_from = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_valid(self, cart_total=0):
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        if cart_total < self.minimum_amount:
            return False
        return True

    def calculate_discount(self, cart_total):
        if not self.is_valid(cart_total):
            return 0

        if self.discount_type == 'percentage':
            discount = (cart_total * self.discount_value) / 100
            if self.maximum_discount and discount > self.maximum_discount:
                return float(self.maximum_discount)
            return float(discount)
        else:  # fixed
            return float(self.discount_value)