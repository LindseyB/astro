/**
 * Toggle functionality for collapsible sections
 */

/**
 * Update the UI state of a section (expanded or collapsed)
 * @param {HTMLElement} content - The content element to toggle
 * @param {HTMLElement} toggleIcon - The icon element to update
 * @param {HTMLElement} header - The header element to update
 * @param {boolean} expanded - Whether the section should be expanded
 */
function updateSectionState(content, toggleIcon, header, expanded) {
    if (expanded) {
        content.classList.remove('collapsed');
        toggleIcon.classList.remove('collapsed');
        toggleIcon.textContent = '▼';
        header.setAttribute('aria-expanded', 'true');
    } else {
        content.classList.add('collapsed');
        toggleIcon.classList.add('collapsed');
        toggleIcon.textContent = '▶';
        header.setAttribute('aria-expanded', 'false');
    }
}

function initializeToggleSections() {
    const headers = document.querySelectorAll('.section-header');
    
    headers.forEach(header => {
        header.addEventListener('click', function(e) {
            e.preventDefault();
            
            const sectionId = this.getAttribute('data-section');
            const content = document.getElementById(sectionId);
            const toggleIcon = this.querySelector('.toggle-btn');
            
            // Check if required elements exist before proceeding
            if (!content || !toggleIcon) {
                console.warn(`Missing elements for section: ${sectionId}`);
                return;
            }
            
            const isCollapsed = content.classList.contains('collapsed');
            const shouldExpand = isCollapsed;
            
            // Update UI state
            updateSectionState(content, toggleIcon, this, shouldExpand);
            
            // Save state to localStorage
            localStorage.setItem(`section-${sectionId}`, shouldExpand ? 'expanded' : 'collapsed');
        });
    });
    
    // Restore saved states from localStorage
    restoreSectionStates();
}

function restoreSectionStates() {
    const headers = document.querySelectorAll('.section-header');
    
    headers.forEach(header => {
        const sectionId = header.getAttribute('data-section');
        const savedState = localStorage.getItem(`section-${sectionId}`);
        const content = document.getElementById(sectionId);
        const toggleIcon = header.querySelector('.toggle-btn');
        
        if (savedState === 'expanded' && content && toggleIcon) {
            updateSectionState(content, toggleIcon, header, true);
        }
        // Default is already collapsed, no need to do anything
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeToggleSections);
} else {
    initializeToggleSections();
}
