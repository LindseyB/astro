// Copy Analysis functionality
function copyAnalysis() {
    const analysisElement = document.getElementById('analysisContent');
    const copyBtn = document.getElementById('copyAnalysisBtn');
    
    if (!analysisElement || !copyBtn) return;
    
    // Get the text content (without HTML tags)
    const analysisText = analysisElement.innerText || analysisElement.textContent;
    
    // Get chart data from data attributes
    const analysisSection = analysisElement.closest('.analysis-section');
    const sun = analysisSection.dataset.sun;
    const moon = analysisSection.dataset.moon;
    const ascendant = analysisSection.dataset.ascendant;
    
    const chartInfo = `${sun} ☉ ${moon} ☽ ${ascendant} ⬆\n\n`;
    const fullText = chartInfo + analysisText + '\n\n✨ Get your cosmic vibe check at: ' + window.location.origin;
    
    // Copy to clipboard
    navigator.clipboard.writeText(fullText).then(function() {
        // Success feedback
        showCopySuccess(copyBtn);
    }).catch(function(err) {
        // Fallback for older browsers
        copyTextFallback(fullText, copyBtn);
    });
}

function showCopySuccess(copyBtn) {
    const originalText = copyBtn.innerHTML;
    copyBtn.innerHTML = '✅';
    copyBtn.style.background = '#22c55e';
    
    // Reset button after 2 seconds
    setTimeout(function() {
        copyBtn.innerHTML = originalText;
        copyBtn.style.background = '';
    }, 2000);
}

function copyTextFallback(text, copyBtn) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showCopySuccess(copyBtn);
    } catch (err) {
        console.error('Copy failed:', err);
    }
    
    document.body.removeChild(textArea);
}
