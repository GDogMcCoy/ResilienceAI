# ResilienceAI Configuration Management Architecture

## Executive Summary

This document provides a comprehensive configuration management architecture for ResilienceAI, covering environment-based configuration, secrets management, feature flags, validation, hot reloading, and security measures. The design follows industry best practices for cloud-native applications with a focus on security, scalability, and operational excellence.

---

## Table of Contents

1. [Configuration Architecture Overview](#1-configuration-architecture-overview)
2. [Configuration Hierarchy](#2-configuration-hierarchy)
3. [Environment-Based Configuration](#3-environment-based-configuration)
4. [Secrets Management](#4-secrets-management)
5. [Feature Flags System](#5-feature-flags-system)
6. [Configuration Validation](#6-configuration-validation)
7. [Hot Configuration Reloading](#7-hot-configuration-reloading)
8. [Sensitive Data Masking](#8-sensitive-data-masking)
9. [Version Control Integration](#9-version-control-integration)
10. [Configuration Testing](#10-configuration-testing)
11. [Implementation Code Examples](#11-implementation-code-examples)
12. [Deployment Guide](#12-deployment-guide)
13. [Best Practices](#13-best-practices)
14. [Implementation Priority Order](#14-implementation-priority-order)

---

## 1. Configuration Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Configuration Management Layer                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Config    │  │   Secrets   │  │   Feature   │  │   Validation        │ │
│  │   Loader    │  │   Manager   │  │   Flags     │  │   Engine            │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                │                │                    │            │
│         └────────────────┴────────────────┴────────────────────┘            │
│                                    │                                        │
│                         ┌──────────┴──────────┐                             │
│                         │   Config Service    │                             │
│                         │   (Central Hub)     │                             │
│                         └──────────┬──────────┘                             │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────┐             │
│         │                          │                          │             │
│  ┌──────┴──────┐          ┌────────┴────────┐        ┌───────┴──────┐      │
│  │  Hot Reload │          │  Config Cache   │        │  Event Bus   │      │
│  │  Watcher    │          │  (Redis)        │        │  (Pub/Sub)   │      │
│  └─────────────┘          └─────────────────┘        └──────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
            ┌───────┴──────┐ ┌──────┴──────┐ ┌──────┴──────┐
            │   Local      │ │   Cloud     │ │   External  │
            │   Files      │ │   Providers │ │   Services  │
            └──────────────┘ └─────────────┘ └─────────────┘
```

### 1.2 Core Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Config Loader | Load and parse configuration files | Python/Pydantic |
| Secrets Manager | Secure secrets retrieval | HashiCorp Vault, AWS SM |
| Feature Flags | Dynamic feature toggling | LaunchDarkly/Custom |
| Validation Engine | Schema validation | Pydantic/Cerberus |
| Hot Reload Watcher | Detect config changes | Watchdog/Inotify |
| Config Cache | Distributed caching | Redis |
| Event Bus | Config change propagation | Redis Pub/Sub |

---

## 2. Configuration Hierarchy

### 2.1 Configuration Precedence (Highest to Lowest)

```
1. Runtime Environment Variables (override everything)
2. Command Line Arguments
3. Environment-Specific Secrets (Vault/AWS SM)
4. Environment-Specific Config Files
5. Shared Config Files
6. Default Config Files
7. Built-in Defaults
```

### 2.2 Configuration Directory Structure

```
config/
├── default/                    # Default configurations (committed)
│   ├── app.yaml               # Application defaults
│   ├── database.yaml          # Database defaults
│   ├── logging.yaml           # Logging defaults
│   └── features.yaml          # Feature flag defaults
├── environments/              # Environment-specific (committed)
│   ├── development/
│   │   ├── app.yaml
│   │   └── database.yaml
│   ├── staging/
│   │   ├── app.yaml
│   │   └── database.yaml
│   └── production/
│       ├── app.yaml
│       └── database.yaml
├── secrets/                   # Secret references (committed, NOT values)
│   ├── development/
│   │   └── secret_refs.yaml
│   ├── staging/
│   │   └── secret_refs.yaml
│   └── production/
│       └── secret_refs.yaml
├── schemas/                   # Validation schemas (committed)
│   ├── app_schema.yaml
│   ├── database_schema.yaml
│   └── feature_schema.yaml
└── templates/                 # Config templates
    └── config.yaml.j2
```

### 2.3 Configuration Merging Strategy

```python
# File: /app/config/merger.py
"""
Configuration merging with precedence handling.
"""
from typing import Dict, Any, List
from copy import deepcopy
import yaml


class ConfigMerger:
    """Merge multiple configuration sources with proper precedence."""
    
    @staticmethod
    def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries. Override values take precedence.
        
        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary
            
        Returns:
            Merged configuration dictionary
        """
        result = deepcopy(base)
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigMerger.deep_merge(result[key], value)
            else:
                result[key] = deepcopy(value)
                
        return result
    
    @staticmethod
    def merge_configs(config_files: List[str], env_vars: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Merge multiple configuration files with environment variable overrides.
        
        Args:
            config_files: List of configuration file paths (lowest to highest precedence)
            env_vars: Environment variable overrides
            
        Returns:
            Fully merged configuration
        """
        merged = {}
        
        # Merge file configurations
        for config_file in config_files:
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    if config:
                        merged = ConfigMerger.deep_merge(merged, config)
            except FileNotFoundError:
                continue
        
        # Apply environment variable overrides
        if env_vars:
            env_config = ConfigMerger._parse_env_vars(env_vars)
            merged = ConfigMerger.deep_merge(merged, env_config)
        
        return merged
    
    @staticmethod
    def _parse_env_vars(env_vars: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse environment variables with nested key support.
        
        Supports formats:
        - APP_DATABASE_HOST=localhost
        - APP__DATABASE__HOST=localhost (double underscore for nesting)
        """
        result = {}
        
        for key, value in env_vars.items():
            if key.startswith('APP__'):
                # Parse nested keys: APP__DATABASE__HOST -> database.host
                keys = key[5:].lower().split('__')
                current = result
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = ConfigMerger._convert_value(value)
            elif key.startswith('APP_'):
                # Flat key: APP_DEBUG -> debug
                result[key[4:].lower()] = ConfigMerger._convert_value(value)
                
        return result
    
    @staticmethod
    def _convert_value(value: str) -> Any:
        """Convert string value to appropriate type."""
        # Boolean conversion
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False
        
        # Integer conversion
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float conversion
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
```

---

## 3. Environment-Based Configuration

### 3.1 Environment Detection Strategy

```python
# File: /app/config/environment.py
"""
Environment detection and configuration loading.
"""
import os
from enum import Enum
from typing import Optional


class Environment(Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentDetector:
    """Detect and manage application environment."""
    
    ENV_VAR_NAME = "APP_ENV"
    DEFAULT_ENV = Environment.DEVELOPMENT
    
    @classmethod
    def detect(cls) -> Environment:
        """
        Detect current environment from various sources.
        
        Detection order:
        1. APP_ENV environment variable
        2. Kubernetes namespace (if running in k8s)
        3. Cloud provider metadata
        4. Default to development
        """
        # Check environment variable
        env_value = os.getenv(cls.ENV_VAR_NAME)
        if env_value:
            try:
                return Environment(env_value.lower())
            except ValueError:
                pass
        
        # Check Kubernetes namespace
        k8s_namespace = cls._detect_kubernetes_namespace()
        if k8s_namespace:
            env_map = {
                'prod': Environment.PRODUCTION,
                'production': Environment.PRODUCTION,
                'staging': Environment.STAGING,
                'stage': Environment.STAGING,
                'dev': Environment.DEVELOPMENT,
                'development': Environment.DEVELOPMENT,
            }
            return env_map.get(k8s_namespace.lower(), cls.DEFAULT_ENV)
        
        # Check cloud provider
        cloud_env = cls._detect_cloud_environment()
        if cloud_env:
            return cloud_env
        
        return cls.DEFAULT_ENV
    
    @classmethod
    def _detect_kubernetes_namespace(cls) -> Optional[str]:
        """Detect if running in Kubernetes and return namespace."""
        namespace_file = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
        try:
            with open(namespace_file, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return None
    
    @classmethod
    def _detect_cloud_environment(cls) -> Optional[Environment]:
        """Detect environment from cloud provider metadata."""
        # AWS
        if os.getenv('AWS_EXECUTION_ENV'):
            # Check ECS/EKS environment
            cluster = os.getenv('ECS_CLUSTER_NAME', '')
            if 'prod' in cluster.lower():
                return Environment.PRODUCTION
            elif 'staging' in cluster.lower():
                return Environment.STAGING
        
        # GCP
        if os.getenv('GOOGLE_CLOUD_PROJECT'):
            project = os.getenv('GOOGLE_CLOUD_PROJECT', '')
            if 'prod' in project.lower():
                return Environment.PRODUCTION
            elif 'staging' in project.lower():
                return Environment.STAGING
        
        # Azure
        if os.getenv('AZURE_RESOURCE_GROUP'):
            rg = os.getenv('AZURE_RESOURCE_GROUP', '')
            if 'prod' in rg.lower():
                return Environment.PRODUCTION
            elif 'staging' in rg.lower():
                return Environment.STAGING
        
        return None
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.detect() == Environment.PRODUCTION
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment."""
        return cls.detect() == Environment.DEVELOPMENT
```

### 3.2 Environment Configuration Models

```python
# File: /app/config/models.py
"""
Pydantic models for configuration validation.
"""
from pydantic import BaseModel, Field, validator, SecretStr
from typing import List, Dict, Optional, Any
from enum import Enum


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseConfig(BaseModel):
    """Database configuration model."""
    host: str = Field(..., description="Database host")
    port: int = Field(default=5432, ge=1, le=65535)
    database: str = Field(..., description="Database name")
    username: str = Field(..., description="Database username")
    password: SecretStr = Field(..., description="Database password")
    pool_size: int = Field(default=10, ge=1, le=100)
    max_overflow: int = Field(default=20, ge=0, le=100)
    ssl_mode: str = Field(default="prefer")
    connection_timeout: int = Field(default=30, ge=1, le=300)
    
    @validator('host')
    def validate_host(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Database host cannot be empty")
        return v.strip()
    
    class Config:
        env_prefix = "DB_"


class RedisConfig(BaseModel):
    """Redis configuration model."""
    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    password: Optional[SecretStr] = None
    db: int = Field(default=0, ge=0, le=15)
    ssl: bool = Field(default=False)
    connection_pool_size: int = Field(default=50)
    socket_timeout: int = Field(default=5)
    socket_connect_timeout: int = Field(default=5)


class SecurityConfig(BaseModel):
    """Security configuration model."""
    secret_key: SecretStr = Field(..., description="Application secret key")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_hours: int = Field(default=24, ge=1, le=168)
    password_min_length: int = Field(default=8, ge=6, le=128)
    max_login_attempts: int = Field(default=5, ge=1, le=20)
    lockout_duration_minutes: int = Field(default=30, ge=5, le=1440)
    allowed_hosts: List[str] = Field(default_factory=list)
    cors_origins: List[str] = Field(default_factory=list)
    enable_https_redirect: bool = Field(default=False)


class MonitoringConfig(BaseModel):
    """Monitoring and observability configuration."""
    enabled: bool = Field(default=True)
    metrics_port: int = Field(default=9090)
    tracing_enabled: bool = Field(default=True)
    jaeger_endpoint: Optional[str] = None
    prometheus_enabled: bool = Field(default=True)
    health_check_interval: int = Field(default=30)
    alert_endpoints: List[str] = Field(default_factory=list)


class MLConfig(BaseModel):
    """Machine learning configuration."""
    model_path: str = Field(default="/app/models")
    batch_size: int = Field(default=32, ge=1, le=1000)
    max_sequence_length: int = Field(default=512, ge=1, le=4096)
    inference_timeout: int = Field(default=30, ge=1, le=300)
    enable_gpu: bool = Field(default=False)
    gpu_memory_fraction: float = Field(default=0.8, ge=0.1, le=1.0)
    model_cache_size: int = Field(default=5, ge=1, le=20)


class AppConfig(BaseModel):
    """Main application configuration."""
    app_name: str = Field(default="ResilienceAI")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=4, ge=1, le=32)
    log_level: LogLevel = Field(default=LogLevel.INFO)
    
    # Sub-configurations
    database: DatabaseConfig
    redis: RedisConfig = Field(default_factory=RedisConfig)
    security: SecurityConfig
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    ml: MLConfig = Field(default_factory=MLConfig)
    
    # Feature flags
    features: Dict[str, bool] = Field(default_factory=dict)
    
    @validator('debug')
    def validate_debug_in_production(cls, v, values):
        """Prevent debug mode in production."""
        environment = values.get('environment', '').lower()
        if environment == 'production' and v:
            raise ValueError("Debug mode cannot be enabled in production")
        return v
    
    class Config:
        validate_assignment = True
        extra = "forbid"
```

---

## 4. Secrets Management

### 4.1 Secrets Manager Interface

```python
# File: /app/secrets/base.py
"""
Abstract base class for secrets managers.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class Secret:
    """Secret data structure."""
    value: str
    metadata: Dict[str, Any]
    version: Optional[str] = None


class SecretsManager(ABC):
    """Abstract base class for secrets management."""
    
    @abstractmethod
    def get_secret(self, key: str, version: Optional[str] = None) -> Secret:
        """
        Retrieve a secret by key.
        
        Args:
            key: Secret identifier
            version: Optional specific version
            
        Returns:
            Secret object containing value and metadata
        """
        pass
    
    @abstractmethod
    def set_secret(self, key: str, value: str, metadata: Optional[Dict] = None) -> None:
        """
        Store a secret.
        
        Args:
            key: Secret identifier
            value: Secret value
            metadata: Optional metadata
        """
        pass
    
    @abstractmethod
    def delete_secret(self, key: str) -> None:
        """Delete a secret."""
        pass
    
    @abstractmethod
    def list_secrets(self, prefix: Optional[str] = None) -> list:
        """List available secrets."""
        pass
    
    @abstractmethod
    def rotate_secret(self, key: str) -> Secret:
        """Rotate a secret and return new value."""
        pass
```

### 4.2 HashiCorp Vault Implementation

```python
# File: /app/secrets/vault.py
"""
HashiCorp Vault secrets manager implementation.
"""
import hvac
from typing import Optional, Dict, Any
from .base import SecretsManager, Secret


class VaultSecretsManager(SecretsManager):
    """HashiCorp Vault secrets manager."""
    
    def __init__(
        self,
        url: str,
        token: Optional[str] = None,
        role_id: Optional[str] = None,
        secret_id: Optional[str] = None,
        mount_point: str = "secret",
        namespace: Optional[str] = None
    ):
        """
        Initialize Vault client.
        
        Args:
            url: Vault server URL
            token: Vault token (for token auth)
            role_id: AppRole role ID
            secret_id: AppRole secret ID
            mount_point: Secrets mount point
            namespace: Vault namespace (for Vault Enterprise)
        """
        self.mount_point = mount_point
        
        # Initialize client
        self.client = hvac.Client(url=url, namespace=namespace)
        
        # Authenticate
        if token:
            self.client.token = token
        elif role_id and secret_id:
            self.client.auth.approle.login(
                role_id=role_id,
                secret_id=secret_id
            )
        else:
            # Try Kubernetes auth
            self._authenticate_kubernetes()
        
        if not self.client.is_authenticated():
            raise ValueError("Failed to authenticate with Vault")
    
    def _authenticate_kubernetes(self) -> None:
        """Authenticate using Kubernetes service account."""
        jwt_path = "/var/run/secrets/kubernetes.io/serviceaccount/token"
        try:
            with open(jwt_path, 'r') as f:
                jwt = f.read()
            
            role = "resilience-ai"
            self.client.auth.kubernetes.login(
                role=role,
                jwt=jwt
            )
        except FileNotFoundError:
            raise ValueError("Kubernetes JWT not found for authentication")
    
    def get_secret(self, key: str, version: Optional[str] = None) -> Secret:
        """Retrieve secret from Vault."""
        try:
            if version:
                response = self.client.secrets.kv.v2.read_secret_version(
                    path=key,
                    version=version,
                    mount_point=self.mount_point
                )
            else:
                response = self.client.secrets.kv.v2.read_secret_version(
                    path=key,
                    mount_point=self.mount_point
                )
            
            data = response['data']['data']
            metadata = response['data']['metadata']
            
            # Return first value if single secret
            value = list(data.values())[0] if len(data) == 1 else str(data)
            
            return Secret(
                value=value,
                metadata=metadata,
                version=str(metadata.get('version', ''))
            )
            
        except hvac.exceptions.InvalidPath:
            raise KeyError(f"Secret not found: {key}")
    
    def set_secret(self, key: str, value: str, metadata: Optional[Dict] = None) -> None:
        """Store secret in Vault."""
        self.client.secrets.kv.v2.create_or_update_secret(
            path=key,
            secret={"value": value, **(metadata or {})},
            mount_point=self.mount_point
        )
    
    def delete_secret(self, key: str) -> None:
        """Delete secret from Vault."""
        self.client.secrets.kv.v2.delete_metadata_and_all_versions(
            path=key,
            mount_point=self.mount_point
        )
    
    def list_secrets(self, prefix: Optional[str] = None) -> list:
        """List secrets in Vault."""
        path = prefix or ""
        try:
            response = self.client.secrets.kv.v2.list_secrets(
                path=path,
                mount_point=self.mount_point
            )
            return response['data']['keys']
        except hvac.exceptions.InvalidPath:
            return []
    
    def rotate_secret(self, key: str) -> Secret:
        """Rotate secret (implementation depends on secret type)."""
        # This would typically integrate with a rotation service
        raise NotImplementedError("Secret rotation not implemented")
```

### 4.3 AWS Secrets Manager Implementation

```python
# File: /app/secrets/aws.py
"""
AWS Secrets Manager implementation.
"""
import boto3
import json
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError
from .base import SecretsManager, Secret


class AWSSecretsManager(SecretsManager):
    """AWS Secrets Manager implementation."""
    
    def __init__(
        self,
        region: str = "us-east-1",
        endpoint_url: Optional[str] = None
    ):
        """
        Initialize AWS Secrets Manager client.
        
        Args:
            region: AWS region
            endpoint_url: Optional custom endpoint (for local testing)
        """
        self.client = boto3.client(
            'secretsmanager',
            region_name=region,
            endpoint_url=endpoint_url
        )
    
    def get_secret(self, key: str, version: Optional[str] = None) -> Secret:
        """Retrieve secret from AWS Secrets Manager."""
        try:
            kwargs = {'SecretId': key}
            if version:
                kwargs['VersionId'] = version
            
            response = self.client.get_secret_value(**kwargs)
            
            # Parse secret value
            if 'SecretString' in response:
                secret_value = response['SecretString']
                try:
                    # Try to parse as JSON
                    parsed = json.loads(secret_value)
                    value = parsed.get('value', secret_value)
                except json.JSONDecodeError:
                    value = secret_value
            else:
                # Binary secret
                value = response['SecretBinary'].decode('utf-8')
            
            metadata = {
                'created_date': response.get('CreatedDate'),
                'version_stages': response.get('VersionStages', []),
                'arn': response.get('ARN'),
                'name': response.get('Name'),
            }
            
            return Secret(
                value=value,
                metadata=metadata,
                version=response.get('VersionId')
            )
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                raise KeyError(f"Secret not found: {key}")
            raise
    
    def set_secret(self, key: str, value: str, metadata: Optional[Dict] = None) -> None:
        """Store secret in AWS Secrets Manager."""
        secret_string = json.dumps({"value": value, **(metadata or {})})
        
        try:
            self.client.put_secret_value(
                SecretId=key,
                SecretString=secret_string
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Create new secret
                self.client.create_secret(
                    Name=key,
                    SecretString=secret_string,
                    Description=metadata.get('description', '') if metadata else ''
                )
            else:
                raise
    
    def delete_secret(self, key: str) -> None:
        """Delete secret from AWS Secrets Manager."""
        self.client.delete_secret(
            SecretId=key,
            ForceDeleteWithoutRecovery=True
        )
    
    def list_secrets(self, prefix: Optional[str] = None) -> list:
        """List secrets in AWS Secrets Manager."""
        secrets = []
        paginator = self.client.get_paginator('list_secrets')
        
        filters = []
        if prefix:
            filters.append({
                'Key': 'name',
                'Values': [f"{prefix}*"]
            })
        
        for page in paginator.paginate(Filters=filters):
            for secret in page['SecretList']:
                secrets.append(secret['Name'])
        
        return secrets
    
    def rotate_secret(self, key: str) -> Secret:
        """Rotate secret using AWS rotation."""
        self.client.rotate_secret(SecretId=key)
        return self.get_secret(key)
```

### 4.4 Secrets Resolution in Configuration

```python
# File: /app/secrets/resolver.py
"""
Secrets resolution for configuration values.
"""
import re
from typing import Dict, Any, Optional
from .base import SecretsManager


class SecretsResolver:
    """Resolve secrets references in configuration."""
    
    SECRET_PATTERN = re.compile(r'\$\{secret:([^}]+)\}')
    
    def __init__(self, secrets_manager: SecretsManager):
        """
        Initialize secrets resolver.
        
        Args:
            secrets_manager: Secrets manager instance
        """
        self.secrets_manager = secrets_manager
        self._cache: Dict[str, str] = {}
    
    def resolve(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve all secret references in configuration.
        
        Args:
            config: Configuration dictionary with possible secret references
            
        Returns:
            Configuration with resolved secrets
        """
        resolved = {}
        
        for key, value in config.items():
            if isinstance(value, dict):
                resolved[key] = self.resolve(value)
            elif isinstance(value, str):
                resolved[key] = self._resolve_value(value)
            elif isinstance(value, list):
                resolved[key] = [
                    self.resolve(item) if isinstance(item, dict)
                    else self._resolve_value(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                resolved[key] = value
        
        return resolved
    
    def _resolve_value(self, value: str) -> str:
        """Resolve secret references in a string value."""
        if not isinstance(value, str):
            return value
        
        # Check for secret reference
        match = self.SECRET_PATTERN.match(value)
        if match:
            secret_key = match.group(1)
            return self._get_secret(secret_key)
        
        # Check for embedded secret references
        def replace_secret(match):
            secret_key = match.group(1)
            return self._get_secret(secret_key)
        
        return self.SECRET_PATTERN.sub(replace_secret, value)
    
    def _get_secret(self, key: str) -> str:
        """Get secret from cache or secrets manager."""
        if key not in self._cache:
            secret = self.secrets_manager.get_secret(key)
            self._cache[key] = secret.value
        return self._cache[key]
    
    def clear_cache(self) -> None:
        """Clear secrets cache."""
        self._cache.clear()
```

---

## 5. Feature Flags System

### 5.1 Feature Flag Manager

```python
# File: /app/features/manager.py
"""
Feature flag management system.
"""
from enum import Enum
from typing import Dict, Optional, Callable, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import json
import hashlib


class FeatureFlagType(Enum):
    """Types of feature flags."""
    BOOLEAN = "boolean"           # Simple on/off
    PERCENTAGE = "percentage"     # Percentage rollout
    USER_TARGET = "user_target"   # Target specific users
    GROUP_TARGET = "group_target" # Target user groups
    TIME_BASED = "time_based"     # Time-based activation


@dataclass
class FeatureFlag:
    """Feature flag definition."""
    key: str
    name: str
    description: str
    flag_type: FeatureFlagType
    enabled: bool = False
    
    # Percentage rollout
    rollout_percentage: int = 100
    
    # Targeting
    target_users: List[str] = field(default_factory=list)
    target_groups: List[str] = field(default_factory=list)
    
    # Time-based
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"
    tags: List[str] = field(default_factory=list)
    
    def is_active(self, user_id: Optional[str] = None, user_groups: Optional[List[str]] = None) -> bool:
        """Check if feature is active for given context."""
        if not self.enabled:
            return False
        
        # Check time-based constraints
        now = datetime.utcnow()
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time:
            return False
        
        # Check user targeting
        if self.target_users and user_id:
            if user_id in self.target_users:
                return True
        
        # Check group targeting
        if self.target_groups and user_groups:
            if any(g in self.target_groups for g in user_groups):
                return True
        
        # Check percentage rollout
        if self.rollout_percentage < 100 and user_id:
            user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
            user_percentage = (user_hash % 100) + 1
            return user_percentage <= self.rollout_percentage
        
        return True


class FeatureFlagManager:
    """Central feature flag management."""
    
    def __init__(self, storage_backend: Optional[Any] = None):
        """
        Initialize feature flag manager.
        
        Args:
            storage_backend: Backend for persisting feature flags
        """
        self._flags: Dict[str, FeatureFlag] = {}
        self._storage = storage_backend
        self._callbacks: Dict[str, List[Callable]] = {}
        
        if storage_backend:
            self._load_from_storage()
    
    def register_flag(self, flag: FeatureFlag) -> None:
        """Register a new feature flag."""
        self._flags[flag.key] = flag
        self._notify_change(flag.key, flag.enabled)
    
    def get_flag(self, key: str) -> Optional[FeatureFlag]:
        """Get feature flag by key."""
        return self._flags.get(key)
    
    def is_enabled(
        self,
        key: str,
        user_id: Optional[str] = None,
        user_groups: Optional[List[str]] = None,
        default: bool = False
    ) -> bool:
        """
        Check if feature is enabled.
        
        Args:
            key: Feature flag key
            user_id: Optional user identifier
            user_groups: Optional user groups
            default: Default value if flag not found
            
        Returns:
            True if feature is enabled for the context
        """
        flag = self._flags.get(key)
        if not flag:
            return default
        return flag.is_active(user_id, user_groups)
    
    def enable(self, key: str) -> None:
        """Enable a feature flag."""
        if key in self._flags:
            self._flags[key].enabled = True
            self._flags[key].updated_at = datetime.utcnow()
            self._persist_flag(key)
            self._notify_change(key, True)
    
    def disable(self, key: str) -> None:
        """Disable a feature flag."""
        if key in self._flags:
            self._flags[key].enabled = False
            self._flags[key].updated_at = datetime.utcnow()
            self._persist_flag(key)
            self._notify_change(key, False)
    
    def update_rollout(self, key: str, percentage: int) -> None:
        """Update rollout percentage."""
        if key in self._flags:
            self._flags[key].rollout_percentage = max(0, min(100, percentage))
            self._persist_flag(key)
    
    def add_target_user(self, key: str, user_id: str) -> None:
        """Add user to target list."""
        if key in self._flags:
            if user_id not in self._flags[key].target_users:
                self._flags[key].target_users.append(user_id)
                self._persist_flag(key)
    
    def list_flags(self, tag: Optional[str] = None) -> List[FeatureFlag]:
        """List all feature flags, optionally filtered by tag."""
        flags = list(self._flags.values())
        if tag:
            flags = [f for f in flags if tag in f.tags]
        return flags
    
    def on_change(self, key: str, callback: Callable[[bool], None]) -> None:
        """Register callback for flag changes."""
        if key not in self._callbacks:
            self._callbacks[key] = []
        self._callbacks[key].append(callback)
    
    def _notify_change(self, key: str, enabled: bool) -> None:
        """Notify registered callbacks of flag change."""
        for callback in self._callbacks.get(key, []):
            try:
                callback(enabled)
            except Exception as e:
                print(f"Error in feature flag callback: {e}")
    
    def _persist_flag(self, key: str) -> None:
        """Persist flag to storage backend."""
        if self._storage:
            flag = self._flags[key]
            self._storage.save(flag.key, self._flag_to_dict(flag))
    
    def _load_from_storage(self) -> None:
        """Load flags from storage backend."""
        if self._storage:
            data = self._storage.load_all()
            for key, flag_data in data.items():
                self._flags[key] = self._dict_to_flag(flag_data)
    
    def _flag_to_dict(self, flag: FeatureFlag) -> Dict:
        """Convert flag to dictionary."""
        return {
            'key': flag.key,
            'name': flag.name,
            'description': flag.description,
            'flag_type': flag.flag_type.value,
            'enabled': flag.enabled,
            'rollout_percentage': flag.rollout_percentage,
            'target_users': flag.target_users,
            'target_groups': flag.target_groups,
            'start_time': flag.start_time.isoformat() if flag.start_time else None,
            'end_time': flag.end_time.isoformat() if flag.end_time else None,
            'tags': flag.tags,
        }
    
    def _dict_to_flag(self, data: Dict) -> FeatureFlag:
        """Convert dictionary to flag."""
        return FeatureFlag(
            key=data['key'],
            name=data['name'],
            description=data['description'],
            flag_type=FeatureFlagType(data['flag_type']),
            enabled=data['enabled'],
            rollout_percentage=data.get('rollout_percentage', 100),
            target_users=data.get('target_users', []),
            target_groups=data.get('target_groups', []),
            start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else None,
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            tags=data.get('tags', []),
        )
```

### 5.2 Feature Flag Decorator

```python
# File: /app/features/decorators.py
"""
Feature flag decorators for easy integration.
"""
from functools import wraps
from typing import Optional, List, Callable, Any
from .manager import FeatureFlagManager


class FeatureFlagDecorator:
    """Decorators for feature flag integration."""
    
    def __init__(self, manager: FeatureFlagManager):
        self.manager = manager
    
    def enabled(
        self,
        flag_key: str,
        fallback: Optional[Callable] = None
    ):
        """
        Decorator to enable/disable function based on feature flag.
        
        Args:
            flag_key: Feature flag key
            fallback: Optional fallback function when flag is disabled
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if self.manager.is_enabled(flag_key):
                    return func(*args, **kwargs)
                elif fallback:
                    return fallback(*args, **kwargs)
                else:
                    raise FeatureDisabledError(f"Feature '{flag_key}' is disabled")
            return wrapper
        return decorator
    
    def variant(
        self,
        flag_key: str,
        variant_a: Callable,
        variant_b: Callable
    ):
        """
        Decorator for A/B testing with feature flags.
        
        Args:
            flag_key: Feature flag key
            variant_a: Function for variant A (control)
            variant_b: Function for variant B (treatment)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                user_id = kwargs.get('user_id')
                if self.manager.is_enabled(flag_key, user_id=user_id):
                    return variant_b(*args, **kwargs)
                else:
                    return variant_a(*args, **kwargs)
            return wrapper
        return decorator


class FeatureDisabledError(Exception):
    """Exception raised when a disabled feature is accessed."""
    pass
```

---

## 6. Configuration Validation

### 6.1 Validation Framework

```python
# File: /app/config/validation.py
"""
Configuration validation framework.
"""
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import re


class ValidationSeverity(Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Validation result."""
    valid: bool
    message: str
    severity: ValidationSeverity
    path: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'valid': self.valid,
            'message': self.message,
            'severity': self.severity.value,
            'path': self.path,
        }


class ConfigValidator:
    """Configuration validator with extensible rules."""
    
    def __init__(self):
        self._rules: Dict[str, List[Callable]] = {}
        self._global_rules: List[Callable] = []
    
    def add_rule(self, path: str, rule: Callable[[Any], Optional[ValidationResult]]) -> None:
        """
        Add validation rule for specific config path.
        
        Args:
            path: Dot-separated config path (e.g., 'database.host')
            rule: Validation function
        """
        if path not in self._rules:
            self._rules[path] = []
        self._rules[path].append(rule)
    
    def add_global_rule(self, rule: Callable[[Dict], List[ValidationResult]]) -> None:
        """Add global validation rule."""
        self._global_rules.append(rule)
    
    def validate(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate configuration against all rules.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List of validation results
        """
        results = []
        
        # Validate specific paths
        for path, rules in self._rules.items():
            value = self._get_value(config, path)
            for rule in rules:
                result = rule(value)
                if result:
                    results.append(result)
        
        # Run global rules
        for rule in self._global_rules:
            results.extend(rule(config))
        
        return results
    
    def is_valid(self, config: Dict[str, Any]) -> bool:
        """Check if configuration is valid (no errors)."""
        results = self.validate(config)
        return not any(
            r.severity == ValidationSeverity.ERROR for r in results
        )
    
    def _get_value(self, config: Dict, path: str) -> Any:
        """Get value from config by dot-separated path."""
        keys = path.split('.')
        value = config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value


# Predefined validation rules

class ValidationRules:
    """Collection of predefined validation rules."""
    
    @staticmethod
    def required(message: str = "Field is required") -> Callable:
        """Rule: Field must be present and not empty."""
        def rule(value: Any) -> Optional[ValidationResult]:
            if value is None or (isinstance(value, str) and not value.strip()):
                return ValidationResult(
                    valid=False,
                    message=message,
                    severity=ValidationSeverity.ERROR,
                    path=""
                )
            return None
        return rule
    
    @staticmethod
    def range(min_val: Optional[float] = None, max_val: Optional[float] = None) -> Callable:
        """Rule: Value must be within range."""
        def rule(value: Any) -> Optional[ValidationResult]:
            if value is None:
                return None
            
            try:
                num_value = float(value)
                if min_val is not None and num_value < min_val:
                    return ValidationResult(
                        valid=False,
                        message=f"Value must be >= {min_val}",
                        severity=ValidationSeverity.ERROR,
                        path=""
                    )
                if max_val is not None and num_value > max_val:
                    return ValidationResult(
                        valid=False,
                        message=f"Value must be <= {max_val}",
                        severity=ValidationSeverity.ERROR,
                        path=""
                    )
            except (ValueError, TypeError):
                return ValidationResult(
                    valid=False,
                    message="Value must be a number",
                    severity=ValidationSeverity.ERROR,
                    path=""
                )
            return None
        return rule
    
    @staticmethod
    def pattern(regex: str, message: str = "Invalid format") -> Callable:
        """Rule: Value must match pattern."""
        compiled = re.compile(regex)
        def rule(value: Any) -> Optional[ValidationResult]:
            if value is None:
                return None
            if not compiled.match(str(value)):
                return ValidationResult(
                    valid=False,
                    message=message,
                    severity=ValidationSeverity.ERROR,
                    path=""
                )
            return None
        return rule
    
    @staticmethod
    def one_of(choices: List[str]) -> Callable:
        """Rule: Value must be one of allowed choices."""
        def rule(value: Any) -> Optional[ValidationResult]:
            if value is None:
                return None
            if str(value) not in choices:
                return ValidationResult(
                    valid=False,
                    message=f"Value must be one of: {', '.join(choices)}",
                    severity=ValidationSeverity.ERROR,
                    path=""
                )
            return None
        return rule
    
    @staticmethod
    def production_security_check() -> Callable:
        """Global rule: Security checks for production."""
        def rule(config: Dict) -> List[ValidationResult]:
            results = []
            
            # Check if debug is disabled in production
            env = config.get('environment', '').lower()
            if env == 'production':
                if config.get('debug', False):
                    results.append(ValidationResult(
                        valid=False,
                        message="Debug mode must be disabled in production",
                        severity=ValidationSeverity.ERROR,
                        path="debug"
                    ))
                
                # Check for strong secret key
                secret_key = config.get('security', {}).get('secret_key', '')
                if len(str(secret_key)) < 32:
                    results.append(ValidationResult(
                        valid=False,
                        message="Secret key must be at least 32 characters in production",
                        severity=ValidationSeverity.ERROR,
                        path="security.secret_key"
                    ))
                
                # Check HTTPS redirect
                if not config.get('security', {}).get('enable_https_redirect', False):
                    results.append(ValidationResult(
                        valid=False,
                        message="HTTPS redirect should be enabled in production",
                        severity=ValidationSeverity.WARNING,
                        path="security.enable_https_redirect"
                    ))
            
            return results
        return rule
```

---

## 7. Hot Configuration Reloading

### 7.1 Configuration Watcher

```python
# File: /app/config/watcher.py
"""
Hot configuration reloading with file watching.
"""
import os
import asyncio
from typing import Callable, List, Dict, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from threading import Lock
import yaml
import json


class ConfigChangeEvent:
    """Configuration change event."""
    def __init__(self, file_path: str, change_type: str, config: Dict):
        self.file_path = file_path
        self.change_type = change_type
        self.config = config


class ConfigFileHandler(FileSystemEventHandler):
    """Handler for configuration file changes."""
    
    def __init__(
        self,
        callback: Callable[[ConfigChangeEvent], None],
        file_extensions: Set[str] = None
    ):
        self.callback = callback
        self.file_extensions = file_extensions or {'.yaml', '.yml', '.json'}
        self._lock = Lock()
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        if not any(file_path.endswith(ext) for ext in self.file_extensions):
            return
        
        with self._lock:
            try:
                config = self._load_config(file_path)
                change_event = ConfigChangeEvent(
                    file_path=file_path,
                    change_type='modified',
                    config=config
                )
                self.callback(change_event)
            except Exception as e:
                print(f"Error loading config file {file_path}: {e}")
    
    def _load_config(self, file_path: str) -> Dict:
        """Load configuration from file."""
        with open(file_path, 'r') as f:
            if file_path.endswith('.json'):
                return json.load(f)
            else:
                return yaml.safe_load(f) or {}


class ConfigWatcher:
    """Watch configuration files for changes."""
    
    def __init__(self, debounce_seconds: float = 1.0):
        """
        Initialize config watcher.
        
        Args:
            debounce_seconds: Debounce time for rapid changes
        """
        self.debounce_seconds = debounce_seconds
        self._observer = Observer()
        self._handlers: Dict[str, ConfigFileHandler] = {}
        self._callbacks: List[Callable[[ConfigChangeEvent], None]] = []
        self._debounce_timers: Dict[str, asyncio.TimerHandle] = {}
    
    def watch(self, path: str, recursive: bool = True) -> None:
        """
        Start watching a directory or file.
        
        Args:
            path: Path to watch
            recursive: Watch subdirectories
        """
        handler = ConfigFileHandler(self._on_change)
        self._handlers[path] = handler
        self._observer.schedule(handler, path, recursive=recursive)
    
    def on_change(self, callback: Callable[[ConfigChangeEvent], None]) -> None:
        """Register callback for configuration changes."""
        self._callbacks.append(callback)
    
    def start(self) -> None:
        """Start watching."""
        self._observer.start()
    
    def stop(self) -> None:
        """Stop watching."""
        self._observer.stop()
        self._observer.join()
    
    def _on_change(self, event: ConfigChangeEvent) -> None:
        """Handle configuration change with debouncing."""
        file_path = event.file_path
        
        # Cancel existing timer for this file
        if file_path in self._debounce_timers:
            self._debounce_timers[file_path].cancel()
        
        # Schedule new debounced callback
        loop = asyncio.get_event_loop()
        timer = loop.call_later(
            self.debounce_seconds,
            self._notify_callbacks,
            event
        )
        self._debounce_timers[file_path] = timer
    
    def _notify_callbacks(self, event: ConfigChangeEvent) -> None:
        """Notify all registered callbacks."""
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"Error in config change callback: {e}")
        
        # Clean up timer
        if event.file_path in self._debounce_timers:
            del self._debounce_timers[event.file_path]
```

### 7.2 Hot Reload Manager

```python
# File: /app/config/hot_reload.py
"""
Hot reload manager for dynamic configuration updates.
"""
from typing import Dict, Any, Callable, Optional
import asyncio
from .watcher import ConfigWatcher, ConfigChangeEvent
from .merger import ConfigMerger


class HotReloadManager:
    """Manage hot reloading of configuration."""
    
    def __init__(self, config_service: 'ConfigService'):
        """
        Initialize hot reload manager.
        
        Args:
            config_service: Configuration service instance
        """
        self.config_service = config_service
        self.watcher = ConfigWatcher(debounce_seconds=1.0)
        self._reload_callbacks: List[Callable[[Dict], None]] = []
        self._validation_callback: Optional[Callable[[Dict], bool]] = None
    
    def enable_hot_reload(self, watch_paths: List[str]) -> None:
        """
        Enable hot reloading for specified paths.
        
        Args:
            watch_paths: List of paths to watch
        """
        for path in watch_paths:
            self.watcher.watch(path, recursive=True)
        
        self.watcher.on_change(self._handle_config_change)
        self.watcher.start()
    
    def disable_hot_reload(self) -> None:
        """Disable hot reloading."""
        self.watcher.stop()
    
    def on_reload(self, callback: Callable[[Dict], None]) -> None:
        """Register callback for successful reloads."""
        self._reload_callbacks.append(callback)
    
    def set_validation_callback(self, callback: Callable[[Dict], bool]) -> None:
        """Set validation callback for config changes."""
        self._validation_callback = callback
    
    def _handle_config_change(self, event: ConfigChangeEvent) -> None:
        """Handle configuration file change."""
        print(f"Configuration changed: {event.file_path}")
        
        # Reload full configuration
        new_config = self.config_service.reload()
        
        # Validate if validator is set
        if self._validation_callback:
            if not self._validation_callback(new_config):
                print("Configuration validation failed, keeping current config")
                return
        
        # Notify callbacks
        for callback in self._reload_callbacks:
            try:
                callback(new_config)
            except Exception as e:
                print(f"Error in reload callback: {e}")
        
        print("Configuration hot-reloaded successfully")


class ConfigService:
    """Central configuration service."""
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._config_files: List[str] = []
        self._merger = ConfigMerger()
        self._hot_reload: Optional[HotReloadManager] = None
    
    def initialize(self, config_files: List[str]) -> None:
        """
        Initialize configuration service.
        
        Args:
            config_files: List of configuration file paths
        """
        self._config_files = config_files
        self._config = self._load_config()
    
    def get(self, key: str = None, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Dot-separated key path
            default: Default value if key not found
        """
        if key is None:
            return self._config
        
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def reload(self) -> Dict[str, Any]:
        """Reload configuration from files."""
        self._config = self._load_config()
        return self._config
    
    def enable_hot_reload(self, watch_paths: List[str]) -> None:
        """Enable hot reloading."""
        self._hot_reload = HotReloadManager(self)
        self._hot_reload.enable_hot_reload(watch_paths)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load and merge configuration files."""
        import os
        env_vars = dict(os.environ)
        return self._merger.merge_configs(self._config_files, env_vars)
```

---

## 8. Sensitive Data Masking

### 8.1 Data Masker

```python
# File: /app/security/masking.py
"""
Sensitive data masking utilities.
"""
import re
import hashlib
from typing import Dict, Any, List, Optional, Pattern
from dataclasses import dataclass
from enum import Enum


class MaskingStrategy(Enum):
    """Data masking strategies."""
    FULL = "full"               # Replace with ****
    PARTIAL = "partial"         # Show first/last characters
    HASH = "hash"               # Replace with hash
    REDACT = "redact"           # Remove entirely
    TOKENIZE = "tokenize"       # Replace with token


@dataclass
class MaskingRule:
    """Masking rule definition."""
    pattern: Pattern
    strategy: MaskingStrategy
    show_first: int = 0
    show_last: int = 0
    replacement: str = "****"


class DataMasker:
    """Sensitive data masker."""
    
    # Default sensitive field patterns
    SENSITIVE_FIELDS = {
        'password', 'secret', 'token', 'key', 'credential',
        'api_key', 'apikey', 'auth_token', 'access_token',
        'refresh_token', 'private_key', 'client_secret',
        'connection_string', 'database_url', 'dsn'
    }
    
    def __init__(self):
        self._rules: List[MaskingRule] = []
        self._setup_default_rules()
    
    def _setup_default_rules(self) -> None:
        """Setup default masking rules."""
        # Credit card numbers
        self.add_rule(
            pattern=re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            strategy=MaskingStrategy.PARTIAL,
            show_first=4,
            show_last=4
        )
        
        # Email addresses
        self.add_rule(
            pattern=re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            strategy=MaskingStrategy.PARTIAL,
            show_first=2,
            show_last=2
        )
        
        # Phone numbers
        self.add_rule(
            pattern=re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            strategy=MaskingStrategy.PARTIAL,
            show_first=3,
            show_last=2
        )
        
        # SSN
        self.add_rule(
            pattern=re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            strategy=MaskingStrategy.FULL
        )
    
    def add_rule(self, pattern: Pattern, strategy: MaskingStrategy, **kwargs) -> None:
        """Add custom masking rule."""
        self._rules.append(MaskingRule(
            pattern=pattern,
            strategy=strategy,
            **kwargs
        ))
    
    def mask(self, data: Any, sensitive_keys: Optional[set] = None) -> Any:
        """
        Mask sensitive data in any data structure.
        
        Args:
            data: Data to mask
            sensitive_keys: Additional keys to consider sensitive
            
        Returns:
            Masked data
        """
        keys = self.SENSITIVE_FIELDS | (sensitive_keys or set())
        return self._mask_recursive(data, keys)
    
    def _mask_recursive(self, data: Any, sensitive_keys: set) -> Any:
        """Recursively mask sensitive data."""
        if isinstance(data, dict):
            return {
                k: self._mask_value(v, k, sensitive_keys)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self._mask_recursive(item, sensitive_keys) for item in data]
        elif isinstance(data, str):
            return self._apply_rules(data)
        else:
            return data
    
    def _mask_value(self, value: Any, key: str, sensitive_keys: set) -> Any:
        """Mask a single value based on key."""
        key_lower = key.lower()
        
        # Check if key is sensitive
        if any(s in key_lower for s in sensitive_keys):
            if isinstance(value, str):
                return self._mask_string(value)
            return "****"
        
        # Recursively process
        return self._mask_recursive(value, sensitive_keys)
    
    def _mask_string(self, value: str) -> str:
        """Mask a string value."""
        if len(value) <= 4:
            return "****"
        return value[:2] + "****" + value[-2:]
    
    def _apply_rules(self, value: str) -> str:
        """Apply all masking rules to string."""
        result = value
        for rule in self._rules:
            def replace_match(match):
                return self._apply_strategy(match.group(), rule)
            result = rule.pattern.sub(replace_match, result)
        return result
    
    def _apply_strategy(self, value: str, rule: MaskingRule) -> str:
        """Apply masking strategy to value."""
        if rule.strategy == MaskingStrategy.FULL:
            return rule.replacement
        elif rule.strategy == MaskingStrategy.PARTIAL:
            if len(value) <= rule.show_first + rule.show_last:
                return rule.replacement
            return (
                value[:rule.show_first] +
                rule.replacement +
                value[-rule.show_last:] if rule.show_last > 0 else ""
            )
        elif rule.strategy == MaskingStrategy.HASH:
            return hashlib.sha256(value.encode()).hexdigest()[:16]
        elif rule.strategy == MaskingStrategy.REDACT:
            return ""
        elif rule.strategy == MaskingStrategy.TOKENIZE:
            return f"<TOKEN:{hashlib.md5(value.encode()).hexdigest()[:8]}>"
        return rule.replacement
    
    def mask_for_logs(self, data: Dict) -> Dict:
        """Mask data specifically for logging."""
        return self.mask(data)
    
    def mask_for_display(self, data: Dict) -> Dict:
        """Mask data for user display."""
        return self.mask(data, sensitive_keys={'id', 'internal_id', 'user_id'})


# Convenience function
def mask_sensitive_data(data: Any, additional_keys: Optional[List[str]] = None) -> Any:
    """Convenience function to mask sensitive data."""
    masker = DataMasker()
    return masker.mask(data, set(additional_keys) if additional_keys else None)
```

---

## 9. Version Control Integration

### 9.1 Configuration Versioning

```python
# File: /app/config/versioning.py
"""
Configuration version control integration.
"""
import hashlib
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import git
import yaml


@dataclass
class ConfigVersion:
    """Configuration version information."""
    version_hash: str
    timestamp: datetime
    git_commit: Optional[str]
    git_branch: Optional[str]
    author: str
    changes: List[str]
    config_snapshot: Dict[str, Any]


class ConfigVersionManager:
    """Manage configuration versions."""
    
    def __init__(self, config_dir: str):
        """
        Initialize version manager.
        
        Args:
            config_dir: Configuration directory path
        """
        self.config_dir = config_dir
        self._git_repo: Optional[git.Repo] = None
        
        try:
            self._git_repo = git.Repo(config_dir, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            pass
    
    def get_current_version(self, config: Dict[str, Any]) -> ConfigVersion:
        """
        Get current configuration version.
        
        Args:
            config: Current configuration
            
        Returns:
            Configuration version information
        """
        config_hash = self._compute_hash(config)
        
        git_commit = None
        git_branch = None
        
        if self._git_repo:
            try:
                git_commit = self._git_repo.head.commit.hexsha
                git_branch = self._git_repo.active_branch.name
            except:
                pass
        
        return ConfigVersion(
            version_hash=config_hash,
            timestamp=datetime.utcnow(),
            git_commit=git_commit,
            git_branch=git_branch,
            author=self._get_author(),
            changes=[],
            config_snapshot=self._create_snapshot(config)
        )
    
    def _compute_hash(self, config: Dict[str, Any]) -> str:
        """Compute configuration hash."""
        config_str = json.dumps(config, sort_keys=True, default=str)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]
    
    def _create_snapshot(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create configuration snapshot (without secrets)."""
        # Remove sensitive data
        snapshot = json.loads(json.dumps(config, default=str))
        self._sanitize_snapshot(snapshot)
        return snapshot
    
    def _sanitize_snapshot(self, data: Any) -> None:
        """Remove sensitive data from snapshot."""
        sensitive_keys = {'password', 'secret', 'token', 'key'}
        
        if isinstance(data, dict):
            for key in list(data.keys()):
                if any(s in key.lower() for s in sensitive_keys):
                    data[key] = "***REDACTED***"
                else:
                    self._sanitize_snapshot(data[key])
        elif isinstance(data, list):
            for item in data:
                self._sanitize_snapshot(item)
    
    def _get_author(self) -> str:
        """Get current user/author."""
        import getpass
        return getpass.getuser()
    
    def track_change(
        self,
        config: Dict[str, Any],
        change_description: str
    ) -> ConfigVersion:
        """
        Track a configuration change.
        
        Args:
            config: New configuration
            change_description: Description of the change
            
        Returns:
            New version information
        """
        version = self.get_current_version(config)
        version.changes = [change_description]
        
        # Store version metadata
        self._store_version_metadata(version)
        
        return version
    
    def _store_version_metadata(self, version: ConfigVersion) -> None:
        """Store version metadata."""
        metadata = {
            'version_hash': version.version_hash,
            'timestamp': version.timestamp.isoformat(),
            'git_commit': version.git_commit,
            'git_branch': version.git_branch,
            'author': version.author,
            'changes': version.changes,
        }
        
        # Store in version tracking file
        version_file = f"{self.config_dir}/.config_versions.yaml"
        
        try:
            with open(version_file, 'r') as f:
                versions = yaml.safe_load(f) or []
        except FileNotFoundError:
            versions = []
        
        versions.append(metadata)
        
        # Keep only last 100 versions
        versions = versions[-100:]
        
        with open(version_file, 'w') as f:
            yaml.dump(versions, f, default_flow_style=False)
    
    def get_version_history(self, limit: int = 10) -> List[Dict]:
        """Get configuration version history."""
        version_file = f"{self.config_dir}/.config_versions.yaml"
        
        try:
            with open(version_file, 'r') as f:
                versions = yaml.safe_load(f) or []
            return versions[-limit:]
        except FileNotFoundError:
            return []
    
    def compare_versions(
        self,
        version1: str,
        version2: str
    ) -> List[str]:
        """Compare two configuration versions."""
        history = self.get_version_history(limit=1000)
        
        v1_data = None
        v2_data = None
        
        for v in history:
            if v['version_hash'] == version1:
                v1_data = v
            if v['version_hash'] == version2:
                v2_data = v
        
        if not v1_data or not v2_data:
            return ["One or both versions not found"]
        
        differences = []
        
        if v1_data['git_commit'] != v2_data['git_commit']:
            differences.append(
                f"Git commit changed: {v1_data['git_commit'][:8]} -> {v2_data['git_commit'][:8]}"
            )
        
        if v1_data['author'] != v2_data['author']:
            differences.append(
                f"Author changed: {v1_data['author']} -> {v2_data['author']}"
            )
        
        return differences


class ConfigGitIntegration:
    """Git integration for configuration files."""
    
    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        self.repo = git.Repo(config_dir, search_parent_directories=True)
    
    def get_config_changes(self) -> List[Dict]:
        """Get recent changes to configuration files."""
        changes = []
        
        for commit in self.repo.iter_commits(paths=self.config_dir, max_count=10):
            changes.append({
                'commit': commit.hexsha,
                'author': commit.author.name,
                'date': commit.committed_datetime.isoformat(),
                'message': commit.message.strip(),
            })
        
        return changes
    
    def validate_before_commit(self) -> List[str]:
        """Validate configuration before commit."""
        errors = []
        
        # Check for secrets in staged files
        staged_files = self._get_staged_config_files()
        
        for file_path in staged_files:
            if self._contains_secrets(file_path):
                errors.append(f"Potential secret found in {file_path}")
        
        return errors
    
    def _get_staged_config_files(self) -> List[str]:
        """Get staged configuration files."""
        staged = []
        
        for item in self.repo.index.diff('HEAD'):
            if item.a_path.endswith(('.yaml', '.yml', '.json')):
                staged.append(item.a_path)
        
        return staged
    
    def _contains_secrets(self, file_path: str) -> bool:
        """Check if file contains potential secrets."""
        secret_patterns = [
            r'password:\s*[^\s*]+',
            r'secret:\s*[^\s*]+',
            r'api_key:\s*[^\s*]+',
            r'token:\s*[^\s*]+',
        ]
        
        try:
            with open(f"{self.repo.working_dir}/{file_path}", 'r') as f:
                content = f.read()
                for pattern in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return True
        except:
            pass
        
        return False
```

---

## 10. Configuration Testing

### 10.1 Configuration Test Framework

```python
# File: /app/config/testing.py
"""
Configuration testing framework.
"""
import pytest
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from .validation import ConfigValidator, ValidationResult
from .models import AppConfig


@dataclass
class ConfigTestCase:
    """Configuration test case."""
    name: str
    config: Dict[str, Any]
    expected_valid: bool
    expected_errors: List[str]
    description: str


class ConfigTestSuite:
    """Configuration test suite."""
    
    def __init__(self):
        self.test_cases: List[ConfigTestCase] = []
        self.validator = ConfigValidator()
    
    def add_test_case(self, test_case: ConfigTestCase) -> None:
        """Add a test case."""
        self.test_cases.append(test_case)
    
    def run_tests(self) -> Dict[str, Any]:
        """
        Run all test cases.
        
        Returns:
            Test results summary
        """
        results = {
            'passed': 0,
            'failed': 0,
            'total': len(self.test_cases),
            'details': []
        }
        
        for test in self.test_cases:
            validation_results = self.validator.validate(test.config)
            errors = [r.message for r in validation_results 
                     if not r.valid]
            
            passed = (
                test.expected_valid == (len(errors) == 0) and
                all(e in errors for e in test.expected_errors)
            )
            
            result = {
                'name': test.name,
                'passed': passed,
                'description': test.description,
                'errors': errors if not passed else []
            }
            
            results['details'].append(result)
            
            if passed:
                results['passed'] += 1
            else:
                results['failed'] += 1
        
        return results


# Predefined test cases

class DefaultTestCases:
    """Default configuration test cases."""
    
    @staticmethod
    def production_security_tests() -> List[ConfigTestCase]:
        """Production security test cases."""
        return [
            ConfigTestCase(
                name="production_debug_disabled",
                config={
                    'environment': 'production',
                    'debug': True
                },
                expected_valid=False,
                expected_errors=["Debug mode must be disabled in production"],
                description="Debug mode should be disabled in production"
            ),
            ConfigTestCase(
                name="production_strong_secret",
                config={
                    'environment': 'production',
                    'debug': False,
                    'security': {
                        'secret_key': 'short'
                    }
                },
                expected_valid=False,
                expected_errors=["Secret key must be at least 32 characters"],
                description="Production should use strong secret key"
            ),
            ConfigTestCase(
                name="valid_production_config",
                config={
                    'environment': 'production',
                    'debug': False,
                    'security': {
                        'secret_key': 'a' * 32
                    }
                },
                expected_valid=True,
                expected_errors=[],
                description="Valid production configuration"
            ),
        ]
    
    @staticmethod
    def database_connection_tests() -> List[ConfigTestCase]:
        """Database connection test cases."""
        return [
            ConfigTestCase(
                name="valid_database_config",
                config={
                    'database': {
                        'host': 'localhost',
                        'port': 5432,
                        'database': 'resilience_ai',
                        'username': 'user',
                        'password': 'password'
                    }
                },
                expected_valid=True,
                expected_errors=[],
                description="Valid database configuration"
            ),
            ConfigTestCase(
                name="missing_database_host",
                config={
                    'database': {
                        'port': 5432,
                        'database': 'resilience_ai'
                    }
                },
                expected_valid=False,
                expected_errors=["Database host cannot be empty"],
                description="Database host is required"
            ),
            ConfigTestCase(
                name="invalid_database_port",
                config={
                    'database': {
                        'host': 'localhost',
                        'port': 99999
                    }
                },
                expected_valid=False,
                expected_errors=["port"],
                description="Database port must be valid"
            ),
        ]


# Pytest fixtures and helpers

@pytest.fixture
def config_validator():
    """Pytest fixture for config validator."""
    return ConfigValidator()


@pytest.fixture
def valid_production_config():
    """Pytest fixture for valid production config."""
    return {
        'app_name': 'ResilienceAI',
        'environment': 'production',
        'debug': False,
        'database': {
            'host': 'db.resilience.ai',
            'port': 5432,
            'database': 'resilience_ai',
            'username': 'app_user',
            'password': 'secure_password'
        },
        'security': {
            'secret_key': 'a' * 32
        }
    }


def test_production_config_security(valid_production_config):
    """Test production configuration security."""
    # Validate with Pydantic model
    config = AppConfig(**valid_production_config)
    
    assert config.environment == 'production'
    assert config.debug is False
    assert len(config.security.secret_key.get_secret_value()) >= 32


def test_config_validation(config_validator):
    """Test configuration validation."""
    # Add validation rules
    from .validation import ValidationRules
    
    config_validator.add_rule(
        'environment',
        ValidationRules.one_of(['development', 'staging', 'production'])
    )
    
    # Test valid config
    valid_config = {'environment': 'production'}
    results = config_validator.validate(valid_config)
    assert len([r for r in results if not r.valid]) == 0
    
    # Test invalid config
    invalid_config = {'environment': 'invalid'}
    results = config_validator.validate(invalid_config)
    assert len([r for r in results if not r.valid]) == 1


# Configuration smoke tests

def test_config_loads_without_errors():
    """Smoke test: Configuration should load without errors."""
    from .hot_reload import ConfigService
    
    service = ConfigService()
    # Should not raise any exceptions
    config = service.get()
    assert isinstance(config, dict)


def test_all_required_configs_present():
    """Test that all required configuration keys are present."""
    required_keys = [
        'app_name',
        'environment',
        'database',
        'security'
    ]
    
    from .hot_reload import ConfigService
    service = ConfigService()
    config = service.get()
    
    for key in required_keys:
        assert key in config, f"Required config key '{key}' is missing"
```

---

## 11. Implementation Code Examples

### 11.1 Complete Configuration Service

```python
# File: /app/config/__init__.py
"""
ResilienceAI Configuration Management System.

This module provides comprehensive configuration management including:
- Environment-based configuration
- Secrets management integration
- Feature flags
- Hot reloading
- Configuration validation
"""
from .environment import Environment, EnvironmentDetector
from .models import AppConfig, DatabaseConfig, SecurityConfig
from .merger import ConfigMerger
from .validation import ConfigValidator, ValidationRules
from .hot_reload import ConfigService, HotReloadManager
from .watcher import ConfigWatcher
from ..secrets.base import SecretsManager
from ..secrets.resolver import SecretsResolver
from ..features.manager import FeatureFlagManager

__all__ = [
    'Environment',
    'EnvironmentDetector',
    'AppConfig',
    'DatabaseConfig',
    'SecurityConfig',
    'ConfigMerger',
    'ConfigValidator',
    'ValidationRules',
    'ConfigService',
    'HotReloadManager',
    'ConfigWatcher',
    'SecretsManager',
    'SecretsResolver',
    'FeatureFlagManager',
]


class ResilienceAIConfig:
    """
    Main configuration class for ResilienceAI.
    
    Usage:
        config = ResilienceAIConfig()
        config.initialize([
            'config/default/app.yaml',
            'config/environments/production/app.yaml'
        ])
        
        # Get configuration values
        db_host = config.get('database.host')
        
        # Check feature flags
        if config.is_feature_enabled('new_ml_model'):
            use_new_model()
    """
    
    def __init__(self):
        self._service = ConfigService()
        self._validator = ConfigValidator()
        self._secrets_resolver: Optional[SecretsResolver] = None
        self._feature_manager = FeatureFlagManager()
        self._initialized = False
    
    def initialize(
        self,
        config_files: List[str],
        secrets_manager: Optional[SecretsManager] = None,
        enable_hot_reload: bool = False,
        watch_paths: Optional[List[str]] = None
    ) -> None:
        """
        Initialize configuration.
        
        Args:
            config_files: List of configuration file paths
            secrets_manager: Optional secrets manager for secret resolution
            enable_hot_reload: Enable hot reloading
            watch_paths: Paths to watch for hot reload
        """
        # Load configuration
        self._service.initialize(config_files)
        config = self._service.get()
        
        # Resolve secrets
        if secrets_manager:
            self._secrets_resolver = SecretsResolver(secrets_manager)
            config = self._secrets_resolver.resolve(config)
        
        # Validate configuration
        self._setup_validation_rules()
        if not self._validator.is_valid(config):
            errors = self._validator.validate(config)
            error_messages = [e.message for e in errors if not e.valid]
            raise ValueError(f"Configuration validation failed: {error_messages}")
        
        # Parse into Pydantic model
        self._config = AppConfig(**config)
        
        # Enable hot reload if requested
        if enable_hot_reload and watch_paths:
            self._service.enable_hot_reload(watch_paths)
        
        self._initialized = True
    
    def get(self, key: str = None, default: Any = None) -> Any:
        """Get configuration value."""
        if not self._initialized:
            raise RuntimeError("Configuration not initialized")
        
        if key is None:
            return self._config
        
        # Navigate through Pydantic model
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return default
        
        return value
    
    def is_feature_enabled(
        self,
        key: str,
        user_id: Optional[str] = None,
        user_groups: Optional[List[str]] = None
    ) -> bool:
        """Check if feature flag is enabled."""
        return self._feature_manager.is_enabled(key, user_id, user_groups)
    
    def reload(self) -> None:
        """Reload configuration."""
        self._service.reload()
    
    def _setup_validation_rules(self) -> None:
        """Setup default validation rules."""
        from .validation import ValidationRules
        
        # Environment validation
        self._validator.add_rule(
            'environment',
            ValidationRules.one_of(['development', 'testing', 'staging', 'production'])
        )
        
        # Production security rules
        self._validator.add_global_rule(ValidationRules.production_security_check())


# Global configuration instance
_config: Optional[ResilienceAIConfig] = None


def get_config() -> ResilienceAIConfig:
    """Get global configuration instance."""
    if _config is None:
        raise RuntimeError("Configuration not initialized. Call init_config() first.")
    return _config


def init_config(
    config_files: List[str],
    secrets_manager: Optional[SecretsManager] = None,
    enable_hot_reload: bool = False
) -> ResilienceAIConfig:
    """
    Initialize global configuration.
    
    Args:
        config_files: List of configuration file paths
        secrets_manager: Optional secrets manager
        enable_hot_reload: Enable hot reloading
        
    Returns:
        Configuration instance
    """
    global _config
    _config = ResilienceAIConfig()
    
    watch_paths = ['config/'] if enable_hot_reload else None
    _config.initialize(
        config_files=config_files,
        secrets_manager=secrets_manager,
        enable_hot_reload=enable_hot_reload,
        watch_paths=watch_paths
    )
    
    return _config
```

### 11.2 FastAPI Integration

```python
# File: /app/api/dependencies.py
"""
FastAPI dependencies for configuration.
"""
from fastapi import Request, HTTPException, Depends
from typing import Optional
from ..config import get_config, ResilienceAIConfig


async def get_config_dependency() -> ResilienceAIConfig:
    """Dependency to get configuration."""
    return get_config()


async def require_feature_flag(
    flag_key: str,
    config: ResilienceAIConfig = Depends(get_config_dependency)
):
    """Dependency to require a feature flag."""
    if not config.is_feature_enabled(flag_key):
        raise HTTPException(
            status_code=403,
            detail=f"Feature '{flag_key}' is not enabled"
        )


async def get_current_user_features(
    request: Request,
    config: ResilienceAIConfig = Depends(get_config_dependency)
) -> dict:
    """Get feature flags for current user."""
    user_id = request.headers.get('X-User-ID')
    user_groups = request.headers.get('X-User-Groups', '').split(',')
    
    all_flags = config._feature_manager.list_flags()
    
    return {
        flag.key: config.is_feature_enabled(flag.key, user_id, user_groups)
        for flag in all_flags
    }
```

---

## 12. Deployment Guide

### 12.1 Docker Configuration

```dockerfile
# Dockerfile.config
FROM python:3.11-slim as config-base

WORKDIR /app

# Install dependencies
COPY requirements-config.txt .
RUN pip install --no-cache-dir -r requirements-config.txt

# Copy configuration files
COPY config/ ./config/

# Copy configuration management code
COPY app/config/ ./app/config/
COPY app/secrets/ ./app/secrets/
COPY app/features/ ./app/features/
COPY app/security/ ./app/security/

# Set environment
ENV APP_ENV=production
ENV CONFIG_PATH=/app/config

# Validate configuration on build
RUN python -c "from app.config import init_config; init_config(['config/default/app.yaml'])"

CMD ["python", "-m", "app.config.validate"]
```

### 12.2 Kubernetes Configuration

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: resilience-ai-config
data:
  APP_ENV: "production"
  CONFIG_PATH: "/app/config"
  LOG_LEVEL: "INFO"
  
---
# k8s/secret-provider.yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: resilience-ai-secrets
spec:
  provider: aws
  parameters:
    objects: |
      - objectName: "resilience-ai/db-password"
        objectType: "secretsmanager"
      - objectName: "resilience-ai/api-key"
        objectType: "secretsmanager"
  secretObjects:
    - secretName: resilience-ai-secrets
      type: Opaque
      data:
        - objectName: "db-password"
          key: DB_PASSWORD
        - objectName: "api-key"
          key: API_KEY

---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resilience-ai
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: resilience-ai:latest
        envFrom:
        - configMapRef:
            name: resilience-ai-config
        - secretRef:
            name: resilience-ai-secrets
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: secrets-store
          mountPath: "/mnt/secrets"
          readOnly: true
      volumes:
      - name: config-volume
        configMap:
          name: resilience-ai-config-files
      - name: secrets-store
        csi:
          driver: secrets-store.csi.k8s.io
          readOnly: true
          volumeAttributes:
            secretProviderClass: resilience-ai-secrets
```

### 12.3 CI/CD Pipeline

```yaml
# .github/workflows/config-validation.yml
name: Configuration Validation

on:
  push:
    paths:
      - 'config/**'
      - 'app/config/**'
  pull_request:
    paths:
      - 'config/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Validate configuration schema
      run: |
        python -m app.config.validate --schema
    
    - name: Run configuration tests
      run: |
        pytest tests/config/ -v
    
    - name: Check for secrets in configs
      run: |
        python -m app.config.check_secrets
    
    - name: Validate environment configs
      run: |
        python -m app.config.validate --env development
        python -m app.config.validate --env staging
        python -m app.config.validate --env production
```

---

## 13. Best Practices

### 13.1 Configuration Security Checklist

| Category | Practice | Priority |
|----------|----------|----------|
| Secrets | Never commit secrets to version control | Critical |
| Secrets | Use dedicated secrets manager (Vault/AWS SM) | Critical |
| Secrets | Rotate secrets regularly | High |
| Secrets | Use different secrets per environment | Critical |
| Validation | Validate all configuration at startup | High |
| Validation | Fail fast on invalid configuration | High |
| Validation | Schema validation for all configs | High |
| Environment | Separate configs per environment | Critical |
| Environment | No production secrets in dev configs | Critical |
| Feature Flags | Use feature flags for risky changes | Medium |
| Feature Flags | Gradual rollout with percentage | Medium |
| Monitoring | Log configuration changes | High |
| Monitoring | Alert on config validation failures | High |
| Hot Reload | Validate before applying hot reload | High |
| Hot Reload | Rollback on validation failure | Medium |

### 13.2 Configuration Naming Conventions

```yaml
# Use consistent naming
app_name: "ResilienceAI"           # Use snake_case
app_version: "1.0.0"               # Semantic versioning
environment: "production"          # lowercase

# Group related settings
database:
  host: "localhost"                # Not: db_host
  port: 5432                       # Not: db_port
  
security:
  secret_key: "${secret:app/key}"  # Secret reference
  jwt_expiration: 3600

# Use arrays for lists
allowed_hosts:
  - "api.resilience.ai"
  - "app.resilience.ai"
```

### 13.3 Environment Variable Mapping

```
# Configuration Key          Environment Variable
# -----------------          --------------------
app.debug                    APP_DEBUG
app.port                     APP_PORT
database.host                APP__DATABASE__HOST
database.port                APP__DATABASE__PORT
database.password            APP__DATABASE__PASSWORD
security.secret_key          APP__SECURITY__SECRET_KEY
```

---

## 14. Implementation Priority Order

### Phase 1: Foundation (Week 1-2)
1. **Configuration Models** - Pydantic models for type safety
2. **Environment Detection** - Environment-aware configuration
3. **Config Merging** - Hierarchy and precedence handling
4. **Basic Validation** - Schema validation with Pydantic

### Phase 2: Security (Week 2-3)
5. **Secrets Manager Interface** - Abstract base class
6. **Vault Integration** - HashiCorp Vault implementation
7. **AWS Secrets Manager** - Cloud provider integration
8. **Secrets Resolution** - Runtime secret injection

### Phase 3: Advanced Features (Week 3-4)
9. **Feature Flags** - Dynamic feature toggling
10. **Hot Reloading** - File watching and dynamic updates
11. **Data Masking** - Sensitive data protection
12. **Version Control** - Git integration and versioning

### Phase 4: Testing & Operations (Week 4-5)
13. **Configuration Tests** - Automated testing framework
14. **CI/CD Integration** - Pipeline validation
15. **Monitoring** - Configuration change tracking
16. **Documentation** - Complete documentation

---

## Appendix A: Configuration File Templates

### Default Application Configuration

```yaml
# config/default/app.yaml
app_name: "ResilienceAI"
app_version: "1.0.0"
debug: false
host: "0.0.0.0"
port: 8000
workers: 4
log_level: "INFO"

features:
  enable_new_ml_model: false
  enable_advanced_analytics: false
  enable_realtime_predictions: false
```

### Production Environment Configuration

```yaml
# config/environments/production/app.yaml
environment: "production"
debug: false
log_level: "WARNING"
workers: 8

database:
  host: "${secret:prod/db/host}"
  port: 5432
  database: "resilience_ai_prod"
  username: "${secret:prod/db/username}"
  password: "${secret:prod/db/password}"
  pool_size: 20
  ssl_mode: "require"

security:
  secret_key: "${secret:prod/app/secret_key}"
  jwt_expiration_hours: 12
  enable_https_redirect: true
  allowed_hosts:
    - "api.resilience.ai"
    - "app.resilience.ai"

monitoring:
  enabled: true
  prometheus_enabled: true
  tracing_enabled: true
  jaeger_endpoint: "https://jaeger.resilience.ai"

features:
  enable_new_ml_model: true
  enable_advanced_analytics: true
  enable_realtime_predictions: true
```

---

## Appendix B: Quick Reference

### Common Tasks

```python
# Initialize configuration
from app.config import init_config

config = init_config([
    'config/default/app.yaml',
    'config/environments/production/app.yaml'
], enable_hot_reload=True)

# Get configuration values
db_host = config.get('database.host')
app_debug = config.get('debug', False)

# Check feature flags
if config.is_feature_enabled('new_ml_model', user_id='user123'):
    use_new_model()

# Register feature flag callback
config._feature_manager.on_change('new_ml_model', lambda enabled: print(f"Feature changed: {enabled}"))
```

### Environment Variables

```bash
# Set environment
export APP_ENV=production

# Override configuration
export APP__DATABASE__HOST=custom-db-host
export APP__DEBUG=false
export APP__LOG_LEVEL=DEBUG
```

---

*Document Version: 1.0*
*Last Updated: 2024*
*Author: ResilienceAI Engineering Team*
