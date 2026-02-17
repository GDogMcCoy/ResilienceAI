"""
USDA NAIP Aerial Imagery Handler
Downloads and processes high-resolution aerial imagery from USDA NAIP
"""
import os
import json
import requests
import tempfile
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import logging

import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask
from rasterio.windows import Window
from rasterio.crs import CRS
from rasterio.io import MemoryFile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class NAIPMetadata:
    """NAIP image metadata"""
    year: int
    resolution: float  # meters
    state: str
    quad_name: str
    acquisition_date: Optional[datetime]
    cloud_cover: Optional[float]
    bands: List[str]
    
    @classmethod
    def from_feature(cls, feature: Dict) -> "NAIPMetadata":
        """Create from GeoJSON feature"""
        props = feature.get("properties", {})
        
        # Parse acquisition date
        acq_date = props.get("acquisition_date") or props.get("AcquisitionDate")
        if acq_date:
            try:
                acq_date = datetime.strptime(str(acq_date)[:10], "%Y-%m-%d")
            except:
                acq_date = None
        
        return cls(
            year=int(props.get("year", props.get("Year", datetime.now().year))),
            resolution=float(props.get("resolution", props.get("Resolution", 1.0))),
            state=props.get("state", props.get("State", "Unknown")),
            quad_name=props.get("quad_name", props.get("QuadName", "Unknown")),
            acquisition_date=acq_date,
            cloud_cover=props.get("cloud_cover", props.get("CloudCover")),
            bands=props.get("bands", ["R", "G", "B", "NIR"])
        )


class NAIPClient:
    """Client for USDA NAIP data access"""
    
    # NAIP WMS/TMS endpoints
    WMS_URL = "https://gis.apfo.usda.gov/arcgis/services/NAIP"
    IMAGERY_URL = "https://naip-source.azurewebsites.net"
    
    # Microsoft Planetary Computer STAC API
    PLANETARY_COMPUTER_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
    
    # Collection ID for NAIP
    COLLECTION_ID = "naip"
    
    # Missouri test region
    MISSOURI_TEST_BBOX = (-90.5, 38.5, -90.0, 39.0)  # St. Louis area
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        use_planetary_computer: bool = True
    ):
        self.api_key = api_key
        self.cache_dir = Path(cache_dir) if cache_dir else Path(tempfile.gettempdir()) / "naip_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.use_planetary_computer = use_planetary_computer
        
        # Set headers for Planetary Computer
        if use_planetary_computer:
            self.session.headers.update({
                "Accept": "application/json"
            })
    
    def search_stac(
        self,
        bbox: Tuple[float, float, float, float],
        datetime_range: Optional[str] = None,
        max_items: int = 100
    ) -> List[Dict]:
        """
        Search NAIP imagery using Microsoft Planetary Computer STAC API
        
        Args:
            bbox: Bounding box (min_x, min_y, max_x, max_y)
            datetime_range: ISO datetime range (e.g., "2020-01-01/2023-12-31")
            max_items: Maximum items to return
            
        Returns:
            List of STAC items
        """
        url = f"{self.PLANETARY_COMPUTER_URL}/search"
        
        params = {
            "collections": [self.COLLECTION_ID],
            "bbox": list(bbox),
            "limit": min(max_items, 1000)
        }
        
        if datetime_range:
            params["datetime"] = datetime_range
        
        try:
            response = self.session.post(
                url,
                json=params,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            features = data.get("features", [])
            logger.info(f"Found {len(features)} NAIP items for bbox {bbox}")
            return features
            
        except requests.RequestException as e:
            logger.error(f"Error searching NAIP STAC: {e}")
            return []
    
    def get_item_assets(self, item: Dict) -> Dict[str, str]:
        """
        Get download URLs for item assets
        
        Args:
            item: STAC item
            
        Returns:
            Dictionary of asset names to URLs
        """
        assets = item.get("assets", {})
        urls = {}
        
        for name, asset in assets.items():
            href = asset.get("href")
            if href:
                urls[name] = href
        
        return urls
    
    def download_image(
        self,
        image_url: str,
        output_path: Optional[Path] = None,
        use_cache: bool = True,
        sign_url: bool = True
    ) -> Optional[Path]:
        """
        Download NAIP image
        
        Args:
            image_url: URL to image (may need signing for Planetary Computer)
            output_path: Where to save
            use_cache: Use cached file if exists
            sign_url: Sign URL for Planetary Computer access
            
        Returns:
            Path to downloaded file
        """
        # Sign URL if needed
        if sign_url and "planetarycomputer" in image_url:
            image_url = self._sign_planetary_computer_url(image_url)
        
        # Generate cache filename
        url_hash = str(hash(image_url)) + ".tif"
        cache_path = self.cache_dir / url_hash
        
        if use_cache and cache_path.exists():
            logger.info(f"Using cached NAIP image: {cache_path}")
            return cache_path
        
        if output_path is None:
            output_path = cache_path
        
        try:
            logger.info(f"Downloading NAIP image from {image_url[:80]}...")
            response = self.session.get(image_url, stream=True, timeout=300)
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as tmp:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp.write(chunk)
                tmp_path = tmp.name
            
            Path(tmp_path).rename(output_path)
            logger.info(f"Downloaded NAIP image to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error downloading NAIP image: {e}")
            return None
    
    def _sign_planetary_computer_url(self, url: str) -> str:
        """Sign URL for Planetary Computer access"""
        try:
            sign_url = f"{self.PLANETARY_COMPUTER_URL}/sign"
            response = self.session.get(sign_url, params={"href": url}, timeout=30)
            response.raise_for_status()
            return response.json().get("href", url)
        except:
            return url
    
    def download_area(
        self,
        bbox: Tuple[float, float, float, float],
        output_dir: Path,
        year: Optional[int] = None,
        merge_tiles: bool = True,
        max_cloud_cover: float = 10.0
    ) -> List[Path]:
        """
        Download all NAIP tiles for an area
        
        Args:
            bbox: Bounding box
            output_dir: Directory to save files
            year: Filter by year
            merge_tiles: Whether to merge tiles
            max_cloud_cover: Maximum cloud cover percentage
            
        Returns:
            List of downloaded file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Build datetime filter
        if year:
            datetime_range = f"{year}-01-01/{year}-12-31"
        else:
            datetime_range = "2020-01-01/2024-12-31"
        
        items = self.search_stac(bbox, datetime_range)
        downloaded = []
        
        for item in items:
            # Check cloud cover
            props = item.get("properties", {})
            cloud_cover = props.get("eo:cloud_cover", 0)
            if cloud_cover is not None and cloud_cover > max_cloud_cover:
                continue
            
            # Get image URL
            assets = self.get_item_assets(item)
            image_url = assets.get("image") or assets.get("data")
            
            if not image_url:
                continue
            
            # Create filename
            item_id = item.get("id", "naip")
            filename = f"{item_id}.tif"
            output_path = output_dir / filename
            
            result = self.download_image(image_url, output_path)
            if result:
                downloaded.append(result)
        
        if merge_tiles and len(downloaded) > 1:
            merged_path = output_dir / "merged_naip.tif"
            self._merge_tiles(downloaded, merged_path)
            return [merged_path]
        
        return downloaded
    
    def _merge_tiles(
        self,
        tile_paths: List[Path],
        output_path: Path
    ) -> Path:
        """Merge NAIP tiles"""
        logger.info(f"Merging {len(tile_paths)} NAIP tiles")
        
        src_files = []
        try:
            for path in tile_paths:
                src = rasterio.open(path)
                src_files.append(src)
            
            mosaic, out_transform = merge(src_files)
            
            out_meta = src_files[0].meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": mosaic.shape[1],
                "width": mosaic.shape[2],
                "transform": out_transform,
                "compress": "lzw",
                "tiled": True,
                "blockxsize": 256,
                "blockysize": 256
            })
            
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(mosaic)
            
            logger.info(f"Merged NAIP saved to {output_path}")
            return output_path
            
        finally:
            for src in src_files:
                src.close()
    
    def create_cloud_optimized_geotiff(
        self,
        input_path: Path,
        output_path: Path,
        overview_levels: List[int] = [2, 4, 8, 16, 32, 64]
    ) -> Path:
        """Convert NAIP image to COG format"""
        logger.info(f"Creating COG from {input_path}")
        
        with rasterio.open(input_path) as src:
            kwargs = src.meta.copy()
            kwargs.update({
                "driver": "GTiff",
                "compress": "jpeg",
                "jpeg_quality": 90,
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
        
        logger.info(f"NAIP COG created at {output_path}")
        return output_path


class NAIPProcessor:
    """Process NAIP imagery for analysis"""
    
    # Band indices for 4-band NAIP (RGBN)
    BAND_RED = 1
    BAND_GREEN = 2
    BAND_BLUE = 3
    BAND_NIR = 4
    
    def __init__(self, image_path: Path):
        self.image_path = Path(image_path)
        self._src = None
    
    def __enter__(self):
        self._src = rasterio.open(self.image_path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._src:
            self._src.close()
            self._src = None
    
    @property
    def src(self):
        if self._src is None:
            raise RuntimeError("NAIPProcessor not opened as context manager")
        return self._src
    
    def calculate_ndvi(self, output_path: Path) -> Path:
        """
        Calculate Normalized Difference Vegetation Index (NDVI)
        NDVI = (NIR - Red) / (NIR + Red)
        
        Args:
            output_path: Output file path
            
        Returns:
            Path to NDVI raster
        """
        red = self.src.read(self.BAND_RED).astype(np.float32)
        nir = self.src.read(self.BAND_NIR).astype(np.float32)
        
        # Calculate NDVI
        denominator = nir + red
        ndvi = np.where(
            denominator > 0,
            (nir - red) / denominator,
            0
        )
        
        # Clip to valid range
        ndvi = np.clip(ndvi, -1, 1)
        
        # Write output
        kwargs = self.src.meta.copy()
        kwargs.update({
            "count": 1,
            "dtype": "float32",
            "compress": "lzw",
            "nodata": -9999
        })
        
        with rasterio.open(output_path, "w", **kwargs) as dst:
            dst.write(ndvi, 1)
            dst.update_tags(description="NDVI")
        
        logger.info(f"NDVI calculated: {output_path}")
        return output_path
    
    def calculate_ndwi(self, output_path: Path) -> Path:
        """
        Calculate Normalized Difference Water Index (NDWI)
        NDWI = (Green - NIR) / (Green + NIR)
        
        Args:
            output_path: Output file path
            
        Returns:
            Path to NDWI raster
        """
        green = self.src.read(self.BAND_GREEN).astype(np.float32)
        nir = self.src.read(self.BAND_NIR).astype(np.float32)
        
        # Calculate NDWI
        denominator = green + nir
        ndwi = np.where(
            denominator > 0,
            (green - nir) / denominator,
            0
        )
        
        # Clip to valid range
        ndwi = np.clip(ndwi, -1, 1)
        
        # Write output
        kwargs = self.src.meta.copy()
        kwargs.update({
            "count": 1,
            "dtype": "float32",
            "compress": "lzw",
            "nodata": -9999
        })
        
        with rasterio.open(output_path, "w", **kwargs) as dst:
            dst.write(ndwi, 1)
            dst.update_tags(description="NDWI")
        
        logger.info(f"NDWI calculated: {output_path}")
        return output_path
    
    def calculate_texture(
        self,
        output_path: Path,
        window_size: int = 5,
        method: str = "contrast"
    ) -> Path:
        """
        Calculate texture metrics from imagery
        
        Args:
            output_path: Output file path
            window_size: GLCM window size
            method: Texture method (contrast, dissimilarity, homogeneity, energy, correlation)
            
        Returns:
            Path to texture raster
        """
        from skimage.feature import graycomatrix, graycoprops
        from scipy import ndimage
        
        # Use NIR band for texture
        band = self.src.read(self.BAND_NIR).astype(np.uint8)
        
        # Calculate texture using sliding window
        texture = np.zeros_like(band, dtype=np.float32)
        
        # Simple texture measure - local standard deviation
        texture = ndimage.generic_filter(
            band.astype(np.float32),
            np.std,
            size=window_size
        )
        
        # Normalize
        texture = (texture - texture.min()) / (texture.max() - texture.min() + 1e-8)
        
        # Write output
        kwargs = self.src.meta.copy()
        kwargs.update({
            "count": 1,
            "dtype": "float32",
            "compress": "lzw",
            "nodata": 0
        })
        
        with rasterio.open(output_path, "w", **kwargs) as dst:
            dst.write(texture, 1)
            dst.update_tags(description=f"Texture ({method})")
        
        logger.info(f"Texture calculated: {output_path}")
        return output_path
    
    def create_false_color_composite(
        self,
        output_path: Path,
        composite_type: str = "nir"
    ) -> Path:
        """
        Create false color composite
        
        Args:
            output_path: Output file path
            composite_type: Type of composite (nir, agriculture, urban)
            
        Returns:
            Path to composite image
        """
        if composite_type == "nir":
            # NIR-Red-Green
            bands = [self.BAND_NIR, self.BAND_RED, self.BAND_GREEN]
        elif composite_type == "agriculture":
            # NIR-SWIR1-Red (if available) or NIR-Red-Green
            bands = [self.BAND_NIR, self.BAND_RED, self.BAND_GREEN]
        elif composite_type == "urban":
            # SWIR2-SWIR1-Red or NIR-Green-Blue
            bands = [self.BAND_NIR, self.BAND_GREEN, self.BAND_BLUE]
        else:
            bands = [self.BAND_NIR, self.BAND_RED, self.BAND_GREEN]
        
        # Read bands
        data = np.stack([self.src.read(b) for b in bands])
        
        # Scale to 8-bit if needed
        if data.dtype != np.uint8:
            data = (data / data.max() * 255).astype(np.uint8)
        
        # Write output
        kwargs = self.src.meta.copy()
        kwargs.update({
            "count": 3,
            "dtype": "uint8",
            "compress": "jpeg",
            "jpeg_quality": 95,
            "photometric": "RGB"
        })
        
        with rasterio.open(output_path, "w", **kwargs) as dst:
            dst.write(data)
            dst.update_tags(description=f"False color composite ({composite_type})")
        
        logger.info(f"False color composite created: {output_path}")
        return output_path
    
    def detect_water_bodies(self, output_path: Path, threshold: float = 0.3) -> Path:
        """
        Detect water bodies using NDWI
        
        Args:
            output_path: Output file path
            threshold: NDWI threshold for water
            
        Returns:
            Path to water mask
        """
        green = self.src.read(self.BAND_GREEN).astype(np.float32)
        nir = self.src.read(self.BAND_NIR).astype(np.float32)
        
        # Calculate NDWI
        denominator = green + nir
        ndwi = np.where(
            denominator > 0,
            (green - nir) / denominator,
            0
        )
        
        # Create water mask
        water_mask = (ndwi > threshold).astype(np.uint8)
        
        # Write output
        kwargs = self.src.meta.copy()
        kwargs.update({
            "count": 1,
            "dtype": "uint8",
            "compress": "lzw",
            "nodata": 255
        })
        
        with rasterio.open(output_path, "w", **kwargs) as dst:
            dst.write(water_mask, 1)
            dst.update_tags(description="Water mask")
        
        logger.info(f"Water mask created: {output_path}")
        return output_path
    
    def get_image_stats(self) -> Dict:
        """Get image statistics"""
        stats = {}
        
        band_names = ["Red", "Green", "Blue", "NIR"]
        for i, name in enumerate(band_names[:self.src.count]):
            band = self.src.read(i + 1)
            stats[name] = {
                "min": int(np.min(band)),
                "max": int(np.max(band)),
                "mean": float(np.mean(band)),
                "std": float(np.std(band))
            }
        
        stats["crs"] = str(self.src.crs)
        stats["resolution"] = (abs(self.src.transform.a), abs(self.src.transform.e))
        stats["shape"] = (self.src.height, self.src.width)
        
        return stats


def main():
    """Example usage"""
    client = NAIPClient()
    
    # Missouri test region
    bbox = client.MISSOURI_TEST_BBOX
    
    # Search for imagery
    items = client.search_stac(bbox, max_items=10)
    print(f"Found {len(items)} NAIP items")
    
    if items:
        output_dir = Path("/tmp/naip_test")
        output_dir.mkdir(exist_ok=True)
        
        # Download first item
        assets = client.get_item_assets(items[0])
        image_url = assets.get("image")
        
        if image_url:
            image_path = client.download_image(image_url, output_dir / "naip.tif")
            
            if image_path:
                with NAIPProcessor(image_path) as processor:
                    # Get stats
                    stats = processor.get_image_stats()
                    print(f"Image stats: {stats}")
                    
                    # Calculate indices
                    processor.calculate_ndvi(output_dir / "ndvi.tif")
                    processor.calculate_ndwi(output_dir / "ndwi.tif")
                    processor.calculate_texture(output_dir / "texture.tif")
                    processor.create_false_color_composite(
                        output_dir / "false_color.tif",
                        composite_type="nir"
                    )
                    processor.detect_water_bodies(output_dir / "water.tif")
                    
                    # Create COG
                    client.create_cloud_optimized_geotiff(
                        image_path,
                        output_dir / "naip_cog.tif"
                    )


if __name__ == "__main__":
    main()
