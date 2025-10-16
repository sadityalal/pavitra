from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User
from extension import db

auth_bp = Blueprint('auth', __name__)


def current_user():
    """Get current user from session"""
    uid = session.get('user_id')
    if not uid:
        return None
    return User.query.get(uid)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    # POST method handling - get ALL form data for debugging
    print("=== REGISTRATION FORM DATA ===")
    for key, value in request.form.items():
        print(f"{key}: {value}")
    print("==============================")

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')

    # Validation
    if not name or not email or not password:
        flash('All fields are required', 'danger')
        return render_template('register.html')

    if password != confirm_password:
        flash('Passwords do not match', 'danger')
        return render_template('register.html')

    if len(password) < 6:
        flash('Password must be at least 6 characters', 'danger')
        return render_template('register.html')

    # Check if email exists
    if User.query.filter_by(email=email).first():
        flash('Email already registered', 'warning')
        return render_template('register.html')

    try:
        # Create user
        user = User(name=name, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        flash('Registration successful! Welcome to our store.', 'success')
        return redirect(url_for('shop.index'))

    except Exception as e:
        db.session.rollback()
        print(f"Database error: {str(e)}")
        flash('An error occurred during registration. Please try again.', 'danger')
        return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    # POST method handling
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    if not email or not password:
        flash('Please enter both email and password', 'danger')
        return render_template('login.html')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        if not user.is_active:
            flash('Your account has been deactivated', 'danger')
            return render_template('login.html')

        session['user_id'] = user.id
        if user.is_admin:
            session['is_admin'] = True
        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(url_for('shop.index'))
    else:
        flash('Invalid email or password', 'danger')
        return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    session.pop('cart', None)
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('shop.index'))