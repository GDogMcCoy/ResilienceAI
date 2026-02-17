"""
Real-Time Weather Feed Integration
Manages connections to multiple weather data sources
"""
import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from abc import ABC, abstractmethod

from enhanced_noaa_client import WeatherAlert
from alert_processor import AlertProcessor, CAPAlertParser

logger = logging.getLogger(__name__)


class FeedStatus(Enum):
    """Feed connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


@dataclass
class FeedMetrics:
    """Metrics for a feed connection"""
    messages_received: int = 0
    messages_processed: int = 0
    messages_failed: int = 0
    bytes_received: int = 0
    last_message_at: Optional[datetime] = None
    connection_started_at: Optional[datetime] = None
    reconnections: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class WeatherFeed(ABC):
    """Abstract base class for weather data feeds"""
    
    def __init__(
        self,
        name: str,
        url: str,
        poll_interval: int = 60,
        reconnect_interval: int = 30,
        max_reconnects: int = 10
    ):
        self.name = name
        self.url = url
        self.poll_interval = poll_interval
        self.reconnect_interval = reconnect_interval
        self.max_reconnects = max_reconnects
        
        self.status = FeedStatus.DISCONNECTED
        self.metrics = FeedMetrics()
        self._message_handlers: List[Callable] = []
        self._is_running = False
        self._reconnect_count = 0
    
    def add_message_handler(self, handler: Callable):
        self._message_handlers.append(handler)
    
    def remove_message_handler(self, handler: Callable):
        self._message_handlers = [h for h in self._message_handlers if h != handler]
    
    async def _notify_handlers(self, message: Any):
        for handler in self._message_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                logger.error(f"Handler error in {self.name}: {e}")
    
    @abstractmethod
    async def connect(self):
        pass
    
    @abstractmethod
    async def disconnect(self):
        pass
    
    @abstractmethod
    async def run(self):
        pass


class NOAACAPFeed(WeatherFeed):
    """NOAA CAP/XML alert feed via HTTP polling"""
    
    def __init__(
        self,
        alert_processor: Optional[AlertProcessor] = None,
        **kwargs
    ):
        super().__init__(
            name="NOAA_CAP_Feed",
            url="https://api.weather.gov/alerts/active.atom",
            **kwargs
        )
        self.alert_processor = alert_processor
        self._session: Optional[aiohttp.ClientSession] = None
        self._last_etag: Optional[str] = None
        self._last_modified: Optional[str] = None
    
    async def connect(self):
        self._session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'ResilienceAI/2.0 (realtime-feed)',
                'Accept': 'application/atom+xml'
            }
        )
        self.status = FeedStatus.CONNECTED
        self.metrics.connection_started_at = datetime.utcnow()
        logger.info(f"{self.name} session initialized")
    
    async def disconnect(self):
        self._is_running = False
        if self._session:
            await self._session.close()
            self._session = None
        self.status = FeedStatus.DISCONNECTED
        logger.info(f"{self.name} session closed")
    
    async def run(self):
        self._is_running = True
        await self.connect()
        
        while self._is_running:
            try:
                await self._poll_feed()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in {self.name}: {e}")
                self.status = FeedStatus.ERROR
                self.metrics.errors.append(str(e))
                await asyncio.sleep(self.reconnect_interval)
    
    async def _poll_feed(self):
        if not self._session:
            return
        
        headers = {}
        if self._last_etag:
            headers['If-None-Match'] = self._last_etag
        if self._last_modified:
            headers['If-Modified-Since'] = self._last_modified
        
        try:
            async with self._session.get(
                self.url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 304:
                    return
                
                response.raise_for_status()
                self._last_etag = response.headers.get('ETag')
                self._last_modified = response.headers.get('Last-Modified')
                
                content = await response.text()
                self.metrics.bytes_received += len(content.encode())
                await self._parse_atom_feed(content)
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error polling {self.name}: {e}")
    
    async def _parse_atom_feed(self, content: str):
        import xml.etree.ElementTree as ET
        
        try:
            root = ET.fromstring(content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                cap_content = entry.find('atom:content', ns)
                if cap_content is not None:
                    cap_xml = ET.tostring(cap_content[0], encoding='unicode')
                    parsed = CAPAlertParser.parse_cap_xml(cap_xml)
                    
                    if parsed:
                        self.metrics.messages_received += 1
                        if self.alert_processor:
                            await self.alert_processor.ingest_cap_xml(cap_xml)
                        await self._notify_handlers(parsed)
                        self.metrics.messages_processed += 1
                        
        except ET.ParseError as e:
            logger.error(f"Failed to parse ATOM feed: {e}")
            self.metrics.messages_failed += 1


class USGSWaterServicesFeed(WeatherFeed):
    """USGS Water Services feed for streamflow and flood data"""
    
    def __init__(
        self,
        site_ids: Optional[List[str]] = None,
        parameter_code: str = "00060",
        **kwargs
    ):
        super().__init__(
            name="USGS_Water_Services",
            url="https://waterservices.usgs.gov/nwis/iv",
            **kwargs
        )
        self.site_ids = site_ids or []
        self.parameter_code = parameter_code
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def connect(self):
        self._session = aiohttp.ClientSession()
        self.status = FeedStatus.CONNECTED
        self.metrics.connection_started_at = datetime.utcnow()
        logger.info(f"{self.name} session initialized")
    
    async def disconnect(self):
        self._is_running = False
        if self._session:
            await self._session.close()
            self._session = None
        self.status = FeedStatus.DISCONNECTED
    
    async def run(self):
        self._is_running = True
        await self.connect()
        
        while self._is_running:
            try:
                await self._fetch_data()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in {self.name}: {e}")
                await asyncio.sleep(self.reconnect_interval)
    
    async def _fetch_data(self):
        if not self._session or not self.site_ids:
            return
        
        params = {
            'format': 'json',
            'sites': ','.join(self.site_ids),
            'parameterCd': self.parameter_code,
            'siteStatus': 'active'
        }
        
        try:
            async with self._session.get(
                self.url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                self.metrics.messages_received += 1
                self.metrics.last_message_at = datetime.utcnow()
                await self._notify_handlers(data)
                self.metrics.messages_processed += 1
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error fetching {self.name}: {e}")


class RealtimeFeedManager:
    """Manages multiple real-time weather feeds"""
    
    def __init__(self):
        self.feeds: Dict[str, WeatherFeed] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
    
    def add_feed(self, feed: WeatherFeed) -> str:
        feed_id = f"{feed.name}_{id(feed)}"
        self.feeds[feed_id] = feed
        return feed_id
    
    def remove_feed(self, feed_id: str):
        if feed_id in self.feeds:
            feed = self.feeds.pop(feed_id)
            if feed_id in self._tasks:
                self._tasks[feed_id].cancel()
                del self._tasks[feed_id]
    
    async def start_feed(self, feed_id: str):
        if feed_id not in self.feeds:
            raise ValueError(f"Feed {feed_id} not found")
        
        feed = self.feeds[feed_id]
        task = asyncio.create_task(feed.run())
        self._tasks[feed_id] = task
        logger.info(f"Started feed {feed_id}")
    
    async def stop_feed(self, feed_id: str):
        if feed_id in self.feeds:
            await self.feeds[feed_id].disconnect()
        if feed_id in self._tasks:
            self._tasks[feed_id].cancel()
            del self._tasks[feed_id]
    
    async def start_all(self):
        for feed_id in self.feeds:
            await self.start_feed(feed_id)
    
    async def stop_all(self):
        for feed_id in list(self.feeds.keys()):
            await self.stop_feed(feed_id)
    
    def get_feed_status(self, feed_id: str) -> Optional[Dict]:
        if feed_id not in self.feeds:
            return None
        
        feed = self.feeds[feed_id]
        return {
            'id': feed_id,
            'name': feed.name,
            'status': feed.status.value,
            'metrics': {
                'messages_received': feed.metrics.messages_received,
                'messages_processed': feed.metrics.messages_processed,
                'messages_failed': feed.metrics.messages_failed,
                'bytes_received': feed.metrics.bytes_received,
                'last_message_at': feed.metrics.last_message_at.isoformat() if feed.metrics.last_message_at else None,
                'reconnections': feed.metrics.reconnections,
                'errors': feed.metrics.errors[-5:]
            }
        }
    
    def get_all_status(self) -> Dict[str, Dict]:
        return {feed_id: self.get_feed_status(feed_id) for feed_id in self.feeds}
