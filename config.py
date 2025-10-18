# config.py
import os
from dotenv import load_dotenv
from datetime import timedelta
load_dotenv(".env")


class Config:
    """Base configuration"""
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'pavitra-india-ecommerce-secret-key-2024-change-this-in-production')

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)  # 10 minute session timeout
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Flask-Login configuration
    REMEMBER_COOKIE_DURATION = timedelta(days=30)  # "Remember me" duration
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = False  # Set to True in production

    # Flask-WTF CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.getenv('CSRF_SECRET_KEY', 'csrf-secret-key-change-in-production')
    WTF_CSRF_ENABLED = False

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', '')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True
    }

    # File Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # E-commerce Settings (India Specific)
    CURRENCY = 'INR'
    CURRENCY_SYMBOL = '₹'
    DEFAULT_COUNTRY = 'India'
    DEFAULT_COUNTRY_CODE = '+91'
    DEFAULT_GST_RATE = 18.0
    FREE_SHIPPING_THRESHOLD = 999.00
    RETURN_PERIOD_DAYS = 10

    # Payment Methods (India)
    PAYMENT_METHODS = [
        'cash_on_delivery',
        'upi',
        'credit_card',
        'debit_card',
        'netbanking',
        'wallet'
    ]



class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    # Use environment variables in production
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}