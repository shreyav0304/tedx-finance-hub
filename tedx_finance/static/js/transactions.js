/**
 * Transaction table filtering and search functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const categoryFilter = document.getElementById('categoryFilter');
    const table = document.getElementById('transactionsTable');
    
    if (!table) return; // Exit if not on transactions page
    
    // Real-time search and filter
    function filterTransactions() {
        const searchTerm = searchInput.value.toLowerCase();
        const statusValue = statusFilter.value;
        const categoryValue = categoryFilter.value;
        const rows = table.querySelectorAll('tbody tr');
        let visibleCount = 0;
        
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length === 0) return;
            
            const title = cells[0].textContent.toLowerCase();
            const category = cells[2].textContent.trim();
            const status = cells[5] ? cells[5].textContent.toLowerCase() : '';
            
            // Check search
            const matchesSearch = title.includes(searchTerm) || 
                                category.toLowerCase().includes(searchTerm);
            
            // Check status
            const matchesStatus = statusValue === 'all' || 
                                 status.includes(statusValue);
            
            // Check category
            const matchesCategory = categoryValue === 'all' || 
                                   category === categoryValue;
            
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
                noResultsRow.innerHTML = '<td colspan="10" class="text-center py-8 text-slate-500">No transactions found</td>';
                tbody.appendChild(noResultsRow);
            }
        } else {
            const noResultsRow = table.querySelector('.no-results');
            if (noResultsRow) {
                noResultsRow.remove();
            }
        }
    }
    
    // Event listeners
    searchInput.addEventListener('input', filterTransactions);
    statusFilter.addEventListener('change', filterTransactions);
    categoryFilter.addEventListener('change', filterTransactions);
    
    // Keyboard shortcut for search (/)
    document.addEventListener('keydown', function(e) {
        if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
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
