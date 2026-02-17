# ResilienceAI Weather Integration Module

Comprehensive weather integration for ResilienceAI platform with NOAA NWS API support, severe weather alert processing, real-time feeds, and impact modeling.

## Features

- **Enhanced NOAA Client**: Async-capable client with intelligent caching and rate limiting
- **Alert Processing Pipeline**: CAP XML parsing, geocoding, severity scoring
- **Real-Time Feeds**: HTTP polling and WebSocket support for live weather data
- **Impact Modeling**: Population, infrastructure, and economic impact estimation
- **Visualization**: Maps, timelines, charts, and dashboards
- **Agent Integration**: Weather agent for ResilienceAI orchestrator
- **Historical Analysis**: Trend detection and pattern analysis

## Installation

```bash
pip install -r requirements.txt
```

### Dependencies

```
aiohttp>=3.8.0
requests>=2.28.0
shapely>=2.0.0
geopandas>=0.13.0
pyproj>=3.6.0
python-dateutil>=2.8.0
```

## Quick Start

```python
from src.weather import EnhancedNOAAClient, WeatherAgent

# Initialize NOAA client
client = EnhancedNOAAClient(
    cache_dir='./weather_cache',
    cache_ttl=300  # 5 minutes
)

# Get active alerts for a state
alerts = client.get_active_alerts(state='MO')

# Get alerts for a specific county
county_alerts = client.get_alerts_for_county('Boone', 'MO')

# Correlate with vulnerability
result = client.correlate_with_vulnerability(
    county_fips='29019',
    county_name='Boone',
    state='MO',
    vulnerability_score=0.7,
    population=180000
)

print(f"Risk Level: {result['risk_assessment']['level']}")
print(f"Composite Score: {result['risk_assessment']['composite_score']}")
```

## Module Structure

```
weather/
├── __init__.py              # Module exports
├── enhanced_noaa_client.py  # Enhanced NOAA API client
├── alert_processor.py       # Alert processing pipeline
├── realtime_feed.py         # Real-time feed management
├── impact_model.py          # Weather impact modeling
├── weather_viz.py           # Visualization components
├── weather_agent.py         # Agent integration
└── historical_weather.py    # Historical analysis
```

## Usage Examples

### 1. Enhanced NOAA Client

```python
from src.weather import EnhancedNOAAClient, AlertSeverity

client = EnhancedNOAAClient()

# Get high-severity alerts
alerts = client.get_active_alerts(
    state='MO',
    severity=AlertSeverity.SEVERE
)

# Get forecast for a location
forecast = client.get_point_forecast(38.9517, -92.3341)
for period in forecast.periods[:3]:
    print(f"{period['name']}: {period['detailedForecast']}")

# Get nearest weather station
station = client.get_nearest_station(38.9517, -92.3341)
obs = client.get_latest_observation(station.station_id)
print(f"Temperature: {obs.temperature}°C")
```

### 2. Alert Processing

```python
from src.weather import AlertProcessor

processor = AlertProcessor()

# Start processing loop
async def main():
    await processor.start()
    
    # Ingest an alert
    await processor.ingest_alert(alert)
    
    # Get processed alerts
    processed = processor.get_active_processed_alerts()

asyncio.run(main())
```

### 3. Real-Time Feeds

```python
from src.weather import RealtimeFeedManager, NOAACAPFeed

manager = RealtimeFeedManager()

# Add NOAA CAP feed
cap_feed = NOAACAPFeed(poll_interval=60)
feed_id = manager.add_feed(cap_feed)

# Start feed
async def main():
    await manager.start_feed(feed_id)
    
    # Get feed status
    status = manager.get_feed_status(feed_id)
    print(f"Messages received: {status['metrics']['messages_received']}")

asyncio.run(main())
```

### 4. Impact Modeling

```python
from src.weather import WeatherImpactModel

model = WeatherImpactModel()

county_data = {
    'population': 180000,
    'vulnerability_score': 0.7,
    'critical_facilities': [
        {'name': 'Hospital A', 'type': 'hospital', 'capacity': 300},
        {'name': 'Fire Station 1', 'type': 'emergency_services'}
    ]
}

impact = model.calculate_impact(alert, county_data)
print(model.get_impact_summary(impact))
```

### 5. Visualization

```python
from src.weather import WeatherDashboard, WeatherChartGenerator

# Create dashboard
dashboard = WeatherDashboard()
data = dashboard.create_dashboard_data(alerts, county_name='Boone', state='MO')

# Create charts
charts = WeatherChartGenerator()
severity_chart = charts.create_severity_chart(alerts)
event_chart = charts.create_event_type_chart(alerts)
```

### 6. Weather Agent

```python
from src.weather import WeatherAgent

agent = WeatherAgent()

# Execute actions
result = agent.execute('get_active_alerts', {'state': 'MO'})
result = agent.execute('assess_impact', {
    'county_data': county_data,
    'alert': alert.to_dict()
})

# Generate summary
summary = agent.generate_weather_summary('Boone', 'MO')
print(summary)
```

### 7. Historical Analysis

```python
from src.weather import HistoricalWeatherReport

report = HistoricalWeatherReport()

# Generate historical report
historical = report.generate_report('Boone', 'MO', days=365)

# Get risk assessment
risk = report.generate_risk_assessment('Boone', 'MO')
print(f"Risk Level: {risk['overall_risk_level']}")
```

## Configuration

```python
# config.py
WEATHER_CONFIG = {
    "noaa_api": {
        "base_url": "https://api.weather.gov",
        "cache_ttl": 300,
        "rate_limit_delay": 0.5,
        "max_retries": 3
    },
    "realtime_feeds": {
        "poll_interval": 60,
        "reconnect_interval": 30
    },
    "geocoding": {
        "county_boundaries_path": "data/county_boundaries.shp",
        "facility_data_path": "data/critical_facilities.shp"
    }
}
```

## API Reference

### EnhancedNOAAClient

| Method | Description |
|--------|-------------|
| `get_active_alerts()` | Get active weather alerts |
| `get_alerts_for_county()` | Get alerts for specific county |
| `get_point_forecast()` | Get forecast for location |
| `get_nearest_station()` | Get nearest weather station |
| `correlate_with_vulnerability()` | Correlate alerts with vulnerability |
| `clear_cache()` | Clear cached data |

### AlertProcessor

| Method | Description |
|--------|-------------|
| `start()` | Start processing loop |
| `stop()` | Stop processing loop |
| `ingest_alert()` | Ingest alert for processing |
| `get_processed_alert()` | Get processed alert by ID |

### WeatherImpactModel

| Method | Description |
|--------|-------------|
| `calculate_impact()` | Calculate comprehensive impact |
| `get_impact_summary()` | Get human-readable summary |

## Testing

```bash
# Run tests
pytest tests/test_weather/

# Run with coverage
pytest --cov=src.weather tests/test_weather/
```

## License

MIT License - See LICENSE file for details
