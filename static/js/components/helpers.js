export function parseBooleanAttribute(value, defaultValue) {
    if (value === null || value === undefined) {
        return Boolean(defaultValue);
    }
    if (value === '' || value === 'true') {
        return true;
    }
    if (value === 'false') {
        return false;
    }
    return Boolean(defaultValue);
}

export function emitComponentEvent(target, name, detail) {
    target.dispatchEvent(new CustomEvent(name, {
        bubbles: true,
        composed: true,
        detail: detail || {}
    }));
}

export function createSpinnerMarkup(text) {
    return '<span class="spinner"></span> ' + text;
}

export function findClosestForm(node) {
    if (!node) {
        return null;
    }
    return node.closest('form');
}

export function safeLocalStorageGet(key) {
    try {
        return window.localStorage.getItem(key);
    } catch (err) {
        return null;
    }
}

export function safeLocalStorageSet(key, value) {
    try {
        window.localStorage.setItem(key, value);
    } catch (err) {
        return false;
    }
    return true;
}
