// Async music suggestion loading with streaming
function loadMusicSuggestion(chartData, chartType) {
    const container = document.getElementById('music-suggestion-placeholder');
    if (!container) return;

    container.innerHTML = '<p><em>Loading song suggestion...</em></p>';

    fetch('/music-suggestion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            birth_date: chartData.birthDate,
            birth_time: chartData.birthTime,
            timezone_offset: chartData.timezoneOffset,
            latitude: chartData.latitude,
            longitude: chartData.longitude,
            music_genre: chartData.musicGenre || 'any',
            chart_type: chartType
        })
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to load music suggestion');
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let suggestionText = '';

        function processStream() {
            return reader.read().then(({ done, value }) => {
                if (done) return;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop();

                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.substring(6));
                            
                            if (data.type === 'chunk') {
                                suggestionText += data.content;
                                container.innerHTML = `<p>${suggestionText}<span class="typing-cursor">|</span></p>`;
                            } else if (data.type === 'verified') {
                                const icon = data.verified ? '' : ' ⚠️';
                                container.innerHTML = `<p>${data.content}${icon}</p>`;
                            } else if (data.type === 'retry') {
                                suggestionText = '';
                                container.innerHTML = '<p><em>Finding alternative...</em></p>';
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
        container.remove();
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
