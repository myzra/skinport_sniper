/**
 * Script Controller JavaScript
 * Handles all client-side functionality for the filter form and script operations
 */

// Set up tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap 5 is used
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Additional UI enhancements
    enhanceFormInputs();
    setupCardAnimations();
});

/**
 * Add interactive elements to form inputs
 */
function enhanceFormInputs() {
    // Add clear buttons to input fields
    const textInputs = document.querySelectorAll('input[type="text"], input[type="number"]');
    textInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.classList.add('active-input');
        });
        
        input.addEventListener('blur', function() {
            this.classList.remove('active-input');
        });
    });
    
    // Enhance select dropdowns
    const selects = document.querySelectorAll('select');
    selects.forEach(select => {
        select.addEventListener('change', function() {
            if (this.value) {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
    });
}

/**
 * Add subtle animations to cards
 */
function setupCardAnimations() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 15px rgba(0, 0, 0, 0.2)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        });
    });
}

/**
 * Validate form inputs before submission
 * @param {Object} formData - The form data to validate
 * @return {boolean} - Is the data valid
 */
function validateFormData(formData) {
    // Validate min/max price
    if (formData.min_price && formData.max_price) {
        if (parseFloat(formData.min_price) > parseFloat(formData.max_price)) {
            showNotification('Min price cannot be greater than max price', 'warning');
            return false;
        }
    }
    
    // Validate min/max wear
    if (formData.min_wear && formData.max_wear) {
        if (parseFloat(formData.min_wear) > parseFloat(formData.max_wear)) {
            showNotification('Min wear cannot be greater than max wear', 'warning');
            return false;
        }
    }
    
    // Check wear values are between 0 and 1
    if (formData.min_wear && (parseFloat(formData.min_wear) < 0 || parseFloat(formData.min_wear) > 1)) {
        showNotification('Min wear must be between 0 and 1', 'warning');
        return false;
    }
    
    if (formData.max_wear && (parseFloat(formData.max_wear) < 0 || parseFloat(formData.max_wear) > 1)) {
        showNotification('Max wear must be between 0 and 1', 'warning');
        return false;
    }
    
    return true;
}

/**
 * Display a notification to the user
 * @param {string} message - The message to display
 * @param {string} type - The notification type (success, warning, danger, info)
 */
function showNotification(message, type) {
    // Create notification element if not exists
    if (!document.querySelector('.notification-container')) {
        const container = document.createElement('div');
        container.className = 'notification-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.querySelector('.notification-container').appendChild(notification);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 150);
    }, 5000);
}

/**
 * Format filter data for display
 * @param {Object} filter - The filter data to format
 * @return {string} - Formatted HTML string
 */
function formatFilterData(filter) {
    let html = '<div class="filter-details">';
    
    if (filter.names) {
        html += `<p><strong>Names:</strong> ${filter.names}</p>`;
    }
    
    if (filter.min_price || filter.max_price) {
        html += `<p><strong>Price:</strong> ${filter.min_price || '0'} - ${filter.max_price || 'No limit'}</p>`;
    }
    
    if (filter.patterns) {
        html += `<p><strong>Patterns:</strong> ${filter.patterns}</p>`;
    }
    
    if (filter.min_wear || filter.max_wear) {
        html += `<p><strong>Wear:</strong> ${filter.min_wear || '0'} - ${filter.max_wear || '1'}</p>`;
    }
    
    if (filter.exterior) {
        html += `<p><strong>Exterior:</strong> ${filter.exterior}</p>`;
    }
    
    html += '</div>';
    return html;
}

/**
 * Update script status UI
 * @param {boolean} isRunning - Is the script currently running
 */
function updateScriptStatus(isRunning) {
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    const stopButton = document.getElementById('stopButton');
    
    if (isRunning) {
        statusIndicator.classList.add('active');
        statusText.textContent = 'Script is running';
        stopButton.disabled = false;
    } else {
        statusIndicator.classList.remove('active');
        statusText.textContent = 'Script is stopped';
        stopButton.disabled = true;
    }
}