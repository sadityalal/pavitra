# routes/admin_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.product import Product
from models.category import Category  # ✅ FIXED: Import from correct module
from models.order import Order
from models.user import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
@login_required
def require_admin():
    """Require admin access for all admin routes"""
    if not current_user.is_admin:
        flash('Admin access required', 'danger')
        return redirect(url_for('shop.index'))


@admin_bp.route('/')
def dashboard():
    """Admin dashboard"""
    # Get stats
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_users = User.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()

    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()

    # Low stock products
    low_stock_products = Product.query.filter(
        Product.stock_quantity <= Product.low_stock_threshold,
        Product.track_inventory == True
    ).limit(5).all()

    return render_template('admin/admin_dashboard.html',
                           total_products=total_products,
                           total_orders=total_orders,
                           total_users=total_users,
                           pending_orders=pending_orders,
                           recent_orders=recent_orders,
                           low_stock_products=low_stock_products)


@admin_bp.route('/products')
def products():
    """Product management"""
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('admin/products.html',
                           products=products,
                           categories=categories)


@admin_bp.route('/orders')
def orders():
    """Order management"""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)