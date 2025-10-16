from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.product import Product
from models.category import Category
from models.order import Order
from models.user import User
from extension import db
import json

# ... rest of your admin_routes.py code ...

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
def protect():
    if not session.get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('shop.index'))


@admin_bp.route('/')
def dashboard():
    try:
        # Get stats
        total_products = Product.query.count()
        total_orders = Order.query.count()
        total_users = User.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()

        # Recent orders
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()

        # Low stock products
        low_stock_products = Product.query.filter(
            Product.inventory_quantity <= Product.low_stock_threshold
        ).limit(5).all()

        return render_template('admin/admin_dashboard.html',
                               total_products=total_products,
                               total_orders=total_orders,
                               total_users=total_users,
                               pending_orders=pending_orders,
                               recent_orders=recent_orders,
                               low_stock_products=low_stock_products)
    except Exception as e:
        print(f"Admin dashboard error: {e}")
        return render_template('admin/admin_dashboard.html')


@admin_bp.route('/products')
def products():
    try:
        products = Product.query.all()
        categories = Category.query.all()
        return render_template('admin/products.html',  # Changed from admin_new.html
                               products=products,
                               categories=categories)
    except Exception as e:
        print(f"Products admin error: {e}")
        return redirect(url_for('admin.dashboard'))

# Similarly update other routes to use appropriate templates


@admin_bp.route('/products/new', methods=['GET', 'POST'])
def new_product():
    try:
        categories = Category.query.all()

        if request.method == 'POST':
            # Get form data
            name = request.form.get('name')
            description = request.form.get('description')
            short_description = request.form.get('short_description')
            price = request.form.get('price', 0, type=float)
            compare_price = request.form.get('compare_price', 0, type=float)
            cost_price = request.form.get('cost_price', 0, type=float)
            sku = request.form.get('sku')
            inventory_quantity = request.form.get('inventory_quantity', 0, type=int)
            category_id = request.form.get('category_id', type=int)
            is_featured = bool(request.form.get('is_featured'))
            is_active = bool(request.form.get('is_active'))
            image_url = request.form.get('image_url')

            # Generate slug from name
            slug = name.lower().replace(' ', '-')

            # Check if slug exists
            existing = Product.query.filter_by(slug=slug).first()
            if existing:
                slug = f"{slug}-{Product.query.count() + 1}"

            product = Product(
                name=name,
                description=description,
                short_description=short_description,
                price=price,
                compare_price=compare_price if compare_price else None,
                cost_price=cost_price if cost_price else None,
                sku=sku,
                inventory_quantity=inventory_quantity,
                category_id=category_id,
                is_featured=is_featured,
                is_active=is_active,
                image_url=image_url,
                slug=slug
            )

            db.session.add(product)
            db.session.commit()

            flash('Product created successfully', 'success')
            return redirect(url_for('admin.products'))

        return render_template('admin/admin_new.html',
                               categories=categories,
                               product=None)

    except Exception as e:
        print(f"New product error: {e}")
        flash('Error creating product', 'danger')
        return redirect(url_for('admin.products'))


@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        categories = Category.query.all()

        if request.method == 'POST':
            product.name = request.form.get('name')
            product.description = request.form.get('description')
            product.short_description = request.form.get('short_description')
            product.price = request.form.get('price', 0, type=float)
            product.compare_price = request.form.get('compare_price', 0, type=float)
            product.cost_price = request.form.get('cost_price', 0, type=float)
            product.sku = request.form.get('sku')
            product.inventory_quantity = request.form.get('inventory_quantity', 0, type=int)
            product.category_id = request.form.get('category_id', type=int)
            product.is_featured = bool(request.form.get('is_featured'))
            product.is_active = bool(request.form.get('is_active'))
            product.image_url = request.form.get('image_url')

            db.session.commit()
            flash('Product updated successfully', 'success')
            return redirect(url_for('admin.products'))

        return render_template('admin/admin_new.html',
                               product=product,
                               categories=categories)

    except Exception as e:
        print(f"Edit product error: {e}")
        flash('Error updating product', 'danger')
        return redirect(url_for('admin.products'))


@admin_bp.route('/products/delete/<int:product_id>')
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully', 'success')
    except Exception as e:
        print(f"Delete product error: {e}")
        flash('Error deleting product', 'danger')

    return redirect(url_for('admin.products'))


@admin_bp.route('/categories')
def categories():
    try:
        categories = Category.query.all()
        return render_template('admin/admin_.html', categories=categories)
    except Exception as e:
        print(f"Categories admin error: {e}")
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/categories/new', methods=['GET', 'POST'])
def new_category():
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            slug = request.form.get('slug')
            image_url = request.form.get('image_url')
            is_active = bool(request.form.get('is_active'))

            category = Category(
                name=name,
                description=description,
                slug=slug,
                image_url=image_url,
                is_active=is_active
            )

            db.session.add(category)
            db.session.commit()

            flash('Category created successfully', 'success')
            return redirect(url_for('admin.categories'))

        return render_template('admin/admin_new.html', category=None)

    except Exception as e:
        print(f"New category error: {e}")
        flash('Error creating category', 'danger')
        return redirect(url_for('admin.categories'))


@admin_bp.route('/orders')
def orders():
    try:
        orders = Order.query.order_by(Order.created_at.desc()).all()
        return render_template('admin/admin_new.html', orders=orders)
    except Exception as e:
        print(f"Orders admin error: {e}")
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/orders/<int:order_id>')
def order_details(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        return render_template('admin/admin_new.html', order=order)
    except Exception as e:
        print(f"Order details error: {e}")
        flash('Error loading order details', 'danger')
        return redirect(url_for('admin.orders'))


@admin_bp.route('/orders/update-status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        new_status = request.form.get('status')
        tracking_number = request.form.get('tracking_number')

        if new_status:
            order.status = new_status

        if tracking_number:
            order.tracking_number = tracking_number

        db.session.commit()
        flash('Order status updated successfully', 'success')

    except Exception as e:
        print(f"Update order status error: {e}")
        flash('Error updating order status', 'danger')

    return redirect(url_for('admin.order_details', order_id=order_id))