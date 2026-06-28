(function () {
    function readConfig() {
        var configEl = document.getElementById('chart-page-config');
        if (!configEl) {
            return null;
        }

        try {
            return JSON.parse(configEl.textContent || '{}');
        } catch (err) {
            return null;
        }
    }

    var config = readConfig();
    if (!config) {
        return;
    }

    var otherGenre = String(config.otherGenre || '').trim();
    var genreSelection = String(config.musicGenre || '').trim();
    var effectiveGenre = (genreSelection === 'other' && otherGenre)
        ? otherGenre
        : (genreSelection || 'any');

    var chartData = {
        birthDate: String(config.birthDate || ''),
        birthTime: String(config.birthTime || ''),
        timezoneOffset: String(config.timezoneOffset || ''),
        latitude: String(config.latitude || ''),
        longitude: String(config.longitude || ''),
        musicGenre: effectiveGenre,
        personality: String(config.personality || 'default')
    };

    window.chartDataForStreaming = {
        pageType: 'chart',
        birthDate: chartData.birthDate,
        birthTime: chartData.birthTime,
        timezoneOffset: chartData.timezoneOffset,
        latitude: chartData.latitude,
        longitude: chartData.longitude,
        musicGenre: chartData.musicGenre,
        personality: chartData.personality
    };

    window.chartDataForMusic = {
        birthDate: chartData.birthDate,
        birthTime: chartData.birthTime,
        timezoneOffset: chartData.timezoneOffset,
        latitude: chartData.latitude,
        longitude: chartData.longitude,
        musicGenre: chartData.musicGenre,
        personality: chartData.personality
    };

    window.birthdayCelebration = {
        isBirthday: Boolean(config.isBirthday)
    };

    if (config.streaming) {
        document.body.dataset.streaming = 'true';
    }

    // Keep the home page and "ask the stars" flow in sync with this chart.
    try {
        var rawOtherGenre = String(config.otherGenre || '').trim();
        var isOther = Boolean(rawOtherGenre);
        var storageData = {
            birth_date: chartData.birthDate,
            birth_time: chartData.birthTime,
            timezone_offset: chartData.timezoneOffset,
            latitude: chartData.latitude,
            longitude: chartData.longitude,
            personality: chartData.personality,
            music_genre: isOther ? 'other' : (String(config.musicGenre || '').trim() || 'any'),
            other_genre: isOther ? rawOtherGenre : ''
        };
        localStorage.setItem('astro_form_data', JSON.stringify({ data: storageData, timestamp: Date.now() }));
        if (storageData.timezone_offset) {
            localStorage.setItem('timezone_offset', storageData.timezone_offset);
        }
    } catch (e) {
        // Ignore storage failures (private mode, quotas, etc.).
    }

    window.askPrompt = function askPrompt(prompt) {
        var askInput = document.getElementById('askInput');
        if (!askInput) {
            return;
        }
        askInput.value = prompt;
        window.sendQuestion();
    };

    window.sendQuestion = function sendQuestion() {
        var askInput = document.getElementById('askInput');
        if (!askInput) {
            return;
        }

        var question = askInput.value;
        if (!question || !question.trim()) {
            return;
        }

        var form = document.createElement('form');
        form.method = 'POST';
        form.action = String(config.askAnythingPath || '/ask-anything');

        var fields = {
            question_prompt: question,
            birth_date: chartData.birthDate,
            birth_time: chartData.birthTime,
            timezone_offset: chartData.timezoneOffset,
            latitude: chartData.latitude,
            longitude: chartData.longitude,
            personality: chartData.personality
        };

        for (var name in fields) {
            if (!Object.prototype.hasOwnProperty.call(fields, name)) {
                continue;
            }
            var input = document.createElement('input');
            input.type = 'hidden';
            input.name = name;
            input.value = String(fields[name]);
            form.appendChild(input);
        }

        document.body.appendChild(form);
        form.submit();
    };

    window.submitForm = function submitForm(event, action) {
        event.preventDefault();
        var navForm = document.getElementById('navForm');
        if (!navForm) {
            return;
        }
        navForm.action = action;
        navForm.submit();
    };
})();
