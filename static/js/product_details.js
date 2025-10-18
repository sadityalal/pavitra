// Product Detail Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeProductDetail();
});

function initializeProductDetail() {
    // Initialize image gallery
    initializeImageGallery();

    // Initialize quantity selector
    initializeQuantitySelector();
}

function initializeImageGallery() {
    const thumbnails = document.querySelectorAll('.thumbnail-item');
    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', function() {
            // Remove active class from all thumbnails
            thumbnails.forEach(t => t.classList.remove('active'));
            // Add active class to clicked thumbnail
            this.classList.add('active');
        });
    });
}

function initializeQuantitySelector() {
    const quantityInput = document.getElementById('productQuantity');
    if (quantityInput) {
        quantityInput.addEventListener('input', validateQuantity);
    }
}

function changeMainImage(src) {
    document.getElementById('mainProductImage').src = src;
}

function increaseQuantity() {
    const quantityInput = document.getElementById('productQuantity');
    const maxQuantity = parseInt(quantityInput.getAttribute('max'));
    let currentQuantity = parseInt(quantityInput.value);

    if (currentQuantity < maxQuantity) {
        quantityInput.value = currentQuantity + 1;
    }
}

function decreaseQuantity() {
    const quantityInput = document.getElementById('productQuantity');
    let currentQuantity = parseInt(quantityInput.value);

    if (currentQuantity > 1) {
        quantityInput.value = currentQuantity - 1;
    }
}

function validateQuantity() {
    const quantityInput = document.getElementById('productQuantity');
    const maxQuantity = parseInt(quantityInput.getAttribute('max'));
    let currentQuantity = parseInt(quantityInput.value);

    if (currentQuantity < 1) {
        quantityInput.value = 1;
    } else if (currentQuantity > maxQuantity) {
        quantityInput.value = maxQuantity;
    }
}

function shareProduct(platform) {
    const productUrl = window.location.href;
    const productTitle = '{{ product.name }}';

    let shareUrl = '';
    switch(platform) {
        case 'facebook':
            shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(productUrl)}`;
            break;
        case 'twitter':
            shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(productTitle)}&url=${encodeURIComponent(productUrl)}`;
            break;
        case 'pinterest':
            shareUrl = `https://pinterest.com/pin/create/button/?url=${encodeURIComponent(productUrl)}&description=${encodeURIComponent(productTitle)}`;
            break;
        case 'whatsapp':
            shareUrl = `https://wa.me/?text=${encodeURIComponent(productTitle + ' ' + productUrl)}`;
            break;
    }

    if (shareUrl) {
        window.open(shareUrl, '_blank', 'width=600,height=400');
    }
}

function submitNotifyRequest() {
    const email = document.getElementById('notifyEmail').value;
    const productId = {{ product.id }};

    if (!email) {
        showToast('Please enter your email address', 'error');
        return;
    }

    // Simulate API call
    showToast('We will notify you when this product is available!', 'success');

    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('notifyModal'));
    modal.hide();

    // Clear form
    document.getElementById('notifyEmail').value = '';
}

// Use global addToCart and addToWishlist functions from addtocart.js
// These will handle the cart and wishlist functionality