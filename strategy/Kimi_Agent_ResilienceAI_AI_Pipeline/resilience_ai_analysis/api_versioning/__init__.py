"""
ResilienceAI API Versioning Module

This module provides comprehensive API versioning support including:
- Version negotiation and detection
- Backward compatibility transformations
- Deprecation lifecycle management
- Migration assistance
- Analytics and monitoring
"""

from .versions import APIVersion, VERSION_REGISTRY, VersionInfo
from .negotiation import VersionNegotiator, version_negotiator
from .compatibility import CompatibilityLayer, compatibility
from .deprecation import DeprecationManager, deprecation_manager, DeprecationStage
from .sunset import SunsetManager, sunset_manager
from .analytics import VersionAnalytics, version_analytics
from .communication import ClientCommunicationManager

__all__ = [
    "APIVersion",
    "VERSION_REGISTRY",
    "VersionInfo",
    "VersionNegotiator",
    "version_negotiator",
    "CompatibilityLayer",
    "compatibility",
    "DeprecationManager",
    "deprecation_manager",
    "DeprecationStage",
    "SunsetManager",
    "sunset_manager",
    "VersionAnalytics",
    "version_analytics",
    "ClientCommunicationManager",
]

__version__ = "1.0.0"
