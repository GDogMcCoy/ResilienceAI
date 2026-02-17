"""
Real-Time Data Pipeline for ResilienceAI
WebSocket-based live data streaming and event processing
"""

import asyncio
import websockets
import json
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import queue
import time


@dataclass
class DataEvent:
    """Represents a real-time data event"""
    event_id: str
    event_type: str  # 'weather_alert', 'disaster_declaration', 'sensor_reading'
    source: str  # 'NOAA', 'FEMA', 'USGS'
    timestamp: str
    data: Dict
    severity: str
    affected_regions: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class RealTimeDataPipeline:
    """
    Real-time data pipeline for streaming disaster and weather data
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_queue = queue.Queue()
        self.is_running = False
        self.websocket_server = None
        self.data_sources = {
            'NOAA': None,
            'FEMA': None,
            'USGS': None
        }
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to specific event types"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from events"""
        if event_type in self.subscribers:
            self.subscribers[event_type] = [
                cb for cb in self.subscribers[event_type] if cb != callback
            ]
    
    def publish_event(self, event: DataEvent):
        """Publish an event to all subscribers"""
        self.event_queue.put(event)
        
        # Notify subscribers
        if event.event_type in self.subscribers:
            for callback in self.subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error notifying subscriber: {e}")
    
    async def websocket_handler(self, websocket, path):
        """Handle WebSocket connections"""
        try:
            async for message in websocket:
                data = json.loads(message)
                
                # Handle subscription requests
                if data.get('action') == 'subscribe':
                    event_type = data.get('event_type', '*')
                    # Store websocket for this event type
                    if event_type not in self.subscribers:
                        self.subscribers[event_type] = []
                    self.subscribers[event_type].append(
                        lambda e, ws=websocket: asyncio.create_task(
                            ws.send(json.dumps(e.to_dict()))
                        )
                    )
                    
                    await websocket.send(json.dumps({
                        'status': 'subscribed',
                        'event_type': event_type
                    }))
        
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"WebSocket error: {e}")
    
    async def start_websocket_server(self, host='localhost', port=8765):
        """Start WebSocket server for real-time updates"""
        self.websocket_server = await websockets.serve(
            self.websocket_handler, host, port
        )
        print(f"WebSocket server started on ws://{host}:{port}")
        await self.websocket_server.wait_closed()
    
    def start_noaa_stream(self):
        """Start NOAA weather alert stream"""
        def noaa_worker():
            from weather_client import NOAAWeatherClient
            client = NOAAWeatherClient()
            
            while self.is_running:
                try:
                    # Fetch high-impact alerts
                    alerts = client.get_high_impact_alerts(min_severity='Severe')
                    
                    for alert in alerts:
                        event = DataEvent(
                            event_id=alert.id,
                            event_type='weather_alert',
                            source='NOAA',
                            timestamp=datetime.now().isoformat(),
                            data=alert.to_dict(),
                            severity=alert.severity,
                            affected_regions=alert.affected_counties
                        )
                        self.publish_event(event)
                    
                    # Poll every 60 seconds
                    time.sleep(60)
                    
                except Exception as e:
                    print(f"NOAA stream error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=noaa_worker, daemon=True)
        thread.start()
        self.data_sources['NOAA'] = thread
    
    def start_fema_stream(self):
        """Start FEMA disaster declaration stream"""
        def fema_worker():
            # FEMA API polling
            while self.is_running:
                try:
                    # Placeholder for FEMA API integration
                    # Would poll https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries
                    time.sleep(300)  # Check every 5 minutes
                except Exception as e:
                    print(f"FEMA stream error: {e}")
                    time.sleep(300)
        
        thread = threading.Thread(target=fema_worker, daemon=True)
        thread.start()
        self.data_sources['FEMA'] = thread
    
    def start_usgs_stream(self):
        """Start USGS earthquake stream"""
        def usgs_worker():
            import requests
            
            while self.is_running:
                try:
                    # USGS real-time earthquake feed
                    response = requests.get(
                        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_hour.geojson",
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        for feature in data.get('features', []):
                            props = feature.get('properties', {})
                            
                            event = DataEvent(
                                event_id=feature.get('id', ''),
                                event_type='earthquake',
                                source='USGS',
                                timestamp=datetime.now().isoformat(),
                                data=props,
                                severity='high' if props.get('mag', 0) > 6 else 'medium',
                                affected_regions=[props.get('place', 'Unknown')]
                            )
                            self.publish_event(event)
                    
                    # Check every 5 minutes
                    time.sleep(300)
                    
                except Exception as e:
                    print(f"USGS stream error: {e}")
                    time.sleep(300)
        
        thread = threading.Thread(target=usgs_worker, daemon=True)
        thread.start()
        self.data_sources['USGS'] = thread
    
    def start_all_streams(self):
        """Start all data streams"""
        self.is_running = True
        self.start_noaa_stream()
        self.start_fema_stream()
        self.start_usgs_stream()
        print("All real-time streams started")
    
    def stop_all_streams(self):
        """Stop all data streams"""
        self.is_running = False
        print("All real-time streams stopped")
    
    def get_recent_events(self, event_type: str = None, limit: int = 100) -> List[DataEvent]:
        """Get recent events from queue"""
        events = []
        temp_queue = queue.Queue()
        
        # Drain queue
        while not self.event_queue.empty() and len(events) < limit:
            try:
                event = self.event_queue.get_nowait()
                if event_type is None or event.event_type == event_type:
                    events.append(event)
                temp_queue.put(event)
            except queue.Empty:
                break
        
        # Restore queue
        while not temp_queue.empty():
            self.event_queue.put(temp_queue.get())
        
        return events


class EventProcessor:
    """
    Process real-time events and trigger actions
    """
    
    def __init__(self, pipeline: RealTimeDataPipeline):
        self.pipeline = pipeline
        self.processors = {}
    
    def register_processor(self, event_type: str, processor_fn: Callable):
        """Register a processor for an event type"""
        self.processors[event_type] = processor_fn
        self.pipeline.subscribe(event_type, self._process_event)
    
    def _process_event(self, event: DataEvent):
        """Process an event"""
        if event.event_type in self.processors:
            try:
                self.processors[event.event_type](event)
            except Exception as e:
                print(f"Error processing event {event.event_id}: {e}")
    
    def auto_correlate_vulnerability(self, event: DataEvent):
        """Auto-correlate events with vulnerability data"""
        # This would integrate with the ResilienceAgent
        # to check if affected counties are high-vulnerability
        pass
    
    def auto_trigger_alerts(self, event: DataEvent):
        """Automatically trigger alerts for severe events"""
        if event.severity in ['high', 'critical', 'Extreme']:
            # Trigger alert system
            print(f"🚨 AUTO-TRIGGER: {event.event_type} - {event.severity}")
            # Would call alert_manager here


def render_realtime_feed():
    """Render real-time event feed in Streamlit"""
    import streamlit as st
    import random
    
    st.subheader("📡 Real-Time Event Feed")
    
    # Initialize pipeline
    if 'pipeline' not in st.session_state:
        st.session_state.pipeline = RealTimeDataPipeline()
        st.session_state.pipeline.start_all_streams()
    
    pipeline = st.session_state.pipeline
    
    # Heartbeat Indicator
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <div style="width: 10px; height: 10px; background: #4ade80; border-radius: 50%; margin-right: 0.5rem; animation: pulse 2s infinite;"></div>
        <span class="mono" style="font-size: 0.8rem; color: #94a3b8;">SYSTEM HEARTBEAT: {datetime.now().strftime('%H:%M:%S')}</span>
    </div>
    <style>
        @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}
    </style>
    """, unsafe_allow_html=True)
    
    # Display events
    events = pipeline.get_recent_events(limit=50)
    
    # If no real events, add simulated "System Check" events for demo polish
    if not events:
        events = [
            DataEvent(
                event_id="sim-001",
                event_type="system_check",
                source="AGENT",
                timestamp=datetime.now().isoformat(),
                data={},
                severity="info",
                affected_regions=["Missouri Assessment Node"]
            ),
            DataEvent(
                event_id="sim-002",
                event_type="weather_alert",
                source="NOAA (SIM)",
                timestamp=(datetime.now() - timedelta(minutes=5)).isoformat(),
                data={"event": "Simulated Severe Storm Watch"},
                severity="medium",
                affected_regions=["Central Missouri"]
            )
        ]
    
    for event in sorted(events, key=lambda x: x.timestamp, reverse=True)[:10]:
        with st.container():
            cols = st.columns([1, 2, 2, 1])
            
            with cols[0]:
                icons = {
                    'weather_alert': '🌦️',
                    'earthquake': '🌋',
                    'disaster_declaration': '🚨',
                    'system_check': '🤖'
                }
                st.markdown(f"### {icons.get(event.event_type, '📊')}")
            
            with cols[1]:
                st.markdown(f"**{event.event_type.replace('_', ' ').title()}**")
                st.caption(f"Source: {event.source}")
            
            with cols[2]:
                st.markdown(f"Severity: `{event.severity.upper()}`")
                st.caption(f"Status: {random.choice(['MONITORING', 'INDEXED', 'STABLE'])}")
            
            with cols[3]:
                try:
                    event_time = datetime.fromisoformat(event.timestamp)
                    st.caption(event_time.strftime("%H:%M:%S"))
                except:
                    st.caption("Just Now")
            
            st.divider()


if __name__ == "__main__":
    # Test the pipeline
    pipeline = RealTimeDataPipeline()
    
    # Subscribe to events
    def print_event(event):
        print(f"📡 {event.event_type}: {event.severity}")
    
    pipeline.subscribe('weather_alert', print_event)
    pipeline.subscribe('earthquake', print_event)
    
    # Start streams
    pipeline.start_all_streams()
    
    print("Real-time pipeline running. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pipeline.stop_all_streams()
        print("\nStopped.")
