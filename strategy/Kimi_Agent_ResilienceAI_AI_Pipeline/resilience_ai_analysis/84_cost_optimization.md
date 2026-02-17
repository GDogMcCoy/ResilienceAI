# ResilienceAI Cloud Cost Optimization & FinOps Framework

## Executive Summary

This document provides a comprehensive cost optimization strategy for ResilienceAI's cloud infrastructure, implementing FinOps best practices to achieve 30-40% cost reduction while maintaining performance and reliability.

**Target Outcomes:**
- 30-40% reduction in cloud spend within 6 months
- 95%+ resource utilization efficiency
- Automated cost governance and optimization
- Real-time cost visibility and accountability
- Predictable monthly cloud expenses

---

## 1. Cost Optimization Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COST OPTIMIZATION PLATFORM                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   COST       │  │  RESOURCE    │  │   BUDGET     │  │  FORECAST    │   │
│  │  MONITORING  │  │ OPTIMIZATION │  │   ALERTS     │  │   ENGINE     │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │                 │            │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐   │
│  │  Data        │  │  Right-      │  │  Threshold   │  │  ML-Based    │   │
│  │  Collection  │  │  Sizing      │  │  Management  │  │  Prediction  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│                           INTEGRATION LAYER                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  AWS APIs  │  │ Azure APIs │  │  GCP APIs  │  │ Kubernetes │            │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘            │
├─────────────────────────────────────────────────────────────────────────────┤
│                         COST DATA WAREHOUSE                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Time-Series DB (InfluxDB/TimescaleDB) + Analytics (ClickHouse)    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Overview

| Component | Purpose | Technology Stack |
|-----------|---------|------------------|
| Cost Collector | Gather cost data from all cloud providers | Python, Cloud SDKs |
| Resource Analyzer | Analyze utilization patterns | Prometheus, Grafana |
| Optimization Engine | Apply cost-saving recommendations | Python, Kubernetes Operators |
| Budget Manager | Track and alert on budgets | Custom Python, PagerDuty |
| Forecasting Service | Predict future costs | Prophet, scikit-learn |
| Waste Detector | Identify unused resources | Python, Cloud APIs |

---

## 2. Cost Monitoring Implementation

### 2.1 Multi-Cloud Cost Collection

```python
# /app/cost_optimization/collectors/cloud_cost_collector.py
"""
Multi-cloud cost collection system for ResilienceAI
"""

import boto3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CostRecord:
    """Standardized cost record across all cloud providers"""
    timestamp: datetime
    service: str
    resource_id: str
    cost: float
    currency: str
    region: str
    tags: Dict[str, str]
    provider: str
    usage_type: str
    usage_quantity: float
    unit: str


class CloudCostCollector(ABC):
    """Abstract base class for cloud cost collectors"""
    
    @abstractmethod
    def collect_costs(self, start_date: datetime, end_date: datetime) -> List[CostRecord]:
        pass
    
    @abstractmethod
    def get_current_month_forecast(self) -> float:
        pass


class AWSCostCollector(CloudCostCollector):
    """AWS Cost Explorer integration"""
    
    def __init__(self, access_key: str = None, secret_key: str = None):
        self.client = boto3.client(
            'ce',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.org_client = boto3.client('organizations')
        
    def collect_costs(self, start_date: datetime, end_date: datetime) -> List[CostRecord]:
        """Collect detailed cost data from AWS Cost Explorer"""
        
        records = []
        
        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost', 'UsageQuantity'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'REGION'},
                    {'Type': 'TAG', 'Key': 'Environment'},
                    {'Type': 'TAG', 'Key': 'Project'},
                    {'Type': 'TAG', 'Key': 'Team'}
                ],
                Filter={
                    'Tags': {
                        'Key': 'Project',
                        'Values': ['ResilienceAI']
                    }
                }
            )
            
            for result in response['ResultsByTime']:
                timestamp = datetime.strptime(result['TimePeriod']['Start'], '%Y-%m-%d')
                
                for group in result.get('Groups', []):
                    keys = group['Keys']
                    metrics = group['Metrics']
                    
                    cost = float(metrics['UnblendedCost']['Amount'])
                    
                    if cost > 0:
                        tags = self._parse_tags(keys[2:])
                        
                        record = CostRecord(
                            timestamp=timestamp,
                            service=keys[0],
                            resource_id=keys[1] if len(keys) > 1 else 'unknown',
                            cost=cost,
                            currency=metrics['UnblendedCost']['Unit'],
                            region=keys[1] if len(keys) > 1 else 'global',
                            tags=tags,
                            provider='AWS',
                            usage_type='OnDemand',
                            usage_quantity=float(metrics['UsageQuantity']['Amount']),
                            unit=metrics['UsageQuantity']['Unit']
                        )
                        records.append(record)
                        
        except Exception as e:
            logger.error(f"Error collecting AWS costs: {e}")
            
        return records
    
    def get_current_month_forecast(self) -> float:
        """Get forecast for current month"""
        try:
            response = self.client.get_cost_forecast(
                TimePeriod={
                    'Start': datetime.now().strftime('%Y-%m-%d'),
                    'End': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                },
                Metric='UNBLENDED_COST',
                Granularity='MONTHLY'
            )
            return float(response['Total']['Amount'])
        except Exception as e:
            logger.error(f"Error getting AWS forecast: {e}")
            return 0.0
    
    def get_savings_plans_recommendations(self) -> List[Dict]:
        """Get Savings Plans recommendations"""
        try:
            response = self.client.get_savings_plans_purchase_recommendation(
                SavingsPlansType='COMPUTE_SP',
                TermInYears='ONE_YEAR',
                PaymentOption='PARTIAL_UPFRONT',
                LookbackPeriodInDays='THIRTY_DAYS'
            )
            return response.get('SavingsPlansPurchaseRecommendation', {}).get('Details', [])
        except Exception as e:
            logger.error(f"Error getting Savings Plans recommendations: {e}")
            return []
    
    def _parse_tags(self, tag_keys: List[str]) -> Dict[str, str]:
        """Parse tag keys into dictionary"""
        tags = {}
        for i in range(0, len(tag_keys), 2):
            if i + 1 < len(tag_keys):
                tags[tag_keys[i]] = tag_keys[i + 1]
        return tags


class AzureCostCollector(CloudCostCollector):
    """Azure Cost Management integration"""
    
    def __init__(self, subscription_id: str, tenant_id: str, client_id: str, client_secret: str):
        from azure.identity import ClientSecretCredential
        from azure.mgmt.costmanagement import CostManagementClient
        
        credentials = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        self.client = CostManagementClient(credentials)
        self.subscription_id = subscription_id
        
    def collect_costs(self, start_date: datetime, end_date: datetime) -> List[CostRecord]:
        """Collect cost data from Azure Cost Management"""
        
        records = []
        
        try:
            scope = f"/subscriptions/{self.subscription_id}"
            
            query = {
                "type": "Usage",
                "timeframe": "Custom",
                "timePeriod": {
                    "from": start_date.isoformat(),
                    "to": end_date.isoformat()
                },
                "dataset": {
                    "granularity": "Daily",
                    "aggregation": {
                        "totalCost": {"name": "Cost", "function": "Sum"},
                        "totalUsage": {"name": "UsageQuantity", "function": "Sum"}
                    },
                    "grouping": [
                        {"type": "Dimension", "name": "ServiceName"},
                        {"type": "Dimension", "name": "ResourceLocation"},
                        {"type": "TagKey", "name": "Environment"},
                        {"type": "TagKey", "name": "Project"}
                    ]
                }
            }
            
            result = self.client.query.usage(scope=scope, parameters=query)
            
            for row in result.rows:
                record = CostRecord(
                    timestamp=datetime.strptime(row[0], '%Y-%m-%d'),
                    service=row[1],
                    resource_id=row[2],
                    cost=float(row[3]),
                    currency='USD',
                    region=row[2],
                    tags={'Project': 'ResilienceAI'},
                    provider='Azure',
                    usage_type='Consumption',
                    usage_quantity=float(row[4]) if len(row) > 4 else 0,
                    unit='Units'
                )
                records.append(record)
                
        except Exception as e:
            logger.error(f"Error collecting Azure costs: {e}")
            
        return records
    
    def get_current_month_forecast(self) -> float:
        """Get Azure cost forecast"""
        try:
            scope = f"/subscriptions/{self.subscription_id}"
            
            query = {
                "type": "Forecast",
                "timeframe": "MonthToDate",
                "dataset": {
                    "granularity": "Monthly",
                    "aggregation": {
                        "totalCost": {"name": "Cost", "function": "Sum"}
                    }
                }
            }
            
            result = self.client.query.forecast(scope=scope, parameters=query)
            return sum(float(row[1]) for row in result.rows)
            
        except Exception as e:
            logger.error(f"Error getting Azure forecast: {e}")
            return 0.0


class GCPCostCollector(CloudCostCollector):
    """GCP Billing API integration"""
    
    def __init__(self, project_id: str, credentials_path: str):
        from google.cloud import billing_v1
        from google.oauth2 import service_account
        
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        
        self.client = billing_v1.CloudBillingClient(credentials=credentials)
        self.project_id = project_id
        
    def collect_costs(self, start_date: datetime, end_date: datetime) -> List[CostRecord]:
        """Collect cost data from GCP Billing Export"""
        
        records = []
        
        try:
            from google.cloud import bigquery
            
            bq_client = bigquery.Client(project=self.project_id)
            
            query = f"""
                SELECT
                    usage_start_time,
                    service.description as service_name,
                    resource.name as resource_id,
                    cost,
                    currency,
                    location.region as region,
                    labels,
                    usage.amount as usage_quantity,
                    usage.unit as usage_unit
                FROM `{self.project_id}.billing_export.gcp_billing_export_v1_*`
                WHERE usage_start_time BETWEEN '{start_date.isoformat()}' AND '{end_date.isoformat()}'
                AND EXISTS (
                    SELECT 1 FROM UNNEST(labels) AS label
                    WHERE label.key = 'project' AND label.value = 'resilienceai'
                )
                ORDER BY usage_start_time
            """
            
            query_job = bq_client.query(query)
            
            for row in query_job:
                tags = {label.key: label.value for label in row.labels}
                
                record = CostRecord(
                    timestamp=row.usage_start_time,
                    service=row.service_name,
                    resource_id=row.resource_id,
                    cost=float(row.cost),
                    currency=row.currency,
                    region=row.region,
                    tags=tags,
                    provider='GCP',
                    usage_type='OnDemand',
                    usage_quantity=float(row.usage_quantity),
                    unit=row.usage_unit
                )
                records.append(record)
                
        except Exception as e:
            logger.error(f"Error collecting GCP costs: {e}")
            
        return records
    
    def get_current_month_forecast(self) -> float:
        """Get GCP cost forecast"""
        # GCP doesn't have native forecasting API; use historical data
        return 0.0


class CostCollectorManager:
    """Manager for all cloud cost collectors"""
    
    def __init__(self):
        self.collectors: Dict[str, CloudCostCollector] = {}
        
    def register_collector(self, name: str, collector: CloudCostCollector):
        """Register a cloud cost collector"""
        self.collectors[name] = collector
        logger.info(f"Registered cost collector: {name}")
        
    def collect_all_costs(self, start_date: datetime, end_date: datetime) -> Dict[str, List[CostRecord]]:
        """Collect costs from all registered collectors"""
        all_costs = {}
        
        for name, collector in self.collectors.items():
            logger.info(f"Collecting costs from {name}...")
            costs = collector.collect_costs(start_date, end_date)
            all_costs[name] = costs
            logger.info(f"Collected {len(costs)} cost records from {name}")
            
        return all_costs
    
    def get_total_forecast(self) -> float:
        """Get combined forecast from all collectors"""
        total = 0.0
        
        for name, collector in self.collectors.items():
            forecast = collector.get_current_month_forecast()
            total += forecast
            logger.info(f"{name} forecast: ${forecast:,.2f}")
            
        return total


# Usage example
if __name__ == "__main__":
    # Initialize collectors
    manager = CostCollectorManager()
    
    # Register AWS collector
    aws_collector = AWSCostCollector()
    manager.register_collector('aws', aws_collector)
    
    # Collect last 7 days of costs
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    all_costs = manager.collect_all_costs(start_date, end_date)
    
    # Print summary
    for provider, costs in all_costs.items():
        total = sum(c.cost for c in costs)
        print(f"{provider.upper()}: ${total:,.2f} ({len(costs)} records)")
```

### 2.2 Real-Time Cost Metrics Collection

```python
# /app/cost_optimization/collectors/realtime_metrics.py
"""
Real-time cost and utilization metrics collection
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp
from dataclasses import dataclass
import json


@dataclass
class ResourceMetrics:
    """Real-time resource metrics"""
    resource_id: str
    resource_type: str
    region: str
    cpu_utilization: float
    memory_utilization: float
    network_in: float
    network_out: float
    disk_read_ops: float
    disk_write_ops: float
    timestamp: datetime
    cost_per_hour: float
    tags: Dict[str, str]


class KubernetesMetricsCollector:
    """Collect Kubernetes resource metrics"""
    
    def __init__(self, api_server: str, token: str):
        self.api_server = api_server
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}
        
    async def collect_pod_metrics(self, namespace: str = None) -> List[ResourceMetrics]:
        """Collect pod resource metrics"""
        
        metrics = []
        url = f"{self.api_server}/apis/metrics.k8s.io/v1beta1/pods"
        
        if namespace:
            url = f"{self.api_server}/apis/metrics.k8s.io/v1beta1/namespaces/{namespace}/pods"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, ssl=False) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    for item in data.get('items', []):
                        for container in item.get('containers', []):
                            usage = container.get('usage', {})
                            
                            metric = ResourceMetrics(
                                resource_id=f"{item['metadata']['namespace']}/{item['metadata']['name']}/{container['name']}",
                                resource_type='kubernetes_pod',
                                region='cluster',
                                cpu_utilization=self._parse_cpu(usage.get('cpu', '0')),
                                memory_utilization=self._parse_memory(usage.get('memory', '0')),
                                network_in=0,
                                network_out=0,
                                disk_read_ops=0,
                                disk_write_ops=0,
                                timestamp=datetime.now(),
                                cost_per_hour=0,  # Calculated separately
                                tags=item['metadata'].get('labels', {})
                            )
                            metrics.append(metric)
                            
        return metrics
    
    def _parse_cpu(self, cpu_str: str) -> float:
        """Parse CPU string to millicores"""
        if cpu_str.endswith('n'):
            return int(cpu_str[:-1]) / 1_000_000
        elif cpu_str.endswith('u'):
            return int(cpu_str[:-1]) / 1_000
        elif cpu_str.endswith('m'):
            return int(cpu_str[:-1])
        else:
            return int(cpu_str) * 1000
    
    def _parse_memory(self, mem_str: str) -> float:
        """Parse memory string to MB"""
        if mem_str.endswith('Ki'):
            return int(mem_str[:-2]) / 1024
        elif mem_str.endswith('Mi'):
            return int(mem_str[:-2])
        elif mem_str.endswith('Gi'):
            return int(mem_str[:-2]) * 1024
        else:
            return int(mem_str) / (1024 * 1024)


class PrometheusMetricsCollector:
    """Collect metrics from Prometheus"""
    
    def __init__(self, prometheus_url: str):
        self.prometheus_url = prometheus_url
        
    async def query(self, query: str) -> Dict:
        """Execute PromQL query"""
        
        url = f"{self.prometheus_url}/api/v1/query"
        params = {'query': query}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {}
    
    async def get_instance_metrics(self) -> List[ResourceMetrics]:
        """Get EC2/GCE instance metrics"""
        
        queries = {
            'cpu': '100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)',
            'memory': '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100',
            'network_in': 'rate(node_network_receive_bytes_total[5m])',
            'network_out': 'rate(node_network_transmit_bytes_total[5m])'
        }
        
        metrics = []
        
        for metric_type, query in queries.items():
            result = await self.query(query)
            
            for item in result.get('data', {}).get('result', []):
                instance = item['metric'].get('instance', 'unknown')
                value = float(item['value'][1])
                
                # Find or create metric
                existing = next((m for m in metrics if m.resource_id == instance), None)
                
                if existing:
                    if metric_type == 'cpu':
                        existing.cpu_utilization = value
                    elif metric_type == 'memory':
                        existing.memory_utilization = value
                    elif metric_type == 'network_in':
                        existing.network_in = value
                    elif metric_type == 'network_out':
                        existing.network_out = value
                else:
                    metric = ResourceMetrics(
                        resource_id=instance,
                        resource_type='compute_instance',
                        region=item['metric'].get('region', 'unknown'),
                        cpu_utilization=value if metric_type == 'cpu' else 0,
                        memory_utilization=value if metric_type == 'memory' else 0,
                        network_in=value if metric_type == 'network_in' else 0,
                        network_out=value if metric_type == 'network_out' else 0,
                        disk_read_ops=0,
                        disk_write_ops=0,
                        timestamp=datetime.now(),
                        cost_per_hour=0,
                        tags=item['metric']
                    )
                    metrics.append(metric)
                    
        return metrics
```

---

## 3. Resource Right-Sizing System

### 3.1 Right-Sizing Analysis Engine

```python
# /app/cost_optimization/right_sizing/analyzer.py
"""
Resource right-sizing analysis and recommendations
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SizingRecommendation(Enum):
    """Types of sizing recommendations"""
    DOWNSIZE = "downsize"
    UPSIZE = "upsize"
    RIGHTSIZED = "rightsized"
    TERMINATE = "terminate"
    NO_CHANGE = "no_change"


@dataclass
class RightSizingRecommendation:
    """Right-sizing recommendation for a resource"""
    resource_id: str
    resource_type: str
    current_size: str
    recommended_size: str
    recommendation_type: SizingRecommendation
    confidence: float
    estimated_savings: float
    estimated_savings_percent: float
    risk_level: str
    reason: str
    metrics: Dict[str, float]
    implementation_plan: List[str]


class RightSizingAnalyzer:
    """Analyze resource utilization and recommend right-sizing"""
    
    # AWS EC2 instance families and sizes
    EC2_INSTANCE_SIZES = {
        't3': ['nano', 'micro', 'small', 'medium', 'large', 'xlarge', '2xlarge'],
        't3a': ['micro', 'small', 'medium', 'large', 'xlarge', '2xlarge'],
        'm5': ['large', 'xlarge', '2xlarge', '4xlarge', '8xlarge', '12xlarge', '16xlarge', '24xlarge'],
        'm5a': ['large', 'xlarge', '2xlarge', '4xlarge', '8xlarge', '12xlarge', '16xlarge', '24xlarge'],
        'm6g': ['medium', 'large', 'xlarge', '2xlarge', '4xlarge', '8xlarge', '12xlarge', '16xlarge'],
        'c5': ['large', 'xlarge', '2xlarge', '4xlarge', '9xlarge', '12xlarge', '18xlarge', '24xlarge'],
        'c6g': ['medium', 'large', 'xlarge', '2xlarge', '4xlarge', '8xlarge', '12xlarge', '16xlarge'],
        'r5': ['large', 'xlarge', '2xlarge', '4xlarge', '8xlarge', '12xlarge', '16xlarge', '24xlarge'],
        'r6g': ['medium', 'large', 'xlarge', '2xlarge', '4xlarge', '8xlarge', '12xlarge', '16xlarge'],
    }
    
    # Instance pricing (on-demand, us-east-1, approximate)
    EC2_PRICING = {
        't3.nano': 0.0052,
        't3.micro': 0.0104,
        't3.small': 0.0208,
        't3.medium': 0.0416,
        't3.large': 0.0832,
        't3.xlarge': 0.1664,
        't3.2xlarge': 0.3328,
        'm5.large': 0.096,
        'm5.xlarge': 0.192,
        'm5.2xlarge': 0.384,
        'm5.4xlarge': 0.768,
        'm5.8xlarge': 1.536,
        'm5.12xlarge': 2.304,
        'm5.16xlarge': 3.072,
        'm5.24xlarge': 4.608,
        'm6g.large': 0.077,
        'm6g.xlarge': 0.154,
        'm6g.2xlarge': 0.308,
        'm6g.4xlarge': 0.616,
        'c5.large': 0.085,
        'c5.xlarge': 0.17,
        'c5.2xlarge': 0.34,
        'c5.4xlarge': 0.68,
        'c5.9xlarge': 1.53,
        'c6g.large': 0.068,
        'c6g.xlarge': 0.136,
        'c6g.2xlarge': 0.272,
        'r5.large': 0.126,
        'r5.xlarge': 0.252,
        'r5.2xlarge': 0.504,
        'r6g.large': 0.1008,
        'r6g.xlarge': 0.2016,
    }
    
    def __init__(self, metrics_retention_days: int = 30):
        self.metrics_retention_days = metrics_retention_days
        
    def analyze_instance(self, 
                         instance_id: str,
                         instance_type: str,
                         metrics_history: pd.DataFrame) -> RightSizingRecommendation:
        """
        Analyze instance utilization and provide right-sizing recommendation
        
        Args:
            instance_id: Unique instance identifier
            instance_type: Current instance type (e.g., 'm5.xlarge')
            metrics_history: DataFrame with columns: timestamp, cpu_utilization, memory_utilization
        
        Returns:
            RightSizingRecommendation object
        """
        
        if metrics_history.empty:
            return RightSizingRecommendation(
                resource_id=instance_id,
                resource_type='ec2_instance',
                current_size=instance_type,
                recommended_size=instance_type,
                recommendation_type=SizingRecommendation.NO_CHANGE,
                confidence=0.0,
                estimated_savings=0.0,
                estimated_savings_percent=0.0,
                risk_level='unknown',
                reason='No metrics data available',
                metrics={},
                implementation_plan=[]
            )
        
        # Calculate utilization statistics
        cpu_stats = self._calculate_utilization_stats(metrics_history['cpu_utilization'])
        memory_stats = self._calculate_utilization_stats(metrics_history['memory_utilization'])
        
        # Determine recommendation
        recommendation = self._determine_recommendation(
            instance_type, cpu_stats, memory_stats
        )
        
        # Calculate savings
        current_cost = self.EC2_PRICING.get(instance_type, 0)
        recommended_cost = self.EC2_PRICING.get(recommendation['recommended_size'], current_cost)
        
        monthly_savings = (current_cost - recommended_cost) * 24 * 30
        savings_percent = ((current_cost - recommended_cost) / current_cost * 100) if current_cost > 0 else 0
        
        # Determine risk level
        risk_level = self._assess_risk(cpu_stats, memory_stats, recommendation['type'])
        
        # Generate implementation plan
        implementation_plan = self._generate_implementation_plan(
            instance_id, instance_type, recommendation['recommended_size'], recommendation['type']
        )
        
        return RightSizingRecommendation(
            resource_id=instance_id,
            resource_type='ec2_instance',
            current_size=instance_type,
            recommended_size=recommendation['recommended_size'],
            recommendation_type=recommendation['type'],
            confidence=recommendation['confidence'],
            estimated_savings=monthly_savings,
            estimated_savings_percent=savings_percent,
            risk_level=risk_level,
            reason=recommendation['reason'],
            metrics={
                'cpu_avg': cpu_stats['mean'],
                'cpu_p95': cpu_stats['p95'],
                'cpu_max': cpu_stats['max'],
                'memory_avg': memory_stats['mean'],
                'memory_p95': memory_stats['p95'],
                'memory_max': memory_stats['max'],
                'data_points': len(metrics_history)
            },
            implementation_plan=implementation_plan
        )
    
    def _calculate_utilization_stats(self, series: pd.Series) -> Dict[str, float]:
        """Calculate utilization statistics"""
        return {
            'mean': series.mean(),
            'median': series.median(),
            'std': series.std(),
            'min': series.min(),
            'max': series.max(),
            'p95': series.quantile(0.95),
            'p99': series.quantile(0.99)
        }
    
    def _determine_recommendation(self, 
                                   instance_type: str,
                                   cpu_stats: Dict[str, float],
                                   memory_stats: Dict[str, float]) -> Dict:
        """Determine right-sizing recommendation based on utilization"""
        
        # Parse instance family and size
        parts = instance_type.split('.')
        if len(parts) != 2:
            return {
                'type': SizingRecommendation.NO_CHANGE,
                'recommended_size': instance_type,
                'confidence': 0.0,
                'reason': 'Unable to parse instance type'
            }
        
        family, size = parts
        
        if family not in self.EC2_INSTANCE_SIZES:
            return {
                'type': SizingRecommendation.NO_CHANGE,
                'recommended_size': instance_type,
                'confidence': 0.0,
                'reason': f'Unknown instance family: {family}'
            }
        
        sizes = self.EC2_INSTANCE_SIZES[family]
        
        if size not in sizes:
            return {
                'type': SizingRecommendation.NO_CHANGE,
                'recommended_size': instance_type,
                'confidence': 0.0,
                'reason': f'Unknown instance size: {size}'
            }
        
        current_index = sizes.index(size)
        
        # Decision logic based on utilization
        cpu_avg = cpu_stats['mean']
        cpu_p95 = cpu_stats['p95']
        cpu_max = cpu_stats['max']
        memory_avg = memory_stats['mean']
        memory_p95 = memory_stats['p95']
        
        # Low utilization - recommend downsizing
        if cpu_avg < 20 and memory_avg < 40:
            # Can downsize multiple levels
            steps = min(2, current_index)
            if steps > 0:
                new_size = sizes[current_index - steps]
                confidence = min(0.95, 0.7 + (20 - cpu_avg) / 100)
                return {
                    'type': SizingRecommendation.DOWNSIZE,
                    'recommended_size': f"{family}.{new_size}",
                    'confidence': confidence,
                    'reason': f'Low utilization: CPU avg {cpu_avg:.1f}%, Memory avg {memory_avg:.1f}%'
                }
        
        # Moderate low utilization - downsize one level
        if cpu_avg < 35 and memory_avg < 50 and current_index > 0:
            new_size = sizes[current_index - 1]
            confidence = min(0.90, 0.6 + (35 - cpu_avg) / 100)
            return {
                'type': SizingRecommendation.DOWNSIZE,
                'recommended_size': f"{family}.{new_size}",
                'confidence': confidence,
                'reason': f'Below optimal utilization: CPU avg {cpu_avg:.1f}%, Memory avg {memory_avg:.1f}%'
            }
        
        # High utilization - recommend upsizing
        if cpu_p95 > 85 or memory_p95 > 85:
            if current_index < len(sizes) - 1:
                new_size = sizes[current_index + 1]
                confidence = min(0.85, 0.5 + (cpu_p95 - 85) / 30)
                return {
                    'type': SizingRecommendation.UPSIZE,
                    'recommended_size': f"{family}.{new_size}",
                    'confidence': confidence,
                    'reason': f'High peak utilization: CPU p95 {cpu_p95:.1f}%, Memory p95 {memory_p95:.1f}%'
                }
        
        # Very low utilization - consider termination
        if cpu_avg < 5 and memory_avg < 20:
            confidence = min(0.80, 0.5 + (5 - cpu_avg) / 10)
            return {
                'type': SizingRecommendation.TERMINATE,
                'recommended_size': 'terminate',
                'confidence': confidence,
                'reason': f'Very low utilization suggests idle resource: CPU avg {cpu_avg:.1f}%, Memory avg {memory_avg:.1f}%'
            }
        
        # Right-sized
        return {
            'type': SizingRecommendation.RIGHTSIZED,
            'recommended_size': instance_type,
            'confidence': 0.85,
            'reason': f'Optimal utilization: CPU avg {cpu_avg:.1f}%, Memory avg {memory_avg:.1f}%'
        }
    
    def _assess_risk(self, 
                     cpu_stats: Dict[str, float],
                     memory_stats: Dict[str, float],
                     recommendation_type: SizingRecommendation) -> str:
        """Assess risk level of recommendation"""
        
        if recommendation_type == SizingRecommendation.TERMINATE:
            return 'high'
        
        if recommendation_type == SizingRecommendation.DOWNSIZE:
            # Check if there are spikes that could cause issues
            if cpu_stats['max'] > 80 or memory_stats['max'] > 80:
                return 'medium'
            return 'low'
        
        if recommendation_type == SizingRecommendation.UPSIZE:
            return 'low'
        
        return 'low'
    
    def _generate_implementation_plan(self,
                                       instance_id: str,
                                       current_size: str,
                                       recommended_size: str,
                                       recommendation_type: SizingRecommendation) -> List[str]:
        """Generate step-by-step implementation plan"""
        
        plan = []
        
        if recommendation_type == SizingRecommendation.DOWNSIZE:
            plan = [
                f"1. Create AMI backup of instance {instance_id}",
                f"2. Schedule maintenance window for instance {instance_id}",
                f"3. Stop instance {instance_id}",
                f"4. Change instance type from {current_size} to {recommended_size}",
                f"5. Start instance {current_size}",
                f"6. Verify application functionality",
                f"7. Monitor for 24-48 hours before cleanup"
            ]
        elif recommendation_type == SizingRecommendation.TERMINATE:
            plan = [
                f"1. Verify instance {instance_id} is not in use (check logs, connections)",
                f"2. Create final snapshot/backup if needed",
                f"3. Notify team about planned termination",
                f"4. Wait 7 days for any objections",
                f"5. Terminate instance {instance_id}",
                f"6. Clean up associated resources (volumes, snapshots)"
            ]
        elif recommendation_type == SizingRecommendation.UPSIZE:
            plan = [
                f"1. Schedule maintenance window for instance {instance_id}",
                f"2. Notify stakeholders of planned upsizing",
                f"3. Stop instance {instance_id}",
                f"4. Change instance type from {current_size} to {recommended_size}",
                f"5. Start instance {instance_id}",
                f"6. Verify application performance improvement"
            ]
        
        return plan
    
    def batch_analyze(self, 
                      instances_data: List[Dict]) -> List[RightSizingRecommendation]:
        """Analyze multiple instances"""
        
        recommendations = []
        
        for instance in instances_data:
            try:
                rec = self.analyze_instance(
                    instance_id=instance['id'],
                    instance_type=instance['type'],
                    metrics_history=instance['metrics']
                )
                recommendations.append(rec)
            except Exception as e:
                logger.error(f"Error analyzing instance {instance['id']}: {e}")
                
        return recommendations


class KubernetesRightSizingAnalyzer:
    """Analyze Kubernetes resource requests and limits"""
    
    def __init__(self):
        self.cpu_request_threshold = 0.5  # 50% of request
        self.memory_request_threshold = 0.5
        
    def analyze_pod(self,
                    pod_name: str,
                    namespace: str,
                    container_name: str,
                    current_requests: Dict[str, str],
                    current_limits: Dict[str, str],
                    metrics_history: pd.DataFrame) -> Dict:
        """Analyze pod resource usage and recommend adjustments"""
        
        # Parse current resources
        cpu_request = self._parse_cpu(current_requests.get('cpu', '0'))
        memory_request = self._parse_memory(current_requests.get('memory', '0'))
        cpu_limit = self._parse_cpu(current_limits.get('cpu', '0'))
        memory_limit = self._parse_memory(current_limits.get('memory', '0'))
        
        # Calculate actual usage
        cpu_usage_avg = metrics_history['cpu_usage'].mean() if 'cpu_usage' in metrics_history.columns else 0
        memory_usage_avg = metrics_history['memory_usage'].mean() if 'memory_usage' in metrics_history.columns else 0
        
        recommendations = {
            'pod': pod_name,
            'namespace': namespace,
            'container': container_name,
            'current': {
                'cpu_request': cpu_request,
                'cpu_limit': cpu_limit,
                'memory_request': memory_request,
                'memory_limit': memory_limit
            },
            'recommended': {},
            'reasons': []
        }
        
        # CPU recommendations
        if cpu_request > 0:
            cpu_utilization = cpu_usage_avg / cpu_request
            
            if cpu_utilization < self.cpu_request_threshold:
                # Over-provisioned
                new_cpu_request = max(cpu_usage_avg * 1.2, 10)  # 20% buffer, min 10m
                recommendations['recommended']['cpu_request'] = f"{int(new_cpu_request)}m"
                recommendations['reasons'].append(
                    f"CPU request over-provisioned: using {cpu_utilization*100:.1f}% of request"
                )
            elif cpu_utilization > 0.8:
                # Under-provisioned
                new_cpu_request = cpu_usage_avg * 1.3
                recommendations['recommended']['cpu_request'] = f"{int(new_cpu_request)}m"
                recommendations['reasons'].append(
                    f"CPU request under-provisioned: using {cpu_utilization*100:.1f}% of request"
                )
        
        # Memory recommendations
        if memory_request > 0:
            memory_utilization = memory_usage_avg / memory_request
            
            if memory_utilization < self.memory_request_threshold:
                # Over-provisioned
                new_memory_request = max(memory_usage_avg * 1.3, 64)  # 30% buffer, min 64Mi
                recommendations['recommended']['memory_request'] = f"{int(new_memory_request)}Mi"
                recommendations['reasons'].append(
                    f"Memory request over-provisioned: using {memory_utilization*100:.1f}% of request"
                )
        
        return recommendations
    
    def _parse_cpu(self, cpu_str: str) -> float:
        """Parse CPU string to millicores"""
        if not cpu_str:
            return 0
        if cpu_str.endswith('m'):
            return float(cpu_str[:-1])
        return float(cpu_str) * 1000
    
    def _parse_memory(self, mem_str: str) -> float:
        """Parse memory string to Mi"""
        if not mem_str:
            return 0
        if mem_str.endswith('Mi'):
            return float(mem_str[:-2])
        if mem_str.endswith('Gi'):
            return float(mem_str[:-2]) * 1024
        if mem_str.endswith('Ki'):
            return float(mem_str[:-2]) / 1024
        return float(mem_str) / (1024 * 1024)


# Usage example
if __name__ == "__main__":
    # Create sample metrics data
    dates = pd.date_range(start='2024-01-01', periods=720, freq='H')
    
    # Low utilization instance
    low_util_metrics = pd.DataFrame({
        'timestamp': dates,
        'cpu_utilization': np.random.normal(15, 5, 720).clip(0, 100),
        'memory_utilization': np.random.normal(30, 10, 720).clip(0, 100)
    })
    
    analyzer = RightSizingAnalyzer()
    
    recommendation = analyzer.analyze_instance(
        instance_id='i-1234567890abcdef0',
        instance_type='m5.xlarge',
        metrics_history=low_util_metrics
    )
    
    print(f"Recommendation for {recommendation.resource_id}:")
    print(f"  Current: {recommendation.current_size}")
    print(f"  Recommended: {recommendation.recommended_size}")
    print(f"  Type: {recommendation.recommendation_type.value}")
    print(f"  Confidence: {recommendation.confidence:.2%}")
    print(f"  Monthly Savings: ${recommendation.estimated_savings:,.2f}")
    print(f"  Risk Level: {recommendation.risk_level}")
    print(f"  Reason: {recommendation.reason}")
```

---

## 4. Reserved Capacity Planning

### 4.1 Reserved Instance/Savings Plans Optimizer

```python
# /app/cost_optimization/reserved_capacity/planner.py
"""
Reserved capacity planning and optimization for AWS, Azure, GCP
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CommitmentType(Enum):
    """Types of reserved capacity commitments"""
    AWS_RESERVED_INSTANCE = "aws_ri"
    AWS_SAVINGS_PLANS = "aws_sp"
    AZURE_RESERVED_VM = "azure_ri"
    AZURE_SAVINGS_PLAN = "azure_sp"
    GCP_COMMITED_USE = "gcp_cud"


@dataclass
class CommitmentRecommendation:
    """Reserved capacity commitment recommendation"""
    commitment_type: CommitmentType
    resource_type: str
    region: str
    term_years: int
    payment_option: str
    hourly_commitment: float
    upfront_cost: float
    monthly_cost: float
    total_cost: float
    on_demand_equivalent: float
    estimated_savings: float
    savings_percent: float
    confidence: float
    utilization_forecast: List[float]
    risk_assessment: Dict
    purchase_recommendation: Dict


class ReservedCapacityPlanner:
    """Plan and optimize reserved capacity purchases"""
    
    # AWS Savings Plans discount rates (approximate)
    SP_DISCOUNT_RATES = {
        'compute': {
            1: {'no_upfront': 0.20, 'partial_upfront': 0.22, 'all_upfront': 0.24},
            3: {'no_upfront': 0.35, 'partial_upfront': 0.37, 'all_upfront': 0.40}
        },
        'ec2_instance': {
            1: {'no_upfront': 0.25, 'partial_upfront': 0.27, 'all_upfront': 0.30},
            3: {'no_upfront': 0.40, 'partial_upfront': 0.42, 'all_upfront': 0.45}
        }
    }
    
    # Azure Reserved VM discount rates
    AZURE_RI_DISCOUNT_RATES = {
        1: {'no_upfront': 0.30, 'upfront': 0.35},
        3: {'no_upfront': 0.45, 'upfront': 0.50},
        5: {'no_upfront': 0.55, 'upfront': 0.60}
    }
    
    def __init__(self, 
                 min_confidence_threshold: float = 0.80,
                 min_savings_threshold: float = 100):
        self.min_confidence_threshold = min_confidence_threshold
        self.min_savings_threshold = min_savings_threshold
        
    def analyze_usage_patterns(self, 
                               usage_data: pd.DataFrame,
                               forecast_days: int = 90) -> Dict:
        """
        Analyze historical usage patterns for commitment planning
        
        Args:
            usage_data: DataFrame with columns: timestamp, instance_type, region, hours
            forecast_days: Number of days to forecast
            
        Returns:
            Dictionary with usage analysis
        """
        analysis = {
            'instance_families': {},
            'regions': {},
            'overall_stability': 0.0,
            'recommendations_ready': False
        }
        
        # Group by instance family
        usage_data['instance_family'] = usage_data['instance_type'].apply(
            lambda x: x.split('.')[0] if '.' in x else x
        )
        
        for family in usage_data['instance_family'].unique():
            family_data = usage_data[usage_data['instance_family'] == family]
            
            # Calculate daily usage
            daily_usage = family_data.groupby(
                pd.Grouper(key='timestamp', freq='D')
            )['hours'].sum()
            
            # Calculate stability metrics
            stability = self._calculate_stability(daily_usage)
            
            # Forecast future usage
            forecast = self._forecast_usage(daily_usage, forecast_days)
            
            analysis['instance_families'][family] = {
                'avg_daily_hours': daily_usage.mean(),
                'std_daily_hours': daily_usage.std(),
                'stability_score': stability,
                'min_daily_hours': daily_usage.min(),
                'max_daily_hours': daily_usage.max(),
                'forecast': forecast,
                'recommended_commitment': self._calculate_commitment_level(
                    daily_usage, stability
                )
            }
        
        # Calculate overall stability
        stability_scores = [
            v['stability_score'] for v in analysis['instance_families'].values()
        ]
        analysis['overall_stability'] = np.mean(stability_scores) if stability_scores else 0
        analysis['recommendations_ready'] = analysis['overall_stability'] >= 0.7
        
        return analysis
    
    def _calculate_stability(self, daily_usage: pd.Series) -> float:
        """Calculate usage stability score (0-1)"""
        if daily_usage.empty or daily_usage.mean() == 0:
            return 0.0
        
        # Coefficient of variation (lower is more stable)
        cv = daily_usage.std() / daily_usage.mean()
        
        # Convert to stability score (higher is more stable)
        stability = max(0, 1 - cv)
        
        return stability
    
    def _forecast_usage(self, 
                        daily_usage: pd.Series,
                        forecast_days: int) -> List[float]:
        """Forecast future usage using simple exponential smoothing"""
        
        if len(daily_usage) < 7:
            return [daily_usage.mean()] * forecast_days
        
        # Simple exponential smoothing
        alpha = 0.3
        forecast = [daily_usage.iloc[-1]]
        
        for _ in range(forecast_days - 1):
            next_val = alpha * daily_usage.iloc[-1] + (1 - alpha) * forecast[-1]
            forecast.append(next_val)
        
        return forecast
    
    def _calculate_commitment_level(self,
                                     daily_usage: pd.Series,
                                     stability: float) -> float:
        """Calculate recommended commitment level based on usage and stability"""
        
        if stability < 0.5:
            # Low stability - conservative commitment
            return daily_usage.quantile(0.3)
        elif stability < 0.7:
            # Medium stability - moderate commitment
            return daily_usage.quantile(0.5)
        else:
            # High stability - aggressive commitment
            return daily_usage.quantile(0.7)
    
    def generate_savings_plans_recommendation(
        self,
        usage_analysis: Dict,
        commitment_type: CommitmentType,
        term_years: int = 1,
        payment_option: str = 'partial_upfront'
    ) -> List[CommitmentRecommendation]:
        """Generate Savings Plans purchase recommendations"""
        
        recommendations = []
        
        if commitment_type == CommitmentType.AWS_SAVINGS_PLANS:
            for family, data in usage_analysis['instance_families'].items():
                if data['stability_score'] < self.min_confidence_threshold:
                    continue
                
                hourly_commitment = data['recommended_commitment'] / 24
                
                # Get discount rate
                discount = self.SP_DISCOUNT_RATES['compute'][term_years].get(
                    payment_option, 0.20
                )
                
                # Calculate costs
                on_demand_rate = self._get_on_demand_rate(family)
                discounted_rate = on_demand_rate * (1 - discount)
                
                hours_per_year = 8760
                total_hours = hours_per_year * term_years
                
                on_demand_cost = hourly_commitment * on_demand_rate * total_hours
                committed_cost = hourly_commitment * discounted_rate * total_hours
                
                # Adjust for payment option
                if payment_option == 'all_upfront':
                    upfront_cost = committed_cost
                    monthly_cost = 0
                elif payment_option == 'partial_upfront':
                    upfront_cost = committed_cost * 0.5
                    monthly_cost = (committed_cost * 0.5) / (term_years * 12)
                else:
                    upfront_cost = 0
                    monthly_cost = committed_cost / (term_years * 12)
                
                savings = on_demand_cost - committed_cost
                savings_percent = (savings / on_demand_cost * 100) if on_demand_cost > 0 else 0
                
                if savings >= self.min_savings_threshold:
                    recommendation = CommitmentRecommendation(
                        commitment_type=commitment_type,
                        resource_type=family,
                        region='all',
                        term_years=term_years,
                        payment_option=payment_option,
                        hourly_commitment=hourly_commitment,
                        upfront_cost=upfront_cost,
                        monthly_cost=monthly_cost,
                        total_cost=committed_cost,
                        on_demand_equivalent=on_demand_cost,
                        estimated_savings=savings,
                        savings_percent=savings_percent,
                        confidence=data['stability_score'],
                        utilization_forecast=data['forecast'],
                        risk_assessment=self._assess_commitment_risk(
                            data, hourly_commitment
                        ),
                        purchase_recommendation={
                            'recommended_action': 'purchase',
                            'priority': 'high' if savings > 1000 else 'medium',
                            'timeline': 'immediate'
                        }
                    )
                    recommendations.append(recommendation)
        
        # Sort by estimated savings
        recommendations.sort(key=lambda x: x.estimated_savings, reverse=True)
        
        return recommendations
    
    def _get_on_demand_rate(self, instance_family: str) -> float:
        """Get approximate on-demand rate for instance family"""
        
        # Approximate rates per vCPU-hour
        rates = {
            't3': 0.0416,
            't3a': 0.0376,
            'm5': 0.096,
            'm5a': 0.086,
            'm6g': 0.077,
            'c5': 0.085,
            'c6g': 0.068,
            'r5': 0.126,
            'r6g': 0.1008,
        }
        
        return rates.get(instance_family, 0.1)
    
    def _assess_commitment_risk(self,
                                 usage_data: Dict,
                                 commitment: float) -> Dict:
        """Assess risk of commitment"""
        
        min_usage = usage_data['min_daily_hours'] / 24
        max_usage = usage_data['max_daily_hours'] / 24
        
        # Risk of under-utilization
        underutilization_risk = max(0, (commitment - max_usage) / commitment) if commitment > 0 else 0
        
        # Risk of over-commitment
        overcommitment_risk = max(0, (commitment - min_usage) / commitment) if commitment > 0 else 0
        
        return {
            'underutilization_risk': underutilization_risk,
            'overcommitment_risk': overcommitment_risk,
            'overall_risk': 'low' if underutilization_risk < 0.1 else 'medium' if underutilization_risk < 0.3 else 'high',
            'risk_factors': [
                f"Minimum hourly usage: {min_usage:.2f}",
                f"Maximum hourly usage: {max_usage:.2f}",
                f"Recommended commitment: {commitment:.2f}",
                f"Stability score: {usage_data['stability_score']:.2%}"
            ]
        }
    
    def generate_purchase_schedule(self,
                                    recommendations: List[CommitmentRecommendation],
                                    budget_constraint: float = None) -> Dict:
        """Generate purchase schedule based on recommendations and budget"""
        
        schedule = {
            'immediate_purchases': [],
            'phased_purchases': [],
            'total_upfront_required': 0,
            'total_monthly_commitment': 0,
            'total_estimated_savings': 0
        }
        
        remaining_budget = budget_constraint or float('inf')
        
        for rec in recommendations:
            if rec.upfront_cost <= remaining_budget:
                schedule['immediate_purchases'].append({
                    'type': rec.commitment_type.value,
                    'resource': rec.resource_type,
                    'term': rec.term_years,
                    'hourly_commitment': rec.hourly_commitment,
                    'upfront_cost': rec.upfront_cost,
                    'monthly_cost': rec.monthly_cost,
                    'estimated_savings': rec.estimated_savings,
                    'confidence': rec.confidence
                })
                remaining_budget -= rec.upfront_cost
                schedule['total_upfront_required'] += rec.upfront_cost
                schedule['total_monthly_commitment'] += rec.monthly_cost
                schedule['total_estimated_savings'] += rec.estimated_savings
            else:
                schedule['phased_purchases'].append({
                    'type': rec.commitment_type.value,
                    'resource': rec.resource_type,
                    'term': rec.term_years,
                    'hourly_commitment': rec.hourly_commitment,
                    'upfront_cost': rec.upfront_cost,
                    'monthly_cost': rec.monthly_cost,
                    'estimated_savings': rec.estimated_savings,
                    'reason': 'Budget constraint'
                })
        
        return schedule


class CommitmentOptimizer:
    """Optimize existing commitments and identify waste"""
    
    def __init__(self):
        self.utilization_threshold = 0.80
        
    def analyze_commitment_utilization(self,
                                        commitments: List[Dict],
                                        actual_usage: pd.DataFrame) -> Dict:
        """Analyze utilization of existing commitments"""
        
        analysis = {
            'well_utilized': [],
            'under_utilized': [],
            'wasted_commitments': [],
            'optimization_opportunities': []
        }
        
        for commitment in commitments:
            commitment_id = commitment['id']
            hourly_commitment = commitment['hourly_commitment']
            
            # Get actual usage for this commitment
            usage = actual_usage[
                actual_usage['commitment_id'] == commitment_id
            ]
            
            if usage.empty:
                analysis['wasted_commitments'].append({
                    'commitment_id': commitment_id,
                    'reason': 'No usage found',
                    'action': 'review_and_exchange'
                })
                continue
            
            # Calculate utilization
            actual_hours = usage['hours'].sum()
            committed_hours = hourly_commitment * len(usage)
            utilization = actual_hours / committed_hours if committed_hours > 0 else 0
            
            if utilization >= self.utilization_threshold:
                analysis['well_utilized'].append({
                    'commitment_id': commitment_id,
                    'utilization': utilization,
                    'status': 'optimal'
                })
            elif utilization >= 0.5:
                analysis['under_utilized'].append({
                    'commitment_id': commitment_id,
                    'utilization': utilization,
                    'recommendation': 'monitor',
                    'action': 'track_usage_trends'
                })
            else:
                analysis['wasted_commitments'].append({
                    'commitment_id': commitment_id,
                    'utilization': utilization,
                    'wasted_hours': committed_hours - actual_hours,
                    'estimated_waste': (committed_hours - actual_hours) * commitment.get('hourly_rate', 0),
                    'action': 'exchange_or_modify'
                })
        
        return analysis


# Usage example
if __name__ == "__main__":
    # Create sample usage data
    dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
    
    usage_data = pd.DataFrame({
        'timestamp': list(dates) * 2,
        'instance_type': ['m5.large'] * 90 + ['c5.xlarge'] * 90,
        'region': ['us-east-1'] * 180,
        'hours': list(np.random.normal(20, 3, 90).clip(10, 24)) + 
                 list(np.random.normal(22, 2, 90).clip(15, 24))
    })
    
    planner = ReservedCapacityPlanner()
    
    # Analyze usage patterns
    analysis = planner.analyze_usage_patterns(usage_data)
    
    print("Usage Analysis:")
    print(f"Overall Stability: {analysis['overall_stability']:.2%}")
    print(f"Recommendations Ready: {analysis['recommendations_ready']}")
    
    for family, data in analysis['instance_families'].items():
        print(f"\n{family}:")
        print(f"  Avg Daily Hours: {data['avg_daily_hours']:.1f}")
        print(f"  Stability Score: {data['stability_score']:.2%}")
        print(f"  Recommended Commitment: {data['recommended_commitment']:.1f} hours/day")
    
    # Generate recommendations
    recommendations = planner.generate_savings_plans_recommendation(
        analysis,
        CommitmentType.AWS_SAVINGS_PLANS,
        term_years=1,
        payment_option='partial_upfront'
    )
    
    print("\n\nSavings Plans Recommendations:")
    for rec in recommendations:
        print(f"\n{rec.resource_type}:")
        print(f"  Hourly Commitment: {rec.hourly_commitment:.2f} hours")
        print(f"  Upfront Cost: ${rec.upfront_cost:,.2f}")
        print(f"  Monthly Cost: ${rec.monthly_cost:,.2f}")
        print(f"  Estimated Savings: ${rec.estimated_savings:,.2f} ({rec.savings_percent:.1f}%)")
        print(f"  Confidence: {rec.confidence:.2%}")


---

## 5. Spot Instance Optimization

### 5.1 Spot Instance Manager

```python
# /app/cost_optimization/spot_instances/manager.py
"""
Spot instance management and optimization for fault-tolerant workloads
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SpotStrategy(Enum):
    """Spot instance allocation strategies"""
    DIVERSIFIED = "diversified"
    LOWEST_PRICE = "lowestPrice"
    CAPACITY_OPTIMIZED = "capacityOptimized"
    PRICE_CAPACITY_OPTIMIZED = "priceCapacityOptimized"


@dataclass
class SpotInstanceRecommendation:
    """Spot instance recommendation"""
    instance_type: str
    region: str
    availability_zone: str
    spot_price: float
    on_demand_price: float
    savings_percent: float
    interruption_frequency: str
    recommendation_score: float
    suitable_workloads: List[str]
    risk_level: str


class SpotPriceAnalyzer:
    """Analyze spot prices and trends"""
    
    def __init__(self):
        self.price_history_days = 30
        self.interruption_thresholds = {
            'very_low': 0.05,
            'low': 0.10,
            'medium': 0.20,
            'high': 0.35
        }
    
    async def get_current_spot_prices(self,
                                       instance_types: List[str],
                                       regions: List[str]) -> Dict[str, List[SpotInstanceRecommendation]]:
        """Get current spot prices for instance types"""
        
        recommendations = {}
        
        for region in regions:
            region_recommendations = []
            
            for instance_type in instance_types:
                # In production, this would call AWS EC2 API
                # For demo, generating realistic data
                spot_price = await self._get_spot_price(instance_type, region)
                on_demand = self._get_on_demand_price(instance_type)
                
                if spot_price and on_demand:
                    savings = (on_demand - spot_price) / on_demand * 100
                    interruption_freq = self._estimate_interruption_frequency(
                        instance_type, region
                    )
                    
                    score = self._calculate_recommendation_score(
                        savings, interruption_freq
                    )
                    
                    recommendation = SpotInstanceRecommendation(
                        instance_type=instance_type,
                        region=region,
                        availability_zone=f"{region}a",
                        spot_price=spot_price,
                        on_demand_price=on_demand,
                        savings_percent=savings,
                        interruption_frequency=interruption_freq,
                        recommendation_score=score,
                        suitable_workloads=self._get_suitable_workloads(interruption_freq),
                        risk_level=self._assess_risk(interruption_freq)
                    )
                    region_recommendations.append(recommendation)
            
            # Sort by recommendation score
            region_recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)
            recommendations[region] = region_recommendations
        
        return recommendations
    
    async def _get_spot_price(self, instance_type: str, region: str) -> Optional[float]:
        """Get current spot price (simulated for demo)"""
        
        # Simulated spot prices (typically 50-90% of on-demand)
        base_prices = {
            'm5.large': 0.096,
            'm5.xlarge': 0.192,
            'm5.2xlarge': 0.384,
            'c5.large': 0.085,
            'c5.xlarge': 0.17,
            'c5.2xlarge': 0.34,
            'r5.large': 0.126,
            'r5.xlarge': 0.252,
            't3.medium': 0.0416,
            't3.large': 0.0832,
        }
        
        base = base_prices.get(instance_type)
        if base:
            # Spot price is typically 30-70% of on-demand
            discount = random.uniform(0.30, 0.70)
            return base * (1 - discount)
        
        return None
    
    def _get_on_demand_price(self, instance_type: str) -> float:
        """Get on-demand price"""
        prices = {
            'm5.large': 0.096,
            'm5.xlarge': 0.192,
            'm5.2xlarge': 0.384,
            'c5.large': 0.085,
            'c5.xlarge': 0.17,
            'c5.2xlarge': 0.34,
            'r5.large': 0.126,
            'r5.xlarge': 0.252,
            't3.medium': 0.0416,
            't3.large': 0.0832,
        }
        return prices.get(instance_type, 0.1)
    
    def _estimate_interruption_frequency(self, instance_type: str, region: str) -> str:
        """Estimate interruption frequency based on instance characteristics"""
        
        # Smaller instances typically have lower interruption rates
        if 'large' in instance_type and 'xlarge' not in instance_type and '2xlarge' not in instance_type:
            return random.choice(['very_low', 'low', 'low'])
        elif 't3' in instance_type:
            return random.choice(['low', 'medium'])
        else:
            return random.choice(['medium', 'high'])
    
    def _calculate_recommendation_score(self, 
                                         savings_percent: float,
                                         interruption_frequency: str) -> float:
        """Calculate overall recommendation score"""
        
        # Weight savings higher than interruption risk
        savings_weight = 0.6
        stability_weight = 0.4
        
        # Normalize savings (0-100 scale)
        savings_score = min(savings_percent, 100) / 100
        
        # Stability score based on interruption frequency
        stability_scores = {
            'very_low': 1.0,
            'low': 0.8,
            'medium': 0.5,
            'high': 0.2
        }
        stability_score = stability_scores.get(interruption_frequency, 0.5)
        
        return (savings_score * savings_weight) + (stability_score * stability_weight)
    
    def _get_suitable_workloads(self, interruption_frequency: str) -> List[str]:
        """Get list of suitable workloads based on interruption frequency"""
        
        workload_mapping = {
            'very_low': [
                'batch_processing',
                'data_analytics',
                'machine_learning_training',
                'ci_cd_runners',
                'stateless_web_services'
            ],
            'low': [
                'batch_processing',
                'data_analytics',
                'ci_cd_runners',
                'container_workloads'
            ],
            'medium': [
                'batch_processing',
                'data_processing',
                'queue_workers'
            ],
            'high': [
                'fault_tolerant_batch_jobs',
                'checkpoint_enabled_workloads'
            ]
        }
        
        return workload_mapping.get(interruption_frequency, ['batch_processing'])
    
    def _assess_risk(self, interruption_frequency: str) -> str:
        """Assess risk level"""
        risk_map = {
            'very_low': 'low',
            'low': 'low',
            'medium': 'medium',
            'high': 'high'
        }
        return risk_map.get(interruption_frequency, 'medium')


class SpotFleetManager:
    """Manage spot fleet configurations"""
    
    def __init__(self):
        self.default_strategies = {
            'diversified': SpotStrategy.DIVERSIFIED,
            'capacity_optimized': SpotStrategy.CAPACITY_OPTIMIZED
        }
    
    def create_fleet_config(self,
                           workload_name: str,
                           target_capacity: int,
                           instance_types: List[str],
                           regions: List[str],
                           strategy: SpotStrategy = SpotStrategy.DIVERSIFIED) -> Dict:
        """Create optimized spot fleet configuration"""
        
        config = {
            'workload_name': workload_name,
            'target_capacity': target_capacity,
            'allocation_strategy': strategy.value,
            'instance_pools_to_use_count': min(4, len(instance_types)),
            'launch_template_configs': [],
            'spot_options': {
                'allocation_strategy': strategy.value,
                'instance_interruption_behavior': 'terminate',
                'single_instance_type': False,
                'single_availability_zone': False
            },
            'on_demand_options': {
                'allocation_strategy': 'lowestPrice',
                'single_instance_type': False,
                'single_availability_zone': False
            },
            'target_capacity_specification': {
                'total_target_capacity': target_capacity,
                'on_demand_target_capacity': int(target_capacity * 0.2),  # 20% on-demand
                'spot_target_capacity': int(target_capacity * 0.8),  # 80% spot
                'default_target_capacity_type': 'spot'
            }
        }
        
        # Create launch template configs for each instance type
        for instance_type in instance_types:
            config['launch_template_configs'].append({
                'launch_template_specification': {
                    'launch_template_name': f'{workload_name}-template',
                    'version': '$Latest'
                },
                'overrides': [
                    {
                        'instance_type': instance_type,
                        'subnet_id': f'subnet-{region}'
                    }
                    for region in regions
                ]
            })
        
        return config
    
    def create_auto_scaling_group_config(self,
                                          asg_name: str,
                                          min_size: int,
                                          max_size: int,
                                          desired_capacity: int,
                                          instance_types: List[str],
                                          on_demand_percentage: int = 20) -> Dict:
        """Create mixed instances policy for Auto Scaling Group"""
        
        return {
            'AutoScalingGroupName': asg_name,
            'MixedInstancesPolicy': {
                'LaunchTemplate': {
                    'LaunchTemplateSpecification': {
                        'LaunchTemplateName': f'{asg_name}-template',
                        'Version': '$Latest'
                    },
                    'Overrides': [
                        {'InstanceType': it} for it in instance_types
                    ]
                },
                'InstancesDistribution': {
                    'OnDemandAllocationStrategy': 'prioritized',
                    'OnDemandBaseCapacity': max(1, int(desired_capacity * on_demand_percentage / 100)),
                    'OnDemandPercentageAboveBaseCapacity': on_demand_percentage,
                    'SpotAllocationStrategy': 'capacity-optimized',
                    'SpotInstancePools': min(4, len(instance_types))
                }
            },
            'MinSize': min_size,
            'MaxSize': max_size,
            'DesiredCapacity': desired_capacity,
            'HealthCheckType': 'EC2',
            'HealthCheckGracePeriod': 300,
            'TerminationPolicies': ['OldestInstance', 'Default']
        }


class SpotInterruptionHandler:
    """Handle spot instance interruptions gracefully"""
    
    def __init__(self):
        self.interruption_buffer_seconds = 120
    
    async def monitor_interruptions(self):
        """Monitor for spot instance interruption notices"""
        
        # In production, this would poll the EC2 metadata service
        # http://169.254.169.254/latest/meta-data/spot/instance-action
        
        while True:
            try:
                # Check for interruption notices
                interruption_notice = await self._check_interruption_notice()
                
                if interruption_notice:
                    await self._handle_interruption(interruption_notice)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring interruptions: {e}")
                await asyncio.sleep(10)
    
    async def _check_interruption_notice(self) -> Optional[Dict]:
        """Check for spot instance interruption notice"""
        # Simulated for demo
        return None
    
    async def _handle_interruption(self, notice: Dict):
        """Handle spot instance interruption"""
        
        instance_id = notice.get('instance_id')
        action = notice.get('action')  # 'terminate', 'stop', 'hibernate'
        time = notice.get('time')
        
        logger.warning(f"Spot interruption notice received for {instance_id}: {action}")
        
        # Actions to take before interruption:
        # 1. Drain connections from load balancer
        await self._drain_connections(instance_id)
        
        # 2. Save checkpoint/state
        await self._save_checkpoint(instance_id)
        
        # 3. Complete in-progress tasks
        await self._complete_tasks(instance_id)
        
        # 4. Notify monitoring
        await self._notify_interruption(instance_id, action)
    
    async def _drain_connections(self, instance_id: str):
        """Drain connections from load balancer"""
        logger.info(f"Draining connections from {instance_id}")
        # Implementation would deregister from target groups
    
    async def _save_checkpoint(self, instance_id: str):
        """Save application state/checkpoint"""
        logger.info(f"Saving checkpoint for {instance_id}")
        # Implementation depends on application
    
    async def _complete_tasks(self, instance_id: str):
        """Complete in-progress tasks"""
        logger.info(f"Completing tasks on {instance_id}")
        # Implementation depends on workload type
    
    async def _notify_interruption(self, instance_id: str, action: str):
        """Notify monitoring systems of interruption"""
        logger.info(f"Notifying systems of interruption: {instance_id} - {action}")


class SpotSavingsCalculator:
    """Calculate savings from spot instance usage"""
    
    def calculate_savings(self,
                         spot_usage: pd.DataFrame,
                         on_demand_prices: Dict[str, float]) -> Dict:
        """Calculate total savings from spot usage"""
        
        total_spot_cost = 0
        total_on_demand_cost = 0
        
        for _, row in spot_usage.iterrows():
            instance_type = row['instance_type']
            hours = row['hours']
            spot_price = row['spot_price']
            on_demand_price = on_demand_prices.get(instance_type, 0)
            
            total_spot_cost += hours * spot_price
            total_on_demand_cost += hours * on_demand_price
        
        savings = total_on_demand_cost - total_spot_cost
        savings_percent = (savings / total_on_demand_cost * 100) if total_on_demand_cost > 0 else 0
        
        return {
            'total_spot_cost': total_spot_cost,
            'total_on_demand_equivalent': total_on_demand_cost,
            'total_savings': savings,
            'savings_percent': savings_percent,
            'instance_breakdown': self._calculate_instance_breakdown(spot_usage, on_demand_prices)
        }
    
    def _calculate_instance_breakdown(self,
                                      spot_usage: pd.DataFrame,
                                      on_demand_prices: Dict[str, float]) -> List[Dict]:
        """Calculate savings breakdown by instance type"""
        
        breakdown = []
        
        for instance_type in spot_usage['instance_type'].unique():
            type_usage = spot_usage[spot_usage['instance_type'] == instance_type]
            
            hours = type_usage['hours'].sum()
            avg_spot_price = type_usage['spot_price'].mean()
            on_demand_price = on_demand_prices.get(instance_type, 0)
            
            spot_cost = hours * avg_spot_price
            on_demand_cost = hours * on_demand_price
            savings = on_demand_cost - spot_cost
            
            breakdown.append({
                'instance_type': instance_type,
                'total_hours': hours,
                'avg_spot_price': avg_spot_price,
                'on_demand_price': on_demand_price,
                'spot_cost': spot_cost,
                'on_demand_cost': on_demand_cost,
                'savings': savings,
                'savings_percent': (savings / on_demand_cost * 100) if on_demand_cost > 0 else 0
            })
        
        return sorted(breakdown, key=lambda x: x['savings'], reverse=True)


# Usage example
if __name__ == "__main__":
    import pandas as pd
    
    async def main():
        analyzer = SpotPriceAnalyzer()
        
        # Get spot price recommendations
        recommendations = await analyzer.get_current_spot_prices(
            instance_types=['m5.large', 'm5.xlarge', 'c5.large', 'c5.xlarge'],
            regions=['us-east-1', 'us-west-2']
        )
        
        print("Spot Instance Recommendations:\n")
        
        for region, recs in recommendations.items():
            print(f"\n{region}:")
            print("-" * 80)
            
            for rec in recs[:5]:  # Top 5 recommendations
                print(f"  {rec.instance_type}:")
                print(f"    Spot Price: ${rec.spot_price:.4f}/hr")
                print(f"    On-Demand: ${rec.on_demand_price:.4f}/hr")
                print(f"    Savings: {rec.savings_percent:.1f}%")
                print(f"    Interruption Risk: {rec.interruption_frequency}")
                print(f"    Score: {rec.recommendation_score:.2f}")
                print(f"    Suitable for: {', '.join(rec.suitable_workloads[:3])}")
                print()
    
    asyncio.run(main())
```

---

## 6. Cost Allocation & Tagging

### 6.1 Cost Allocation System

```python
# /app/cost_optimization/allocation/allocator.py
"""
Cost allocation and chargeback system for ResilienceAI
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class AllocationMethod(Enum):
    """Cost allocation methods"""
    DIRECT = "direct"
    PROPORTIONAL = "proportional"
    EQUAL = "equal"
    WEIGHTED = "weighted"


@dataclass
class CostAllocation:
    """Cost allocation record"""
    cost_center: str
    team: str
    project: str
    environment: str
    service: str
    resource_id: str
    cost: float
    currency: str
    period: str
    allocation_percentage: float
    allocated_from: str
    tags: Dict[str, str]


class CostAllocationEngine:
    """Engine for allocating costs across teams and projects"""
    
    # Required tags for cost allocation
    REQUIRED_TAGS = [
        'CostCenter',
        'Team',
        'Project',
        'Environment',
        'Owner'
    ]
    
    # Tag compliance rules
    TAG_RULES = {
        'CostCenter': {
            'required': True,
            'allowed_values': ['engineering', 'data-science', 'platform', 'operations', 'security'],
            'default': 'engineering'
        },
        'Team': {
            'required': True,
            'allowed_values': None,  # Any value allowed
            'default': 'unassigned'
        },
        'Project': {
            'required': True,
            'allowed_values': None,
            'default': 'shared'
        },
        'Environment': {
            'required': True,
            'allowed_values': ['production', 'staging', 'development', 'testing'],
            'default': 'development'
        },
        'Owner': {
            'required': True,
            'allowed_values': None,
            'default': 'unassigned'
        }
    }
    
    def __init__(self):
        self.shared_resource_allocations = {}
        
    def allocate_costs(self,
                      cost_records: List[Dict],
                      allocation_period: str) -> List[CostAllocation]:
        """
        Allocate costs based on tags and rules
        
        Args:
            cost_records: List of cost records with tags
            allocation_period: Period for allocation (e.g., '2024-01')
            
        Returns:
            List of allocated cost records
        """
        allocations = []
        
        for record in cost_records:
            tags = record.get('tags', {})
            
            # Validate and normalize tags
            normalized_tags = self._normalize_tags(tags)
            
            # Check if this is a shared resource
            if self._is_shared_resource(record):
                shared_allocations = self._allocate_shared_resource(
                    record, normalized_tags, allocation_period
                )
                allocations.extend(shared_allocations)
            else:
                # Direct allocation
                allocation = CostAllocation(
                    cost_center=normalized_tags.get('CostCenter', 'engineering'),
                    team=normalized_tags.get('Team', 'unassigned'),
                    project=normalized_tags.get('Project', 'shared'),
                    environment=normalized_tags.get('Environment', 'development'),
                    service=record.get('service', 'unknown'),
                    resource_id=record.get('resource_id', 'unknown'),
                    cost=record.get('cost', 0),
                    currency=record.get('currency', 'USD'),
                    period=allocation_period,
                    allocation_percentage=100.0,
                    allocated_from='direct',
                    tags=normalized_tags
                )
                allocations.append(allocation)
        
        return allocations
    
    def _normalize_tags(self, tags: Dict[str, str]) -> Dict[str, str]:
        """Normalize and validate tags"""
        normalized = {}
        
        for tag_name, rules in self.TAG_RULES.items():
            value = tags.get(tag_name, tags.get(tag_name.lower(), ''))
            
            # Check if value is allowed
            if rules['allowed_values'] and value not in rules['allowed_values']:
                value = rules['default']
            
            # Use default if empty
            if not value:
                value = rules['default']
            
            normalized[tag_name] = value
        
        return normalized
    
    def _is_shared_resource(self, record: Dict) -> bool:
        """Determine if resource is shared across teams"""
        tags = record.get('tags', {})
        
        # Check for shared indicators
        shared_indicators = [
            tags.get('Project') == 'shared',
            tags.get('Team') == 'platform',
            'vpc' in record.get('service', '').lower(),
            'loadbalancer' in record.get('service', '').lower(),
            'nat' in record.get('resource_id', '').lower()
        ]
        
        return any(shared_indicators)
    
    def _allocate_shared_resource(self,
                                   record: Dict,
                                   tags: Dict[str, str],
                                   period: str) -> List[CostAllocation]:
        """Allocate shared resource costs proportionally"""
        
        allocations = []
        total_cost = record.get('cost', 0)
        service = record.get('service', 'unknown')
        resource_id = record.get('resource_id', 'unknown')
        
        # Get allocation weights for this shared resource
        weights = self._get_shared_resource_weights(service, period)
        
        if not weights:
            # No weights defined, allocate equally to all teams
            weights = self._get_default_weights(period)
        
        # Normalize weights
        total_weight = sum(weights.values())
        
        for team, weight in weights.items():
            percentage = (weight / total_weight) * 100
            allocated_cost = total_cost * (weight / total_weight)
            
            allocation = CostAllocation(
                cost_center=tags.get('CostCenter', 'engineering'),
                team=team,
                project=tags.get('Project', 'shared'),
                environment=tags.get('Environment', 'development'),
                service=service,
                resource_id=resource_id,
                cost=allocated_cost,
                currency=record.get('currency', 'USD'),
                period=period,
                allocation_percentage=percentage,
                allocated_from=f'shared:{resource_id}',
                tags=tags
            )
            allocations.append(allocation)
        
        return allocations
    
    def _get_shared_resource_weights(self, service: str, period: str) -> Dict[str, float]:
        """Get allocation weights for shared resources"""
        
        # In production, this would come from a database
        # Based on team usage patterns
        default_weights = {
            'data-science': 0.30,
            'ml-platform': 0.25,
            'inference': 0.20,
            'data-engineering': 0.15,
            'platform': 0.10
        }
        
        return default_weights
    
    def _get_default_weights(self, period: str) -> Dict[str, float]:
        """Get default allocation weights"""
        return {
            'data-science': 0.20,
            'ml-platform': 0.20,
            'inference': 0.20,
            'data-engineering': 0.20,
            'platform': 0.20
        }
    
    def generate_chargeback_report(self,
                                    allocations: List[CostAllocation],
                                    period: str) -> Dict:
        """Generate chargeback report by team and project"""
        
        report = {
            'period': period,
            'generated_at': datetime.now().isoformat(),
            'summary': {},
            'by_team': {},
            'by_project': {},
            'by_environment': {},
            'by_service': {},
            'untagged_costs': 0
        }
        
        for allocation in allocations:
            # Team breakdown
            team = allocation.team
            if team not in report['by_team']:
                report['by_team'][team] = {
                    'total_cost': 0,
                    'resources': [],
                    'by_project': {},
                    'by_environment': {}
                }
            
            report['by_team'][team]['total_cost'] += allocation.cost
            report['by_team'][team]['resources'].append({
                'resource_id': allocation.resource_id,
                'service': allocation.service,
                'cost': allocation.cost,
                'allocation_percentage': allocation.allocation_percentage
            })
            
            # Project breakdown within team
            project = allocation.project
            if project not in report['by_team'][team]['by_project']:
                report['by_team'][team]['by_project'][project] = 0
            report['by_team'][team]['by_project'][project] += allocation.cost
            
            # Environment breakdown
            env = allocation.environment
            if env not in report['by_environment']:
                report['by_environment'][env] = 0
            report['by_environment'][env] += allocation.cost
            
            # Service breakdown
            service = allocation.service
            if service not in report['by_service']:
                report['by_service'][service] = 0
            report['by_service'][service] += allocation.cost
            
            # Track untagged costs
            if allocation.team == 'unassigned' or allocation.project == 'shared':
                report['untagged_costs'] += allocation.cost
        
        # Calculate summary
        report['summary']['total_cost'] = sum(
            t['total_cost'] for t in report['by_team'].values()
        )
        report['summary']['total_teams'] = len(report['by_team'])
        report['summary']['untagged_percentage'] = (
            report['untagged_costs'] / report['summary']['total_cost'] * 100
            if report['summary']['total_cost'] > 0 else 0
        )
        
        return report


class TagComplianceChecker:
    """Check and enforce tag compliance"""
    
    def __init__(self):
        self.required_tags = [
            'CostCenter',
            'Team',
            'Project',
            'Environment',
            'Owner'
        ]
    
    def check_compliance(self, resources: List[Dict]) -> Dict:
        """Check tag compliance across resources"""
        
        compliance = {
            'total_resources': len(resources),
            'compliant_resources': 0,
            'non_compliant_resources': [],
            'tag_coverage': {tag: 0 for tag in self.required_tags},
            'compliance_rate': 0.0
        }
        
        for resource in resources:
            tags = resource.get('tags', {})
            missing_tags = []
            
            for required_tag in self.required_tags:
                if required_tag not in tags and required_tag.lower() not in tags:
                    missing_tags.append(required_tag)
                else:
                    compliance['tag_coverage'][required_tag] += 1
            
            if missing_tags:
                compliance['non_compliant_resources'].append({
                    'resource_id': resource.get('resource_id'),
                    'resource_type': resource.get('resource_type'),
                    'missing_tags': missing_tags
                })
            else:
                compliance['compliant_resources'] += 1
        
        # Calculate compliance rate
        compliance['compliance_rate'] = (
            compliance['compliant_resources'] / compliance['total_resources'] * 100
            if compliance['total_resources'] > 0 else 0
        )
        
        # Calculate tag coverage percentages
        for tag in compliance['tag_coverage']:
            compliance['tag_coverage'][tag] = (
                compliance['tag_coverage'][tag] / compliance['total_resources'] * 100
                if compliance['total_resources'] > 0 else 0
            )
        
        return compliance
    
    def generate_remediation_plan(self, compliance_report: Dict) -> List[Dict]:
        """Generate remediation plan for non-compliant resources"""
        
        remediations = []
        
        for resource in compliance_report['non_compliant_resources']:
            for missing_tag in resource['missing_tags']:
                remediations.append({
                    'resource_id': resource['resource_id'],
                    'resource_type': resource['resource_type'],
                    'missing_tag': missing_tag,
                    'action': 'add_tag',
                    'priority': 'high' if missing_tag in ['Team', 'Project'] else 'medium',
                    'automation_possible': True
                })
        
        return remediations


# Usage example
if __name__ == "__main__":
    # Sample cost records
    cost_records = [
        {
            'resource_id': 'i-1234567890abcdef0',
            'service': 'EC2',
            'cost': 150.50,
            'currency': 'USD',
            'tags': {
                'CostCenter': 'engineering',
                'Team': 'ml-platform',
                'Project': 'resilience-ai',
                'Environment': 'production',
                'Owner': 'team-ml@example.com'
            }
        },
        {
            'resource_id': 'vpc-12345678',
            'service': 'VPC',
            'cost': 350.00,
            'currency': 'USD',
            'tags': {
                'CostCenter': 'engineering',
                'Team': 'platform',
                'Project': 'shared',
                'Environment': 'production'
            }
        },
        {
            'resource_id': 'i-0987654321fedcba0',
            'service': 'EC2',
            'cost': 75.25,
            'currency': 'USD',
            'tags': {
                'CostCenter': 'data-science',
                'Team': 'data-science',
                'Project': 'model-training',
                'Environment': 'development'
                # Missing Owner tag
            }
        }
    ]
    
    # Allocate costs
    allocator = CostAllocationEngine()
    allocations = allocator.allocate_costs(cost_records, '2024-01')
    
    # Generate chargeback report
    report = allocator.generate_chargeback_report(allocations, '2024-01')
    
    print("Chargeback Report Summary:")
    print(f"Period: {report['period']}")
    print(f"Total Cost: ${report['summary']['total_cost']:,.2f}")
    print(f"Total Teams: {report['summary']['total_teams']}")
    print(f"Untagged Costs: ${report['untagged_costs']:,.2f} ({report['summary']['untagged_percentage']:.1f}%)")
    
    print("\nBy Team:")
    for team, data in report['by_team'].items():
        print(f"  {team}: ${data['total_cost']:,.2f}")
    
    print("\nBy Environment:")
    for env, cost in report['by_environment'].items():
        print(f"  {env}: ${cost:,.2f}")
    
    # Check tag compliance
    checker = TagComplianceChecker()
    compliance = checker.check_compliance(cost_records)
    
    print("\n\nTag Compliance:")
    print(f"Compliance Rate: {compliance['compliance_rate']:.1f}%")
    print(f"Compliant Resources: {compliance['compliant_resources']}/{compliance['total_resources']}")
    
    print("\nTag Coverage:")
    for tag, coverage in compliance['tag_coverage'].items():
        print(f"  {tag}: {coverage:.1f}%")
```

---

## 7. Budget Alerts & Forecasting

### 7.1 Budget Management System

```python
# /app/cost_optimization/budget/manager.py
"""
Budget management, alerts, and forecasting system
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from prophet import Prophet
import logging

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class BudgetStatus(Enum):
    """Budget status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    EXCEEDED = "exceeded"
    FORECAST_EXCEEDED = "forecast_exceeded"


@dataclass
class BudgetAlert:
    """Budget alert"""
    budget_id: str
    budget_name: str
    severity: AlertSeverity
    message: str
    current_spend: float
    budget_limit: float
    percentage_used: float
    forecasted_spend: float
    timestamp: datetime
    recommended_actions: List[str]


@dataclass
class Budget:
    """Budget definition"""
    budget_id: str
    name: str
    amount: float
    period: str  # 'monthly', 'quarterly', 'annual'
    start_date: datetime
    end_date: Optional[datetime]
    alert_thresholds: List[float]  # Percentages (e.g., [50, 80, 100])
    filters: Dict[str, List[str]]  # Tags, services, etc.
    notifications: List[str]  # Email addresses, SNS topics, etc.


class BudgetManager:
    """Manage budgets and generate alerts"""
    
    def __init__(self):
        self.budgets: Dict[str, Budget] = {}
        self.alert_history: List[BudgetAlert] = []
        
    def create_budget(self,
                      name: str,
                      amount: float,
                      period: str = 'monthly',
                      alert_thresholds: List[float] = None,
                      filters: Dict[str, List[str]] = None,
                      notifications: List[str] = None) -> Budget:
        """Create a new budget"""
        
        budget_id = f"budget-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        budget = Budget(
            budget_id=budget_id,
            name=name,
            amount=amount,
            period=period,
            start_date=datetime.now(),
            end_date=None,
            alert_thresholds=alert_thresholds or [50, 80, 100],
            filters=filters or {},
            notifications=notifications or []
        )
        
        self.budgets[budget_id] = budget
        logger.info(f"Created budget: {name} (${amount:,.2f})")
        
        return budget
    
    def check_budgets(self,
                      current_spend: Dict[str, float],
                      forecasted_spend: Dict[str, float] = None) -> List[BudgetAlert]:
        """Check all budgets and generate alerts"""
        
        alerts = []
        forecasted_spend = forecasted_spend or {}
        
        for budget_id, budget in self.budgets.items():
            spend = current_spend.get(budget_id, 0)
            forecast = forecasted_spend.get(budget_id, spend)
            
            percentage_used = (spend / budget.amount * 100) if budget.amount > 0 else 0
            forecast_percentage = (forecast / budget.amount * 100) if budget.amount > 0 else 0
            
            # Check alert thresholds
            for threshold in sorted(budget.alert_thresholds, reverse=True):
                if percentage_used >= threshold:
                    severity = self._get_severity(threshold, percentage_used)
                    
                    alert = BudgetAlert(
                        budget_id=budget_id,
                        budget_name=budget.name,
                        severity=severity,
                        message=self._generate_alert_message(
                            budget, spend, percentage_used, threshold
                        ),
                        current_spend=spend,
                        budget_limit=budget.amount,
                        percentage_used=percentage_used,
                        forecasted_spend=forecast,
                        timestamp=datetime.now(),
                        recommended_actions=self._get_recommended_actions(
                            severity, percentage_used
                        )
                    )
                    alerts.append(alert)
                    break
            
            # Check forecast
            if forecast_percentage > 100 and percentage_used < 100:
                alert = BudgetAlert(
                    budget_id=budget_id,
                    budget_name=budget.name,
                    severity=AlertSeverity.WARNING,
                    message=f"Forecast indicates budget will be exceeded by {forecast_percentage - 100:.1f}%",
                    current_spend=spend,
                    budget_limit=budget.amount,
                    percentage_used=percentage_used,
                    forecasted_spend=forecast,
                    timestamp=datetime.now(),
                    recommended_actions=[
                        'Review resource usage trends',
                        'Implement cost optimization measures',
                        'Consider increasing budget or reducing usage'
                    ]
                )
                alerts.append(alert)
        
        self.alert_history.extend(alerts)
        return alerts
    
    def _get_severity(self, threshold: float, percentage_used: float) -> AlertSeverity:
        """Determine alert severity"""
        if percentage_used >= 100:
            return AlertSeverity.CRITICAL
        elif percentage_used >= 80:
            return AlertSeverity.WARNING
        else:
            return AlertSeverity.INFO
    
    def _generate_alert_message(self,
                                 budget: Budget,
                                 spend: float,
                                 percentage_used: float,
                                 threshold: float) -> str:
        """Generate alert message"""
        
        if percentage_used >= 100:
            return f"Budget '{budget.name}' has been exceeded! Spent: ${spend:,.2f} / ${budget.amount:,.2f} ({percentage_used:.1f}%)"
        else:
            return f"Budget '{budget.name}' has reached {threshold}% threshold. Spent: ${spend:,.2f} / ${budget.amount:,.2f} ({percentage_used:.1f}%)"
    
    def _get_recommended_actions(self,
                                  severity: AlertSeverity,
                                  percentage_used: float) -> List[str]:
        """Get recommended actions based on severity"""
        
        if severity == AlertSeverity.CRITICAL:
            return [
                'Immediately review and terminate unused resources',
                'Contact team leads for emergency cost review',
                'Implement emergency cost controls',
                'Consider disabling non-critical services'
            ]
        elif severity == AlertSeverity.WARNING:
            return [
                'Review resource utilization and right-size instances',
                'Identify and terminate unused resources',
                'Evaluate spot instance opportunities',
                'Schedule cost optimization review meeting'
            ]
        else:
            return [
                'Monitor spending trends',
                'Review budget allocation',
                'Plan for potential optimization opportunities'
            ]
    
    def get_budget_status(self, budget_id: str, current_spend: float) -> Dict:
        """Get current budget status"""
        
        budget = self.budgets.get(budget_id)
        if not budget:
            return {'error': 'Budget not found'}
        
        percentage_used = (current_spend / budget.amount * 100) if budget.amount > 0 else 0
        
        if percentage_used >= 100:
            status = BudgetStatus.EXCEEDED
        elif percentage_used >= 80:
            status = BudgetStatus.WARNING
        else:
            status = BudgetStatus.HEALTHY
        
        return {
            'budget_id': budget_id,
            'budget_name': budget.name,
            'status': status.value,
            'amount': budget.amount,
            'current_spend': current_spend,
            'remaining': budget.amount - current_spend,
            'percentage_used': percentage_used,
            'days_remaining': self._get_days_remaining(budget)
        }
    
    def _get_days_remaining(self, budget: Budget) -> int:
        """Get days remaining in budget period"""
        
        now = datetime.now()
        
        if budget.period == 'monthly':
            end_of_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            return (end_of_month - now).days
        elif budget.period == 'quarterly':
            quarter_end = pd.Timestamp(now).to_period('Q').end_time
            return (quarter_end - now).days
        elif budget.period == 'annual':
            year_end = now.replace(month=12, day=31)
            return (year_end - now).days
        
        return 0


class CostForecaster:
    """Forecast future costs using ML models"""
    
    def __init__(self):
        self.forecast_horizon_days = 30
        self.confidence_interval = 0.95
    
    def forecast_costs(self,
                      historical_costs: pd.DataFrame,
                      forecast_days: int = 30) -> Dict:
        """
        Forecast future costs using Prophet
        
        Args:
            historical_costs: DataFrame with 'ds' (date) and 'y' (cost) columns
            forecast_days: Number of days to forecast
            
        Returns:
            Dictionary with forecast results
        """
        
        if len(historical_costs) < 14:
            return {
                'error': 'Insufficient historical data (minimum 14 days required)',
                'forecast': None
            }
        
        try:
            # Prepare data for Prophet
            df = historical_costs.copy()
            df['ds'] = pd.to_datetime(df['ds'])
            df = df.groupby('ds')['y'].sum().reset_index()
            
            # Create and fit model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                interval_width=self.confidence_interval
            )
            
            # Add monthly seasonality for cloud billing patterns
            model.add_seasonality(
                name='monthly',
                period=30.5,
                fourier_order=5
            )
            
            model.fit(df)
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=forecast_days)
            
            # Generate forecast
            forecast = model.predict(future)
            
            # Calculate statistics
            forecasted_total = forecast.tail(forecast_days)['yhat'].sum()
            forecasted_mean = forecast.tail(forecast_days)['yhat'].mean()
            
            historical_mean = df['y'].mean()
            historical_total = df['y'].sum()
            
            # Calculate trend
            trend_change = ((forecasted_mean - historical_mean) / historical_mean * 100) if historical_mean > 0 else 0
            
            return {
                'forecast_days': forecast_days,
                'forecasted_total': forecasted_total,
                'forecasted_daily_mean': forecasted_mean,
                'historical_daily_mean': historical_mean,
                'trend_percent': trend_change,
                'confidence_interval': self.confidence_interval,
                'forecast_data': forecast.tail(forecast_days)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict('records'),
                'components': {
                    'trend': self._extract_trend_component(forecast),
                    'weekly_seasonality': self._extract_weekly_pattern(forecast),
                    'monthly_seasonality': self._extract_monthly_pattern(forecast)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            return {
                'error': str(e),
                'forecast': None
            }
    
    def _extract_trend_component(self, forecast: pd.DataFrame) -> Dict:
        """Extract trend component from forecast"""
        trend = forecast['trend']
        return {
            'direction': 'increasing' if trend.iloc[-1] > trend.iloc[0] else 'decreasing',
            'change_percent': ((trend.iloc[-1] - trend.iloc[0]) / trend.iloc[0] * 100) if trend.iloc[0] > 0 else 0
        }
    
    def _extract_weekly_pattern(self, forecast: pd.DataFrame) -> Dict:
        """Extract weekly seasonality pattern"""
        if 'weekly' in forecast.columns:
            weekly = forecast['weekly']
            return {
                'peak_day': weekly.idxmax(),
                'low_day': weekly.idxmin(),
                'variation_percent': (weekly.max() - weekly.min()) / weekly.mean() * 100 if weekly.mean() > 0 else 0
            }
        return {}
    
    def _extract_monthly_pattern(self, forecast: pd.DataFrame) -> Dict:
        """Extract monthly seasonality pattern"""
        if 'monthly' in forecast.columns:
            monthly = forecast['monthly']
            return {
                'peak_period': monthly.idxmax(),
                'low_period': monthly.idxmin(),
                'variation_percent': (monthly.max() - monthly.min()) / monthly.mean() * 100 if monthly.mean() > 0 else 0
            }
        return {}
    
    def detect_anomalies(self,
                        historical_costs: pd.DataFrame,
                        threshold_std: float = 2.0) -> List[Dict]:
        """Detect anomalous cost spikes"""
        
        df = historical_costs.copy()
        df['ds'] = pd.to_datetime(df['ds'])
        df = df.groupby('ds')['y'].sum().reset_index()
        
        # Calculate rolling statistics
        df['rolling_mean'] = df['y'].rolling(window=7, min_periods=1).mean()
        df['rolling_std'] = df['y'].rolling(window=7, min_periods=1).std()
        
        # Detect anomalies
        df['z_score'] = (df['y'] - df['rolling_mean']) / df['rolling_std'].replace(0, 1)
        df['is_anomaly'] = df['z_score'].abs() > threshold_std
        
        anomalies = df[df['is_anomaly']].copy()
        
        return [
            {
                'date': row['ds'].isoformat(),
                'cost': row['y'],
                'expected_range': [
                    row['rolling_mean'] - threshold_std * row['rolling_std'],
                    row['rolling_mean'] + threshold_std * row['rolling_std']
                ],
                'z_score': row['z_score'],
                'severity': 'critical' if abs(row['z_score']) > 3 else 'warning'
            }
            for _, row in anomalies.iterrows()
        ]


# Usage example
if __name__ == "__main__":
    # Initialize budget manager
    budget_manager = BudgetManager()
    
    # Create budgets
    production_budget = budget_manager.create_budget(
        name='Production Infrastructure',
        amount=50000,
        period='monthly',
        alert_thresholds=[50, 75, 90, 100],
        filters={'Environment': ['production']},
        notifications=['team-platform@example.com']
    )
    
    ml_budget = budget_manager.create_budget(
        name='ML Training & Inference',
        amount=30000,
        period='monthly',
        alert_thresholds=[60, 80, 100],
        filters={'Team': ['ml-platform', 'data-science']},
        notifications=['team-ml@example.com']
    )
    
    # Simulate current spend
    current_spend = {
        production_budget.budget_id: 42500,  # 85% of budget
        ml_budget.budget_id: 28500  # 95% of budget
    }
    
    # Check budgets
    alerts = budget_manager.check_budgets(current_spend)
    
    print("Budget Alerts:")
    for alert in alerts:
        print(f"\n[{alert.severity.value.upper()}] {alert.budget_name}")
        print(f"  Message: {alert.message}")
        print(f"  Current Spend: ${alert.current_spend:,.2f}")
        print(f"  Budget Limit: ${alert.budget_limit:,.2f}")
        print(f"  Percentage Used: {alert.percentage_used:.1f}%")
        print("  Recommended Actions:")
        for action in alert.recommended_actions:
            print(f"    - {action}")
    
    # Generate cost forecast
    forecaster = CostForecaster()
    
    # Create sample historical data
    dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
    historical_costs = pd.DataFrame({
        'ds': dates,
        'y': np.random.normal(1500, 300, 90) + np.sin(np.arange(90) * 2 * np.pi / 7) * 200
    })
    
    forecast = forecaster.forecast_costs(historical_costs, forecast_days=30)
    
    print("\n\nCost Forecast:")
    print(f"Forecasted Total (30 days): ${forecast['forecasted_total']:,.2f}")
    print(f"Forecasted Daily Average: ${forecast['forecasted_daily_mean']:,.2f}")
    print(f"Historical Daily Average: ${forecast['historical_daily_mean']:,.2f}")
    print(f"Trend: {forecast['trend_percent']:+.1f}%")
    
    # Detect anomalies
    anomalies = forecaster.detect_anomalies(historical_costs)
    
    if anomalies:
        print(f"\nDetected {len(anomalies)} anomalies:")
        for anomaly in anomalies[:5]:
            print(f"  {anomaly['date']}: ${anomaly['cost']:,.2f} (z-score: {anomaly['z_score']:.2f})")
```


---

## 8. Waste Identification System

### 8.1 Resource Waste Detector

```python
# /app/cost_optimization/waste_detection/detector.py
"""
Resource waste detection and identification system
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class WasteType(Enum):
    """Types of resource waste"""
    IDLE_RESOURCE = "idle_resource"
    OVER_PROVISIONED = "over_provisioned"
    UNUSED_STORAGE = "unused_storage"
    ORPHANED_RESOURCE = "orphaned_resource"
    UNATTACHED_VOLUME = "unattached_volume"
    UNUSED_IP = "unused_ip"
    OLD_SNAPSHOT = "old_snapshot"
    UNUSED_LOAD_BALANCER = "unused_load_balancer"
    INEFFICIENT_ARCHITECTURE = "inefficient_architecture"


@dataclass
class WasteFinding:
    """Waste finding record"""
    finding_id: str
    waste_type: WasteType
    resource_id: str
    resource_type: str
    region: str
    estimated_monthly_waste: float
    estimated_annual_waste: float
    confidence: float
    severity: str
    description: str
    detection_criteria: Dict
    recommended_action: str
    automation_possible: bool
    safe_deletion_date: Optional[datetime]


class WasteDetector:
    """Detect various types of resource waste"""
    
    # Detection thresholds
    IDLE_CPU_THRESHOLD = 5.0  # 5% average CPU
    IDLE_MEMORY_THRESHOLD = 20.0  # 20% average memory
    UNUSED_DAYS_THRESHOLD = 7  # 7 days of no activity
    OLD_SNAPSHOT_DAYS = 90  # 90 days
    UNATTACHED_VOLUME_DAYS = 30  # 30 days
    
    def __init__(self):
        self.findings: List[WasteFinding] = []
    
    def detect_idle_instances(self,
                              instances: List[Dict],
                              metrics_data: pd.DataFrame) -> List[WasteFinding]:
        """Detect idle EC2 instances"""
        
        findings = []
        
        for instance in instances:
            instance_id = instance['instance_id']
            instance_type = instance['instance_type']
            
            # Get metrics for this instance
            instance_metrics = metrics_data[
                metrics_data['resource_id'] == instance_id
            ]
            
            if instance_metrics.empty:
                continue
            
            # Calculate average utilization
            avg_cpu = instance_metrics['cpu_utilization'].mean()
            avg_memory = instance_metrics.get('memory_utilization', pd.Series([0])).mean()
            
            # Check if idle
            if avg_cpu < self.IDLE_CPU_THRESHOLD and avg_memory < self.IDLE_MEMORY_THRESHOLD:
                # Calculate waste
                hourly_rate = self._get_instance_hourly_rate(instance_type)
                monthly_waste = hourly_rate * 24 * 30
                annual_waste = monthly_waste * 12
                
                # Determine confidence based on data points
                confidence = min(0.95, 0.6 + len(instance_metrics) / 100)
                
                finding = WasteFinding(
                    finding_id=f"idle-{instance_id}",
                    waste_type=WasteType.IDLE_RESOURCE,
                    resource_id=instance_id,
                    resource_type='ec2_instance',
                    region=instance.get('region', 'unknown'),
                    estimated_monthly_waste=monthly_waste,
                    estimated_annual_waste=annual_waste,
                    confidence=confidence,
                    severity='high' if avg_cpu < 2 else 'medium',
                    description=f"Instance has very low utilization: CPU {avg_cpu:.1f}%, Memory {avg_memory:.1f}%",
                    detection_criteria={
                        'avg_cpu': avg_cpu,
                        'avg_memory': avg_memory,
                        'data_points': len(instance_metrics),
                        'threshold_cpu': self.IDLE_CPU_THRESHOLD,
                        'threshold_memory': self.IDLE_MEMORY_THRESHOLD
                    },
                    recommended_action='Terminate instance after confirming no active use',
                    automation_possible=True,
                    safe_deletion_date=datetime.now() + timedelta(days=7)
                )
                findings.append(finding)
        
        return findings
    
    def detect_unattached_volumes(self, volumes: List[Dict]) -> List[WasteFinding]:
        """Detect unattached EBS volumes"""
        
        findings = []
        
        for volume in volumes:
            if volume.get('state') == 'available':
                # Volume is not attached
                detached_days = volume.get('detached_days', 0)
                
                if detached_days >= self.UNATTACHED_VOLUME_DAYS:
                    # Calculate waste
                    size_gb = volume.get('size', 0)
                    volume_type = volume.get('volume_type', 'gp2')
                    
                    monthly_cost = self._calculate_volume_cost(size_gb, volume_type)
                    annual_cost = monthly_cost * 12
                    
                    finding = WasteFinding(
                        finding_id=f"volume-{volume['volume_id']}",
                        waste_type=WasteType.UNATTACHED_VOLUME,
                        resource_id=volume['volume_id'],
                        resource_type='ebs_volume',
                        region=volume.get('region', 'unknown'),
                        estimated_monthly_waste=monthly_cost,
                        estimated_annual_waste=annual_cost,
                        confidence=0.95,
                        severity='medium',
                        description=f"Volume has been unattached for {detached_days} days",
                        detection_criteria={
                            'detached_days': detached_days,
                            'size_gb': size_gb,
                            'volume_type': volume_type
                        },
                        recommended_action='Create snapshot and delete volume if not needed',
                        automation_possible=True,
                        safe_deletion_date=datetime.now() + timedelta(days=14)
                    )
                    findings.append(finding)
        
        return findings
    
    def detect_unused_elastic_ips(self, addresses: List[Dict]) -> List[WasteFinding]:
        """Detect unused Elastic IPs"""
        
        findings = []
        
        for address in addresses:
            if not address.get('instance_id') and not address.get('network_interface_id'):
                # IP is not associated
                finding = WasteFinding(
                    finding_id=f"eip-{address['allocation_id']}",
                    waste_type=WasteType.UNUSED_IP,
                    resource_id=address['allocation_id'],
                    resource_type='elastic_ip',
                    region=address.get('region', 'unknown'),
                    estimated_monthly_waste=3.6,  # $0.005/hour * 24 * 30
                    estimated_annual_waste=43.2,
                    confidence=1.0,
                    severity='low',
                    description='Elastic IP is not associated with any instance',
                    detection_criteria={'associated': False},
                    recommended_action='Release unused Elastic IP',
                    automation_possible=True,
                    safe_deletion_date=datetime.now() + timedelta(days=1)
                )
                findings.append(finding)
        
        return findings
    
    def detect_old_snapshots(self, snapshots: List[Dict]) -> List[WasteFinding]:
        """Detect old, potentially unnecessary snapshots"""
        
        findings = []
        
        for snapshot in snapshots:
            age_days = snapshot.get('age_days', 0)
            
            if age_days >= self.OLD_SNAPSHOT_DAYS:
                # Check if parent volume still exists
                parent_volume_exists = snapshot.get('parent_volume_exists', True)
                
                size_gb = snapshot.get('volume_size', 0)
                monthly_cost = size_gb * 0.05  # $0.05 per GB-month
                annual_cost = monthly_cost * 12
                
                severity = 'high' if not parent_volume_exists else 'low'
                
                finding = WasteFinding(
                    finding_id=f"snapshot-{snapshot['snapshot_id']}",
                    waste_type=WasteType.OLD_SNAPSHOT,
                    resource_id=snapshot['snapshot_id'],
                    resource_type='ebs_snapshot',
                    region=snapshot.get('region', 'unknown'),
                    estimated_monthly_waste=monthly_cost,
                    estimated_annual_waste=annual_cost,
                    confidence=0.7 if parent_volume_exists else 0.9,
                    severity=severity,
                    description=f"Snapshot is {age_days} days old" + 
                               (" and parent volume no longer exists" if not parent_volume_exists else ""),
                    detection_criteria={
                        'age_days': age_days,
                        'size_gb': size_gb,
                        'parent_volume_exists': parent_volume_exists
                    },
                    recommended_action='Review and delete if no longer needed',
                    automation_possible=False,  # Requires manual review
                    safe_deletion_date=None
                )
                findings.append(finding)
        
        return findings
    
    def detect_orphaned_resources(self, resources: List[Dict]) -> List[WasteFinding]:
        """Detect orphaned resources (resources without valid parent)"""
        
        findings = []
        
        for resource in resources:
            # Check if resource has valid tags
            tags = resource.get('tags', {})
            
            # Check for orphan indicators
            is_orphan = (
                not tags.get('Project') or
                not tags.get('Owner') or
                tags.get('Project') == 'terminated' or
                tags.get('Owner') == 'departed'
            )
            
            if is_orphan:
                monthly_cost = resource.get('monthly_cost', 0)
                
                finding = WasteFinding(
                    finding_id=f"orphan-{resource['resource_id']}",
                    waste_type=WasteType.ORPHANED_RESOURCE,
                    resource_id=resource['resource_id'],
                    resource_type=resource.get('resource_type', 'unknown'),
                    region=resource.get('region', 'unknown'),
                    estimated_monthly_waste=monthly_cost,
                    estimated_annual_waste=monthly_cost * 12,
                    confidence=0.8,
                    severity='medium',
                    description='Resource appears to be orphaned (missing or invalid tags)',
                    detection_criteria={'tags': tags},
                    recommended_action='Investigate ownership and delete if confirmed orphaned',
                    automation_possible=False,
                    safe_deletion_date=None
                )
                findings.append(finding)
        
        return findings
    
    def detect_unused_load_balancers(self, load_balancers: List[Dict]) -> List[WasteFinding]:
        """Detect unused load balancers"""
        
        findings = []
        
        for lb in load_balancers:
            # Check request count
            request_count = lb.get('request_count_30d', 0)
            active_connections = lb.get('active_connections', 0)
            
            if request_count < 100 and active_connections == 0:
                monthly_cost = lb.get('monthly_cost', 20)  # Base ALB cost
                
                finding = WasteFinding(
                    finding_id=f"lb-{lb['load_balancer_arn'].split('/')[-1]}",
                    waste_type=WasteType.UNUSED_LOAD_BALANCER,
                    resource_id=lb['load_balancer_arn'],
                    resource_type='load_balancer',
                    region=lb.get('region', 'unknown'),
                    estimated_monthly_waste=monthly_cost,
                    estimated_annual_waste=monthly_cost * 12,
                    confidence=0.85,
                    severity='medium',
                    description=f'Load balancer has minimal traffic: {request_count} requests in 30 days',
                    detection_criteria={
                        'request_count_30d': request_count,
                        'active_connections': active_connections
                    },
                    recommended_action='Delete load balancer if no longer needed',
                    automation_possible=False,  # Requires verification
                    safe_deletion_date=datetime.now() + timedelta(days=7)
                )
                findings.append(finding)
        
        return findings
    
    def _get_instance_hourly_rate(self, instance_type: str) -> float:
        """Get hourly rate for instance type"""
        rates = {
            't3.nano': 0.0052,
            't3.micro': 0.0104,
            't3.small': 0.0208,
            't3.medium': 0.0416,
            't3.large': 0.0832,
            'm5.large': 0.096,
            'm5.xlarge': 0.192,
            'm5.2xlarge': 0.384,
            'c5.large': 0.085,
            'c5.xlarge': 0.17,
            'r5.large': 0.126,
            'r5.xlarge': 0.252,
        }
        return rates.get(instance_type, 0.1)
    
    def _calculate_volume_cost(self, size_gb: int, volume_type: str) -> float:
        """Calculate monthly cost for EBS volume"""
        pricing = {
            'gp2': 0.10,
            'gp3': 0.08,
            'io1': 0.125,
            'io2': 0.125,
            'st1': 0.045,
            'sc1': 0.025,
            'standard': 0.05
        }
        rate = pricing.get(volume_type, 0.10)
        return size_gb * rate
    
    def generate_waste_report(self, findings: List[WasteFinding]) -> Dict:
        """Generate comprehensive waste report"""
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_findings': len(findings),
                'total_monthly_waste': sum(f.estimated_monthly_waste for f in findings),
                'total_annual_waste': sum(f.estimated_annual_waste for f in findings),
                'by_waste_type': {},
                'by_severity': {},
                'automation_opportunities': sum(1 for f in findings if f.automation_possible)
            },
            'findings': []
        }
        
        # Group by waste type
        for waste_type in WasteType:
            type_findings = [f for f in findings if f.waste_type == waste_type]
            if type_findings:
                report['summary']['by_waste_type'][waste_type.value] = {
                    'count': len(type_findings),
                    'monthly_waste': sum(f.estimated_monthly_waste for f in type_findings),
                    'annual_waste': sum(f.estimated_annual_waste for f in type_findings)
                }
        
        # Group by severity
        for severity in ['high', 'medium', 'low']:
            severity_findings = [f for f in findings if f.severity == severity]
            report['summary']['by_severity'][severity] = {
                'count': len(severity_findings),
                'monthly_waste': sum(f.estimated_monthly_waste for f in severity_findings)
            }
        
        # Sort findings by annual waste
        sorted_findings = sorted(findings, key=lambda x: x.estimated_annual_waste, reverse=True)
        
        report['findings'] = [
            {
                'finding_id': f.finding_id,
                'waste_type': f.waste_type.value,
                'resource_id': f.resource_id,
                'resource_type': f.resource_type,
                'monthly_waste': f.estimated_monthly_waste,
                'annual_waste': f.estimated_annual_waste,
                'severity': f.severity,
                'confidence': f.confidence,
                'description': f.description,
                'recommended_action': f.recommended_action,
                'automation_possible': f.automation_possible
            }
            for f in sorted_findings
        ]
        
        return report


class AutomatedWasteRemediation:
    """Automated remediation for safe waste removal"""
    
    def __init__(self):
        self.enabled_actions = {
            'delete_unattached_volumes': True,
            'release_unused_ips': True,
            'terminate_idle_instances': False,  # Requires approval
            'delete_old_snapshots': False  # Requires approval
        }
    
    def create_remediation_plan(self, findings: List[WasteFinding]) -> Dict:
        """Create automated remediation plan"""
        
        plan = {
            'created_at': datetime.now().isoformat(),
            'automated_actions': [],
            'manual_actions': [],
            'estimated_savings': 0
        }
        
        for finding in findings:
            if finding.automation_possible and self._is_action_enabled(finding.waste_type):
                plan['automated_actions'].append({
                    'finding_id': finding.finding_id,
                    'action': finding.recommended_action,
                    'resource_id': finding.resource_id,
                    'scheduled_date': finding.safe_deletion_date.isoformat() if finding.safe_deletion_date else None,
                    'estimated_savings': finding.estimated_monthly_waste
                })
                plan['estimated_savings'] += finding.estimated_monthly_waste
            else:
                plan['manual_actions'].append({
                    'finding_id': finding.finding_id,
                    'action': finding.recommended_action,
                    'resource_id': finding.resource_id,
                    'reason': 'Requires manual approval' if not finding.automation_possible else 'Automation disabled',
                    'estimated_savings': finding.estimated_monthly_waste
                })
        
        return plan
    
    def _is_action_enabled(self, waste_type: WasteType) -> bool:
        """Check if automated action is enabled for waste type"""
        
        action_map = {
            WasteType.UNATTACHED_VOLUME: 'delete_unattached_volumes',
            WasteType.UNUSED_IP: 'release_unused_ips',
            WasteType.IDLE_RESOURCE: 'terminate_idle_instances',
            WasteType.OLD_SNAPSHOT: 'delete_old_snapshots'
        }
        
        action_key = action_map.get(waste_type)
        return self.enabled_actions.get(action_key, False) if action_key else False


# Usage example
if __name__ == "__main__":
    detector = WasteDetector()
    
    # Sample data
    instances = [
        {
            'instance_id': 'i-1234567890abcdef0',
            'instance_type': 'm5.xlarge',
            'region': 'us-east-1'
        },
        {
            'instance_id': 'i-0987654321fedcba0',
            'instance_type': 'c5.large',
            'region': 'us-east-1'
        }
    ]
    
    # Sample metrics (one idle, one active)
    dates = pd.date_range(start='2024-01-01', periods=168, freq='H')
    metrics_data = pd.DataFrame({
        'resource_id': ['i-1234567890abcdef0'] * 168 + ['i-0987654321fedcba0'] * 168,
        'timestamp': list(dates) * 2,
        'cpu_utilization': list(np.random.normal(3, 2, 168).clip(0, 100)) + list(np.random.normal(45, 15, 168).clip(0, 100)),
        'memory_utilization': list(np.random.normal(15, 5, 168).clip(0, 100)) + list(np.random.normal(60, 10, 168).clip(0, 100))
    })
    
    # Detect idle instances
    idle_findings = detector.detect_idle_instances(instances, metrics_data)
    
    # Sample volumes
    volumes = [
        {
            'volume_id': 'vol-1234567890abcdef0',
            'state': 'available',
            'detached_days': 45,
            'size': 100,
            'volume_type': 'gp2',
            'region': 'us-east-1'
        }
    ]
    
    # Detect unattached volumes
    volume_findings = detector.detect_unattached_volumes(volumes)
    
    # Combine all findings
    all_findings = idle_findings + volume_findings
    
    # Generate report
    report = detector.generate_waste_report(all_findings)
    
    print("Waste Detection Report")
    print("=" * 50)
    print(f"Total Findings: {report['summary']['total_findings']}")
    print(f"Total Monthly Waste: ${report['summary']['total_monthly_waste']:,.2f}")
    print(f"Total Annual Waste: ${report['summary']['total_annual_waste']:,.2f}")
    print(f"Automation Opportunities: {report['summary']['automation_opportunities']}")
    
    print("\nBy Waste Type:")
    for waste_type, data in report['summary']['by_waste_type'].items():
        print(f"  {waste_type}: {data['count']} findings, ${data['monthly_waste']:,.2f}/month")
    
    print("\nTop Findings:")
    for finding in report['findings'][:5]:
        print(f"  {finding['resource_id']} ({finding['waste_type']}):")
        print(f"    Monthly Waste: ${finding['monthly_waste']:,.2f}")
        print(f"    Severity: {finding['severity']}")
        print(f"    Action: {finding['recommended_action']}")
        print()


---

## 9. Optimization Recommendations Engine

### 9.1 Centralized Recommendation System

```python
# /app/cost_optimization/recommendations/engine.py
"""
Centralized cost optimization recommendations engine
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class RecommendationCategory(Enum):
    """Categories of optimization recommendations"""
    RIGHTSIZING = "right_sizing"
    RESERVED_CAPACITY = "reserved_capacity"
    SPOT_INSTANCES = "spot_instances"
    WASTE_ELIMINATION = "waste_elimination"
    STORAGE_OPTIMIZATION = "storage_optimization"
    ARCHITECTURE = "architecture"
    PRICING_MODEL = "pricing_model"
    NETWORKING = "networking"


class RecommendationPriority(Enum):
    """Priority levels for recommendations"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation"""
    recommendation_id: str
    category: RecommendationCategory
    priority: RecommendationPriority
    title: str
    description: str
    affected_resources: List[str]
    current_state: Dict
    recommended_state: Dict
    estimated_monthly_savings: float
    estimated_annual_savings: float
    implementation_effort: str  # 'low', 'medium', 'high'
    implementation_risk: str  # 'low', 'medium', 'high'
    confidence: float
    implementation_steps: List[str]
    automation_script: Optional[str]
    approval_required: bool
    created_at: datetime
    expires_at: Optional[datetime]


class RecommendationEngine:
    """Generate and manage optimization recommendations"""
    
    def __init__(self):
        self.recommendations: List[OptimizationRecommendation] = []
        self.savings_tracker = SavingsTracker()
    
    def generate_all_recommendations(self,
                                     cost_data: pd.DataFrame,
                                     utilization_data: pd.DataFrame,
                                     resource_inventory: Dict) -> List[OptimizationRecommendation]:
        """Generate all types of optimization recommendations"""
        
        recommendations = []
        
        # Generate right-sizing recommendations
        rightsizing_recs = self._generate_rightsizing_recommendations(
            utilization_data, resource_inventory
        )
        recommendations.extend(rightsizing_recs)
        
        # Generate reserved capacity recommendations
        reserved_recs = self._generate_reserved_capacity_recommendations(
            cost_data, resource_inventory
        )
        recommendations.extend(reserved_recs)
        
        # Generate spot instance recommendations
        spot_recs = self._generate_spot_instance_recommendations(
            utilization_data, resource_inventory
        )
        recommendations.extend(spot_recs)
        
        # Generate waste elimination recommendations
        waste_recs = self._generate_waste_elimination_recommendations(
            resource_inventory
        )
        recommendations.extend(waste_recs)
        
        # Generate storage optimization recommendations
        storage_recs = self._generate_storage_optimization_recommendations(
            resource_inventory
        )
        recommendations.extend(storage_recs)
        
        # Sort by priority and savings
        recommendations.sort(key=lambda x: (
            x.priority.value,
            -x.estimated_annual_savings
        ))
        
        self.recommendations = recommendations
        return recommendations
    
    def _generate_rightsizing_recommendations(self,
                                               utilization_data: pd.DataFrame,
                                               resource_inventory: Dict) -> List[OptimizationRecommendation]:
        """Generate right-sizing recommendations"""
        
        recommendations = []
        
        for instance_id, instance_data in resource_inventory.get('ec2_instances', {}).items():
            # Get utilization metrics
            instance_metrics = utilization_data[
                utilization_data['resource_id'] == instance_id
            ]
            
            if instance_metrics.empty:
                continue
            
            avg_cpu = instance_metrics['cpu_utilization'].mean()
            avg_memory = instance_metrics.get('memory_utilization', pd.Series([0])).mean()
            
            # Determine if right-sizing is needed
            if avg_cpu < 20 and avg_memory < 40:
                current_type = instance_data['instance_type']
                recommended_type = self._get_smaller_instance_type(current_type)
                
                if recommended_type != current_type:
                    current_cost = self._get_instance_monthly_cost(current_type)
                    recommended_cost = self._get_instance_monthly_cost(recommended_type)
                    savings = current_cost - recommended_cost
                    
                    rec = OptimizationRecommendation(
                        recommendation_id=f"rs-{instance_id}",
                        category=RecommendationCategory.RIGHTSIZING,
                        priority=RecommendationPriority.HIGH,
                        title=f"Downsize {instance_id} from {current_type} to {recommended_type}",
                        description=f"Instance has low utilization (CPU: {avg_cpu:.1f}%, Memory: {avg_memory:.1f}%). " +
                                   f"Recommended to downsize to {recommended_type}.",
                        affected_resources=[instance_id],
                        current_state={
                            'instance_type': current_type,
                            'monthly_cost': current_cost,
                            'avg_cpu': avg_cpu,
                            'avg_memory': avg_memory
                        },
                        recommended_state={
                            'instance_type': recommended_type,
                            'monthly_cost': recommended_cost
                        },
                        estimated_monthly_savings=savings,
                        estimated_annual_savings=savings * 12,
                        implementation_effort='low',
                        implementation_risk='low',
                        confidence=0.85,
                        implementation_steps=[
                            f"1. Create AMI backup of {instance_id}",
                            f"2. Stop instance {instance_id}",
                            f"3. Change instance type to {recommended_type}",
                            f"4. Start instance",
                            f"5. Verify application functionality"
                        ],
                        automation_script=self._generate_rightsizing_script(instance_id, recommended_type),
                        approval_required=False,
                        created_at=datetime.now(),
                        expires_at=datetime.now() + timedelta(days=30)
                    )
                    recommendations.append(rec)
        
        return recommendations
    
    def _generate_reserved_capacity_recommendations(self,
                                                     cost_data: pd.DataFrame,
                                                     resource_inventory: Dict) -> List[OptimizationRecommendation]:
        """Generate reserved capacity recommendations"""
        
        recommendations = []
        
        # Analyze usage patterns for each instance family
        instance_families = {}
        
        for instance_id, instance_data in resource_inventory.get('ec2_instances', {}).items():
            family = instance_data['instance_type'].split('.')[0]
            
            if family not in instance_families:
                instance_families[family] = {
                    'instances': [],
                    'total_hours': 0
                }
            
            instance_families[family]['instances'].append(instance_id)
            instance_families[family]['total_hours'] += 720  # Assume full month
        
        for family, data in instance_families.items():
            # Check if stable usage (high hours)
            if data['total_hours'] >= 500:  # At least 500 instance-hours per month
                # Calculate potential savings with 1-year reserved
                on_demand_cost = self._get_family_monthly_cost(family) * len(data['instances'])
                reserved_cost = on_demand_cost * 0.60  # 40% discount
                savings = on_demand_cost - reserved_cost
                
                rec = OptimizationRecommendation(
                    recommendation_id=f"ri-{family}",
                    category=RecommendationCategory.RESERVED_CAPACITY,
                    priority=RecommendationPriority.CRITICAL,
                    title=f"Purchase Reserved Instances for {family} family",
                    description=f"Stable usage detected for {family} instances. " +
                               f"Purchasing 1-year reserved capacity can save 40%.",
                    affected_resources=data['instances'],
                    current_state={
                        'instance_family': family,
                        'instance_count': len(data['instances']),
                        'monthly_on_demand_cost': on_demand_cost
                    },
                    recommended_state={
                        'commitment_type': '1-year reserved',
                        'monthly_reserved_cost': reserved_cost
                    },
                    estimated_monthly_savings=savings,
                    estimated_annual_savings=savings * 12,
                    implementation_effort='low',
                    implementation_risk='low',
                    confidence=0.90,
                    implementation_steps=[
                        f"1. Calculate exact commitment needed",
                        f"2. Purchase {family} reserved instances",
                        f"3. Monitor utilization",
                        f"4. Adjust if needed"
                    ],
                    automation_script=None,  # Manual purchase required
                    approval_required=True,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=14)
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _generate_spot_instance_recommendations(self,
                                                 utilization_data: pd.DataFrame,
                                                 resource_inventory: Dict) -> List[OptimizationRecommendation]:
        """Generate spot instance recommendations"""
        
        recommendations = []
        
        # Identify fault-tolerant workloads
        for instance_id, instance_data in resource_inventory.get('ec2_instances', {}).items():
            tags = instance_data.get('tags', {})
            
            # Check if workload is suitable for spot
            is_fault_tolerant = (
                tags.get('WorkloadType') in ['batch', 'training', 'processing'] or
                'auto-scaling' in tags.get('Name', '').lower()
            )
            
            if is_fault_tolerant and not instance_data.get('is_spot', False):
                current_type = instance_data['instance_type']
                on_demand_cost = self._get_instance_monthly_cost(current_type)
                spot_cost = on_demand_cost * 0.30  # 70% savings
                savings = on_demand_cost - spot_cost
                
                rec = OptimizationRecommendation(
                    recommendation_id=f"spot-{instance_id}",
                    category=RecommendationCategory.SPOT_INSTANCES,
                    priority=RecommendationPriority.HIGH,
                    title=f"Migrate {instance_id} to Spot instances",
                    description=f"Fault-tolerant workload detected. Migrating to spot instances " +
                               f"can save up to 70% with minimal risk.",
                    affected_resources=[instance_id],
                    current_state={
                        'instance_type': current_type,
                        'purchase_option': 'on-demand',
                        'monthly_cost': on_demand_cost
                    },
                    recommended_state={
                        'purchase_option': 'spot',
                        'monthly_cost': spot_cost
                    },
                    estimated_monthly_savings=savings,
                    estimated_annual_savings=savings * 12,
                    implementation_effort='medium',
                    implementation_risk='medium',
                    confidence=0.80,
                    implementation_steps=[
                        f"1. Implement checkpoint/save functionality",
                        f"2. Configure spot interruption handling",
                        f"3. Create spot instance launch template",
                        f"4. Test spot instance behavior",
                        f"5. Migrate workload to spot"
                    ],
                    automation_script=self._generate_spot_migration_script(instance_id),
                    approval_required=True,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=30)
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _generate_waste_elimination_recommendations(self,
                                                     resource_inventory: Dict) -> List[OptimizationRecommendation]:
        """Generate waste elimination recommendations"""
        
        recommendations = []
        
        # Check for unattached volumes
        for volume_id, volume_data in resource_inventory.get('ebs_volumes', {}).items():
            if volume_data.get('state') == 'available':
                size = volume_data.get('size', 0)
                monthly_cost = size * 0.10  # gp2 pricing
                
                rec = OptimizationRecommendation(
                    recommendation_id=f"waste-vol-{volume_id}",
                    category=RecommendationCategory.WASTE_ELIMINATION,
                    priority=RecommendationPriority.HIGH,
                    title=f"Delete unattached volume {volume_id}",
                    description=f"Volume has been unattached for {volume_data.get('detached_days', 0)} days. " +
                               f"Consider creating a snapshot and deleting the volume.",
                    affected_resources=[volume_id],
                    current_state={
                        'volume_size': size,
                        'volume_type': volume_data.get('volume_type'),
                        'monthly_cost': monthly_cost
                    },
                    recommended_state={
                        'action': 'delete_after_snapshot',
                        'monthly_cost': 0
                    },
                    estimated_monthly_savings=monthly_cost,
                    estimated_annual_savings=monthly_cost * 12,
                    implementation_effort='low',
                    implementation_risk='low',
                    confidence=0.95,
                    implementation_steps=[
                        f"1. Create snapshot of volume {volume_id}",
                        f"2. Verify snapshot completion",
                        f"3. Delete volume {volume_id}",
                        f"4. Tag snapshot for reference"
                    ],
                    automation_script=self._generate_volume_cleanup_script(volume_id),
                    approval_required=False,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=14)
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _generate_storage_optimization_recommendations(self,
                                                        resource_inventory: Dict) -> List[OptimizationRecommendation]:
        """Generate storage optimization recommendations"""
        
        recommendations = []
        
        # Check for gp2 volumes that could use gp3
        for volume_id, volume_data in resource_inventory.get('ebs_volumes', {}).items():
            if volume_data.get('volume_type') == 'gp2':
                size = volume_data.get('size', 0)
                current_cost = size * 0.10  # gp2: $0.10/GB
                gp3_cost = size * 0.08  # gp3: $0.08/GB
                savings = current_cost - gp3_cost
                
                rec = OptimizationRecommendation(
                    recommendation_id=f"storage-{volume_id}",
                    category=RecommendationCategory.STORAGE_OPTIMIZATION,
                    priority=RecommendationPriority.MEDIUM,
                    title=f"Migrate volume {volume_id} from gp2 to gp3",
                    description=f"gp3 volumes offer 20% cost savings and better performance. " +
                               f"Migrating requires no downtime.",
                    affected_resources=[volume_id],
                    current_state={
                        'volume_type': 'gp2',
                        'volume_size': size,
                        'monthly_cost': current_cost
                    },
                    recommended_state={
                        'volume_type': 'gp3',
                        'monthly_cost': gp3_cost
                    },
                    estimated_monthly_savings=savings,
                    estimated_annual_savings=savings * 12,
                    implementation_effort='low',
                    implementation_risk='low',
                    confidence=0.95,
                    implementation_steps=[
                        f"1. Create snapshot of volume {volume_id}",
                        f"2. Modify volume type to gp3",
                        f"3. Monitor performance"
                    ],
                    automation_script=self._generate_gp3_migration_script(volume_id),
                    approval_required=False,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(days=30)
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _get_smaller_instance_type(self, current_type: str) -> str:
        """Get next smaller instance type"""
        
        size_order = ['2xlarge', 'xlarge', 'large', 'medium', 'small', 'micro', 'nano']
        
        parts = current_type.split('.')
        if len(parts) != 2:
            return current_type
        
        family, size = parts
        
        for i, s in enumerate(size_order):
            if s in size:
                if i < len(size_order) - 1:
                    new_size = size.replace(s, size_order[i + 1])
                    return f"{family}.{new_size}"
        
        return current_type
    
    def _get_instance_monthly_cost(self, instance_type: str) -> float:
        """Get monthly cost for instance type"""
        hourly_rates = {
            't3.nano': 0.0052,
            't3.micro': 0.0104,
            't3.small': 0.0208,
            't3.medium': 0.0416,
            't3.large': 0.0832,
            'm5.large': 0.096,
            'm5.xlarge': 0.192,
            'm5.2xlarge': 0.384,
            'c5.large': 0.085,
            'c5.xlarge': 0.17,
            'r5.large': 0.126,
            'r5.xlarge': 0.252,
        }
        return hourly_rates.get(instance_type, 0.1) * 24 * 30
    
    def _get_family_monthly_cost(self, family: str) -> float:
        """Get monthly cost for instance family (base size)"""
        return self._get_instance_monthly_cost(f"{family}.large")
    
    def _generate_rightsizing_script(self, instance_id: str, new_type: str) -> str:
        """Generate automation script for right-sizing"""
        return f"""#!/bin/bash
# Right-size instance {instance_id} to {new_type}

INSTANCE_ID="{instance_id}"
NEW_TYPE="{new_type}"

# Create AMI backup
echo "Creating AMI backup..."
aws ec2 create-image \\
    --instance-id $INSTANCE_ID \\
    --name "backup-$(date +%Y%m%d)-$INSTANCE_ID" \\
    --no-reboot

# Stop instance
echo "Stopping instance..."
aws ec2 stop-instances --instance-ids $INSTANCE_ID
aws ec2 wait instance-stopped --instance-ids $INSTANCE_ID

# Change instance type
echo "Changing instance type to $NEW_TYPE..."
aws ec2 modify-instance-attribute \\
    --instance-id $INSTANCE_ID \\
    --instance-type \\"Value=$NEW_TYPE\"

# Start instance
echo "Starting instance..."
aws ec2 start-instances --instance-ids $INSTANCE_ID

echo "Right-sizing complete!"
"""
    
    def _generate_spot_migration_script(self, instance_id: str) -> str:
        """Generate spot migration script"""
        return f"""#!/bin/bash
# Migrate {instance_id} to spot

# Create launch template with spot option
aws ec2 create-launch-template \\
    --launch-template-name spot-template-{instance_id} \\
    --launch-template-data '{{"InstanceMarketOptions":{{"MarketType":"spot"}}}}'

echo "Spot launch template created. Update Auto Scaling Group to use this template."
"""
    
    def _generate_volume_cleanup_script(self, volume_id: str) -> str:
        """Generate volume cleanup script"""
        return f"""#!/bin/bash
# Clean up volume {volume_id}

VOLUME_ID="{volume_id}"

# Create snapshot
echo "Creating snapshot..."
SNAPSHOT_ID=$(aws ec2 create-snapshot \\
    --volume-id $VOLUME_ID \\
    --description "Backup before deletion" \\
    --query 'SnapshotId' \\
    --output text)

echo "Waiting for snapshot completion..."
aws ec2 wait snapshot-completed --snapshot-ids $SNAPSHOT_ID

# Delete volume
echo "Deleting volume..."
aws ec2 delete-volume --volume-id $VOLUME_ID

echo "Volume deleted. Snapshot ID: $SNAPSHOT_ID"
"""
    
    def _generate_gp3_migration_script(self, volume_id: str) -> str:
        """Generate gp3 migration script"""
        return f"""#!/bin/bash
# Migrate volume {volume_id} to gp3

aws ec2 modify-volume \\
    --volume-id {volume_id} \\
    --volume-type gp3

echo "Volume migration initiated. Monitor with: aws ec2 describe-volumes --volume-ids {volume_id}"
"""
    
    def generate_recommendation_report(self) -> Dict:
        """Generate comprehensive recommendation report"""
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_recommendations': len(self.recommendations),
                'total_monthly_savings': sum(r.estimated_monthly_savings for r in self.recommendations),
                'total_annual_savings': sum(r.estimated_annual_savings for r in self.recommendations),
                'by_category': {},
                'by_priority': {}
            },
            'quick_wins': [],
            'requires_approval': [],
            'all_recommendations': []
        }
        
        # Group by category
        for category in RecommendationCategory:
            cat_recs = [r for r in self.recommendations if r.category == category]
            if cat_recs:
                report['summary']['by_category'][category.value] = {
                    'count': len(cat_recs),
                    'monthly_savings': sum(r.estimated_monthly_savings for r in cat_recs),
                    'annual_savings': sum(r.estimated_annual_savings for r in cat_recs)
                }
        
        # Group by priority
        for priority in RecommendationPriority:
            pri_recs = [r for r in self.recommendations if r.priority == priority]
            report['summary']['by_priority'][priority.name] = len(pri_recs)
        
        # Quick wins (low effort, high savings)
        quick_wins = [
            r for r in self.recommendations
            if r.implementation_effort == 'low' and r.estimated_monthly_savings > 100
        ]
        report['quick_wins'] = [
            {
                'id': r.recommendation_id,
                'title': r.title,
                'monthly_savings': r.estimated_monthly_savings,
                'automation_available': r.automation_script is not None
            }
            for r in sorted(quick_wins, key=lambda x: -x.estimated_monthly_savings)[:10]
        ]
        
        # Requires approval
        approval_recs = [r for r in self.recommendations if r.approval_required]
        report['requires_approval'] = [
            {
                'id': r.recommendation_id,
                'title': r.title,
                'monthly_savings': r.estimated_monthly_savings,
                'risk_level': r.implementation_risk
            }
            for r in sorted(approval_recs, key=lambda x: -x.estimated_monthly_savings)
        ]
        
        return report


class SavingsTracker:
    """Track realized savings from implemented recommendations"""
    
    def __init__(self):
        self.implemented_recommendations: List[Dict] = []
        self.realized_savings: float = 0.0
    
    def track_implementation(self, recommendation: OptimizationRecommendation):
        """Track implementation of a recommendation"""
        
        implementation = {
            'recommendation_id': recommendation.recommendation_id,
            'implemented_at': datetime.now().isoformat(),
            'expected_monthly_savings': recommendation.estimated_monthly_savings,
            'actual_savings': None,
            'verification_status': 'pending'
        }
        
        self.implemented_recommendations.append(implementation)
    
    def verify_savings(self, recommendation_id: str, actual_savings: float):
        """Verify actual savings from implemented recommendation"""
        
        for impl in self.implemented_recommendations:
            if impl['recommendation_id'] == recommendation_id:
                impl['actual_savings'] = actual_savings
                impl['verification_status'] = 'verified'
                impl['verified_at'] = datetime.now().isoformat()
                self.realized_savings += actual_savings
                break
    
    def get_savings_report(self) -> Dict:
        """Get savings tracking report"""
        
        return {
            'total_implemented': len(self.implemented_recommendations),
            'total_realized_savings': self.realized_savings,
            'implementations': self.implemented_recommendations,
            'savings_accuracy': self._calculate_accuracy()
        }
    
    def _calculate_accuracy(self) -> float:
        """Calculate accuracy of savings predictions"""
        
        verified = [i for i in self.implemented_recommendations 
                   if i['verification_status'] == 'verified' and i['actual_savings'] is not None]
        
        if not verified:
            return 0.0
        
        total_expected = sum(i['expected_monthly_savings'] for i in verified)
        total_actual = sum(i['actual_savings'] for i in verified)
        
        if total_expected == 0:
            return 0.0
        
        return (1 - abs(total_actual - total_expected) / total_expected) * 100


# Usage example
if __name__ == "__main__":
    engine = RecommendationEngine()
    
    # Sample data
    resource_inventory = {
        'ec2_instances': {
            'i-1234567890abcdef0': {
                'instance_type': 'm5.xlarge',
                'tags': {'WorkloadType': 'batch'},
                'is_spot': False
            },
            'i-0987654321fedcba0': {
                'instance_type': 'c5.large',
                'tags': {'WorkloadType': 'api'},
                'is_spot': False
            }
        },
        'ebs_volumes': {
            'vol-1234567890abcdef0': {
                'state': 'available',
                'size': 100,
                'volume_type': 'gp2',
                'detached_days': 45
            },
            'vol-0987654321fedcba0': {
                'state': 'in-use',
                'size': 50,
                'volume_type': 'gp2'
            }
        }
    }
    
    # Sample utilization data
    dates = pd.date_range(start='2024-01-01', periods=168, freq='H')
    utilization_data = pd.DataFrame({
        'resource_id': ['i-1234567890abcdef0'] * 168,
        'timestamp': dates,
        'cpu_utilization': np.random.normal(15, 5, 168).clip(0, 100),
        'memory_utilization': np.random.normal(25, 8, 168).clip(0, 100)
    })
    
    # Sample cost data
    cost_data = pd.DataFrame({
        'date': pd.date_range(start='2024-01-01', periods=30, freq='D'),
        'cost': np.random.normal(500, 50, 30)
    })
    
    # Generate recommendations
    recommendations = engine.generate_all_recommendations(
        cost_data, utilization_data, resource_inventory
    )
    
    # Generate report
    report = engine.generate_recommendation_report()
    
    print("Optimization Recommendations Report")
    print("=" * 50)
    print(f"Total Recommendations: {report['summary']['total_recommendations']}")
    print(f"Total Monthly Savings Potential: ${report['summary']['total_monthly_savings']:,.2f}")
    print(f"Total Annual Savings Potential: ${report['summary']['total_annual_savings']:,.2f}")
    
    print("\nBy Category:")
    for category, data in report['summary']['by_category'].items():
        print(f"  {category}: {data['count']} recs, ${data['monthly_savings']:,.2f}/month")
    
    print("\nQuick Wins:")
    for win in report['quick_wins']:
        print(f"  - {win['title']}: ${win['monthly_savings']:,.2f}/month")


---

## 10. FinOps Practices & Governance

### 10.1 FinOps Framework Implementation

```python
# /app/cost_optimization/finops/governance.py
"""
FinOps governance and practice implementation
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FinOpsPhase(Enum):
    """FinOps phases"""
    INFORM = "inform"
    OPTIMIZE = "optimize"
    OPERATE = "operate"


class FinOpsCapability(Enum):
    """FinOps capabilities"""
    COST_ALLOCATION = "cost_allocation"
    DATA_ANALYSIS = "data_analysis"
    MEASURING_UNIT_COSTS = "measuring_unit_costs"
    MANAGING_ANOMALIES = "managing_anomalies"
    BUDGET_MANAGEMENT = "budget_management"
    WORKLOAD_OPTIMIZATION = "workload_optimization"
    RATE_OPTIMIZATION = "rate_optimization"
    COMMITMENT_MANAGEMENT = "commitment_management"
    CLOUD_POLICY_GOVERNANCE = "cloud_policy_governance"
    RESOURCE_UTILIZATION = "resource_utilization_efficiency"


@dataclass
class FinOpsMetric:
    """FinOps metric definition"""
    name: str
    description: str
    calculation_method: str
    target_value: float
    current_value: float
    unit: str
    frequency: str


class FinOpsGovernance:
    """Implement FinOps governance framework"""
    
    def __init__(self):
        self.capabilities: Dict[FinOpsCapability, Dict] = {}
        self.policies: List[Dict] = []
        self.metrics: List[FinOpsMetric] = []
        self._initialize_capabilities()
    
    def _initialize_capabilities(self):
        """Initialize FinOps capabilities"""
        
        self.capabilities = {
            FinOpsCapability.COST_ALLOCATION: {
                'maturity': 'advanced',
                'implemented': True,
                'owner': 'finance_team',
                'tools': ['cost_allocation_engine', 'tagging_policy'],
                'kpis': ['tag_compliance_rate', 'allocation_accuracy']
            },
            FinOpsCapability.DATA_ANALYSIS: {
                'maturity': 'advanced',
                'implemented': True,
                'owner': 'platform_team',
                'tools': ['cost_data_warehouse', 'analytics_dashboard'],
                'kpis': ['data_freshness', 'report_accuracy']
            },
            FinOpsCapability.MEASURING_UNIT_COSTS: {
                'maturity': 'intermediate',
                'implemented': True,
                'owner': 'engineering_leads',
                'tools': ['unit_cost_calculator', 'business_metrics'],
                'kpis': ['cost_per_transaction', 'cost_per_user']
            },
            FinOpsCapability.MANAGING_ANOMALIES: {
                'maturity': 'advanced',
                'implemented': True,
                'owner': 'platform_team',
                'tools': ['anomaly_detector', 'alert_manager'],
                'kpis': ['detection_time', 'false_positive_rate']
            },
            FinOpsCapability.BUDGET_MANAGEMENT: {
                'maturity': 'advanced',
                'implemented': True,
                'owner': 'finance_team',
                'tools': ['budget_manager', 'forecasting_engine'],
                'kpis': ['budget_variance', 'forecast_accuracy']
            },
            FinOpsCapability.WORKLOAD_OPTIMIZATION: {
                'maturity': 'intermediate',
                'implemented': True,
                'owner': 'engineering_teams',
                'tools': ['right_sizing_analyzer', 'spot_manager'],
                'kpis': ['utilization_rate', 'optimization_savings']
            },
            FinOpsCapability.RATE_OPTIMIZATION: {
                'maturity': 'intermediate',
                'implemented': True,
                'owner': 'platform_team',
                'tools': ['reserved_capacity_planner', 'savings_calculator'],
                'kpis': ['coverage_rate', 'savings_realized']
            },
            FinOpsCapability.COMMITMENT_MANAGEMENT: {
                'maturity': 'intermediate',
                'implemented': True,
                'owner': 'finance_team',
                'tools': ['commitment_optimizer', 'utilization_tracker'],
                'kpis': ['utilization_rate', 'commitment_coverage']
            },
            FinOpsCapability.CLOUD_POLICY_GOVERNANCE: {
                'maturity': 'advanced',
                'implemented': True,
                'owner': 'security_team',
                'tools': ['policy_engine', 'compliance_checker'],
                'kpis': ['policy_compliance', 'violation_count']
            },
            FinOpsCapability.RESOURCE_UTILIZATION: {
                'maturity': 'intermediate',
                'implemented': True,
                'owner': 'engineering_teams',
                'tools': ['utilization_monitor', 'efficiency_analyzer'],
                'kpis': ['cpu_utilization', 'memory_utilization']
            }
        }
    
    def define_tagging_policy(self) -> Dict:
        """Define comprehensive tagging policy"""
        
        return {
            'policy_name': 'ResilienceAI Resource Tagging Policy',
            'version': '2.0',
            'effective_date': '2024-01-01',
            'mandatory_tags': {
                'CostCenter': {
                    'description': 'Cost center for chargeback',
                    'allowed_values': [
                        'engineering',
                        'data-science',
                        'platform',
                        'operations',
                        'security'
                    ],
                    'validation': 'strict'
                },
                'Team': {
                    'description': 'Team responsible for resource',
                    'allowed_values': None,  # Free text
                    'validation': 'required'
                },
                'Project': {
                    'description': 'Project or application name',
                    'allowed_values': None,
                    'validation': 'required'
                },
                'Environment': {
                    'description': 'Deployment environment',
                    'allowed_values': [
                        'production',
                        'staging',
                        'development',
                        'testing'
                    ],
                    'validation': 'strict'
                },
                'Owner': {
                    'description': 'Email of resource owner',
                    'allowed_values': None,
                    'validation': 'email_format'
                }
            },
            'optional_tags': {
                'DataClassification': {
                    'description': 'Data sensitivity level',
                    'allowed_values': ['public', 'internal', 'confidential', 'restricted']
                },
                'BackupPolicy': {
                    'description': 'Backup requirements',
                    'allowed_values': ['daily', 'weekly', 'monthly', 'none']
                },
                'AutoShutdown': {
                    'description': 'Auto-shutdown schedule',
                    'allowed_values': ['nights-weekends', 'weekends-only', 'never']
                },
                'WorkloadType': {
                    'description': 'Type of workload',
                    'allowed_values': ['api', 'batch', 'training', 'inference', 'database']
                }
            },
            'enforcement': {
                'prevent_resource_creation': True,
                'alert_on_violation': True,
                'remediation_automation': True,
                'compliance_threshold': 95.0
            }
        }
    
    def define_cost_optimization_policy(self) -> Dict:
        """Define cost optimization policy"""
        
        return {
            'policy_name': 'ResilienceAI Cost Optimization Policy',
            'version': '2.0',
            'principles': [
                'Optimize continuously, not just during budget reviews',
                'Rightsize before purchasing reserved capacity',
                'Use spot instances for fault-tolerant workloads',
                'Implement auto-shutdown for non-production environments',
                'Regular waste detection and remediation'
            ],
            'rules': {
                'instance_rightsizing': {
                    'description': 'Right-size underutilized instances',
                    'threshold_cpu': 30,
                    'threshold_memory': 50,
                    'evaluation_period_days': 14,
                    'action': 'recommend_downsize',
                    'auto_approve_savings_above': 500
                },
                'reserved_capacity': {
                    'description': 'Purchase reserved capacity for stable workloads',
                    'min_stable_hours_monthly': 500,
                    'preferred_term': 1,
                    'preferred_payment': 'partial_upfront',
                    'coverage_target': 70
                },
                'spot_instances': {
                    'description': 'Use spot instances for eligible workloads',
                    'eligible_workloads': ['batch', 'training', 'processing'],
                    'min_savings_threshold': 50,
                    'max_interruption_tolerance': 'medium'
                },
                'storage_lifecycle': {
                    'description': 'Implement storage lifecycle policies',
                    'transition_to_ia_after_days': 30,
                    'transition_to_glacier_after_days': 90,
                    'delete_after_days': 365
                },
                'auto_shutdown': {
                    'description': 'Auto-shutdown non-production resources',
                    'environments': ['development', 'testing'],
                    'shutdown_schedule': '0 19 * * 1-5',  # 7 PM weekdays
                    'startup_schedule': '0 8 * * 1-5'  # 8 AM weekdays
                }
            },
            'governance': {
                'cost_review_frequency': 'weekly',
                'optimization_review_frequency': 'monthly',
                'budget_owner_meeting_frequency': 'monthly',
                'escalation_threshold_percent': 90
            }
        }
    
    def create_cost_awareness_program(self) -> Dict:
        """Create cost awareness and education program"""
        
        return {
            'program_name': 'ResilienceAI Cost Awareness Program',
            'objectives': [
                'Increase cost visibility across all teams',
                'Promote cost-conscious engineering practices',
                'Reduce cloud waste through education',
                'Empower teams to optimize their own resources'
            ],
            'initiatives': {
                'training': {
                    'finops_fundamentals': {
                        'audience': 'all_engineers',
                        'frequency': 'quarterly',
                        'format': 'online_course',
                        'duration_hours': 4
                    },
                    'cloud_cost_optimization': {
                        'audience': 'senior_engineers',
                        'frequency': 'bi-annual',
                        'format': 'workshop',
                        'duration_hours': 8
                    },
                    'cost_analysis_tools': {
                        'audience': 'team_leads',
                        'frequency': 'annual',
                        'format': 'hands_on_lab',
                        'duration_hours': 4
                    }
                },
                'communication': {
                    'monthly_cost_newsletter': {
                        'content': ['cost_trends', 'optimization_tips', 'success_stories'],
                        'audience': 'all_staff'
                    },
                    'team_cost_dashboards': {
                        'access': 'self_service',
                        'update_frequency': 'daily'
                    },
                    'cost_alerts': {
                        'channels': ['slack', 'email'],
                        'thresholds': [50, 80, 100]
                    }
                },
                'gamification': {
                    'cost_savings_challenges': {
                        'frequency': 'quarterly',
                        'rewards': 'team_lunch_budget'
                    },
                    'optimization_leaderboard': {
                        'metrics': ['savings_achieved', 'efficiency_improvement'],
                        'visibility': 'internal'
                    }
                }
            },
            'success_metrics': {
                'training_completion_rate': 90,
                'cost_optimization_suggestions_per_quarter': 50,
                'employee_cost_awareness_score': 80
            }
        }
    
    def define_roles_and_responsibilities(self) -> Dict:
        """Define FinOps roles and responsibilities"""
        
        return {
            'executive_sponsor': {
                'role': 'VP of Engineering',
                'responsibilities': [
                    'Champion FinOps culture',
                    'Approve major cost optimization initiatives',
                    'Remove organizational barriers'
                ]
            },
            'finops_practitioner': {
                'role': 'FinOps Analyst',
                'responsibilities': [
                    'Monitor cloud costs daily',
                    'Generate cost reports and analysis',
                    'Identify optimization opportunities',
                    'Track savings realization',
                    'Maintain cost allocation accuracy'
                ]
            },
            'cloud_center_of_excellence': {
                'role': 'Cloud Platform Team',
                'responsibilities': [
                    'Implement cost optimization tools',
                    'Develop cost governance policies',
                    'Provide cost optimization guidance',
                    'Manage reserved capacity purchases',
                    'Maintain tagging compliance'
                ]
            },
            'engineering_teams': {
                'role': 'Engineering Teams',
                'responsibilities': [
                    'Tag all resources correctly',
                    'Right-size their workloads',
                    'Review and act on optimization recommendations',
                    'Participate in cost reviews',
                    'Implement auto-shutdown for dev environments'
                ]
            },
            'finance_team': {
                'role': 'Finance & Procurement',
                'responsibilities': [
                    'Set and manage budgets',
                    'Approve major cloud purchases',
                    'Handle vendor negotiations',
                    'Conduct chargeback/showback',
                    'Forecast cloud spend'
                ]
            }
        }
    
    def get_maturity_assessment(self) -> Dict:
        """Assess FinOps maturity"""
        
        maturity_levels = {
            'crawl': 1,
            'walk': 2,
            'run': 3
        }
        
        assessment = {
            'overall_maturity': 'walk',
            'overall_score': 0,
            'capability_scores': {},
            'recommendations': []
        }
        
        total_score = 0
        capability_count = len(self.capabilities)
        
        for capability, data in self.capabilities.items():
            maturity = data['maturity']
            score = maturity_levels.get(maturity, 1)
            total_score += score
            
            assessment['capability_scores'][capability.value] = {
                'maturity': maturity,
                'score': score,
                'implemented': data['implemented']
            }
        
        assessment['overall_score'] = total_score / capability_count
        
        # Determine overall maturity
        if assessment['overall_score'] >= 2.5:
            assessment['overall_maturity'] = 'run'
        elif assessment['overall_score'] >= 1.5:
            assessment['overall_maturity'] = 'walk'
        else:
            assessment['overall_maturity'] = 'crawl'
        
        # Generate improvement recommendations
        for capability, data in self.capabilities.items():
            if data['maturity'] == 'crawl':
                assessment['recommendations'].append({
                    'capability': capability.value,
                    'current_maturity': 'crawl',
                    'target_maturity': 'walk',
                    'action': f'Implement basic {capability.value} capabilities'
                })
        
        return assessment


class CostAllocationShowback:
    """Implement cost allocation and showback system"""
    
    def __init__(self):
        self.allocation_rules = {}
    
    def generate_monthly_showback(self,
                                   cost_data: Dict,
                                   month: str) -> Dict:
        """Generate monthly showback report"""
        
        showback = {
            'month': month,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_cloud_spend': 0,
                'total_allocated': 0,
                'unallocated': 0,
                'allocation_rate': 0
            },
            'by_team': {},
            'by_project': {},
            'by_environment': {},
            'trends': {}
        }
        
        # Calculate totals
        total_spend = sum(cost_data.values())
        showback['summary']['total_cloud_spend'] = total_spend
        
        # Team breakdown
        for team, costs in cost_data.get('by_team', {}).items():
            showback['by_team'][team] = {
                'total_cost': costs['total'],
                'percentage_of_total': (costs['total'] / total_spend * 100) if total_spend > 0 else 0,
                'by_service': costs.get('by_service', {}),
                'trend': costs.get('trend', 0),
                'budget_variance': costs.get('budget_variance', 0)
            }
        
        # Calculate allocation rate
        allocated = sum(t['total_cost'] for t in showback['by_team'].values())
        showback['summary']['total_allocated'] = allocated
        showback['summary']['unallocated'] = total_spend - allocated
        showback['summary']['allocation_rate'] = (
            allocated / total_spend * 100 if total_spend > 0 else 0
        )
        
        return showback
    
    def calculate_unit_economics(self,
                                  cost_data: Dict,
                                  business_metrics: Dict) -> Dict:
        """Calculate unit economics metrics"""
        
        unit_economics = {
            'calculated_at': datetime.now().isoformat(),
            'metrics': {}
        }
        
        # Cost per API call
        if 'api_calls' in business_metrics:
            api_cost = cost_data.get('api_services', 0)
            unit_economics['metrics']['cost_per_api_call'] = {
                'value': api_cost / business_metrics['api_calls'],
                'unit': 'USD per call',
                'trend': business_metrics.get('api_calls_trend', 0)
            }
        
        # Cost per ML inference
        if 'ml_inferences' in business_metrics:
            ml_cost = cost_data.get('ml_services', 0)
            unit_economics['metrics']['cost_per_inference'] = {
                'value': ml_cost / business_metrics['ml_inferences'],
                'unit': 'USD per inference',
                'trend': business_metrics.get('ml_inferences_trend', 0)
            }
        
        # Cost per active user
        if 'active_users' in business_metrics:
            total_cost = cost_data.get('total', 0)
            unit_economics['metrics']['cost_per_user'] = {
                'value': total_cost / business_metrics['active_users'],
                'unit': 'USD per user',
                'trend': business_metrics.get('active_users_trend', 0)
            }
        
        # Cost per GB processed
        if 'data_processed_gb' in business_metrics:
            data_cost = cost_data.get('data_services', 0)
            unit_economics['metrics']['cost_per_gb'] = {
                'value': data_cost / business_metrics['data_processed_gb'],
                'unit': 'USD per GB',
                'trend': business_metrics.get('data_processed_gb_trend', 0)
            }
        
        return unit_economics


# Usage example
if __name__ == "__main__":
    finops = FinOpsGovernance()
    
    # Get tagging policy
    tagging_policy = finops.define_tagging_policy()
    print("Tagging Policy:")
    print(f"  Mandatory tags: {list(tagging_policy['mandatory_tags'].keys())}")
    print(f"  Optional tags: {list(tagging_policy['optional_tags'].keys())}")
    
    # Get cost optimization policy
    cost_policy = finops.define_cost_optimization_policy()
    print("\nCost Optimization Principles:")
    for principle in cost_policy['principles']:
        print(f"  - {principle}")
    
    # Get maturity assessment
    maturity = finops.get_maturity_assessment()
    print(f"\nFinOps Maturity Assessment:")
    print(f"  Overall Maturity: {maturity['overall_maturity']}")
    print(f"  Overall Score: {maturity['overall_score']:.2f}/3.0")
    
    print("\nCapability Scores:")
    for capability, score in maturity['capability_scores'].items():
        print(f"  {capability}: {score['maturity']} (score: {score['score']})")
    
    # Create showback report
    showback_system = CostAllocationShowback()
    
    sample_cost_data = {
        'by_team': {
            'ml-platform': {
                'total': 15000,
                'by_service': {'EC2': 8000, 'SageMaker': 5000, 'S3': 2000},
                'trend': 5.2,
                'budget_variance': -500
            },
            'data-science': {
                'total': 12000,
                'by_service': {'EC2': 6000, 'EMR': 4000, 'S3': 2000},
                'trend': 3.1,
                'budget_variance': 200
            }
        }
    }
    
    showback = showback_system.generate_monthly_showback(sample_cost_data, '2024-01')
    
    print("\n\nShowback Report (2024-01):")
    print(f"  Total Cloud Spend: ${showback['summary']['total_cloud_spend']:,.2f}")
    print(f"  Allocation Rate: {showback['summary']['allocation_rate']:.1f}%")
    
    print("\nBy Team:")
    for team, data in showback['by_team'].items():
        print(f"  {team}: ${data['total_cost']:,.2f} ({data['percentage_of_total']:.1f}%)")
        print(f"    Trend: {data['trend']:+.1f}%, Budget Variance: ${data['budget_variance']:+,.2f}")
```

---

## 11. Implementation Guide

### 11.1 Implementation Phases

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COST OPTIMIZATION IMPLEMENTATION ROADMAP                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 1: FOUNDATION (Weeks 1-4)                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Deploy cost monitoring infrastructure                            │   │
│  │ • Implement tagging policy and compliance                          │   │
│  │ • Set up budget alerts and basic dashboards                        │   │
│  │ • Establish cost allocation framework                              │   │
│  │ • Train teams on FinOps fundamentals                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  Expected Savings: 5-10%                                                    │
│                                                                             │
│  PHASE 2: QUICK WINS (Weeks 5-8)                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Identify and eliminate idle resources                            │   │
│  │ • Delete unattached volumes and unused IPs                         │   │
│  │ • Implement auto-shutdown for dev environments                     │   │
│  │ • Right-size obvious over-provisioned instances                    │   │
│  │ • Clean up old snapshots and unused load balancers                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  Expected Savings: 15-20% additional                                        │
│                                                                             │
│  PHASE 3: OPTIMIZATION (Weeks 9-16)                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Implement comprehensive right-sizing program                     │   │
│  │ • Purchase reserved capacity for stable workloads                  │   │
│  │ • Migrate fault-tolerant workloads to spot instances               │   │
│  │ • Optimize storage with lifecycle policies                         │   │
│  │ • Implement container resource optimization                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  Expected Savings: 20-30% additional                                        │
│                                                                             │
│  PHASE 4: AUTOMATION (Weeks 17-24)                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Automate waste detection and remediation                         │   │
│  │ • Implement predictive cost forecasting                            │   │
│  │ • Set up continuous optimization recommendations                   │   │
│  │ • Deploy intelligent spot instance management                      │   │
│  │ • Establish FinOps governance at scale                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  Expected Savings: 5-10% additional, sustained                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.2 Implementation Priority Matrix

| Priority | Category | Action | Effort | Impact | Timeline |
|----------|----------|--------|--------|--------|----------|
| P0 | Monitoring | Deploy cost monitoring infrastructure | Medium | High | Week 1-2 |
| P0 | Governance | Implement mandatory tagging policy | Low | High | Week 1-2 |
| P0 | Budgeting | Set up budget alerts and thresholds | Low | High | Week 2 |
| P1 | Waste | Delete unattached volumes | Low | High | Week 3-4 |
| P1 | Waste | Release unused Elastic IPs | Low | Medium | Week 3-4 |
| P1 | Waste | Terminate idle instances | Low | High | Week 3-4 |
| P1 | Optimization | Auto-shutdown dev environments | Low | High | Week 4-5 |
| P2 | Right-sizing | Right-size over-provisioned instances | Medium | High | Week 6-10 |
| P2 | Reserved | Purchase Savings Plans | Low | High | Week 8-12 |
| P2 | Spot | Migrate batch workloads to spot | Medium | High | Week 10-14 |
| P3 | Storage | Implement lifecycle policies | Low | Medium | Week 12-16 |
| P3 | Architecture | Optimize container resources | Medium | Medium | Week 14-18 |
| P4 | Automation | Automate waste remediation | High | Medium | Week 18-24 |
| P4 | ML | Deploy predictive forecasting | High | Medium | Week 20-24 |

### 11.3 Key Performance Indicators (KPIs)

```python
# /app/cost_optimization/metrics/kpis.py
"""
Cost optimization KPIs and metrics tracking
"""

COST_OPTIMIZATION_KPIS = {
    'financial_metrics': {
        'monthly_cloud_spend': {
            'description': 'Total monthly cloud spend',
            'target': 'Within budget',
            'frequency': 'daily',
            'alert_threshold': 'budget_90_percent'
        },
        'cost_per_transaction': {
            'description': 'Cost per business transaction',
            'target': 'Decreasing trend',
            'frequency': 'weekly',
            'alert_threshold': 'increase_10_percent'
        },
        'savings_realized': {
            'description': 'Actual savings from optimizations',
            'target': '> 20% of spend',
            'frequency': 'monthly',
            'alert_threshold': 'none'
        },
        'forecast_accuracy': {
            'description': 'Accuracy of cost forecasts',
            'target': '> 90%',
            'frequency': 'monthly',
            'alert_threshold': '< 80%'
        }
    },
    'operational_metrics': {
        'resource_utilization': {
            'description': 'Average resource utilization',
            'target': '> 60%',
            'frequency': 'daily',
            'alert_threshold': '< 40%'
        },
        'tag_compliance_rate': {
            'description': 'Percentage of resources properly tagged',
            'target': '> 95%',
            'frequency': 'daily',
            'alert_threshold': '< 90%'
        },
        'waste_identified': {
            'description': 'Monthly waste identified',
            'target': 'Decreasing trend',
            'frequency': 'weekly',
            'alert_threshold': '> 5% of spend'
        },
        'optimization_recommendations': {
            'description': 'Number of recommendations implemented',
            'target': '> 80% of high-priority',
            'frequency': 'weekly',
            'alert_threshold': '< 50%'
        }
    },
    'efficiency_metrics': {
        'reserved_capacity_coverage': {
            'description': 'Percentage of usage covered by reserved capacity',
            'target': '> 70%',
            'frequency': 'monthly',
            'alert_threshold': '< 50%'
        },
        'spot_instance_adoption': {
            'description': 'Percentage of eligible workloads on spot',
            'target': '> 50%',
            'frequency': 'weekly',
            'alert_threshold': '< 30%'
        },
        'right_sizing_rate': {
            'description': 'Percentage of instances properly sized',
            'target': '> 90%',
            'frequency': 'monthly',
            'alert_threshold': '< 70%'
        }
    }
}


class KPITracker:
    """Track and report on cost optimization KPIs"""
    
    def __init__(self):
        self.metrics_history = {}
    
    def record_metric(self, metric_name: str, value: float, timestamp: datetime = None):
        """Record a metric value"""
        
        if metric_name not in self.metrics_history:
            self.metrics_history[metric_name] = []
        
        self.metrics_history[metric_name].append({
            'value': value,
            'timestamp': timestamp or datetime.now()
        })
    
    def get_metric_trend(self, metric_name: str, days: int = 30) -> Dict:
        """Get trend for a metric"""
        
        history = self.metrics_history.get(metric_name, [])
        
        if len(history) < 2:
            return {'trend': 'insufficient_data'}
        
        # Get recent values
        cutoff = datetime.now() - timedelta(days=days)
        recent = [h for h in history if h['timestamp'] > cutoff]
        
        if len(recent) < 2:
            return {'trend': 'insufficient_data'}
        
        values = [h['value'] for h in recent]
        
        # Calculate trend
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        change = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
        
        return {
            'current_value': values[-1],
            'average': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
            'trend_percent': change,
            'trend_direction': 'improving' if change < 0 and 'cost' in metric_name else 
                              ('improving' if change > 0 else 'degrading')
        }
    
    def generate_kpi_dashboard(self) -> Dict:
        """Generate KPI dashboard data"""
        
        dashboard = {
            'generated_at': datetime.now().isoformat(),
            'kpis': {}
        }
        
        for category, metrics in COST_OPTIMIZATION_KPIS.items():
            dashboard['kpis'][category] = {}
            
            for metric_name, config in metrics.items():
                trend = self.get_metric_trend(metric_name)
                
                dashboard['kpis'][category][metric_name] = {
                    'config': config,
                    'current': trend.get('current_value'),
                    'trend': trend
                }
        
        return dashboard
```

---

## 12. Best Practices Summary

### 12.1 Cost Optimization Best Practices

| Area | Best Practice | Implementation |
|------|--------------|----------------|
| **Tagging** | Mandatory tags on all resources | Enforce via policy, block non-compliant creation |
| **Monitoring** | Real-time cost visibility | Deploy dashboards, daily cost emails |
| **Budgeting** | Team-level budgets with alerts | 50%, 80%, 100% thresholds |
| **Right-sizing** | Continuous right-sizing analysis | Weekly automated analysis, monthly reviews |
| **Reserved** | Purchase for stable workloads | 70% coverage target, 1-year terms |
| **Spot** | Use for fault-tolerant workloads | 50% adoption target, proper handling |
| **Waste** | Automated waste detection | Daily scans, weekly remediation |
| **Storage** | Lifecycle policies on all data | 30d IA, 90d Glacier, 365d delete |
| **Dev/Test** | Auto-shutdown schedules | 7 PM - 8 AM weekdays, weekends off |
| **Governance** | FinOps culture and training | Monthly reviews, quarterly training |

### 12.2 Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|-------------|---------|----------|
| Over-provisioning "just in case" | Wasted resources | Right-size based on actual usage |
| Ignoring dev/test costs | 30-40% of waste | Auto-shutdown, resource quotas |
| Manual cost reviews | Delayed optimization | Automated monitoring and alerts |
| No tagging strategy | Unallocated costs | Mandatory tags, compliance checks |
| Buying reserved capacity without analysis | Under-utilization | Analyze 30-day usage first |
| One-size-fits-all instance types | Poor efficiency | Match instance to workload |
| Ignoring storage costs | Growing waste | Lifecycle policies, regular cleanup |
| No spot instance strategy | Missing savings | Identify fault-tolerant workloads |

---

## 13. Tools and Integration

### 13.1 Recommended Tool Stack

| Category | Tool | Purpose | Integration |
|----------|------|---------|-------------|
| **Cost Collection** | AWS Cost Explorer API | AWS cost data | Python SDK |
| **Cost Collection** | Azure Cost Management API | Azure cost data | Python SDK |
| **Cost Collection** | GCP Billing Export | GCP cost data | BigQuery |
| **Monitoring** | Prometheus + Grafana | Resource metrics | Native |
| **Forecasting** | Prophet | Cost forecasting | Python library |
| **Storage** | TimescaleDB | Cost data warehouse | SQL |
| **Visualization** | Grafana | Cost dashboards | Native |
| **Alerting** | PagerDuty | Budget alerts | Webhook |
| **Automation** | Kubernetes Operators | Resource optimization | CRDs |
| **Reporting** | Custom Python | Cost reports | Scheduled jobs |

### 13.2 Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA COLLECTION LAYER                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────────┐   │
│  │ AWS APIs   │  │ Azure APIs │  │  GCP APIs  │  │ Kubernetes Metrics │   │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────────┬──────────┘   │
└────────┼───────────────┼───────────────┼───────────────────┼──────────────┘
         │               │               │                   │
         └───────────────┴───────┬───────┴───────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│                          PROCESSING LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Cost Normalization → Tag Enforcement → Allocation → Analytics      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│                         DATA STORAGE LAYER                                  │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ │
│  │ TimescaleDB         │  │ ClickHouse          │  │ S3 (Parquet)        │ │
│  │ (Real-time costs)   │  │ (Analytics)         │  │ (Historical)        │ │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│                        APPLICATION LAYER                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Right-Sizing │  │ Reserved     │  │ Spot         │  │ Waste        │   │
│  │ Analyzer     │  │ Planner      │  │ Manager      │  │ Detector     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Budget       │  │ Forecasting  │  │ Allocation   │  │ Recommendation│  │
│  │ Manager      │  │ Engine       │  │ Engine       │  │ Engine       │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────────┐
│                        PRESENTATION LAYER                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ Grafana         │  │ Email Reports   │  │ Slack Alerts    │             │
│  │ Dashboards      │  │ (Daily/Weekly)  │  │ (Real-time)     │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 14. Conclusion

This comprehensive cost optimization framework for ResilienceAI provides:

1. **Complete visibility** into cloud costs across all providers
2. **Automated optimization** through right-sizing, spot instances, and waste elimination
3. **Reserved capacity planning** to maximize savings on stable workloads
4. **Budget governance** with proactive alerts and forecasting
5. **FinOps practices** to build cost-conscious culture

**Expected Outcomes:**
- 30-40% reduction in cloud spend within 6 months
- 95%+ resource tagging compliance
- 70%+ reserved capacity coverage
- 50%+ spot instance adoption for eligible workloads
- Real-time cost visibility for all teams

**Next Steps:**
1. Deploy cost monitoring infrastructure (Week 1-2)
2. Implement tagging policy (Week 1-2)
3. Identify and eliminate waste (Week 3-4)
4. Begin right-sizing program (Week 5-8)
5. Purchase reserved capacity (Week 8-12)
6. Implement continuous optimization (Ongoing)

---

## Appendix A: Quick Reference Commands

```bash
# AWS Cost Explorer CLI examples
# Get current month costs by service
aws ce get-cost-and-usage \
  --time-period Start=$(date -d "$(date +%Y-%m-01)" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# Get Savings Plans recommendations
aws ce get-savings-plans-purchase-recommendation \
  --savings-plans-type COMPUTE_SP \
  --term-in-years ONE_YEAR \
  --payment-option PARTIAL_UPFRONT \
  --lookback-period-in-days THIRTY_DAYS

# Find unattached volumes
aws ec2 describe-volumes \
  --filters Name=status,Values=available \
  --query 'Volumes[*].[VolumeId,Size,CreateTime]'

# Find unused Elastic IPs
aws ec2 describe-addresses \
  --query 'Addresses[?AssociationId==null].[AllocationId,PublicIp]'
```

## Appendix B: File Structure

```
/app/cost_optimization/
├── collectors/
│   ├── cloud_cost_collector.py      # Multi-cloud cost collection
│   └── realtime_metrics.py          # Real-time metrics collection
├── right_sizing/
│   └── analyzer.py                  # Right-sizing analysis engine
├── reserved_capacity/
│   └── planner.py                   # Reserved capacity planning
├── spot_instances/
│   └── manager.py                   # Spot instance management
├── allocation/
│   └── allocator.py                 # Cost allocation & tagging
├── budget/
│   └── manager.py                   # Budget management & forecasting
├── waste_detection/
│   └── detector.py                  # Resource waste detection
├── recommendations/
│   └── engine.py                    # Optimization recommendations
├── finops/
│   └── governance.py                # FinOps governance
└── metrics/
    └── kpis.py                      # KPI tracking
```

---

*Document Version: 1.0*
*Last Updated: 2024*
*Author: ResilienceAI Cost Optimization Team*
