# routes/shop_routes.py
from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for, flash
from flask_login import current_user, login_required, logout_user
from models.product import Product
from models.category import Category
from models.review import Review
from models.brand import Brand
from models.cart import ShoppingCart
from models.wishlist import Wishlist
from models.order import Order
from models.user import User
from models.address import UserAddress
from extension import db

shop_bp = Blueprint('shop', __name__)


@shop_bp.route('/')
def index():
    """Homepage"""
    # Featured products
    featured_products = Product.query.filter_by(
        is_featured=True,
        status='active'
    ).limit(8).all()

    # New arrivals
    new_arrivals = Product.query.filter_by(
        status='active'
    ).order_by(Product.created_at.desc()).limit(8).all()

    # Best sellers (based on total_sold field)
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


# Cart Routes
@shop_bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    """Add product to cart"""
    try:
        product_id = request.form.get('product_id') or request.json.get('product_id')
        variation_id = request.form.get('variation_id') or request.json.get('variation_id')
        quantity = int(request.form.get('quantity', 1) or request.json.get('quantity', 1))

        print(f"DEBUG: Adding to cart - product_id: {product_id}, variation_id: {variation_id}, quantity: {quantity}")
        print(f"DEBUG: User authenticated: {current_user.is_authenticated}")

        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID is required'})

        product = Product.query.get_or_404(product_id)

        if current_user.is_authenticated:
            # For logged-in users - save to database
            print(f"DEBUG: Checking existing cart items for user {current_user.id}")
            cart_item = ShoppingCart.query.filter_by(
                user_id=current_user.id,
                product_id=product_id,
                variation_id=variation_id
            ).first()

            if cart_item:
                print(
                    f"DEBUG: Found existing cart item, increasing quantity from {cart_item.quantity} to {cart_item.quantity + quantity}")
                cart_item.quantity += quantity
            else:
                print(f"DEBUG: No existing cart item, creating new one")
                cart_item = ShoppingCart(
                    user_id=current_user.id,
                    product_id=product_id,
                    variation_id=variation_id,
                    quantity=quantity
                )
                db.session.add(cart_item)

            db.session.commit()
            print(f"DEBUG: Cart updated in database")
        else:
            # For guests - save to session
            print(f"DEBUG: Guest user - using session cart")
            if 'cart' not in session:
                session['cart'] = []
                print(f"DEBUG: Created new session cart")

            # Check if item already exists in cart
            cart_item_exists = False
            print(f"DEBUG: Current session cart: {session['cart']}")

            for index, item in enumerate(session['cart']):
                print(f"DEBUG: Checking item {index}: {item}")
                if (str(item['product_id']) == str(product_id) and
                        str(item.get('variation_id', '')) == str(variation_id if variation_id else '')):
                    print(
                        f"DEBUG: Found existing item at index {index}, increasing quantity from {item['quantity']} to {item['quantity'] + quantity}")
                    item['quantity'] += quantity
                    cart_item_exists = True
                    break

            if not cart_item_exists:
                print(f"DEBUG: No existing item found, adding new item")
                session['cart'].append({
                    'product_id': int(product_id),
                    'variation_id': int(variation_id) if variation_id else None,
                    'quantity': quantity
                })

            session.modified = True
            print(f"DEBUG: Updated session cart: {session['cart']}")

        # Get updated cart count
        updated_cart_count = get_cart_count()
        print(f"DEBUG: Updated cart count: {updated_cart_count}")

        return jsonify({
            'success': True,
            'message': 'Product added to cart',
            'cart_count': updated_cart_count
        })

    except Exception as e:
        print(f"DEBUG: Error in add-to-cart: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})


@shop_bp.route('/cart')
def cart():
    """Shopping cart page"""
    cart_items = []
    total_amount = 0

    if current_user.is_authenticated:
        # Get cart items from database
        cart_items = ShoppingCart.query.filter_by(user_id=current_user.id).all()
        for item in cart_items:
            if item.product:
                item_total = float(item.product.base_price) * item.quantity
                total_amount += item_total
    else:
        # Get cart items from session
        if 'cart' in session:
            for item_data in session['cart']:
                product = Product.query.get(item_data['product_id'])
                if product:
                    item_total = float(product.base_price) * item_data['quantity']
                    total_amount += item_total
                    cart_items.append({
                        'product': product,
                        'quantity': item_data['quantity'],
                        'variation_id': item_data.get('variation_id')
                    })

    return render_template('shop/cart.html',
                           cart_items=cart_items,
                           total_amount=total_amount)


@shop_bp.route('/update-cart', methods=['POST'])
def update_cart():
    """Update cart item quantity"""
    # Flask-WTF automatically handles CSRF validation

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
    # Flask-WTF automatically handles CSRF validation

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


# Wishlist Routes
@shop_bp.route('/add-to-wishlist', methods=['POST'])
@login_required
def add_to_wishlist():
    """Add product to wishlist"""
    # Flask-WTF automatically handles CSRF validation

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
    # Flask-WTF automatically handles CSRF validation

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


# User Routes - UPDATED PATHS
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
    # Flask-WTF automatically handles CSRF validation

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
    # Flask-WTF automatically handles CSRF validation

    try:
        address = UserAddress.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
        db.session.delete(address)
        db.session.commit()
        flash('Address deleted successfully', 'success')
    except Exception as e:
        flash('Error deleting address', 'danger')

    return redirect(url_for('shop.addresses'))


# Static pages - UPDATED PATHS
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


# API endpoints for AJAX
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


# Helper functions
def get_cart_count():
    """Get total cart count (sum of all quantities)"""
    if current_user.is_authenticated:
        # Sum all quantities for logged-in users
        total_quantity = db.session.query(db.func.sum(ShoppingCart.quantity)).filter_by(user_id=current_user.id).scalar()
        count = total_quantity or 0
        print(f"DEBUG: Database cart total quantity for user {current_user.id}: {count}")
        return count
    else:
        # Sum all quantities for guest users
        cart = session.get('cart', [])
        total_quantity = sum(item.get('quantity', 0) for item in cart)
        print(f"DEBUG: Session cart total quantity: {total_quantity}")
        return total_quantity


def get_wishlist_count():
    """Get wishlist count"""
    if current_user.is_authenticated:
        return Wishlist.query.filter_by(user_id=current_user.id).count()
    return 0


def get_cart_total():
    """Get cart total amount"""
    total = 0
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

# logout
@shop_bp.route('/auth/logout', methods=['POST'])
@login_required
def api_logout():
    """API endpoint for logout"""
    logout_user()
    session.clear()
    return jsonify({'success': True})

# Error handlers for shop routes
@shop_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors for shop routes"""
    return render_template('errors/404.html'), 404


@shop_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors for shop routes"""
    db.session.rollback()
    return render_template('errors/500.html'), 500


# Debugging helper for CSRF
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

    # Render a simple template to see what's happening
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

        <script>
            const metaTag = document.querySelector('meta[name="csrf-token"]');
            console.log('Meta tag CSRF:', metaTag ? metaTag.getAttribute('content') : 'Not found');
        </script>
    </body>
    </html>
    """