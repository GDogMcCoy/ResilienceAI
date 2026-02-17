import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Custom metrics
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');
const recoveryTime = Trend('recovery_time');

// Spike test configuration - sudden traffic changes
export const options = {
    stages: [
        { duration: '2m', target: 50 },    // Normal load
        { duration: '30s', target: 1000 }, // Sudden spike (20x)
        { duration: '5m', target: 1000 },  // Sustained spike
        { duration: '30s', target: 50 },   // Sudden drop
        { duration: '3m', target: 50 },    // Recovery period
    ],
    thresholds: {
        http_req_duration: ['p(95)<5000'],  // Relaxed during spike
        http_req_failed: ['rate<0.10'],      // Up to 10% errors acceptable
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const MODEL_IDS = ['model_1', 'model_2', 'model_3', 'model_4', 'model_5', 
                   'model_6', 'model_7', 'model_8', 'model_9', 'model_10'];

let spikeStartTime = null;
let recoveryStartTime = null;

export function setup() {
    console.log('Starting spike test - simulating sudden traffic changes');
    return { 
        startTime: Date.now(),
        spikePhases: [],
    };
}

export default function (data) {
    const modelId = randomItem(MODEL_IDS);
    
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
        timeout: '10s',  // Shorter timeout for spike test
    };
    
    const startTime = Date.now();
    const response = http.post(`${BASE_URL}/api/v1/predict`, payload, params);
    const requestDuration = Date.now() - startTime;
    
    // Record metrics
    responseTime.add(response.timings.duration);
    errorRate.add(response.status >= 400 ? 1 : 0);
    
    // Check response
    const checks = check(response, {
        'response received': (r) => r.status !== 0,
        'acceptable status': (r) => r.status === 200 || r.status === 429 || r.status === 503,
    });
    
    // Track spike behavior
    if (__VU > 100 && !spikeStartTime) {
        spikeStartTime = Date.now();
        console.log(`Spike started at ${spikeStartTime}`);
    }
    
    // Log rate limiting during spike
    if (response.status === 429) {
        console.log(`Rate limited during spike - VU: ${__VU}`);
    }
    
    // Log service unavailable
    if (response.status === 503) {
        console.log(`Service unavailable - potential overload at VU: ${__VU}`);
    }
    
    // Minimal sleep during spike
    sleep(__VU > 100 ? 0.01 : 0.5);
}

export function handleSummary(data) {
    const errorRate = data.metrics.http_req_failed ? data.metrics.http_req_failed.values.rate : 0;
    const maxVUs = data.metrics.vus_max ? data.metrics.vus_max.value : 0;
    
    // Determine if system handled spike well
    let spikeHandling = 'Good';
    if (errorRate > 0.05) {
        spikeHandling = 'Poor - high error rate';
    } else if (data.metrics.http_req_duration && data.metrics.http_req_duration.values['p(95)'] > 3000) {
        spikeHandling = 'Fair - high latency';
    }
    
    return {
        'spike_test_summary.json': JSON.stringify({
            spike_handling: spikeHandling,
            max_concurrent_users: maxVUs,
            spike_multiplier: 20,  // 50 -> 1000
            total_requests: data.metrics.http_reqs ? data.metrics.http_reqs.values.count : 0,
            avg_response_time_ms: data.metrics.http_req_duration ? data.metrics.http_req_duration.values.avg : 0,
            p95_response_time_ms: data.metrics.http_req_duration ? data.metrics.http_req_duration.values['p(95)'] : 0,
            p99_response_time_ms: data.metrics.http_req_duration ? data.metrics.http_req_duration.values['p(99)'] : 0,
            error_rate: errorRate,
            rate_limited_requests: 'Check logs for 429 responses',
            service_unavailable: 'Check logs for 503 responses',
            test_duration_minutes: data.state.testRunDurationMs / 1000 / 60,
            recommendations: generateRecommendations(errorRate, spikeHandling),
        }, null, 2),
    };
}

function generateRecommendations(errorRate, handling) {
    const recommendations = [];
    
    if (errorRate > 0.05) {
        recommendations.push('Implement circuit breaker pattern');
        recommendations.push('Add rate limiting with graceful degradation');
        recommendations.push('Increase connection pool sizes');
    }
    
    if (handling !== 'Good') {
        recommendations.push('Implement auto-scaling policies');
        recommendations.push('Add request queuing with priority levels');
        recommendations.push('Optimize critical path code');
    }
    
    recommendations.push('Set up alerting for traffic spikes');
    recommendations.push('Implement caching for frequently accessed data');
    
    return recommendations;
}
