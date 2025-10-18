# models/__init__.py
from .user import User
from .address import UserAddress
from .product import Product, ProductAttribute, ProductAttributeValue, ProductVariation, VariationAttribute
from .category import Category
from .brand import Brand
from .order import Order, OrderItem
from .wishlist import Wishlist
from .cart import ShoppingCart
from .review import Review, ReviewHelpfulness
from .coupon import Coupon, CouponUsage
from .stock import StockMovement, StockAlert

# Make all models available for import
__all__ = [
    'User', 'UserAddress',
    'Product', 'ProductAttribute', 'ProductAttributeValue',
    'ProductVariation', 'VariationAttribute',
    'Category', 'Brand',
    'Order', 'OrderItem',
    'Wishlist', 'ShoppingCart',
    'Review', 'ReviewHelpfulness',
    'Coupon', 'CouponUsage',
    'StockMovement', 'StockAlert'
]