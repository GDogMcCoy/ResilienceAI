import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Custom metrics
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');

// Stress test configuration - gradually increase to breaking point
export const options = {
    stages: [
        { duration: '5m', target: 100 },   // Baseline
        { duration: '5m', target: 250 },   // Light stress
        { duration: '5m', target: 500 },   // Medium stress
        { duration: '5m', target: 1000 },  // Heavy stress
        { duration: '5m', target: 2000 },  // Extreme stress
        { duration: '10m', target: 2000 }, // Sustained peak
        { duration: '5m', target: 0 },     // Recovery
    ],
    thresholds: {
        http_req_duration: ['p(95)<5000'],  // Relaxed threshold for stress
        http_req_failed: ['rate<0.10'],      // Allow up to 10% errors
    },
    noConnectionReuse: true,  // Create new connections for more stress
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const MODEL_IDS = ['model_1', 'model_2', 'model_3', 'model_4', 'model_5', 
                   'model_6', 'model_7', 'model_8', 'model_9', 'model_10'];

export function setup() {
    console.log('Starting stress test - looking for breaking points');
    
    // Verify target is up
    const healthCheck = http.get(`${BASE_URL}/health`);
    check(healthCheck, {
        'target is healthy': (r) => r.status === 200,
    });
    
    return { startTime: Date.now() };
}

export default function (data) {
    const modelId = randomItem(MODEL_IDS);
    
    // High-frequency prediction requests
    const payload = JSON.stringify({
        model_id: modelId,
        features: {
            feature_1: Math.random() * 100,
            feature_2: Math.random() * 100,
            feature_3: Math.random() * 100,
            feature_4: Math.random() * 100,
            feature_5: Math.random() * 100,
        },
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
    
    // Check for different response scenarios
    check(response, {
        'response received': (r) => r.status !== 0,
        'success or rate limited': (r) => r.status === 200 || r.status === 429,
    });
    
    // Log errors at high load
    if (response.status >= 500) {
        console.log(`Server error at high load: ${response.status}`);
    }
    
    // Minimal sleep for stress
    sleep(0.1);
}

export function handleSummary(data) {
    // Find the breaking point (where error rate spikes)
    const errorRate = data.metrics.http_req_failed ? data.metrics.http_req_failed.values.rate : 0;
    const maxVUs = data.metrics.vus_max ? data.metrics.vus_max.value : 0;
    
    let breakingPoint = 'Not reached';
    if (errorRate > 0.05) {
        breakingPoint = `Approximately ${Math.round(maxVUs * 0.8)} VUs`;
    }
    
    return {
        'stress_test_summary.json': JSON.stringify({
            breaking_point_estimate: breakingPoint,
            max_vus: maxVUs,
            total_requests: data.metrics.http_reqs ? data.metrics.http_reqs.values.count : 0,
            avg_response_time: data.metrics.http_req_duration ? data.metrics.http_req_duration.values.avg : 0,
            p95_response_time: data.metrics.http_req_duration ? data.metrics.http_req_duration.values['p(95)'] : 0,
            error_rate: errorRate,
            test_duration_minutes: data.state.testRunDurationMs / 1000 / 60,
        }, null, 2),
    };
}
