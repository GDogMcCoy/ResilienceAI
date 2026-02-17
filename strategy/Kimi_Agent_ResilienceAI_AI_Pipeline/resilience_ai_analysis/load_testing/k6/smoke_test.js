import http from 'k6/http';
import { check, group } from 'k6';

// Smoke test - quick validation that system is working
export const options = {
    vus: 5,              // Very few virtual users
    duration: '1m',      // Short duration
    thresholds: {
        http_req_duration: ['p(95)<1000'],  // Strict threshold
        http_req_failed: ['rate<0.01'],      // Almost no errors allowed
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
    group('Health Check', () => {
        const healthResponse = http.get(`${BASE_URL}/health`);
        check(healthResponse, {
            'health status is 200': (r) => r.status === 200,
            'health response time < 500ms': (r) => r.timings.duration < 500,
        });
    });

    group('API Endpoints', () => {
        // Test prediction endpoint
        const predictPayload = JSON.stringify({
            model_id: 'model_1',
            features: {
                feature_1: 50,
                feature_2: 60,
                feature_3: 70,
            },
        });
        
        const predictResponse = http.post(
            `${BASE_URL}/api/v1/predict`,
            predictPayload,
            { headers: { 'Content-Type': 'application/json' } }
        );
        
        check(predictResponse, {
            'predict status is 200': (r) => r.status === 200,
            'predict has result': (r) => r.json('prediction') !== undefined,
        });
        
        // Test models list endpoint
        const modelsResponse = http.get(`${BASE_URL}/api/v1/models`);
        check(modelsResponse, {
            'models status is 200': (r) => r.status === 200,
            'models returns array': (r) => Array.isArray(r.json()),
        });
    });
}

export function handleSummary(data) {
    const allChecksPassed = data.metrics.checks ? data.metrics.checks.values.rate === 1 : false;
    
    return {
        'smoke_test_result.json': JSON.stringify({
            passed: allChecksPassed,
            timestamp: new Date().toISOString(),
            duration_seconds: data.state.testRunDurationMs / 1000,
            checks_passed: data.metrics.checks ? data.metrics.checks.values.passes : 0,
            checks_failed: data.metrics.checks ? data.metrics.checks.values.fails : 0,
            avg_response_time_ms: data.metrics.http_req_duration ? data.metrics.http_req_duration.values.avg : 0,
            max_response_time_ms: data.metrics.http_req_duration ? data.metrics.http_req_duration.values.max : 0,
        }, null, 2),
    };
}
