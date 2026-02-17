import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';
import { randomIntBetween, randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Custom metrics
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');
const requestsPerSecond = new Counter('requests_per_second');
const activeUsers = Gauge('active_users');

// Load test configuration
export const options = {
    stages: [
        { duration: '2m', target: 50 },   // Ramp up
        { duration: '5m', target: 50 },   // Steady state
        { duration: '2m', target: 100 },  // Ramp up
        { duration: '5m', target: 100 },  // Steady state
        { duration: '2m', target: 200 },  // Peak load
        { duration: '5m', target: 200 },  // Sustained peak
        { duration: '2m', target: 0 },    // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<2000'],  // 95% under 2s
        http_req_failed: ['rate<0.05'],      // Error rate < 5%
        error_rate: ['rate<0.05'],
        'response_time': ['p(95)<2000'],
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const MODEL_IDS = ['model_1', 'model_2', 'model_3', 'model_4', 'model_5', 
                   'model_6', 'model_7', 'model_8', 'model_9', 'model_10'];

export function setup() {
    // Setup code - runs once before all VUs
    console.log(`Starting load test against ${BASE_URL}`);
    
    // Health check
    const healthCheck = http.get(`${BASE_URL}/health`);
    check(healthCheck, {
        'health check passes': (r) => r.status === 200,
    });
    
    return { startTime: new Date().toISOString() };
}

export default function (data) {
    activeUsers.add(1);
    
    group('Prediction Workflow', () => {
        // Make prediction request
        const modelId = randomItem(MODEL_IDS);
        const payload = JSON.stringify({
            model_id: modelId,
            features: {
                feature_1: Math.random() * 100,
                feature_2: Math.random() * 100,
                feature_3: Math.random() * 100,
                feature_4: Math.random() * 100,
                feature_5: Math.random() * 100,
                feature_6: Math.random() * 100,
                feature_7: Math.random() * 100,
                feature_8: Math.random() * 100,
                feature_9: Math.random() * 100,
                feature_10: Math.random() * 100,
            },
            request_id: `req_${randomIntBetween(100000, 999999)}`,
        });
        
        const params = {
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: '30s',
        };
        
        const response = http.post(`${BASE_URL}/api/v1/predict`, payload, params);
        
        // Record metrics
        responseTime.add(response.timings.duration);
        errorRate.add(response.status >= 400 ? 1 : 0);
        requestsPerSecond.add(1);
        
        // Assertions
        const checkResult = check(response, {
            'predict status is 200': (r) => r.status === 200,
            'predict response time < 5s': (r) => r.timings.duration < 5000,
            'predict has prediction': (r) => r.json('prediction') !== undefined,
        });
        
        if (!checkResult) {
            console.log(`Predict failed: ${response.status} - ${response.body}`);
        }
    });
    
    // Random think time
    sleep(randomIntBetween(1, 5));
    
    group('Health Check', () => {
        const healthResponse = http.get(`${BASE_URL}/health`);
        
        check(healthResponse, {
            'health status is 200': (r) => r.status === 200,
        });
    });
    
    sleep(randomIntBetween(1, 3));
}

export function teardown(data) {
    // Teardown code - runs once after all VUs complete
    console.log(`Load test completed. Started at: ${data.startTime}`);
}

export function handleSummary(data) {
    return {
        'load_test_summary.json': JSON.stringify({
            metrics: data.metrics,
            root_group: data.root_group,
            test_run_duration: data.state.testRunDurationMs,
        }, null, 2),
        'load_test_summary.html': generateHTMLReport(data),
    };
}

function generateHTMLReport(data) {
    return `
<!DOCTYPE html>
<html>
<head>
    <title>k6 Load Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        .metric { margin: 10px 0; padding: 10px; background: #f5f5f5; }
        .passed { color: green; }
        .failed { color: red; }
    </style>
</head>
<body>
    <h1>k6 Load Test Report</h1>
    <div class="metric">
        <strong>Test Duration:</strong> ${(data.state.testRunDurationMs / 1000 / 60).toFixed(2)} minutes
    </div>
    <div class="metric">
        <strong>Total Requests:</strong> ${data.metrics.http_reqs ? data.metrics.http_reqs.values.count : 'N/A'}
    </div>
    <div class="metric">
        <strong>Avg Response Time:</strong> ${data.metrics.http_req_duration ? data.metrics.http_req_duration.values.avg.toFixed(2) : 'N/A'} ms
    </div>
    <div class="metric">
        <strong>p95 Response Time:</strong> ${data.metrics.http_req_duration ? data.metrics.http_req_duration.values['p(95)'].toFixed(2) : 'N/A'} ms
    </div>
    <div class="metric">
        <strong>Error Rate:</strong> ${data.metrics.http_req_failed ? (data.metrics.http_req_failed.values.rate * 100).toFixed(2) : 'N/A'}%
    </div>
</body>
</html>
    `;
}
