// Interactive map for location selection using Leaflet
let map;
let marker;

document.addEventListener('DOMContentLoaded', function() {
    initMap();
    
    // Mark timezone field as user-modified when manually changed
    const timezoneField = document.getElementById('timezone_offset');
    if (timezoneField) {
        timezoneField.addEventListener('input', function() {
            this.dataset.userModified = 'true';
        });
    }
    
    // Handle Enter key in search input
    const searchInput = document.getElementById('locationSearch');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchLocation();
            }
        });
    }
});

function initMap() {
    // Default to New York City
    const defaultLocation = [40.7128, -74.0060];
    
    // Initialize map
    map = L.map('locationMap').setView(defaultLocation, 4);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Add click listener to map
    map.on('click', function(e) {
        setLocationFromMap(e.latlng);
    });
    
    // Try to get user's current location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const userLocation = [position.coords.latitude, position.coords.longitude];
                map.setView(userLocation, 10);
                setLocationFromMap({ lat: position.coords.latitude, lng: position.coords.longitude });
            },
            function() {
                // If geolocation fails, use default location
                setLocationFromMap({ lat: defaultLocation[0], lng: defaultLocation[1] });
            }
        );
    } else {
        // If geolocation is not supported, use default location
        setLocationFromMap({ lat: defaultLocation[0], lng: defaultLocation[1] });
    }
}

function setLocationFromMap(location) {
    const lat = location.lat;
    const lng = location.lng;
    
    // Remove existing marker
    if (marker) {
        map.removeLayer(marker);
    }
    
    // Add new marker
    marker = L.marker([lat, lng]).addTo(map);
    
    // Convert to astrology format and update form fields
    const astroLat = convertToAstroFormat(lat, 'lat');
    const astroLng = convertToAstroFormat(lng, 'lng');
    
    document.getElementById('latitude').value = astroLat;
    document.getElementById('longitude').value = astroLng;
    
    // Update the display
    updateLocationDisplay(lat, lng, astroLat, astroLng);
    
    // Try to get timezone for this location
    getTimezoneForLocation(lat, lng);
}

function convertToAstroFormat(decimal, type) {
    const abs = Math.abs(decimal);
    const degrees = Math.floor(abs);
    const minutes = Math.floor((abs - degrees) * 60);
    
    let direction;
    if (type === 'lat') {
        direction = decimal >= 0 ? 'n' : 's';
    } else {
        direction = decimal >= 0 ? 'e' : 'w';
    }
    
    return `${degrees.toString().padStart(2, '0')}${direction}${minutes.toString().padStart(2, '0')}`;
}

function updateLocationDisplay(lat, lng, astroLat, astroLng) {
    const display = document.getElementById('locationDisplay');
    if (display) {
        display.innerHTML = `
            <strong>Selected Location:</strong><br>
            Decimal: ${lat.toFixed(4)}°, ${lng.toFixed(4)}°<br>
            Astrology Format: ${astroLat}, ${astroLng}
        `;
    }
}

function getTimezoneForLocation(lat, lng) {
    // Use a simple timezone estimation based on longitude
    // For a more accurate timezone, you'd want to use a timezone API
    const timezoneOffset = Math.round(lng / 15);
    const offsetString = (timezoneOffset >= 0 ? '+' : '') + 
                        timezoneOffset.toString().padStart(2, '0') + ':00';
    
    const timezoneField = document.getElementById('timezone_offset');
    if (timezoneField && !timezoneField.dataset.userModified) {
        timezoneField.value = offsetString;
    }
}

// Search for locations using Nominatim (OpenStreetMap's geocoding service)
function searchLocation() {
    const searchInput = document.getElementById('locationSearch');
    const searchValue = searchInput.value.trim();
    
    if (!searchValue) return;
    
    // Show loading state
    const searchButton = document.querySelector('.location-search button');
    const originalText = searchButton.textContent;
    searchButton.textContent = 'Searching...';
    searchButton.disabled = true;
    
    // Use Nominatim API for geocoding
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchValue)}&limit=1`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                const result = data[0];
                const lat = parseFloat(result.lat);
                const lng = parseFloat(result.lon);
                
                map.setView([lat, lng], 10);
                setLocationFromMap({ lat: lat, lng: lng });
            } else {
                alert('Location not found. Please try a different search term.');
            }
        })
        .catch(error => {
            console.error('Geocoding error:', error);
            alert('Error searching for location. Please try again.');
        })
        .finally(() => {
            // Reset button state
            searchButton.textContent = originalText;
            searchButton.disabled = false;
        });
}
