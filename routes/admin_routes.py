# routes/admin_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc, func, or_
from datetime import datetime, timedelta
import json

# FIXED IMPORTS:
from models.product import Product, ProductVariation
from models.category import Category
from models.brand import Brand
from models.order import Order, OrderItem
from models.user import User
from models.stock import StockMovement, StockAlert
from models.review import Review
from models.coupon import Coupon
from extension import db

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
    """Admin dashboard with comprehensive stats"""
    try:
        # Get basic stats
        total_products = Product.query.count()
        total_orders = Order.query.count()
        total_users = User.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()

        # Revenue stats (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_revenue_orders = Order.query.filter(
            Order.created_at >= thirty_days_ago,
            Order.payment_status == 'paid'
        ).all()
        total_revenue = sum(order.total_amount for order in recent_revenue_orders)

        # Today's stats
        today = datetime.utcnow().date()
        today_orders = Order.query.filter(
            func.date(Order.created_at) == today
        ).count()

        today_revenue_orders = Order.query.filter(
            func.date(Order.created_at) == today,
            Order.payment_status == 'paid'
        ).all()
        today_revenue = sum(order.total_amount for order in today_revenue_orders)

        # Low stock alerts
        low_stock_products = Product.query.filter(
            Product.stock_quantity <= Product.low_stock_threshold,
            Product.track_inventory == True,
            Product.status == 'active'
        ).limit(10).all()

        # Recent orders for dashboard
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()

        # Pending reviews
        pending_reviews = Review.query.filter_by(status='pending').count()

        return render_template('admin/admin_dashboard.html',
                               total_products=total_products,
                               total_orders=total_orders,
                               total_users=total_users,
                               pending_orders=pending_orders,
                               recent_orders=recent_orders,
                               low_stock_products=low_stock_products,
                               total_revenue=total_revenue,
                               today_orders=today_orders,
                               today_revenue=today_revenue,
                               pending_reviews=pending_reviews)

    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return render_template('admin/admin_dashboard.html')


@admin_bp.route('/products')
def products():
    """Product management with stock information"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20

        # Get filter parameters
        category_id = request.args.get('category_id', type=int)
        stock_filter = request.args.get('stock_filter')
        status_filter = request.args.get('status_filter', 'all')
        search_query = request.args.get('q', '')

        # Build query
        query = Product.query

        if search_query:
            query = query.filter(
                or_(
                    Product.name.ilike(f'%{search_query}%'),
                    Product.sku.ilike(f'%{search_query}%'),
                    Product.description.ilike(f'%{search_query}%')
                )
            )

        if category_id:
            query = query.filter(Product.category_id == category_id)

        if status_filter != 'all':
            query = query.filter(Product.status == status_filter)

        if stock_filter == 'low':
            query = query.filter(
                Product.stock_quantity <= Product.low_stock_threshold,
                Product.track_inventory == True
            )
        elif stock_filter == 'out':
            query = query.filter(
                Product.stock_quantity == 0,
                Product.track_inventory == True
            )
        elif stock_filter == 'in_stock':
            query = query.filter(Product.stock_quantity > 0)

        # Get products with pagination
        products_pagination = query.order_by(Product.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        categories = Category.query.all()

        return render_template('admin/products.html',
                               products=products_pagination.items,
                               pagination=products_pagination,
                               categories=categories,
                               category_id=category_id,
                               stock_filter=stock_filter,
                               status_filter=status_filter,
                               search_query=search_query)

    except Exception as e:
        flash(f'Error loading products: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/products/new', methods=['GET', 'POST'])
def new_product():
    """Add new product"""
    try:
        if request.method == 'POST':
            # Extract form data
            name = request.form.get('name')
            description = request.form.get('description')
            base_price = float(request.form.get('base_price', 0))
            compare_price = float(request.form.get('compare_price', 0)) if request.form.get('compare_price') else None
            cost_price = float(request.form.get('cost_price', 0)) if request.form.get('cost_price') else None
            sku = request.form.get('sku')
            category_id = request.form.get('category_id')
            brand_id = request.form.get('brand_id') if request.form.get('brand_id') else None
            stock_quantity = int(request.form.get('stock_quantity', 0))
            low_stock_threshold = int(request.form.get('low_stock_threshold', 5))
            weight_grams = float(request.form.get('weight_grams', 0)) if request.form.get('weight_grams') else None
            gst_rate = float(request.form.get('gst_rate', 18.0))
            hsn_code = request.form.get('hsn_code')

            # Generate slug from name
            slug = request.form.get('slug') or name.lower().replace(' ', '-')

            # Status flags
            is_featured = 'is_featured' in request.form
            is_active = 'is_active' in request.form
            track_inventory = 'track_inventory' in request.form
            is_returnable = 'is_returnable' in request.form

            # Create product
            product = Product(
                name=name,
                description=description,
                base_price=base_price,
                compare_price=compare_price,
                cost_price=cost_price,
                sku=sku,
                slug=slug,
                category_id=category_id,
                brand_id=brand_id,
                stock_quantity=stock_quantity,
                low_stock_threshold=low_stock_threshold,
                weight_grams=weight_grams,
                gst_rate=gst_rate,
                hsn_code=hsn_code,
                is_featured=is_featured,
                status='active' if is_active else 'draft',
                track_inventory=track_inventory,
                is_returnable=is_returnable
            )

            db.session.add(product)
            db.session.commit()

            flash('Product created successfully!', 'success')
            return redirect(url_for('admin.products'))

        # GET request - show form
        categories = Category.query.filter_by(is_active=True).all()
        brands = Brand.query.filter_by(is_active=True).all()

        return render_template('admin/product_form.html',
                               categories=categories,
                               brands=brands,
                               product=None)

    except Exception as e:
        db.session.rollback()
        flash(f'Error creating product: {str(e)}', 'danger')
        return redirect(url_for('admin.products'))


@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    """Edit existing product"""
    try:
        product = Product.query.get_or_404(product_id)

        if request.method == 'POST':
            # Update product data
            product.name = request.form.get('name')
            product.description = request.form.get('description')
            product.base_price = float(request.form.get('base_price', 0))
            product.compare_price = float(request.form.get('compare_price', 0)) if request.form.get(
                'compare_price') else None
            product.cost_price = float(request.form.get('cost_price', 0)) if request.form.get('cost_price') else None
            product.sku = request.form.get('sku')
            product.slug = request.form.get('slug')
            product.category_id = request.form.get('category_id')
            product.brand_id = request.form.get('brand_id') if request.form.get('brand_id') else None
            product.stock_quantity = int(request.form.get('stock_quantity', 0))
            product.low_stock_threshold = int(request.form.get('low_stock_threshold', 5))
            product.weight_grams = float(request.form.get('weight_grams', 0)) if request.form.get(
                'weight_grams') else None
            product.gst_rate = float(request.form.get('gst_rate', 18.0))
            product.hsn_code = request.form.get('hsn_code')
            product.is_featured = 'is_featured' in request.form
            product.status = 'active' if 'is_active' in request.form else 'draft'
            product.track_inventory = 'track_inventory' in request.form
            product.is_returnable = 'is_returnable' in request.form

            product.update_stock_status()  # Update stock status based on new quantity

            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('admin.products'))

        categories = Category.query.filter_by(is_active=True).all()
        brands = Brand.query.filter_by(is_active=True).all()

        return render_template('admin/product_form.html',
                               product=product,
                               categories=categories,
                               brands=brands)

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating product: {str(e)}', 'danger')
        return redirect(url_for('admin.products'))


@admin_bp.route('/products/<int:product_id>/stock', methods=['POST'])
def update_stock(product_id):
    """Update product stock quantity"""
    try:
        product = Product.query.get_or_404(product_id)
        new_quantity = int(request.form.get('stock_quantity', 0))
        reason = request.form.get('reason', 'manual_adjustment')

        # Calculate difference
        quantity_change = new_quantity - product.stock_quantity

        # Create stock movement record
        if quantity_change != 0:
            stock_movement = StockMovement(
                product_id=product_id,
                movement_type='adjustment',
                quantity=quantity_change,
                stock_before=product.stock_quantity,
                stock_after=new_quantity,
                reason=reason,
                performed_by=current_user.id
            )
            db.session.add(stock_movement)

        # Update product stock
        product.stock_quantity = new_quantity
        product.update_stock_status()
        db.session.commit()

        flash(f'Stock updated successfully! New quantity: {new_quantity}', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating stock: {str(e)}', 'danger')

    return redirect(url_for('admin.products'))


@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
def delete_product(product_id):
    """Delete product"""
    try:
        product = Product.query.get_or_404(product_id)

        # Check if product has orders
        if product.order_items:
            flash('Cannot delete product with existing orders', 'danger')
            return redirect(url_for('admin.products'))

        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'danger')

    return redirect(url_for('admin.products'))


@admin_bp.route('/orders')
def orders():
    """Order management with filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        status_filter = request.args.get('status', 'all')
        payment_filter = request.args.get('payment_status', 'all')
        date_filter = request.args.get('date_filter', 'all')
        search_query = request.args.get('q', '')

        # Build query
        query = Order.query

        if search_query:
            query = query.filter(
                or_(
                    Order.order_number.ilike(f'%{search_query}%'),
                    Order.customer_email.ilike(f'%{search_query}%') if hasattr(Order, 'customer_email') else False,
                    Order.id.ilike(f'%{search_query}%')
                )
            )

        if status_filter != 'all':
            query = query.filter(Order.status == status_filter)

        if payment_filter != 'all':
            query = query.filter(Order.payment_status == payment_filter)

        if date_filter == 'today':
            today = datetime.utcnow().date()
            query = query.filter(func.date(Order.created_at) == today)
        elif date_filter == 'week':
            week_ago = datetime.utcnow() - timedelta(days=7)
            query = query.filter(Order.created_at >= week_ago)
        elif date_filter == 'month':
            month_ago = datetime.utcnow() - timedelta(days=30)
            query = query.filter(Order.created_at >= month_ago)

        # Get orders with pagination
        orders_pagination = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return render_template('admin/orders.html',
                               orders=orders_pagination.items,
                               pagination=orders_pagination,
                               status_filter=status_filter,
                               payment_filter=payment_filter,
                               date_filter=date_filter,
                               search_query=search_query)

    except Exception as e:
        flash(f'Error loading orders: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/orders/<int:order_id>')
def order_detail(order_id):
    """Order detail view"""
    try:
        order = Order.query.get_or_404(order_id)
        return render_template('admin/order_detail.html', order=order)

    except Exception as e:
        flash(f'Error loading order: {str(e)}', 'danger')
        return redirect(url_for('admin.orders'))


@admin_bp.route('/orders/<int:order_id>/update-status', methods=['POST'])
def update_order_status(order_id):
    """Update order status"""
    try:
        order = Order.query.get_or_404(order_id)
        new_status = request.form.get('status')

        valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
        if new_status in valid_statuses:
            order.status = new_status

            # Update timestamps based on status
            if new_status == 'shipped':
                order.shipped_at = datetime.utcnow()
            elif new_status == 'delivered':
                order.delivered_at = datetime.utcnow()
            elif new_status == 'cancelled':
                order.cancelled_at = datetime.utcnow()

            db.session.commit()
            flash(f'Order status updated to {new_status}', 'success')
        else:
            flash('Invalid status', 'danger')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating order status: {str(e)}', 'danger')

    return redirect(url_for('admin.order_detail', order_id=order_id))


@admin_bp.route('/stock')
def stock_management():
    """Stock management dashboard"""
    try:
        # Low stock products
        low_stock_products = Product.query.filter(
            Product.stock_quantity <= Product.low_stock_threshold,
            Product.track_inventory == True,
            Product.status == 'active'
        ).all()

        # Out of stock products
        out_of_stock_products = Product.query.filter(
            Product.stock_quantity == 0,
            Product.track_inventory == True,
            Product.status == 'active'
        ).all()

        # Recent stock movements
        recent_movements = StockMovement.query.order_by(
            StockMovement.performed_at.desc()
        ).limit(50).all()

        return render_template('admin/stock_management.html',
                               low_stock_products=low_stock_products,
                               out_of_stock_products=out_of_stock_products,
                               recent_movements=recent_movements)

    except Exception as e:
        flash(f'Error loading stock management: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/categories')
def categories():
    """Category management"""
    try:
        categories = Category.query.order_by(Category.sort_order, Category.name).all()
        return render_template('admin/categories.html', categories=categories)

    except Exception as e:
        flash(f'Error loading categories: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/reviews')
def reviews():
    """Review management"""
    try:
        status_filter = request.args.get('status', 'pending')
        page = request.args.get('page', 1, type=int)
        per_page = 20

        query = Review.query

        if status_filter != 'all':
            query = query.filter(Review.status == status_filter)

        reviews_pagination = query.order_by(Review.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return render_template('admin/reviews.html',
                               reviews=reviews_pagination.items,
                               pagination=reviews_pagination,
                               status_filter=status_filter)

    except Exception as e:
        flash(f'Error loading reviews: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/api/admin/stats')
def api_admin_stats():
    """API endpoint for admin dashboard stats"""
    try:
        # Pending orders count
        pending_orders = Order.query.filter_by(status='pending').count()

        # Today's orders count
        today = datetime.utcnow().date()
        today_orders = Order.query.filter(
            func.date(Order.created_at) == today
        ).count()

        # Today's revenue
        today_revenue_orders = Order.query.filter(
            func.date(Order.created_at) == today,
            Order.payment_status == 'paid'
        ).all()
        today_revenue = sum(order.total_amount for order in today_revenue_orders)

        return jsonify({
            'pending_orders': pending_orders,
            'today_orders': today_orders,
            'today_revenue': today_revenue
        })

    except Exception as e:
        return jsonify({
            'pending_orders': 0,
            'today_orders': 0,
            'today_revenue': 0,
            'error': str(e)
        }), 500