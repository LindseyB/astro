/**
 * Client-side streaming for horoscope analysis
 * Fetches and displays AI-generated content as it streams in
 */

(function() {
    'use strict';
    
    // Wait for DOM to be fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initStreaming);
    } else {
        initStreaming();
    }
    
    function initStreaming() {
        // Check if we're on a streaming-enabled page
        const streamingEnabled = document.body.dataset.streaming === 'true';
        if (!streamingEnabled) {
            return;
        }
        
        const analysisContainer = document.getElementById('analysisContent');
        const chartData = window.chartDataForStreaming;
        
        console.log('Streaming initialized:', {
            analysisContainer: !!analysisContainer,
            chartData: chartData,
            hasChartData: !!chartData
        });
        
        if (!analysisContainer || !chartData) {
            console.error('Missing required elements for streaming', {
                analysisContainer: !!analysisContainer,
                chartData: chartData
            });
            return;
        }
    
    // Show loading state
    analysisContainer.innerHTML = '<p style="font-style: italic;">✨ Consulting the stars...</p>';
    
    // Determine endpoint based on page type
    let endpoint;
    if (chartData.pageType === 'chart') {
        endpoint = '/stream-chart-analysis';
    } else if (chartData.pageType === 'full-chart') {
        endpoint = '/stream-full-chart-analysis';
    } else if (chartData.pageType === 'live-mas') {
        endpoint = '/stream-live-mas-analysis';
    } else {
        console.error('Unknown page type:', chartData.pageType);
        return;
    }
    
    // Start streaming
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            birth_date: chartData.birthDate,
            birth_time: chartData.birthTime,
            timezone_offset: chartData.timezoneOffset,
            latitude: chartData.latitude,
            longitude: chartData.longitude,
            music_genre: chartData.musicGenre
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullText = '';
        
        // Clear loading message
        analysisContainer.innerHTML = '';
        
        function processStream() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    // Convert markdown to HTML if we have marked.js
                    if (window.marked && fullText) {
                        analysisContainer.innerHTML = marked.parse(fullText);
                    }
                    // Re-add music suggestion placeholder and trigger loading
                    const musicPlaceholder = document.createElement('div');
                    musicPlaceholder.id = 'music-suggestion-placeholder';
                    const chartType = chartData.pageType === 'chart' ? 'daily' : (chartData.pageType === 'full-chart' ? 'natal' : 'live-mas');
                    musicPlaceholder.setAttribute('data-chart-type', chartType);
                    analysisContainer.appendChild(musicPlaceholder);
                    
                    // Trigger music suggestion loading if function exists
                    if (typeof loadMusicSuggestion === 'function' && window.chartDataForMusic) {
                        loadMusicSuggestion(window.chartDataForMusic, chartType);
                    }
                    return;
                }
                
                // Decode the chunk
                buffer += decoder.decode(value, { stream: true });
                
                // Process complete SSE messages
                const lines = buffer.split('\n');
                buffer = lines.pop() || ''; // Keep incomplete line in buffer
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.substring(6));
                            
                            if (data.chunk) {
                                fullText += data.chunk;
                                // Display raw text while streaming
                                analysisContainer.textContent = fullText;
                            } else if (data.done) {
                                // Convert to HTML when done
                                if (window.marked && fullText) {
                                    analysisContainer.innerHTML = marked.parse(fullText);
                                }
                                // Re-add music suggestion placeholder and trigger loading
                                const musicPlaceholder = document.createElement('div');
                                musicPlaceholder.id = 'music-suggestion-placeholder';
                                const chartType = chartData.pageType === 'chart' ? 'daily' : (chartData.pageType === 'full-chart' ? 'natal' : 'live-mas');
                                musicPlaceholder.setAttribute('data-chart-type', chartType);
                                analysisContainer.appendChild(musicPlaceholder);
                                
                                // Trigger music suggestion loading if function exists
                                if (typeof loadMusicSuggestion === 'function' && window.chartDataForMusic) {
                                    loadMusicSuggestion(window.chartDataForMusic, chartType);
                                }
                            } else if (data.error) {
                                console.error('Streaming error:', data.error);
                                analysisContainer.innerHTML = '<p>☕ The AI astrologer is taking a cosmic tea break. Trust your intuition today! 🔮</p>';
                                return;
                            }
                        } catch (e) {
                            console.error('Error parsing SSE data:', e);
                        }
                    }
                }
                
                processStream();
            }).catch(err => {
                console.error('Stream reading error:', err);
                analysisContainer.innerHTML = '<p>☕ The AI astrologer is taking a cosmic tea break. Trust your intuition today! 🔮</p>';
            });
        }
        
        processStream();
    })
    .catch(err => {
        console.error('Fetch error:', err);
        analysisContainer.innerHTML = '<p>☕ The AI astrologer is taking a cosmic tea break. Trust your intuition today! 🔮</p>';
    });
    }
})();
