# extension.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta, datetime

# Initialize all extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

# Login manager configuration
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'
login_manager.refresh_view = 'auth.login'
login_manager.needs_refresh_message = 'Your session has expired. Please login again.'
login_manager.needs_refresh_message_category = 'info'

# Custom user loader with session timeout check
@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    user = User.query.get(int(user_id))
    if user and user.is_active:
        # Check if session should be expired
        if user.last_activity and datetime.utcnow() - user.last_activity > timedelta(minutes=10):
            return None  # This will force re-login
        return user
    return None