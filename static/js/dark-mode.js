/**
 * Dark Mode Toggle with LocalStorage and System Preference Detection
 */

(function() {
    const STORAGE_KEY = 'astro-dark-mode';
    
    /**
     * Get the user's dark mode preference
     * Priority: localStorage > system preference > default (light)
     */
    function getDarkModePreference() {
        // Check localStorage first
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored !== null) {
            return stored === 'true';
        }
        
        // Fall back to system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return true;
        }
        
        // Default to light mode
        return false;
    }
    
    /**
     * Apply dark mode to the document
     */
    function applyDarkMode(isDark) {
        if (isDark) {
            document.documentElement.classList.add('dark-mode');
        } else {
            document.documentElement.classList.remove('dark-mode');
        }
        
        // Update toggle button if it exists
        updateToggleButton(isDark);
    }
    
    /**
     * Update the toggle button appearance
     */
    function updateToggleButton(isDark) {
        const toggleBtn = document.getElementById('darkModeToggle');
        if (toggleBtn) {
            toggleBtn.textContent = isDark ? '☀️' : '🌙';
            toggleBtn.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
            toggleBtn.title = isDark ? 'Switch to light mode' : 'Switch to dark mode';
        }
    }
    
    /**
     * Toggle dark mode and save preference
     */
    function toggleDarkMode() {
        const isDark = !document.documentElement.classList.contains('dark-mode');
        applyDarkMode(isDark);
        localStorage.setItem(STORAGE_KEY, isDark);
    }
    
    /**
     * Initialize dark mode on page load
     */
    function init() {
        // Apply dark mode immediately to avoid flash
        const isDark = getDarkModePreference();
        applyDarkMode(isDark);
        
        // Set up toggle button when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', setupToggleButton);
        } else {
            setupToggleButton();
        }
        
        // Listen for system preference changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                // Only apply system preference if user hasn't set a preference
                if (localStorage.getItem(STORAGE_KEY) === null) {
                    applyDarkMode(e.matches);
                }
            });
        }
    }
    
    /**
     * Set up the toggle button event listener
     */
    function setupToggleButton() {
        const toggleBtn = document.getElementById('darkModeToggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', toggleDarkMode);
            updateToggleButton(document.documentElement.classList.contains('dark-mode'));
        }
    }
    
    // Initialize immediately
    init();
})();
