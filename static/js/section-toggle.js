/**
 * Toggle functionality for collapsible sections
 */

function initializeToggleSections() {
    const headers = document.querySelectorAll('.section-header');
    
    headers.forEach(header => {
        header.addEventListener('click', function(e) {
            e.preventDefault();
            
            const sectionId = this.getAttribute('data-section');
            const content = document.getElementById(sectionId);
            const toggleIcon = this.querySelector('.toggle-btn');
            const isCollapsed = content.classList.contains('collapsed');
            
            if (isCollapsed) {
                // Expand section
                content.classList.remove('collapsed');
                toggleIcon.classList.remove('collapsed');
                toggleIcon.textContent = '▼';
                this.setAttribute('aria-expanded', 'true');
                
                // Save state to localStorage
                localStorage.setItem(`section-${sectionId}`, 'expanded');
            } else {
                // Collapse section
                content.classList.add('collapsed');
                toggleIcon.classList.add('collapsed');
                toggleIcon.textContent = '▶';
                this.setAttribute('aria-expanded', 'false');
                
                // Save state to localStorage
                localStorage.setItem(`section-${sectionId}`, 'collapsed');
            }
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
        
        if (savedState === 'expanded') {
            content.classList.remove('collapsed');
            toggleIcon.classList.remove('collapsed');
            toggleIcon.textContent = '▼';
            header.setAttribute('aria-expanded', 'true');
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
