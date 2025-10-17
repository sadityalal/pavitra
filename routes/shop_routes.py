from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from models.user import User
from models.product import Product
from models.category import Category
from models.review import Review
from models.order import Order, OrderItem
from models.wishlist import Wishlist
from models.coupon import Coupon
from extension import db
from sqlalchemy import or_, and_

shop_bp = Blueprint('shop', __name__)


def current_user():
    """Get current user from session"""
    uid = session.get('user_id')
    if not uid:
        return None
    return User.query.get(uid)


def get_cart_total():
    """Calculate cart total"""
    cart = session.get('cart', [])
    return sum(item['price'] * item['quantity'] for item in cart)


@shop_bp.route('/')
def index():
    try:
        # Get featured products
        featured_products = Product.query.filter_by(
            is_featured=True,
            is_active=True
        ).limit(8).all()

        # Get new arrivals (latest products)
        new_arrivals = Product.query.filter_by(
            is_active=True
        ).order_by(Product.created_at.desc()).limit(8).all()

        # Get best sellers (most ordered products)
        best_sellers = Product.query.filter_by(
            is_active=True
        ).limit(8).all()

        # Get categories for navigation
        categories = Category.query.filter_by(is_active=True).all()

        return render_template('index.html',
                               featured_products=featured_products,
                               new_arrivals=new_arrivals,
                               best_sellers=best_sellers,
                               categories=categories,
                               user=current_user())
    except Exception as e:
        print(f"Error loading products: {e}")
        return render_template('index.html',
                               featured_products=[],
                               new_arrivals=[],
                               best_sellers=[],
                               categories=[],
                               user=current_user())


@shop_bp.route('/about')
def about():
    try:
        # Get some stats for the about page
        total_products = Product.query.filter_by(is_active=True).count()
        total_orders = Order.query.count()

        stats = {
            'happy_customers': 500,
            'total_products': total_products,
            'orders_delivered': total_orders,
            'positive_reviews': 98
        }

        return render_template('about.html',
                               stats=stats,
                               user=current_user())
    except Exception as e:
        print(f"Error loading about page: {e}")
        return render_template('about.html',
                               stats={},
                               user=current_user())


@shop_bp.route('/contact')
def contact():
    return render_template('contact.html', user=current_user())


@shop_bp.route('/category')
@shop_bp.route('/category/<slug>')
def category(slug=None):
    try:
        if slug:
            # Specific category page
            category_obj = Category.query.filter_by(slug=slug, is_active=True).first()
            if not category_obj:
                flash('Category not found', 'warning')
                return redirect(url_for('shop.category'))

            products = Product.query.filter_by(
                category_id=category_obj.id,
                is_active=True
            ).all()

            return render_template('category.html',
                                   category=category_obj,
                                   products=products,
                                   user=current_user())
        else:
            # All categories page
            products = Product.query.filter_by(is_active=True).all()
            return render_template('category.html',
                                   products=products,
                                   user=current_user())

    except Exception as e:
        print(f"Error loading category: {e}")
        return redirect(url_for('shop.index'))


@shop_bp.route('/product/<slug>')
def product_details(slug):
    try:
        product = Product.query.filter_by(slug=slug, is_active=True).first()
        if not product:
            flash('Product not found', 'warning')
            return redirect(url_for('shop.index'))

        # Get related products (same category)
        related_products = Product.query.filter(
            Product.category_id == product.category_id,
            Product.id != product.id,
            Product.is_active == True
        ).limit(4).all()

        # Get approved reviews
        reviews = Review.query.filter_by(
            product_id=product.id,
            is_approved=True
        ).order_by(Review.created_at.desc()).all()

        return render_template('product-details.html',
                               product=product,
                               related_products=related_products,
                               reviews=reviews,
                               user=current_user())
    except Exception as e:
        print(f"Error loading product: {e}")
        flash('Error loading product', 'danger')
        return redirect(url_for('shop.index'))


@shop_bp.route('/search')
def search():
    try:
        query = request.args.get('q', '').strip()
        category_id = request.args.get('category', type=int)

        if not query:
            return redirect(url_for('shop.index'))

        # Build search query
        search_filter = and_(
            Product.is_active == True,
            or_(
                Product.name.ilike(f'%{query}%'),
                Product.description.ilike(f'%{query}%'),
                Product.short_description.ilike(f'%{query}%')
            )
        )

        if category_id:
            search_filter = and_(search_filter, Product.category_id == category_id)

        products = Product.query.filter(search_filter).all()

        return render_template('search-results.html',
                               products=products,
                               search_query=query,
                               selected_category=category_id,
                               user=current_user())

    except Exception as e:
        print(f"Search error: {e}")
        return redirect(url_for('shop.index'))


@shop_bp.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    try:
        product = Product.query.get(product_id)
        if not product or not product.is_active:
            flash('Product not available', 'warning')
            return redirect(request.referrer or url_for('shop.index'))

        if not product.is_in_stock():
            flash('Product is out of stock', 'warning')
            return redirect(request.referrer or url_for('shop.index'))

        quantity = request.form.get('quantity', 1, type=int)

        # Validate quantity
        if quantity < 1:
            quantity = 1
        if quantity > product.inventory_quantity:
            flash(f'Only {product.inventory_quantity} items available', 'warning')
            quantity = product.inventory_quantity

        cart = session.get('cart', [])

        # Check if product already in cart
        cart_item = None
        for item in cart:
            if item['id'] == product_id:
                cart_item = item
                break

        if cart_item:
            # Update quantity
            new_quantity = cart_item['quantity'] + quantity
            if new_quantity > product.inventory_quantity:
                flash(f'Only {product.inventory_quantity} items available in total', 'warning')
                new_quantity = product.inventory_quantity
            cart_item['quantity'] = new_quantity
        else:
            # Add new item
            cart.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'quantity': quantity,
                'image_url': product.image_url,
                'slug': product.slug,
                'max_quantity': product.inventory_quantity
            })

        session['cart'] = cart
        session.modified = True

        flash(f'Added {product.name} to cart', 'success')
        return redirect(request.referrer or url_for('shop.index'))

    except Exception as e:
        print(f"Add to cart error: {e}")
        flash('Error adding item to cart', 'danger')
        return redirect(request.referrer or url_for('shop.index'))


@shop_bp.route('/cart')
def cart():
    try:
        cart_items = session.get('cart', [])
        subtotal = sum(item['price'] * item['quantity'] for item in cart_items)

        # Calculate totals
        shipping = 0 if subtotal >= 50 else 5.99  # Free shipping over $50
        tax = subtotal * 0.08  # 8% tax
        total = subtotal + shipping + tax

        return render_template('cart.html',
                               cart=cart_items,
                               subtotal=subtotal,
                               shipping=shipping,
                               tax=tax,
                               total=total,
                               user=current_user())
    except Exception as e:
        print(f"Cart error: {e}")
        return render_template('cart.html',
                               cart=[],
                               subtotal=0,
                               shipping=0,
                               tax=0,
                               total=0,
                               user=current_user())


@shop_bp.route('/update-cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    try:
        quantity = request.form.get('quantity', type=int)
        cart = session.get('cart', [])

        for item in cart:
            if item['id'] == product_id:
                if quantity and quantity > 0:
                    if quantity <= item.get('max_quantity', 999):
                        item['quantity'] = quantity
                        flash('Cart updated', 'success')
                    else:
                        flash(f'Maximum {item.get("max_quantity")} items available', 'warning')
                        item['quantity'] = item.get('max_quantity', 1)
                else:
                    cart.remove(item)
                    flash('Item removed from cart', 'success')
                break

        session['cart'] = cart
        session.modified = True
        return redirect(url_for('shop.cart'))

    except Exception as e:
        print(f"Update cart error: {e}")
        flash('Error updating cart', 'danger')
        return redirect(url_for('shop.cart'))


@shop_bp.route('/remove-from-cart/<int:product_id>')
def remove_from_cart(product_id):
    try:
        cart = session.get('cart', [])
        cart = [item for item in cart if item['id'] != product_id]
        session['cart'] = cart
        session.modified = True
        flash('Item removed from cart', 'success')
        return redirect(url_for('shop.cart'))
    except Exception as e:
        print(f"Remove from cart error: {e}")
        flash('Error removing item', 'danger')
        return redirect(url_for('shop.cart'))


@shop_bp.route('/wishlist/add/<int:product_id>')
def add_to_wishlist(product_id):
    try:
        user = current_user()
        if not user:
            flash('Please login to add items to wishlist', 'warning')
            return redirect(url_for('auth.login'))

        product = Product.query.get(product_id)
        if not product:
            flash('Product not found', 'warning')
            return redirect(request.referrer or url_for('shop.index'))

        # Check if already in wishlist
        existing = Wishlist.query.filter_by(
            user_id=user.id,
            product_id=product_id
        ).first()

        if existing:
            flash('Product already in wishlist', 'info')
        else:
            wishlist_item = Wishlist(user_id=user.id, product_id=product_id)
            db.session.add(wishlist_item)
            db.session.commit()
            flash('Added to wishlist', 'success')

        return redirect(request.referrer or url_for('shop.index'))

    except Exception as e:
        print(f"Wishlist error: {e}")
        flash('Error adding to wishlist', 'danger')
        return redirect(request.referrer or url_for('shop.index'))


@shop_bp.route('/wishlist')
def wishlist():
    try:
        user = current_user()
        if not user:
            flash('Please login to view your wishlist', 'warning')
            return redirect(url_for('auth.login'))

        wishlist_items = Wishlist.query.filter_by(user_id=user.id).all()
        wishlist_products = [item.product for item in wishlist_items]

        return render_template('wishlist.html',
                               wishlist_products=wishlist_products,
                               user=user)

    except Exception as e:
        print(f"Wishlist error: {e}")
        return redirect(url_for('shop.index'))


@shop_bp.route('/wishlist/remove/<int:product_id>')
def remove_from_wishlist(product_id):
    try:
        user = current_user()
        if not user:
            return redirect(url_for('auth.login'))

        wishlist_item = Wishlist.query.filter_by(
            user_id=user.id,
            product_id=product_id
        ).first()

        if wishlist_item:
            db.session.delete(wishlist_item)
            db.session.commit()
            flash('Removed from wishlist', 'success')

        return redirect(url_for('shop.wishlist'))

    except Exception as e:
        print(f"Remove wishlist error: {e}")
        flash('Error removing from wishlist', 'danger')
        return redirect(url_for('shop.wishlist'))


@shop_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    try:
        user = current_user()
        cart_items = session.get('cart', [])

        if not cart_items:
            flash('Your cart is empty', 'warning')
            return redirect(url_for('shop.cart'))

        if request.method == 'POST':
            if not user:
                flash('Please login to checkout', 'warning')
                return redirect(url_for('auth.login'))

            # Calculate totals
            subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
            shipping = 0 if subtotal >= 50 else 5.99
            tax = subtotal * 0.08
            total = subtotal + shipping + tax

            # Get form data
            shipping_address = {
                'name': request.form.get('shipping_name'),
                'address': request.form.get('shipping_address'),
                'city': request.form.get('shipping_city'),
                'state': request.form.get('shipping_state'),
                'zip_code': request.form.get('shipping_zip'),
                'country': request.form.get('shipping_country'),
                'phone': request.form.get('shipping_phone')
            }

            # Create order
            order = Order(
                user_id=user.id,
                subtotal=subtotal,
                shipping_amount=shipping,
                tax_amount=tax,
                total=total,
                payment_method=request.form.get('payment_method'),
                shipping_address=shipping_address,
                billing_address=shipping_address,  # Same as shipping for now
                customer_note=request.form.get('customer_note')
            )

            db.session.add(order)
            db.session.commit()

            # Add order items
            for item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item['id'],
                    product_name=item['name'],
                    product_price=item['price'],
                    quantity=item['quantity'],
                    image_url=item['image_url']
                )
                db.session.add(order_item)

            db.session.commit()

            # Clear cart
            session.pop('cart', None)
            session.modified = True

            flash('Order placed successfully!', 'success')
            return redirect(url_for('shop.order_confirmation', order_id=order.id))

        # GET request - show checkout form
        subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
        shipping = 0 if subtotal >= 50 else 5.99
        tax = subtotal * 0.08
        total = subtotal + shipping + tax

        return render_template('checkout.html',
                               cart=cart_items,
                               subtotal=subtotal,
                               shipping=shipping,
                               tax=tax,
                               total=total,
                               user=user)

    except Exception as e:
        print(f"Checkout error: {e}")
        flash('Error during checkout', 'danger')
        return redirect(url_for('shop.cart'))


@shop_bp.route('/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    try:
        user = current_user()
        if not user:
            flash('Please login to view order', 'warning')
            return redirect(url_for('auth.login'))

        order = Order.query.filter_by(id=order_id, user_id=user.id).first()
        if not order:
            flash('Order not found', 'warning')
            return redirect(url_for('shop.profile'))

        return render_template('order-confirmation.html',
                               order=order,
                               user=user)

    except Exception as e:
        print(f"Order confirmation error: {e}")
        return redirect(url_for('shop.profile'))


@shop_bp.route('/profile')
def profile():
    user = current_user()
    if not user:
        flash('Please login to view your profile', 'warning')
        return redirect(url_for('auth.login'))

    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return render_template('profile.html', user=user, orders=orders)


@shop_bp.route('/account')
def account():
    user = current_user()
    if not user:
        flash('Please login to access your account', 'warning')
        return redirect(url_for('auth.login'))

    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).limit(5).all()
    wishlist_count = Wishlist.query.filter_by(user_id=user.id).count()

    return render_template('account.html',
                           user=user,
                           orders=orders,
                           wishlist_count=wishlist_count)


@shop_bp.route('/update-profile', methods=['POST'])
def update_profile():
    try:
        user = current_user()
        if not user:
            return redirect(url_for('auth.login'))

        user.name = request.form.get('name', user.name)
        user.phone = request.form.get('phone', user.phone)
        user.address = request.form.get('address', user.address)
        user.city = request.form.get('city', user.city)
        user.state = request.form.get('state', user.state)
        user.zip_code = request.form.get('zip_code', user.zip_code)
        user.country = request.form.get('country', user.country)

        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('shop.account'))

    except Exception as e:
        print(f"Update profile error: {e}")
        flash('Error updating profile', 'danger')
        return redirect(url_for('shop.account'))


# Static pages
@shop_bp.route('/support')
def support():
    return render_template('support.html', user=current_user())


@shop_bp.route('/shipping-info')
def shipping_info():
    return render_template('shipping-info.html', user=current_user())


@shop_bp.route('/return-policy')
def return_policy():
    return render_template('return-policy.html', user=current_user())


@shop_bp.route('/tos')
def tos():
    return render_template('tos.html', user=current_user())


@shop_bp.route('/privacy')
def privacy():
    return render_template('privacy.html', user=current_user())


@shop_bp.route('/faq')
def faq():
    return render_template('faq.html', user=current_user())


@shop_bp.route('/payment-methods')
def payment_methods():
    return render_template('payment-methods.html', user=current_user())


# API endpoints for AJAX
@shop_bp.route('/api/cart-count')
def api_cart_count():
    cart = session.get('cart', [])
    count = sum(item['quantity'] for item in cart)
    return jsonify({'count': count})


@shop_bp.route('/api/wishlist-count')
def api_wishlist_count():
    user = current_user()
    if not user:
        return jsonify({'count': 0})

    count = Wishlist.query.filter_by(user_id=user.id).count()
    return jsonify({'count': count})


# Error handler
@shop_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html', user=current_user()), 404



# Add these context processors to your shop/routes.py

@shop_bp.context_processor
def inject_categories():
    """Inject categories into all templates"""
    try:
        categories = Category.query.filter_by(is_active=True).all()
        return dict(categories=categories)
    except Exception as e:
        print(f"Error loading categories: {e}")
        return dict(categories=[])

@shop_bp.context_processor
def inject_featured_products():
    """Inject featured products into all templates"""
    try:
        featured_products = Product.query.filter_by(
            is_featured=True,
            is_active=True
        ).limit(4).all()
        return dict(featured_products=featured_products)
    except Exception as e:
        print(f"Error loading featured products: {e}")
        return dict(featured_products=[])

@shop_bp.context_processor
def inject_new_arrivals():
    """Inject new arrivals into all templates"""
    try:
        new_arrivals = Product.query.filter_by(
            is_active=True
        ).order_by(Product.created_at.desc()).limit(4).all()
        return dict(new_arrivals=new_arrivals)
    except Exception as e:
        print(f"Error loading new arrivals: {e}")
        return dict(new_arrivals=[])