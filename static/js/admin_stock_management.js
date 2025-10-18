// Admin Stock Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin Stock Management initialized');

    // Initialize stock management functionality
    initStockManagement();

    function initStockManagement() {
        setupEventListeners();
        setupMovementFilter();
        setupQuickStockForm();
    }

    function setupEventListeners() {
        // Restock product buttons
        document.querySelectorAll('.restock-product').forEach(button => {
            button.addEventListener('click', handleRestockProduct);
        });

        // Add stock form
        const addStockForm = document.getElementById('addStockForm');
        if (addStockForm) {
            addStockForm.addEventListener('submit', handleAddStock);
        }

        // Quick stock form
        const quickStockForm = document.getElementById('quickStockForm');
        if (quickStockForm) {
            quickStockForm.addEventListener('submit', handleQuickStock);
        }

        // Refresh movements
        const refreshBtn = document.getElementById('refreshMovements');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', refreshMovements);
        }

        // Bulk update functionality
        setupBulkUpdate();
    }

    function setupMovementFilter() {
        const movementFilter = document.getElementById('movementFilter');
        if (movementFilter) {
            movementFilter.addEventListener('change', function() {
                const filterValue = this.value;
                const rows = document.querySelectorAll('.movement-row');

                rows.forEach(row => {
                    if (filterValue === 'all' || row.getAttribute('data-movement-type') === filterValue) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
        }
    }

    function setupQuickStockForm() {
        const quickAction = document.getElementById('quickAction');
        const quickProduct = document.getElementById('quickProduct');

        if (quickAction && quickProduct) {
            quickAction.addEventListener('change', updateQuickStockPlaceholder);
            quickProduct.addEventListener('change', updateQuickStockInfo);
        }
    }

    function updateQuickStockPlaceholder() {
        const action = document.getElementById('quickAction').value;
        const quantityInput = document.getElementById('quickQuantity');

        switch(action) {
            case 'add':
                quantityInput.placeholder = 'Quantity to add...';
                break;
            case 'remove':
                quantityInput.placeholder = 'Quantity to remove...';
                break;
            case 'set':
                quantityInput.placeholder = 'New stock level...';
                break;
        }
    }

    function updateQuickStockInfo() {
        const productSelect = document.getElementById('quickProduct');
        const selectedOption = productSelect.options[productSelect.selectedIndex];
        const currentStock = selectedOption.getAttribute('data-current-stock');

        // You could show current stock info here
        console.log('Current stock:', currentStock);
    }

    function handleRestockProduct(e) {
        const productId = e.currentTarget.getAttribute('data-product-id');
        const productName = e.currentTarget.getAttribute('data-product-name');

        // Populate the add stock modal with this product
        const stockProduct = document.getElementById('stockProduct');
        if (stockProduct) {
            stockProduct.value = productId;
        }

        // Show the add stock modal
        const addStockModal = new bootstrap.Modal(document.getElementById('addStockModal'));
        addStockModal.show();
    }

    function handleAddStock(e) {
        e.preventDefault();

        const productId = document.getElementById('stockProduct').value;
        const quantity = document.getElementById('stockQuantity').value;
        const reason = document.getElementById('stockReason').value;
        const notes = document.getElementById('stockNotes').value;

        if (!productId || !quantity || !reason) {
            showAlert('Please fill all required fields.', 'danger');
            return;
        }

        // Show loading state
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="bi bi-arrow-repeat spinner-border spinner-border-sm me-2"></i>Adding...';
        submitBtn.disabled = true;

        // Submit stock addition - USING CORRECT ENDPOINT
        fetch('/admin/stock/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: parseInt(quantity),
                reason: reason,
                notes: notes,
                movement_type: 'purchase'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Stock added successfully!', 'success');
                bootstrap.Modal.getInstance(document.getElementById('addStockModal')).hide();
                refreshPage();
            } else {
                showAlert(data.message || 'Failed to add stock.', 'danger');
            }
        })
        .catch(error => {
            console.error('Error adding stock:', error);
            showAlert('Error adding stock.', 'danger');
        })
        .finally(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        });
    }

    function handleQuickStock(e) {
        e.preventDefault();

        const productId = document.getElementById('quickProduct').value;
        const action = document.getElementById('quickAction').value;
        const quantity = document.getElementById('quickQuantity').value;
        const reason = document.getElementById('quickReason').value;

        if (!productId || !quantity) {
            showAlert('Please fill all required fields.', 'danger');
            return;
        }

        let finalQuantity;

        switch(action) {
            case 'add':
                finalQuantity = parseInt(quantity);
                break;
            case 'remove':
                finalQuantity = -parseInt(quantity);
                break;
            case 'set':
                // For set action, we need to calculate the difference
                const currentStock = parseInt(document.getElementById('quickProduct')
                    .options[document.getElementById('quickProduct').selectedIndex]
                    .getAttribute('data-current-stock'));
                finalQuantity = parseInt(quantity) - currentStock;
                break;
        }

        // Show loading state
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="bi bi-arrow-repeat spinner-border spinner-border-sm me-2"></i>Updating...';
        submitBtn.disabled = true;

        // USE THE EXISTING UPDATE_STOCK ROUTE - CORRECTED ENDPOINT
        fetch(`/admin/products/${productId}/stock`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                stock_quantity: parseInt(quantity), // Use the target quantity for 'set' action
                reason: reason || 'Quick stock adjustment'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Stock updated successfully!', 'success');
                e.target.reset();
                refreshPage();
            } else {
                showAlert(data.message || 'Failed to update stock.', 'danger');
            }
        })
        .catch(error => {
            console.error('Error updating stock:', error);
            showAlert('Error updating stock.', 'danger');
        })
        .finally(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        });
    }

    function setupBulkUpdate() {
        // Add row to bulk update table
        const addRowBtn = document.getElementById('addBulkRow');
        if (addRowBtn) {
            addRowBtn.addEventListener('click', function() {
                const tbody = document.querySelector('#bulkStockTable tbody');
                const newRow = document.createElement('tr');
                newRow.innerHTML = `
                    <td><input type="text" class="form-control form-control-sm" placeholder="SKU"></td>
                    <td><input type="number" class="form-control form-control-sm" placeholder="Quantity"></td>
                    <td>
                        <button type="button" class="btn btn-sm btn-outline-danger remove-row">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(newRow);

                // Add event listener to new remove button
                newRow.querySelector('.remove-row').addEventListener('click', function() {
                    this.closest('tr').remove();
                });
            });
        }

        // Remove row event delegation
        document.addEventListener('click', function(e) {
            if (e.target.closest('.remove-row')) {
                e.target.closest('tr').remove();
            }
        });

        // Process bulk update
        const processBulkBtn = document.getElementById('processBulkUpdate');
        if (processBulkBtn) {
            processBulkBtn.addEventListener('click', processBulkUpdate);
        }

        // Download template
        const downloadTemplate = document.getElementById('downloadTemplate');
        if (downloadTemplate) {
            downloadTemplate.addEventListener('click', function(e) {
                e.preventDefault();
                downloadCSVTemplate();
            });
        }
    }

    function processBulkUpdate() {
        const csvFile = document.getElementById('bulkCsvFile').files[0];
        const manualRows = document.querySelectorAll('#bulkStockTable tbody tr');

        let updates = [];

        // Process CSV file
        if (csvFile) {
            // You would need to implement CSV parsing here
            showAlert('CSV processing would be implemented here.', 'info');
            return;
        }

        // Process manual entries
        manualRows.forEach(row => {
            const skuInput = row.querySelector('input[type="text"]');
            const quantityInput = row.querySelector('input[type="number"]');

            if (skuInput.value && quantityInput.value) {
                updates.push({
                    sku: skuInput.value,
                    quantity: parseInt(quantityInput.value)
                });
            }
        });

        if (updates.length === 0) {
            showAlert('No valid stock updates found.', 'warning');
            return;
        }

        // Show loading state
        const processBtn = document.getElementById('processBulkUpdate');
        const originalText = processBtn.innerHTML;
        processBtn.innerHTML = '<i class="bi bi-arrow-repeat spinner-border spinner-border-sm me-2"></i>Processing...';
        processBtn.disabled = true;

        // USE CORRECT BULK UPDATE ENDPOINT
        fetch('/admin/stock/bulk-update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ updates: updates })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(`Bulk update completed! ${data.updated} products updated.`, 'success');
                bootstrap.Modal.getInstance(document.getElementById('bulkStockUpdateModal')).hide();
                refreshPage();
            } else {
                showAlert(data.message || 'Failed to process bulk update.', 'danger');
            }
        })
        .catch(error => {
            console.error('Error processing bulk update:', error);
            showAlert('Error processing bulk update.', 'danger');
        })
        .finally(() => {
            processBtn.innerHTML = originalText;
            processBtn.disabled = false;
        });
    }

    function downloadCSVTemplate() {
        const csvContent = "SKU,Quantity\nEXAMPLE001,100\nEXAMPLE002,50";
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'stock_update_template.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    }

    function refreshMovements() {
        // You could implement AJAX refresh here
        showAlert('Refreshing stock movements...', 'info');
        setTimeout(() => {
            // Simulate refresh
            const rows = document.querySelectorAll('.movement-row');
            rows.forEach(row => {
                row.classList.add('fade-in');
            });
        }, 500);
    }

    function refreshPage() {
        setTimeout(() => {
            window.location.reload();
        }, 1500);
    }

    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }

    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('.container-fluid');
        container.insertBefore(alertDiv, container.firstChild);

        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
});

// Utility functions
window.stockManager = {
    refresh: function() {
        window.location.reload();
    },
    showLowStock: function() {
        document.getElementById('movementFilter').value = 'all';
        document.querySelectorAll('.movement-row').forEach(row => row.style.display = '');
        // Scroll to low stock section
        document.querySelector('.card-border-warning').scrollIntoView({ behavior: 'smooth' });
    }
};