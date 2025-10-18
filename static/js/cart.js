// static/js/cart.js
class CartManager {
    constructor() {
        this.init();
    }

    init() {
        this.initializeEventListeners();
        console.log('Cart Manager initialized');
    }

    initializeEventListeners() {
        // Quantity update buttons
        document.querySelectorAll('.quantity-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleQuantityChange(e));
        });

        // Remove item buttons
        document.querySelectorAll('.remove-item-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.removeItem(e));
        });

        // Coupon form
        const couponForm = document.getElementById('couponForm');
        if (couponForm) {
            couponForm.addEventListener('submit', (e) => this.applyCoupon(e));
        }

        // Clear cart
        const clearCartBtn = document.getElementById('clearCartBtn');
        if (clearCartBtn) {
            clearCartBtn.addEventListener('click', (e) => this.clearCart(e));
        }
    }

    updateCartCount(count) {
        // Update all cart count elements in the header
        const cartCountElements = document.querySelectorAll('#cart-count');
        cartCountElements.forEach(element => {
            element.textContent = count;
        });

        // Also update any other elements with cart-count class
        const cartCountClassElements = document.querySelectorAll('.cart-count');
        cartCountClassElements.forEach(element => {
            element.textContent = count;
        });
    }

    async handleQuantityChange(e) {
        e.preventDefault();

        const button = e.target.closest('button');
        const action = button.getAttribute('data-action');
        const form = button.closest('form');
        const itemId = form.querySelector('input[name="item_id"]').value;
        const csrfToken = form.querySelector('input[name="csrf_token"]').value;

        // Get current quantity display
        const quantityDisplay = form.querySelector('.quantity-display');
        let currentQuantity = parseInt(quantityDisplay.textContent);

        // Update quantity locally for instant feedback
        if (action === 'increase') {
            currentQuantity += 1;
        } else if (action === 'decrease' && currentQuantity > 1) {
            currentQuantity -= 1;
        }

        // Update display immediately
        quantityDisplay.textContent = currentQuantity;

        try {
            const formData = new FormData();
            formData.append('item_id', itemId);
            formData.append('action', action);
            formData.append('csrf_token', csrfToken);

            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                // Update cart count in header
                this.updateCartCount(data.total_items || data.cart_count);
                this.showAlert('Quantity updated', 'success');
            } else {
                // Revert quantity if update failed
                const originalQuantity = currentQuantity - (action === 'increase' ? 1 : -1);
                quantityDisplay.textContent = originalQuantity;
                this.showAlert(data.message, 'danger');
            }
        } catch (error) {
            console.error('Error updating quantity:', error);
            // Revert quantity on error
            const originalQuantity = currentQuantity - (action === 'increase' ? 1 : -1);
            quantityDisplay.textContent = originalQuantity;
            this.showAlert('Error updating quantity', 'danger');
        }
    }

    async removeItem(e) {
        e.preventDefault();

        if (!confirm('Are you sure you want to remove this item from cart?')) {
            return;
        }

        const form = e.target.closest('form');
        const cartItem = form.closest('.cart-item');

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    // Remove item from DOM with animation
                    cartItem.style.opacity = '0';
                    cartItem.style.transition = 'opacity 0.3s ease';
                    setTimeout(() => {
                        cartItem.remove();
                        this.updateCartDisplay();
                    }, 300);

                    // Update cart count
                    this.updateCartCount(data.total_items || data.cart_count);
                    this.showAlert('Item removed from cart', 'success');
                } else {
                    this.showAlert(data.message, 'danger');
                }
            } else {
                throw new Error('Failed to remove item');
            }
        } catch (error) {
            console.error('Error removing item:', error);
            this.showAlert('Error removing item', 'danger');
        }
    }


    async applyCoupon(e) {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    location.reload();
                } else {
                    this.showAlert(data.message, 'warning');
                }
            } else {
                throw new Error('Failed to apply coupon');
            }
        } catch (error) {
            console.error('Error applying coupon:', error);
            this.showAlert('Error applying coupon', 'danger');
        }
    }

    async clearCart(e) {
        e.preventDefault();

        if (!confirm('Are you sure you want to clear your entire cart?')) {
            return;
        }

        const form = e.target.closest('form');

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    location.reload();
                } else {
                    this.showAlert(data.message, 'danger');
                }
            } else {
                throw new Error('Failed to clear cart');
            }
        } catch (error) {
            console.error('Error clearing cart:', error);
            this.showAlert('Error clearing cart', 'danger');
        }
    }

    getCSRFToken() {
        // Try multiple ways to get CSRF token
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) return metaTag.getAttribute('content');

        const csrfInput = document.querySelector('input[name="csrf_token"]');
        if (csrfInput) return csrfInput.value;

        return '';
    }

    showAlert(message, type) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert-dismissible');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}-fill me-2"></i>
                <div>${message}</div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alert);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new CartManager();
});