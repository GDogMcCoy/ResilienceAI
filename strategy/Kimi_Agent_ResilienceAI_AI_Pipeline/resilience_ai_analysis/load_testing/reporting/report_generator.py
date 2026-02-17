"""
Load test report generation for ResilienceAI
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import os


@dataclass
class LoadTestReport:
    """Comprehensive load test report"""
    test_id: str
    test_type: str
    start_time: datetime
    end_time: datetime
    summary: Dict
    metrics: Dict
    charts: List[str]
    findings: List[str]
    recommendations: List[str]


class ReportGenerator:
    """
    Generate comprehensive load test reports
    """
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_report(
        self,
        test_results: Dict,
        test_type: str = "load"
    ) -> LoadTestReport:
        """
        Generate a comprehensive load test report
        
        Args:
            test_results: Raw test results
            test_type: Type of test (load, stress, spike, endurance)
        
        Returns:
            LoadTestReport object
        """
        test_id = f"{test_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate summary
        summary = self._generate_summary(test_results)
        
        # Calculate metrics
        metrics = self._calculate_metrics(test_results)
        
        # Generate charts (placeholder - would use matplotlib)
        charts = []
        
        # Identify findings
        findings = self._identify_findings(metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(findings, metrics)
        
        report = LoadTestReport(
            test_id=test_id,
            test_type=test_type,
            start_time=datetime.fromisoformat(test_results.get("start_time", datetime.now().isoformat())),
            end_time=datetime.fromisoformat(test_results.get("end_time", datetime.now().isoformat())),
            summary=summary,
            metrics=metrics,
            charts=charts,
            findings=findings,
            recommendations=recommendations,
        )
        
        # Save report
        self._save_report(report)
        
        return report
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate test summary"""
        return {
            "total_requests": results.get("total_requests", 0),
            "successful_requests": results.get("successful_requests", 0),
            "failed_requests": results.get("failed_requests", 0),
            "success_rate": results.get("success_rate", 0),
            "total_duration_seconds": results.get("duration", 0),
            "peak_concurrent_users": results.get("peak_users", 0),
            "avg_requests_per_second": results.get("avg_rps", 0),
            "peak_requests_per_second": results.get("peak_rps", 0),
        }
    
    def _calculate_metrics(self, results: Dict) -> Dict:
        """Calculate detailed metrics"""
        response_times = results.get("response_times", [])
        
        if not response_times:
            return {}
        
        sorted_times = sorted(response_times)
        n = len(sorted_times)
        
        # Calculate mean
        mean_time = sum(response_times) / n if n > 0 else 0
        
        # Calculate percentiles
        p50 = sorted_times[int(n * 0.50)] if n > 0 else 0
        p90 = sorted_times[int(n * 0.90)] if n > 0 else 0
        p95 = sorted_times[int(n * 0.95)] if n > 0 else 0
        p99 = sorted_times[int(n * 0.99)] if n > 0 else 0
        
        return {
            "response_time": {
                "min_ms": min(response_times) if response_times else 0,
                "max_ms": max(response_times) if response_times else 0,
                "mean_ms": mean_time,
                "median_ms": p50,
                "p50_ms": p50,
                "p90_ms": p90,
                "p95_ms": p95,
                "p99_ms": p99,
            },
            "throughput": {
                "avg_rps": results.get("avg_rps", 0),
                "peak_rps": results.get("peak_rps", 0),
                "total_requests": results.get("total_requests", 0),
            },
            "errors": {
                "total_errors": results.get("failed_requests", 0),
                "error_rate": results.get("error_rate", 0),
                "error_breakdown": results.get("error_breakdown", {}),
            },
        }
    
    def _identify_findings(self, metrics: Dict) -> List[str]:
        """Identify key findings from metrics"""
        findings = []
        
        rt = metrics.get("response_time", {})
        errors = metrics.get("errors", {})
        
        # Response time findings
        p95 = rt.get("p95_ms", 0)
        p99 = rt.get("p99_ms", 0)
        
        if p95 > 2000:
            findings.append(f"CRITICAL: p95 response time ({p95:.0f}ms) exceeds 2000ms threshold")
        elif p95 > 1000:
            findings.append(f"WARNING: p95 response time ({p95:.0f}ms) exceeds 1000ms target")
        
        if p99 > 5000:
            findings.append(f"CRITICAL: p99 response time ({p99:.0f}ms) exceeds 5000ms threshold")
        
        # Error rate findings
        error_rate = errors.get("error_rate", 0)
        if error_rate > 5.0:
            findings.append(f"CRITICAL: Error rate ({error_rate:.2f}%) exceeds 5% threshold")
        elif error_rate > 1.0:
            findings.append(f"WARNING: Error rate ({error_rate:.2f}%) exceeds 1% warning level")
        
        # Throughput findings
        avg_rps = metrics.get("throughput", {}).get("avg_rps", 0)
        if avg_rps < 50:
            findings.append(f"WARNING: Average throughput ({avg_rps:.1f} RPS) below target of 100 RPS")
        
        return findings
    
    def _generate_recommendations(self, findings: List[str], metrics: Dict) -> List[str]:
        """Generate recommendations based on findings"""
        recommendations = []
        
        for finding in findings:
            if "response time" in finding.lower():
                recommendations.append(
                    "Consider implementing caching layer (Redis) to reduce response times"
                )
                recommendations.append(
                    "Optimize database queries and add appropriate indexes"
                )
                recommendations.append(
                    "Scale horizontally by adding more application servers"
                )
            
            if "error rate" in finding.lower():
                recommendations.append(
                    "Review application logs to identify root cause of errors"
                )
                recommendations.append(
                    "Implement circuit breaker pattern for external service calls"
                )
                recommendations.append(
                    "Increase connection pool sizes for database and external services"
                )
            
            if "throughput" in finding.lower():
                recommendations.append(
                    "Optimize ML model inference with batching or GPU acceleration"
                )
                recommendations.append(
                    "Implement async processing for non-critical operations"
                )
        
        # Add general recommendations
        recommendations.append(
            "Set up continuous monitoring with alerting for early detection"
        )
        recommendations.append(
            "Implement auto-scaling based on CPU and request queue depth"
        )
        
        return list(set(recommendations))  # Remove duplicates
    
    def _save_report(self, report: LoadTestReport):
        """Save report to file"""
        report_data = {
            "test_id": report.test_id,
            "test_type": report.test_type,
            "start_time": report.start_time.isoformat(),
            "end_time": report.end_time.isoformat(),
            "summary": report.summary,
            "metrics": report.metrics,
            "charts": report.charts,
            "findings": report.findings,
            "recommendations": report.recommendations,
        }
        
        report_file = f"{self.output_dir}/{report.test_id}_report.json"
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)
        
        # Generate HTML report
        self._generate_html_report(report, report_file.replace(".json", ".html"))
    
    def _generate_html_report(self, report: LoadTestReport, output_file: str):
        """Generate HTML report"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Load Test Report - {report.test_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #666; border-bottom: 2px solid #ddd; padding-bottom: 10px; margin-top: 30px; }}
        .summary {{ background: #f9f9f9; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .metric {{ margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #4CAF50; }}
        .finding {{ background: #fff3cd; padding: 15px; margin: 10px 0; border-left: 4px solid #ffc107; border-radius: 4px; }}
        .finding.critical {{ background: #f8d7da; border-left-color: #dc3545; }}
        .finding.warning {{ background: #fff3cd; border-left-color: #ffc107; }}
        .recommendation {{ background: #d1ecf1; padding: 15px; margin: 10px 0; border-left: 4px solid #17a2b8; border-radius: 4px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background: #f2f2f2; }}
        .status-passed {{ color: #28a745; font-weight: bold; }}
        .status-warning {{ color: #ffc107; font-weight: bold; }}
        .status-failed {{ color: #dc3545; font-weight: bold; }}
        .header-info {{ display: flex; gap: 30px; margin: 20px 0; flex-wrap: wrap; }}
        .header-item {{ background: #e9ecef; padding: 10px 20px; border-radius: 4px; }}
        .header-item strong {{ color: #495057; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Load Test Report</h1>
        
        <div class="header-info">
            <div class="header-item"><strong>Test ID:</strong> {report.test_id}</div>
            <div class="header-item"><strong>Test Type:</strong> {report.test_type}</div>
            <div class="header-item"><strong>Duration:</strong> {report.start_time.strftime('%Y-%m-%d %H:%M')} to {report.end_time.strftime('%Y-%m-%d %H:%M')}</div>
        </div>
        
        <h2>Summary</h2>
        <div class="summary">
            <div class="metric"><strong>Total Requests:</strong> {report.summary.get('total_requests', 0):,}</div>
            <div class="metric"><strong>Success Rate:</strong> {report.summary.get('success_rate', 0):.2f}%</div>
            <div class="metric"><strong>Average RPS:</strong> {report.summary.get('avg_requests_per_second', 0):.1f}</div>
            <div class="metric"><strong>Peak Concurrent Users:</strong> {report.summary.get('peak_concurrent_users', 0)}</div>
        </div>
        
        <h2>Performance Metrics</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
                <th>Target</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>p50 Response Time</td>
                <td>{report.metrics.get('response_time', {}).get('p50_ms', 0):.2f} ms</td>
                <td>&lt; 100 ms</td>
                <td>{self._get_status(report.metrics.get('response_time', {}).get('p50_ms', 0), 100)}</td>
            </tr>
            <tr>
                <td>p95 Response Time</td>
                <td>{report.metrics.get('response_time', {}).get('p95_ms', 0):.2f} ms</td>
                <td>&lt; 500 ms</td>
                <td>{self._get_status(report.metrics.get('response_time', {}).get('p95_ms', 0), 500)}</td>
            </tr>
            <tr>
                <td>p99 Response Time</td>
                <td>{report.metrics.get('response_time', {}).get('p99_ms', 0):.2f} ms</td>
                <td>&lt; 1000 ms</td>
                <td>{self._get_status(report.metrics.get('response_time', {}).get('p99_ms', 0), 1000)}</td>
            </tr>
            <tr>
                <td>Error Rate</td>
                <td>{report.metrics.get('errors', {}).get('error_rate', 0):.2f}%</td>
                <td>&lt; 0.1%</td>
                <td>{self._get_status(report.metrics.get('errors', {}).get('error_rate', 0), 0.1, inverse=True)}</td>
            </tr>
        </table>
        
        <h2>Key Findings</h2>
        {''.join(f'<div class="finding{" critical" if "CRITICAL" in f else " warning" if "WARNING" in f else ""}">{f}</div>' for f in report.findings) if report.findings else '<p>No significant findings.</p>'}
        
        <h2>Recommendations</h2>
        {''.join(f'<div class="recommendation">{r}</div>' for r in report.recommendations) if report.recommendations else '<p>No specific recommendations.</p>'}
    </div>
</body>
</html>"""
        
        with open(output_file, "w") as f:
            f.write(html)
    
    def _get_status(self, value: float, threshold: float, inverse: bool = False) -> str:
        """Get status indicator"""
        if inverse:
            if value > threshold * 5:
                return '<span class="status-failed">FAILED</span>'
            elif value > threshold:
                return '<span class="status-warning">WARNING</span>'
            else:
                return '<span class="status-passed">PASSED</span>'
        else:
            if value > threshold * 2:
                return '<span class="status-failed">FAILED</span>'
            elif value > threshold:
                return '<span class="status-warning">WARNING</span>'
            else:
                return '<span class="status-passed">PASSED</span>'
