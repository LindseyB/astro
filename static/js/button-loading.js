// Button Loading State Handler

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            // Use event.submitter to find which button was clicked
            const clickedButton = e.submitter;
            
            if (clickedButton && clickedButton.type === 'submit') {
                // Disable all submit buttons
                submitButtons.forEach(btn => {
                    btn.disabled = true;
                    btn.classList.add('loading');
                });
                
                // Store the original text and add spinner to the clicked button
                const originalText = clickedButton.innerHTML;
                clickedButton.setAttribute('data-original-text', originalText);
                clickedButton.innerHTML = '<span class="spinner"></span> Loading...';
            }
        });
    }
});
