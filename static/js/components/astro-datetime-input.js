const ELEMENT_NAME = 'astro-datetime-input';

function pad(n) {
    return String(n).padStart(2, '0');
}

function digitsOnly(value) {
    return (value || '').replace(/\D/g, '');
}

function formatDateDigits(digits) {
    const normalized = digits.slice(0, 8);
    if (normalized.length <= 4) {
        return normalized;
    }
    if (normalized.length <= 6) {
        return normalized.slice(0, 4) + '-' + normalized.slice(4);
    }
    return normalized.slice(0, 4) + '-' + normalized.slice(4, 6) + '-' + normalized.slice(6);
}

function formatTimeDigits(digits) {
    const normalized = digits.slice(0, 4);
    if (normalized.length <= 2) {
        return normalized;
    }
    return normalized.slice(0, 2) + ':' + normalized.slice(2);
}

function buildDate(yearValue, monthValue, dayValue) {
    const year = parseInt(yearValue, 10);
    const month = parseInt(monthValue, 10);
    const day = parseInt(dayValue, 10);

    if (!year || month < 1 || month > 12 || day < 1 || day > 31) {
        return '';
    }

    const date = new Date(Date.UTC(year, month - 1, day));
    if (date.getUTCFullYear() !== year || date.getUTCMonth() + 1 !== month || date.getUTCDate() !== day) {
        return '';
    }

    return String(year).padStart(4, '0') + '-' + pad(month) + '-' + pad(day);
}

function normalizeDate(value) {
    const digits = digitsOnly(value);
    if (digits.length !== 8) {
        return '';
    }
    return buildDate(digits.slice(0, 4), digits.slice(4, 6), digits.slice(6, 8));
}

function normalizeTime(value) {
    const digits = digitsOnly(value);
    if (digits.length !== 4) {
        return '';
    }

    const hour = parseInt(digits.slice(0, 2), 10);
    const minute = parseInt(digits.slice(2, 4), 10);

    if (hour > 23 || minute > 59) {
        return '';
    }

    return pad(hour) + ':' + pad(minute);
}

class AstroDatetimeInput extends HTMLElement {
    constructor() {
        super();
        this.textInput = null;
        this.nativeInput = null;
        this.triggerButton = null;
        this.kind = 'date';
        this.onFocus = this.onFocus.bind(this);
        this.onKeydown = this.onKeydown.bind(this);
        this.onInput = this.onInput.bind(this);
        this.onBlur = this.onBlur.bind(this);
        this.onTriggerClick = this.onTriggerClick.bind(this);
        this.onNativeChange = this.onNativeChange.bind(this);
    }

    connectedCallback() {
        this.kind = this.getAttribute('kind') === 'time' ? 'time' : 'date';

        const inputSelector = this.getAttribute('input-selector') || 'input[type="text"]';
        const nativeSelector = this.getAttribute('native-selector') || 'input[type="date"], input[type="time"]';
        const triggerSelector = this.getAttribute('trigger-selector') || 'button[type="button"]';

        this.textInput = this.querySelector(inputSelector);
        this.nativeInput = this.querySelector(nativeSelector);
        this.triggerButton = this.querySelector(triggerSelector);

        if (!this.textInput) {
            return;
        }

        this.textInput.addEventListener('focus', this.onFocus);
        this.textInput.addEventListener('keydown', this.onKeydown);
        this.textInput.addEventListener('input', this.onInput);
        this.textInput.addEventListener('blur', this.onBlur);

        if (this.triggerButton && this.nativeInput) {
            this.triggerButton.addEventListener('click', this.onTriggerClick);
            this.nativeInput.addEventListener('change', this.onNativeChange);
        }
    }

    disconnectedCallback() {
        if (!this.textInput) {
            return;
        }

        this.textInput.removeEventListener('focus', this.onFocus);
        this.textInput.removeEventListener('keydown', this.onKeydown);
        this.textInput.removeEventListener('input', this.onInput);
        this.textInput.removeEventListener('blur', this.onBlur);

        if (this.triggerButton && this.nativeInput) {
            this.triggerButton.removeEventListener('click', this.onTriggerClick);
            this.nativeInput.removeEventListener('change', this.onNativeChange);
        }
    }

    formatter() {
        return this.kind === 'time' ? formatTimeDigits : formatDateDigits;
    }

    normalizer() {
        return this.kind === 'time' ? normalizeTime : normalizeDate;
    }

    onFocus() {
        this.textInput.value = '';
    }

    onKeydown(event) {
        const navigationKeys = [
            'Backspace', 'Delete', 'ArrowLeft', 'ArrowRight',
            'ArrowUp', 'ArrowDown', 'Tab', 'Home', 'End'
        ];

        if (navigationKeys.includes(event.key)) {
            return;
        }

        if (event.ctrlKey || event.metaKey) {
            return;
        }

        if (event.key.length === 1 && !/^\d$/.test(event.key)) {
            event.preventDefault();
        }
    }

    onInput() {
        const formatted = this.formatter()(digitsOnly(this.textInput.value));
        if (formatted !== this.textInput.value) {
            this.textInput.value = formatted;
        }
    }

    onBlur() {
        const normalized = this.normalizer()(this.textInput.value);
        const rawValue = (this.textInput.value || '').trim();

        if (rawValue && !normalized) {
            this.textInput.value = '';
            this.textInput.dispatchEvent(new Event('change', { bubbles: true }));
            return;
        }

        if (normalized && normalized !== this.textInput.value) {
            this.textInput.value = normalized;
            this.textInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }

    onTriggerClick() {
        const normalized = this.normalizer()(this.textInput.value);
        this.nativeInput.value = normalized || this.nativeInput.value;

        try {
            this.nativeInput.showPicker();
        } catch (err) {
            this.nativeInput.focus();
            this.nativeInput.click();
        }
    }

    onNativeChange() {
        if (!this.nativeInput.value) {
            return;
        }

        this.textInput.value = this.nativeInput.value;
        this.textInput.dispatchEvent(new Event('change', { bubbles: true }));
    }
}

export function registerAstroDatetimeInput() {
    if (!window.customElements.get(ELEMENT_NAME)) {
        window.customElements.define(ELEMENT_NAME, AstroDatetimeInput);
    }
}
