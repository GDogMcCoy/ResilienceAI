"""
ResilienceAI Database Connection Management
Implements connection pooling and query utilities for PostgreSQL
"""

from contextlib import contextmanager
from typing import Generator, Optional, List, Dict, Any, Callable
from functools import wraps
import os
import logging
import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor, execute_values
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration from environment
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "6432")),  # PgBouncer port by default
    "database": os.getenv("DB_NAME", "resilienceai"),
    "user": os.getenv("DB_USER", "resilienceai_app"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# Connection pool settings
POOL_CONFIG = {
    "minconn": int(os.getenv("DB_POOL_MIN", "5")),
    "maxconn": int(os.getenv("DB_POOL_MAX", "50")),
}

# Query timeout (seconds)
QUERY_TIMEOUT = int(os.getenv("DB_QUERY_TIMEOUT", "30"))


class DatabasePool:
    """
    Thread-safe database connection pool singleton.
    Uses psycopg2's ThreadedConnectionPool for concurrent access.
    """
    
    _instance = None
    _lock = threading.Lock()
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._initialize_pool()
        return cls._instance
    
    @classmethod
    def _initialize_pool(cls):
        """Initialize the connection pool"""
        try:
            cls._pool = pool.ThreadedConnectionPool(
                **POOL_CONFIG,
                **DB_CONFIG
            )
            logger.info(f"Database pool initialized: {POOL_CONFIG['minconn']}-{POOL_CONFIG['maxconn']} connections")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self) -> Generator:
        """
        Get connection from pool with automatic return.
        Usage:
            with db_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM counties")
        """
        conn = None
        try:
            conn = self._pool.getconn()
            # Set query timeout
            conn.set_session(options=f'-c statement_timeout={QUERY_TIMEOUT * 1000}')
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self._pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor) -> Generator:
        """
        Get cursor with automatic cleanup.
        Usage:
            with db_pool.get_cursor() as cursor:
                cursor.execute("SELECT * FROM counties")
                results = cursor.fetchall()
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()
    
    def execute(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """
        Execute query and return results as list of dictionaries.
        
        Args:
            query: SQL query string
            params: Query parameters (tuple)
            
        Returns:
            List of dictionaries with query results
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict]:
        """
        Execute query and return single result.
        
        Args:
            query: SQL query string
            params: Query parameters (tuple)
            
        Returns:
            Single dictionary or None
        """
        results = self.execute(query, params)
        return results[0] if results else None
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Execute query with multiple parameter sets.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Number of rows affected
        """
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    def execute_values(self, query: str, values: List[tuple], page_size: int = 1000) -> int:
        """
        Execute INSERT/UPDATE with VALUES using execute_values for efficiency.
        
        Args:
            query: SQL query with %s placeholder for values
            values: List of value tuples
            page_size: Number of rows per batch
            
        Returns:
            Number of rows inserted/updated
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                execute_values(cursor, query, values, page_size=page_size)
                return cursor.rowcount
            finally:
                cursor.close()
    
    def close_all(self):
        """Close all connections in pool"""
        if self._pool:
            self._pool.closeall()
            logger.info("All database connections closed")


# Global pool instance
db_pool = DatabasePool()


# ============================================
# QUERY BUILDER UTILITIES
# ============================================

class QueryBuilder:
    """Helper class for building SQL queries safely"""
    
    @staticmethod
    def build_where_clause(conditions: Dict[str, Any]) -> tuple:
        """
        Build WHERE clause from conditions dictionary.
        
        Args:
            conditions: Dict of column_name -> value
            
        Returns:
            Tuple of (where_clause_string, params_tuple)
        """
        if not conditions:
            return "", ()
        
        clauses = []
        params = []
        
        for column, value in conditions.items():
            if isinstance(value, list):
                # IN clause
                placeholders = ', '.join(['%s'] * len(value))
                clauses.append(f"{column} IN ({placeholders})")
                params.extend(value)
            elif isinstance(value, tuple) and len(value) == 2:
                # Range (BETWEEN)
                clauses.append(f"{column} BETWEEN %s AND %s")
                params.extend(value)
            else:
                # Equality
                clauses.append(f"{column} = %s")
                params.append(value)
        
        where_clause = " AND ".join(clauses)
        return f"WHERE {where_clause}", tuple(params)
    
    @staticmethod
    def build_order_clause(order_by: List[tuple]) -> str:
        """
        Build ORDER BY clause.
        
        Args:
            order_by: List of (column, direction) tuples
            
        Returns:
            ORDER BY clause string
        """
        if not order_by:
            return ""
        
        clauses = []
        for column, direction in order_by:
            direction = direction.upper() if direction.upper() in ['ASC', 'DESC'] else 'ASC'
            clauses.append(f"{column} {direction}")
        
        return f"ORDER BY {', '.join(clauses)}"


# ============================================
# CACHED QUERY DECORATOR
# ============================================

def cached_query(prefix: str, ttl_seconds: int = 300):
    """
    Decorator for caching query results.
    Requires Redis cache to be configured.
    
    Args:
        prefix: Cache key prefix
        ttl_seconds: Time-to-live in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to import and use Redis cache
            try:
                from redis_cache import cache
                import hashlib
                import json
                
                # Generate cache key
                key_data = f"{prefix}:{json.dumps(args, sort_keys=True)}:{json.dumps(kwargs, sort_keys=True)}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
                
                # Try to get from cache
                cached = cache.get(cache_key)
                if cached is not None:
                    return cached
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Cache result
                cache.set(cache_key, result, ttl_seconds)
                
                return result
            except ImportError:
                # Redis not available, execute without caching
                return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================
# COUNTY DATA ACCESS FUNCTIONS
# ============================================

def get_county_by_fips(fips_code: str) -> Optional[Dict]:
    """
    Get county by FIPS code.
    
    Args:
        fips_code: 5-digit FIPS code
        
    Returns:
        County data dictionary or None
    """
    query = """
    SELECT * FROM counties 
    WHERE fips_code = %s
    """
    return db_pool.execute_one(query, (fips_code,))


def get_county_by_name(county_name: str, state_abbrev: Optional[str] = None) -> Optional[Dict]:
    """
    Get county by name (with optional state filter).
    
    Args:
        county_name: County name
        state_abbrev: Optional state abbreviation
        
    Returns:
        County data dictionary or None
    """
    if state_abbrev:
        query = """
        SELECT * FROM counties 
        WHERE county_name ILIKE %s AND state_abbrev = %s
        LIMIT 1
        """
        return db_pool.execute_one(query, (f"%{county_name}%", state_abbrev))
    else:
        query = """
        SELECT * FROM counties 
        WHERE county_name ILIKE %s
        LIMIT 1
        """
        return db_pool.execute_one(query, (f"%{county_name}%",))


def get_counties_by_state(state_abbrev: str, limit: int = 1000) -> List[Dict]:
    """
    Get all counties in a state.
    
    Args:
        state_abbrev: State abbreviation (e.g., 'MO')
        limit: Maximum number of results
        
    Returns:
        List of county dictionaries
    """
    query = """
    SELECT * FROM counties 
    WHERE state_abbrev = %s
    ORDER BY county_name
    LIMIT %s
    """
    return db_pool.execute(query, (state_abbrev, limit))


@cached_query(prefix="county_features", ttl_seconds=300)
def get_county_features(fips_code: str, feature_keys: Optional[List[str]] = None) -> List[Dict]:
    """
    Get features for a county.
    
    Args:
        fips_code: 5-digit FIPS code
        feature_keys: Optional list of feature keys to filter
        
    Returns:
        List of feature dictionaries
    """
    if feature_keys:
        query = """
        SELECT 
            f.feature_key, 
            f.display_name, 
            f.unit,
            fc.category_name,
            cf.numeric_value, 
            cf.confidence_score,
            cf.effective_date
        FROM counties c
        JOIN county_features cf ON c.id = cf.county_id
        JOIN feature_definitions f ON cf.feature_id = f.id
        JOIN feature_categories fc ON f.category_id = fc.id
        WHERE c.fips_code = %s 
          AND f.feature_key = ANY(%s)
          AND cf.effective_date = CURRENT_DATE
        ORDER BY fc.display_order, f.display_name
        """
        return db_pool.execute(query, (fips_code, feature_keys))
    else:
        query = """
        SELECT 
            f.feature_key, 
            f.display_name, 
            f.unit,
            fc.category_name,
            cf.numeric_value, 
            cf.confidence_score,
            cf.effective_date
        FROM counties c
        JOIN county_features cf ON c.id = cf.county_id
        JOIN feature_definitions f ON cf.feature_id = f.id
        JOIN feature_categories fc ON f.category_id = fc.id
        WHERE c.fips_code = %s
          AND cf.effective_date = CURRENT_DATE
        ORDER BY fc.display_order, f.display_name
        """
        return db_pool.execute(query, (fips_code,))


def get_counties_in_radius(
    lat: float, 
    lon: float, 
    radius_km: float,
    limit: int = 100
) -> List[Dict]:
    """
    Get counties within radius of a point.
    
    Args:
        lat: Latitude
        lon: Longitude
        radius_km: Radius in kilometers
        limit: Maximum results
        
    Returns:
        List of county dictionaries with distance_km
    """
    query = """
    SELECT 
        c.*,
        ST_Distance(
            c.centroid::geography,
            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
        ) / 1000 as distance_km
    FROM counties c
    WHERE ST_DWithin(
        c.centroid::geography,
        ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
        %s * 1000
    )
    ORDER BY distance_km
    LIMIT %s
    """
    return db_pool.execute(query, (lon, lat, lon, lat, radius_km, limit))


def search_counties(
    query: str,
    state_abbrev: Optional[str] = None,
    limit: int = 20
) -> List[Dict]:
    """
    Search counties by name (fuzzy search).
    
    Args:
        query: Search query
        state_abbrev: Optional state filter
        limit: Maximum results
        
    Returns:
        List of matching counties
    """
    if state_abbrev:
        sql_query = """
        SELECT * FROM counties 
        WHERE county_name % %s 
          AND state_abbrev = %s
        ORDER BY similarity(county_name, %s) DESC
        LIMIT %s
        """
        return db_pool.execute(sql_query, (query, state_abbrev, query, limit))
    else:
        sql_query = """
        SELECT * FROM counties 
        WHERE county_name % %s
        ORDER BY similarity(county_name, %s) DESC
        LIMIT %s
        """
        return db_pool.execute(sql_query, (query, query, limit))


# ============================================
# FEATURE DATA ACCESS FUNCTIONS
# ============================================

def get_feature_definition(feature_key: str) -> Optional[Dict]:
    """Get feature definition by key"""
    query = """
    SELECT fd.*, fc.category_name, fc.domain
    FROM feature_definitions fd
    JOIN feature_categories fc ON fd.category_id = fc.id
    WHERE fd.feature_key = %s
    """
    return db_pool.execute_one(query, (feature_key,))


def get_all_feature_definitions(category: Optional[str] = None) -> List[Dict]:
    """Get all feature definitions, optionally filtered by category"""
    if category:
        query = """
        SELECT fd.*, fc.category_name, fc.domain
        FROM feature_definitions fd
        JOIN feature_categories fc ON fd.category_id = fc.id
        WHERE fc.category_name = %s AND fd.is_active = TRUE
        ORDER BY fc.display_order, fd.display_name
        """
        return db_pool.execute(query, (category,))
    else:
        query = """
        SELECT fd.*, fc.category_name, fc.domain
        FROM feature_definitions fd
        JOIN feature_categories fc ON fd.category_id = fc.id
        WHERE fd.is_active = TRUE
        ORDER BY fc.display_order, fd.display_name
        """
        return db_pool.execute(query)


def get_feature_statistics(feature_key: str) -> Optional[Dict]:
    """Get statistics for a feature across all counties"""
    query = """
    SELECT 
        fd.feature_key,
        fd.display_name,
        fd.unit,
        COUNT(cf.id) as county_count,
        AVG(cf.numeric_value) as avg_value,
        MIN(cf.numeric_value) as min_value,
        MAX(cf.numeric_value) as max_value,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cf.numeric_value) as median_value,
        STDDEV(cf.numeric_value) as stddev_value
    FROM feature_definitions fd
    LEFT JOIN county_features cf ON fd.id = cf.feature_id
    WHERE fd.feature_key = %s
      AND cf.effective_date = CURRENT_DATE
    GROUP BY fd.id, fd.feature_key, fd.display_name, fd.unit
    """
    return db_pool.execute_one(query, (feature_key,))


# ============================================
# ALERT DATA ACCESS FUNCTIONS
# ============================================

def get_active_alerts(
    fips_code: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100
) -> List[Dict]:
    """Get active alerts, optionally filtered by county and severity"""
    conditions = ["ae.status = 'active'", "(ae.expires_at IS NULL OR ae.expires_at > NOW())"]
    params = []
    
    if fips_code:
        conditions.append("c.fips_code = %s")
        params.append(fips_code)
    
    if severity:
        conditions.append("ae.severity = %s")
        params.append(severity)
    
    where_clause = " AND ".join(conditions)
    
    query = f"""
    SELECT 
        ae.id,
        ae.alert_type,
        ae.severity,
        ae.title,
        ae.message,
        ae.risk_score,
        ae.triggered_at,
        ae.expires_at,
        c.fips_code,
        c.county_name,
        c.state_abbrev
    FROM alert_events ae
    JOIN counties c ON ae.county_id = c.id
    WHERE {where_clause}
    ORDER BY ae.severity DESC, ae.triggered_at DESC
    LIMIT %s
    """
    params.append(limit)
    
    return db_pool.execute(query, tuple(params))


def create_alert_subscription(
    county_fips: str,
    email: str,
    alert_types: List[str],
    severity_threshold: str = 'medium',
    risk_threshold: Optional[float] = None
) -> str:
    """Create a new alert subscription"""
    query = """
    INSERT INTO alert_subscriptions (
        county_id, email, alert_types, severity_threshold, risk_threshold
    )
    SELECT 
        c.id, %s, %s::alert_type[], %s::alert_severity, %s
    FROM counties c
    WHERE c.fips_code = %s
    RETURNING id
    """
    result = db_pool.execute_one(
        query, 
        (email, alert_types, severity_threshold, risk_threshold, county_fips)
    )
    return str(result['id']) if result else None


# ============================================
# BATCH OPERATIONS
# ============================================

def bulk_insert_county_features(data: List[Dict]) -> int:
    """
    Bulk insert county features efficiently.
    
    Args:
        data: List of dicts with keys: county_id, feature_id, numeric_value, effective_date
        
    Returns:
        Number of rows inserted
    """
    query = """
    INSERT INTO county_features (county_id, feature_id, numeric_value, effective_date)
    VALUES %s
    ON CONFLICT (county_id, feature_id, effective_date) DO UPDATE SET
        numeric_value = EXCLUDED.numeric_value,
        calculated_at = NOW()
    """
    
    values = [
        (d['county_id'], d['feature_id'], d['numeric_value'], d.get('effective_date', 'CURRENT_DATE'))
        for d in data
    ]
    
    return db_pool.execute_values(query, values, page_size=1000)


def bulk_insert_metrics_history(data: List[Dict]) -> int:
    """
    Bulk insert historical metrics efficiently.
    
    Args:
        data: List of dicts with keys: time, county_id, feature_id, value, value_type, confidence
        
    Returns:
        Number of rows inserted
    """
    query = """
    INSERT INTO county_metrics_history (time, county_id, feature_id, value, value_type, confidence, data_source)
    VALUES %s
    ON CONFLICT (time, county_id, feature_id) DO UPDATE SET
        value = EXCLUDED.value,
        value_type = EXCLUDED.value_type,
        confidence = EXCLUDED.confidence
    """
    
    values = [
        (d['time'], d['county_id'], d['feature_id'], d['value'], 
         d.get('value_type', 'measured'), d.get('confidence', 1.0), d.get('data_source'))
        for d in data
    ]
    
    return db_pool.execute_values(query, values, page_size=1000)


# ============================================
# HEALTH CHECK
# ============================================

def health_check() -> Dict[str, Any]:
    """Check database health and return status"""
    try:
        start_time = __import__('time').time()
        result = db_pool.execute_one("SELECT 1 as health")
        latency_ms = (__import__('time').time() - start_time) * 1000
        
        # Get connection pool stats
        pool_stats = {
            "min_connections": POOL_CONFIG["minconn"],
            "max_connections": POOL_CONFIG["maxconn"],
        }
        
        return {
            "status": "healthy",
            "latency_ms": round(latency_ms, 2),
            "pool": pool_stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    # Test the connection
    print("Testing database connection...")
    health = health_check()
    print(f"Health check: {health}")
    
    # Test county lookup
    county = get_county_by_fips("29095")  # Jackson County, MO
    print(f"County lookup: {county}")
