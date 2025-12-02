# LaunchDarkly Integration

This document explains the LaunchDarkly feature flag integration in the Astro application.

## Overview

The application uses LaunchDarkly to control whether the interactive chart wheel visualization is displayed on the full natal chart page. This allows for:

- **Gradual feature rollouts**: Enable the chart wheel for specific IP ranges or percentages
- **Geographic testing**: Target users from specific regions or networks
- **Emergency disable**: Quickly turn off the feature if issues arise
- **IP-based targeting**: Show the feature to users from specific networks or locations

## Feature Flag Configuration

### Flag Details
- **Flag Name**: `show-new-chart`
- **Type**: Boolean
- **Default Value**: `false` (safe fallback)
- **Purpose**: Controls display of the interactive chart wheel visualization

### Setup in LaunchDarkly Dashboard

1. Create a new boolean flag called `show-new-chart`
2. Set the default value to `false` for safety
3. Configure targeting rules as needed:
   - **IP range targeting**: Target specific IP address ranges
   - **Geographic targeting**: Use IP geolocation for regional rollouts
   - **Percentage rollouts**: Enable for X% of traffic
   - **Custom rules**: Combine IP attributes with other conditions
4. Set variations:
   - `true`: Show chart wheel
   - `false`: Hide chart wheel

## Environment Configuration

### Required Environment Variables

```bash
# LaunchDarkly SDK key (get from your LaunchDarkly project settings)
LAUNCHDARKLY_SDK_KEY=sdk-your-key-here
```

### Local Development

For local development without LaunchDarkly:

```bash
# The app will use fallback values (feature disabled) if no SDK key is set
unset LAUNCHDARKLY_SDK_KEY
```

## Implementation Details

### Service Layer (`launchdarkly_service.py`)

The `LaunchDarklyService` class handles:
- Client initialization with error handling
- Feature flag evaluation with fallback values
- IP-based user context creation
- Graceful degradation when LaunchDarkly is unavailable

```python
from launchdarkly_service import should_show_chart_wheel

# Check if chart wheel should be shown for a user's IP
show_chart = should_show_chart_wheel(user_ip)
```

### Route Integration (`routes.py`)

The `/full-chart` route:
1. Extracts the user's IP address from request headers
2. Evaluates the `show-new-chart` flag for that IP
3. Passes the flag result to the template

```python
user_ip = get_user_ip()
show_chart_wheel = should_show_chart_wheel(user_ip)
return render_template('full_chart.html', 
                      chart_data=chart_data, 
                      show_chart_wheel=show_chart_wheel)
```

### Template Integration (`templates/full_chart.html`)

The template conditionally renders:
- Chart wheel container and canvas
- Chart wheel JavaScript
- Chart legend and interactions

```html
{% if show_chart_wheel %}
<div class="chart-wheel-container">
    <!-- Chart wheel visualization -->
</div>
{% endif %}
```

## User Experience

### When Feature is Enabled (`show-new-chart: true`)
- Users see an interactive chart wheel visualization
- Chart wheel JavaScript loads and renders planetary positions
- Legend shows planet symbols and aspect lines
- Fully interactive astrological chart display

### When Feature is Disabled (`show-new-chart: false`)
- Chart wheel section is hidden
- No chart wheel JavaScript loads (faster page load)
- Users see text-based planetary information only
- All other functionality remains unchanged

## Testing

### Unit Tests
```bash
# Run LaunchDarkly service tests
python -m pytest tests/test_launchdarkly_service.py -v

# Run integration tests
python -m pytest tests/test_frontend.py::TestLaunchDarklyIntegration -v
```


### Manual Testing

1. **With LaunchDarkly enabled**:
   ```bash
   export LAUNCHDARKLY_SDK_KEY=your-key-here
   flask run
   ```

2. **Without LaunchDarkly**:
   ```bash
   unset LAUNCHDARKLY_SDK_KEY
   flask run
   ```

3. Test the `/full-chart` endpoint and verify chart wheel visibility

## Monitoring and Debugging

### Logs
The application logs LaunchDarkly events:
- Client initialization status
- Flag evaluation results with IP addresses
- Error conditions and fallbacks

```bash
# Check logs for LaunchDarkly events
grep -i "launchdarkly\|show-new-chart" app.log
```

### Common Issues

1. **SDK Key not set**:
   - Symptoms: Feature always disabled, warnings in logs
   - Solution: Set `LAUNCHDARKLY_SDK_KEY` environment variable

2. **Client initialization failure**:
   - Symptoms: Flags always return default values
   - Check: Network connectivity, SDK key validity

3. **Flag not found**:
   - Symptoms: Always returns default value
   - Check: Flag exists in LaunchDarkly with correct name

### Fallback Behavior

The implementation is designed to fail gracefully:
- If LaunchDarkly is unavailable → feature disabled (safe default)
- If flag evaluation fails → feature disabled
- If client can't initialize → feature disabled

This ensures the application always works, even if LaunchDarkly has issues.

## Best Practices

1. **Start with feature disabled**: Set default to `false` for new features
2. **Gradual rollout**: Use percentage targeting to slowly enable
3. **Monitor metrics**: Track engagement and error rates by IP/region
4. **Test both states**: Ensure app works with feature on/off
5. **Document changes**: Update this README when adding new flags
6. **Privacy considerations**: Be mindful of IP-based tracking regulations
7. **Clean up**: Remove old flags and code when features are fully launched

## Future Enhancements

Potential improvements to the LaunchDarkly integration:

1. **Geographic attributes**: Send country/region data for location-based targeting
2. **Multiple flags**: Control other features (animations, AI analysis, etc.)
3. **Metrics tracking**: Send custom events to LaunchDarkly
4. **ISP/Organization targeting**: Target based on IP ownership data
5. **Time-based rules**: Combine IP targeting with time-of-day conditions
6. **Flag management**: Automated flag cleanup and lifecycle management