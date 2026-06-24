// Async music suggestion loading with streaming
function loadMusicSuggestion(chartData, chartType) {
    const container = document.getElementById('music-suggestion-placeholder');
    if (!container) return;

    // Prevent duplicate requests if multiple triggers fire.
    if (container.dataset.loading === 'true' || container.dataset.loaded === 'true') {
        return;
    }
    container.dataset.loading = 'true';

    let reader;

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
        
        reader = response.body.getReader();
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
                            
                            if (data.chunk) {
                                suggestionText += data.chunk;
                                // Safely update suggestion text with cursor
                                const p = document.createElement('p');
                                p.textContent = suggestionText;
                                const cursor = document.createElement('span');
                                cursor.className = 'typing-cursor';
                                cursor.textContent = '|';
                                p.appendChild(cursor);
                                container.innerHTML = '';
                                container.appendChild(p);
                            } else if (data.done) {
                                // Remove cursor when done
                                const p = document.createElement('p');
                                p.textContent = suggestionText;
                                container.innerHTML = '';
                                container.appendChild(p);
                                container.dataset.loaded = 'true';
                                container.dataset.loading = 'false';
                            } else if (data.error) {
                                console.error('Music suggestion error:', data.error);
                                reader.cancel();
                                container.dataset.loading = 'false';
                                container.remove();
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
        if (reader) {
            reader.cancel();
        }
        container.dataset.loading = 'false';
        container.remove();
    });
}

// Auto-load music suggestion when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Streaming pages trigger music suggestion after analysis finishes.
    if (document.body.dataset.streaming === 'true') {
        return;
    }

    const musicContainer = document.getElementById('music-suggestion-placeholder');
    if (musicContainer) {
        const chartData = window.chartDataForMusic;
        const chartType = musicContainer.dataset.chartType || 'daily';
        
        if (chartData) {
            loadMusicSuggestion(chartData, chartType);
        }
    }
});
