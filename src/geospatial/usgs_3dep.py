"""
USGS 3DEP 1m DEM Data Handler
Downloads and processes Digital Elevation Model data from USGS National Map API
"""
import os
import json
import requests
import tempfile
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import logging

import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.io import MemoryFile
from rasterio.crs import CRS
from rasterio.windows import Window

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BoundingBox:
    """Geographic bounding box"""
    min_x: float  # West
    min_y: float  # South
    max_x: float  # East
    max_y: float  # North
    
    def to_wkt(self) -> str:
        """Convert to WKT polygon"""
        return f"POLYGON(({self.min_x} {self.min_y}, {self.max_x} {self.min_y}, {self.max_x} {self.max_y}, {self.min_x} {self.max_y}, {self.min_x} {self.min_y}))"
    
    def to_list(self) -> List[float]:
        """Return as [min_x, min_y, max_x, max_y]"""
        return [self.min_x, self.min_y, self.max_x, self.max_y]
    
    @property
    def center(self) -> Tuple[float, float]:
        """Get center point"""
        return ((self.min_x + self.max_x) / 2, (self.min_y + self.max_y) / 2)
    
    @property
    def area(self) -> float:
        """Approximate area in square degrees"""
        return (self.max_x - self.min_x) * (self.max_y - self.min_y)


class USGS3DEPClient:
    """Client for USGS 3DEP National Map API"""
    
    BASE_URL = "https://tnmaccess.nationalmap.gov/api/v1"
    PRODUCT_TAG = "Digital Elevation Model (DEM) 1 meter"
    
    # Missouri test region - St. Louis area
    MISSOURI_TEST_BBOX = BoundingBox(
        min_x=-90.5,
        min_y=38.5,
        max_x=-90.0,
        max_y=39.0
    )
    
    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[str] = None):
        self.api_key = api_key
        self.cache_dir = Path(cache_dir) if cache_dir else Path(tempfile.gettempdir()) / "usgs_3dep_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        
    def search_products(
        self, 
        bbox: BoundingBox,
        max_results: int = 100
    ) -> List[Dict]:
        """
        Search for 3DEP 1m DEM products within bounding box
        
        Args:
            bbox: Geographic bounding box
            max_results: Maximum number of results
            
        Returns:
            List of product metadata dictionaries
        """
        url = f"{self.BASE_URL}/products"
        
        params = {
            "bbox": ",".join(map(str, bbox.to_list())),
            "prodFormats": "GeoTIFF",
            "prodExtents": "1 x 1 degree",
            "max": max_results,
            "offset": 0,
            "q": self.PRODUCT_TAG
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            items = data.get("items", [])
            logger.info(f"Found {len(items)} 3DEP products for bbox {bbox.to_list()}")
            return items
            
        except requests.RequestException as e:
            logger.error(f"Error searching 3DEP products: {e}")
            return []
    
    def download_dem(
        self, 
        product_url: str, 
        output_path: Optional[Path] = None,
        use_cache: bool = True
    ) -> Optional[Path]:
        """
        Download a single DEM file
        
        Args:
            product_url: URL to download
            output_path: Where to save (None for cache)
            use_cache: Use cached file if exists
            
        Returns:
            Path to downloaded file or None if failed
        """
        # Generate cache filename from URL
        url_hash = str(hash(product_url)) + ".tif"
        cache_path = self.cache_dir / url_hash
        
        if use_cache and cache_path.exists():
            logger.info(f"Using cached DEM: {cache_path}")
            return cache_path
        
        if output_path is None:
            output_path = cache_path
        
        try:
            logger.info(f"Downloading DEM from {product_url}")
            response = self.session.get(product_url, stream=True, timeout=120)
            response.raise_for_status()
            
            # Check if it's a zip file
            content_type = response.headers.get('content-type', '')
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.download') as tmp:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp.write(chunk)
                tmp_path = tmp.name
            
            # Handle zip files
            if 'zip' in content_type or product_url.endswith('.zip'):
                import zipfile
                with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                    # Find the TIF file in the archive
                    tif_files = [f for f in zip_ref.namelist() if f.endswith('.tif')]
                    if tif_files:
                        zip_ref.extract(tif_files[0], self.cache_dir)
                        extracted_path = self.cache_dir / tif_files[0]
                        extracted_path.rename(output_path)
            else:
                Path(tmp_path).rename(output_path)
            
            os.unlink(tmp_path) if os.path.exists(tmp_path) else None
            logger.info(f"Downloaded DEM to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error downloading DEM: {e}")
            return None
    
    def download_area(
        self,
        bbox: BoundingBox,
        output_dir: Path,
        merge_tiles: bool = True
    ) -> List[Path]:
        """
        Download all DEM tiles for an area
        
        Args:
            bbox: Geographic bounding box
            output_dir: Directory to save files
            merge_tiles: Whether to merge tiles into single file
            
        Returns:
            List of downloaded file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        products = self.search_products(bbox)
        downloaded = []
        
        for product in products:
            download_url = product.get("downloadURL")
            if not download_url:
                continue
            
            # Create filename from product info
            filename = f"{product.get('title', 'dem')}.tif"
            output_path = output_dir / filename
            
            result = self.download_dem(download_url, output_path)
            if result:
                downloaded.append(result)
        
        if merge_tiles and len(downloaded) > 1:
            merged_path = output_dir / "merged_dem.tif"
            self._merge_tiles(downloaded, merged_path)
            return [merged_path]
        
        return downloaded
    
    def _merge_tiles(
        self, 
        tile_paths: List[Path], 
        output_path: Path,
        method: str = "first"
    ) -> Path:
        """
        Merge multiple DEM tiles into single file
        
        Args:
            tile_paths: List of tile paths
            output_path: Output file path
            method: Merge method (first, last, min, max, mean)
            
        Returns:
            Path to merged file
        """
        logger.info(f"Merging {len(tile_paths)} tiles into {output_path}")
        
        src_files = []
        try:
            for path in tile_paths:
                src = rasterio.open(path)
                src_files.append(src)
            
            # Merge
            mosaic, out_transform = merge(src_files, method=method)
            
            # Copy metadata from first file
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
            
            # Write output
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(mosaic)
            
            logger.info(f"Merged DEM saved to {output_path}")
            return output_path
            
        finally:
            for src in src_files:
                src.close()
    
    def create_cloud_optimized_geotiff(
        self,
        input_path: Path,
        output_path: Path,
        overview_levels: List[int] = [2, 4, 8, 16, 32]
    ) -> Path:
        """
        Convert DEM to Cloud-Optimized GeoTIFF format
        
        Args:
            input_path: Input DEM path
            output_path: Output COG path
            overview_levels: Pyramid overview levels
            
        Returns:
            Path to COG file
        """
        logger.info(f"Creating COG from {input_path}")
        
        with rasterio.open(input_path) as src:
            # Copy to new file with proper COG settings
            kwargs = src.meta.copy()
            kwargs.update({
                "driver": "GTiff",
                "compress": "deflate",
                "predictor": 2,
                "tiled": True,
                "blockxsize": 512,
                "blockysize": 512,
                "BIGTIFF": "YES"
            })
            
            with rasterio.open(output_path, "w", **kwargs) as dst:
                # Copy data
                for i in range(1, src.count + 1):
                    dst.write(src.read(i), i)
                
                # Copy colormap if exists
                if src.colormaps():
                    dst.write_colormap(1, src.colormap(1))
                
                # Build overviews
                dst.build_overviews(overview_levels, Resampling.nearest)
                dst.update_tags(ns='gdal', OVERVIEWS='YES')
        
        logger.info(f"COG created at {output_path}")
        return output_path


class DEMProcessor:
    """Process DEM data to derive terrain products"""
    
    def __init__(self, dem_path: Path):
        self.dem_path = Path(dem_path)
        self._src = None
    
    def __enter__(self):
        self._src = rasterio.open(self.dem_path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._src:
            self._src.close()
            self._src = None
    
    @property
    def src(self):
        if self._src is None:
            raise RuntimeError("DEMProcessor not opened as context manager")
        return self._src
    
    def calculate_slope(
        self, 
        output_path: Path,
        units: str = "degrees"
    ) -> Path:
        """
        Calculate slope from DEM
        
        Args:
            output_path: Output file path
            units: 'degrees' or 'percent'
            
        Returns:
            Path to slope raster
        """
        from scipy import ndimage
        
        dem = self.src.read(1).astype(np.float32)
        
        # Get pixel size
        pixel_size_x = abs(self.src.transform.a)
        pixel_size_y = abs(self.src.transform.e)
        
        # Calculate gradients
        dz_dx = ndimage.sobel(dem, axis=1) / (8 * pixel_size_x)
        dz_dy = ndimage.sobel(dem, axis=0) / (8 * pixel_size_y)
        
        # Calculate slope
        slope = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
        
        if units == "degrees":
            slope = np.degrees(slope)
        elif units == "percent":
            slope = np.tan(slope) * 100
        
        # Write output
        kwargs = self.src.meta.copy()
        kwargs.update({
            "dtype": "float32",
            "compress": "lzw",
            "nodata": -9999
        })
        
        with rasterio.open(output_path, "w", **kwargs) as dst:
            dst.write(slope, 1)
            dst.update_tags(description="Slope", units=units)
        
        logger.info(f"Slope calculated: {output_path}")
        return output_path
    
    def calculate_aspect(self, output_path: Path) -> Path:
        """
        Calculate aspect (direction of slope) from DEM
        
        Args:
            output_path: Output file path
            
        Returns:
            Path to aspect raster
        """
        from scipy import ndimage
        
        dem = self.src.read(1).astype(np.float32)
        
        # Get pixel size
        pixel_size_x = abs(self.src.transform.a)
        pixel_size_y = abs(self.src.transform.e)
        
        # Calculate gradients
        dz_dx = ndimage.sobel(dem, axis=1) / (8 * pixel_size_x)
        dz_dy = ndimage.sobel(dem, axis=0) / (8 * pixel_size_y)
        
        # Calculate aspect (0-360 degrees, -1 for flat)
        aspect = np.degrees(np.arctan2(dz_dy, -dz_dx))
        aspect = np.where(aspect < 0, 90.0 - aspect, 360.0 - aspect + 90.0)
        aspect = np.where(aspect >= 360.0, aspect - 360.0, aspect)
        
        # Mark flat areas as -1
        slope = np.sqrt(dz_dx**2 + dz_dy**2)
        aspect = np.where(slope == 0, -1, aspect)
        
        # Write output
        kwargs = self.src.meta.copy()
        kwargs.update({
            "dtype": "float32",
            "compress": "lzw",
            "nodata": -1
        })
        
        with rasterio.open(output_path, "w", **kwargs) as dst:
            dst.write(aspect, 1)
            dst.update_tags(description="Aspect", units="degrees")
        
        logger.info(f"Aspect calculated: {output_path}")
        return output_path
    
    def calculate_hillshade(
        self, 
        output_path: Path,
        azimuth: float = 315.0,
        altitude: float = 45.0
    ) -> Path:
        """
        Calculate hillshade from DEM
        
        Args:
            output_path: Output file path
            azimuth: Sun azimuth angle (degrees)
            altitude: Sun altitude angle (degrees)
            
        Returns:
            Path to hillshade raster
        """
        from scipy import ndimage
        
        dem = self.src.read(1).astype(np.float32)
        
        # Get pixel size
        pixel_size_x = abs(self.src.transform.a)
        pixel_size_y = abs(self.src.transform.e)
        
        # Calculate gradients
        dz_dx = ndimage.sobel(dem, axis=1) / (8 * pixel_size_x)
        dz_dy = ndimage.sobel(dem, axis=0) / (8 * pixel_size_y)
        
        # Convert angles to radians
        azimuth_rad = np.radians(360.0 - azimuth + 90.0)
        altitude_rad = np.radians(altitude)
        
        # Calculate slope and aspect
        slope = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
        aspect = np.arctan2(dz_dy, -dz_dx)
        
        # Calculate hillshade
        hillshade = 255.0 * (
            np.sin(altitude_rad) * np.cos(slope) +
            np.cos(altitude_rad) * np.sin(slope) * np.cos(azimuth_rad - aspect)
        )
        
        # Clip to 0-255
        hillshade = np.clip(hillshade, 0, 255).astype(np.uint8)
        
        # Write output
        kwargs = self.src.meta.copy()
        kwargs.update({
            "dtype": "uint8",
            "compress": "lzw",
            "nodata": 0
        })
        
        with rasterio.open(output_path, "w", **kwargs) as dst:
            dst.write(hillshade, 1)
            dst.update_tags(
                description="Hillshade",
                azimuth=str(azimuth),
                altitude=str(altitude)
            )
        
        logger.info(f"Hillshade calculated: {output_path}")
        return output_path
    
    def calculate_tpi(
        self, 
        output_path: Path,
        window_size: int = 3
    ) -> Path:
        """
        Calculate Topographic Position Index (TPI)
        
        TPI = elevation - mean elevation in neighborhood
        Positive values = ridges/peaks
        Negative values = valleys/depressions
        
        Args:
            output_path: Output file path
            window_size: Neighborhood window size (odd number)
            
        Returns:
            Path to TPI raster
        """
        from scipy import ndimage
        
        dem = self.src.read(1).astype(np.float32)
        
        # Calculate mean in neighborhood
        kernel = np.ones((window_size, window_size)) / (window_size ** 2)
        mean_elev = ndimage.convolve(dem, kernel, mode='nearest')
        
        # Calculate TPI
        tpi = dem - mean_elev
        
        # Write output
        kwargs = self.src.meta.copy()
        kwargs.update({
            "dtype": "float32",
            "compress": "lzw",
            "nodata": -9999
        })
        
        with rasterio.open(output_path, "w", **kwargs) as dst:
            dst.write(tpi, 1)
            dst.update_tags(
                description="Topographic Position Index",
                window_size=str(window_size)
            )
        
        logger.info(f"TPI calculated: {output_path}")
        return output_path
    
    def get_elevation_stats(self) -> Dict:
        """Get statistics for the DEM"""
        dem = self.src.read(1)
        nodata = self.src.nodata
        
        # Mask nodata
        if nodata is not None:
            dem = np.ma.masked_equal(dem, nodata)
        
        return {
            "min": float(np.min(dem)),
            "max": float(np.max(dem)),
            "mean": float(np.mean(dem)),
            "std": float(np.std(dem)),
            "crs": str(self.src.crs),
            "resolution": (abs(self.src.transform.a), abs(self.src.transform.e)),
            "shape": dem.shape
        }


def main():
    """Example usage"""
    # Initialize client
    client = USGS3DEPClient()
    
    # Use Missouri test region
    bbox = client.MISSOURI_TEST_BBOX
    
    # Search for products
    products = client.search_products(bbox)
    print(f"Found {len(products)} products")
    
    if products:
        # Download first product
        output_dir = Path("/tmp/usgs_3dep_test")
        output_dir.mkdir(exist_ok=True)
        
        downloaded = client.download_area(bbox, output_dir, merge_tiles=True)
        print(f"Downloaded {len(downloaded)} files")
        
        # Process DEM
        if downloaded:
            dem_path = downloaded[0]
            
            with DEMProcessor(dem_path) as processor:
                # Get stats
                stats = processor.get_elevation_stats()
                print(f"Elevation stats: {stats}")
                
                # Calculate derivatives
                processor.calculate_slope(output_dir / "slope.tif")
                processor.calculate_aspect(output_dir / "aspect.tif")
                processor.calculate_hillshade(output_dir / "hillshade.tif")
                processor.calculate_tpi(output_dir / "tpi.tif")
                
                # Create COG
                client.create_cloud_optimized_geotiff(
                    dem_path,
                    output_dir / "dem_cog.tif"
                )


if __name__ == "__main__":
    main()
