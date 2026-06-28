/**
 * Client-side streaming for horoscope analysis
 * Fetches and displays AI-generated content as it streams in
 */

(function() {
    'use strict';

    var STREAMING_INDICATOR_MARKUP =
        '<span class="streaming-indicator__icon" aria-hidden="true">✦</span>' +
        '<div class="streaming-indicator__bars" aria-hidden="true">' +
            '<span class="streaming-indicator__bar"></span>' +
            '<span class="streaming-indicator__bar"></span>' +
            '<span class="streaming-indicator__bar"></span>' +
            '<span class="streaming-indicator__bar"></span>' +
        '</div>' +
        '<span class="sr-only">More content is still streaming in</span>';

    function createStreamingIndicator() {
        var indicator = document.createElement('div');
        indicator.className = 'streaming-indicator';
        indicator.innerHTML = STREAMING_INDICATOR_MARKUP;
        return indicator;
    }

    function hydrateStreamingIndicator(streamingIndicator) {
        if (!streamingIndicator) {
            return;
        }

        // Remove aria-hidden from server-rendered containers so the sr-only text is announced.
        streamingIndicator.removeAttribute('aria-hidden');

        // Keep server-rendered indicator containers, but normalize inner markup.
        if (!streamingIndicator.querySelector('.streaming-indicator__bars')) {
            streamingIndicator.innerHTML = STREAMING_INDICATOR_MARKUP;
        }
    }

    function ensureStreamingSurface(analysisContainer) {
        var streamedContent = document.getElementById('analysisStreamContent');
        if (!streamedContent) {
            streamedContent = document.createElement('div');
            streamedContent.id = 'analysisStreamContent';
            streamedContent.className = 'streaming-analysis-text';
            analysisContainer.insertBefore(streamedContent, analysisContainer.firstChild);
        }

        var streamingIndicator = document.getElementById('analysisStreamIndicator');
        if (!streamingIndicator) {
            streamingIndicator = createStreamingIndicator();
            streamingIndicator.id = 'analysisStreamIndicator';
            analysisContainer.appendChild(streamingIndicator);
        } else {
            hydrateStreamingIndicator(streamingIndicator);
        }

        return {
            streamedContent: streamedContent,
            streamingIndicator: streamingIndicator
        };
    }
    
    // Wait for DOM to be fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initStreaming);
    } else {
        initStreaming();
    }
    
    /**
     * Finalize streaming: convert markdown and trigger music suggestion
     */
    function finalizeStream(analysisContainer, streamedContent, streamingIndicator, fullText, chartData) {
        // Convert markdown to HTML if we have marked.js
        if (window.marked && fullText) {
            streamedContent.innerHTML = marked.parse(fullText);
        } else {
            streamedContent.textContent = fullText;
        }
        streamedContent.style.whiteSpace = 'normal';
        if (streamingIndicator && streamingIndicator.parentNode) {
            streamingIndicator.parentNode.removeChild(streamingIndicator);
        }
        analysisContainer.setAttribute('aria-busy', 'false');

        // Only horoscope/full-chart pages load the async music suggestion.
        if (chartData.pageType === 'chart' || chartData.pageType === 'full-chart') {
            let musicPlaceholder = document.getElementById('music-suggestion-placeholder');
            if (!musicPlaceholder) {
                musicPlaceholder = document.createElement('div');
                musicPlaceholder.id = 'music-suggestion-placeholder';
                analysisContainer.appendChild(musicPlaceholder);
            }
            const chartType = chartData.pageType === 'chart' ? 'daily' : 'natal';
            musicPlaceholder.setAttribute('data-chart-type', chartType);

            if (typeof loadMusicSuggestion === 'function' && window.chartDataForMusic) {
                loadMusicSuggestion(window.chartDataForMusic, chartType);
            }
        }
    }
    
    function initStreaming() {
        // Check if we're on a streaming-enabled page
        const streamingEnabled = document.body.dataset.streaming === 'true';
        if (!streamingEnabled) {
            return;
        }
        
        const analysisContainer = document.getElementById('analysisContent');
        const chartData = window.chartDataForStreaming;
        let fullText = '';
        let hasFinalized = false;

        function safeFinalizeStream() {
            if (hasFinalized) {
                return;
            }
            hasFinalized = true;
            finalizeStream(
                analysisContainer,
                streamingSurface.streamedContent,
                streamingSurface.streamingIndicator,
                fullText,
                chartData
            );
        }
        
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

        var streamingSurface = ensureStreamingSurface(analysisContainer);

        analysisContainer.setAttribute('aria-busy', 'true');

        streamingSurface.streamedContent.textContent = '';
        streamingSurface.streamedContent.style.whiteSpace = 'pre-wrap';
        if (streamingSurface.streamingIndicator) {
            streamingSurface.streamingIndicator.setAttribute('aria-hidden', 'true');
        }
    
        // Determine endpoint based on page type
        let endpoint;
        if (chartData.pageType === 'chart') {
            endpoint = '/stream-chart-analysis';
        } else if (chartData.pageType === 'full-chart') {
            endpoint = '/stream-full-chart-analysis';
        } else if (chartData.pageType === 'live-mas') {
            endpoint = '/stream-live-mas-analysis';
        } else if (chartData.pageType === 'ask-anything') {
            endpoint = '/stream-ask-anything';
        } else {
            console.error('Unknown page type:', chartData.pageType);
            analysisContainer.setAttribute('aria-busy', 'false');
            return;
        }

        const requestPayload = chartData.pageType === 'ask-anything'
            ? {
                question: chartData.question,
                birth_date: chartData.birthDate,
                birth_time: chartData.birthTime,
                timezone_offset: chartData.timezoneOffset,
                latitude: chartData.latitude,
                longitude: chartData.longitude,
                personality: chartData.personality || 'default'
            }
            : {
                birth_date: chartData.birthDate,
                birth_time: chartData.birthTime,
                timezone_offset: chartData.timezoneOffset,
                latitude: chartData.latitude,
                longitude: chartData.longitude,
                music_genre: chartData.musicGenre,
                personality: chartData.personality || 'default'
            };
    
        // Start streaming
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestPayload)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            function processStream() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        safeFinalizeStream();
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
                                    streamingSurface.streamedContent.textContent = fullText;
                                } else if (data.done) {
                                    safeFinalizeStream();
                                } else if (data.error) {
                                    console.error('Streaming error:', data.error);
                                    analysisContainer.innerHTML = '<p>☕ The AI astrologer is taking a cosmic tea break. Trust your intuition today! 🔮</p>';
                                    analysisContainer.setAttribute('aria-busy', 'false');
                                    reader.cancel();
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
                    analysisContainer.setAttribute('aria-busy', 'false');
                    reader.cancel();
                });
            }

            processStream();
        })
        .catch(err => {
            console.error('Fetch error:', err);
            analysisContainer.innerHTML = '<p>☕ The AI astrologer is taking a cosmic tea break. Trust your intuition today! 🔮</p>';
            analysisContainer.setAttribute('aria-busy', 'false');
        });
    }
})();
