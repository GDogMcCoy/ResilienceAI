"""
Neo4j Connection Manager for ResilienceAI
Provides connection pooling, transaction management, and query execution.
"""

import os
import logging
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from functools import wraps
import time

from neo4j import GraphDatabase, Driver, Session, Transaction
from neo4j.exceptions import Neo4jError, ServiceUnavailable, TransientError
from neo4j.graph import Node, Relationship

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class Neo4jConfig:
    """Configuration for Neo4j connection."""
    uri: str = field(default_factory=lambda: os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    user: str = field(default_factory=lambda: os.getenv("NEO4J_USER", "neo4j"))
    password: str = field(default_factory=lambda: os.getenv("NEO4J_PASSWORD", "password"))
    database: str = field(default_factory=lambda: os.getenv("NEO4J_DATABASE", "neo4j"))
    max_connection_pool_size: int = 50
    connection_timeout: int = 30
    max_transaction_retry_time: int = 30
    encrypted: bool = True
    trust: str = "TRUST_SYSTEM_CA_SIGNED_CERTIFICATES"


class Neo4jConnectionManager:
    """
    Manages Neo4j connections with pooling and retry logic.
    Implements singleton pattern for connection reuse.
    """
    
    _instance: Optional['Neo4jConnectionManager'] = None
    _driver: Optional[Driver] = None
    _lock = None
    
    def __new__(cls, config: Optional[Neo4jConfig] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = config or Neo4jConfig()
            cls._instance._initialize_driver()
        return cls._instance
    
    def _initialize_driver(self) -> None:
        """Initialize the Neo4j driver with connection pooling."""
        try:
            self._driver = GraphDatabase.driver(
                self._config.uri,
                auth=(self._config.user, self._config.password),
                max_connection_pool_size=self._config.max_connection_pool_size,
                connection_timeout=self._config.connection_timeout,
                max_transaction_retry_time=self._config.max_transaction_retry_time,
                encrypted=self._config.encrypted
            )
            
            # Verify connectivity
            self._driver.verify_connectivity()
            logger.info(f"Neo4j driver initialized: {self._config.uri}")
            
        except ServiceUnavailable as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    @property
    def driver(self) -> Driver:
        """Get the Neo4j driver instance."""
        if self._driver is None:
            self._initialize_driver()
        return self._driver
    
    @contextmanager
    def session(self, database: Optional[str] = None, access_mode: str = "READ"):
        """
        Context manager for Neo4j sessions.
        
        Args:
            database: Database name (defaults to config)
            access_mode: "READ" or "WRITE"
            
        Usage:
            with manager.session() as session:
                result = session.run("MATCH (n) RETURN n")
        """
        db = database or self._config.database
        session = self.driver.session(database=db)
        try:
            yield session
        finally:
            session.close()
    
    def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a read query and return results.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Target database name
            
        Returns:
            List of result records as dictionaries
        """
        with self.session(database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def execute_write(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a write query within a transaction.
        
        Args:
            query: Cypher write query
            parameters: Query parameters
            database: Target database name
            
        Returns:
            List of result records
        """
        def _execute_tx(tx: Transaction):
            result = tx.run(query, parameters or {})
            return [record.data() for record in result]
        
        with self.session(database, access_mode="WRITE") as session:
            return session.execute_write(_execute_tx)
    
    def execute_read(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a read query within a transaction.
        
        Args:
            query: Cypher read query
            parameters: Query parameters
            database: Target database name
            
        Returns:
            List of result records
        """
        def _execute_tx(tx: Transaction):
            result = tx.run(query, parameters or {})
            return [record.data() for record in result]
        
        with self.session(database, access_mode="READ") as session:
            return session.execute_read(_execute_tx)
    
    def bulk_insert(
        self,
        query: str,
        batch_data: List[Dict[str, Any]],
        batch_size: int = 1000,
        database: Optional[str] = None
    ) -> int:
        """
        Efficiently insert data in batches using UNWIND.
        
        Args:
            query: Cypher query with $batch parameter
            batch_data: List of data dictionaries
            batch_size: Number of records per batch
            database: Target database name
            
        Returns:
            Total number of records inserted
        """
        total_inserted = 0
        
        for i in range(0, len(batch_data), batch_size):
            batch = batch_data[i:i + batch_size]
            
            result = self.execute_write(
                query,
                {"batch": batch},
                database
            )
            
            total_inserted += len(batch)
            logger.debug(f"Inserted batch {i//batch_size + 1}: {len(batch)} records")
        
        logger.info(f"Bulk insert complete: {total_inserted} total records")
        return total_inserted
    
    def execute_with_retry(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Execute query with automatic retry on transient errors.
        
        Args:
            query: Cypher query
            parameters: Query parameters
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries in seconds
            
        Returns:
            Query results
        """
        for attempt in range(max_retries):
            try:
                return self.execute_write(query, parameters)
            except TransientError as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Transient error, retrying ({attempt + 1}/{max_retries}): {e}")
                time.sleep(retry_delay * (attempt + 1))
        return []
    
    def close(self) -> None:
        """Close the Neo4j driver and release resources."""
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Neo4j driver closed")
    
    def __del__(self):
        """Destructor to ensure driver cleanup."""
        self.close()
    
    def health_check(self) -> Dict[str, Any]:
        """Check Neo4j connection health."""
        try:
            start_time = time.time()
            result = self.execute_read("RETURN 1 AS health")
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "connected": True
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "connected": False
            }


def retry_on_error(max_retries: int = 3, exceptions: tuple = (Neo4jError, ServiceUnavailable)):
    """Decorator for retrying Neo4j operations."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(1.0 * (attempt + 1))
        return wrapper
    return decorator


def get_neo4j_manager(config: Optional[Neo4jConfig] = None) -> Neo4jConnectionManager:
    """Get or create Neo4j connection manager instance."""
    return Neo4jConnectionManager(config)
