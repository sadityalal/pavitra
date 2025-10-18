// Admin Orders Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin Orders Management initialized');

    // Initialize orders functionality
    initOrdersManagement();

    function initOrdersManagement() {
        setupEventListeners();
        setupBulkActions();
        setupExportFunctionality();
    }

    function setupEventListeners() {
        // Refresh orders
        const refreshBtn = document.getElementById('refreshOrders');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', refreshOrders);
        }

        // Select all orders checkbox
        const selectAll = document.getElementById('selectAllOrders');
        if (selectAll) {
            selectAll.addEventListener('change', function() {
                const checkboxes = document.querySelectorAll('.order-checkbox');
                checkboxes.forEach(checkbox => {
                    checkbox.checked = this.checked;
                });
            });
        }

        // Date range toggle for export
        const exportDateRange = document.getElementById('exportDateRange');
        if (exportDateRange) {
            exportDateRange.addEventListener('change', function() {
                const customRange = document.getElementById('customDateRange');
                customRange.style.display = this.value === 'custom' ? 'block' : 'none';
            });
        }
    }

    function setupBulkActions() {
        const applyBulkBtn = document.getElementById('applyBulkAction');
        const bulkActionSelect = document.getElementById('bulkAction');

        if (applyBulkBtn && bulkActionSelect) {
            applyBulkBtn.addEventListener('click', function() {
                const action = bulkActionSelect.value;
                const selectedOrders = getSelectedOrders();

                if (!action) {
                    showAlert('Please select a bulk action.', 'warning');
                    return;
                }

                if (selectedOrders.length === 0) {
                    showAlert('Please select at least one order.', 'warning');
                    return;
                }

                performBulkAction(action, selectedOrders);
            });
        }
    }

    function setupExportFunctionality() {
        const confirmExport = document.getElementById('confirmExport');
        if (confirmExport) {
            confirmExport.addEventListener('click', handleExportOrders);
        }

        // Quick export buttons
        const exportCSV = document.getElementById('exportCSV');
        if (exportCSV) {
            exportCSV.addEventListener('click', function(e) {
                e.preventDefault();
                quickExport('csv');
            });
        }

        const exportPDF = document.getElementById('exportPDF');
        if (exportPDF) {
            exportPDF.addEventListener('click', function(e) {
                e.preventDefault();
                quickExport('pdf');
            });
        }
    }

    function refreshOrders() {
        window.location.reload();
    }

    function getSelectedOrders() {
        const selected = [];
        document.querySelectorAll('.order-checkbox:checked').forEach(checkbox => {
            selected.push(checkbox.value);
        });
        return selected;
    }

    function performBulkAction(action, orderIds) {
        // Show loading state
        const applyBtn = document.getElementById('applyBulkAction');
        const originalText = applyBtn.innerHTML;
        applyBtn.innerHTML = '<i class="bi bi-arrow-repeat spinner-border spinner-border-sm me-2"></i>Processing...';
        applyBtn.disabled = true;

        fetch('/admin/orders/bulk-update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                action: action,
                order_ids: orderIds
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(`Bulk action completed! ${data.updated} orders updated.`, 'success');
                refreshOrders();
            } else {
                showAlert(data.message || 'Failed to perform bulk action.', 'danger');
            }
        })
        .catch(error => {
            console.error('Error performing bulk action:', error);
            showAlert('Error performing bulk action.', 'danger');
        })
        .finally(() => {
            applyBtn.innerHTML = originalText;
            applyBtn.disabled = false;
        });
    }

    function handleExportOrders() {
        const format = document.getElementById('exportFormat').value;
        const dateRange = document.getElementById('exportDateRange').value;
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;

        let exportUrl = `/admin/orders/export?format=${format}`;

        if (dateRange !== 'all') {
            exportUrl += `&date_range=${dateRange}`;
        }

        if (dateRange === 'custom' && startDate && endDate) {
            exportUrl += `&start_date=${startDate}&end_date=${endDate}`;
        }

        // Add include fields
        const includeCustomer = document.getElementById('includeCustomer').checked;
        const includeProducts = document.getElementById('includeProducts').checked;
        const includePayment = document.getElementById('includePayment').checked;

        if (!includeCustomer) exportUrl += '&exclude=customer';
        if (!includeProducts) exportUrl += '&exclude=products';
        if (!includePayment) exportUrl += '&exclude=payment';

        // Close modal and trigger download
        bootstrap.Modal.getInstance(document.getElementById('exportOrdersModal')).hide();
        window.open(exportUrl, '_blank');

        showAlert('Export started. Your download will begin shortly.', 'success');
    }

    function quickExport(format) {
        const exportUrl = `/admin/orders/export?format=${format}`;
        window.open(exportUrl, '_blank');
        showAlert(`Exporting orders as ${format.toUpperCase()}...`, 'info');
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

// Global function for updating order status
function updateOrderStatus(orderId, newStatus) {
    if (!confirm(`Are you sure you want to mark this order as ${newStatus}?`)) {
        return;
    }

    fetch(`/admin/orders/${orderId}/update-status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
        },
        body: JSON.stringify({
            status: newStatus
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(`Order status updated to ${newStatus}`, 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showAlert(data.message || 'Failed to update order status.', 'danger');
        }
    })
    .catch(error => {
        console.error('Error updating order status:', error);
        showAlert('Error updating order status.', 'danger');
    });
}

// Utility functions
window.orderManager = {
    refresh: function() {
        window.location.reload();
    },
    filterByStatus: function(status) {
        document.getElementById('status').value = status;
        document.getElementById('ordersFilterForm').submit();
    },
    showAlert: function(message, type) {
        // Implementation for global access
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('.container-fluid').insertBefore(alertDiv,
            document.querySelector('.container-fluid').firstChild);
    }
};