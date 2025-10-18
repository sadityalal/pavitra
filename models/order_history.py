# models/order_history.py
from extension import db
from datetime import datetime


class OrderHistory(db.Model):
    __tablename__ = 'order_history'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)

    # What changed
    field_changed = db.Column(db.String(100), nullable=False)  # status, payment_status, etc.
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)

    # Who made the change
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # User ID or system
    change_type = db.Column(db.String(20), default='system')  # system, admin, customer

    # Context
    reason = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    order = db.relationship('Order', backref='history_entries')
    changed_by_user = db.relationship('User', backref='order_changes')

    def to_dict(self):
        return {
            'id': self.id,
            'field_changed': self.field_changed,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'change_type': self.change_type,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'changed_by_name': self.changed_by_user.get_full_name() if self.changed_by_user else 'System'
        }