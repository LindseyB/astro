const ELEMENT_NAME = 'astro-chart-wheel';

class AstroChartWheel extends HTMLElement {
    constructor() {
        super();
        this.cleanup = null;
    }

    connectedCallback() {
        if (this.cleanup) {
            return;
        }

        const dataKey = this.getAttribute('data-source') || 'chartData';
        const chartData = window[dataKey];
        if (!chartData) {
            return;
        }

        const canvasSelector = this.getAttribute('canvas-selector') || '#chartWheel';
        const buttonSelector = this.getAttribute('download-selector') || '#downloadChartWheelBtn';
        const fileName = this.getAttribute('download-filename') || 'chartWheel.png';

        if (typeof window.initChartWheel !== 'function') {
            return;
        }

        const result = window.initChartWheel({
            root: this,
            chartData,
            canvasSelector,
            downloadSelector: buttonSelector,
            downloadFilename: fileName
        });

        this.cleanup = result && typeof result.cleanup === 'function' ? result.cleanup : null;
    }

    disconnectedCallback() {
        if (this.cleanup) {
            this.cleanup();
            this.cleanup = null;
        }
    }
}

export function registerAstroChartWheel() {
    if (!window.customElements.get(ELEMENT_NAME)) {
        window.customElements.define(ELEMENT_NAME, AstroChartWheel);
    }
}
