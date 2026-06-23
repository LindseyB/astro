/**
 * Modal functionality for help dialogs
 */

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
    }
}

function syncAskAnythingBirthFields() {
    const fieldMap = [
        ['birth_date', 'ask_birth_date'],
        ['birth_time', 'ask_birth_time'],
        ['timezone_offset', 'ask_timezone_offset'],
        ['latitude', 'ask_latitude'],
        ['longitude', 'ask_longitude']
    ];

    let missingSourceField = null;

    fieldMap.forEach(([sourceId, targetId]) => {
        const source = document.getElementById(sourceId);
        const target = document.getElementById(targetId);
        const value = source ? source.value : '';

        if (target) {
            target.value = value;
        }

        if (!missingSourceField && source && !value) {
            missingSourceField = source;
        }
    });

    return missingSourceField;
}

// Initialize modal listeners when DOM is ready
function initializeModals() {
    // Open location help modal when button is clicked
    const locationHelpBtn = document.getElementById('locationHelpBtn');
    if (locationHelpBtn) {
        locationHelpBtn.addEventListener('click', function() {
            openModal('locationHelpModal');
        });
    }

    // Open Ask Anything modal from the mode button
    const askAnythingBtn = document.getElementById('askAnythingBtn');
    if (askAnythingBtn) {
        askAnythingBtn.addEventListener('click', function() {
            const missingField = syncAskAnythingBirthFields();
            openModal('askAnythingModal');
            const askInput = document.getElementById('question_prompt');
            if (askInput) {
                askInput.focus();
            }

            if (missingField) {
                if (missingField.id === 'latitude' || missingField.id === 'longitude') {
                    openModal('locationHelpModal');
                    const locationSearch = document.getElementById('locationSearch');
                    if (locationSearch) {
                        locationSearch.focus();
                    }
                } else {
                    missingField.reportValidity();
                }
            }
        });
    }

    const askAnythingForm = document.querySelector('#askAnythingModal form');
    if (askAnythingForm) {
        askAnythingForm.addEventListener('submit', function(e) {
            const missingField = syncAskAnythingBirthFields();
            if (missingField) {
                e.preventDefault();
                closeModal('askAnythingModal');

                if (missingField.id === 'latitude' || missingField.id === 'longitude') {
                    openModal('locationHelpModal');
                    const locationSearch = document.getElementById('locationSearch');
                    if (locationSearch) {
                        locationSearch.focus();
                    }
                    return;
                }

                missingField.focus();
                missingField.reportValidity();
            }
        });
    }
    
    // Close modal when clicking on overlay (outside modal content)
    const overlays = document.querySelectorAll('.modal-overlay');
    overlays.forEach(overlay => {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal(this.id);
            }
        });
    });
    
    // Close modal when clicking close button
    const closeButtons = document.querySelectorAll('.modal-close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal-overlay');
            if (modal) {
                closeModal(modal.id);
            }
        });
    });
    
    // Close modal on Escape key (remove old listener first to prevent duplicates)
    document.removeEventListener('keydown', handleEscapeKey);
    document.addEventListener('keydown', handleEscapeKey);
}

// Named function for Escape key handling to allow proper cleanup
function handleEscapeKey(e) {
    if (e.key === 'Escape') {
        const activeModal = document.querySelector('.modal-overlay.active');
        if (activeModal) {
            closeModal(activeModal.id);
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeModals);
} else {
    initializeModals();
}
