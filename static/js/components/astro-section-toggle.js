import { emitComponentEvent, safeLocalStorageGet, safeLocalStorageSet } from './helpers.js';

const ELEMENT_NAME = 'astro-section-toggle';

class AstroSectionToggle extends HTMLElement {
    constructor() {
        super();
        this.button = null;
        this.toggleIcon = null;
        this.targetElement = null;
        this.onClick = this.onClick.bind(this);
    }

    connectedCallback() {
        this.button = this.querySelector('button');
        this.toggleIcon = this.querySelector('.toggle-btn');

        const targetSelector = this.getAttribute('target');
        if (!targetSelector) {
            return;
        }

        this.targetElement = document.querySelector(targetSelector);
        if (!this.button || !this.targetElement) {
            return;
        }

        this.button.addEventListener('click', this.onClick);
        this.restoreState();
    }

    disconnectedCallback() {
        if (this.button) {
            this.button.removeEventListener('click', this.onClick);
        }
    }

    onClick(event) {
        event.preventDefault();
        const shouldExpand = this.targetElement.classList.contains('collapsed');
        this.updateSectionState(shouldExpand);
        this.persistState(shouldExpand);

        emitComponentEvent(this, 'astro:section-toggle', {
            expanded: shouldExpand,
            target: this.getAttribute('target')
        });
    }

    updateSectionState(expanded) {
        if (!this.targetElement || !this.button) {
            return;
        }

        if (expanded) {
            this.targetElement.classList.remove('collapsed');
            this.button.setAttribute('aria-expanded', 'true');
            if (this.toggleIcon) {
                this.toggleIcon.classList.remove('collapsed');
                this.toggleIcon.textContent = '▼';
            }
            this.setAttribute('expanded', '');
        } else {
            this.targetElement.classList.add('collapsed');
            this.button.setAttribute('aria-expanded', 'false');
            if (this.toggleIcon) {
                this.toggleIcon.classList.add('collapsed');
                this.toggleIcon.textContent = '▶';
            }
            this.removeAttribute('expanded');
        }
    }

    restoreState() {
        const storageKey = this.getStorageKey();
        const persisted = storageKey ? safeLocalStorageGet(storageKey) : null;
        if (persisted === 'expanded') {
            this.updateSectionState(true);
            return;
        }

        if (persisted === 'collapsed') {
            this.updateSectionState(false);
            return;
        }

        const expandedByAttribute = this.hasAttribute('expanded');
        this.updateSectionState(expandedByAttribute);
    }

    persistState(expanded) {
        const storageKey = this.getStorageKey();
        if (!storageKey) {
            return;
        }
        safeLocalStorageSet(storageKey, expanded ? 'expanded' : 'collapsed');
    }

    getStorageKey() {
        return this.getAttribute('storage-key');
    }
}

export function registerAstroSectionToggle() {
    if (!window.customElements.get(ELEMENT_NAME)) {
        window.customElements.define(ELEMENT_NAME, AstroSectionToggle);
    }
}
