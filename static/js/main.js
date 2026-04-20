// Main JavaScript for Finance Manager

document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    initializePopovers();
    setupNumberFormatting();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize Bootstrap popovers
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Format numbers as currency
function formatCurrency(value) {
    return '$' + parseFloat(value).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Setup number formatting for currency inputs
function setupNumberFormatting() {
    const currencyInputs = document.querySelectorAll('input[type="number"]');
    currencyInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });
}

// Show loading spinner
function showLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'spinner-border text-primary';
    spinner.role = 'status';
    document.body.appendChild(spinner);
}

// Hide loading spinner
function hideLoadingSpinner() {
    const spinner = document.querySelector('.spinner-border');
    if (spinner) {
        spinner.remove();
    }
}

// Confirm delete action
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this?');
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard!');
    });
}

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Get query parameter from URL
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

// Set active nav item
function setActiveNavItem() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.href === window.location.href) {
            link.classList.add('active');
        }
    });
}

setActiveNavItem();

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Validate form
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    }
}

// Export data to CSV
function exportToCSV(filename, data) {
    let csvContent = "data:text/csv;charset=utf-8,";

    if (data && data.length > 0) {
        const headers = Object.keys(data[0]);
        csvContent += headers.join(",") + "\r\n";

        data.forEach(row => {
            const values = headers.map(header => row[header]);
            csvContent += values.join(",") + "\r\n";
        });
    }

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", filename || 'data.csv');
    document.body.appendChild(link);

    link.click();
    document.body.removeChild(link);
}

// Calculate totals
function calculateTotal(selector) {
    let total = 0;
    document.querySelectorAll(selector).forEach(element => {
        total += parseFloat(element.textContent.replace(/[^0-9.-]+/g, '')) || 0;
    });
    return total;
}

// Highlight budget warnings
function highlightBudgetWarnings() {
    document.querySelectorAll('[data-budget-percentage]').forEach(element => {
        const percentage = parseInt(element.dataset.budgetPercentage);
        if (percentage >= 100) {
            element.classList.add('table-danger');
        } else if (percentage >= 75) {
            element.classList.add('table-warning');
        }
    });
}

highlightBudgetWarnings();

// Real-time search
function setupRealtimeSearch(inputSelector, resultSelector) {
    const input = document.querySelector(inputSelector);
    if (!input) return;

    input.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        document.querySelectorAll(resultSelector).forEach(element => {
            const text = element.textContent.toLowerCase();
            element.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

// Toggle dark mode
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Load dark mode preference
function loadDarkModePreference() {
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
}

loadDarkModePreference();