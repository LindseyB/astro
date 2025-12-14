// Initialize timezone selector with Select2
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Select2 on the timezone select element
    $('#timezone_offset').select2({
        placeholder: 'Select or search for a timezone...',
        allowClear: false,
        width: '100%',
        dropdownAutoWidth: false
    });
    
    // If there's a stored value in localStorage, restore it
    var storedTimezone = localStorage.getItem('timezone_offset');
    if (storedTimezone) {
        $('#timezone_offset').val(storedTimezone).trigger('change');
    }
    
    // Save timezone to localStorage when changed
    $('#timezone_offset').on('change', function() {
        localStorage.setItem('timezone_offset', $(this).val());
    });
});
