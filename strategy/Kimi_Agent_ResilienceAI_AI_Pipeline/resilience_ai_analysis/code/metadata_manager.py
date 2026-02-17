# /mnt/okcomputer/output/resilience_ai_analysis/code/metadata_manager.py
"""
Metadata Manager for ResilienceAI
Manages metadata for archived data objects.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import hashlib


class MetadataType(Enum):
    """Metadata type enumeration."""
    SYSTEM = "system"
    BUSINESS = "business"
    TECHNICAL = "technical"


@dataclass
class ArchiveMetadata:
    """Complete metadata for archived data."""
    
    # System metadata
    object_id: str
    object_key: str
    bucket: str
    size_bytes: int
    created_at: datetime
    modified_at: datetime
    storage_tier: str
    checksum_sha256: str
    encryption_enabled: bool
    encryption_key_id: Optional[str]
    
    # Business metadata
    data_category: str
    retention_policy: str
    compliance_standards: List[str]
    legal_hold: bool
    owner: str
    department: str
    project: str
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Technical metadata
    content_type: str
    compression_algorithm: Optional[str]
    compression_ratio: Optional[float]
    schema_version: Optional[str]
    related_objects: List[str] = field(default_factory=list)
    lineage: Dict[str, Any] = field(default_factory=dict)
    
    # Access tracking
    access_count: int = 0
    last_accessed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert metadata to dictionary."""
        return {
            "system": {
                "object_id": self.object_id,
                "object_key": self.object_key,
                "bucket": self.bucket,
                "size_bytes": self.size_bytes,
                "created_at": self.created_at.isoformat(),
                "modified_at": self.modified_at.isoformat(),
                "storage_tier": self.storage_tier,
                "checksum_sha256": self.checksum_sha256,
                "encryption_enabled": self.encryption_enabled,
                "encryption_key_id": self.encryption_key_id
            },
            "business": {
                "data_category": self.data_category,
                "retention_policy": self.retention_policy,
                "compliance_standards": self.compliance_standards,
                "legal_hold": self.legal_hold,
                "owner": self.owner,
                "department": self.department,
                "project": self.project,
                "tags": self.tags
            },
            "technical": {
                "content_type": self.content_type,
                "compression_algorithm": self.compression_algorithm,
                "compression_ratio": self.compression_ratio,
                "schema_version": self.schema_version,
                "related_objects": self.related_objects,
                "lineage": self.lineage
            },
            "access": {
                "access_count": self.access_count,
                "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ArchiveMetadata':
        """Create metadata from dictionary."""
        system = data.get("system", {})
        business = data.get("business", {})
        technical = data.get("technical", {})
        access = data.get("access", {})
        
        return cls(
            object_id=system.get("object_id"),
            object_key=system.get("object_key"),
            bucket=system.get("bucket"),
            size_bytes=system.get("size_bytes"),
            created_at=datetime.fromisoformat(system.get("created_at")),
            modified_at=datetime.fromisoformat(system.get("modified_at")),
            storage_tier=system.get("storage_tier"),
            checksum_sha256=system.get("checksum_sha256"),
            encryption_enabled=system.get("encryption_enabled"),
            encryption_key_id=system.get("encryption_key_id"),
            data_category=business.get("data_category"),
            retention_policy=business.get("retention_policy"),
            compliance_standards=business.get("compliance_standards", []),
            legal_hold=business.get("legal_hold", False),
            owner=business.get("owner"),
            department=business.get("department"),
            project=business.get("project"),
            tags=business.get("tags", {}),
            content_type=technical.get("content_type"),
            compression_algorithm=technical.get("compression_algorithm"),
            compression_ratio=technical.get("compression_ratio"),
            schema_version=technical.get("schema_version"),
            related_objects=technical.get("related_objects", []),
            lineage=technical.get("lineage", {}),
            access_count=access.get("access_count", 0),
            last_accessed_at=datetime.fromisoformat(access.get("last_accessed_at")) if access.get("last_accessed_at") else None
        )


class MetadataManager:
    """Manager for archive metadata operations."""
    
    def __init__(self, db_connection=None, es_client=None, redis_client=None):
        self.db = db_connection
        self.es = es_client
        self.redis = redis_client
    
    def create_metadata(self, object_id: str, object_key: str, bucket: str,
                       size_bytes: int, data_category: str, owner: str,
                       **kwargs) -> ArchiveMetadata:
        """Create new metadata record for archived object."""
        metadata = ArchiveMetadata(
            object_id=object_id,
            object_key=object_key,
            bucket=bucket,
            size_bytes=size_bytes,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            storage_tier=kwargs.get("storage_tier", "STANDARD"),
            checksum_sha256=kwargs.get("checksum_sha256", ""),
            encryption_enabled=kwargs.get("encryption_enabled", True),
            encryption_key_id=kwargs.get("encryption_key_id"),
            data_category=data_category,
            retention_policy=kwargs.get("retention_policy", "default"),
            compliance_standards=kwargs.get("compliance_standards", []),
            legal_hold=kwargs.get("legal_hold", False),
            owner=owner,
            department=kwargs.get("department", ""),
            project=kwargs.get("project", ""),
            tags=kwargs.get("tags", {}),
            content_type=kwargs.get("content_type", "application/octet-stream"),
            compression_algorithm=kwargs.get("compression_algorithm"),
            compression_ratio=kwargs.get("compression_ratio"),
            schema_version=kwargs.get("schema_version"),
            related_objects=kwargs.get("related_objects", []),
            lineage=kwargs.get("lineage", {})
        )
        
        # Store metadata
        self._store_metadata(metadata)
        
        return metadata
    
    def _store_metadata(self, metadata: ArchiveMetadata):
        """Store metadata in all backends."""
        metadata_dict = metadata.to_dict()
        
        # Store in PostgreSQL (primary)
        if self.db:
            self._store_in_postgres(metadata)
        
        # Index in Elasticsearch
        if self.es:
            self._index_in_elasticsearch(metadata)
        
        # Cache in Redis
        if self.redis:
            self._cache_in_redis(metadata)
    
    def _store_in_postgres(self, metadata: ArchiveMetadata):
        """Store metadata in PostgreSQL."""
        # Implementation would use SQLAlchemy or similar
        pass
    
    def _index_in_elasticsearch(self, metadata: ArchiveMetadata):
        """Index metadata in Elasticsearch."""
        # Implementation would use elasticsearch-py
        pass
    
    def _cache_in_redis(self, metadata: ArchiveMetadata):
        """Cache metadata in Redis."""
        # Implementation would use redis-py
        pass
    
    def get_metadata(self, object_id: str) -> Optional[ArchiveMetadata]:
        """Retrieve metadata for an object."""
        # Try cache first
        if self.redis:
            cached = self._get_from_redis(object_id)
            if cached:
                return cached
        
        # Try database
        if self.db:
            metadata = self._get_from_postgres(object_id)
            if metadata:
                # Cache for future
                if self.redis:
                    self._cache_in_redis(metadata)
                return metadata
        
        return None
    
    def update_metadata(self, object_id: str, updates: Dict) -> Optional[ArchiveMetadata]:
        """Update metadata for an object."""
        metadata = self.get_metadata(object_id)
        if not metadata:
            return None
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)
        
        metadata.modified_at = datetime.now()
        
        # Store updated metadata
        self._store_metadata(metadata)
        
        return metadata
    
    def record_access(self, object_id: str):
        """Record access to an archived object."""
        metadata = self.get_metadata(object_id)
        if metadata:
            metadata.access_count += 1
            metadata.last_accessed_at = datetime.now()
            self._store_metadata(metadata)
    
    def search_metadata(self, query: Dict) -> List[ArchiveMetadata]:
        """Search metadata using Elasticsearch."""
        if not self.es:
            return []
        
        # Build Elasticsearch query
        es_query = {"bool": {"must": []}}
        
        for field, value in query.items():
            es_query["bool"]["must"].append({
                "match": {field: value}
            })
        
        # Execute search
        response = self.es.search(index="archive_metadata", body={
            "query": es_query
        })
        
        # Parse results
        results = []
        for hit in response["hits"]["hits"]:
            results.append(ArchiveMetadata.from_dict(hit["_source"]))
        
        return results
    
    def generate_metadata_report(self, filters: Dict) -> Dict:
        """Generate metadata statistics report."""
        # Implementation would aggregate from database
        return {
            "total_objects": 0,
            "total_size_bytes": 0,
            "by_category": {},
            "by_tier": {},
            "by_department": {},
            "generated_at": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Example usage
    manager = MetadataManager()
    
    # Create metadata
    metadata = manager.create_metadata(
        object_id="INC-2024-001",
        object_key="archive/incidents/INC-2024-001",
        bucket="resilienceai-archive",
        size_bytes=1024 * 1024 * 10,  # 10MB
        data_category="incident_data",
        owner="security-team@resilienceai.com",
        department="Security",
        project="Incident Management",
        compliance_standards=["SOX", "ISO27001"],
        compression_algorithm="zstd",
        compression_ratio=3.5,
        tags={"severity": "high", "status": "resolved"}
    )
    
    print("Created metadata:")
    print(json.dumps(metadata.to_dict(), indent=2))
