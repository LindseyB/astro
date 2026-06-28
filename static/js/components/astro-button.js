import {
    createSpinnerMarkup,
    emitComponentEvent,
    findClosestForm,
    parseBooleanAttribute
} from './helpers.js';

const ELEMENT_NAME = 'astro-button';

class AstroButton extends HTMLElement {
    constructor() {
        super();
        this.button = null;
        this.form = null;
        this.onSubmit = this.onSubmit.bind(this);
    }

    connectedCallback() {
        this.button = this.querySelector('button');
        if (!this.button) {
            return;
        }

        this.form = findClosestForm(this.button);
        if (!this.form) {
            return;
        }

        this.form.addEventListener('submit', this.onSubmit);
    }

    disconnectedCallback() {
        if (this.form) {
            this.form.removeEventListener('submit', this.onSubmit);
        }
    }

    onSubmit(event) {
        if (!this.button || event.submitter !== this.button) {
            return;
        }

        const requiredSelector = this.getAttribute('require-input-selector');
        if (requiredSelector) {
            const requiredInput = this.form.querySelector(requiredSelector);
            if (requiredInput && !requiredInput.value.trim()) {
                event.preventDefault();
                requiredInput.focus();
                const validationMessage = this.getAttribute('validation-message') || 'Please complete this field.';
                requiredInput.setCustomValidity(validationMessage);
                requiredInput.reportValidity();
                return;
            }
            if (requiredInput) {
                requiredInput.setCustomValidity('');
            }
        }

        const disableAll = parseBooleanAttribute(this.getAttribute('disable-all-submit'), true);
        if (disableAll) {
            const submitButtons = this.form.querySelectorAll('button[type="submit"]');
            submitButtons.forEach((submitButton) => {
                submitButton.disabled = true;
                submitButton.classList.add('loading');
            });
        } else {
            this.button.disabled = true;
            this.button.classList.add('loading');
        }

        const loadingText = this.getAttribute('loading-text') || 'Loading...';
        this.button.dataset.originalText = this.button.innerHTML;
        this.button.innerHTML = createSpinnerMarkup(loadingText);

        emitComponentEvent(this, 'astro:button-loading', {
            buttonId: this.button.id || null,
            loadingText
        });
    }
}

export function registerAstroButton() {
    if (!window.customElements.get(ELEMENT_NAME)) {
        window.customElements.define(ELEMENT_NAME, AstroButton);
    }
}
