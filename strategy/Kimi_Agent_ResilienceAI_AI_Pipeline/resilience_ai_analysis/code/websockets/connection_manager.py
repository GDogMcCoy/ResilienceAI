"""
WebSocket Connection Manager for Real-Time Dashboard Updates
Handles live data streaming from NOAA, USGS, and internal sources
"""
import streamlit as st
import asyncio
import json
import threading
import queue
import time
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ConnectionStatus(Enum):
    """WebSocket connection status."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


@dataclass
class DataUpdate:
    """Represents a single data update from a WebSocket source."""
    source: str
    timestamp: datetime
    data_type: str
    payload: Dict[str, Any]
    priority: str = 'normal'  # 'low', 'normal', 'high', 'critical'
    processed: bool = False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'data_type': self.data_type,
            'payload': self.payload,
            'priority': self.priority
        }


@dataclass
class DataSourceConfig:
    """Configuration for a WebSocket data source."""
    name: str
    url: str
    description: str
    reconnect_interval: int = 30
    max_reconnect_attempts: int = 5
    priority_sources: List[str] = field(default_factory=list)
    message_handler: Optional[Callable] = None


class WebSocketManager:
    """
    Manages WebSocket connections for real-time data streaming.
    Supports multiple data sources with automatic reconnection and failover.
    """
    
    DEFAULT_SOURCES = {
        'noaa_alerts': DataSourceConfig(
            name='noaa_alerts',
            url='wss://api.weather.gov/alerts/active',
            description='NOAA Weather Alerts',
            reconnect_interval=30
        ),
        'usgs_earthquakes': DataSourceConfig(
            name='usgs_earthquakes',
            url='wss://earthquake.usgs.gov/streams/websocket',
            description='USGS Earthquake Feed',
            reconnect_interval=60
        ),
        'simulated_feed': DataSourceConfig(
            name='simulated_feed',
            url='internal://simulation',
            description='Simulated Data Feed (Demo Mode)',
            reconnect_interval=10
        )
    }
    
    def __init__(self, sources: Optional[Dict[str, DataSourceConfig]] = None):
        self.sources = sources or self.DEFAULT_SOURCES.copy()
        self.connections: Dict[str, Any] = {}
        self.connection_status: Dict[str, ConnectionStatus] = {
            name: ConnectionStatus.DISCONNECTED for name in self.sources
        }
        self.update_queue: queue.Queue = queue.Queue(maxsize=1000)
        self.subscribers: Dict[str, List[Callable]] = {}
        self.is_running = False
        self._lock = threading.RLock()
        self._threads: Dict[str, threading.Thread] = {}
        self._message_history: List[DataUpdate] = []
        self._max_history = 100
        
    def subscribe(self, source: str, callback: Callable[[DataUpdate], None]):
        """Subscribe to updates from a data source."""
        with self._lock:
            if source not in self.subscribers:
                self.subscribers[source] = []
            self.subscribers[source].append(callback)
            
    def unsubscribe(self, source: str, callback: Callable[[DataUpdate], None]):
        """Unsubscribe from a data source."""
        with self._lock:
            if source in self.subscribers:
                try:
                    self.subscribers[source].remove(callback)
                except ValueError:
                    pass
    
    def add_source(self, config: DataSourceConfig):
        """Add a new data source dynamically."""
        with self._lock:
            self.sources[config.name] = config
            self.connection_status[config.name] = ConnectionStatus.DISCONNECTED
    
    def remove_source(self, name: str):
        """Remove a data source."""
        with self._lock:
            if name in self.sources:
                self.disconnect(name)
                del self.sources[name]
                del self.connection_status[name]
    
    def connect(self, source_name: str) -> bool:
        """Establish connection to a data source."""
        if source_name not in self.sources:
            st.error(f"Unknown data source: {source_name}")
            return False
        
        config = self.sources[source_name]
        self.connection_status[source_name] = ConnectionStatus.CONNECTING
        
        try:
            # For simulated feed, start simulation thread
            if config.url.startswith('internal://'):
                self._start_simulation(source_name)
                return True
            
            # For real WebSocket connections, start async connection
            thread = threading.Thread(
                target=self._run_async_connection,
                args=(source_name,),
                daemon=True,
                name=f"ws-{source_name}"
            )
            thread.start()
            self._threads[source_name] = thread
            return True
            
        except Exception as e:
            self.connection_status[source_name] = ConnectionStatus.ERROR
            st.error(f"Failed to connect to {source_name}: {str(e)}")
            return False
    
    def _start_simulation(self, source_name: str):
        """Start simulated data feed for demo purposes."""
        self.connection_status[source_name] = ConnectionStatus.CONNECTED
        
        def simulate():
            import random
            event_types = ['weather_alert', 'earthquake', 'flood_warning', 'tornado_watch']
            severities = ['low', 'normal', 'high', 'critical']
            
            while self.is_running and self.connection_status[source_name] == ConnectionStatus.CONNECTED:
                time.sleep(random.uniform(5, 15))  # Random interval
                
                update = DataUpdate(
                    source=source_name,
                    timestamp=datetime.now(),
                    data_type=random.choice(event_types),
                    payload={
                        'event_id': f"SIM-{random.randint(1000, 9999)}",
                        'location': f"County {random.randint(1, 100)}",
                        'severity': random.choice(severities),
                        'message': f"Simulated {random.choice(event_types).replace('_', ' ').title()}"
                    },
                    priority=random.choice(['low', 'normal', 'high', 'critical'])
                )
                
                self.update_queue.put(update)
                self._notify_subscribers(update)
        
        thread = threading.Thread(target=simulate, daemon=True)
        thread.start()
        self._threads[source_name] = thread
    
    async def _async_connect(self, source_name: str):
        """Async WebSocket connection handler."""
        try:
            import websockets
            
            config = self.sources[source_name]
            reconnect_attempts = 0
            
            while self.is_running and reconnect_attempts < config.max_reconnect_attempts:
                try:
                    self.connection_status[source_name] = ConnectionStatus.CONNECTING
                    
                    async with websockets.connect(config.url) as ws:
                        self.connections[source_name] = ws
                        self.connection_status[source_name] = ConnectionStatus.CONNECTED
                        reconnect_attempts = 0
                        
                        st.toast(f"Connected to {config.description}")
                        
                        async for message in ws:
                            if not self.is_running:
                                break
                            
                            try:
                                data = json.loads(message)
                                update = self._parse_message(source_name, data)
                                if update:
                                    self.update_queue.put(update)
                                    self._notify_subscribers(update)
                            except json.JSONDecodeError:
                                continue
                                
                except websockets.exceptions.ConnectionClosed:
                    self.connection_status[source_name] = ConnectionStatus.RECONNECTING
                    reconnect_attempts += 1
                    await asyncio.sleep(config.reconnect_interval)
                    
                except Exception as e:
                    self.connection_status[source_name] = ConnectionStatus.ERROR
                    reconnect_attempts += 1
                    await asyncio.sleep(config.reconnect_interval)
                    
        except ImportError:
            st.warning("websockets library not installed. Using simulated mode.")
            self._start_simulation(source_name)
    
    def _parse_message(self, source: str, data: Dict) -> Optional[DataUpdate]:
        """Parse incoming message into DataUpdate."""
        parsers = {
            'noaa_alerts': self._parse_noaa_alert,
            'usgs_earthquakes': self._parse_usgs_earthquake
        }
        
        parser = parsers.get(source)
        if parser:
            return parser(data)
        
        # Generic parser
        return DataUpdate(
            source=source,
            timestamp=datetime.now(),
            data_type=data.get('type', 'unknown'),
            payload=data,
            priority=data.get('priority', 'normal')
        )
    
    def _parse_noaa_alert(self, data: Dict) -> DataUpdate:
        """Parse NOAA alert message."""
        return DataUpdate(
            source='noaa_alerts',
            timestamp=datetime.now(),
            data_type='weather_alert',
            payload={
                'event': data.get('event', 'Unknown'),
                'area': data.get('areaDesc', 'Unknown'),
                'severity': data.get('severity', 'Unknown'),
                'description': data.get('description', '')[:200]
            },
            priority=self._severity_to_priority(data.get('severity', 'Unknown'))
        )
    
    def _parse_usgs_earthquake(self, data: Dict) -> DataUpdate:
        """Parse USGS earthquake message."""
        properties = data.get('properties', {})
        magnitude = properties.get('mag', 0)
        
        priority = 'normal'
        if magnitude >= 6.0:
            priority = 'critical'
        elif magnitude >= 4.5:
            priority = 'high'
        
        return DataUpdate(
            source='usgs_earthquakes',
            timestamp=datetime.now(),
            data_type='earthquake',
            payload={
                'magnitude': magnitude,
                'location': properties.get('place', 'Unknown'),
                'depth': data.get('geometry', {}).get('coordinates', [0, 0, 0])[2],
                'time': properties.get('time')
            },
            priority=priority
        )
    
    def _severity_to_priority(self, severity: str) -> str:
        """Convert severity level to priority."""
        mapping = {
            'Extreme': 'critical',
            'Severe': 'high',
            'Moderate': 'normal',
            'Minor': 'low'
        }
        return mapping.get(severity, 'normal')
    
    def _notify_subscribers(self, update: DataUpdate):
        """Notify all subscribers of a new update."""
        with self._lock:
            callbacks = self.subscribers.get(update.source, []).copy()
        
        for callback in callbacks:
            try:
                callback(update)
            except Exception as e:
                print(f"Subscriber error: {e}")
        
        # Add to history
        self._message_history.append(update)
        if len(self._message_history) > self._max_history:
            self._message_history.pop(0)
    
    def _run_async_connection(self, source_name: str):
        """Run async connection in a thread."""
        asyncio.run(self._async_connect(source_name))
    
    def start(self):
        """Start all WebSocket connections."""
        self.is_running = True
        
        for source_name in self.sources:
            self.connect(source_name)
    
    def stop(self):
        """Stop all WebSocket connections."""
        self.is_running = False
        
        for source_name in list(self.connections.keys()):
            self.disconnect(source_name)
        
        # Wait for threads to finish
        for thread in self._threads.values():
            if thread.is_alive():
                thread.join(timeout=2)
    
    def disconnect(self, source_name: str):
        """Disconnect from a specific source."""
        self.connection_status[source_name] = ConnectionStatus.DISCONNECTED
        
        if source_name in self.connections:
            try:
                # Close connection
                if hasattr(self.connections[source_name], 'close'):
                    asyncio.create_task(self.connections[source_name].close())
            except:
                pass
            del self.connections[source_name]
    
    def get_status(self, source_name: Optional[str] = None) -> Dict:
        """Get connection status."""
        if source_name:
            return {
                'status': self.connection_status.get(source_name, ConnectionStatus.DISCONNECTED).value,
                'connected': self.connection_status.get(source_name) == ConnectionStatus.CONNECTED
            }
        
        return {
            name: {
                'status': status.value,
                'connected': status == ConnectionStatus.CONNECTED
            }
            for name, status in self.connection_status.items()
        }
    
    def get_recent_updates(self, count: int = 10, source: Optional[str] = None) -> List[DataUpdate]:
        """Get recent updates from history."""
        updates = self._message_history
        
        if source:
            updates = [u for u in updates if u.source == source]
        
        return updates[-count:]


class StreamlitRealtimeFeed:
    """
    Streamlit component for displaying real-time WebSocket data.
    Provides visual feed with filtering and alert management.
    """
    
    PRIORITY_COLORS = {
        'critical': '#ef4444',
        'high': '#f97316',
        'normal': '#3b82f6',
        'low': '#6b7280'
    }
    
    PRIORITY_ICONS = {
        'critical': '🔴',
        'high': '🟠',
        'normal': '🔵',
        'low': '⚪'
    }
    
    def __init__(self, ws_manager: WebSocketManager):
        self.ws_manager = ws_manager
        self.received_updates: List[DataUpdate] = []
        self._subscribed = False
        
    def render(self):
        """Render the real-time feed component."""
        # Subscribe to updates on first render
        if not self._subscribed:
            for source in self.ws_manager.sources:
                self.ws_manager.subscribe(source, self._on_update)
            self._subscribed = True
        
        st.markdown("### 📡 Live Data Feed")
        
        # Connection status panel
        self._render_status_panel()
        
        # Filters
        self._render_filters()
        
        # Updates feed
        self._render_updates_feed()
        
        # Statistics
        self._render_statistics()
    
    def _render_status_panel(self):
        """Render connection status panel."""
        status = self.ws_manager.get_status()
        
        cols = st.columns(len(status))
        for col, (source, info) in zip(cols, status.items()):
            with col:
                config = self.ws_manager.sources[source]
                status_emoji = '🟢' if info['connected'] else '🔴'
                
                st.markdown(f"""
                <div style="
                    background: rgba(30, 41, 59, 0.8);
                    border-radius: 8px;
                    padding: 10px;
                    text-align: center;
                ">
                    <div style="font-size: 20px;">{status_emoji}</div>
                    <div style="font-size: 11px; color: #94a3b8;">{config.description}</div>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_filters(self):
        """Render update filters."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            self.priority_filter = st.multiselect(
                "Priority",
                ['critical', 'high', 'normal', 'low'],
                default=['critical', 'high', 'normal'],
                key="feed_priority_filter"
            )
        
        with col2:
            self.source_filter = st.multiselect(
                "Source",
                list(self.ws_manager.sources.keys()),
                default=list(self.ws_manager.sources.keys()),
                key="feed_source_filter"
            )
        
        with col3:
            self.type_filter = st.text_input(
                "Event Type",
                placeholder="Filter by type...",
                key="feed_type_filter"
            )
    
    def _render_updates_feed(self):
        """Render the updates feed."""
        st.markdown("#### Recent Events")
        
        # Get filtered updates
        filtered_updates = self._filter_updates(self.received_updates)
        
        if not filtered_updates:
            st.info("No events matching current filters")
            return
        
        # Display updates
        feed_container = st.container()
        with feed_container:
            for update in reversed(filtered_updates[-20:]):  # Show last 20
                self._render_update_card(update)
    
    def _render_update_card(self, update: DataUpdate):
        """Render a single update card."""
        color = self.PRIORITY_COLORS.get(update.priority, '#6b7280')
        icon = self.PRIORITY_ICONS.get(update.priority, '⚪')
        
        # Format timestamp
        time_str = update.timestamp.strftime('%H:%M:%S')
        
        # Create expandable card
        with st.expander(f"{icon} {update.data_type.replace('_', ' ').title()} - {time_str}"):
            st.markdown(f"""
            <div style="
                border-left: 4px solid {color};
                padding-left: 12px;
                margin: 8px 0;
            ">
                <div style="color: #94a3b8; font-size: 12px;">
                    Source: {update.source} | Priority: {update.priority.upper()}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display payload
            st.json(update.payload)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📍 View on Map", key=f"map_{update.timestamp}"):
                    st.session_state['focus_location'] = update.payload.get('location')
            with col2:
                if st.button("📊 Analyze", key=f"analyze_{update.timestamp}"):
                    st.session_state['analyze_event'] = update
            with col3:
                if st.button("🔔 Alert", key=f"alert_{update.timestamp}"):
                    st.toast("Alert configured for similar events")
    
    def _render_statistics(self):
        """Render feed statistics."""
        col1, col2, col3, col4 = st.columns(4)
        
        updates = self.received_updates
        
        with col1:
            st.metric("Total Events", len(updates))
        with col2:
            critical = len([u for u in updates if u.priority == 'critical'])
            st.metric("Critical", critical, delta=None)
        with col3:
            last_minute = len([
                u for u in updates 
                if (datetime.now() - u.timestamp).seconds < 60
            ])
            st.metric("Last Minute", last_minute)
        with col4:
            sources = len(set(u.source for u in updates))
            st.metric("Active Sources", sources)
    
    def _filter_updates(self, updates: List[DataUpdate]) -> List[DataUpdate]:
        """Apply filters to updates."""
        filtered = updates
        
        # Priority filter
        if hasattr(self, 'priority_filter') and self.priority_filter:
            filtered = [u for u in filtered if u.priority in self.priority_filter]
        
        # Source filter
        if hasattr(self, 'source_filter') and self.source_filter:
            filtered = [u for u in filtered if u.source in self.source_filter]
        
        # Type filter
        if hasattr(self, 'type_filter') and self.type_filter:
            type_lower = self.type_filter.lower()
            filtered = [
                u for u in filtered 
                if type_lower in u.data_type.lower()
            ]
        
        return filtered
    
    def _on_update(self, update: DataUpdate):
        """Handle incoming update."""
        self.received_updates.append(update)
        
        # Keep only recent updates
        if len(self.received_updates) > 100:
            self.received_updates = self.received_updates[-100:]
        
        # Trigger notification for critical updates
        if update.priority == 'critical':
            st.session_state['critical_alert'] = update


# Convenience functions for dashboard integration
def initialize_websocket_manager() -> WebSocketManager:
    """Initialize and return a WebSocket manager."""
    if 'ws_manager' not in st.session_state:
        st.session_state.ws_manager = WebSocketManager()
    return st.session_state.ws_manager


def render_realtime_feed(ws_manager: Optional[WebSocketManager] = None):
    """Render the real-time feed with minimal setup."""
    if ws_manager is None:
        ws_manager = initialize_websocket_manager()
    
    feed = StreamlitRealtimeFeed(ws_manager)
    feed.render()
