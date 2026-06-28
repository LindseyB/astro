const ELEMENT_NAME = 'astro-timezone-select';

class AstroTimezoneSelect extends HTMLElement {
    constructor() {
        super();
        this.select = null;
        this.boundChangeHandler = this.onChange.bind(this);
    }

    connectedCallback() {
        const selector = this.getAttribute('select-selector') || 'select';
        this.select = this.querySelector(selector);
        if (!this.select) {
            return;
        }

        this.initSelect2();
        this.restoreValue();
        this.bindChangeHandler();
    }

    disconnectedCallback() {
        if (this.select) {
            this.select.removeEventListener('change', this.boundChangeHandler);
        }

        if (window.jQuery && window.jQuery.fn && window.jQuery.fn.select2 && this.select) {
            const $select = window.jQuery(this.select);
            if ($select.data('select2')) {
                $select.off('change.astroTimezoneSelect');
            }
        }
    }

    initSelect2() {
        if (!(window.jQuery && window.jQuery.fn && window.jQuery.fn.select2)) {
            return;
        }

        const $select = window.jQuery(this.select);
        if ($select.data('select2')) {
            return;
        }

        $select.select2({
            placeholder: 'Select or search for a timezone...',
            allowClear: false,
            width: '100%',
            dropdownAutoWidth: false
        });
    }

    restoreValue() {
        let storedValue = null;
        try {
            storedValue = window.localStorage.getItem('timezone_offset');
        } catch (err) {
            storedValue = null;
        }

        if (!storedValue) {
            return;
        }

        this.select.value = storedValue;

        if (window.jQuery && window.jQuery.fn && window.jQuery.fn.select2) {
            window.jQuery(this.select).trigger('change');
        }
    }

    bindChangeHandler() {
        if (!this.select) {
            return;
        }

        this.select.addEventListener('change', this.boundChangeHandler);

        if (window.jQuery && window.jQuery.fn && window.jQuery.fn.select2) {
            window.jQuery(this.select).on('change.astroTimezoneSelect', this.boundChangeHandler);
        }
    }

    onChange() {
        if (!this.select) {
            return;
        }

        try {
            window.localStorage.setItem('timezone_offset', this.select.value);
        } catch (err) {
            // Ignore storage write failures.
        }
    }
}

export function registerAstroTimezoneSelect() {
    if (!window.customElements.get(ELEMENT_NAME)) {
        window.customElements.define(ELEMENT_NAME, AstroTimezoneSelect);
    }
}
