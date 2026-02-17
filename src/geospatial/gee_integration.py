"""
Google Earth Engine Integration
Access Sentinel-2 and other satellite data via GEE
"""
import os
import json
import tempfile
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta
import logging

import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.crs import CRS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GEEConfig:
    """Google Earth Engine configuration"""
    project_id: Optional[str] = None
    service_account: Optional[str] = None
    private_key_file: Optional[str] = None
    
    def is_configured(self) -> bool:
        """Check if GEE is properly configured"""
        try:
            import ee
            return ee.data._credentials is not None
        except:
            return False


class GEEClient:
    """Client for Google Earth Engine data access"""
    
    # Missouri test region
    MISSOURI_TEST_BBOX = {
        "west": -90.5,
        "south": 38.5,
        "east": -90.0,
        "north": 39.0
    }
    
    def __init__(self, config: Optional[GEEConfig] = None):
        self.config = config or GEEConfig()
        self._ee = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize Google Earth Engine
        
        Returns:
            True if successful
        """
        try:
            import ee
            self._ee = ee
            
            # Try to initialize
            if self.config.project_id:
                ee.Initialize(project=self.config.project_id)
            else:
                ee.Initialize()
            
            self._initialized = True
            logger.info("Google Earth Engine initialized successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Could not initialize GEE: {e}")
            logger.info("GEE will run in mock mode for testing")
            self._initialized = False
            return False
    
    @property
    def ee(self):
        """Get Earth Engine module"""
        if self._ee is None:
            self.initialize()
        return self._ee
    
    def is_initialized(self) -> bool:
        """Check if GEE is initialized"""
        return self._initialized
    
    def create_geometry(
        self,
        bbox: Dict[str, float]
    ) -> Any:
        """
        Create GEE geometry from bounding box
        
        Args:
            bbox: Dict with west, south, east, north
            
        Returns:
            GEE Geometry
        """
        if not self.is_initialized():
            return None
        
        return self.ee.Geometry.Rectangle([
            bbox["west"], bbox["south"],
            bbox["east"], bbox["north"]
        ])
    
    def get_sentinel2_collection(
        self,
        bbox: Dict[str, float],
        start_date: str,
        end_date: str,
        cloud_cover_threshold: float = 20.0
    ) -> Any:
        """
        Get Sentinel-2 image collection
        
        Args:
            bbox: Bounding box
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            cloud_cover_threshold: Max cloud cover percentage
            
        Returns:
            GEE ImageCollection
        """
        if not self.is_initialized():
            return None
        
        geometry = self.create_geometry(bbox)
        
        # Get Sentinel-2 SR collection
        collection = (self.ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
            .filterBounds(geometry)
            .filterDate(start_date, end_date)
            .filter(self.ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_cover_threshold))
            .sort('CLOUDY_PIXEL_PERCENTAGE')
        )
        
        return collection
    
    def get_landsat_collection(
        self,
        bbox: Dict[str, float],
        start_date: str,
        end_date: str,
        cloud_cover_threshold: float = 20.0,
        collection: str = "LANDSAT/LC09/C02/T1_L2"
    ) -> Any:
        """
        Get Landsat image collection
        
        Args:
            bbox: Bounding box
            start_date: Start date
            end_date: End date
            cloud_cover_threshold: Max cloud cover
            collection: Landsat collection ID
            
        Returns:
            GEE ImageCollection
        """
        if not self.is_initialized():
            return None
        
        geometry = self.create_geometry(bbox)
        
        col = (self.ee.ImageCollection(collection)
            .filterBounds(geometry)
            .filterDate(start_date, end_date)
            .filter(self.ee.Filter.lt('CLOUD_COVER', cloud_cover_threshold))
            .sort('CLOUD_COVER')
        )
        
        return col
    
    def calculate_sentinel2_mosaic(
        self,
        bbox: Dict[str, float],
        start_date: str,
        end_date: str,
        mosaic_type: str = "median",
        cloud_cover: float = 20.0
    ) -> Any:
        """
        Create Sentinel-2 mosaic
        
        Args:
            bbox: Bounding box
            start_date: Start date
            end_date: End date
            mosaic_type: 'median', 'mean', or 'mosaic'
            cloud_cover: Max cloud cover
            
        Returns:
            GEE Image
        """
        if not self.is_initialized():
            return None
        
        collection = self.get_sentinel2_collection(
            bbox, start_date, end_date, cloud_cover
        )
        
        if mosaic_type == "median":
            return collection.median()
        elif mosaic_type == "mean":
            return collection.mean()
        elif mosaic_type == "mosaic":
            return collection.mosaic()
        else:
            return collection.median()
    
    def calculate_ndvi_sentinel2(self, image: Any) -> Any:
        """
        Calculate NDVI from Sentinel-2 image
        
        Args:
            image: GEE Image
            
        Returns:
            GEE Image with NDVI band
        """
        if not self.is_initialized():
            return None
        
        # Sentinel-2 bands: B4=Red, B8=NIR
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        return ndvi
    
    def calculate_ndwi_sentinel2(self, image: Any) -> Any:
        """
        Calculate NDWI from Sentinel-2 image
        
        Args:
            image: GEE Image
            
        Returns:
            GEE Image with NDWI band
        """
        if not self.is_initialized():
            return None
        
        # Sentinel-2 bands: B3=Green, B8=NIR
        ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
        return ndwi
    
    def calculate_evi_sentinel2(self, image: Any) -> Any:
        """
        Calculate Enhanced Vegetation Index (EVI) from Sentinel-2
        
        Args:
            image: GEE Image
            
        Returns:
            GEE Image with EVI band
        """
        if not self.is_initialized():
            return None
        
        # EVI = 2.5 * ((NIR - Red) / (NIR + 6 * Red - 7.5 * Blue + 1))
        evi = image.expression(
            '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
            {
                'NIR': image.select('B8'),
                'RED': image.select('B4'),
                'BLUE': image.select('B2')
            }
        ).rename('EVI')
        
        return evi
    
    def export_image_to_drive(
        self,
        image: Any,
        description: str,
        folder: str = "ResilienceAI",
        region: Optional[Dict] = None,
        scale: float = 10.0,
        crs: str = "EPSG:4326"
    ) -> Any:
        """
        Export image to Google Drive
        
        Args:
            image: GEE Image
            description: Export description
            folder: Drive folder
            region: Export region
            scale: Pixel scale in meters
            crs: Coordinate reference system
            
        Returns:
            GEE Task
        """
        if not self.is_initialized():
            return None
        
        if region is None:
            region = self.MISSOURI_TEST_BBOX
        
        geometry = self.create_geometry(region)
        
        task = self.ee.batch.Export.image.toDrive(
            image=image,
            description=description,
            folder=folder,
            region=geometry,
            scale=scale,
            crs=crs,
            maxPixels=1e13
        )
        
        task.start()
        logger.info(f"Started export task: {description}")
        return task
    
    def export_image_to_cloud_storage(
        self,
        image: Any,
        bucket: str,
        file_name: str,
        region: Optional[Dict] = None,
        scale: float = 10.0,
        crs: str = "EPSG:4326"
    ) -> Any:
        """
        Export image to Google Cloud Storage
        
        Args:
            image: GEE Image
            bucket: GCS bucket name
            file_name: Output file name
            region: Export region
            scale: Pixel scale
            crs: CRS
            
        Returns:
            GEE Task
        """
        if not self.is_initialized():
            return None
        
        if region is None:
            region = self.MISSOURI_TEST_BBOX
        
        geometry = self.create_geometry(region)
        
        task = self.ee.batch.Export.image.toCloudStorage(
            image=image,
            description=file_name,
            bucket=bucket,
            fileNamePrefix=file_name,
            region=geometry,
            scale=scale,
            crs=crs,
            maxPixels=1e13
        )
        
        task.start()
        logger.info(f"Started GCS export task: {file_name}")
        return task
    
    def get_image_thumbnail(
        self,
        image: Any,
        region: Dict[str, float],
        dimensions: Tuple[int, int] = (1024, 1024),
        bands: Optional[List[str]] = None,
        min_val: float = 0,
        max_val: float = 3000
    ) -> Optional[bytes]:
        """
        Get image thumbnail as bytes
        
        Args:
            image: GEE Image
            region: Region to visualize
            dimensions: Image dimensions
            bands: Bands to visualize
            min_val: Min visualization value
            max_val: Max visualization value
            
        Returns:
            Image bytes or None
        """
        if not self.is_initialized():
            return None
        
        try:
            if bands is None:
                bands = ['B4', 'B3', 'B2']  # RGB
            
            vis_params = {
                'bands': bands,
                'min': min_val,
                'max': max_val,
                'dimensions': dimensions,
                'region': self.create_geometry(region)
            }
            
            thumb_url = image.getThumbURL(vis_params)
            
            import requests
            response = requests.get(thumb_url, timeout=60)
            response.raise_for_status()
            return response.content
            
        except Exception as e:
            logger.error(f"Error getting thumbnail: {e}")
            return None
    
    def get_image_info(self, image: Any) -> Dict:
        """
        Get image metadata
        
        Args:
            image: GEE Image
            
        Returns:
            Image metadata dictionary
        """
        if not self.is_initialized():
            return {"error": "GEE not initialized"}
        
        try:
            info = image.getInfo()
            return {
                "id": info.get("id"),
                "bands": [b.get("id") for b in info.get("bands", [])],
                "properties": info.get("properties", {})
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_collection_info(self, collection: Any, limit: int = 10) -> List[Dict]:
        """
        Get info about images in collection
        
        Args:
            collection: GEE ImageCollection
            limit: Max number of images
            
        Returns:
            List of image metadata
        """
        if not self.is_initialized():
            return []
        
        try:
            images = collection.limit(limit).getInfo()
            features = images.get("features", [])
            
            results = []
            for feat in features:
                props = feat.get("properties", {})
                results.append({
                    "id": feat.get("id"),
                    "date": props.get("system:time_start"),
                    "cloud_cover": props.get("CLOUDY_PIXEL_PERCENTAGE") or props.get("CLOUD_COVER")
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return []


class GEEProcessor:
    """Process GEE data locally after download"""
    
    def __init__(self, image_path: Path):
        self.image_path = Path(image_path)
    
    def load_as_array(self, band: Optional[int] = None) -> np.ndarray:
        """
        Load image as numpy array
        
        Args:
            band: Band index (None for all bands)
            
        Returns:
            Numpy array
        """
        with rasterio.open(self.image_path) as src:
            if band is None:
                return src.read()
            return src.read(band)
    
    def create_cloud_optimized_geotiff(
        self,
        output_path: Path,
        overview_levels: List[int] = [2, 4, 8, 16, 32]
    ) -> Path:
        """Convert to COG format"""
        with rasterio.open(self.image_path) as src:
            kwargs = src.meta.copy()
            kwargs.update({
                "driver": "GTiff",
                "compress": "deflate",
                "tiled": True,
                "blockxsize": 512,
                "blockysize": 512,
                "BIGTIFF": "YES"
            })
            
            with rasterio.open(output_path, "w", **kwargs) as dst:
                for i in range(1, src.count + 1):
                    dst.write(src.read(i), i)
                
                dst.build_overviews(overview_levels, Resampling.average)
                dst.update_tags(ns='gdal', OVERVIEWS='YES')
        
        return output_path


class MockGEEClient:
    """Mock GEE client for testing without authentication"""
    
    MISSOURI_TEST_BBOX = {
        "west": -90.5,
        "south": 38.5,
        "east": -90.0,
        "north": 39.0
    }
    
    def __init__(self):
        self._initialized = True
        logger.info("Using Mock GEE Client (no authentication required)")
    
    def initialize(self) -> bool:
        return True
    
    def is_initialized(self) -> bool:
        return True
    
    def create_geometry(self, bbox: Dict[str, float]) -> Dict:
        return bbox
    
    def get_sentinel2_collection(self, *args, **kwargs):
        logger.info("Mock: get_sentinel2_collection called")
        return {"mock": True, "type": "collection"}
    
    def calculate_ndvi_sentinel2(self, image):
        logger.info("Mock: calculate_ndvi_sentinel2 called")
        return {"mock": True, "type": "ndvi"}
    
    def get_image_info(self, image) -> Dict:
        return {
            "mock": True,
            "bands": ["B2", "B3", "B4", "B8"],
            "properties": {"system:time_start": datetime.now().timestamp() * 1000}
        }


def get_gee_client(use_mock: bool = False) -> Union[GEEClient, MockGEEClient]:
    """
    Factory function to get appropriate GEE client
    
    Args:
        use_mock: Force use of mock client
        
    Returns:
        GEE client instance
    """
    if use_mock:
        return MockGEEClient()
    
    client = GEEClient()
    if client.initialize():
        return client
    else:
        return MockGEEClient()


def main():
    """Example usage"""
    # Try to use real GEE, fall back to mock
    client = get_gee_client(use_mock=False)
    
    bbox = client.MISSOURI_TEST_BBOX
    
    # Get Sentinel-2 collection
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    collection = client.get_sentinel2_collection(
        bbox=bbox,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        cloud_cover_threshold=20.0
    )
    
    if collection:
        # Get collection info
        info = client.get_collection_info(collection, limit=5)
        print(f"Found {len(info)} images:")
        for img in info:
            print(f"  - {img['id']}: cloud cover = {img.get('cloud_cover')}")
        
        # Create mosaic
        if hasattr(client, 'calculate_sentinel2_mosaic'):
            mosaic = client.calculate_sentinel2_mosaic(
                bbox=bbox,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )
            
            if mosaic:
                # Calculate NDVI
                ndvi = client.calculate_ndvi_sentinel2(mosaic)
                print(f"NDVI calculated: {ndvi}")


if __name__ == "__main__":
    main()
