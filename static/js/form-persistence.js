// Form Persistence using localStorage
// Saves and restores form data to provide a better user experience

class FormPersistence {
    constructor() {
        this.storageKey = 'astro_form_data';
        this.formFields = [
            'birth_date',
            'birth_time', 
            'timezone_offset',
            'latitude',
            'longitude',
            'music_genre',
            'other_genre'
        ];
        
        // Initialize on page load
        this.init();
    }
    
    init() {
        // Load saved data when page loads
        this.loadFormData();
        
        // Save data whenever form fields change
        this.attachEventListeners();
        
        // Save data before form submission (as backup)
        this.attachSubmitListener();
    }
    
    // Save form data to localStorage
    saveFormData() {
        const formData = {};
        
        this.formFields.forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                if (element.type === 'checkbox') {
                    formData[fieldId] = element.checked;
                } else {
                    formData[fieldId] = element.value;
                }
            }
        });
        
        // Store with timestamp for potential cleanup
        const dataWithTimestamp = {
            data: formData,
            timestamp: Date.now()
        };
        
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(dataWithTimestamp));
        } catch (e) {
            console.warn('Failed to save form data to localStorage:', e);
        }
    }
    
    // Load form data from localStorage
    loadFormData() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            
            if (!stored) {
                // First time user - set some reasonable defaults
                this.setDefaultValues();
                return;
            }
            
            const parsed = JSON.parse(stored);
            const formData = parsed.data || parsed; // Handle both new and old format
            
            // Check if data is older than 30 days and clean up
            if (parsed.timestamp && (Date.now() - parsed.timestamp > 30 * 24 * 60 * 60 * 1000)) {
                this.clearFormData();
                this.setDefaultValues();
                return;
            }
            
            // Restore form values
            this.formFields.forEach(fieldId => {
                const element = document.getElementById(fieldId);
                if (element && formData.hasOwnProperty(fieldId)) {
                    if (element.type === 'checkbox') {
                        element.checked = formData[fieldId];
                    } else {
                        element.value = formData[fieldId];
                    }
                }
            });
            
            // Special handling for music genre dropdown change
            const musicGenre = document.getElementById('music_genre');
            if (musicGenre && formData.music_genre === 'other') {
                // Trigger the dropdown change to show the "other" input field
                if (typeof toggleOtherGenre === 'function') {
                    toggleOtherGenre();
                }
            }
            
            // Handle location restoration if we have coordinates
            if (formData.latitude && formData.longitude) {
                // Wait for map to be initialized, then update it
                setTimeout(() => {
                    this.restoreLocationOnMap(formData.latitude, formData.longitude);
                }, 1000);
            }
            
            // Show restoration indicator
            this.showRestorationIndicator();
            
        } catch (e) {
            console.warn('Failed to load form data from localStorage:', e);
            this.clearFormData(); // Clear corrupted data
            this.setDefaultValues();
        }
    }
    
    // Show indicator that form data was restored
    showRestorationIndicator() {
        const indicator = document.getElementById('formDataStatus');
        if (indicator) {
            indicator.style.display = 'block';
            
            // Hide after 5 seconds
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 5000);
        }
    }
    
    // Set reasonable default values for first-time users
    setDefaultValues() {
        // Set default birth date to a common date
        const birthDate = document.getElementById('birth_date');
        if (birthDate && !birthDate.value) {
            birthDate.value = '1990-01-01';
        }
        
        // Set default birth time to 9:00 AM
        const birthTime = document.getElementById('birth_time');
        if (birthTime && !birthTime.value) {
            birthTime.value = '09:00';
        }
        
        // Set default timezone to EST/EDT (common for US East Coast)
        const timezone = document.getElementById('timezone_offset');
        if (timezone && !timezone.value) {
            timezone.value = '-05:00';
        }
        
        // Set default location to New York City (if not already set)
        const latitude = document.getElementById('latitude');
        const longitude = document.getElementById('longitude');
        if (latitude && longitude && !latitude.value && !longitude.value) {
            latitude.value = '40n42';
            longitude.value = '74w00';
        }
        
        // Music genre defaults to "any"
        const musicGenre = document.getElementById('music_genre');
        if (musicGenre && !musicGenre.value) {
            musicGenre.value = 'any';
        }
    }
    
    // Restore location on map from saved coordinates
    restoreLocationOnMap(astroLat, astroLng) {
        // Wait for map to be initialized
        const waitForMap = () => {
            if (typeof window.map === 'undefined' || !window.map) {
                setTimeout(waitForMap, 100);
                return;
            }
            
            try {
                // Convert astrology format back to decimal
                const decimalCoords = this.astroToDecimal(astroLat, astroLng);
                if (decimalCoords) {
                    const { lat, lng } = decimalCoords;
                    
                    // Update map view and marker
                    map.setView([lat, lng], 10);
                    
                    // Add/update marker
                    if (window.marker) {
                        map.removeLayer(window.marker);
                    }
                    window.marker = L.marker([lat, lng]).addTo(map);
                    
                    // Update location display
                    if (typeof updateLocationDisplay === 'function') {
                        updateLocationDisplay(lat, lng, astroLat, astroLng);
                    }
                }
            } catch (e) {
                console.warn('Failed to restore location on map:', e);
            }
        };
        
        waitForMap();
    }
    
    // Convert astrology format coordinates back to decimal
    astroToDecimal(astroLat, astroLng) {
        try {
            // Parse latitude (e.g., "40n42" or "40s42")
            const latMatch = astroLat.match(/(\d+)([ns])(\d+)/i);
            if (!latMatch) return null;
            
            const latDegrees = parseInt(latMatch[1]);
            const latDirection = latMatch[2].toLowerCase();
            const latMinutes = parseInt(latMatch[3]);
            let lat = latDegrees + (latMinutes / 60);
            if (latDirection === 's') lat = -lat;
            
            // Parse longitude (e.g., "74w00" or "74e00")
            const lngMatch = astroLng.match(/(\d+)([we])(\d+)/i);
            if (!lngMatch) return null;
            
            const lngDegrees = parseInt(lngMatch[1]);
            const lngDirection = lngMatch[2].toLowerCase();
            const lngMinutes = parseInt(lngMatch[3]);
            let lng = lngDegrees + (lngMinutes / 60);
            if (lngDirection === 'w') lng = -lng;
            
            return { lat, lng };
        } catch (e) {
            console.warn('Failed to convert astrology coordinates:', e);
            return null;
        }
    }
    
    // Attach event listeners to form fields
    attachEventListeners() {
        this.formFields.forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                // Use 'input' event for most fields, 'change' for dropdowns
                const eventType = element.type === 'select-one' ? 'change' : 'input';
                element.addEventListener(eventType, () => {
                    // Debounce saving to avoid excessive localStorage writes
                    clearTimeout(this.saveTimeout);
                    this.saveTimeout = setTimeout(() => {
                        this.saveFormData();
                    }, 500);
                });
            }
        });
    }
    
    // Attach submit listener to save before form submission
    attachSubmitListener() {
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', () => {
                this.saveFormData();
            });
        }
    }
    
    // Clear saved form data
    clearFormData() {
        try {
            localStorage.removeItem(this.storageKey);
        } catch (e) {
            console.warn('Failed to clear form data from localStorage:', e);
        }
    }
    
    // Public method to manually clear data (could be used for a "reset" button)
    reset() {
        this.clearFormData();
        
        // Reset form to default values
        this.formFields.forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = false;
                } else if (element.tagName === 'SELECT') {
                    element.selectedIndex = 0;
                } else {
                    element.value = '';
                }
            }
        });
    }
}

// Initialize form persistence when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Small delay to ensure other scripts have initialized first
    setTimeout(() => {
        window.formPersistence = new FormPersistence();
    }, 100);
});

// Optional: Add a reset button handler if one exists
document.addEventListener('DOMContentLoaded', function() {
    const resetButton = document.getElementById('resetFormBtn');
    if (resetButton) {
        resetButton.addEventListener('click', function(e) {
            e.preventDefault();
            if (window.formPersistence) {
                window.formPersistence.reset();
            }
        });
    }
});
