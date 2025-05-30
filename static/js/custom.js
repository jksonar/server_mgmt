/* Server Management - Custom JavaScript for UI/UX Enhancement */

document.addEventListener('DOMContentLoaded', function() {
    // ===== DYNAMIC ELEMENTS =====
    
    // Initialize all tooltips
    initTooltips();
    
    // Add form validation
    initFormValidation();
    
    // Initialize interactive tables
    initTables();
    
    // Initialize accordion functionality
    initAccordions();
    
    // Add responsive navigation enhancements
    initResponsiveNav();
    
    // Initialize status indicators
    updateStatusIndicators();
    
    // Add accessibility enhancements
    enhanceAccessibility();
});

// ===== TOOLTIPS =====
function initTooltips() {
    // Add tooltips to all elements with data-toggle="tooltip"
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        tooltipTriggerList.forEach(function(tooltipTriggerEl) {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Add tooltips to action buttons that don't have text labels
    const actionButtons = document.querySelectorAll('.btn-sm');
    actionButtons.forEach(function(button) {
        if (!button.hasAttribute('data-bs-toggle')) {
            button.setAttribute('data-bs-toggle', 'tooltip');
            if (!button.hasAttribute('title') && button.textContent.trim()) {
                button.setAttribute('title', button.textContent.trim());
            }
            new bootstrap.Tooltip(button);
        }
    });
}

// ===== FORM VALIDATION =====
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        // Add novalidate attribute to enable custom validation
        form.setAttribute('novalidate', '');
        
        // Add event listener for form submission
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            // Add validation classes to form elements
            const formControls = form.querySelectorAll('.form-control');
            formControls.forEach(function(control) {
                // Add validation feedback
                if (control.checkValidity()) {
                    control.classList.add('is-valid');
                    control.classList.remove('is-invalid');
                } else {
                    control.classList.add('is-invalid');
                    control.classList.remove('is-valid');
                    
                    // Show validation feedback
                    let feedbackElement = control.nextElementSibling;
                    if (!feedbackElement || !feedbackElement.classList.contains('invalid-feedback')) {
                        feedbackElement = document.createElement('div');
                        feedbackElement.classList.add('invalid-feedback');
                        control.parentNode.insertBefore(feedbackElement, control.nextSibling);
                    }
                    feedbackElement.textContent = control.validationMessage;
                }
            });
            
            form.classList.add('was-validated');
        }, false);
        
        // Real-time validation feedback
        const formControls = form.querySelectorAll('.form-control');
        formControls.forEach(function(control) {
            control.addEventListener('input', function() {
                if (form.classList.contains('was-validated')) {
                    if (control.checkValidity()) {
                        control.classList.add('is-valid');
                        control.classList.remove('is-invalid');
                    } else {
                        control.classList.add('is-invalid');
                        control.classList.remove('is-valid');
                    }
                }
            });
        });
    });
}

// ===== INTERACTIVE TABLES =====
function initTables() {
    const tables = document.querySelectorAll('.table-hover');
    
    tables.forEach(function(table) {
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(function(row) {
            // Skip rows that already have click handlers (like VM rows)
            if (row.classList.contains('vm-row')) return;
            
            // Make rows with detail links clickable
            const detailLink = row.querySelector('a.btn-info, a.btn-outline-info');
            if (detailLink) {
                row.style.cursor = 'pointer';
                row.setAttribute('title', 'Click for details');
                
                row.addEventListener('click', function(event) {
                    // Don't trigger if clicking on a button or link
                    if (event.target.tagName === 'A' || event.target.tagName === 'BUTTON' ||
                        event.target.closest('a') || event.target.closest('button')) {
                        return;
                    }
                    
                    // Add visual feedback
                    this.style.backgroundColor = 'rgba(0, 123, 255, 0.2)';
                    this.style.transition = 'background-color 0.2s ease';
                    
                    // Navigate to detail page
                    setTimeout(() => {
                        window.location.href = detailLink.getAttribute('href');
                    }, 150);
                });
            }
        });
    });
}

// ===== ACCORDION FUNCTIONALITY =====
function initAccordions() {
    const accordionButtons = document.querySelectorAll('.accordion-button');
    
    // Initial setup
    accordionButtons.forEach(button => {
        updateCollapseIndicator(button);
    });
    
    // Add event listeners to all accordion buttons
    const accordionElements = document.querySelectorAll('.accordion-collapse');
    accordionElements.forEach(element => {
        element.addEventListener('show.bs.collapse', function() {
            const button = document.querySelector(`[data-bs-target="#${this.id}"]`);
            updateCollapseIndicator(button, true);
        });
        
        element.addEventListener('hide.bs.collapse', function() {
            const button = document.querySelector(`[data-bs-target="#${this.id}"]`);
            updateCollapseIndicator(button, false);
        });
    });
}

// Update collapse indicator text and icon
function updateCollapseIndicator(button, isExpanded) {
    const indicator = button.querySelector('.collapse-indicator');
    if (!indicator) return;
    
    // Use the button's aria-expanded attribute if isExpanded is not provided
    if (isExpanded === undefined) {
        isExpanded = button.getAttribute('aria-expanded') === 'true';
    }
    
    if (isExpanded) {
        indicator.innerHTML = '<i class="fas fa-chevron-up"></i> Click to collapse';
        button.classList.add('active-accordion');
    } else {
        indicator.innerHTML = '<i class="fas fa-chevron-down"></i> Click to expand';
        button.classList.remove('active-accordion');
    }
}

// ===== RESPONSIVE NAVIGATION =====
function initResponsiveNav() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Add animation classes
        navbarCollapse.classList.add('collapse-transition');
        
        // Add event listeners for navbar toggle
        navbarToggler.addEventListener('click', function() {
            if (navbarCollapse.classList.contains('show')) {
                navbarCollapse.style.height = navbarCollapse.scrollHeight + 'px';
                setTimeout(() => {
                    navbarCollapse.style.height = '0';
                }, 10);
                setTimeout(() => {
                    navbarCollapse.classList.remove('show');
                    navbarCollapse.style.height = '';
                }, 300);
            } else {
                navbarCollapse.classList.add('show');
                navbarCollapse.style.height = '0';
                setTimeout(() => {
                    navbarCollapse.style.height = navbarCollapse.scrollHeight + 'px';
                }, 10);
                setTimeout(() => {
                    navbarCollapse.style.height = '';
                }, 300);
            }
        });
    }
}

// ===== STATUS INDICATORS =====
function updateStatusIndicators() {
    // Replace text status indicators with visual ones
    const statusBadges = document.querySelectorAll('.badge');
    
    statusBadges.forEach(function(badge) {
        const text = badge.textContent.trim().toLowerCase();
        
        if (text === 'online' || text === 'running') {
            // Add a visual indicator before the text
            const indicator = document.createElement('span');
            indicator.classList.add('status-indicator', 'status-online');
            badge.prepend(indicator);
        } else if (text === 'offline' || text === 'stopped') {
            // Add a visual indicator before the text
            const indicator = document.createElement('span');
            indicator.classList.add('status-indicator', 'status-offline');
            badge.prepend(indicator);
        }
    });
}

// ===== ACCESSIBILITY ENHANCEMENTS =====
function enhanceAccessibility() {
    // Add skip to content link
    const mainContent = document.querySelector('main');
    if (mainContent && !document.querySelector('.skip-link')) {
        const skipLink = document.createElement('a');
        skipLink.classList.add('skip-link');
        skipLink.href = '#content';
        skipLink.textContent = 'Skip to content';
        document.body.prepend(skipLink);
        
        // Add ID to main content
        mainContent.id = 'content';
    }
    
    // Ensure all interactive elements are keyboard accessible
    const interactiveElements = document.querySelectorAll('a, button, input, select, textarea, [tabindex]');
    interactiveElements.forEach(function(element) {
        if (element.getAttribute('tabindex') === '-1' && !element.hasAttribute('aria-hidden')) {
            element.setAttribute('tabindex', '0');
        }
    });
    
    // Add aria labels to buttons without text
    const buttons = document.querySelectorAll('button, .btn');
    buttons.forEach(function(button) {
        if (!button.textContent.trim() && !button.hasAttribute('aria-label')) {
            const icon = button.querySelector('i, .fa, .fas, .far, .fab');
            if (icon && icon.classList) {
                // Try to generate a label from icon classes
                const iconClasses = Array.from(icon.classList);
                const iconType = iconClasses.find(cls => cls.startsWith('fa-'));
                if (iconType) {
                    const label = iconType.replace('fa-', '').replace(/-/g, ' ');
                    button.setAttribute('aria-label', label);
                }
            }
        }
    });
}