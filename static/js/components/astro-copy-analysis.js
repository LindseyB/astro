import { emitComponentEvent } from './helpers.js';

const ELEMENT_NAME = 'astro-copy-analysis';
const SUCCESS_MS = 2000;

class AstroCopyAnalysis extends HTMLElement {
    constructor() {
        super();
        this.button = null;
        this.onClick = this.onClick.bind(this);
    }

    connectedCallback() {
        this.button = this.querySelector('button');
        if (!this.button) {
            this.button = document.createElement('button');
            this.button.type = 'button';
            this.button.className = this.getAttribute('button-class') || 'copy-chip';
            this.button.title = this.getAttribute('title') || 'Copy analysis';
            this.button.setAttribute('aria-label', this.getAttribute('aria-label') || this.button.title);
            this.button.innerHTML = this.getAttribute('icon-html') || 'Copy';
            this.appendChild(this.button);
        }

        this.button.addEventListener('click', this.onClick);
    }

    disconnectedCallback() {
        if (this.button) {
            this.button.removeEventListener('click', this.onClick);
        }
    }

    onClick(event) {
        event.preventDefault();
        const copyText = this.buildCopyText();
        if (!copyText) {
            return;
        }

        this.copyToClipboard(copyText)
            .then(() => {
                this.showCopySuccess();
                emitComponentEvent(this, 'astro:copy-success', {
                    sourceSelector: this.getSourceSelector()
                });
            })
            .catch(() => {
                emitComponentEvent(this, 'astro:copy-failure', {
                    sourceSelector: this.getSourceSelector()
                });
            });
    }

    getSourceSelector() {
        return this.getAttribute('source-selector') || '#analysisContent';
    }

    getSectionSelector() {
        return this.getAttribute('section-selector') || '.analysis-section';
    }

    getAnalysisElement() {
        const selector = this.getSourceSelector();
        return document.querySelector(selector);
    }

    getAnalysisSection(analysisElement) {
        if (!analysisElement) {
            return null;
        }
        return analysisElement.closest(this.getSectionSelector());
    }

    buildCopyText() {
        const analysisElement = this.getAnalysisElement();
        if (!analysisElement) {
            return '';
        }

        const analysisText = analysisElement.innerText || analysisElement.textContent || '';
        const section = this.getAnalysisSection(analysisElement);

        const sun = section ? section.dataset.sun : '';
        const moon = section ? section.dataset.moon : '';
        const ascendant = section ? section.dataset.ascendant : '';

        const chartInfo = sun && moon && ascendant
            ? sun + ' ☉ ' + moon + ' ☽ ' + ascendant + ' ⬆\n\n'
            : '';

        const footerText = this.getAttribute('footer-text') || '✨ Get your cosmic vibe check at:';
        return chartInfo + analysisText.trim() + '\n\n' + footerText + ' ' + window.location.origin;
    }

    copyToClipboard(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            return navigator.clipboard.writeText(text).catch(() => this.copyTextFallback(text));
        }
        return this.copyTextFallback(text);
    }

    copyTextFallback(text) {
        return new Promise((resolve, reject) => {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();

            try {
                const success = document.execCommand('copy');
                if (success) {
                    resolve();
                } else {
                    reject(new Error('Copy command was rejected.'));
                }
            } catch (err) {
                reject(err);
            }

            document.body.removeChild(textArea);
        });
    }

    showCopySuccess() {
        if (!this.button) {
            return;
        }

        const originalText = this.button.innerHTML;
        this.button.innerHTML = this.getAttribute('success-text') || '✓';
        this.button.style.background = '#22c55e';

        window.setTimeout(() => {
            this.button.innerHTML = originalText;
            this.button.style.background = '';
        }, SUCCESS_MS);
    }
}

export function registerAstroCopyAnalysis() {
    if (!window.customElements.get(ELEMENT_NAME)) {
        window.customElements.define(ELEMENT_NAME, AstroCopyAnalysis);
    }
}
