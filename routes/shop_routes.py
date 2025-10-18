# routes/shop_routes.py
from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for, flash
from flask_login import current_user, login_required, logout_user
from models.product import Product
from models.category import Category
from models.review import Review
from models.brand import Brand
from models.cart import ShoppingCart
from models.wishlist import Wishlist
from models.address import UserAddress
from extension import db
import uuid
from datetime import datetime
from models.order import Order, OrderItem  # Make sure these models exist

shop_bp = Blueprint('shop', __name__)

# =============================================
# HELPER FUNCTIONS
# =============================================

def get_cart_count():
    """Get total cart count (sum of all quantities)"""
    if current_user.is_authenticated:
        total_quantity = db.session.query(db.func.sum(ShoppingCart.quantity)).filter_by(user_id=current_user.id).scalar()
        return total_quantity or 0
    else:
        cart = session.get('cart', [])
        return sum(item.get('quantity', 0) for item in cart)

def get_cart_data():
    """Get complete cart data including totals with proper type handling"""
    cart_items = []
    subtotal = 0.0
    total_items = 0
    tax_amount = 0.0
    discount_amount = 0.0

    if current_user.is_authenticated:
        # Get cart items from database
        cart_items = ShoppingCart.query.filter_by(user_id=current_user.id).all()
        for item in cart_items:
            if item.product:
                # Convert Decimal to float for calculations
                item_price = float(item.product.base_price)
                item_total = item_price * item.quantity
                subtotal += item_total
                total_items += item.quantity
                # Calculate GST for this item
                gst_rate = float(item.product.gst_rate)
                tax_amount += item_total * (gst_rate / 100)
    else:
        # Get cart items from session
        if 'cart' in session:
            for item_data in session['cart']:
                product = Product.query.get(item_data['product_id'])
                if product:
                    # Convert Decimal to float for calculations
                    item_price = float(product.base_price)
                    item_total = item_price * item_data['quantity']
                    subtotal += item_total
                    total_items += item_data['quantity']
                    # Calculate GST for this item
                    gst_rate = float(product.gst_rate)
                    tax_amount += item_total * (gst_rate / 100)
                    cart_items.append({
                        'product': product,
                        'quantity': item_data['quantity'],
                        'variation_id': item_data.get('variation_id')
                    })

    return {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total_items': total_items,
        'tax_amount': tax_amount,
        'discount_amount': discount_amount
    }


def get_cart_total():
    """Get cart total amount with proper Decimal handling"""
    total = 0.0
    if current_user.is_authenticated:
        cart_items = ShoppingCart.query.filter_by(user_id=current_user.id).all()
        for item in cart_items:
            if item.product:
                total += float(item.product.base_price) * item.quantity
    else:
        if 'cart' in session:
            for item_data in session['cart']:
                product = Product.query.get(item_data['product_id'])
                if product:
                    total += float(product.base_price) * item_data['quantity']
    return total


def get_wishlist_count():
    """Get wishlist count"""
    if current_user.is_authenticated:
        return Wishlist.query.filter_by(user_id=current_user.id).count()
    return 0

# =============================================
# PRODUCT & CATALOG ROUTES
# =============================================

@shop_bp.route('/')
def index():
    """Homepage"""
    featured_products = Product.query.filter_by(
        is_featured=True,
        status='active'
    ).limit(8).all()

    new_arrivals = Product.query.filter_by(
        status='active'
    ).order_by(Product.created_at.desc()).limit(8).all()

    best_sellers = Product.query.filter_by(
        status='active'
    ).order_by(Product.total_sold.desc()).limit(8).all()

    return render_template('index.html',
                           featured_products=featured_products,
                           new_arrivals=new_arrivals,
                           best_sellers=best_sellers)

@shop_bp.route('/products')
def products():
    """All products page with filtering"""
    category_slug = request.args.get('category')
    search_query = request.args.get('q')
    featured = request.args.get('featured')
    new_arrivals = request.args.get('new_arrivals')
    on_sale = request.args.get('on_sale')
    best_sellers = request.args.get('best_sellers')

    # Base query
    query = Product.query.filter_by(status='active')

    # Filter by category
    if category_slug:
        category = Category.query.filter_by(slug=category_slug, is_active=True).first()
        if category:
            query = query.filter_by(category_id=category.id)

    # Search
    if search_query:
        query = query.filter(
            Product.name.ilike(f'%{search_query}%') |
            Product.description.ilike(f'%{search_query}%') |
            Product.short_description.ilike(f'%{search_query}%')
        )

    # Additional filters
    if featured:
        query = query.filter_by(is_featured=True)
    if new_arrivals:
        query = query.order_by(Product.created_at.desc())
    if on_sale:
        query = query.filter_by(is_on_sale=True)
    if best_sellers:
        query = query.order_by(Product.total_sold.desc())

    products = query.all()

    return render_template('shop/products.html',
                           products=products,
                           category_slug=category_slug,
                           search_query=search_query)

@shop_bp.route('/search')
def search():
    """Search page - redirects to products with search query"""
    search_query = request.args.get('q', '')
    return redirect(url_for('shop.products', q=search_query))

@shop_bp.route('/product/<slug>')
def product_detail(slug):
    """Product detail page"""
    product = Product.query.filter_by(slug=slug, status='active').first_or_404()

    # Increment view count
    product.view_count += 1
    db.session.commit()

    # Get related products
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.status == 'active'
    ).limit(4).all()

    # Get approved reviews
    reviews = Review.query.filter_by(
        product_id=product.id,
        status='approved'
    ).order_by(Review.created_at.desc()).all()

    return render_template('shop/product_detail.html',
                           product=product,
                           related_products=related_products,
                           reviews=reviews)

@shop_bp.route('/categories')
def categories():
    """Categories page"""
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('shop/categories.html', categories=categories)

@shop_bp.route('/category/<slug>')
def category(slug):
    """Category detail page"""
    category = Category.query.filter_by(slug=slug, is_active=True).first_or_404()
    products = Product.query.filter_by(
        category_id=category.id,
        status='active'
    ).all()

    return render_template('shop/category_detail.html',
                           category=category,
                           products=products)

@shop_bp.route('/brand/<slug>')
def brand(slug):
    """Brand products page"""
    brand = Brand.query.filter_by(slug=slug, is_active=True).first_or_404()
    products = Product.query.filter_by(
        brand_id=brand.id,
        status='active'
    ).all()

    return render_template('shop/brand.html',
                           brand=brand,
                           products=products)


# =============================================
# CART ROUTES
# =============================================

# =============================================
# CART ROUTES
# =============================================

@shop_bp.route('/cart')
def cart():
    """Shopping cart page"""
    try:
        cart_data = get_cart_data()
        return render_template('shop/cart.html', **cart_data)
    except Exception as e:
        flash('Error loading cart', 'danger')
        return redirect(url_for('shop.index'))

@shop_bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    """Add product to cart"""
    try:
        product_id = request.form.get('product_id') or request.json.get('product_id')
        variation_id = request.form.get('variation_id') or request.json.get('variation_id')
        quantity = int(request.form.get('quantity', 1) or request.json.get('quantity', 1))

        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID is required'})

        product = Product.query.get_or_404(product_id)

        if current_user.is_authenticated:
            # For logged-in users - save to database
            cart_item = ShoppingCart.query.filter_by(
                user_id=current_user.id,
                product_id=product_id,
                variation_id=variation_id
            ).first()

            if cart_item:
                cart_item.quantity += quantity
            else:
                cart_item = ShoppingCart(
                    user_id=current_user.id,
                    product_id=product_id,
                    variation_id=variation_id,
                    quantity=quantity
                )
                db.session.add(cart_item)

            db.session.commit()
        else:
            # For guests - save to session
            if 'cart' not in session:
                session['cart'] = []

            # Check if item already exists in cart
            cart_item_exists = False
            for item in session['cart']:
                if (str(item['product_id']) == str(product_id) and
                        str(item.get('variation_id', '')) == str(variation_id if variation_id else '')):
                    item['quantity'] += quantity
                    cart_item_exists = True
                    break

            if not cart_item_exists:
                session['cart'].append({
                    'product_id': int(product_id),
                    'variation_id': int(variation_id) if variation_id else None,
                    'quantity': quantity
                })

            session.modified = True

        # Get updated cart count
        updated_cart_count = get_cart_count()

        return jsonify({
            'success': True,
            'message': 'Product added to cart',
            'cart_count': updated_cart_count
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@shop_bp.route('/update-cart', methods=['POST'])
def update_cart():
    """Update cart item quantity"""
    try:
        item_id = request.json.get('item_id')
        quantity = int(request.json.get('quantity', 1))

        if current_user.is_authenticated:
            cart_item = ShoppingCart.query.get_or_404(item_id)
            if cart_item.user_id != current_user.id:
                return jsonify({'success': False, 'message': 'Unauthorized'})

            if quantity <= 0:
                db.session.delete(cart_item)
            else:
                cart_item.quantity = quantity
        else:
            # Update session cart
            if 'cart' in session and 0 <= item_id < len(session['cart']):
                if quantity <= 0:
                    session['cart'].pop(item_id)
                else:
                    session['cart'][item_id]['quantity'] = quantity
                session.modified = True

        db.session.commit()
        return jsonify({'success': True, 'message': 'Cart updated'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@shop_bp.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    """Remove item from cart"""
    try:
        item_id = request.json.get('item_id')

        if current_user.is_authenticated:
            cart_item = ShoppingCart.query.get_or_404(item_id)
            if cart_item.user_id != current_user.id:
                return jsonify({'success': False, 'message': 'Unauthorized'})
            db.session.delete(cart_item)
        else:
            # Remove from session cart
            if 'cart' in session and 0 <= item_id < len(session['cart']):
                session['cart'].pop(item_id)
                session.modified = True

        db.session.commit()
        return jsonify({'success': True, 'message': 'Item removed from cart'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@shop_bp.route('/cart/update', methods=['POST'])
@login_required
def update_cart_item():
    """Update cart item quantity (for form submissions)"""
    try:
        item_id = request.form.get('item_id')
        action = request.form.get('action')

        cart_item = ShoppingCart.query.get_or_404(item_id)

        # Verify the cart item belongs to current user
        if cart_item.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        if action == 'increase':
            if cart_item.quantity < cart_item.product.max_cart_quantity:
                cart_item.quantity += 1
            else:
                return jsonify({'success': False, 'message': 'Maximum quantity reached'})
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                return jsonify({'success': False, 'message': 'Minimum quantity is 1'})

        db.session.commit()

        # Get updated cart count
        cart_data = get_cart_data()
        return jsonify({
            'success': True,
            'message': 'Cart updated',
            'quantity': cart_item.quantity,
            'total_items': cart_data['total_items'],
            'cart_count': cart_data['total_items']
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@shop_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart_item(item_id):
    """Remove item from cart (for form submissions)"""
    try:
        cart_item = ShoppingCart.query.get_or_404(item_id)

        # Verify the cart item belongs to current user
        if cart_item.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        db.session.delete(cart_item)
        db.session.commit()

        # Get updated cart count
        cart_data = get_cart_data()
        return jsonify({
            'success': True,
            'message': 'Item removed from cart',
            'total_items': cart_data['total_items'],
            'cart_count': cart_data['total_items']
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@shop_bp.route('/cart/clear', methods=['POST'])
@login_required
def clear_cart():
    """Clear entire cart"""
    try:
        ShoppingCart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Cart cleared'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@shop_bp.route('/cart/apply-coupon', methods=['POST'])
@login_required
def apply_coupon():
    """Apply coupon to cart"""
    try:
        coupon_code = request.form.get('coupon_code')
        # Add coupon validation logic here
        return jsonify({'success': True, 'message': 'Coupon applied successfully'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# =============================================
# WISHLIST ROUTES
# =============================================

@shop_bp.route('/add-to-wishlist', methods=['POST'])
@login_required
def add_to_wishlist():
    """Add product to wishlist"""
    try:
        product_id = request.form.get('product_id') or request.json.get('product_id')

        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID is required'})

        # Check if already in wishlist
        existing = Wishlist.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()

        if existing:
            return jsonify({'success': False, 'message': 'Product already in wishlist'})

        wishlist_item = Wishlist(
            user_id=current_user.id,
            product_id=product_id
        )
        db.session.add(wishlist_item)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Product added to wishlist',
            'wishlist_count': get_wishlist_count()
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@shop_bp.route('/wishlist')
@login_required
def wishlist():
    """Wishlist page"""
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template('shop/wishlist.html', wishlist_items=wishlist_items)

@shop_bp.route('/remove-from-wishlist', methods=['POST'])
@login_required
def remove_from_wishlist():
    """Remove item from wishlist"""
    try:
        item_id = request.json.get('item_id')
        wishlist_item = Wishlist.query.get_or_404(item_id)

        if wishlist_item.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized'})

        db.session.delete(wishlist_item)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Item removed from wishlist'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# =============================================
# USER ACCOUNT ROUTES
# =============================================

@shop_bp.route('/account')
@login_required
def account():
    """User account dashboard"""
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()
    default_address = UserAddress.query.filter_by(user_id=current_user.id, is_default=True).first()

    return render_template('account/account.html',
                           user_orders=user_orders,
                           default_address=default_address)

@shop_bp.route('/orders')
@login_required
def orders():
    """User orders page"""
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('account/orders.html', user_orders=user_orders)

@shop_bp.route('/order/<order_number>')
@login_required
def order_detail(order_number):
    """Order detail page"""
    order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
    return render_template('account/order_detail.html', order=order)

@shop_bp.route('/addresses')
@login_required
def addresses():
    """User addresses management"""
    user_addresses = UserAddress.query.filter_by(user_id=current_user.id).all()
    return render_template('account/addresses.html', user_addresses=user_addresses)

@shop_bp.route('/add-address', methods=['POST'])
@login_required
def add_address():
    """Add new address"""
    try:
        address_data = {
            'user_id': current_user.id,
            'full_name': request.form.get('full_name'),
            'phone': request.form.get('phone'),
            'address_line1': request.form.get('address_line1'),
            'address_line2': request.form.get('address_line2'),
            'landmark': request.form.get('landmark'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'country': request.form.get('country', 'India'),
            'postal_code': request.form.get('postal_code'),
            'address_type': request.form.get('address_type', 'shipping'),
            'address_type_detail': request.form.get('address_type_detail', 'home'),
            'is_default': bool(request.form.get('is_default'))
        }

        # If setting as default, remove default from other addresses
        if address_data['is_default']:
            UserAddress.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})

        new_address = UserAddress(**address_data)
        db.session.add(new_address)
        db.session.commit()

        flash('Address added successfully', 'success')
        return redirect(url_for('shop.addresses'))

    except Exception as e:
        flash('Error adding address', 'danger')
        return redirect(url_for('shop.addresses'))

@shop_bp.route('/edit-address/<int:address_id>', methods=['GET', 'POST'])
@login_required
def edit_address(address_id):
    """Edit existing address"""
    address = UserAddress.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        try:
            address.full_name = request.form.get('full_name')
            address.phone = request.form.get('phone')
            address.address_line1 = request.form.get('address_line1')
            address.address_line2 = request.form.get('address_line2')
            address.landmark = request.form.get('landmark')
            address.city = request.form.get('city')
            address.state = request.form.get('state')
            address.country = request.form.get('country', 'India')
            address.postal_code = request.form.get('postal_code')
            address.address_type = request.form.get('address_type', 'shipping')
            address.address_type_detail = request.form.get('address_type_detail', 'home')

            is_default = bool(request.form.get('is_default'))
            if is_default and not address.is_default:
                # Remove default from other addresses
                UserAddress.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})
                address.is_default = True
            elif not is_default and address.is_default:
                address.is_default = False

            db.session.commit()
            flash('Address updated successfully', 'success')
            return redirect(url_for('shop.addresses'))

        except Exception as e:
            flash('Error updating address', 'danger')
            return redirect(url_for('shop.addresses'))

    return render_template('account/edit_address.html', address=address)

@shop_bp.route('/delete-address/<int:address_id>', methods=['POST'])
@login_required
def delete_address(address_id):
    """Delete address"""
    try:
        address = UserAddress.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
        db.session.delete(address)
        db.session.commit()
        flash('Address deleted successfully', 'success')
    except Exception as e:
        flash('Error deleting address', 'danger')

    return redirect(url_for('shop.addresses'))


# =============================================
# STATIC PAGES ROUTES
# =============================================

@shop_bp.route('/about')
def about():
    """About us page"""
    return render_template('shop/about.html')

@shop_bp.route('/contact')
def contact():
    """Contact us page"""
    return render_template('shop/contact.html')

@shop_bp.route('/shipping-info')
def shipping_info():
    """Shipping information page"""
    return render_template('static_pages/shipping_info.html')

@shop_bp.route('/return-policy')
def return_policy():
    """Return policy page"""
    return render_template('static_pages/return_policy.html')

@shop_bp.route('/faq')
def faq():
    """FAQ page"""
    return render_template('static_pages/faq.html')

@shop_bp.route('/terms')
def tos():
    """Terms of service page"""
    return render_template('static_pages/tos.html')

@shop_bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('static_pages/privacy.html')


# =============================================
# API ENDPOINTS FOR AJAX
# =============================================

@shop_bp.route('/api/cart-count')
def api_cart_count():
    """Get cart count for AJAX requests"""
    count = get_cart_count()
    return jsonify({'count': count})

@shop_bp.route('/api/wishlist-count')
def api_wishlist_count():
    """Get wishlist count for AJAX requests"""
    return jsonify({'count': get_wishlist_count()})

@shop_bp.route('/api/product/<int:product_id>/stock')
def api_product_stock(product_id):
    """Get product stock information"""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({
            'success': True,
            'stock_quantity': product.stock_quantity,
            'stock_status': product.stock_status,
            'is_in_stock': product.is_in_stock(),
            'available_quantity': product.get_available_quantity()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# =============================================
# AUTHENTICATION ROUTES
# =============================================

@shop_bp.route('/auth/logout', methods=['POST'])
@login_required
def api_logout():
    """API endpoint for logout"""
    logout_user()
    session.clear()
    return jsonify({'success': True})


# =============================================
# DEBUG ROUTES
# =============================================

@shop_bp.route('/debug-csrf')
def debug_csrf():
    """Debug CSRF token"""
    from flask_wtf.csrf import generate_csrf
    return jsonify({
        'csrf_token_in_meta': 'Check browser console',
        'csrf_token_from_wtf': generate_csrf(),
        'session_csrf_token': session.get('csrf_token')
    })

@shop_bp.route('/debug-template')
def debug_template():
    """Debug template CSRF token"""
    from flask_wtf.csrf import generate_csrf
    csrf_from_wtf = generate_csrf()

    return f"""
    <html>
    <head>
        <title>CSRF Debug</title>
        <meta name="csrf-token" content="{{{{ csrf_token() }}}}">
    </head>
    <body>
        <h1>CSRF Debug Info</h1>
        <p>CSRF from WTF: {csrf_from_wtf}</p>
        <p>CSRF in template: {{ csrf_token() }}</p>
        <p>Session CSRF: {session.get('csrf_token')}</p>
    </body>
    </html>
    """


# =============================================
# CHECKOUT ROUTES
# =============================================

@shop_bp.route('/checkout')
@login_required
def checkout():
    """Checkout page"""
    cart_data = get_cart_data()

    # Check if cart is empty
    if not cart_data['cart_items']:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('shop.cart'))

    # Get user addresses for checkout
    user_addresses = UserAddress.query.filter_by(user_id=current_user.id).all()
    default_address = UserAddress.query.filter_by(user_id=current_user.id, is_default=True).first()

    return render_template('checkout/checkout.html',
                           **cart_data,
                           user_addresses=user_addresses,
                           default_address=default_address)


@shop_bp.route('/checkout/process', methods=['POST'])
@login_required
def process_checkout():
    """Process checkout and create order"""
    try:
        cart_data = get_cart_data()

        # Check if cart is empty
        if not cart_data['cart_items']:
            return jsonify({'success': False, 'message': 'Cart is empty'})

        # Get form data
        shipping_address_id = request.form.get('shipping_address_id')
        billing_address_id = request.form.get('billing_address_id')
        payment_method = request.form.get('payment_method', 'cash_on_delivery')
        customer_note = request.form.get('customer_note', '')

        # Get or create addresses
        shipping_address = UserAddress.query.filter_by(id=shipping_address_id, user_id=current_user.id).first()
        if not shipping_address:
            return jsonify({'success': False, 'message': 'Invalid shipping address'})

        billing_address = UserAddress.query.filter_by(id=billing_address_id, user_id=current_user.id).first()
        if not billing_address:
            billing_address = shipping_address  # Use shipping address as billing address

        # Calculate totals
        shipping_cost = 0 if cart_data['subtotal'] >= 999 else 50
        final_total = cart_data['subtotal'] + cart_data['tax_amount'] + shipping_cost

        # Generate order number
        order_number = f"ORD-{int(datetime.utcnow().timestamp())}"

        # Create order
        order = Order(
            uuid=str(uuid.uuid4()),
            order_number=order_number,
            user_id=current_user.id,
            subtotal=cart_data['subtotal'],
            shipping_amount=shipping_cost,
            tax_amount=cart_data['tax_amount'],
            discount_amount=cart_data['discount_amount'],
            total_amount=final_total,
            status='pending',
            payment_status='pending',
            payment_method=payment_method,
            shipping_address={
                'full_name': shipping_address.full_name,
                'phone': shipping_address.phone,
                'address_line1': shipping_address.address_line1,
                'address_line2': shipping_address.address_line2,
                'landmark': shipping_address.landmark,
                'city': shipping_address.city,
                'state': shipping_address.state,
                'country': shipping_address.country,
                'postal_code': shipping_address.postal_code
            },
            billing_address={
                'full_name': billing_address.full_name,
                'phone': billing_address.phone,
                'address_line1': billing_address.address_line1,
                'address_line2': billing_address.address_line2,
                'landmark': billing_address.landmark,
                'city': billing_address.city,
                'state': billing_address.state,
                'country': billing_address.country,
                'postal_code': billing_address.postal_code
            },
            customer_note=customer_note
        )

        db.session.add(order)
        db.session.flush()  # Get order ID without committing

        # Create order items
        for cart_item in cart_data['cart_items']:
            if hasattr(cart_item, 'product'):
                product = cart_item.product
                quantity = cart_item.quantity
            else:
                product = cart_item['product']
                quantity = cart_item['quantity']

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                product_sku=product.sku,
                product_image=product.main_image_url,
                unit_price=float(product.base_price),
                quantity=quantity,
                total_price=float(product.base_price) * quantity,
                gst_rate=float(product.gst_rate),
                gst_amount=float(product.base_price) * quantity * (float(product.gst_rate) / 100)
            )
            db.session.add(order_item)

        # Clear cart after successful order
        if current_user.is_authenticated:
            ShoppingCart.query.filter_by(user_id=current_user.id).delete()
        else:
            session.pop('cart', None)

        db.session.commit()

        # Redirect to order confirmation
        return jsonify({
            'success': True,
            'order_number': order_number,
            'redirect_url': url_for('shop.order_confirmation', order_number=order_number)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@shop_bp.route('/order-confirmation/<order_number>')
@login_required
def order_confirmation(order_number):
    """Order confirmation page"""
    order = Order.query.filter_by(order_number=order_number, user_id=current_user.id).first_or_404()
    return render_template('checkout/order_confirmation.html', order=order)


# =============================================
# ERROR HANDLERS
# =============================================

@shop_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors for shop routes"""
    return render_template('errors/404.html'), 404

@shop_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors for shop routes"""
    db.session.rollback()
    return render_template('errors/500.html'), 500