// LaunchDarkly Experiment - Main CTA Button
(function() {
    const ldClientId = "692742d0a95e1a0ac789ca56";
    
    if (!ldClientId) {
        return;
    }
    
    // Wait for LaunchDarkly SDK to be available
    if (typeof window.LDClient === 'undefined') {
        console.warn('LaunchDarkly SDK not loaded');
        return;
    }
    
    const context = {
        kind: 'user',
        key: 'anonymous-' + Math.random().toString(36).substring(7),
        anonymous: true
    };
    
    const ldClient = window.LDClient.initialize(ldClientId, context);
    
    
    
    
    
    ldClient.on('ready', () => {
        const showMainCta = ldClient.variation('get-horoscope-main-button-experiment', false);
        
        if (showMainCta) {
            const horoscopeButton = document.querySelector('button[formaction="/chart"]');
            if (horoscopeButton) {
                horoscopeButton.classList.add('main-cta');
            }
        }
    });
    
    ldClient.on('change:get-horoscope-main-button-experiment', (value) => {
        const horoscopeButton = document.querySelector('button[formaction="/chart"]');
        if (horoscopeButton) {
            if (value) {
                horoscopeButton.classList.add('main-cta');
            } else {
                horoscopeButton.classList.remove('main-cta');
            }
        }
    });
})();
