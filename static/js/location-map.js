// Interactive map for location selection using Leaflet
let map;
let marker;
let currentTileLayer;
// Set while we programmatically change the timezone, so those updates are not
// mistaken for a manual override by the user.
let suppressTzModified = false;

document.addEventListener('DOMContentLoaded', function() {
    initMap();
    
    // Mark timezone field as user-modified when the user changes it themselves,
    // so our location/date best-guess never overrides their choice.
    const timezoneField = document.getElementById('timezone_offset');
    if (timezoneField) {
        timezoneField.addEventListener('change', function() {
            if (!suppressTzModified) this.dataset.userModified = 'true';
        });
        if (window.jQuery) {
            jQuery('#timezone_offset').on('select2:select', function() {
                this.dataset.userModified = 'true';
            });
        }
    }

    // When the birth date changes, re-evaluate the timezone guess so the offset
    // reflects daylight saving for that time of year.
    const birthDateField = document.getElementById('birth_date');
    if (birthDateField) {
        birthDateField.addEventListener('change', applyTimezoneGuess);
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
    
    // Listen for dark mode changes and update map tiles
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'class') {
                updateMapTiles();
            }
        });
    });
    
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class']
    });
});

function initMap() {
    // Default to New York City
    const defaultLocation = [40.7128, -74.0060];
    
    // Initialize map
    map = L.map('locationMap').setView(defaultLocation, 4);
    
    // Make map globally available for form persistence
    window.map = map;
    
    // Add appropriate tile layer based on current mode
    updateMapTiles();
    
    // Add click listener to map
    map.on('click', function(e) {
        setLocationFromMap(e.latlng);
    });
    
    // Check if form already has saved location data (from localStorage)
    const latField = document.getElementById('latitude');
    const lngField = document.getElementById('longitude');
    const hasExistingLocation = latField && lngField && latField.value && lngField.value;
    
    if (hasExistingLocation) {
        // Don't override existing saved location - form persistence will handle map restoration
        return;
    }
    
    // Only try to get user's current location if no saved location exists
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
    
    // Make marker globally available for form persistence
    window.marker = marker;
    
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
    const timezoneField = document.getElementById('timezone_offset');
    if (!timezoneField) return;
    // Respect a manual override — never clobber a timezone the user chose.
    if (timezoneField.dataset.userModified === 'true') return;

    // Resolve the IANA timezone for these coordinates, then compute the UTC
    // offset for the birth date so daylight saving (time of year) is handled.
    const url = `https://timeapi.io/api/timezone/coordinate?latitude=${lat}&longitude=${lng}`;
    fetch(url)
        .then(response => response.ok ? response.json() : Promise.reject(new Error('timezone lookup failed')))
        .then(data => {
            if (!data || !data.timeZone) throw new Error('no timezone in response');
            timezoneField.dataset.ianaZone = data.timeZone;
            applyTimezoneGuess();
        })
        .catch(() => {
            // Fallback: rough estimate from longitude (no DST awareness).
            estimateTimezoneFromLongitude(lng);
        });
}

// Compute the UTC offset (e.g. "-04:00") for an IANA timezone on a given date,
// using the browser's Intl support so daylight saving is taken into account.
function offsetForZoneOnDate(timeZone, date) {
    try {
        const dtf = new Intl.DateTimeFormat('en-US', { timeZone: timeZone, timeZoneName: 'longOffset' });
        const part = dtf.formatToParts(date).find(p => p.type === 'timeZoneName');
        const name = part ? part.value : 'GMT+00:00';
        const match = name.match(/GMT([+-])(\d{1,2})(?::?(\d{2}))?/);
        if (!match) return '+00:00'; // plain "GMT" => UTC
        const sign = match[1];
        const hours = match[2].padStart(2, '0');
        const minutes = match[3] || '00';
        return `${sign}${hours}:${minutes}`;
    } catch (e) {
        return null;
    }
}

// Apply the best-guess timezone for the resolved IANA zone and the birth date.
function applyTimezoneGuess() {
    const timezoneField = document.getElementById('timezone_offset');
    if (!timezoneField || timezoneField.dataset.userModified === 'true') return;
    const zone = timezoneField.dataset.ianaZone;
    if (!zone) return;

    const birthDateField = document.getElementById('birth_date');
    let refDate;
    if (birthDateField && birthDateField.value) {
        // Noon UTC on the birth date keeps us clear of DST transition edges.
        refDate = new Date(birthDateField.value + 'T12:00:00Z');
        if (isNaN(refDate.getTime())) refDate = new Date();
    } else {
        refDate = new Date();
    }

    const offset = offsetForZoneOnDate(zone, refDate);
    if (offset) {
        setTimezoneSelectValue(offset);
        return;
    }
    const lastLng = parseFloat(timezoneField.dataset.lastLng || '');
    if (!isNaN(lastLng)) estimateTimezoneFromLongitude(lastLng);

// Rough timezone estimate from longitude, used only when the lookup fails.
function estimateTimezoneFromLongitude(lng) {
    const timezoneField = document.getElementById('timezone_offset');
    if (!timezoneField || timezoneField.dataset.userModified === 'true') return;
    const offsetHours = Math.round(lng / 15);
    const sign = offsetHours >= 0 ? '+' : '-';
    const abs = Math.abs(offsetHours).toString().padStart(2, '0');
    setTimezoneSelectValue(`${sign}${abs}:00`);
}

// Programmatically set the timezone select (Select2-aware) without it counting
// as a manual user override.
function setTimezoneSelectValue(offset) {
    const timezoneField = document.getElementById('timezone_offset');
    if (!timezoneField) return;
    suppressTzModified = true;
    if (window.jQuery && jQuery('#timezone_offset').data('select2')) {
        jQuery('#timezone_offset').val(offset).trigger('change');
    } else {
        timezoneField.value = offset;
        timezoneField.dispatchEvent(new Event('change'));
    }
    setTimeout(function() { suppressTzModified = false; }, 0);
}

function updateMapTiles() {
    if (!map) return;
    
    // Remove existing tile layer if present
    if (currentTileLayer) {
        map.removeLayer(currentTileLayer);
    }
    
    const isDarkMode = document.documentElement.classList.contains('dark') ||
        document.documentElement.classList.contains('dark-mode');
    
    if (isDarkMode) {
        // Dark mode: Use CartoDB Dark Matter tiles
        currentTileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '© OpenStreetMap contributors © CARTO',
            subdomains: 'abcd',
            maxZoom: 19
        }).addTo(map);
    } else {
        // Light mode: Use standard OpenStreetMap tiles
        currentTileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);
    }
}

// Search for locations using Nominatim (OpenStreetMap's geocoding service)
function searchLocation() {
    const searchInput = document.getElementById('locationSearch');
    const searchValue = searchInput.value.trim();
    
    if (!searchValue) return;
    
    // Show loading state
    const searchButton = document.querySelector('.location-search-btn');
    const originalText = searchButton.textContent;
    searchButton.textContent = 'Searching...';
    searchButton.disabled = true;
    
    // Use Nominatim API for geocoding
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchValue)}&limit=1`;
    
    clearSearchError();
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Geocoding request failed (${response.status})`);
            }
            return response.json();
        })
        .then(data => {
            if (data && data.length > 0) {
                const result = data[0];
                const lat = parseFloat(result.lat);
                const lng = parseFloat(result.lon);
                
                map.setView([lat, lng], 10);
                setLocationFromMap({ lat: lat, lng: lng });
            } else {
                showSearchError('Location not found. Try a different search term.');
            }
        })
        .catch(error => {
            console.error('Geocoding error:', error);
            showSearchError('Could not search right now. Please try again.');
        })
        .finally(() => {
            // Reset button state
            searchButton.textContent = originalText;
            searchButton.disabled = false;
        });
}

// Show / clear an inline search error message (replaces blocking alerts).
function showSearchError(message) {
    const el = document.getElementById('locationSearchError');
    if (!el) return;
    el.textContent = message;
    el.hidden = false;
}

function clearSearchError() {
    const el = document.getElementById('locationSearchError');
    if (!el) return;
    el.textContent = '';
    el.hidden = true;
}
