# models/payment.py
from extension import db
from datetime import datetime
import uuid


class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Payment method type
    method_type = db.Column(db.String(50), nullable=False)  # upi, card, netbanking, wallet

    # Common fields
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # UPI specific fields
    upi_id = db.Column(db.String(255))
    upi_app = db.Column(db.String(100))  # Google Pay, PhonePe, PayTM, etc.

    # Card specific fields
    card_last_four = db.Column(db.String(4))
    card_type = db.Column(db.String(50))  # visa, mastercard, rupay
    card_network = db.Column(db.String(100))
    expiry_month = db.Column(db.Integer)
    expiry_year = db.Column(db.Integer)
    card_holder_name = db.Column(db.String(255))

    # Net Banking fields
    bank_name = db.Column(db.String(255))
    account_last_four = db.Column(db.String(4))

    # Wallet fields
    wallet_provider = db.Column(db.String(100))  # PayTM, Amazon Pay, etc.
    wallet_id = db.Column(db.String(255))

    # Security
    token = db.Column(db.String(500))  # For payment gateway tokens

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='payment_methods')

    def to_dict(self):
        """Convert to safe dictionary (exclude sensitive data)"""
        data = {
            'id': self.id,
            'method_type': self.method_type,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if self.method_type == 'upi':
            data.update({
                'upi_id': self.mask_upi_id(),
                'upi_app': self.upi_app
            })
        elif self.method_type == 'card':
            data.update({
                'card_last_four': self.card_last_four,
                'card_type': self.card_type,
                'card_network': self.card_network,
                'expiry_month': self.expiry_month,
                'expiry_year': self.expiry_year,
                'card_holder_name': self.card_holder_name
            })
        elif self.method_type == 'netbanking':
            data.update({
                'bank_name': self.bank_name,
                'account_last_four': self.account_last_four
            })
        elif self.method_type == 'wallet':
            data.update({
                'wallet_provider': self.wallet_provider,
                'wallet_id': self.mask_wallet_id()
            })

        return data

    def mask_upi_id(self):
        """Mask UPI ID for display"""
        if not self.upi_id:
            return None
        parts = self.upi_id.split('@')
        if len(parts) == 2:
            return f"***{parts[0][-2:]}@{parts[1]}" if len(parts[0]) > 2 else f"***@{parts[1]}"
        return "***" + self.upi_id[-4:] if len(self.upi_id) > 4 else "***"

    def mask_wallet_id(self):
        """Mask wallet ID for display"""
        if not self.wallet_id:
            return None
        return "***" + self.wallet_id[-4:] if len(self.wallet_id) > 4 else "***"


class PaymentTransaction(db.Model):
    __tablename__ = 'payment_transactions'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Payment details
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), default='INR')
    payment_method = db.Column(db.String(50), nullable=False)  # upi, card, netbanking, wallet, cash_on_delivery

    # Payment gateway info
    gateway_name = db.Column(db.String(100))  # razorpay, paytm, stripe, etc.
    gateway_transaction_id = db.Column(db.String(255))
    gateway_order_id = db.Column(db.String(255))

    # UPI specific
    upi_id = db.Column(db.String(255))
    upi_transaction_id = db.Column(db.String(255))
    vpa = db.Column(db.String(255))  # Virtual Payment Address

    # Card specific
    card_last_four = db.Column(db.String(4))
    card_type = db.Column(db.String(50))
    card_network = db.Column(db.String(100))

    # Net Banking specific
    bank_name = db.Column(db.String(255))
    bank_transaction_id = db.Column(db.String(255))

    # Wallet specific
    wallet_provider = db.Column(db.String(100))
    wallet_transaction_id = db.Column(db.String(255))

    # Status and timing
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed, refunded
    payment_status = db.Column(db.String(50), default='pending')  # authorized, captured, failed
    failure_reason = db.Column(db.Text)

    # Timestamps
    initiated_at = db.Column(db.DateTime, default=datetime.utcnow)
    authorized_at = db.Column(db.DateTime)
    captured_at = db.Column(db.DateTime)
    failed_at = db.Column(db.DateTime)
    refunded_at = db.Column(db.DateTime)

    # Refund info
    refund_amount = db.Column(db.Numeric(12, 2), default=0)
    refund_reason = db.Column(db.Text)

    # Security
    signature = db.Column(db.Text)  # Payment gateway signature for verification

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    order = db.relationship('Order', backref='payment_transactions')
    user = db.relationship('User', backref='payment_transactions')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'payment_method': self.payment_method,
            'status': self.status,
            'payment_status': self.payment_status,
            'gateway_name': self.gateway_name,
            'gateway_transaction_id': self.gateway_transaction_id,
            'initiated_at': self.initiated_at.isoformat() if self.initiated_at else None,
            'captured_at': self.captured_at.isoformat() if self.captured_at else None
        }

    def is_successful(self):
        return self.status == 'completed' and self.payment_status == 'captured'

    def can_refund(self):
        return self.is_successful() and self.refund_amount < self.amount