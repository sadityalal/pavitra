// static/js/account.js
// Account page specific functionality

document.addEventListener('DOMContentLoaded', function() {
    console.log('Account page loaded');

    // Initialize tab functionality
    initializeTabs();

    // Initialize mobile menu
    initializeMobileMenu();

    // Initialize order search
    initializeOrderSearch();

    // Initialize wishlist functionality
    initializeWishlist();

    // Initialize forms
    initializeForms();
});

function initializeTabs() {
    const triggerTabList = [].slice.call(document.querySelectorAll('#profileMenu a[data-bs-toggle="tab"]'));
    triggerTabList.forEach(function (triggerEl) {
        const tabTrigger = new bootstrap.Tab(triggerEl);
        triggerEl.addEventListener('click', function (event) {
            event.preventDefault();
            tabTrigger.show();
        });
    });
}

function initializeMobileMenu() {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            const target = document.querySelector(this.getAttribute('data-bs-target'));
            if (target) {
                target.classList.toggle('show');
            }
        });
    }
}

function initializeOrderSearch() {
    const orderSearch = document.getElementById('orderSearch');
    const ordersGrid = document.getElementById('ordersGrid');

    if (orderSearch && ordersGrid) {
        orderSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const orderCards = ordersGrid.querySelectorAll('.order-card');

            orderCards.forEach(card => {
                const orderId = card.querySelector('.order-id .value').textContent.toLowerCase();
                const orderDate = card.querySelector('.order-date').textContent.toLowerCase();
                const orderStatus = card.querySelector('.status').textContent.toLowerCase();

                const matches = orderId.includes(searchTerm) ||
                               orderDate.includes(searchTerm) ||
                               orderStatus.includes(searchTerm);

                card.style.display = matches ? 'block' : 'none';
            });
        });
    }
}

function initializeWishlist() {
    // Remove from wishlist
    const removeButtons = document.querySelectorAll('.remove-wishlist');
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-item-id');
            removeFromWishlist(itemId, this);
        });
    });

    // Add to cart from wishlist
    const addToCartButtons = document.querySelectorAll('.add-to-cart-wishlist');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            addToCartFromWishlist(productId, this);
        });
    });

    // Add all to cart
    const addAllButton = document.getElementById('addAllToCart');
    if (addAllButton) {
        addAllButton.addEventListener('click', addAllToCart);
    }
}

function removeFromWishlist(itemId, buttonElement) {
    if (!confirm('Are you sure you want to remove this item from your wishlist?')) {
        return;
    }

    const originalHTML = buttonElement.innerHTML;
    buttonElement.innerHTML = '<i class="bi bi-arrow-repeat spinner"></i>';
    buttonElement.disabled = true;

    fetch('/remove-from-wishlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin',
        body: JSON.stringify({
            item_id: itemId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the wishlist card from DOM
            const wishlistCard = buttonElement.closest('.wishlist-card');
            wishlistCard.style.opacity = '0';
            setTimeout(() => {
                wishlistCard.remove();
                updateWishlistCount();
                showToast('Item removed from wishlist', 'success');

                // Show empty state if no items left
                const wishlistGrid = document.getElementById('wishlistGrid');
                if (wishlistGrid && wishlistGrid.children.length === 0) {
                    showEmptyWishlistState();
                }
            }, 300);
        } else {
            buttonElement.innerHTML = originalHTML;
            buttonElement.disabled = false;
            showToast(data.message || 'Error removing from wishlist', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        buttonElement.innerHTML = originalHTML;
        buttonElement.disabled = false;
        showToast('Network error. Please try again.', 'error');
    });
}

function addToCartFromWishlist(productId, buttonElement) {
    const originalHTML = buttonElement.innerHTML;
    buttonElement.innerHTML = '<i class="bi bi-arrow-repeat spinner"></i> Adding...';
    buttonElement.disabled = true;

    addToCart(productId, buttonElement, () => {
        // Success callback - button will be reset by addToCart function
    });
}

function addAllToCart() {
    const addButtons = document.querySelectorAll('.add-to-cart-wishlist:not([disabled])');
    let successCount = 0;
    let errorCount = 0;

    addButtons.forEach((button, index) => {
        setTimeout(() => {
            const productId = button.getAttribute('data-product-id');
            addToCart(productId, button, (success) => {
                if (success) {
                    successCount++;
                } else {
                    errorCount++;
                }

                // Check if all operations are complete
                if (successCount + errorCount === addButtons.length) {
                    let message = `Added ${successCount} items to cart`;
                    if (errorCount > 0) {
                        message += `, ${errorCount} items failed`;
                    }
                    showToast(message, successCount > 0 ? 'success' : 'warning');
                }
            });
        }, index * 500); // Stagger requests to avoid overwhelming the server
    });

    if (addButtons.length === 0) {
        showToast('No available items to add to cart', 'info');
    }
}

function showEmptyWishlistState() {
    const wishlistGrid = document.getElementById('wishlistGrid');
    if (wishlistGrid) {
        wishlistGrid.innerHTML = `
            <div class="empty-state" data-aos="fade-up">
                <div class="empty-icon">
                    <i class="bi bi-heart"></i>
                </div>
                <h3>Your Wishlist is Empty</h3>
                <p>Save items you love to your wishlist. Review them anytime and easily move them to the bag.</p>
                <a href="/products" class="btn btn-primary">Start Shopping</a>
            </div>
        `;
    }
}

function initializeForms() {
    // Profile form
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileUpdate);
    }

    // Password form
    const passwordForm = document.getElementById('passwordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', handlePasswordChange);
    }
}

function handleProfileUpdate(e) {
    e.preventDefault();

    const form = e.target;
    const submitButton = form.querySelector('.btn-save');
    const originalText = submitButton.innerHTML;

    submitButton.innerHTML = '<i class="bi bi-arrow-repeat spinner"></i> Saving...';
    submitButton.disabled = true;

    const formData = new FormData(form);

    fetch('/api/update-profile', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Profile updated successfully', 'success');
        } else {
            showToast(data.message || 'Error updating profile', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Network error. Please try again.', 'error');
    })
    .finally(() => {
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    });
}

function handlePasswordChange(e) {
    e.preventDefault();

    const form = e.target;
    const submitButton = form.querySelector('.btn-save');
    const originalText = submitButton.innerHTML;

    const newPassword = form.querySelector('#newPassword').value;
    const confirmPassword = form.querySelector('#confirmPassword').value;

    if (newPassword !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }

    if (newPassword.length < 6) {
        showToast('Password must be at least 6 characters long', 'error');
        return;
    }

    submitButton.innerHTML = '<i class="bi bi-arrow-repeat spinner"></i> Updating...';
    submitButton.disabled = true;

    const formData = new FormData(form);

    fetch('/api/change-password', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Password updated successfully', 'success');
            form.reset();
        } else {
            showToast(data.message || 'Error updating password', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Network error. Please try again.', 'error');
    })
    .finally(() => {
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    });
}

// Helper function to update wishlist count in the menu
function updateWishlistCount() {
    const wishlistBadge = document.querySelector('a[href="#wishlist"] .badge');
    if (wishlistBadge) {
        const currentCount = parseInt(wishlistBadge.textContent) || 0;
        wishlistBadge.textContent = Math.max(0, currentCount - 1);
    }
}