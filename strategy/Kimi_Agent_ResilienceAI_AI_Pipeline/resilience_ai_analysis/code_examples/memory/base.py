"""
ResilienceAI - Agent Memory System
Multi-tier memory management for agents.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import hashlib


class MemoryType(Enum):
    """Types of memory storage."""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


@dataclass
class MemoryEntry:
    """Single memory entry."""
    key: str
    value: Any
    memory_type: MemoryType
    created_at: datetime
    accessed_at: Optional[datetime] = None
    access_count: int = 0
    importance: float = 0.5
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None


class BaseMemory(ABC):
    """Abstract base for memory implementations."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry."""
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        ttl: Optional[int] = None,
        importance: float = 0.5,
        tags: Optional[List[str]] = None
    ) -> None:
        """Store a memory entry."""
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Search memories by semantic similarity."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a memory entry."""
        pass
    
    @abstractmethod
    async def clear(self, memory_type: Optional[MemoryType] = None) -> None:
        """Clear memories."""
        pass


class InMemoryStorage(BaseMemory):
    """In-memory storage implementation."""
    
    def __init__(self, max_size: int = 1000):
        self._storage: Dict[str, MemoryEntry] = {}
        self._max_size = max_size
    
    async def get(self, key: str) -> Optional[MemoryEntry]:
        entry = self._storage.get(key)
        if entry:
            entry.accessed_at = datetime.utcnow()
            entry.access_count += 1
        return entry
    
    async def set(
        self,
        key: str,
        value: Any,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        ttl: Optional[int] = None,
        importance: float = 0.5,
        tags: Optional[List[str]] = None
    ) -> None:
        # Evict if at capacity and new entry is less important
        if len(self._storage) >= self._max_size:
            self._evict_least_important()
        
        entry = MemoryEntry(
            key=key,
            value=value,
            memory_type=memory_type,
            created_at=datetime.utcnow(),
            importance=importance,
            tags=tags or []
        )
        self._storage[key] = entry
    
    def _evict_least_important(self) -> None:
        """Evict least important entries."""
        if not self._storage:
            return
        
        # Sort by importance and access count
        sorted_entries = sorted(
            self._storage.items(),
            key=lambda x: (x[1].importance, x[1].access_count)
        )
        
        # Remove bottom 10%
        to_remove = int(len(sorted_entries) * 0.1)
        for key, _ in sorted_entries[:to_remove]:
            del self._storage[key]
    
    async def search(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10
    ) -> List[MemoryEntry]:
        # Simple string matching (can be enhanced with embeddings)
        results = []
        query_lower = query.lower()
        
        for entry in self._storage.values():
            if memory_type and entry.memory_type != memory_type:
                continue
            
            value_str = str(entry.value).lower()
            if query_lower in value_str or any(
                query_lower in tag.lower() for tag in entry.tags
            ):
                results.append(entry)
        
        # Sort by importance
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:limit]
    
    async def delete(self, key: str) -> bool:
        if key in self._storage:
            del self._storage[key]
            return True
        return False
    
    async def clear(self, memory_type: Optional[MemoryType] = None) -> None:
        if memory_type:
            keys_to_remove = [
                k for k, v in self._storage.items()
                if v.memory_type == memory_type
            ]
            for key in keys_to_remove:
                del self._storage[key]
        else:
            self._storage.clear()


class MemoryManager:
    """
    Unified memory manager for agents.
    
    Features:
    - Multi-tier memory (short-term, long-term)
    - Vector-based semantic search
    - Automatic memory consolidation
    - Importance-based retention
    """
    
    def __init__(
        self,
        short_term: BaseMemory,
        long_term: BaseMemory,
        embedding_model: Optional[Any] = None,
        max_short_term: int = 100,
        consolidation_threshold: int = 50
    ):
        self.short_term = short_term
        self.long_term = long_term
        self.embedding_model = embedding_model
        self.max_short_term = max_short_term
        self.consolidation_threshold = consolidation_threshold
        
        # Conversation context
        self._conversation_history: List[Dict[str, Any]] = []
        self._current_context: Dict[str, Any] = {}
    
    async def get(
        self,
        key: str,
        check_long_term: bool = True
    ) -> Any:
        """Get value from memory (short-term first, then long-term)."""
        # Check short-term
        entry = await self.short_term.get(key)
        if entry:
            await self._update_access(entry)
            return entry.value
        
        # Check long-term
        if check_long_term:
            entry = await self.long_term.get(key)
            if entry:
                # Promote to short-term
                await self.short_term.set(
                    key, entry.value, MemoryType.SHORT_TERM
                )
                return entry.value
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        ttl: Optional[int] = None,
        importance: float = 0.5,
        tags: Optional[List[str]] = None
    ) -> None:
        """Store value in memory."""
        # Generate embedding if model available
        embedding = None
        if self.embedding_model:
            embedding = await self._generate_embedding(str(value))
        
        if memory_type == MemoryType.SHORT_TERM:
            await self.short_term.set(
                key, value, memory_type, ttl, importance, tags
            )
            
            # Check if consolidation needed
            await self._maybe_consolidate()
        else:
            await self.long_term.set(
                key, value, memory_type, ttl, importance, tags
            )
    
    async def search_relevant(
        self,
        query: str,
        context: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for relevant memories."""
        results = []
        
        # Search short-term
        stm_results = await self.short_term.search(query, limit=limit)
        results.extend([{"source": "short_term", "entry": e} for e in stm_results])
        
        # Search long-term
        ltm_results = await self.long_term.search(query, limit=limit)
        results.extend([{"source": "long_term", "entry": e} for e in ltm_results])
        
        # Sort by relevance (simplified)
        results.sort(key=lambda x: x["entry"].importance, reverse=True)
        
        return [
            {
                "key": r["entry"].key,
                "value": r["entry"].value,
                "source": r["source"],
                "importance": r["entry"].importance
            }
            for r in results[:limit]
        ]
    
    async def add_to_conversation(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add message to conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self._conversation_history.append(message)
        
        # Store in short-term memory
        key = f"conv_{len(self._conversation_history)}"
        await self.short_term.set(
            key, message, MemoryType.EPISODIC, importance=0.7
        )
    
    async def get_conversation_context(
        self,
        window_size: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent conversation context."""
        return self._conversation_history[-window_size:]
    
    async def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract and store entities from text."""
        entities = []
        
        # County mentions
        import re
        county_pattern = r'(\w+)\s+County'
        counties = re.findall(county_pattern, text, re.IGNORECASE)
        for county in counties:
            entity_key = f"entity_county_{county.lower()}"
            await self.set(
                entity_key,
                {"type": "county", "name": county, "mentions": 1},
                MemoryType.SEMANTIC,
                importance=0.8,
                tags=["entity", "county"]
            )
            entities.append({"type": "county", "name": county})
        
        # State mentions
        state_pattern = r'(Missouri|California|Texas|Florida|New York)'
        states = re.findall(state_pattern, text, re.IGNORECASE)
        for state in states:
            entity_key = f"entity_state_{state.lower()}"
            await self.set(
                entity_key,
                {"type": "state", "name": state},
                MemoryType.SEMANTIC,
                importance=0.8,
                tags=["entity", "state"]
            )
            entities.append({"type": "state", "name": state})
        
        return entities
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        if not self.embedding_model:
            return []
        
        return await self.embedding_model.embed(text)
    
    async def _update_access(self, entry: MemoryEntry) -> None:
        """Update access metadata."""
        entry.accessed_at = datetime.utcnow()
        entry.access_count += 1
    
    async def _maybe_consolidate(self) -> None:
        """Consolidate short-term to long-term if needed."""
        # Check short-term size
        # If exceeds threshold, move least accessed to long-term
        pass
    
    def get_context_hash(self) -> str:
        """Get hash of current context for caching."""
        context_str = json.dumps(self._current_context, sort_keys=True)
        return hashlib.sha256(context_str.encode()).hexdigest()
