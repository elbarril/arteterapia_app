/**
 * Main Application JavaScript
 * Application initializer that loads appropriate modules based on page context
 */

// Application initialization
document.addEventListener('DOMContentLoaded', function () {
    // Initialize based on page context
    initializePage();
});

/**
 * Initialize the appropriate manager based on current page
 */
function initializePage() {
    const path = window.location.pathname;

    // Workshop detail page
    if (path.match(/^\/workshop\/\d+$/)) {
        initializeWorkshopDetail();
    }

    // Observation page
    if (path.match(/^\/session\/\d+\/observe\/\d+$/)) {
        initializeObservation();
    }
}

/**
 * Initialize workshop detail page
 */
function initializeWorkshopDetail() {
    // Get workshop ID from global variable (set in template)
    if (typeof workshopId !== 'undefined') {
        new WorkshopDetailManager(workshopId);
    }
}

/**
 * Initialize observation page
 */
function initializeObservation() {
    // Get observation config from global variables (set in template)
    if (typeof observationConfig !== 'undefined') {
        new ObservationFlow(observationConfig);
    }
}
