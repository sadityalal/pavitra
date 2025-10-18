# models/password_history.py
from extension import db
from datetime import datetime
import bcrypt


class PasswordHistory(db.Model):
    __tablename__ = 'password_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='password_history')

    @classmethod
    def is_password_in_history(cls, user_id, password, last_n=3):
        """Check if password exists in user's last N passwords"""
        if isinstance(password, str):
            password = password.encode('utf-8')

        recent_passwords = cls.query.filter_by(user_id=user_id) \
            .order_by(cls.created_at.desc()) \
            .limit(last_n) \
            .all()

        for pwd_history in recent_passwords:
            stored_hash = pwd_history.password_hash.encode('utf-8') if isinstance(pwd_history.password_hash,
                                                                                  str) else pwd_history.password_hash
            if bcrypt.checkpw(password, stored_hash):
                return True
        return False