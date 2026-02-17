"""
Prometheus exporter for load test results
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime


class PrometheusExporter:
    """Export load test metrics to Prometheus"""
    
    def __init__(self, prometheus_url: str = "http://localhost:9090"):
        self.prometheus_url = prometheus_url
        self.pushgateway_url = f"{prometheus_url}:9091"
    
    def push_metrics(self, job_name: str, metrics: Dict, 
                     grouping_key: Optional[Dict] = None) -> bool:
        """
        Push metrics to Prometheus Pushgateway
        
        Args:
            job_name: Name of the job
            metrics: Dictionary of metrics to push
            grouping_key: Optional grouping key for the job
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Format metrics for Pushgateway
            formatted_metrics = self._format_metrics(metrics)
            
            # Build URL
            url = f"{self.pushgateway_url}/metrics/job/{job_name}"
            if grouping_key:
                for key, value in grouping_key.items():
                    url += f"/{key}/{value}"
            
            # Push metrics
            response = requests.post(
                url,
                data=formatted_metrics,
                headers={'Content-Type': 'text/plain'}
            )
            
            return response.status_code in [200, 202]
        
        except Exception as e:
            print(f"Failed to push metrics: {e}")
            return False
    
    def _format_metrics(self, metrics: Dict) -> str:
        """Format metrics for Prometheus text format"""
        lines = []
        
        for name, value in metrics.items():
            if isinstance(value, (int, float)):
                lines.append(f"# TYPE {name} gauge")
                lines.append(f"{name} {value}")
        
        return "\n".join(lines)
    
    def query_prometheus(self, query: str, time: Optional[datetime] = None) -> Dict:
        """
        Query Prometheus for metrics
        
        Args:
            query: PromQL query
            time: Optional time for the query
        
        Returns:
            Query result
        """
        try:
            params = {'query': query}
            if time:
                params['time'] = time.timestamp()
            
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params=params
            )
            
            return response.json()
        
        except Exception as e:
            print(f"Failed to query Prometheus: {e}")
            return {}
    
    def query_range(self, query: str, start: datetime, 
                    end: datetime, step: str = "1m") -> Dict:
        """
        Query Prometheus for metrics over a time range
        
        Args:
            query: PromQL query
            start: Start time
            end: End time
            step: Query resolution step width
        
        Returns:
            Query result
        """
        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query_range",
                params={
                    'query': query,
                    'start': start.timestamp(),
                    'end': end.timestamp(),
                    'step': step,
                }
            )
            
            return response.json()
        
        except Exception as e:
            print(f"Failed to query Prometheus range: {e}")
            return {}
    
    def get_load_test_metrics(self, test_id: str, 
                              start: datetime, 
                              end: datetime) -> Dict:
        """
        Get all relevant metrics for a load test
        
        Args:
            test_id: Load test ID
            start: Test start time
            end: Test end time
        
        Returns:
            Dictionary of metrics
        """
        queries = {
            'request_rate': 'rate(loadtest_requests_total[1m])',
            'error_rate': 'rate(loadtest_errors_total[1m])',
            'response_time_p50': 'loadtest_response_time_p50_seconds',
            'response_time_p95': 'loadtest_response_time_p95_seconds',
            'response_time_p99': 'loadtest_response_time_p99_seconds',
            'active_users': 'loadtest_active_users',
            'current_rps': 'loadtest_current_rps',
        }
        
        results = {}
        for name, query in queries.items():
            results[name] = self.query_range(query, start, end)
        
        return results


class InfluxDBExporter:
    """Export load test metrics to InfluxDB"""
    
    def __init__(self, influxdb_url: str = "http://localhost:8086", 
                 database: str = "loadtests"):
        self.influxdb_url = influxdb_url
        self.database = database
    
    def write_point(self, measurement: str, tags: Dict, 
                    fields: Dict, timestamp: Optional[datetime] = None) -> bool:
        """
        Write a data point to InfluxDB
        
        Args:
            measurement: Measurement name
            tags: Tag dictionary
            fields: Field dictionary
            timestamp: Optional timestamp
        
        Returns:
            True if successful
        """
        try:
            # Format line protocol
            tags_str = ",".join([f"{k}={v}" for k, v in tags.items()]) if tags else ""
            fields_str = ",".join([f"{k}={v}" for k, v in fields.items()])
            
            line = f"{measurement}"
            if tags_str:
                line += f",{tags_str}"
            line += f" {fields_str}"
            
            if timestamp:
                line += f" {int(timestamp.timestamp() * 1e9)}"
            
            # Write to InfluxDB
            response = requests.post(
                f"{self.influxdb_url}/write",
                params={'db': self.database},
                data=line
            )
            
            return response.status_code == 204
        
        except Exception as e:
            print(f"Failed to write to InfluxDB: {e}")
            return False
    
    def write_load_test_results(self, test_id: str, test_type: str,
                                results: Dict, timestamp: datetime) -> bool:
        """
        Write complete load test results to InfluxDB
        
        Args:
            test_id: Test ID
            test_type: Type of test
            results: Test results dictionary
            timestamp: Test timestamp
        
        Returns:
            True if successful
        """
        tags = {
            'test_id': test_id,
            'test_type': test_type,
        }
        
        fields = {
            'total_requests': results.get('total_requests', 0),
            'successful_requests': results.get('successful_requests', 0),
            'failed_requests': results.get('failed_requests', 0),
            'avg_response_time': results.get('avg_response_time', 0),
            'p95_response_time': results.get('p95_response_time', 0),
            'p99_response_time': results.get('p99_response_time', 0),
            'error_rate': results.get('error_rate', 0),
            'requests_per_second': results.get('rps', 0),
        }
        
        return self.write_point('load_test', tags, fields, timestamp)
