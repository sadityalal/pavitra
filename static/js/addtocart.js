// static/js/addtocart.js
// Cart and Wishlist functionality for Pavitra Enterprises

console.log('addtocart.js loaded');

// Global add to cart function
function addToCart(productId, buttonElement) {
    console.log('Adding product to cart:', productId);

    if (!buttonElement) {
        console.error('No button element provided');
        showToast('Error: Could not add to cart', 'error');
        return;
    }

    const originalText = buttonElement.innerHTML;

    // Show loading state
    buttonElement.innerHTML = '<i class="bi bi-arrow-repeat spinner"></i> Adding...';
    buttonElement.disabled = true;

    const csrfToken = getCSRFToken();
    console.log('Using CSRF Token:', csrfToken);

    fetch("/add-to-cart", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        credentials: 'same-origin',
        body: JSON.stringify({
            product_id: productId,
            quantity: 1
        })
    })
    .then(response => {
        console.log('Response status:', response.status);
        if (!response.ok) {
            if (response.status === 400) {
                return response.text().then(text => {
                    console.log('CSRF Error details:', text);
                    throw new Error('CSRF validation failed');
                });
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Success response:', data);
        if (data.success) {
            buttonElement.innerHTML = '<i class="bi bi-check"></i> Added!';
            setTimeout(() => {
                buttonElement.innerHTML = originalText;
                buttonElement.disabled = false;
            }, 2000);
            showToast('Product added to cart!');

            // Update cart count with the response data
            updateCartCountWithData(data.cart_count);
        } else {
            buttonElement.innerHTML = originalText;
            buttonElement.disabled = false;
            showToast(data.message || 'Error adding to cart', 'error');
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        buttonElement.innerHTML = originalText;
        buttonElement.disabled = false;
        if (error.message.includes('CSRF')) {
            showToast('Security error. Please refresh the page and try again.', 'error');
        } else {
            showToast('Network error. Please try again.', 'error');
        }
    });
}

// Update cart count with specific data (from add-to-cart response)
function updateCartCountWithData(count) {
    console.log('Updating cart count to:', count);
    const cartCountElements = document.querySelectorAll('#cart-count, .cart-count, .notification-dot' );
    cartCountElements.forEach(element => {
        element.textContent = count || 0;
        console.log('Updated element:', element, 'to count:', count);
    });
}

// Global update cart count function (fetches from API)
function updateCartCount() {
    fetch("/api/cart-count")
        .then(response => response.json())
        .then(data => {
            console.log('Cart count API response:', data);
            updateCartCountWithData(data.count);
        })
        .catch(error => console.error('Error updating cart count:', error));
}

// Global add to wishlist function
function addToWishlist(productId, buttonElement) {
    console.log('Adding product to wishlist:', productId);

    if (!buttonElement) {
        console.error('No button element provided');
        showToast('Error: Could not add to wishlist', 'error');
        return;
    }

    const originalHTML = buttonElement.innerHTML;

    buttonElement.innerHTML = '<i class="bi bi-arrow-repeat spinner"></i>';
    buttonElement.disabled = true;

    const csrfToken = getCSRFToken();

    fetch("/add-to-wishlist", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        credentials: 'same-origin',
        body: JSON.stringify({
            product_id: productId
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Wishlist response:', data);
        if (data.success) {
            buttonElement.innerHTML = '<i class="bi bi-heart-fill text-danger"></i>';
            showToast('Product added to wishlist!');
            updateWishlistCountWithData(data.wishlist_count);
        } else {
            buttonElement.innerHTML = originalHTML;
            buttonElement.disabled = false;
            showToast(data.message || 'Error adding to wishlist', 'error');
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        buttonElement.innerHTML = originalHTML;
        buttonElement.disabled = false;
        showToast('Network error. Please try again.', 'error');
    });
}

// Update wishlist count with specific data
function updateWishlistCountWithData(count) {
    console.log('Updating wishlist count to:', count);
    const wishlistCountElements = document.querySelectorAll('#wishlist-count, .wishlist-count');
    wishlistCountElements.forEach(element => {
        element.textContent = count || 0;
    });
}

// Global update wishlist count function
function updateWishlistCount() {
    fetch("/api/wishlist-count")
        .then(response => response.json())
        .then(data => {
            updateWishlistCountWithData(data.count);
        })
        .catch(error => console.error('Error updating wishlist count:', error));
}

// Initialize cart counts when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing cart and wishlist counts...');
    updateCartCount();
    updateWishlistCount();
});