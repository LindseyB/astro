// Async music suggestion loading with streaming

/**
 * Load music suggestion asynchronously using Server-Sent Events (SSE)
 * @param {Object} chartData - The chart data including birth info and music preference
 * @param {string} chartType - Type of chart ('daily' or 'natal')
 */
function loadMusicSuggestion(chartData, chartType) {
    const container = document.getElementById('music-suggestion-placeholder');
    if (!container) return;

    // Show simple loading state
    container.innerHTML = '<p><em>Loading song suggestion...</em></p>';
    container.style.display = 'block';

    // Prepare request data
    const requestData = {
        birth_date: chartData.birthDate,
        birth_time: chartData.birthTime,
        timezone_offset: chartData.timezoneOffset,
        latitude: chartData.latitude,
        longitude: chartData.longitude,
        music_genre: chartData.musicGenre || 'any',
        chart_type: chartType
    };

    // Use fetch with streaming
    fetch('/music-suggestion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to load music suggestion');
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let suggestionText = '';
        let isVerifying = false;
        let isRetrying = false;

        function processStream() {
            return reader.read().then(({ done, value }) => {
                if (done) {
                    return;
                }

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Keep incomplete line in buffer

                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.substring(6));
                            
                            switch (data.type) {
                                case 'chunk':
                                    suggestionText += data.content;
                                    if (!isVerifying && !isRetrying) {
                                        container.innerHTML = `<p>${suggestionText}<span class="typing-cursor">|</span></p>`;
                                    }
                                    break;
                                
                                case 'verifying':
                                    isVerifying = true;
                                    container.innerHTML = `<p>${suggestionText}</p>`;
                                    break;
                                
                                case 'retry':
                                    isRetrying = true;
                                    suggestionText = '';
                                    container.innerHTML = '<p><em>Finding alternative...</em></p>';
                                    break;
                                
                                case 'verified':
                                    isVerifying = false;
                                    isRetrying = false;
                                    const verifiedIcon = data.verified ? '' : ' ⚠️';
                                    container.innerHTML = `<p>${data.content}${verifiedIcon}</p>`;
                                    break;
                                
                                case 'done':
                                    // Stream complete
                                    break;
                            }
                        } catch (e) {
                            console.error('Error parsing SSE data:', e);
                        }
                    }
                });

                return processStream();
            });
        }

        return processStream();
    })
    .catch(error => {
        console.error('Error loading music suggestion:', error);
        container.innerHTML = '<p><em>🎵 Couldn\'t load song suggestion</em></p>';
    });
}

// Auto-load music suggestion when page loads
document.addEventListener('DOMContentLoaded', function() {
    const musicContainer = document.getElementById('music-suggestion-placeholder');
    if (musicContainer) {
        const chartData = window.chartDataForMusic;
        const chartType = musicContainer.dataset.chartType || 'daily';
        
        if (chartData) {
            loadMusicSuggestion(chartData, chartType);
        }
    }
});
