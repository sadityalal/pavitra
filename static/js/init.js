// static/js/init.js
// Initialize all components and plugins

function initializeAllComponents() {
    console.log('Initializing all components...');

    // Initialize Swiper
    const announcementSwiper = new Swiper('.announcement-slider', {
        loop: true,
        speed: 600,
        autoplay: {
            delay: 5000,
        },
        slidesPerView: 1,
        direction: 'vertical',
        effect: 'slide'
    });

    // Initialize AOS
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 1000,
            easing: 'ease-in-out',
            once: true,
            mirror: false
        });
    }

    // Initialize GLightbox
    if (typeof GLightbox !== 'undefined') {
        const lightbox = GLightbox({
            selector: '.glightbox'
        });
    }

    // Initialize PureCounter if it exists
    if (typeof PureCounter !== 'undefined') {
        new PureCounter();
    } else {
        console.log('PureCounter not found, skipping initialization');
    }

    // Mobile navigation toggle
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    const navmenu = document.querySelector('#navmenu');

    if (mobileNavToggle && navmenu) {
        mobileNavToggle.addEventListener('click', function(e) {
            e.preventDefault();
            navmenu.classList.toggle('mobile-nav-active');
            this.classList.toggle('bi-list');
            this.classList.toggle('bi-x');
        });
    }

    // Initialize dropdowns
    const dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    const dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl);
    });

    // Initialize cart and wishlist counts
    if (typeof updateCartCount !== 'undefined') {
        updateCartCount();
    }

    // Check if user is authenticated (this will be handled by template condition)
    if (typeof updateWishlistCount !== 'undefined') {
        updateWishlistCount();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeAllComponents();
});