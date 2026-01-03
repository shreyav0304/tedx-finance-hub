/**
 * Transaction table filtering and search functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const categoryFilter = document.getElementById('categoryFilter');
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    const minAmount = document.getElementById('minAmount');
    const maxAmount = document.getElementById('maxAmount');
    const submittedBy = document.getElementById('submittedBy');
    const table = document.getElementById('transactionsTable');
    
    if (!table) return; // Exit if not on transactions page
    
    // Advanced filters toggle
    const advancedFiltersToggle = document.getElementById('advancedFiltersToggle');
    const advancedFiltersContent = document.getElementById('advancedFiltersContent');
    const advancedChevron = document.getElementById('advancedChevron');
    
    if (advancedFiltersToggle) {
        advancedFiltersToggle.addEventListener('click', function() {
            advancedFiltersContent.classList.toggle('hidden');
            advancedChevron.style.transform = advancedFiltersContent.classList.contains('hidden') 
                ? 'rotate(0deg)' 
                : 'rotate(180deg)';
        });
        
        // Auto-expand if any advanced filter has value
        const hasAdvancedFilters = (startDate && startDate.value) || 
                                   (endDate && endDate.value) || 
                                   (minAmount && minAmount.value) || 
                                   (maxAmount && maxAmount.value) ||
                                   (submittedBy && submittedBy.value);
        if (hasAdvancedFilters) {
            advancedFiltersContent.classList.remove('hidden');
            advancedChevron.style.transform = 'rotate(180deg)';
        }
    }
    
    // Real-time search and filter (client-side for UX, server-side on page load)
    function filterTransactions() {
        const searchTerm = searchInput.value.toLowerCase();
        const statusValue = statusFilter.value;
        const categoryValue = categoryFilter.value;
        const rows = table.querySelectorAll('tbody tr');
        let visibleCount = 0;
        
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length === 0) return;
            
            // Get row data
            const rowData = row.dataset;
            const title = cells[2] ? cells[2].textContent.toLowerCase() : '';
            const category = rowData.category || '';
            const status = rowData.status || '';
            
            // Check search (searches in title - server handles full search)
            const matchesSearch = !searchTerm || title.includes(searchTerm);
            
            // Check status
            const matchesStatus = statusValue === 'all' || status === statusValue;
            
            // Check category
            const matchesCategory = categoryValue === 'all' || category === categoryValue;
            
            if (matchesSearch && matchesStatus && matchesCategory) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });
        
        // Show "no results" message if needed
        if (visibleCount === 0) {
            const tbody = table.querySelector('tbody');
            let noResultsRow = tbody.querySelector('.no-results');
            if (!noResultsRow) {
                noResultsRow = document.createElement('tr');
                noResultsRow.className = 'no-results';
                noResultsRow.innerHTML = '<td colspan="10" class="text-center py-8 text-slate-500 dark:text-slate-400">No transactions found matching filters</td>';
                tbody.appendChild(noResultsRow);
            }
        } else {
            const noResultsRow = table.querySelector('.no-results');
            if (noResultsRow) {
                noResultsRow.remove();
            }
        }
    }
    
    // Apply server-side filters by updating URL
    function applyServerFilters() {
        const params = new URLSearchParams();
        
        if (searchInput.value) params.set('search', searchInput.value);
        if (statusFilter.value !== 'all') params.set('status', statusFilter.value);
        if (categoryFilter.value !== 'all') params.set('category', categoryFilter.value);
        if (startDate && startDate.value) params.set('start_date', startDate.value);
        if (endDate && endDate.value) params.set('end_date', endDate.value);
        if (minAmount && minAmount.value) params.set('min_amount', minAmount.value);
        if (maxAmount && maxAmount.value) params.set('max_amount', maxAmount.value);
        if (submittedBy && submittedBy.value) params.set('submitted_by', submittedBy.value);
        
        // Reload page with filters
        window.location.search = params.toString();
    }
    
    // Debounce function for search input
    let searchTimeout;
    function debounceSearch() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            applyServerFilters();
        }, 800); // Wait 800ms after user stops typing
    }
    
    // Event listeners for real-time client-side filtering
    searchInput.addEventListener('input', filterTransactions);
    statusFilter.addEventListener('change', function() {
        filterTransactions();
        applyServerFilters(); // Also update URL
    });
    categoryFilter.addEventListener('change', function() {
        filterTransactions();
        applyServerFilters(); // Also update URL
    });
    
    // Event listeners for advanced filters (server-side only)
    if (startDate) startDate.addEventListener('change', applyServerFilters);
    if (endDate) endDate.addEventListener('change', applyServerFilters);
    if (minAmount) minAmount.addEventListener('blur', applyServerFilters);
    if (maxAmount) maxAmount.addEventListener('blur', applyServerFilters);
    if (submittedBy) submittedBy.addEventListener('blur', applyServerFilters);
    
    // Debounced search for server-side filtering
    searchInput.addEventListener('input', debounceSearch);
    
    // Keyboard shortcut for search (/)
    document.addEventListener('keydown', function(e) {
        if (e.key === '/' && !e.ctrlKey && !e.metaKey && document.activeElement.tagName !== 'INPUT') {
            e.preventDefault();
            searchInput.focus();
        }
    });
    
    // Mobile filters toggle
    const filtersToggle = document.getElementById('filtersToggle');
    const filtersContent = document.getElementById('filtersContent');
    const filtersChevron = document.getElementById('filtersChevron');
    
    if (filtersToggle) {
        filtersToggle.addEventListener('click', function() {
            filtersContent.classList.toggle('hidden');
            filtersChevron.style.transform = filtersContent.classList.contains('hidden') 
                ? 'rotate(0deg)' 
                : 'rotate(180deg)';
        });
    }
});

// Clear all filters function
function clearAllFilters() {
    window.location.href = window.location.pathname; // Reload without query params
}


// Bulk actions
function bulkApprove() {
    const confirmed = confirm('Approve selected transactions? This action cannot be undone.');
    if (confirmed) {
        // Get selected row IDs and submit bulk approve form
        const selected = getSelectedRows();
        if (selected.length === 0) {
            showToast('Please select at least one transaction', 'warning');
            return;
        }
        submitBulkAction('approve', selected);
    }
}

function bulkReject() {
    const confirmed = confirm('Reject selected transactions? This action cannot be undone.');
    if (confirmed) {
        const selected = getSelectedRows();
        if (selected.length === 0) {
            showToast('Please select at least one transaction', 'warning');
            return;
        }
        submitBulkAction('reject', selected);
    }
}

function bulkExport() {
    const selected = getSelectedRows();
    if (selected.length === 0) {
        showToast('Please select at least one transaction', 'warning');
        return;
    }
    // Export logic would go here
    showToast('Exporting ' + selected.length + ' transactions...', 'info');
}

function getSelectedRows() {
    const checkboxes = document.querySelectorAll('input[name="transaction_ids"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

function submitBulkAction(action, ids) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/bulk-action/'; // Adjust URL as needed
    
    const actionInput = document.createElement('input');
    actionInput.type = 'hidden';
    actionInput.name = 'action';
    actionInput.value = action;
    form.appendChild(actionInput);
    
    ids.forEach(id => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'transaction_ids';
        input.value = id;
        form.appendChild(input);
    });
    
    // Add CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken.value;
        form.appendChild(csrfInput);
    }
    
    document.body.appendChild(form);
    form.submit();
}

// Enhanced delete with confirmation
function deleteTransaction(id) {
    if (confirm('Are you sure you want to delete this transaction? This action cannot be undone.')) {
        document.getElementById(`delete-form-${id}`).submit();
    }
}

function approveTransaction(id) {
    if (confirm('Approve this transaction?')) {
        document.getElementById(`approve-form-${id}`).submit();
    }
}

function rejectTransaction(id) {
    const reason = prompt('Enter rejection reason (optional):');
    if (reason !== null) {
        // Submit with reason
        const form = document.getElementById(`reject-form-${id}`);
        if (form) {
            const reasonInput = document.createElement('input');
            reasonInput.type = 'hidden';
            reasonInput.name = 'rejection_reason';
            reasonInput.value = reason;
            form.appendChild(reasonInput);
            form.submit();
        }
    }
}
