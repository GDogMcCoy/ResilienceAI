"""
Geospatial package initialization
"""
from .usgs_3dep import USGS3DEPClient, DEMProcessor, BoundingBox
from .naip import NAIPClient, NAIPProcessor, NAIPMetadata
from .gee_integration import GEEClient, MockGEEClient, get_gee_client
from .pipeline import (
    GeospatialPipeline,
    PipelineConfig,
    PipelineResult,
    DataSource,
    ProcessingStep,
    BuildingFootprintExtractor,
    LandCoverClassifier
)

__version__ = "3.2.0"

__all__ = [
    # USGS 3DEP
    "USGS3DEPClient",
    "DEMProcessor",
    "BoundingBox",
    
    # NAIP
    "NAIPClient",
    "NAIPProcessor",
    "NAIPMetadata",
    
    # GEE
    "GEEClient",
    "MockGEEClient",
    "get_gee_client",
    
    # Pipeline
    "GeospatialPipeline",
    "PipelineConfig",
    "PipelineResult",
    "DataSource",
    "ProcessingStep",
    "BuildingFootprintExtractor",
    "LandCoverClassifier",
]
