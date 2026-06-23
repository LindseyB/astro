// Button Loading State Handler

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    const questionInput = document.getElementById('question_prompt');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            // Use event.submitter to find which button was clicked
            const clickedButton = e.submitter;

            if (!clickedButton || clickedButton.type !== 'submit') {
                return;
            }

            const submitMode = clickedButton.dataset.submitMode || '';
            const isAskAnythingMode = submitMode === 'ask-anything';

            if (questionInput) {
                if (isAskAnythingMode) {
                    const questionValue = questionInput.value.trim();
                    if (!questionValue) {
                        e.preventDefault();
                        questionInput.focus();
                        questionInput.setCustomValidity('Please enter a question for Ask Anything mode.');
                        questionInput.reportValidity();
                        return;
                    }
                    questionInput.setCustomValidity('');
                } else {
                    questionInput.setCustomValidity('');
                }
            }
            
            // Disable all submit buttons
            submitButtons.forEach(btn => {
                btn.disabled = true;
                btn.classList.add('loading');
            });

            // Store the original text and add spinner to the clicked button
            const originalText = clickedButton.innerHTML;
            clickedButton.setAttribute('data-original-text', originalText);
            clickedButton.innerHTML = '<span class="spinner"></span> Loading...';
        });
    }
});
