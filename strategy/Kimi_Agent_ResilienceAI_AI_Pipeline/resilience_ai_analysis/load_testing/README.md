# ResilienceAI Load Testing Framework

Comprehensive load testing framework for ResilienceAI, supporting performance testing, stress testing, spike testing, and endurance testing.

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Running Tests

#### Smoke Test (Quick Validation)
```bash
locust -f locustfile.py --host=http://localhost:8000 --users=10 --run-time=2m --headless
```

#### Load Test
```bash
locust -f locustfile.py --host=http://localhost:8000 --users=200 --run-time=30m --html=report.html
```

#### k6 Load Test
```bash
k6 run k6/load_test.js -e BASE_URL=http://localhost:8000
```

#### Stress Test
```bash
locust -f locustfile.py --host=http://localhost:8000 --users=1000 --run-time=1h
```

#### Spike Test
```bash
k6 run k6/spike_test.js -e BASE_URL=http://localhost:8000
```

## Project Structure

```
load_testing/
├── locustfile.py              # Main Locust test file
├── k6/                        # k6 test scripts
│   ├── load_test.js
│   ├── stress_test.js
│   ├── spike_test.js
│   └── smoke_test.js
├── scenarios/                 # Test scenarios
│   ├── user_profiles.py
│   └── test_data.py
├── monitoring/                # Monitoring & metrics
│   ├── metrics.py
│   └── prometheus_exporter.py
├── analysis/                  # Analysis tools
│   ├── bottleneck_detection.py
│   ├── capacity_planning.py
│   └── trend_analysis.py
├── reporting/                 # Report generation
│   └── report_generator.py
├── ci/                        # CI/CD workflows
│   └── github-workflows/
│       └── load-tests.yml
├── config/                    # Configuration files
│   ├── benchmarks.yaml
│   ├── thresholds.yaml
│   └── test_scenarios.yaml
└── requirements.txt
```

## Test Types

### 1. Smoke Test
- **Purpose**: Quick validation that system is working
- **Duration**: 2 minutes
- **Users**: 10
- **Command**: `locust -f locustfile.py --users=10 --run-time=2m --headless`

### 2. Load Test
- **Purpose**: Validate performance under expected load
- **Duration**: 30 minutes
- **Users**: 200
- **Target**: 100 RPS

### 3. Stress Test
- **Purpose**: Find system breaking points
- **Duration**: 1 hour
- **Users**: Up to 2000
- **Stages**: Gradual ramp-up to extreme load

### 4. Spike Test
- **Purpose**: Test sudden traffic changes
- **Duration**: 15 minutes
- **Spike**: 20x normal load
- **Tool**: k6

### 5. Endurance Test
- **Purpose**: Detect memory leaks and stability issues
- **Duration**: 12 hours
- **Users**: 200
- **Monitoring**: Memory growth, error rate trends

## User Profiles

The framework simulates different user types:

1. **API Consumer** (50%): Regular prediction requests
2. **Batch Processor** (25%): Batch prediction jobs
3. **Model Manager** (15%): Model deployment and management
4. **Streaming Client** (10%): Real-time prediction streams

## Performance Benchmarks

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| p50 Response Time | < 100ms | 200ms | 500ms |
| p95 Response Time | < 500ms | 1000ms | 2000ms |
| p99 Response Time | < 1000ms | 2000ms | 5000ms |
| Error Rate | < 0.1% | 1% | 5% |
| Throughput | > 100 RPS | 50 RPS | 20 RPS |

## CI/CD Integration

The framework includes GitHub Actions workflows for:
- Smoke tests on PR
- Load tests on main branch
- Weekly stress tests
- Monthly spike tests
- Quarterly endurance tests

## Monitoring

Metrics are exposed in Prometheus format on port 9090:
- `loadtest_requests_total`
- `loadtest_request_duration_seconds`
- `loadtest_errors_total`
- `loadtest_active_users`
- `loadtest_current_rps`

## Report Generation

Generate HTML reports with:
```bash
python reporting/report_generator.py --results results.json
```

## Distributed Testing

Run distributed tests with multiple workers:

```bash
# Start master
locust -f locustfile.py --master --expect-workers=4

# Start workers (on different machines)
locust -f locustfile.py --worker --master-host=<master-ip>
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOAD_TEST_HOST` | Target API host | `http://localhost:8000` |
| `LOAD_TEST_USERS` | Number of concurrent users | `100` |
| `LOAD_TEST_DURATION` | Test duration | `10m` |
| `PROMETHEUS_URL` | Prometheus endpoint | `http://localhost:9090` |

## Troubleshooting

### High Error Rates
- Check target system health
- Verify network connectivity
- Review application logs

### Low Throughput
- Increase spawn rate
- Check CPU/memory usage
- Verify database connection pools

### Connection Timeouts
- Increase timeout values
- Check firewall settings
- Verify load balancer health

## Contributing

1. Add new test scenarios in `scenarios/`
2. Update benchmarks in `config/benchmarks.yaml`
3. Add analysis tools in `analysis/`
4. Update documentation

## License

MIT License
