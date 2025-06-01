/* Server Management - Custom JavaScript for UI/UX Enhancement */

// Cache for DOM elements to avoid repeated queries
const DOM = {};

document.addEventListener('DOMContentLoaded', function() {
    // Cache frequently accessed DOM elements
    cacheCommonElements();
    
    // Initialize all UI components
    initializeUI();
});

// Cache common DOM elements for better performance
function cacheCommonElements() {
    // Tables and search elements
    DOM.tables = document.querySelectorAll('.table-hover');
    DOM.serverTable = document.getElementById('serverTable');
    DOM.serverSearch = document.getElementById('serverSearch');
    
    // Form elements
    DOM.forms = document.querySelectorAll('form');
    
    // Navigation elements
    DOM.navbarToggler = document.querySelector('.navbar-toggler');
    DOM.navbarCollapse = document.querySelector('.navbar-collapse');
    
    // Accordion elements
    DOM.accordionButtons = document.querySelectorAll('.accordion-button');
    DOM.accordionElements = document.querySelectorAll('.accordion-collapse');
    
    // Main content for accessibility
    DOM.mainContent = document.querySelector('main');
}

// Initialize all UI components
function initializeUI() {
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
}

// ===== TOOLTIPS =====
function initTooltips() {
    // Use a single selector to get all tooltip elements
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"], .btn-sm:not([data-bs-toggle])');
    
    tooltipElements.forEach(function(element) {
        // Only set attributes for buttons without tooltips
        if (!element.hasAttribute('data-bs-toggle')) {
            element.setAttribute('data-bs-toggle', 'tooltip');
            if (!element.hasAttribute('title') && element.textContent.trim()) {
                element.setAttribute('title', element.textContent.trim());
            }
        }
        
        // Initialize tooltip
        new bootstrap.Tooltip(element);
    });
}

// ===== FORM VALIDATION =====
function initFormValidation() {
    if (!DOM.forms || !DOM.forms.length) return;
    
    DOM.forms.forEach(function(form) {
        // Add novalidate attribute to enable custom validation
        form.setAttribute('novalidate', '');
        
        // Add event listener for form submission
        form.addEventListener('submit', handleFormSubmit);
        
        // Add real-time validation for form controls
        const formControls = form.querySelectorAll('.form-control');
        formControls.forEach(control => {
            control.addEventListener('input', () => validateControl(control, form));
        });
    });
}

// Handle form submission and validation
function handleFormSubmit(event) {
    const form = event.currentTarget;
    
    if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    // Validate all form controls
    const formControls = form.querySelectorAll('.form-control');
    formControls.forEach(control => validateControl(control, form));
    
    form.classList.add('was-validated');
}

// Validate a single form control
function validateControl(control, form) {
    // Only apply validation if form has been submitted
    if (!form.classList.contains('was-validated')) return;
    
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
}

// ===== INTERACTIVE TABLES =====
function initTables() {
    if (!DOM.tables || !DOM.tables.length) return;
    
    // Use event delegation for table rows
    DOM.tables.forEach(function(table) {
        const tbody = table.querySelector('tbody');
        if (!tbody) return;
        
        // Add a single event listener to the tbody instead of each row
        tbody.addEventListener('click', handleTableRowClick);
        
        // Set cursor style on rows that should be clickable
        setupClickableRows(tbody);
    });
    
    // Initialize server search functionality if present
    initServerSearch();
}

// Set up clickable rows with appropriate styles
function setupClickableRows(tbody) {
    const rows = tbody.querySelectorAll('tr');
    
    rows.forEach(function(row) {
        // Skip rows that already have click handlers (like VM rows)
        if (row.classList.contains('vm-row')) return;
        
        // Check if row has detail links
        const hasDetailLink = row.querySelector('a.btn-info, a.btn-outline-info');
        const isServerRow = row.classList.contains('server-row');
        
        if (hasDetailLink || isServerRow) {
            row.style.cursor = 'pointer';
            if (hasDetailLink) {
                row.setAttribute('title', 'Click for details');
            }
        }
    });
}

// Handle click events on table rows using event delegation
function handleTableRowClick(event) {
    const target = event.target;
    const row = target.closest('tr');
    
    // Don't proceed if no row was clicked or if clicking on a button/link
    if (!row || target.tagName === 'A' || target.tagName === 'BUTTON' || 
        target.closest('a') || target.closest('button') || 
        target.closest('[onclick="event.stopPropagation();"]')) {
        return;
    }
    
    // Handle server rows
    if (row.classList.contains('server-row')) {
        const detailLink = row.querySelector('a.btn-info');
        if (detailLink) {
            addClickFeedbackAndNavigate(row, detailLink.getAttribute('href'));
        }
        return;
    }
    
    // Handle other clickable rows
    const detailLink = row.querySelector('a.btn-info, a.btn-outline-info');
    if (detailLink) {
        addClickFeedbackAndNavigate(row, detailLink.getAttribute('href'));
    }
}

// Add visual feedback and navigate to the specified URL
function addClickFeedbackAndNavigate(element, url) {
    if (!url) return;
    
    // Add visual feedback
    element.style.backgroundColor = 'rgba(0, 123, 255, 0.2)';
    element.style.transition = 'background-color 0.2s ease';
    
    // Navigate after a short delay for visual feedback
    setTimeout(() => {
        window.location.href = url;
    }, 150);
}

// Initialize server search functionality
function initServerSearch() {
    if (!DOM.serverSearch || !DOM.serverTable) return;
    
    const rows = DOM.serverTable.querySelectorAll('tbody tr');
    if (!rows.length) return;
    
    // Debounce the search to improve performance
    let searchTimeout;
    
    DOM.serverSearch.addEventListener('keyup', function() {
        clearTimeout(searchTimeout);
        
        searchTimeout = setTimeout(() => {
            const searchTerm = DOM.serverSearch.value.toLowerCase();
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        }, 200); // 200ms debounce delay
    });
}

// ===== ACCORDION FUNCTIONALITY =====
function initAccordions() {
    if (!DOM.accordionButtons || !DOM.accordionButtons.length) return;
    
    // Initial setup
    DOM.accordionButtons.forEach(button => {
        updateCollapseIndicator(button);
    });
    
    // Add event listeners to all accordion elements
    if (DOM.accordionElements && DOM.accordionElements.length) {
        DOM.accordionElements.forEach(element => {
            element.addEventListener('show.bs.collapse', handleAccordionShow);
            element.addEventListener('hide.bs.collapse', handleAccordionHide);
        });
    }
}

// Handle accordion show event
function handleAccordionShow(event) {
    const button = document.querySelector(`[data-bs-target="#${event.target.id}"]`);
    updateCollapseIndicator(button, true);
}

// Handle accordion hide event
function handleAccordionHide(event) {
    const button = document.querySelector(`[data-bs-target="#${event.target.id}"]`);
    updateCollapseIndicator(button, false);
}

// Update collapse indicator text and icon
function updateCollapseIndicator(button, isExpanded) {
    const indicator = button?.querySelector('.collapse-indicator');
    if (!indicator) return;
    
    // Use the button's aria-expanded attribute if isExpanded is not provided
    if (isExpanded === undefined) {
        isExpanded = button.getAttribute('aria-expanded') === 'true';
    }
    
    indicator.innerHTML = isExpanded ? 
        '<i class="fas fa-chevron-up"></i> Click to collapse' : 
        '<i class="fas fa-chevron-down"></i> Click to expand';
    
    button.classList.toggle('active-accordion', isExpanded);
}

// ===== RESPONSIVE NAVIGATION =====
function initResponsiveNav() {
    if (!DOM.navbarToggler || !DOM.navbarCollapse) return;
    
    // Add animation classes
    DOM.navbarCollapse.classList.add('collapse-transition');
    
    // Add event listener for navbar toggle
    DOM.navbarToggler.addEventListener('click', toggleNavbar);
}

// Toggle navbar with animation
function toggleNavbar() {
    const isExpanded = DOM.navbarCollapse.classList.contains('show');
    
    if (isExpanded) {
        // Collapse navbar
        DOM.navbarCollapse.style.height = DOM.navbarCollapse.scrollHeight + 'px';
        requestAnimationFrame(() => {
            DOM.navbarCollapse.style.height = '0';
            setTimeout(() => {
                DOM.navbarCollapse.classList.remove('show');
                DOM.navbarCollapse.style.height = '';
            }, 300);
        });
    } else {
        // Expand navbar
        DOM.navbarCollapse.classList.add('show');
        DOM.navbarCollapse.style.height = '0';
        requestAnimationFrame(() => {
            DOM.navbarCollapse.style.height = DOM.navbarCollapse.scrollHeight + 'px';
            setTimeout(() => {
                DOM.navbarCollapse.style.height = '';
            }, 300);
        });
    }
}

// ===== STATUS INDICATORS =====
function updateStatusIndicators() {
    // Replace text status indicators with visual ones
    const statusBadges = document.querySelectorAll('.badge');
    if (!statusBadges.length) return;
    
    const statusMap = {
        'online': 'status-online',
        'running': 'status-online',
        'offline': 'status-offline',
        'stopped': 'status-offline'
    };
    
    statusBadges.forEach(function(badge) {
        const text = badge.textContent.trim().toLowerCase();
        const statusClass = statusMap[text];
        
        if (statusClass) {
            // Create indicator only if it doesn't already exist
            if (!badge.querySelector('.status-indicator')) {
                const indicator = document.createElement('span');
                indicator.classList.add('status-indicator', statusClass);
                badge.prepend(indicator);
            }
        }
    });
}

// ===== ACCESSIBILITY ENHANCEMENTS =====
function enhanceAccessibility() {
    addSkipLink();
    ensureKeyboardAccessibility();
    addAriaLabelsToButtons();
}

// Add skip to content link
function addSkipLink() {
    if (!DOM.mainContent || document.querySelector('.skip-link')) return;
    
    const skipLink = document.createElement('a');
    skipLink.classList.add('skip-link');
    skipLink.href = '#content';
    skipLink.textContent = 'Skip to content';
    document.body.prepend(skipLink);
    
    // Add ID to main content
    DOM.mainContent.id = 'content';
}

// Ensure all interactive elements are keyboard accessible
function ensureKeyboardAccessibility() {
    const interactiveElements = document.querySelectorAll('a, button, input, select, textarea, [tabindex]');
    
    interactiveElements.forEach(function(element) {
        if (element.getAttribute('tabindex') === '-1' && !element.hasAttribute('aria-hidden')) {
            element.setAttribute('tabindex', '0');
        }
    });
}

// Add aria labels to buttons without text
function addAriaLabelsToButtons() {
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