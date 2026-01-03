/**
 * UI Enhancements and Utility Functions
 * Includes: Confirmation dialogs, loading states, copy-to-clipboard, tooltips, keyboard shortcuts
 */

// ====== CONFIRMATION DIALOGS ======

function confirmAction(message, onConfirm, onCancel = null) {
    /**
     * Show a custom confirmation dialog
     * @param {string} message - The confirmation message
     * @param {function} onConfirm - Callback when confirmed
     * @param {function} onCancel - Optional callback when cancelled
     */
    const confirmed = confirm(message);
    if (confirmed) {
        onConfirm();
    } else if (onCancel) {
        onCancel();
    }
}

function confirmDelete(itemName, onConfirm) {
    /**
     * Confirm deletion of an item
     */
    confirmAction(
        `Are you sure you want to delete "${itemName}"? This action cannot be undone.`,
        onConfirm
    );
}

function confirmApproval(itemName, onConfirm) {
    /**
     * Confirm approval of a transaction
     */
    confirmAction(
        `Approve "${itemName}"? This action is permanent.`,
        onConfirm
    );
}

function confirmRejection(itemName, onConfirm) {
    /**
     * Confirm rejection of a transaction
     */
    confirmAction(
        `Reject and delete "${itemName}"? This action is permanent.`,
        onConfirm
    );
}

// Add confirmation to forms with class 'confirm-action'
document.addEventListener('DOMContentLoaded', function() {
    // Delete confirmations
    document.querySelectorAll('[data-confirm-delete]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const itemName = this.dataset.itemName || this.textContent.trim();
            if (!confirm(`Are you sure you want to delete "${itemName}"?`)) {
                e.preventDefault();
            }
        });
    });

    // Approve confirmations
    document.querySelectorAll('[data-confirm-approve]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const itemName = this.dataset.itemName || 'this item';
            if (!confirm(`Approve "${itemName}"?`)) {
                e.preventDefault();
            }
        });
    });

    // Reject confirmations
    document.querySelectorAll('[data-confirm-reject]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const itemName = this.dataset.itemName || 'this item';
            if (!confirm(`Reject "${itemName}"? This cannot be undone.`)) {
                e.preventDefault();
            }
        });
    });
});

// ====== LOADING STATES ======

function setButtonLoading(button, isLoading = true) {
    /**
     * Set button to loading state
     */
    if (!button) return;
    
    if (isLoading) {
        button.disabled = true;
        button.classList.add('opacity-75', 'cursor-not-allowed');
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = '<span class="inline-block mr-2">⏳</span>Processing...';
    } else {
        button.disabled = false;
        button.classList.remove('opacity-75', 'cursor-not-allowed');
        button.innerHTML = button.dataset.originalText || button.innerHTML;
    }
}

// Auto-add loading state to submit buttons
document.addEventListener('submit', function(e) {
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn && submitBtn.dataset.loadingState !== 'false') {
        setButtonLoading(submitBtn, true);
    }
});

// ====== COPY TO CLIPBOARD ======

function copyToClipboard(text, feedbackElement = null) {
    /**
     * Copy text to clipboard with feedback
     */
    navigator.clipboard.writeText(text).then(() => {
        if (feedbackElement) {
            const originalText = feedbackElement.innerHTML;
            feedbackElement.innerHTML = '✅ Copied!';
            feedbackElement.classList.add('text-green-600');
            setTimeout(() => {
                feedbackElement.innerHTML = originalText;
                feedbackElement.classList.remove('text-green-600');
            }, 2000);
        }
    }).catch(err => {
        console.error('Failed to copy:', err);
        if (feedbackElement) {
            feedbackElement.innerHTML = '❌ Copy failed';
            feedbackElement.classList.add('text-red-600');
            setTimeout(() => {
                feedbackElement.innerHTML = originalText;
                feedbackElement.classList.remove('text-red-600');
            }, 2000);
        }
    });
}

// Add copy buttons automatically
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[data-copy]').forEach(element => {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            const text = this.dataset.copy;
            copyToClipboard(text, this);
        });
        this.style.cursor = 'pointer';
        this.title = 'Click to copy';
        this.classList.add('hover:bg-opacity-80', 'transition');
    });
});

// ====== TOOLTIP HELP TEXT ======

function initializeTooltips() {
    /**
     * Initialize tooltips with title attributes
     */
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        const tooltip = element.dataset.tooltip;
        element.title = tooltip;
    });
}

document.addEventListener('DOMContentLoaded', initializeTooltips);

// ====== BACK TO TOP BUTTON ======

function initBackToTop() {
    /**
     * Create and manage "Back to Top" button
     */
    const backToTopBtn = document.createElement('button');
    backToTopBtn.id = 'backToTopBtn';
    backToTopBtn.innerHTML = '⬆️';
    backToTopBtn.className = 'fixed bottom-6 right-6 bg-purple-600 text-white p-3 rounded-full shadow-lg hover:bg-purple-700 transition opacity-0 invisible duration-300 z-40';
    backToTopBtn.title = 'Back to top (End key)';
    
    document.body.appendChild(backToTopBtn);
    
    // Show button when scrolled down
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTopBtn.classList.remove('opacity-0', 'invisible');
        } else {
            backToTopBtn.classList.add('opacity-0', 'invisible');
        }
    });
    
    // Scroll to top on click
    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    
    // Also support End key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'End') {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });
}

document.addEventListener('DOMContentLoaded', initBackToTop);

// ====== KEYBOARD SHORTCUTS ======

function initKeyboardShortcuts() {
    /**
     * Initialize keyboard shortcuts
     * Ctrl+K: Open search
     * Ctrl+N: New item
     * Ctrl+S: Save/Submit form
     * Escape: Close modals/dialogs
     */
    document.addEventListener('keydown', (e) => {
        // Only trigger if not typing in input
        if (e.target.tagName === 'INPUT' && e.ctrlKey === false && e.key !== 'Escape') {
            return;
        }

        // Ctrl+K: Open search
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('[data-search-input]');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            } else {
                console.log('Search input not found');
            }
        }

        // Ctrl+N: New item (first "New" button)
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            const newBtn = document.querySelector('[data-new-item]');
            if (newBtn) {
                newBtn.click();
            }
        }

        // Ctrl+S: Save/Submit form
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            const submitBtn = document.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.click();
            }
        }

        // Escape: Close modals
        if (e.key === 'Escape') {
            const modal = document.querySelector('[data-modal].open');
            if (modal) {
                modal.classList.remove('open');
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', initKeyboardShortcuts);

// ====== DARK MODE PERSISTENCE ======

function initDarkModePersistence() {
    /**
     * Remember user's dark mode preference
     */
    const htmlElement = document.documentElement;
    const darkModeToggle = document.querySelector('[data-dark-mode-toggle]');

    // Load saved preference
    const savedTheme = localStorage.getItem('tedx-theme');
    if (savedTheme === 'light') {
        htmlElement.classList.add('light-theme');
        if (darkModeToggle) {
            darkModeToggle.textContent = '☀️';
        }
    } else if (savedTheme === 'dark') {
        htmlElement.classList.remove('light-theme');
        if (darkModeToggle) {
            darkModeToggle.textContent = '🌙';
        }
    }

    // Save preference on toggle
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            htmlElement.classList.toggle('light-theme');
            const isLight = htmlElement.classList.contains('light-theme');
            localStorage.setItem('tedx-theme', isLight ? 'light' : 'dark');
            darkModeToggle.textContent = isLight ? '☀️' : '🌙';
        });
    }
}

document.addEventListener('DOMContentLoaded', initDarkModePersistence);

// ====== FORM VALIDATION IMPROVEMENTS ======

function improveFormValidation() {
    /**
     * Enhance form validation messages
     */
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('border-red-500', 'ring-red-500');
                    
                    // Show inline error
                    const errorMsg = input.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        const error = document.createElement('div');
                        error.className = 'error-message text-red-600 text-sm mt-1';
                        error.textContent = `${input.placeholder || input.name} is required`;
                        input.parentNode.insertBefore(error, input.nextSibling);
                    }
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });

        // Remove error styling on input
        form.querySelectorAll('input, textarea, select').forEach(input => {
            input.addEventListener('input', () => {
                input.classList.remove('border-red-500', 'ring-red-500');
                const error = input.nextElementSibling;
                if (error && error.classList.contains('error-message')) {
                    error.remove();
                }
            });
        });
    });
}

document.addEventListener('DOMContentLoaded', improveFormValidation);

// ====== PAGINATION HELPER ======

function initPagination(itemsPerPage = 10) {
    /**
     * Add pagination to long tables
     */
    const tables = document.querySelectorAll('[data-paginate]');
    
    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        const pageCount = Math.ceil(rows.length / itemsPerPage);
        
        if (pageCount <= 1) return; // No pagination needed
        
        // Hide all rows except first page
        rows.forEach((row, index) => {
            row.style.display = index < itemsPerPage ? '' : 'none';
        });
        
        // Create pagination controls
        const paginationDiv = document.createElement('div');
        paginationDiv.className = 'flex justify-center gap-2 mt-6 flex-wrap';
        
        for (let i = 1; i <= pageCount; i++) {
            const btn = document.createElement('button');
            btn.className = `px-3 py-1 rounded ${i === 1 ? 'bg-purple-600 text-white' : 'bg-slate-200 dark:bg-slate-700'}`;
            btn.textContent = i;
            btn.addEventListener('click', () => {
                // Hide all rows
                rows.forEach(row => row.style.display = 'none');
                // Show current page
                for (let j = (i - 1) * itemsPerPage; j < i * itemsPerPage && j < rows.length; j++) {
                    rows[j].style.display = '';
                }
                // Update button styles
                paginationDiv.querySelectorAll('button').forEach(b => {
                    b.classList.remove('bg-purple-600', 'text-white');
                    b.classList.add('bg-slate-200', 'dark:bg-slate-700');
                });
                btn.classList.remove('bg-slate-200', 'dark:bg-slate-700');
                btn.classList.add('bg-purple-600', 'text-white');
            });
            paginationDiv.appendChild(btn);
        }
        
        table.parentNode.insertBefore(paginationDiv, table.nextSibling);
    });
}

document.addEventListener('DOMContentLoaded', () => initPagination(15));

// ====== EXPORT TO CSV HELPER ======

function exportTableToCSV(tableId, filename = 'export.csv') {
    /**
     * Export table to CSV
     */
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const csvrow = [];
        cols.forEach(col => {
            csvrow.push('"' + col.textContent.replace(/"/g, '""') + '"');
        });
        csv.push(csvrow.join(','));
    });
    
    const csvContent = 'data:text/csv;charset=utf-8,' + csv.join('\n');
    const link = document.createElement('a');
    link.setAttribute('href', encodeURI(csvContent));
    link.setAttribute('download', filename);
    link.click();
}

// ====== SEARCH/FILTER TABLE ======

function filterTable(inputId, tableId) {
    /**
     * Filter table rows based on search input
     */
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    if (!input || !table) return;
    
    input.addEventListener('keyup', () => {
        const filter = input.value.toUpperCase();
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toUpperCase();
            row.style.display = text.includes(filter) ? '' : 'none';
        });
    });
}

// ====== UTILITY: SHOW NOTIFICATIONS ======

function showNotification(message, type = 'info') {
    /**
     * Show a toast-like notification
     * @param {string} message - Notification message
     * @param {string} type - 'success', 'error', 'warning', 'info'
     */
    const notificationDiv = document.createElement('div');
    const bgColor = {
        'success': 'bg-green-500',
        'error': 'bg-red-500',
        'warning': 'bg-yellow-500',
        'info': 'bg-blue-500'
    }[type] || 'bg-blue-500';
    
    notificationDiv.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-pulse`;
    notificationDiv.textContent = message;
    document.body.appendChild(notificationDiv);
    
    setTimeout(() => {
        notificationDiv.remove();
    }, 4000);
}

// Initialize all features on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 UI Enhancements loaded successfully');
});
