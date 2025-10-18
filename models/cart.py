# models/cart.py
from extension import db
from datetime import datetime


class ShoppingCart(db.Model):
    __tablename__ = 'shopping_cart'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    variation_id = db.Column(db.Integer, db.ForeignKey('product_variations.id'))
    quantity = db.Column(db.Integer, nullable=False, default=1)
    cart_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = db.relationship('Product', backref='cart_items')
    variation = db.relationship('ProductVariation', backref='cart_items')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'variation_id': self.variation_id,
            'quantity': self.quantity,
            'product': self.product.to_dict() if self.product else None
        }