// Only AOS re-initialization if needed for this specific page
document.addEventListener('DOMContentLoaded', function() {
    if (typeof AOS !== 'undefined') {
        AOS.refresh(); // Refresh AOS for dynamic content if needed
    }
});

// Toggle search functionality for floating search icon
function toggleSearch() {
    // Check if mobile search is available (for mobile devices)
    const mobileSearch = document.getElementById('mobileSearch');
    if (mobileSearch && window.innerWidth < 1200) {
        // Toggle mobile search on mobile devices
        const bsCollapse = new bootstrap.Collapse(mobileSearch, {
            toggle: true
        });
    } else {
        // Focus on desktop search input
        const desktopSearch = document.querySelector('.desktop-search-form input');
        if (desktopSearch) {
            desktopSearch.focus();
        } else {
            // Fallback: redirect to search page
            window.location.href = "{{ url_for('shop.search') }}";
        }
    }
}

// Add hover effects for floating icons
document.addEventListener('DOMContentLoaded', function() {
    const floatingIcons = document.querySelectorAll('.floating-icon');

    floatingIcons.forEach(icon => {
        // Add hover effect
        icon.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
            this.style.transition = 'transform 0.3s ease';
        });

        icon.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });

        // Add click animation
        icon.addEventListener('click', function() {
            this.style.transform = 'scale(0.9)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    });
});