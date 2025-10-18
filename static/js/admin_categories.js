// Admin Categories Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin Categories Management initialized');

    // Initialize categories functionality
    initCategoriesManagement();

    function initCategoriesManagement() {
        setupEventListeners();
        setupSearchFunctionality();
        setupBulkActions();
    }

    function setupEventListeners() {
        // Add category form handling
        const addCategoryForm = document.getElementById('addCategoryForm');
        if (addCategoryForm) {
            addCategoryForm.addEventListener('submit', handleAddCategory);
        }

        // Edit category buttons
        document.querySelectorAll('.edit-category').forEach(button => {
            button.addEventListener('click', handleEditCategory);
        });

        // Delete category buttons
        document.querySelectorAll('.delete-category').forEach(button => {
            button.addEventListener('click', handleDeleteCategory);
        });

        // Toggle category status
        document.querySelectorAll('.toggle-category').forEach(button => {
            button.addEventListener('click', handleToggleCategory);
        });

        // View category products
        document.querySelectorAll('.view-category').forEach(button => {
            button.addEventListener('click', handleViewCategory);
        });

        // Refresh categories
        const refreshBtn = document.getElementById('refreshCategories');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', refreshCategories);
        }

        // Auto-generate slug from category name
        const categoryNameInput = document.getElementById('categoryName');
        const categorySlugInput = document.getElementById('categorySlug');
        if (categoryNameInput && categorySlugInput) {
            categoryNameInput.addEventListener('blur', function() {
                if (!categorySlugInput.value) {
                    categorySlugInput.value = generateSlug(this.value);
                }
            });
        }
    }

    function setupSearchFunctionality() {
        const searchInput = document.getElementById('categorySearch');
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                const rows = document.querySelectorAll('.category-row');

                rows.forEach(row => {
                    const categoryName = row.querySelector('h6').textContent.toLowerCase();
                    const categoryDescription = row.querySelector('small').textContent.toLowerCase();

                    if (categoryName.includes(searchTerm) || categoryDescription.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
        }
    }

    function setupBulkActions() {
        const applyBulkActionBtn = document.getElementById('applyBulkAction');
        const bulkActionSelect = document.getElementById('bulkAction');

        if (applyBulkActionBtn && bulkActionSelect) {
            applyBulkActionBtn.addEventListener('click', function() {
                const action = bulkActionSelect.value;
                const selectedCategories = getSelectedCategories();

                if (!action) {
                    showAlert('Please select a bulk action.', 'warning');
                    return;
                }

                if (selectedCategories.length === 0) {
                    showAlert('Please select at least one category.', 'warning');
                    return;
                }

                performBulkAction(action, selectedCategories);
            });
        }

        // Select all checkbox
        const selectAllCheckbox = document.createElement('input');
        selectAllCheckbox.type = 'checkbox';
        selectAllCheckbox.className = 'form-check-input';
        selectAllCheckbox.style.marginLeft = '0';

        const firstTh = document.querySelector('thead th:first-child');
        if (firstTh) {
            firstTh.appendChild(selectAllCheckbox);
        }

        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.category-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }

    function handleAddCategory(e) {
        e.preventDefault();
        const formData = new FormData(e.target);

        // Basic validation
        const categoryName = formData.get('name');
        const gstSlab = parseFloat(formData.get('gst_slab'));

        if (!categoryName.trim()) {
            showAlert('Category name is required.', 'danger');
            return;
        }

        if (isNaN(gstSlab) || gstSlab < 0 || gstSlab > 100) {
            showAlert('Please enter a valid GST rate between 0 and 100.', 'danger');
            return;
        }

        // Show loading state
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="bi bi-arrow-repeat spinner-border spinner-border-sm me-2"></i>Creating...';
        submitBtn.disabled = true;

        // Submit form (you'll need to handle this in your backend)
        e.target.submit();
    }

    function handleEditCategory(e) {
        const categoryId = e.currentTarget.getAttribute('data-category-id');
        const editModal = new bootstrap.Modal(document.getElementById('editCategoryModal'));

        // Show loading state
        const modalBody = document.querySelector('#editCategoryModal .modal-body');
        modalBody.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading category details...</p>
            </div>
        `;

        // Fetch category data (you'll need to implement this endpoint)
        fetch(`/admin/categories/${categoryId}/edit`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    populateEditForm(data.category);
                } else {
                    showAlert('Failed to load category details.', 'danger');
                }
            })
            .catch(error => {
                console.error('Error loading category:', error);
                showAlert('Error loading category details.', 'danger');
            });

        editModal.show();
    }

    function populateEditForm(category) {
        const modalBody = document.querySelector('#editCategoryModal .modal-body');

        modalBody.innerHTML = `
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="editCategoryName" class="form-label">Category Name *</label>
                    <input type="text" class="form-control" id="editCategoryName" name="name" value="${category.name}" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="editCategoryNameHindi" class="form-label">Hindi Name</label>
                    <input type="text" class="form-control" id="editCategoryNameHindi" name="name_hindi" value="${category.name_hindi || ''}">
                </div>
            </div>

            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="editParentCategory" class="form-label">Parent Category</label>
                    <select class="form-select" id="editParentCategory" name="parent_id">
                        <option value="">No Parent (Main Category)</option>
                        ${generateParentOptions(category.id)}
                    </select>
                </div>
                <div class="col-md-6 mb-3">
                    <label for="editCategorySlug" class="form-label">URL Slug *</label>
                    <input type="text" class="form-control" id="editCategorySlug" name="slug" value="${category.slug}" required>
                </div>
            </div>

            <div class="mb-3">
                <label for="editCategoryDescription" class="form-label">Description</label>
                <textarea class="form-control" id="editCategoryDescription" name="description" rows="3">${category.description || ''}</textarea>
            </div>

            <div class="row">
                <div class="col-md-4 mb-3">
                    <label for="editGstSlab" class="form-label">GST Rate (%) *</label>
                    <input type="number" step="0.01" class="form-control" id="editGstSlab" name="gst_slab" value="${category.gst_slab}" required>
                </div>
                <div class="col-md-4 mb-3">
                    <label for="editHsnCode" class="form-label">HSN Code</label>
                    <input type="text" class="form-control" id="editHsnCode" name="hsn_code" value="${category.hsn_code || ''}">
                </div>
                <div class="col-md-4 mb-3">
                    <label for="editSortOrder" class="form-label">Sort Order</label>
                    <input type="number" class="form-control" id="editSortOrder" name="sort_order" value="${category.sort_order}">
                </div>
            </div>

            <div class="row">
                <div class="col-md-6">
                    <div class="form-check form-switch mb-3">
                        <input class="form-check-input" type="checkbox" id="editIsActive" name="is_active" ${category.is_active ? 'checked' : ''}>
                        <label class="form-check-label" for="editIsActive">Active Category</label>
                    </div>
                    <div class="form-check form-switch mb-3">
                        <input class="form-check-input" type="checkbox" id="editIsFeatured" name="is_featured" ${category.is_featured ? 'checked' : ''}>
                        <label class="form-check-label" for="editIsFeatured">Featured Category</label>
                    </div>
                </div>
            </div>
        `;

        // Set the selected parent category
        if (category.parent_id) {
            const parentSelect = document.getElementById('editParentCategory');
            if (parentSelect) {
                parentSelect.value = category.parent_id;
            }
        }

        // Set up the edit form submission
        const editForm = document.getElementById('editCategoryForm');
        editForm.action = `/admin/categories/${category.id}/edit`;
        editForm.onsubmit = handleEditCategorySubmit;
    }

    function handleEditCategorySubmit(e) {
        e.preventDefault();
        // Handle edit form submission
        // You'll need to implement this based on your backend
        console.log('Editing category:', e.target.action);
        e.target.submit();
    }

    function handleDeleteCategory(e) {
        const categoryId = e.currentTarget.getAttribute('data-category-id');
        const categoryName = e.currentTarget.closest('tr').querySelector('h6').textContent;
        const productCount = e.currentTarget.closest('tr').querySelector('.badge').textContent;

        document.getElementById('deleteCategoryInfo').textContent =
            `Category: ${categoryName} (${productCount} products)`;

        const deleteModal = new bootstrap.Modal(document.getElementById('deleteCategoryModal'));
        const confirmBtn = document.getElementById('confirmDeleteCategory');

        // Remove previous event listeners
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

        newConfirmBtn.addEventListener('click', function() {
            deleteCategory(categoryId);
        });

        deleteModal.show();
    }

    function deleteCategory(categoryId) {
        // Implement category deletion
        fetch(`/admin/categories/${categoryId}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Category deleted successfully!', 'success');
                document.querySelector(`[data-category-id="${categoryId}"]`).remove();
                bootstrap.Modal.getInstance(document.getElementById('deleteCategoryModal')).hide();
            } else {
                showAlert(data.message || 'Failed to delete category.', 'danger');
            }
        })
        .catch(error => {
            console.error('Error deleting category:', error);
            showAlert('Error deleting category.', 'danger');
        });
    }

    function handleToggleCategory(e) {
        const categoryId = e.currentTarget.getAttribute('data-category-id');
        const action = e.currentTarget.getAttribute('data-action');

        fetch(`/admin/categories/${categoryId}/toggle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ action: action })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(`Category ${action}d successfully!`, 'success');
                refreshCategories();
            } else {
                showAlert(data.message || `Failed to ${action} category.`, 'danger');
            }
        })
        .catch(error => {
            console.error('Error toggling category:', error);
            showAlert('Error updating category status.', 'danger');
        });
    }

    function handleViewCategory(e) {
        const categoryId = e.currentTarget.getAttribute('data-category-id');
        // Redirect to category products page
        window.location.href = `/admin/categories/${categoryId}/products`;
    }

    function refreshCategories() {
        window.location.reload();
    }

    function getSelectedCategories() {
        const selected = [];
        document.querySelectorAll('.category-checkbox:checked').forEach(checkbox => {
            selected.push(checkbox.value);
        });
        return selected;
    }

    function performBulkAction(action, categoryIds) {
        fetch('/admin/categories/bulk-action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                action: action,
                category_ids: categoryIds
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(`Bulk action completed successfully!`, 'success');
                refreshCategories();
            } else {
                showAlert(data.message || 'Failed to perform bulk action.', 'danger');
            }
        })
        .catch(error => {
            console.error('Error performing bulk action:', error);
            showAlert('Error performing bulk action.', 'danger');
        });
    }

    function generateSlug(text) {
        return text
            .toLowerCase()
            .trim()
            .replace(/[^\w\s-]/g, '')
            .replace(/[\s_-]+/g, '-')
            .replace(/^-+|-+$/g, '');
    }

    function generateParentOptions(excludeId) {
        // This should be populated from your categories data
        // For now, returning empty string - you'll need to implement this
        return '';
    }

    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }

    function showAlert(message, type) {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Add to page
        const container = document.querySelector('.container-fluid');
        container.insertBefore(alertDiv, container.firstChild);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
});

// Utility functions
window.categoryManager = {
    refresh: function() {
        window.location.reload();
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