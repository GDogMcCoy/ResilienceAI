"""
Data Synchronization Strategies for ResilienceAI
================================================
Handles data sync between edge and cloud with conflict resolution.
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib
import json
import gzip


class ConflictStrategy(Enum):
    """Conflict resolution strategies"""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    SERVER_WINS = "server_wins"
    CLIENT_WINS = "client_wins"
    MERGE = "merge"
    MANUAL = "manual"


class SyncPriority(Enum):
    """Sync priority levels"""
    CRITICAL = 1      # Emergency alerts, life-safety data
    HIGH = 2          # Resource allocation, damage assessments
    MEDIUM = 3        # Status updates, metrics
    LOW = 4           # Analytics, logs
    BATCH = 5         # Historical data, reports


@dataclass
class SyncItem:
    """Item to be synchronized"""
    id: str
    entity_type: str
    data: Dict[str, Any]
    local_version: int
    server_version: Optional[int]
    local_timestamp: datetime
    server_timestamp: Optional[datetime]
    checksum: str
    priority: SyncPriority


@dataclass
class Conflict:
    """Represents a sync conflict"""
    item_id: str
    local_data: Dict[str, Any]
    server_data: Dict[str, Any]
    local_timestamp: datetime
    server_timestamp: datetime
    resolution: Optional[str] = None


class DeltaSyncEngine:
    """Efficient delta synchronization engine"""
    
    def __init__(self, conflict_strategy: ConflictStrategy = ConflictStrategy.LAST_WRITE_WINS):
        self.conflict_strategy = conflict_strategy
        self.conflict_handlers: Dict[str, Callable] = {}
        
    def calculate_delta(self, local_data: Dict, server_data: Dict) -> Dict:
        """Calculate differences between local and server data"""
        delta = {
            "added": {},
            "modified": {},
            "deleted": [],
            "unchanged": []
        }
        
        local_keys = set(local_data.keys())
        server_keys = set(server_data.keys())
        
        for key in local_keys - server_keys:
            delta["added"][key] = local_data[key]
            
        for key in server_keys - local_keys:
            delta["deleted"].append(key)
            
        for key in local_keys & server_keys:
            local_hash = self._hash_data(local_data[key])
            server_hash = self._hash_data(server_data[key])
            
            if local_hash != server_hash:
                delta["modified"][key] = {
                    "local": local_data[key],
                    "server": server_data[key]
                }
            else:
                delta["unchanged"].append(key)
                
        return delta
        
    def _hash_data(self, data: Any) -> str:
        """Generate hash for data comparison"""
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
        
    def resolve_conflict(self, conflict: Conflict) -> Dict[str, Any]:
        """Resolve sync conflict based on strategy"""
        if self.conflict_strategy == ConflictStrategy.LAST_WRITE_WINS:
            if conflict.local_timestamp > conflict.server_timestamp:
                return conflict.local_data
            else:
                return conflict.server_data
        elif self.conflict_strategy == ConflictStrategy.SERVER_WINS:
            return conflict.server_data
        elif self.conflict_strategy == ConflictStrategy.CLIENT_WINS:
            return conflict.local_data
        elif self.conflict_strategy == ConflictStrategy.MERGE:
            return self._merge_data(conflict.local_data, conflict.server_data)
        elif self.conflict_strategy == ConflictStrategy.MANUAL:
            return conflict.local_data
            
    def _merge_data(self, local: Dict, server: Dict) -> Dict:
        """Intelligently merge conflicting data"""
        merged = server.copy()
        
        for key, value in local.items():
            if key not in server:
                merged[key] = value
            elif isinstance(value, dict) and isinstance(server[key], dict):
                merged[key] = self._merge_data(value, server[key])
            elif value != server[key]:
                if key in ["status", "priority", "notes"]:
                    merged[key] = value
                    
        return merged


class BatchedSyncManager:
    """Manages batched synchronization for bandwidth optimization"""
    
    def __init__(
        self,
        batch_size: int = 100,
        compression_enabled: bool = True,
        max_batch_interval_seconds: int = 300
    ):
        self.batch_size = batch_size
        self.compression_enabled = compression_enabled
        self.max_batch_interval = max_batch_interval_seconds
        self.pending_batches: Dict[SyncPriority, List[SyncItem]] = {
            priority: [] for priority in SyncPriority
        }
        
    def add_to_batch(self, item: SyncItem):
        """Add item to appropriate priority batch"""
        self.pending_batches[item.priority].append(item)
        
        if len(self.pending_batches[item.priority]) >= self.batch_size:
            return self._flush_batch(item.priority)
            
    def _flush_batch(self, priority: SyncPriority) -> Dict:
        """Flush a priority batch for sync"""
        batch = self.pending_batches[priority]
        self.pending_batches[priority] = []
        batch.sort(key=lambda x: x.local_timestamp)
        
        if self.compression_enabled:
            batch_data = self._compress_batch(batch)
        else:
            batch_data = [self._serialize_item(item) for item in batch]
            
        return {
            "priority": priority.value,
            "item_count": len(batch),
            "data": batch_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def _serialize_item(self, item: SyncItem) -> Dict:
        """Serialize sync item for transmission"""
        return {
            "id": item.id,
            "entity_type": item.entity_type,
            "data": item.data,
            "version": item.local_version,
            "timestamp": item.local_timestamp.isoformat(),
            "checksum": item.checksum
        }
        
    def _compress_batch(self, batch: List[SyncItem]) -> bytes:
        """Compress batch data for efficient transmission"""
        data = json.dumps([self._serialize_item(item) for item in batch])
        return gzip.compress(data.encode())
        
    def get_all_pending_batches(self) -> List[Dict]:
        """Get all pending batches ordered by priority"""
        batches = []
        for priority in SyncPriority:
            if self.pending_batches[priority]:
                batches.append(self._flush_batch(priority))
        return batches


class AdaptiveSyncScheduler:
    """Adaptive sync scheduling based on network conditions"""
    
    def __init__(self):
        self.network_quality = 1.0
        self.bandwidth_mbps = 10.0
        self.latency_ms = 100
        
    def update_network_metrics(self, bandwidth: float, latency: float, packet_loss: float):
        """Update network quality metrics"""
        self.bandwidth_mbps = bandwidth
        self.latency_ms = latency
        
        bw_score = min(bandwidth / 10.0, 1.0)
        latency_score = max(0, 1.0 - (latency / 1000))
        loss_score = max(0, 1.0 - (packet_loss * 10))
        
        self.network_quality = (bw_score + latency_score + loss_score) / 3
        
    def get_sync_parameters(self) -> Dict:
        """Get optimal sync parameters based on network conditions"""
        if self.network_quality > 0.8:
            return {
                "batch_size": 500,
                "sync_interval_seconds": 30,
                "compression": False,
                "parallel_uploads": 5
            }
        elif self.network_quality > 0.5:
            return {
                "batch_size": 200,
                "sync_interval_seconds": 60,
                "compression": True,
                "parallel_uploads": 3
            }
        elif self.network_quality > 0.3:
            return {
                "batch_size": 50,
                "sync_interval_seconds": 180,
                "compression": True,
                "parallel_uploads": 1
            }
        else:
            return {
                "batch_size": 10,
                "sync_interval_seconds": 600,
                "compression": True,
                "parallel_uploads": 1,
                "critical_only": True
            }
