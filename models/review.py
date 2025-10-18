# models/review.py
from extension import db
from datetime import datetime
import uuid


class Review(db.Model):
    __tablename__ = 'product_reviews'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_items.id'))

    rating = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255))
    comment = db.Column(db.Text)

    # Media
    review_images = db.Column(db.JSON)

    # Status
    status = db.Column(db.String(20), default='pending')
    is_verified_purchase = db.Column(db.Boolean, default=False)

    # Helpfulness
    helpful_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    order_item = db.relationship('OrderItem', backref='review')
    helpful_votes = db.relationship('ReviewHelpfulness', backref='review', lazy=True, cascade='all, delete-orphan')

    def is_approved(self):
        return self.status == 'approved'

    def mark_verified_purchase(self):
        """Mark review as verified purchase"""
        self.is_verified_purchase = True

    def increment_helpful_count(self):
        """Increment helpful count"""
        self.helpful_count += 1

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user.get_full_name(),
            'rating': self.rating,
            'title': self.title,
            'comment': self.comment,
            'is_verified_purchase': self.is_verified_purchase,
            'helpful_count': self.helpful_count,
            'created_at': self.created_at.strftime('%d %b, %Y'),
            'review_images': self.review_images or []
        }


class ReviewHelpfulness(db.Model):
    __tablename__ = 'review_helpfulness'

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('product_reviews.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_helpful = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)