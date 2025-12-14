// Dropdown button functionality
function toggleDropdown() {
    const dropdown = document.getElementById('chartDropdown');
    dropdown.classList.toggle('show');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('chartDropdown');
    const toggleButton = document.querySelector('.dropdown-toggle');
    
    if (dropdown && !event.target.closest('.dropdown-button-wrapper')) {
        dropdown.classList.remove('show');
    }
});

// Prevent form submission when clicking the dropdown toggle
document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.querySelector('.dropdown-toggle');
    if (toggleButton) {
        toggleButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
        });
    }
});
