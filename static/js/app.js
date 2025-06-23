// Global JavaScript utilities for CISSP Quiz App

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (document.body.contains(notification)) {
            document.body.removeChild(notification);
        }
    }, 3000);
}

// Loading state management
function setLoading(element, loading = true) {
    if (loading) {
        element.disabled = true;
        element.dataset.originalText = element.textContent;
        element.innerHTML = '<div class="loading-spinner"></div> Loading...';
    } else {
        element.disabled = false;
        element.textContent = element.dataset.originalText || element.textContent;
    }
}

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    // Handle Escape key to close modals
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal[style*="flex"]');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
    }
});

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    console.log('CISSP Quiz Web App initialized');
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}); 