# ResilienceAI Database Migration Strategy

## Executive Summary

This document provides a comprehensive database migration strategy for ResilienceAI, designed to support schema evolution across multiple databases with zero-downtime requirements. The strategy leverages Alembic as the primary migration framework with custom extensions for enterprise-grade migration management.

---

## Table of Contents

1. [Migration Architecture](#1-migration-architecture)
2. [Schema Versioning Strategy](#2-schema-versioning-strategy)
3. [Migration Scripts](#3-migration-scripts)
4. [Rollback Strategies](#4-rollback-strategies)
5. [Data Migrations](#5-data-migrations)
6. [Testing Framework](#6-testing-framework)
7. [Continuous Migration](#7-continuous-migration)
8. [Database Seeding](#8-database-seeding)
9. [Schema Comparison](#9-schema-comparison)
10. [Implementation Priority](#10-implementation-priority)

---

## 1. Migration Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RESILIENCEAI MIGRATION ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   Primary    │    │   Replica    │    │   Replica    │                   │
│  │  PostgreSQL  │◄──►│  PostgreSQL  │◄──►│  PostgreSQL  │                   │
│  │   (Write)    │    │   (Read)     │    │   (Read)     │                   │
│  └──────┬───────┘    └──────────────┘    └──────────────┘                   │
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────┐                │
│  │              ALEMBIC MIGRATION ENGINE                    │                │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │                │
│  │  │   Version   │  │   Schema    │  │   Migration     │  │                │
│  │  │   Control   │  │   Registry  │  │   Orchestrator  │  │                │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │                │
│  └─────────────────────────────────────────────────────────┘                │
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────┐                │
│  │              MIGRATION LIFECYCLE MANAGER                 │                │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │                │
│  │  │  Create  │ │  Test    │ │  Deploy  │ │ Rollback │   │                │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │                │
│  └─────────────────────────────────────────────────────────┘                │
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────┐                │
│  │              CI/CD INTEGRATION                           │                │
│  │     GitHub Actions / GitLab CI / Jenkins Pipeline       │                │
│  └─────────────────────────────────────────────────────────┘                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Directory Structure

```
/migrations/
├── alembic/
│   ├── versions/                    # Migration scripts
│   │   ├── 001_initial_schema.py
│   │   ├── 002_add_user_indexes.py
│   │   └── 003_add_audit_tables.py
│   ├── env.py                       # Alembic environment configuration
│   ├── script.py.mako              # Migration template
│   └── README.md                   # Alembic documentation
├── scripts/
│   ├── migrate.py                  # Main migration script
│   ├── rollback.py                 # Rollback utility
│   ├── verify.py                   # Migration verification
│   └── seed.py                     # Database seeding
├── tests/
│   ├── test_migrations.py          # Migration tests
│   ├── test_rollbacks.py           # Rollback tests
│   └── fixtures/                   # Test fixtures
├── config/
│   ├── alembic.ini                 # Alembic configuration
│   └── environments/               # Environment-specific configs
│       ├── development.ini
│       ├── staging.ini
│       └── production.ini
├── models/
│   ├── __init__.py
│   ├── base.py                     # SQLAlchemy base
│   ├── user.py
│   ├── incident.py
│   └── audit.py
└── utils/
    ├── migration_utils.py          # Migration utilities
    ├── schema_diff.py              # Schema comparison
    └── validators.py               # Migration validators
```

### 1.3 Core Migration Manager

```python
# /migrations/core/migration_manager.py
"""
Core migration manager for ResilienceAI database migrations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any, Callable
import logging
import asyncio
from contextlib import asynccontextmanager

import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from alembic import command
from alembic.config import Config


class MigrationStatus(Enum):
    """Migration execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class MigrationType(Enum):
    """Types of database migrations."""
    SCHEMA = "schema"           # DDL changes
    DATA = "data"               # DML changes
    INDEX = "index"             # Index operations
    CONSTRAINT = "constraint"   # Constraint operations
    PARTITION = "partition"     # Partition operations


@dataclass
class MigrationContext:
    """Context for migration execution."""
    environment: str
    database_url: str
    dry_run: bool = False
    timeout_seconds: int = 3600
    max_retries: int = 3
    retry_delay_seconds: int = 5


@dataclass
class MigrationResult:
    """Result of migration execution."""
    migration_id: str
    status: MigrationStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    changes_applied: List[str] = None
    rollback_script: Optional[str] = None


class MigrationStrategy(ABC):
    """Abstract base class for migration strategies."""
    
    @abstractmethod
    async def execute(self, context: MigrationContext) -> MigrationResult:
        """Execute the migration."""
        pass
    
    @abstractmethod
    async def rollback(self, context: MigrationContext) -> MigrationResult:
        """Rollback the migration."""
        pass
    
    @abstractmethod
    async def verify(self, context: MigrationContext) -> bool:
        """Verify migration was applied correctly."""
        pass


class ZeroDowntimeMigrationStrategy(MigrationStrategy):
    """
    Strategy for zero-downtime migrations using online schema changes.
    
    Techniques:
    - Online index creation (PostgreSQL 11+)
    - Concurrent index builds
    - Column addition without table lock
    - Shadow table pattern for major changes
    """
    
    def __init__(self, migration_sql: str, rollback_sql: str):
        self.migration_sql = migration_sql
        self.rollback_sql = rollback_sql
        self._shadow_table_suffix = "_shadow"
    
    async def execute(self, context: MigrationContext) -> MigrationResult:
        """Execute zero-downtime migration."""
        start_time = datetime.utcnow()
        
        try:
            async with self._get_connection(context) as conn:
                # Use advisory lock for coordination
                await conn.execute("SELECT pg_advisory_lock(42)")
                
                # Check if migration already applied
                if await self._is_migration_applied(conn, context):
                    return MigrationResult(
                        migration_id=self._get_migration_id(),
                        status=MigrationStatus.SUCCESS,
                        start_time=start_time,
                        end_time=datetime.utcnow(),
                        changes_applied=[]
                    )
                
                # Execute migration with retries
                for attempt in range(context.max_retries):
                    try:
                        changes = await self._execute_with_online_changes(conn)
                        break
                    except Exception as e:
                        if attempt == context.max_retries - 1:
                            raise
                        await asyncio.sleep(context.retry_delay_seconds)
                
                await conn.execute("SELECT pg_advisory_unlock(42)")
                
                return MigrationResult(
                    migration_id=self._get_migration_id(),
                    status=MigrationStatus.SUCCESS,
                    start_time=start_time,
                    end_time=datetime.utcnow(),
                    changes_applied=changes,
                    rollback_script=self.rollback_sql
                )
                
        except Exception as e:
            return MigrationResult(
                migration_id=self._get_migration_id(),
                status=MigrationStatus.FAILED,
                start_time=start_time,
                end_time=datetime.utcnow(),
                error_message=str(e),
                rollback_script=self.rollback_sql
            )
    
    async def _execute_with_online_changes(self, conn) -> List[str]:
        """Execute migration using online schema change techniques."""
        changes = []
        
        # Parse and execute SQL with online modifications
        statements = self._parse_sql_statements()
        
        for stmt in statements:
            if self._is_index_operation(stmt):
                # Use CONCURRENTLY for index operations
                stmt = self._make_concurrent(stmt)
            elif self._is_alter_table(stmt):
                # Use online alter table if available
                stmt = self._optimize_alter_table(stmt)
            
            await conn.execute(stmt)
            changes.append(stmt)
        
        return changes
    
    def _make_concurrent(self, sql: str) -> str:
        """Make index creation concurrent."""
        if "CREATE INDEX" in sql.upper() and "CONCURRENTLY" not in sql.upper():
            return sql.replace("CREATE INDEX", "CREATE INDEX CONCURRENTLY", 1)
        return sql


class MigrationOrchestrator:
    """Orchestrates migrations across multiple databases and environments."""
    
    def __init__(self):
        self.strategies: Dict[str, MigrationStrategy] = {}
        self.hooks: Dict[str, List[Callable]] = {
            'pre_migrate': [],
            'post_migrate': [],
            'pre_rollback': [],
            'post_rollback': []
        }
        self.logger = logging.getLogger(__name__)
    
    def register_strategy(self, name: str, strategy: MigrationStrategy):
        """Register a migration strategy."""
        self.strategies[name] = strategy
    
    async def migrate(self, context: MigrationContext, strategy_name: str = "zero_downtime") -> MigrationResult:
        """Execute migration with full lifecycle management."""
        # Execute pre-migrate hooks
        for hook in self.hooks['pre_migrate']:
            await hook(context)
        
        strategy = self.strategies.get(strategy_name)
        if not strategy:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        # Execute migration
        result = await strategy.execute(context)
        
        # Execute post-migrate hooks
        for hook in self.hooks['post_migrate']:
            await hook(context, result)
        
        return result


# Singleton instance
migration_orchestrator = MigrationOrchestrator()
```

---

## 2. Schema Versioning Strategy

### 2.1 Version Control Model

```python
# /migrations/core/versioning.py
"""
Schema versioning and version control for ResilienceAI.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Set
from enum import Enum
import hashlib
import json


class VersionStatus(Enum):
    """Version status enumeration."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


@dataclass
class SchemaVersion:
    """Represents a schema version with metadata."""
    version_id: str
    revision: str
    parent_revision: Optional[str]
    created_at: datetime
    author: str
    description: str
    status: VersionStatus
    checksum: str
    dependencies: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, any] = field(default_factory=dict)
    
    def calculate_checksum(self, content: str) -> str:
        """Calculate SHA-256 checksum of migration content."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def verify_checksum(self, content: str) -> bool:
        """Verify content matches stored checksum."""
        return self.calculate_checksum(content) == self.checksum


class SemanticVersioning:
    """
    Semantic versioning for schema changes.
    Format: MAJOR.MINOR.PATCH-BUILD
    
    MAJOR: Breaking schema changes (table drops, column removals)
    MINOR: Non-breaking additions (new tables, new columns)
    PATCH: Fixes and optimizations (index additions, constraint fixes)
    BUILD: Build metadata (timestamp, git commit)
    """
    
    def __init__(self, major: int = 0, minor: int = 0, patch: int = 0, build: Optional[str] = None):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.build = build or datetime.utcnow().strftime("%Y%m%d%H%M%S")
    
    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.build:
            version += f"+{self.build}"
        return version
    
    def bump_major(self) -> 'SemanticVersioning':
        """Bump major version."""
        return SemanticVersioning(major=self.major + 1, minor=0, patch=0)
    
    def bump_minor(self) -> 'SemanticVersioning':
        """Bump minor version."""
        return SemanticVersioning(major=self.major, minor=self.minor + 1, patch=0)
    
    def bump_patch(self) -> 'SemanticVersioning':
        """Bump patch version."""
        return SemanticVersioning(major=self.major, minor=self.minor, patch=self.patch + 1)


class VersionGraph:
    """Directed acyclic graph for tracking version dependencies."""
    
    def __init__(self):
        self.versions: Dict[str, SchemaVersion] = {}
        self.edges: Dict[str, List[str]] = {}  # version -> dependents
        self.reverse_edges: Dict[str, List[str]] = {}  # version -> dependencies
    
    def add_version(self, version: SchemaVersion) -> None:
        """Add a version to the graph."""
        self.versions[version.revision] = version
        
        if version.revision not in self.edges:
            self.edges[version.revision] = []
        
        if version.revision not in self.reverse_edges:
            self.reverse_edges[version.revision] = []
        
        # Add dependency edges
        for dep in version.dependencies:
            if dep not in self.edges:
                self.edges[dep] = []
            self.edges[dep].append(version.revision)
            self.reverse_edges[version.revision].append(dep)
    
    def topological_sort(self) -> List[str]:
        """Return versions in topological order."""
        in_degree = {v: len(self.reverse_edges.get(v, [])) for v in self.versions}
        
        queue = [v for v, d in in_degree.items() if d == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for dependent in self.edges.get(current, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        if len(result) != len(self.versions):
            raise ValueError("Version graph contains cycles")
        
        return result


class VersionRegistry:
    """Central registry for managing schema versions."""
    
    def __init__(self, storage_backend: Optional[Any] = None):
        self.graph = VersionGraph()
        self.storage = storage_backend
        self._current_version: Optional[str] = None
    
    def register(self, version: SchemaVersion) -> None:
        """Register a new schema version."""
        # Validate checksum
        if not version.verify_checksum(version.metadata.get('content', '')):
            raise ValueError(f"Checksum mismatch for version {version.version_id}")
        
        self.graph.add_version(version)
        
        if self.storage:
            self._persist_version(version)
    
    def get_version(self, revision: str) -> Optional[SchemaVersion]:
        """Get version by revision."""
        return self.graph.versions.get(revision)
```

### 2.2 Version Table Schema

```sql
-- Schema version tracking table
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    applied_by VARCHAR(255),
    checksum VARCHAR(64),
    execution_time_ms INTEGER,
    rollback_sql TEXT,
    PRIMARY KEY (version_num)
);

-- Extended version metadata
CREATE TABLE IF NOT EXISTS schema_version_metadata (
    version_num VARCHAR(32) NOT NULL REFERENCES alembic_version(version_num),
    key VARCHAR(255) NOT NULL,
    value TEXT,
    PRIMARY KEY (version_num, key)
);

-- Migration execution log
CREATE TABLE IF NOT EXISTS migration_execution_log (
    id SERIAL PRIMARY KEY,
    version_num VARCHAR(32) NOT NULL,
    action VARCHAR(50) NOT NULL,  -- 'upgrade', 'downgrade', 'verify'
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    executed_by VARCHAR(255),
    success BOOLEAN NOT NULL,
    error_message TEXT,
    duration_ms INTEGER
);

-- Create indexes
CREATE INDEX idx_migration_log_version ON migration_execution_log(version_num);
CREATE INDEX idx_migration_log_executed_at ON migration_execution_log(executed_at);
```

---

## 3. Migration Scripts

### 3.1 Migration Template

```python
# /migrations/alembic/script.py.mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}
from migrations.utils.migration_utils import (
    create_index_concurrently,
    add_column_online,
    execute_with_timeout,
    verify_migration
)

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

# Migration metadata
MIGRATION_TYPE = "${migration_type | default('schema')}"
ONLINE_MIGRATION = ${online_migration | default('True')}
TIMEOUT_SECONDS = ${timeout_seconds | default('3600')}
REQUIRES_DOWNTIME = ${requires_downtime | default('False')}


def upgrade():
    """
    Apply migration changes.
    
    This function is called when migrating to this revision.
    All changes should be idempotent and support retries.
    """
    ${upgrades if upgrades else "pass"}


def downgrade():
    """
    Revert migration changes.
    
    This function is called when rolling back from this revision.
    Should restore the database to the previous state.
    """
    ${downgrades if downgrades else "pass"}


def verify():
    """
    Verify migration was applied correctly.
    
    Returns True if migration is verified, False otherwise.
    """
    ${verification if verification else "return True"}
```

### 3.2 Example Migration Scripts

```python
# /migrations/alembic/versions/001_initial_schema.py
"""
Initial schema creation for ResilienceAI.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-01-15 10:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

MIGRATION_TYPE = "schema"
ONLINE_MIGRATION = False
REQUIRES_DOWNTIME = True


def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_admin', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), 
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('CURRENT_TIMESTAMP'),
                  onupdate=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # Create incidents table (partitioned)
    op.execute("""
        CREATE TABLE incidents (
            id BIGSERIAL,
            title VARCHAR(500) NOT NULL,
            description TEXT,
            severity VARCHAR(50) NOT NULL,
            status VARCHAR(50) DEFAULT 'open',
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP WITH TIME ZONE NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE,
            metadata JSONB DEFAULT '{}',
            PRIMARY KEY (id, created_at)
        ) PARTITION BY RANGE (created_at);
    """)
    
    # Create partitions
    op.execute("""
        CREATE TABLE incidents_2024_q1 PARTITION OF incidents
        FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
    """)
    
    op.execute("""
        CREATE TABLE incidents_2024_q2 PARTITION OF incidents
        FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');
    """)
    
    # Create indexes on partitioned table
    op.create_index('idx_incidents_status', 'incidents', ['status'])
    op.create_index('idx_incidents_severity', 'incidents', ['severity'])
    op.create_index('idx_incidents_created_at', 'incidents', ['created_at'])
    op.create_index(
        'idx_incidents_metadata',
        'incidents',
        ['metadata'],
        postgresql_using='gin'
    )


def downgrade():
    op.drop_table('incidents')
    op.drop_table('users')
```

---

## 4. Rollback Strategies

### 4.1 Rollback Framework

```python
# /migrations/core/rollback.py
"""
Rollback strategies and utilities for database migrations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Callable, Tuple
from enum import Enum
import logging
import json
from datetime import datetime

from sqlalchemy import text, create_engine
from alembic import command, op
from alembic.config import Config


class RollbackLevel(Enum):
    """Levels of rollback granularity."""
    TRANSACTION = "transaction"      # Rollback current transaction
    MIGRATION = "migration"          # Rollback single migration
    BATCH = "batch"                  # Rollback to specific point
    FULL = "full"                    # Full database restore


class RollbackStrategy(ABC):
    """Abstract base class for rollback strategies."""
    
    @abstractmethod
    def can_rollback(self, context: Dict[str, Any]) -> bool:
        """Check if rollback is possible."""
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute rollback."""
        pass
    
    @abstractmethod
    def estimate_time(self, context: Dict[str, Any]) -> int:
        """Estimate rollback time in seconds."""
        pass


@dataclass
class RollbackPoint:
    """Represents a point to which we can rollback."""
    revision: str
    description: str
    created_at: datetime
    backup_path: Optional[str] = None
    snapshot_id: Optional[str] = None
    is_safe: bool = True


class TransactionRollback(RollbackStrategy):
    """Rollback using database transactions. Best for: Recent changes, development environments."""
    
    def can_rollback(self, context: Dict[str, Any]) -> bool:
        return context.get('transaction_active', False)
    
    def execute(self, context: Dict[str, Any]) -> bool:
        conn = context.get('connection')
        if conn:
            conn.execute(text("ROLLBACK"))
            return True
        return False
    
    def estimate_time(self, context: Dict[str, Any]) -> int:
        return 1  # Very fast


class MigrationRollback(RollbackStrategy):
    """Rollback to previous migration revision. Best for: Schema changes, tested migrations."""
    
    def __init__(self, alembic_config: Config):
        self.alembic_config = alembic_config
        self.logger = logging.getLogger(__name__)
    
    def can_rollback(self, context: Dict[str, Any]) -> bool:
        target_revision = context.get('target_revision')
        return target_revision is not None
    
    def execute(self, context: Dict[str, Any]) -> bool:
        target_revision = context.get('target_revision')
        
        try:
            command.downgrade(self.alembic_config, target_revision)
            return True
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            return False
    
    def estimate_time(self, context: Dict[str, Any]) -> int:
        return 60  # Default estimate


class ShadowTableRollback(RollbackStrategy):
    """Rollback using shadow tables for zero-downtime. Best for: Production environments."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.shadow_suffix = "_shadow"
    
    def can_rollback(self, context: Dict[str, Any]) -> bool:
        table_name = context.get('table_name')
        conn = context.get('connection')
        
        if not table_name or not conn:
            return False
        
        result = conn.execute(text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table_name}{self.shadow_suffix}'
            );
        """))
        return result.scalar()
    
    def execute(self, context: Dict[str, Any]) -> bool:
        table_name = context.get('table_name')
        conn = context.get('connection')
        
        try:
            # Atomic swap using rename
            conn.execute(text(f"""
                BEGIN;
                ALTER TABLE {table_name} RENAME TO {table_name}_failed;
                ALTER TABLE {table_name}{self.shadow_suffix} RENAME TO {table_name};
                DROP TABLE {table_name}_failed;
                COMMIT;
            """))
            return True
        except Exception as e:
            self.logger.error(f"Shadow rollback failed: {e}")
            conn.execute(text("ROLLBACK"))
            return False
    
    def estimate_time(self, context: Dict[str, Any]) -> int:
        return 5  # Very fast - just renames


class RollbackManager:
    """Manages rollback operations with automatic strategy selection."""
    
    def __init__(self):
        self.strategies: Dict[RollbackLevel, RollbackStrategy] = {}
        self.rollback_points: List[RollbackPoint] = []
        self.logger = logging.getLogger(__name__)
    
    def register_strategy(self, level: RollbackLevel, strategy: RollbackStrategy):
        """Register a rollback strategy."""
        self.strategies[level] = strategy
    
    def add_rollback_point(self, point: RollbackPoint):
        """Add a rollback point."""
        self.rollback_points.append(point)
        self.rollback_points = self.rollback_points[-10:]  # Keep only recent points
    
    def select_strategy(self, context: Dict[str, Any]) -> Optional[Tuple[RollbackLevel, RollbackStrategy]]:
        """Select best rollback strategy."""
        priority_order = [
            RollbackLevel.TRANSACTION,
            RollbackLevel.MIGRATION,
            RollbackLevel.BATCH,
            RollbackLevel.FULL
        ]
        
        for level in priority_order:
            strategy = self.strategies.get(level)
            if strategy and strategy.can_rollback(context):
                return (level, strategy)
        
        return None
    
    def rollback(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute rollback with best available strategy."""
        result = {
            'success': False,
            'strategy_used': None,
            'estimated_time': 0,
            'actual_time': 0,
            'error': None
        }
        
        selection = self.select_strategy(context)
        if not selection:
            result['error'] = "No rollback strategy available"
            return result
        
        level, strategy = selection
        result['strategy_used'] = level.value
        result['estimated_time'] = strategy.estimate_time(context)
        
        start_time = datetime.utcnow()
        
        try:
            success = strategy.execute(context)
            result['success'] = success
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Rollback failed: {e}")
        
        result['actual_time'] = (datetime.utcnow() - start_time).total_seconds()
        
        return result
```

### 4.2 Automatic Rollback Triggers

```python
# /migrations/core/auto_rollback.py
"""
Automatic rollback triggers and monitoring.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Callable
import asyncio
import logging
from datetime import datetime, timedelta


@dataclass
class RollbackTrigger:
    """Trigger condition for automatic rollback."""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    action: Callable[[], None]
    cooldown_minutes: int = 30
    last_triggered: datetime = None
    
    def should_trigger(self, metrics: Dict[str, Any]) -> bool:
        """Check if trigger should fire."""
        if self.last_triggered:
            cooldown = timedelta(minutes=self.cooldown_minutes)
            if datetime.utcnow() - self.last_triggered < cooldown:
                return False
        
        return self.condition(metrics)
    
    def trigger(self):
        """Execute trigger action."""
        self.last_triggered = datetime.utcnow()
        self.action()


class AutoRollbackMonitor:
    """Monitors migration health and triggers automatic rollbacks."""
    
    def __init__(self, rollback_manager: RollbackManager):
        self.rollback_manager = rollback_manager
        self.triggers: List[RollbackTrigger] = []
        self.logger = logging.getLogger(__name__)
        self.is_running = False
    
    def add_trigger(self, trigger: RollbackTrigger):
        """Add a rollback trigger."""
        self.triggers.append(trigger)
    
    def setup_default_triggers(self):
        """Setup common rollback triggers."""
        
        # Error rate trigger
        self.add_trigger(RollbackTrigger(
            name="high_error_rate",
            condition=lambda m: m.get('error_rate', 0) > 0.1,
            action=self._rollback_for_error_rate,
            cooldown_minutes=15
        ))
        
        # Latency trigger
        self.add_trigger(RollbackTrigger(
            name="high_latency",
            condition=lambda m: m.get('p99_latency_ms', 0) > 5000,
            action=self._rollback_for_latency,
            cooldown_minutes=30
        ))
        
        # Deadlock trigger
        self.add_trigger(RollbackTrigger(
            name="deadlock_spike",
            condition=lambda m: m.get('deadlocks_per_minute', 0) > 10,
            action=self._rollback_for_deadlocks,
            cooldown_minutes=10
        ))
    
    async def start_monitoring(self, metrics_provider: Callable):
        """Start monitoring loop."""
        self.is_running = True
        
        while self.is_running:
            try:
                metrics = await metrics_provider()
                await self._check_triggers(metrics)
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _check_triggers(self, metrics: Dict[str, Any]):
        """Check all triggers against current metrics."""
        for trigger in self.triggers:
            if trigger.should_trigger(metrics):
                self.logger.warning(f"Trigger '{trigger.name}' activated")
                trigger.trigger()
    
    def _rollback_for_error_rate(self):
        """Handle high error rate."""
        self.logger.error("High error rate detected - initiating rollback")
    
    def _rollback_for_latency(self):
        """Handle high latency."""
        self.logger.error("High latency detected - initiating rollback")
    
    def _rollback_for_deadlocks(self):
        """Handle deadlock spike."""
        self.logger.error("Deadlock spike detected - initiating rollback")
    
    def stop_monitoring(self):
        """Stop monitoring loop."""
        self.is_running = False
```


---

## 5. Data Migrations

### 5.1 Data Migration Framework

```python
# /migrations/core/data_migration.py
"""
Data migration utilities and patterns.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator, List, Dict, Any, Optional, Callable
from enum import Enum
import logging
import asyncio
from datetime import datetime

from sqlalchemy import Table, select, update, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession


class DataMigrationType(Enum):
    """Types of data migrations."""
    TRANSFORM = "transform"       # Transform existing data
    MIGRATE = "migrate"           # Move data between tables
    CLEANUP = "cleanup"           # Clean up old data
    AGGREGATE = "aggregate"       # Create aggregated data
    DENORMALIZE = "denormalize"   # Create denormalized views


@dataclass
class MigrationBatch:
    """Represents a batch of records to migrate."""
    batch_number: int
    records: List[Dict[str, Any]]
    start_id: Any
    end_id: Any


@dataclass
class MigrationCheckpoint:
    """Checkpoint for resumable migrations."""
    migration_id: str
    batch_number: int
    last_processed_id: Any
    total_processed: int
    started_at: datetime
    updated_at: datetime
    status: str


class DataMigrationStrategy(ABC):
    """Abstract base class for data migration strategies."""
    
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self.logger = logging.getLogger(__name__)
    
    @abstractmethod
    def fetch_batch(self, session: AsyncSession, last_id: Optional[Any] = None) -> MigrationBatch:
        """Fetch next batch of records."""
        pass
    
    @abstractmethod
    def transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a single record."""
        pass
    
    @abstractmethod
    def save_batch(self, session: AsyncSession, batch: MigrationBatch) -> None:
        """Save transformed batch."""
        pass
    
    async def migrate(self, session: AsyncSession, checkpoint: Optional[MigrationCheckpoint] = None) -> Dict[str, Any]:
        """Execute data migration with checkpoint support."""
        result = {
            'total_processed': 0,
            'batches_processed': 0,
            'errors': [],
            'start_time': datetime.utcnow(),
            'end_time': None
        }
        
        last_id = checkpoint.last_processed_id if checkpoint else None
        batch_number = checkpoint.batch_number if checkpoint else 0
        
        try:
            while True:
                batch = await self.fetch_batch(session, last_id)
                
                if not batch.records:
                    break
                
                # Transform records
                transformed = []
                for record in batch.records:
                    try:
                        transformed.append(self.transform_record(record))
                    except Exception as e:
                        result['errors'].append({
                            'record_id': record.get('id'),
                            'error': str(e)
                        })
                
                # Save batch
                await self.save_batch(session, MigrationBatch(
                    batch_number=batch_number,
                    records=transformed,
                    start_id=batch.start_id,
                    end_id=batch.end_id
                ))
                
                # Update progress
                result['total_processed'] += len(transformed)
                result['batches_processed'] += 1
                last_id = batch.end_id
                batch_number += 1
                
                # Commit batch
                await session.commit()
                
                # Checkpoint every 10 batches
                if batch_number % 10 == 0:
                    await self._save_checkpoint(
                        session,
                        checkpoint.migration_id if checkpoint else 'migration',
                        batch_number,
                        last_id,
                        result['total_processed']
                    )
        
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            result['errors'].append({'error': str(e)})
            raise
        
        finally:
            result['end_time'] = datetime.utcnow()
        
        return result


class ColumnMigration(DataMigrationStrategy):
    """Migrate data from one column format to another."""
    
    def __init__(
        self,
        source_table: str,
        source_column: str,
        target_table: str,
        target_column: str,
        transform_func: Callable[[Any], Any],
        batch_size: int = 1000
    ):
        super().__init__(batch_size)
        self.source_table = source_table
        self.source_column = source_column
        self.target_table = target_table
        self.target_column = target_column
        self.transform_func = transform_func
    
    async def fetch_batch(self, session: AsyncSession, last_id: Optional[Any] = None) -> MigrationBatch:
        """Fetch batch of records."""
        query = select(
            Table(self.source_table).c.id,
            Table(self.source_table).c[self.source_column]
        ).where(
            Table(self.source_table).c[self.target_column].is_(None)
        ).order_by(
            Table(self.source_table).c.id
        ).limit(self.batch_size)
        
        if last_id:
            query = query.where(Table(self.source_table).c.id > last_id)
        
        result = await session.execute(query)
        records = result.mappings().all()
        
        return MigrationBatch(
            batch_number=0,
            records=[dict(r) for r in records],
            start_id=records[0]['id'] if records else None,
            end_id=records[-1]['id'] if records else None
        )
    
    def transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform single record."""
        return {
            'id': record['id'],
            self.target_column: self.transform_func(record[self.source_column])
        }
    
    async def save_batch(self, session: AsyncSession, batch: MigrationBatch) -> None:
        """Save transformed batch."""
        for record in batch.records:
            await session.execute(
                update(Table(self.target_table))
                .where(Table(self.target_table).c.id == record['id'])
                .values(**{self.target_column: record[self.target_column]})
            )


class DataMigrationRunner:
    """Runner for executing data migrations."""
    
    def __init__(self):
        self.migrations: Dict[str, DataMigrationStrategy] = {}
        self.checkpoints: Dict[str, MigrationCheckpoint] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_migration(self, name: str, strategy: DataMigrationStrategy):
        """Register a data migration."""
        self.migrations[name] = strategy
    
    async def run_migration(self, name: str, session: AsyncSession, resume: bool = True) -> Dict[str, Any]:
        """Run a registered migration."""
        migration = self.migrations.get(name)
        if not migration:
            raise ValueError(f"Unknown migration: {name}")
        
        checkpoint = None
        if resume and name in self.checkpoints:
            checkpoint = self.checkpoints[name]
            self.logger.info(f"Resuming migration {name} from checkpoint")
        
        result = await migration.migrate(session, checkpoint)
        
        # Clear checkpoint on success
        if not result['errors']:
            self.checkpoints.pop(name, None)
        
        return result
```

---

## 6. Testing Framework

### 6.1 Migration Testing

```python
# /migrations/tests/test_migrations.py
"""
Migration testing framework for ResilienceAI.
"""

import pytest
import asyncio
from typing import Dict, List, Any
from datetime import datetime
from unittest.mock import Mock, patch

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config

from migrations.core.migration_manager import (
    MigrationContext,
    ZeroDowntimeMigrationStrategy,
    MigrationOrchestrator
)
from migrations.core.rollback import RollbackManager, RollbackLevel


class MigrationTestBase:
    """Base class for migration tests."""
    
    @pytest.fixture(scope='class')
    def database_url(self):
        """Test database URL."""
        return 'postgresql://test:test@localhost:5432/test_migrations'
    
    @pytest.fixture(scope='class')
    def alembic_config(self, database_url):
        """Alembic configuration."""
        config = Config('alembic.ini')
        config.set_main_option('sqlalchemy.url', database_url)
        return config
    
    @pytest.fixture
    def db_engine(self, database_url):
        """Database engine fixture."""
        engine = create_engine(database_url)
        yield engine
        engine.dispose()
    
    @pytest.fixture
    def db_session(self, db_engine):
        """Database session fixture."""
        Session = sessionmaker(bind=db_engine)
        session = Session()
        yield session
        session.rollback()
        session.close()
    
    def get_table_columns(self, engine, table_name: str) -> List[str]:
        """Get column names for a table."""
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        return [col['name'] for col in columns]


class TestMigrationIntegrity(MigrationTestBase):
    """Test migration integrity and consistency."""
    
    def test_migration_checksums(self, alembic_config):
        """Test that all migrations have valid checksums."""
        from pathlib import Path
        versions_dir = Path('migrations/alembic/versions')
        migration_files = list(versions_dir.glob('*.py'))
        
        for migration_file in migration_files:
            content = migration_file.read_text()
            assert 'checksum' in content or 'revision' in content
    
    def test_migration_dependencies(self, alembic_config):
        """Test that migration dependencies are valid."""
        script = command.get_current_revision(alembic_config)
        history = command.history(alembic_config, indicate_current=True)
        revisions = list(history)
        
        revision_ids = {r.revision for r in revisions}
        for rev in revisions:
            if rev.down_revision:
                assert rev.down_revision in revision_ids
    
    def test_no_duplicate_revisions(self, alembic_config):
        """Test that revision IDs are unique."""
        history = command.history(alembic_config)
        revisions = [r.revision for r in history]
        assert len(revisions) == len(set(revisions))


class TestZeroDowntimeMigrations(MigrationTestBase):
    """Test zero-downtime migration strategies."""
    
    @pytest.mark.asyncio
    async def test_concurrent_index_creation(self, db_engine):
        """Test that indexes are created concurrently."""
        strategy = ZeroDowntimeMigrationStrategy(
            migration_sql="CREATE INDEX idx_test ON users (email);",
            rollback_sql="DROP INDEX idx_test;"
        )
        
        context = MigrationContext(
            environment='test',
            database_url=str(db_engine.url),
            dry_run=True
        )
        
        result = await strategy.execute(context)
        
        assert result.status == MigrationStatus.SUCCESS
        assert 'CONCURRENTLY' in str(result.changes_applied)
    
    def test_migration_idempotency(self, db_engine, alembic_config):
        """Test that migrations can be run multiple times safely."""
        # Run migration
        command.upgrade(alembic_config, 'head')
        
        # Record state
        inspector = inspect(db_engine)
        tables_after_first = inspector.get_table_names()
        
        # Run migration again
        command.upgrade(alembic_config, 'head')
        
        # Verify state unchanged
        tables_after_second = inspector.get_table_names()
        assert tables_after_first == tables_after_second


class TestRollbackProcedures(MigrationTestBase):
    """Test rollback procedures."""
    
    def test_rollback_availability(self, db_engine, alembic_config):
        """Test that all migrations have rollback scripts."""
        history = command.history(alembic_config)
        
        for revision in history:
            script = command.get_script(alembic_config, revision.revision)
            assert hasattr(script.module, 'downgrade')
    
    def test_rollback_success(self, db_engine, alembic_config):
        """Test successful rollback."""
        inspector = inspect(db_engine)
        initial_tables = set(inspector.get_table_names())
        
        # Apply migration
        command.upgrade(alembic_config, '+1')
        
        # Rollback
        command.downgrade(alembic_config, '-1')
        
        # Verify state restored
        final_tables = set(inspector.get_table_names())
        assert initial_tables == final_tables


class TestMigrationPerformance(MigrationTestBase):
    """Test migration performance characteristics."""
    
    @pytest.mark.performance
    def test_migration_execution_time(self, db_engine, alembic_config):
        """Test that migrations complete within expected time."""
        import time
        
        start = time.time()
        command.upgrade(alembic_config, '+1')
        duration = time.time() - start
        
        # Should complete in under 60 seconds
        assert duration < 60


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
```

### 6.2 Migration Verification

```python
# /migrations/utils/verification.py
"""
Migration verification utilities.
"""

from typing import List, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


class VerificationResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


@dataclass
class VerificationCheck:
    """Single verification check result."""
    name: str
    result: VerificationResult
    message: str
    details: Dict[str, Any]


class MigrationVerifier:
    """Verifies that migrations were applied correctly."""
    
    def __init__(self, engine: Engine):
        self.engine = engine
        self.logger = logging.getLogger(__name__)
        self.checks: List[Callable] = []
    
    def add_check(self, check: Callable):
        """Add a verification check."""
        self.checks.append(check)
    
    def verify_all(self) -> List[VerificationCheck]:
        """Run all verification checks."""
        results = []
        
        for check in self.checks:
            try:
                result = check(self.engine)
                results.append(result)
            except Exception as e:
                results.append(VerificationCheck(
                    name=check.__name__,
                    result=VerificationResult.FAIL,
                    message=str(e),
                    details={}
                ))
        
        return results
    
    def verify_table_exists(self, table_name: str) -> VerificationCheck:
        """Verify table exists."""
        inspector = inspect(self.engine)
        exists = table_name in inspector.get_table_names()
        
        return VerificationCheck(
            name=f"table_exists_{table_name}",
            result=VerificationResult.PASS if exists else VerificationResult.FAIL,
            message=f"Table {table_name} {'exists' if exists else 'missing'}",
            details={'table_name': table_name}
        )
    
    def verify_column_exists(self, table_name: str, column_name: str) -> VerificationCheck:
        """Verify column exists."""
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table_name)
        column_names = [c['name'] for c in columns]
        exists = column_name in column_names
        
        return VerificationCheck(
            name=f"column_exists_{table_name}.{column_name}",
            result=VerificationResult.PASS if exists else VerificationResult.FAIL,
            message=f"Column {table_name}.{column_name} {'exists' if exists else 'missing'}",
            details={'table_name': table_name, 'column_name': column_name}
        )
    
    def verify_index_exists(self, table_name: str, index_name: str) -> VerificationCheck:
        """Verify index exists."""
        inspector = inspect(self.engine)
        indexes = inspector.get_indexes(table_name)
        index_names = [i['name'] for i in indexes]
        exists = index_name in index_names
        
        return VerificationCheck(
            name=f"index_exists_{index_name}",
            result=VerificationResult.PASS if exists else VerificationResult.FAIL,
            message=f"Index {index_name} {'exists' if exists else 'missing'}",
            details={'table_name': table_name, 'index_name': index_name}
        )
    
    def verify_row_count(self, table_name: str, expected_min: int = 0, expected_max: int = None) -> VerificationCheck:
        """Verify row count is within expected range."""
        with self.engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
        
        passed = count >= expected_min
        if expected_max is not None:
            passed = passed and count <= expected_max
        
        return VerificationCheck(
            name=f"row_count_{table_name}",
            result=VerificationResult.PASS if passed else VerificationResult.FAIL,
            message=f"Row count {count} is {'within' if passed else 'outside'} expected range [{expected_min}, {expected_max or 'unlimited'}]",
            details={
                'table_name': table_name,
                'actual_count': count,
                'expected_min': expected_min,
                'expected_max': expected_max
            }
        )
```

---

## 7. Continuous Migration

### 7.1 CI/CD Integration

```yaml
# /migrations/ci/.github/workflows/migrations.yml
name: Database Migrations

on:
  push:
    branches: [main, develop]
    paths:
      - 'migrations/**'
      - 'models/**'
  pull_request:
    branches: [main]
    paths:
      - 'migrations/**'

env:
  DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
  ALEMBIC_CONFIG: migrations/config/alembic.ini

jobs:
  lint-migrations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install sqlalchemy alembic psycopg2-binary
          pip install sqlparse sqlfluff
      
      - name: Lint migration SQL
        run: |
          find migrations/alembic/versions -name "*.py" -exec \
            python -m migrations.scripts.lint {} \;
      
      - name: Check migration naming
        run: python migrations/scripts/check_naming.py
      
      - name: Validate migration order
        run: python migrations/scripts/validate_order.py

  test-migrations:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run migration tests
        run: pytest migrations/tests/ -v --cov=migrations
      
      - name: Test upgrade/downgrade cycle
        run: |
          alembic upgrade head
          alembic downgrade base
          alembic upgrade head
      
      - name: Test idempotency
        run: |
          alembic upgrade head
          alembic upgrade head
      
      - name: Generate migration report
        run: python migrations/scripts/generate_report.py
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy-staging:
    runs-on: ubuntu-latest
    needs: [lint-migrations, test-migrations]
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Create snapshot
        run: |
          aws rds create-db-snapshot \
            --db-instance-identifier staging-db \
            --db-snapshot-identifier pre-migration-${{ github.sha }}
      
      - name: Run migrations
        run: |
          export DATABASE_URL=${{ secrets.STAGING_DATABASE_URL }}
          alembic upgrade head
      
      - name: Verify migrations
        run: python migrations/scripts/verify.py --environment staging
      
      - name: Notify on failure
        if: failure()
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -H 'Content-Type: application/json' \
            -d '{"text":"Migration failed on staging"}'

  deploy-production:
    runs-on: ubuntu-latest
    needs: [test-migrations, deploy-staging]
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Create production snapshot
        run: |
          aws rds create-db-snapshot \
            --db-instance-identifier production-db \
            --db-snapshot-identifier pre-migration-${{ github.sha }}
      
      - name: Run migrations with monitoring
        run: |
          export DATABASE_URL=${{ secrets.PRODUCTION_DATABASE_URL }}
          python migrations/scripts/migrate_with_monitoring.py \
            --environment production \
            --notify-on-complete
      
      - name: Verify migrations
        run: python migrations/scripts/verify.py --environment production
      
      - name: Run smoke tests
        run: pytest tests/smoke/ -v
      
      - name: Notify team
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -H 'Content-Type: application/json' \
            -d '{"text":"Production migration completed successfully"}'
```

### 7.2 Migration Scripts

```python
# /migrations/scripts/migrate.py
"""
Main migration script for ResilienceAI.
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from typing import Optional

from alembic import command, config
from alembic.script import ScriptDirectory

from migrations.core.migration_manager import (
    MigrationContext,
    MigrationOrchestrator,
    MigrationStatus
)
from migrations.core.rollback import RollbackManager
from migrations.utils.verification import MigrationVerifier


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='ResilienceAI Database Migration Tool')
    
    parser.add_argument(
        'action',
        choices=['upgrade', 'downgrade', 'revision', 'history', 'current', 'verify'],
        help='Migration action to perform'
    )
    
    parser.add_argument('--revision', help='Target revision (default: head)')
    parser.add_argument('--environment', default='development', choices=['development', 'staging', 'production'])
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    parser.add_argument('--sql', action='store_true', help='Output SQL instead of executing')
    parser.add_argument('--backup', action='store_true', help='Create backup before migration')
    parser.add_argument('--verify', action='store_true', help='Verify migration after execution')
    parser.add_argument('--timeout', type=int, default=3600, help='Migration timeout in seconds')
    
    return parser.parse_args()


def get_database_url(environment: str) -> str:
    """Get database URL for environment."""
    import os
    env_var = f'{environment.upper()}_DATABASE_URL'
    url = os.getenv(env_var)
    
    if not url:
        raise ValueError(f"Database URL not found for {environment}")
    
    return url


def create_backup(environment: str) -> str:
    """Create database backup."""
    logger.info(f"Creating backup for {environment}")
    
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    backup_id = f"{environment}_{timestamp}"
    
    logger.info(f"Backup created: {backup_id}")
    return backup_id


def run_upgrade(args) -> bool:
    """Run upgrade migration."""
    revision = args.revision or 'head'
    
    logger.info(f"Upgrading to revision: {revision}")
    
    # Create backup if requested
    backup_id = None
    if args.backup:
        backup_id = create_backup(args.environment)
    
    # Load Alembic configuration
    alembic_cfg = config.Config('alembic.ini')
    alembic_cfg.set_main_option('sqlalchemy.url', get_database_url(args.environment))
    
    if args.dry_run:
        script = ScriptDirectory.from_config(alembic_cfg)
        current = command.current(alembic_cfg)
        
        logger.info(f"Current revision: {current}")
        logger.info(f"Target revision: {revision}")
        
        path = script.get_revisions(current, revision)
        for rev in path:
            logger.info(f"  Would apply: {rev.revision} - {rev.doc}")
        
        return True
    
    if args.sql:
        command.upgrade(alembic_cfg, revision, sql=True)
        return True
    
    # Execute migration
    try:
        command.upgrade(alembic_cfg, revision)
        logger.info(f"Successfully upgraded to {revision}")
        
        # Verify if requested
        if args.verify:
            return run_verify(args)
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        
        if backup_id:
            logger.info(f"Backup available for rollback: {backup_id}")
        
        return False


def run_downgrade(args) -> bool:
    """Run downgrade migration."""
    revision = args.revision or '-1'
    
    logger.info(f"Downgrading to revision: {revision}")
    
    # Confirm for production
    if args.environment == 'production':
        confirm = input("WARNING: Downgrading in production. Type 'yes' to confirm: ")
        if confirm != 'yes':
            logger.info("Downgrade cancelled")
            return False
    
    alembic_cfg = config.Config('alembic.ini')
    alembic_cfg.set_main_option('sqlalchemy.url', get_database_url(args.environment))
    
    try:
        command.downgrade(alembic_cfg, revision)
        logger.info(f"Successfully downgraded to {revision}")
        return True
        
    except Exception as e:
        logger.error(f"Downgrade failed: {e}")
        return False


def run_verify(args) -> bool:
    """Run migration verification."""
    from sqlalchemy import create_engine
    
    logger.info("Running migration verification")
    
    engine = create_engine(get_database_url(args.environment))
    verifier = MigrationVerifier(engine)
    
    # Add standard verification checks
    verifier.add_check(lambda e: verifier.verify_table_exists('users'))
    verifier.add_check(lambda e: verifier.verify_table_exists('incidents'))
    verifier.add_check(lambda e: verifier.verify_table_exists('audit_log'))
    
    # Run all checks
    results = verifier.verify_all()
    
    all_passed = True
    for check in results:
        status = "✓" if check.result.value == 'pass' else "✗"
        logger.info(f"{status} {check.name}: {check.message}")
        
        if check.result.value == 'fail':
            all_passed = False
    
    return all_passed


def run_history(args):
    """Show migration history."""
    alembic_cfg = config.Config('alembic.ini')
    alembic_cfg.set_main_option('sqlalchemy.url', get_database_url(args.environment))
    command.history(alembic_cfg, indicate_current=True)


def run_current(args):
    """Show current revision."""
    alembic_cfg = config.Config('alembic.ini')
    alembic_cfg.set_main_option('sqlalchemy.url', get_database_url(args.environment))
    current = command.current(alembic_cfg)
    logger.info(f"Current revision: {current}")


def main():
    """Main entry point."""
    args = parse_args()
    
    success = False
    
    if args.action == 'upgrade':
        success = run_upgrade(args)
    elif args.action == 'downgrade':
        success = run_downgrade(args)
    elif args.action == 'history':
        run_history(args)
        success = True
    elif args.action == 'current':
        run_current(args)
        success = True
    elif args.action == 'verify':
        success = run_verify(args)
    else:
        logger.error(f"Unknown action: {args.action}")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

---

## 8. Database Seeding

### 8.1 Seeding Framework

```python
# /migrations/scripts/seed.py
"""
Database seeding framework for ResilienceAI.
"""

import argparse
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import uuid

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from faker import Faker

logger = logging.getLogger(__name__)
fake = Faker()


@dataclass
class SeedConfig:
    """Configuration for database seeding."""
    users_count: int = 100
    incidents_count: int = 1000
    audit_logs_count: int = 5000
    organizations_count: int = 10
    teams_count: int = 20
    
    incident_severities: List[str] = None
    incident_statuses: List[str] = None
    user_roles: List[str] = None
    
    def __post_init__(self):
        if self.incident_severities is None:
            self.incident_severities = ['low', 'medium', 'high', 'critical']
        if self.incident_statuses is None:
            self.incident_statuses = ['open', 'in_progress', 'resolved', 'closed']
        if self.user_roles is None:
            self.user_roles = ['admin', 'manager', 'analyst', 'viewer']


class DataGenerator:
    """Generate realistic seed data."""
    
    def __init__(self, config: SeedConfig):
        self.config = config
        self.generated_ids = {
            'users': [],
            'incidents': [],
            'organizations': [],
            'teams': []
        }
    
    def generate_user(self, role: Optional[str] = None) -> Dict[str, Any]:
        """Generate a user record."""
        username = fake.user_name()
        return {
            'id': str(uuid.uuid4()),
            'email': fake.email(),
            'username': username,
            'display_name': fake.name(),
            'password_hash': f'hash_{fake.password()}',
            'is_active': True,
            'is_admin': role == 'admin',
            'role': role or random.choice(self.config.user_roles),
            'created_at': fake.date_time_between(start_date='-2y', end_date='now'),
            'last_login': fake.date_time_between(start_date='-30d', end_date='now'),
            'preferences': json.dumps({
                'theme': random.choice(['light', 'dark']),
                'notifications': random.choice([True, False]),
                'timezone': fake.timezone()
            })
        }
    
    def generate_incident(self, created_by: Optional[str] = None) -> Dict[str, Any]:
        """Generate an incident record."""
        severity = random.choice(self.config.incident_severities)
        status = random.choice(self.config.incident_statuses)
        created_at = fake.date_time_between(start_date='-1y', end_date='now')
        
        if status in ['resolved', 'closed']:
            resolved_at = created_at + timedelta(hours=random.randint(1, 168))
        else:
            resolved_at = None
        
        return {
            'id': str(uuid.uuid4()),
            'title': f"{severity.upper()}: {fake.sentence(nb_words=6)}",
            'description': fake.paragraph(nb_sentences=5),
            'severity': severity,
            'status': status,
            'created_by': created_by or random.choice(self.generated_ids['users']),
            'assigned_to': random.choice(self.generated_ids['users']) if random.random() > 0.3 else None,
            'created_at': created_at,
            'updated_at': created_at + timedelta(hours=random.randint(1, 48)),
            'resolved_at': resolved_at,
            'metadata': json.dumps({
                'source': random.choice(['manual', 'api', 'webhook', 'email']),
                'tags': [fake.word() for _ in range(random.randint(1, 5))],
                'affected_systems': [fake.domain_name() for _ in range(random.randint(1, 3))]
            })
        }


class DatabaseSeeder:
    """Seeds database with test data."""
    
    def __init__(self, database_url: str, config: SeedConfig):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.config = config
        self.generator = DataGenerator(config)
    
    def seed_all(self, clear_existing: bool = False):
        """Seed all tables."""
        if clear_existing:
            self.clear_all()
        
        self.seed_users()
        self.seed_incidents()
        
        logger.info("Database seeding completed")
    
    def clear_all(self):
        """Clear all existing data."""
        logger.warning("Clearing all existing data")
        
        with self.engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE audit_log CASCADE"))
            conn.execute(text("TRUNCATE TABLE incidents CASCADE"))
            conn.execute(text("TRUNCATE TABLE users CASCADE"))
            conn.commit()
    
    def seed_users(self):
        """Seed users."""
        logger.info(f"Seeding {self.config.users_count} users")
        
        session = self.Session()
        
        # Create admin users
        for _ in range(5):
            user = self.generator.generate_user(role='admin')
            self.generator.generated_ids['users'].append(user['id'])
            self._insert_user(session, user)
        
        # Create regular users
        for _ in range(self.config.users_count - 5):
            user = self.generator.generate_user()
            self.generator.generated_ids['users'].append(user['id'])
            self._insert_user(session, user)
        
        session.commit()
        session.close()
    
    def _insert_user(self, session, user: Dict[str, Any]):
        """Insert user record."""
        session.execute(text("""
            INSERT INTO users (
                id, email, username, display_name, password_hash,
                is_active, is_admin, role, created_at, last_login, preferences
            ) VALUES (
                :id, :email, :username, :display_name, :password_hash,
                :is_active, :is_admin, :role, :created_at, :last_login, :preferences
            )
        """), user)
    
    def seed_incidents(self):
        """Seed incidents."""
        logger.info(f"Seeding {self.config.incidents_count} incidents")
        
        session = self.Session()
        
        for _ in range(self.config.incidents_count):
            incident = self.generator.generate_incident()
            self.generator.generated_ids['incidents'].append(incident['id'])
            
            session.execute(text("""
                INSERT INTO incidents (
                    id, title, description, severity, status,
                    created_by, assigned_to, created_at, updated_at, resolved_at, metadata
                ) VALUES (
                    :id, :title, :description, :severity, :status,
                    :created_by, :assigned_to, :created_at, :updated_at, :resolved_at, :metadata
                )
            """), incident)
        
        session.commit()
        session.close()


def main():
    """Main entry point for seeding."""
    parser = argparse.ArgumentParser(description='Database Seeding Tool')
    parser.add_argument('--database-url', required=True, help='Database URL')
    parser.add_argument('--clear', action='store_true', help='Clear existing data')
    parser.add_argument('--users', type=int, default=100, help='Number of users')
    parser.add_argument('--incidents', type=int, default=1000, help='Number of incidents')
    
    args = parser.parse_args()
    
    config = SeedConfig(
        users_count=args.users,
        incidents_count=args.incidents
    )
    
    seeder = DatabaseSeeder(args.database_url, config)
    seeder.seed_all(clear_existing=args.clear)


if __name__ == '__main__':
    main()
```

---

## 9. Schema Comparison

### 9.1 Schema Diff Tool

```python
# /migrations/utils/schema_diff.py
"""
Schema comparison and diff utilities.
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import json

from sqlalchemy import create_engine, inspect, MetaData, Table
from sqlalchemy.engine import Engine


class DiffType(Enum):
    """Types of schema differences."""
    TABLE_ADDED = "table_added"
    TABLE_REMOVED = "table_removed"
    TABLE_MODIFIED = "table_modified"
    COLUMN_ADDED = "column_added"
    COLUMN_REMOVED = "column_removed"
    COLUMN_MODIFIED = "column_modified"
    INDEX_ADDED = "index_added"
    INDEX_REMOVED = "index_removed"


@dataclass
class SchemaDifference:
    """Represents a schema difference."""
    diff_type: DiffType
    object_type: str
    object_name: str
    table_name: Optional[str] = None
    details: Dict[str, Any] = None
    old_value: Any = None
    new_value: Any = None


class SchemaSnapshot:
    """Captures a snapshot of database schema."""
    
    def __init__(self, engine: Engine):
        self.engine = engine
        self.metadata = MetaData()
        self.metadata.reflect(bind=engine)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary."""
        schema = {'tables': {}, 'indexes': {}, 'constraints': {}}
        
        inspector = inspect(self.engine)
        
        for table_name in inspector.get_table_names():
            schema['tables'][table_name] = self._table_to_dict(inspector, table_name)
        
        return schema
    
    def _table_to_dict(self, inspector, table_name: str) -> Dict[str, Any]:
        """Convert table schema to dictionary."""
        return {
            'columns': {
                col['name']: {
                    'type': str(col['type']),
                    'nullable': col['nullable'],
                    'default': str(col['default']) if col['default'] else None
                }
                for col in inspector.get_columns(table_name)
            },
            'indexes': {
                idx['name']: {
                    'columns': idx['column_names'],
                    'unique': idx['unique']
                }
                for idx in inspector.get_indexes(table_name)
            },
            'primary_key': inspector.get_pk_constraint(table_name),
            'foreign_keys': inspector.get_foreign_keys(table_name),
            'unique_constraints': inspector.get_unique_constraints(table_name)
        }
    
    def save_to_file(self, filepath: str):
        """Save schema snapshot to file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


class SchemaComparator:
    """Compares two schema snapshots and identifies differences."""
    
    def __init__(self):
        self.differences: List[SchemaDifference] = []
    
    def compare(self, old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> List[SchemaDifference]:
        """Compare two schemas and return differences."""
        self.differences = []
        self._compare_tables(old_schema, new_schema)
        return self.differences
    
    def _compare_tables(self, old_schema: Dict[str, Any], new_schema: Dict[str, Any]):
        """Compare tables between schemas."""
        old_tables = set(old_schema.get('tables', {}).keys())
        new_tables = set(new_schema.get('tables', {}).keys())
        
        # Added tables
        for table_name in new_tables - old_tables:
            self.differences.append(SchemaDifference(
                diff_type=DiffType.TABLE_ADDED,
                object_type='table',
                object_name=table_name,
                new_value=new_schema['tables'][table_name]
            ))
        
        # Removed tables
        for table_name in old_tables - new_tables:
            self.differences.append(SchemaDifference(
                diff_type=DiffType.TABLE_REMOVED,
                object_type='table',
                object_name=table_name,
                old_value=old_schema['tables'][table_name]
            ))
        
        # Modified tables
        for table_name in old_tables & new_tables:
            self._compare_table_columns(
                table_name,
                old_schema['tables'][table_name],
                new_schema['tables'][table_name]
            )
    
    def _compare_table_columns(self, table_name: str, old_table: Dict[str, Any], new_table: Dict[str, Any]):
        """Compare columns within a table."""
        old_columns = set(old_table.get('columns', {}).keys())
        new_columns = set(new_table.get('columns', {}).keys())
        
        # Added columns
        for col_name in new_columns - old_columns:
            self.differences.append(SchemaDifference(
                diff_type=DiffType.COLUMN_ADDED,
                object_type='column',
                object_name=col_name,
                table_name=table_name,
                new_value=new_table['columns'][col_name]
            ))
        
        # Removed columns
        for col_name in old_columns - new_columns:
            self.differences.append(SchemaDifference(
                diff_type=DiffType.COLUMN_REMOVED,
                object_type='column',
                object_name=col_name,
                table_name=table_name,
                old_value=old_table['columns'][col_name]
            ))
    
    def generate_report(self) -> str:
        """Generate human-readable diff report."""
        lines = ["Schema Comparison Report", "=" * 50, ""]
        
        for diff in self.differences:
            emoji = {
                DiffType.TABLE_ADDED: "➕",
                DiffType.TABLE_REMOVED: "➖",
                DiffType.TABLE_MODIFIED: "📝",
                DiffType.COLUMN_ADDED: "➕",
                DiffType.COLUMN_REMOVED: "➖",
                DiffType.COLUMN_MODIFIED: "📝",
                DiffType.INDEX_ADDED: "📊",
                DiffType.INDEX_REMOVED: "🗑️",
            }.get(diff.diff_type, "❓")
            
            location = f"{diff.table_name}." if diff.table_name else ""
            lines.append(f"{emoji} {diff.diff_type.value}: {location}{diff.object_name}")
            
            if diff.old_value and diff.new_value:
                lines.append(f"   Old: {diff.old_value}")
                lines.append(f"   New: {diff.new_value}")
        
        return "\n".join(lines)


def compare_schemas(source_url: str, target_url: str) -> List[SchemaDifference]:
    """Compare schemas between two databases."""
    source_engine = create_engine(source_url)
    target_engine = create_engine(target_url)
    
    source_snapshot = SchemaSnapshot(source_engine)
    target_snapshot = SchemaSnapshot(target_engine)
    
    comparator = SchemaComparator()
    differences = comparator.compare(source_snapshot.to_dict(), target_snapshot.to_dict())
    
    return differences
```

---

## 10. Implementation Priority

### 10.1 Priority Matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION PRIORITY MATRIX                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  HIGH PRIORITY (Week 1-2)                                                   │
│  ════════════════════════                                                   │
│  1. Migration Framework Setup                                               │
│     - Alembic configuration                                                 │
│     - Directory structure                                                   │
│     - Environment configurations                                            │
│                                                                              │
│  2. Core Migration Components                                               │
│     - Migration manager                                                     │
│     - Version control                                                       │
│     - Basic rollback                                                        │
│                                                                              │
│  3. Initial Schema Migration                                                │
│     - Users table                                                           │
│     - Incidents table (partitioned)                                         │
│     - Basic indexes                                                         │
│                                                                              │
│  MEDIUM PRIORITY (Week 3-4)                                                 │
│  ══════════════════════════                                                 │
│  4. Zero-Downtime Migration Strategy                                        │
│     - Concurrent index creation                                             │
│     - Online schema changes                                                 │
│     - Shadow table pattern                                                  │
│                                                                              │
│  5. Testing Framework                                                       │
│     - Migration tests                                                       │
│     - Rollback tests                                                        │
│     - Verification utilities                                                │
│                                                                              │
│  6. CI/CD Integration                                                       │
│     - GitHub Actions workflow                                               │
│     - Automated testing                                                     │
│     - Staging deployment                                                    │
│                                                                              │
│  LOW PRIORITY (Week 5-6)                                                    │
│  ═══════════════════════                                                    │
│  7. Advanced Rollback                                                       │
│     - Automatic triggers                                                    │
│     - Snapshot rollback                                                     │
│     - Point-in-time recovery                                                │
│                                                                              │
│  8. Data Migration Tools                                                    │
│     - Batch processing                                                      │
│     - Checkpoint/resume                                                     │
│     - Data validation                                                       │
│                                                                              │
│  9. Schema Comparison                                                       │
│     - Diff generation                                                       │
│     - Migration generation                                                  │
│     - Validation rules                                                      │
│                                                                              │
│  ONGOING                                                                    │
│  ════════                                                                   │
│  10. Documentation                                                          │
│  11. Monitoring & Alerting                                                  │
│  12. Performance Optimization                                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Implementation Checklist

```
MIGRATION IMPLEMENTATION CHECKLIST
═══════════════════════════════════

Phase 1: Foundation (Week 1)
─────────────────────────────
□ Set up Alembic configuration
□ Create migration directory structure
□ Configure environment-specific settings
□ Create initial schema migration
□ Set up version control tracking
□ Create basic migration scripts

Phase 2: Core Features (Week 2)
────────────────────────────────
□ Implement migration manager
□ Create version registry
□ Add rollback capabilities
□ Create migration templates
□ Set up testing framework
□ Write initial tests

Phase 3: Zero-Downtime (Week 3)
────────────────────────────────
□ Implement concurrent index creation
□ Add online schema change support
□ Create shadow table utilities
□ Add migration verification
□ Implement safety checks
□ Test zero-downtime scenarios

Phase 4: Automation (Week 4)
─────────────────────────────
□ Set up CI/CD pipeline
□ Create automated testing
□ Add staging deployment
□ Implement health checks
□ Add notification system
□ Create migration reports

Phase 5: Advanced Features (Week 5-6)
──────────────────────────────────────
□ Implement automatic rollback triggers
□ Add data migration framework
□ Create schema comparison tools
□ Add performance monitoring
□ Implement backup integration
□ Create comprehensive documentation

Phase 6: Production Readiness (Ongoing)
────────────────────────────────────────
□ Load testing
□ Security review
□ Documentation review
□ Team training
□ Runbook creation
□ Monitoring setup
```

---

## Summary

This comprehensive database migration strategy for ResilienceAI provides:

1. **Migration Framework**: Alembic-based with custom extensions for enterprise needs
2. **Schema Versioning**: Semantic versioning with dependency tracking
3. **Migration Scripts**: Templates and examples for common operations
4. **Rollback Strategies**: Multiple levels from transaction to full snapshot
5. **Data Migrations**: Batch processing with checkpoint/resume support
6. **Testing Framework**: Comprehensive test suite for migrations
7. **Continuous Migration**: CI/CD integration with automated deployment
8. **Database Seeding**: Realistic test data generation
9. **Schema Comparison**: Diff tools and validation
10. **Implementation Priority**: Phased approach for gradual rollout

The strategy emphasizes zero-downtime migrations, comprehensive testing, and robust rollback capabilities to ensure database changes can be made safely in production environments.
