import os
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-pavitra')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://myapp_user:password123@localhost:3305/pavitra')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
