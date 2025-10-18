# models/stock.py
from extension import db
from datetime import datetime
import uuid


class StockMovement(db.Model):
    __tablename__ = 'stock_movements'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    variation_id = db.Column(db.Integer, db.ForeignKey('product_variations.id'))

    movement_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    stock_before = db.Column(db.Integer, nullable=False)
    stock_after = db.Column(db.Integer, nullable=False)

    reference_type = db.Column(db.String(20), default='other')
    reference_id = db.Column(db.Integer)
    reason = db.Column(db.Text)

    performed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    performed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    variation = db.relationship('ProductVariation', backref='stock_movements')
    performer = db.relationship('User', backref='stock_movements')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'movement_type': self.movement_type,
            'quantity': self.quantity,
            'stock_before': self.stock_before,
            'stock_after': self.stock_after,
            'reason': self.reason,
            'performed_at': self.performed_at.isoformat() if self.performed_at else None
        }


class StockAlert(db.Model):
    __tablename__ = 'stock_alerts'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    variation_id = db.Column(db.Integer, db.ForeignKey('product_variations.id'))

    alert_type = db.Column(db.String(20), nullable=False)
    current_stock = db.Column(db.Integer, nullable=False)
    threshold = db.Column(db.Integer, nullable=False)

    is_resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    product = db.relationship('Product', backref='stock_alerts')
    variation = db.relationship('ProductVariation', backref='stock_alerts')
    resolver = db.relationship('User', backref='resolved_alerts')

    def resolve(self, resolved_by):
        """Mark alert as resolved"""
        self.is_resolved = True
        self.resolved_at = datetime.utcnow()
        self.resolved_by = resolved_by