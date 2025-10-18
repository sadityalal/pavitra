# models/address.py
from extension import db
from datetime import datetime
import uuid


class UserAddress(db.Model):
    __tablename__ = 'user_addresses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address_type = db.Column(db.Enum('shipping', 'billing'), default='shipping')

    # Contact information
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    country_code = db.Column(db.String(5), default='+91')

    # Address fields
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255))
    landmark = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), default='India')
    postal_code = db.Column(db.String(20), nullable=False)

    # Address classification
    address_type_detail = db.Column(db.Enum('home', 'work', 'other'), default='home')
    is_default = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'phone': f"{self.country_code} {self.phone}",
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'landmark': self.landmark,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'postal_code': self.postal_code,
            'address_type': self.address_type,
            'is_default': self.is_default
        }

    def get_complete_address(self):
        """Get complete formatted address"""
        address_parts = [
            self.address_line1,
            self.address_line2,
            self.landmark,
            f"{self.city} - {self.postal_code}",
            self.state,
            self.country
        ]
        return ", ".join(filter(None, address_parts))