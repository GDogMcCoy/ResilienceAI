"""
Offline-First Implementation for ResilienceAI
=============================================
Ensures critical functionality during network outages.
"""

from typing import Optional, Any, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import sqlite3
import json
import hashlib
import asyncio
from enum import Enum


class OperationType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SYNC = "sync"


@dataclass
class OfflineOperation:
    """Represents an operation to be synced when online"""
    id: str
    operation_type: OperationType
    entity_type: str
    entity_id: str
    data: Dict[str, Any]
    timestamp: datetime
    retry_count: int = 0
    priority: int = 5  # 1 = highest, 10 = lowest
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "operation_type": self.operation_type.value,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "retry_count": self.retry_count,
            "priority": self.priority
        }


class OfflineFirstManager:
    """Manages offline-first operations for ResilienceAI"""
    
    def __init__(self, db_path: str = "/data/offline_ops.db"):
        self.db_path = db_path
        self._init_database()
        self.sync_handlers: Dict[str, callable] = {}
        
    def _init_database(self):
        """Initialize SQLite database for offline storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                id TEXT PRIMARY KEY,
                operation_type TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                retry_count INTEGER DEFAULT 0,
                priority INTEGER DEFAULT 5,
                synced BOOLEAN DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS local_cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                last_modified TEXT NOT NULL,
                ttl_seconds INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_id TEXT,
                sync_time TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                server_response TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
    def queue_operation(self, operation: OfflineOperation) -> bool:
        """Queue an operation for later sync"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO operations 
            (id, operation_type, entity_type, entity_id, data, timestamp, retry_count, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            operation.id,
            operation.operation_type.value,
            operation.entity_type,
            operation.entity_id,
            json.dumps(operation.data),
            operation.timestamp.isoformat(),
            operation.retry_count,
            operation.priority
        ))
        
        conn.commit()
        conn.close()
        return True
        
    def get_pending_operations(self, entity_type: Optional[str] = None) -> List[OfflineOperation]:
        """Get all pending operations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if entity_type:
            cursor.execute("""
                SELECT * FROM operations 
                WHERE synced = 0 AND entity_type = ?
                ORDER BY priority ASC, timestamp ASC
            """, (entity_type,))
        else:
            cursor.execute("""
                SELECT * FROM operations 
                WHERE synced = 0
                ORDER BY priority ASC, timestamp ASC
            """)
            
        rows = cursor.fetchall()
        conn.close()
        
        operations = []
        for row in rows:
            operations.append(OfflineOperation(
                id=row[0],
                operation_type=OperationType(row[1]),
                entity_type=row[2],
                entity_id=row[3],
                data=json.loads(row[4]),
                timestamp=datetime.fromisoformat(row[5]),
                retry_count=row[6],
                priority=row[7]
            ))
        return operations
        
    def cache_locally(self, key: str, value: Any, entity_type: str, ttl_seconds: Optional[int] = None):
        """Cache data locally with optional TTL"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO local_cache 
            (key, value, entity_type, last_modified, ttl_seconds)
            VALUES (?, ?, ?, ?, ?)
        """, (
            key,
            json.dumps(value),
            entity_type,
            datetime.utcnow().isoformat(),
            ttl_seconds
        ))
        
        conn.commit()
        conn.close()
        
    def get_cached(self, key: str) -> Optional[Any]:
        """Retrieve cached data if not expired"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT value, last_modified, ttl_seconds FROM local_cache WHERE key = ?
        """, (key,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        value, last_modified, ttl_seconds = row
        last_modified = datetime.fromisoformat(last_modified)
        
        if ttl_seconds:
            if datetime.utcnow() - last_modified > timedelta(seconds=ttl_seconds):
                return None
                
        return json.loads(value)
        
    async def sync_operations(self, is_online: bool) -> Dict[str, Any]:
        """Attempt to sync pending operations"""
        if not is_online:
            return {"status": "offline", "synced": 0}
            
        operations = self.get_pending_operations()
        results = {"synced": 0, "failed": 0, "errors": []}
        
        for op in operations:
            try:
                success = await self._sync_single_operation(op)
                if success:
                    results["synced"] += 1
                    self._mark_synced(op.id)
                else:
                    results["failed"] += 1
                    self._increment_retry(op.id)
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(str(e))
                self._increment_retry(op.id)
                
        return results
        
    async def _sync_single_operation(self, operation: OfflineOperation) -> bool:
        """Sync a single operation to the server"""
        handler = self.sync_handlers.get(operation.entity_type)
        if not handler:
            return False
        return await handler(operation)
        
    def _mark_synced(self, operation_id: str):
        """Mark operation as successfully synced"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE operations SET synced = 1 WHERE id = ?", (operation_id,))
        conn.commit()
        conn.close()
        
    def _increment_retry(self, operation_id: str):
        """Increment retry count for failed operation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE operations SET retry_count = retry_count + 1 WHERE id = ?",
            (operation_id,)
        )
        conn.commit()
        conn.close()
        
    def register_sync_handler(self, entity_type: str, handler: callable):
        """Register a sync handler for an entity type"""
        self.sync_handlers[entity_type] = handler
        
    def get_offline_stats(self) -> Dict[str, Any]:
        """Get statistics about offline operations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM operations WHERE synced = 0")
        pending = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT operation_type, COUNT(*) FROM operations WHERE synced = 0 GROUP BY operation_type
        """)
        by_type = dict(cursor.fetchall())
        
        cursor.execute("SELECT COUNT(*) FROM local_cache")
        cache_size = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM operations WHERE retry_count > 3")
        failed = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "pending_operations": pending,
            "by_operation_type": by_type,
            "cache_entries": cache_size,
            "failed_operations": failed,
            "last_check": datetime.utcnow().isoformat()
        }
