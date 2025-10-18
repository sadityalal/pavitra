# models/user.py
from extension import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
import bcrypt
from .password_history import PasswordHistory
from .address import UserAddress


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)

    # International phone format
    phone = db.Column(db.String(20))
    country_code = db.Column(db.String(5), default='+91')
    phone_verified = db.Column(db.Boolean, default=False)

    avatar_url = db.Column(db.String(500))
    email_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)

    # Additional fields
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum('male', 'female', 'other'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    addresses = db.relationship('UserAddress', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)
    wishlists = db.relationship('Wishlist', backref='user', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy=True)
    cart_items = db.relationship('ShoppingCart', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password using bcrypt"""
        if isinstance(password, str):
            password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password, salt).decode('utf-8')

    def check_password(self, password):
        """Check password against hash using bcrypt"""
        if isinstance(password, str):
            password = password.encode('utf-8')
        if isinstance(self.password_hash, str):
            stored_hash = self.password_hash.encode('utf-8')
        else:
            stored_hash = self.password_hash
        return bcrypt.checkpw(password, stored_hash)

    def get_full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"

    def get_full_phone(self):
        """Get complete phone number with country code"""
        if self.phone and self.country_code:
            return f"{self.country_code} {self.phone}"
        return None

    def get_order_count(self):
        """Get total orders count"""
        return len(self.orders)

    def get_default_address(self):
        """Get user's default shipping address"""
        return UserAddress.query.filter_by(user_id=self.id, is_default=True).first()

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.get_full_phone(),
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @property
    def name(self):
        """Template compatibility - returns full name"""
        return f"{self.first_name} {self.last_name}"

    def set_password_with_history(self, password):
        """Hash and set password using bcrypt with history tracking"""
        if isinstance(password, str):
            password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        new_hash = bcrypt.hashpw(password, salt).decode('utf-8')

        # Save current password to history before changing
        if self.password_hash:
            password_history = PasswordHistory(
                user_id=self.id,
                password_hash=self.password_hash
            )
            db.session.add(password_history)

        self.password_hash = new_hash

    def is_password_in_history(self, password, last_n=3):
        """Check if password exists in user's last N passwords"""
        return PasswordHistory.is_password_in_history(self.id, password, last_n)

    def get_password_age_days(self):
        """Get how many days since password was last changed"""
        if not self.password_hash:
            return 0

        # Find the most recent password history entry
        latest_history = PasswordHistory.query.filter_by(user_id=self.id) \
            .order_by(PasswordHistory.created_at.desc()) \
            .first()

        if latest_history:
            age_days = (datetime.utcnow() - latest_history.created_at).days
        else:
            # If no history, use user creation date
            age_days = (datetime.utcnow() - self.created_at).days

        return age_days

    def should_change_password(self, max_age_days=90):
        """Check if password should be changed based on age"""
        return self.get_password_age_days() >= max_age_days

# ✅ CLASS ENDS HERE - NO MORE METHODS AFTER THIS