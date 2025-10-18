// static/js/utils.js
// Utility functions for Pavitra Enterprises

// Get CSRF token from meta tag
function getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        const token = metaTag.getAttribute('content');
        console.log('CSRF Token found:', token);
        return token;
    }
    console.warn('CSRF token not found');
    return '';
}

// Global toast notification function
function showToast(message, type = 'success') {
    const bgColor = type === 'error' ? 'bg-danger' : 'bg-success';

    const toast = document.createElement('div');
    toast.className = 'position-fixed bottom-0 end-0 p-3';
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <div class="toast show" role="alert">
            <div class="toast-body text-white ${bgColor}">
                ${message}
            </div>
        </div>
    `;
    document.body.appendChild(toast);

    setTimeout(() => {
        if (toast.parentNode) {
            document.body.removeChild(toast);
        }
    }, 3000);
}

// Format price with Indian currency
function formatPrice(price) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2
    }).format(price);
}

// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}