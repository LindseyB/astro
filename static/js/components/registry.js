import { registerAstroButton } from './astro-button.js';
import { registerAstroChartWheel } from './astro-chart-wheel.js';
import { registerAstroCopyAnalysis } from './astro-copy-analysis.js';
import { registerAstroDatetimeInput } from './astro-datetime-input.js';
import { registerAstroSectionToggle } from './astro-section-toggle.js';
import { registerAstroTimezoneSelect } from './astro-timezone-select.js';

let componentsRegistered = false;

export function registerAstroComponents() {
    if (componentsRegistered) {
        return;
    }

    registerAstroButton();
    registerAstroChartWheel();
    registerAstroCopyAnalysis();
    registerAstroDatetimeInput();
    registerAstroSectionToggle();
    registerAstroTimezoneSelect();

    componentsRegistered = true;
}
