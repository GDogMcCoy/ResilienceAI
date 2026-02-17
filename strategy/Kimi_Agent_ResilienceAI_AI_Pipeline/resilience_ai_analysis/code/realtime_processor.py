"""
Real-Time Stream Processing for ResilienceAI
Uses Apache Kafka / AWS Kinesis style architecture
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from collections import defaultdict
import numpy as np
from enum import Enum

logger = logging.getLogger(__name__)


class ProcessingWindow(Enum):
    """Time window types for aggregation"""
    TUMBLING = "tumbling"      # Fixed, non-overlapping windows
    SLIDING = "sliding"        # Overlapping windows
    SESSION = "session"        # Dynamic windows based on activity


@dataclass
class StreamEvent:
    """Event in the processing stream"""
    event_id: str
    timestamp: datetime
    device_id: str
    sensor_type: str
    readings: Dict[str, float]
    metadata: Dict[str, Any]


@dataclass
class AggregatedResult:
    """Result of windowed aggregation"""
    window_start: datetime
    window_end: datetime
    device_id: str
    sensor_type: str
    aggregations: Dict[str, Dict[str, float]]  # reading_name -> stats
    event_count: int


class WindowedAggregator:
    """Time-windowed aggregation for sensor streams"""
    
    def __init__(
        self,
        window_size_seconds: int = 60,
        window_type: ProcessingWindow = ProcessingWindow.TUMBLING
    ):
        self.window_size = window_size_seconds
        self.window_type = window_type
        self.windows: Dict[str, List[StreamEvent]] = defaultdict(list)
        self.last_window_end: Dict[str, datetime] = {}
    
    def _get_window_key(self, event: StreamEvent) -> str:
        """Generate key for window lookup"""
        return f"{event.device_id}:{event.sensor_type}"
    
    def _get_window_start(self, timestamp: datetime) -> datetime:
        """Calculate window start time"""
        seconds = timestamp.second + timestamp.microsecond / 1e6
        window_start_seconds = (int(seconds) // self.window_size) * self.window_size
        return timestamp.replace(second=window_start_seconds, microsecond=0)
    
    def add_event(self, event: StreamEvent) -> Optional[AggregatedResult]:
        """Add event to window, return result if window complete"""
        key = self._get_window_key(event)
        window_start = self._get_window_start(event.timestamp)
        
        # Check if we need to emit previous window
        if key in self.last_window_end:
            if event.timestamp >= self.last_window_end[key]:
                result = self._emit_window(key, self.last_window_end[key])
                self.windows[key] = []
                return result
        
        # Add to current window
        self.windows[key].append(event)
        
        # Update window end time
        self.last_window_end[key] = window_start + timedelta(seconds=self.window_size)
        
        return None
    
    def _emit_window(
        self,
        key: str,
        window_end: datetime
    ) -> Optional[AggregatedResult]:
        """Emit aggregated results for a window"""
        events = self.windows.get(key, [])
        
        if not events:
            return None
        
        device_id, sensor_type = key.split(":")
        window_start = self._get_window_start(events[0].timestamp)
        
        # Aggregate by reading name
        reading_values: Dict[str, List[float]] = defaultdict(list)
        
        for event in events:
            for name, value in event.readings.items():
                reading_values[name].append(value)
        
        aggregations = {}
        for name, values in reading_values.items():
            if values:
                aggregations[name] = {
                    "count": len(values),
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "median": np.median(values),
                    "p95": np.percentile(values, 95),
                    "p99": np.percentile(values, 99)
                }
        
        return AggregatedResult(
            window_start=window_start,
            window_end=window_end,
            device_id=device_id,
            sensor_type=sensor_type,
            aggregations=aggregations,
            event_count=len(events)
        )
    
    def flush_all(self) -> List[AggregatedResult]:
        """Force emit all pending windows"""
        results = []
        for key in list(self.windows.keys()):
            if key in self.last_window_end:
                result = self._emit_window(key, self.last_window_end[key])
                if result:
                    results.append(result)
                self.windows[key] = []
        return results


class RealTimeAlertEngine:
    """Real-time alerting based on stream processing"""
    
    def __init__(self):
        self.rules: List[Dict] = []
        self.alert_handlers: List[Callable] = []
    
    def add_rule(
        self,
        name: str,
        sensor_type: str,
        reading_name: str,
        condition: str,  # 'gt', 'lt', 'eq', 'range'
        threshold: float or tuple,
        severity: str = "warning",
        cooldown_seconds: int = 300
    ):
        """Add an alert rule"""
        self.rules.append({
            "name": name,
            "sensor_type": sensor_type,
            "reading_name": reading_name,
            "condition": condition,
            "threshold": threshold,
            "severity": severity,
            "cooldown_seconds": cooldown_seconds,
            "last_triggered": None
        })
    
    def evaluate(self, event: StreamEvent) -> List[Dict]:
        """Evaluate all rules against an event"""
        triggered = []
        
        for rule in self.rules:
            # Check sensor type match
            if rule["sensor_type"] != event.sensor_type:
                continue
            
            # Check if reading exists
            if rule["reading_name"] not in event.readings:
                continue
            
            value = event.readings[rule["reading_name"]]
            
            # Check cooldown
            if rule["last_triggered"]:
                cooldown = timedelta(seconds=rule["cooldown_seconds"])
                if datetime.utcnow() - rule["last_triggered"] < cooldown:
                    continue
            
            # Evaluate condition
            triggered_alert = self._evaluate_condition(
                value, rule["condition"], rule["threshold"]
            )
            
            if triggered_alert:
                rule["last_triggered"] = datetime.utcnow()
                triggered.append({
                    "rule_name": rule["name"],
                    "severity": rule["severity"],
                    "message": f"{rule['reading_name']} = {value:.2f} "
                               f"({rule['condition']} {rule['threshold']})",
                    "device_id": event.device_id,
                    "timestamp": event.timestamp,
                    "value": value
                })
        
        return triggered
    
    def _evaluate_condition(
        self,
        value: float,
        condition: str,
        threshold: any
    ) -> bool:
        """Evaluate a single condition"""
        if condition == "gt":
            return value > threshold
        elif condition == "lt":
            return value < threshold
        elif condition == "eq":
            return value == threshold
        elif condition == "range":
            return threshold[0] <= value <= threshold[1]
        elif condition == "outside":
            return value < threshold[0] or value > threshold[1]
        return False
    
    def register_alert_handler(self, handler: Callable):
        """Register handler for triggered alerts"""
        self.alert_handlers.append(handler)
    
    async def process_alerts(self, alerts: List[Dict]):
        """Process triggered alerts"""
        for alert in alerts:
            for handler in self.alert_handlers:
                try:
                    await handler(alert)
                except Exception as e:
                    logger.error(f"Alert handler error: {e}")


class StreamProcessor:
    """Main stream processing pipeline"""
    
    def __init__(self):
        self.aggregator = WindowedAggregator(window_size_seconds=60)
        self.alert_engine = RealTimeAlertEngine()
        self.processors: List[Callable] = []
        self.output_handlers: List[Callable] = []
        
        # Statistics
        self.stats = {
            "events_processed": 0,
            "alerts_generated": 0,
            "windows_emitted": 0
        }
    
    def add_processor(self, processor: Callable):
        """Add custom processor to pipeline"""
        self.processors.append(processor)
    
    def add_output_handler(self, handler: Callable):
        """Add output handler"""
        self.output_handlers.append(handler)
    
    async def process_event(self, event: StreamEvent):
        """Process a single event through the pipeline"""
        
        # 1. Run custom processors
        for processor in self.processors:
            try:
                event = await processor(event)
                if event is None:
                    return  # Event filtered out
            except Exception as e:
                logger.error(f"Processor error: {e}")
        
        # 2. Add to windowed aggregator
        agg_result = self.aggregator.add_event(event)
        
        if agg_result:
            self.stats["windows_emitted"] += 1
            await self._emit_aggregation(agg_result)
        
        # 3. Evaluate alert rules
        alerts = self.alert_engine.evaluate(event)
        
        if alerts:
            self.stats["alerts_generated"] += len(alerts)
            await self.alert_engine.process_alerts(alerts)
        
        # 4. Send to output handlers
        for handler in self.output_handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Output handler error: {e}")
        
        self.stats["events_processed"] += 1
    
    async def _emit_aggregation(self, result: AggregatedResult):
        """Emit aggregated window result"""
        for handler in self.output_handlers:
            try:
                await handler(result)
            except Exception as e:
                logger.error(f"Aggregation handler error: {e}")
    
    def get_stats(self) -> Dict:
        """Get processing statistics"""
        return self.stats.copy()


# Example usage
async def example():
    # Initialize processor
    processor = StreamProcessor()
    
    # Add alert rules
    processor.alert_engine.add_rule(
        name="high_pm25",
        sensor_type="air_quality",
        reading_name="pm25",
        condition="gt",
        threshold=35.0,  # EPA unhealthy threshold
        severity="warning",
        cooldown_seconds=600
    )
    
    processor.alert_engine.add_rule(
        name="critical_pm25",
        sensor_type="air_quality",
        reading_name="pm25",
        condition="gt",
        threshold=150.0,  # Very unhealthy
        severity="critical",
        cooldown_seconds=300
    )
    
    # Add alert handler
    async def print_alert(alert):
        print(f"ALERT [{alert['severity'].upper()}]: {alert['message']}")
    
    processor.alert_engine.register_alert_handler(print_alert)
    
    # Process sample events
    for i in range(10):
        event = StreamEvent(
            event_id=f"evt_{i}",
            timestamp=datetime.utcnow(),
            device_id="sensor_001",
            sensor_type="air_quality",
            readings={
                "pm25": 20.0 + i * 15,  # Increasing values
                "pm10": 30.0 + i * 20,
                "co2": 400 + i * 10
            },
            metadata={"quality": 0.95}
        )
        
        await processor.process_event(event)
        await asyncio.sleep(0.1)
    
    print(f"\nStats: {processor.get_stats()}")


if __name__ == "__main__":
    asyncio.run(example())
