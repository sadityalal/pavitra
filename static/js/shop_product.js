// Products page specific JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeProductsPage();
});

function initializeProductsPage() {
    initializeFilters();
    initializeSorting();

    // Refresh AOS for dynamic content
    if (typeof AOS !== 'undefined') {
        AOS.refresh();
    }
}

function initializeFilters() {
    const minPriceInput = document.getElementById('minPrice');
    const maxPriceInput = document.getElementById('maxPrice');

    if (minPriceInput && maxPriceInput) {
        minPriceInput.addEventListener('change', filterProducts);
        maxPriceInput.addEventListener('change', filterProducts);
    }

    document.querySelectorAll('.brand-filter').forEach(filter => {
        filter.addEventListener('change', filterProducts);
    });
}

function initializeSorting() {
    document.querySelectorAll('.sort-option').forEach(option => {
        option.addEventListener('click', function(e) {
            e.preventDefault();
            const sortBy = this.getAttribute('data-sort');
            sortProducts(sortBy);
        });
    });
}

function filterProducts() {
    const minPrice = parseFloat(document.getElementById('minPrice').value) || 0;
    const maxPrice = parseFloat(document.getElementById('maxPrice').value) || 1000000;

    const selectedBrands = Array.from(document.querySelectorAll('.brand-filter:checked'))
        .map(cb => cb.value);

    const products = document.querySelectorAll('.product-item');
    let visibleCount = 0;

    products.forEach(product => {
        const productPrice = parseFloat(product.getAttribute('data-price'));
        const productBrand = product.getAttribute('data-brand');

        const priceMatch = productPrice >= minPrice && productPrice <= maxPrice;
        const brandMatch = selectedBrands.length === 0 || selectedBrands.includes(productBrand);

        if (priceMatch && brandMatch) {
            product.style.display = 'block';
            visibleCount++;
        } else {
            product.style.display = 'none';
        }
    });

    document.getElementById('showingCount').textContent = visibleCount;
}

function sortProducts(sortBy) {
    const productsGrid = document.getElementById('productsGrid');
    const products = Array.from(document.querySelectorAll('.product-item'));

    products.sort((a, b) => {
        switch(sortBy) {
            case 'name_asc':
                return a.getAttribute('data-name').localeCompare(b.getAttribute('data-name'));
            case 'name_desc':
                return b.getAttribute('data-name').localeCompare(a.getAttribute('data-name'));
            case 'price_asc':
                return parseFloat(a.getAttribute('data-price')) - parseFloat(b.getAttribute('data-price'));
            case 'price_desc':
                return parseFloat(b.getAttribute('data-price')) - parseFloat(a.getAttribute('data-price'));
            default:
                return 0;
        }
    });

    products.forEach(product => {
        productsGrid.appendChild(product);
    });
}

function applyPriceFilter() {
    filterProducts();
}

function clearAllFilters() {
    document.getElementById('minPrice').value = 0;
    document.getElementById('maxPrice').value = 100000;
    document.querySelectorAll('.brand-filter').forEach(cb => cb.checked = false);
    filterProducts();
}

function quickView(productId) {
    showToast('Quick view feature coming soon!', 'info');
}