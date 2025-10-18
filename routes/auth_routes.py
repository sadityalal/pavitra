# routes/auth_routes.py
from datetime import timedelta, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from extension import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('shop.index'))

    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        errors = []
        if not all([first_name, last_name, email, password]):
            errors.append('All fields are required')
        if password != confirm_password:
            errors.append('Passwords do not match')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters')

        # Check if email exists
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')

        try:
            # Create user
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                country_code='+91'  # Default for India
            )
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            # Log the user in
            login_user(user)
            flash('Registration successful! Welcome to Pavitra Enterprises.', 'success')
            return redirect(url_for('shop.index'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('auth/register.html')

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('shop.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = bool(request.form.get('remember_me'))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated', 'danger')
                return render_template('auth/login.html')

            # Login user with session configuration
            login_user(user, remember=remember_me, duration=timedelta(minutes=10))

            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()

            flash(f'Welcome back, {user.first_name}!', 'success')

            # Redirect to next page if exists
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('shop.index'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/api/update-activity', methods=['POST'])
@login_required
def update_activity():
    """Update the user's last activity time in session"""
    session['last_activity'] = datetime.datetime.utcnow().isoformat()
    return jsonify({'success': True})

@auth_bp.route('/api/check-session', methods=['GET'])
@login_required
def check_session():
    """Check if user session is still valid"""
    return jsonify({'session_valid': True})


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('cart', None)  # Clear session cart
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('shop.index'))