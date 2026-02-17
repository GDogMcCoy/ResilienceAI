"""
Main Geospatial Pipeline for ResilienceAI
Integrates USGS 3DEP, NAIP, and GEE data sources
"""
import os
import json
import tempfile
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
import logging
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask
from rasterio.crs import CRS
from rasterio.io import MemoryFile

# Fix imports for standalone execution
import sys
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    from usgs_3dep import USGS3DEPClient, DEMProcessor, BoundingBox
    from naip import NAIPClient, NAIPProcessor
    from gee_integration import GEEClient, get_gee_client
else:
    from .usgs_3dep import USGS3DEPClient, DEMProcessor, BoundingBox
    from .naip import NAIPClient, NAIPProcessor
    from .gee_integration import GEEClient, get_gee_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Available data sources"""
    USGS_3DEP = "usgs_3dep"
    NAIP = "naip"
    SENTINEL2 = "sentinel2"
    LANDSAT = "landsat"
    MICROSOFT_BUILDINGS = "microsoft_buildings"


class ProcessingStep(Enum):
    """Available processing steps"""
    SLOPE = "slope"
    ASPECT = "aspect"
    HILLSHADE = "hillshade"
    TPI = "tpi"
    NDVI = "ndvi"
    NDWI = "ndwi"
    TEXTURE = "texture"
    WATER_MASK = "water_mask"
    LAND_COVER = "land_cover"


@dataclass
class PipelineConfig:
    """Pipeline configuration"""
    # Data sources to use
    sources: List[DataSource] = field(default_factory=lambda: [
        DataSource.USGS_3DEP,
        DataSource.NAIP,
        DataSource.SENTINEL2
    ])
    
    # Processing steps to run
    processing_steps: List[ProcessingStep] = field(default_factory=lambda: [
        ProcessingStep.SLOPE,
        ProcessingStep.ASPECT,
        ProcessingStep.HILLSHADE,
        ProcessingStep.NDVI,
        ProcessingStep.NDWI
    ])
    
    # Output settings
    output_dir: Path = field(default_factory=lambda: Path("/tmp/resilienceai_geospatial"))
    create_cogs: bool = True
    cache_enabled: bool = True
    
    # Parallel processing
    max_workers: int = 4
    
    # GEE settings
    gee_project_id: Optional[str] = None
    use_mock_gee: bool = False


@dataclass
class PipelineResult:
    """Result from pipeline execution"""
    success: bool
    data_products: Dict[str, Path] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0


class GeospatialPipeline:
    """
    Main geospatial data pipeline for ResilienceAI
    
    Coordinates data acquisition from multiple sources (USGS 3DEP, NAIP, GEE)
    and runs processing workflows to generate analysis-ready products.
    """
    
    # Missouri test region (St. Louis area)
    DEFAULT_BBOX = BoundingBox(
        min_x=-90.5,
        min_y=38.5,
        max_x=-90.0,
        max_y=39.0
    )
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.config.output_dir = Path(self.config.output_dir)
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize clients
        self.usgs_client = USGS3DEPClient(cache_dir=str(self.config.output_dir / "cache" / "usgs"))
        self.naip_client = NAIPClient(cache_dir=str(self.config.output_dir / "cache" / "naip"))
        self.gee_client = get_gee_client(use_mock=self.config.use_mock_gee)
        
        # Cache for processed products
        self._product_cache: Dict[str, Path] = {}
    
    def run(
        self,
        bbox: Optional[BoundingBox] = None,
        region_name: str = "missouri_test"
    ) -> PipelineResult:
        """
        Run the full pipeline
        
        Args:
            bbox: Geographic bounding box (default: Missouri test region)
            region_name: Name for output files
            
        Returns:
            PipelineResult with all products
        """
        import time
        start_time = time.time()
        
        if bbox is None:
            bbox = self.DEFAULT_BBOX
        
        logger.info(f"Starting geospatial pipeline for region: {region_name}")
        logger.info(f"Bounding box: {bbox.to_list()}")
        
        result = PipelineResult(success=True)
        
        try:
            # Step 1: Data Acquisition
            logger.info("Step 1: Data Acquisition")
            raw_data = self._acquire_data(bbox, region_name)
            result.data_products.update(raw_data)
            
            # Step 2: Processing
            logger.info("Step 2: Processing")
            processed = self._process_data(raw_data, region_name)
            result.data_products.update(processed)
            
            # Step 3: Create COGs
            if self.config.create_cogs:
                logger.info("Step 3: Creating Cloud-Optimized GeoTIFFs")
                cogs = self._create_cogs(result.data_products, region_name)
                result.data_products.update(cogs)
            
            # Step 4: Generate metadata
            logger.info("Step 4: Generating metadata")
            result.metadata = self._generate_metadata(bbox, result.data_products)
            
            result.success = True
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            result.success = False
            result.errors.append(str(e))
        
        result.execution_time = time.time() - start_time
        logger.info(f"Pipeline completed in {result.execution_time:.2f} seconds")
        
        return result
    
    def _acquire_data(
        self,
        bbox: BoundingBox,
        region_name: str
    ) -> Dict[str, Path]:
        """
        Acquire data from all configured sources
        
        Args:
            bbox: Bounding box
            region_name: Region name
            
        Returns:
            Dictionary of data products
        """
        products = {}
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = {}
            
            # Schedule USGS 3DEP download
            if DataSource.USGS_3DEP in self.config.sources:
                futures[executor.submit(
                    self._download_usgs_3dep, bbox, region_name
                )] = "usgs_3dep"
            
            # Schedule NAIP download
            if DataSource.NAIP in self.config.sources:
                futures[executor.submit(
                    self._download_naip, bbox, region_name
                )] = "naip"
            
            # Schedule GEE download
            if DataSource.SENTINEL2 in self.config.sources:
                futures[executor.submit(
                    self._download_sentinel2, bbox, region_name
                )] = "sentinel2"
            
            # Collect results
            for future in as_completed(futures):
                source = futures[future]
                try:
                    result = future.result()
                    if result:
                        products.update(result)
                except Exception as e:
                    logger.error(f"Error acquiring {source}: {e}")
        
        return products
    
    def _download_usgs_3dep(
        self,
        bbox: BoundingBox,
        region_name: str
    ) -> Dict[str, Path]:
        """Download USGS 3DEP DEM data"""
        output_dir = self.config.output_dir / region_name / "dem"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Downloading USGS 3DEP data...")
        
        downloaded = self.usgs_client.download_area(
            bbox=bbox,
            output_dir=output_dir,
            merge_tiles=True
        )
        
        if downloaded:
            return {"dem": downloaded[0]}
        return {}
    
    def _download_naip(
        self,
        bbox: BoundingBox,
        region_name: str
    ) -> Dict[str, Path]:
        """Download NAIP imagery"""
        output_dir = self.config.output_dir / region_name / "naip"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Downloading NAIP imagery...")
        
        downloaded = self.naip_client.download_area(
            bbox=tuple(bbox.to_list()),
            output_dir=output_dir,
            merge_tiles=True,
            max_cloud_cover=10.0
        )
        
        if downloaded:
            return {"naip": downloaded[0]}
        return {}
    
    def _download_sentinel2(
        self,
        bbox: BoundingBox,
        region_name: str
    ) -> Dict[str, Path]:
        """Download Sentinel-2 data via GEE"""
        output_dir = self.config.output_dir / region_name / "sentinel2"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Downloading Sentinel-2 data via GEE...")
        
        if not self.gee_client.is_initialized():
            logger.warning("GEE not initialized, skipping Sentinel-2 download")
            return {}
        
        # For actual download, we would export from GEE
        # For now, return empty (GEE data stays in cloud)
        return {}
    
    def _process_data(
        self,
        raw_data: Dict[str, Path],
        region_name: str
    ) -> Dict[str, Path]:
        """
        Process raw data into analysis products
        
        Args:
            raw_data: Dictionary of raw data paths
            region_name: Region name
            
        Returns:
            Dictionary of processed products
        """
        products = {}
        output_dir = self.config.output_dir / region_name / "processed"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process DEM
        if "dem" in raw_data and ProcessingStep.SLOPE in self.config.processing_steps:
            dem_path = raw_data["dem"]
            
            with DEMProcessor(dem_path) as processor:
                # Calculate terrain derivatives
                if ProcessingStep.SLOPE in self.config.processing_steps:
                    products["slope"] = processor.calculate_slope(
                        output_dir / "slope.tif"
                    )
                
                if ProcessingStep.ASPECT in self.config.processing_steps:
                    products["aspect"] = processor.calculate_aspect(
                        output_dir / "aspect.tif"
                    )
                
                if ProcessingStep.HILLSHADE in self.config.processing_steps:
                    products["hillshade"] = processor.calculate_hillshade(
                        output_dir / "hillshade.tif"
                    )
                
                if ProcessingStep.TPI in self.config.processing_steps:
                    products["tpi"] = processor.calculate_tpi(
                        output_dir / "tpi.tif"
                    )
        
        # Process NAIP
        if "naip" in raw_data:
            naip_path = raw_data["naip"]
            
            with NAIPProcessor(naip_path) as processor:
                if ProcessingStep.NDVI in self.config.processing_steps:
                    products["ndvi"] = processor.calculate_ndvi(
                        output_dir / "ndvi.tif"
                    )
                
                if ProcessingStep.NDWI in self.config.processing_steps:
                    products["ndwi"] = processor.calculate_ndwi(
                        output_dir / "ndwi.tif"
                    )
                
                if ProcessingStep.TEXTURE in self.config.processing_steps:
                    products["texture"] = processor.calculate_texture(
                        output_dir / "texture.tif"
                    )
                
                if ProcessingStep.WATER_MASK in self.config.processing_steps:
                    products["water_mask"] = processor.detect_water_bodies(
                        output_dir / "water_mask.tif"
                    )
        
        return products
    
    def _create_cogs(
        self,
        products: Dict[str, Path],
        region_name: str
    ) -> Dict[str, Path]:
        """
        Create Cloud-Optimized GeoTIFFs for all products
        
        Args:
            products: Dictionary of product paths
            region_name: Region name
            
        Returns:
            Dictionary of COG paths
        """
        cogs = {}
        cog_dir = self.config.output_dir / region_name / "cog"
        cog_dir.mkdir(parents=True, exist_ok=True)
        
        for name, path in products.items():
            if path is None or not path.exists():
                continue
            
            cog_path = cog_dir / f"{name}_cog.tif"
            
            try:
                if "dem" in name or "slope" in name or "aspect" in name:
                    # Use USGS client for DEM-like products
                    self.usgs_client.create_cloud_optimized_geotiff(path, cog_path)
                else:
                    # Use NAIP client for imagery
                    self.naip_client.create_cloud_optimized_geotiff(path, cog_path)
                
                cogs[f"{name}_cog"] = cog_path
                
            except Exception as e:
                logger.error(f"Error creating COG for {name}: {e}")
        
        return cogs
    
    def _generate_metadata(
        self,
        bbox: BoundingBox,
        products: Dict[str, Path]
    ) -> Dict[str, Any]:
        """
        Generate metadata for all products
        
        Args:
            bbox: Bounding box
            products: Dictionary of products
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            "created_at": datetime.now().isoformat(),
            "bounding_box": {
                "west": bbox.min_x,
                "south": bbox.min_y,
                "east": bbox.max_x,
                "north": bbox.max_y
            },
            "products": {},
            "crs": "EPSG:4326"
        }
        
        for name, path in products.items():
            if path is None or not path.exists():
                continue
            
            try:
                with rasterio.open(path) as src:
                    metadata["products"][name] = {
                        "path": str(path),
                        "size_bytes": path.stat().st_size,
                        "shape": (src.height, src.width),
                        "crs": str(src.crs),
                        "resolution": (abs(src.transform.a), abs(src.transform.e)),
                        "bands": src.count,
                        "dtype": str(src.dtypes[0])
                    }
            except Exception as e:
                logger.error(f"Error reading metadata for {name}: {e}")
        
        return metadata
    
    def save_metadata(self, metadata: Dict, region_name: str) -> Path:
        """Save metadata to JSON file"""
        metadata_path = self.config.output_dir / region_name / "metadata.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"Metadata saved to {metadata_path}")
        return metadata_path
    
    def get_product_path(self, product_name: str, region_name: str = "missouri_test") -> Optional[Path]:
        """Get path to a specific product"""
        # Check cache first
        cache_key = f"{region_name}/{product_name}"
        if cache_key in self._product_cache:
            return self._product_cache[cache_key]
        
        # Search in output directory
        output_dir = self.config.output_dir / region_name
        
        for subdir in ["processed", "cog", "dem", "naip"]:
            path = output_dir / subdir / f"{product_name}.tif"
            if path.exists():
                self._product_cache[cache_key] = path
                return path
            
            # Try with _cog suffix
            path = output_dir / subdir / f"{product_name}_cog.tif"
            if path.exists():
                self._product_cache[cache_key] = path
                return path
        
        return None
    
    def list_products(self, region_name: str = "missouri_test") -> List[str]:
        """List all available products for a region"""
        output_dir = self.config.output_dir / region_name
        products = []
        
        for subdir in ["processed", "cog", "dem", "naip"]:
            dir_path = output_dir / subdir
            if dir_path.exists():
                for f in dir_path.glob("*.tif"):
                    products.append(f.stem)
        
        return sorted(set(products))


class BuildingFootprintExtractor:
    """Extract building footprints from Microsoft dataset"""
    
    MICROSOFT_BUILDINGS_URL = "https://minedbuildings.blob.core.windows.net/global-buildings"
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path(tempfile.gettempdir()) / "microsoft_buildings"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def download_buildings(
        self,
        bbox: BoundingBox,
        region_name: str = "missouri"
    ) -> Optional[Path]:
        """
        Download building footprints for region
        
        Args:
            bbox: Bounding box
            region_name: Region name
            
        Returns:
            Path to GeoJSON or GeoPackage file
        """
        import requests
        
        # Microsoft buildings are organized by country/region
        # For US, we can use the US-specific dataset
        
        logger.info(f"Downloading Microsoft building footprints for {region_name}")
        
        # This is a simplified version - actual implementation would
        # query the appropriate quadkey tiles from Microsoft dataset
        
        output_path = self.cache_dir / f"{region_name}_buildings.geojson"
        
        # For now, return None (actual implementation would download)
        logger.info("Building footprint download not yet implemented")
        return None
    
    def rasterize_buildings(
        self,
        buildings_path: Path,
        reference_raster: Path,
        output_path: Path
    ) -> Path:
        """
        Rasterize building footprints to match reference raster
        
        Args:
            buildings_path: Path to building footprints vector file
            reference_raster: Path to reference raster for extent/resolution
            output_path: Output raster path
            
        Returns:
            Path to rasterized buildings
        """
        import geopandas as gpd
        from rasterio import features
        
        # Read buildings
        buildings = gpd.read_file(buildings_path)
        
        # Open reference raster
        with rasterio.open(reference_raster) as src:
            out_shape = (src.height, src.width)
            transform = src.transform
            crs = src.crs
            
            # Reproject buildings if needed
            if buildings.crs != crs:
                buildings = buildings.to_crs(crs)
            
            # Rasterize
            shapes = ((geom, 1) for geom in buildings.geometry)
            burned = features.rasterize(
                shapes=shapes,
                out_shape=out_shape,
                transform=transform,
                fill=0,
                dtype=np.uint8
            )
            
            # Write output
            kwargs = src.meta.copy()
            kwargs.update({
                "count": 1,
                "dtype": "uint8",
                "compress": "lzw"
            })
            
            with rasterio.open(output_path, "w", **kwargs) as dst:
                dst.write(burned, 1)
        
        return output_path


class LandCoverClassifier:
    """Land cover classification using satellite imagery"""
    
    # NLCD land cover classes
    NLCD_CLASSES = {
        11: ("Open Water", "#466b9f"),
        12: ("Perennial Ice/Snow", "#d1def8"),
        21: ("Developed, Open Space", "#dec5c5"),
        22: ("Developed, Low Intensity", "#d99282"),
        23: ("Developed, Medium Intensity", "#eb0000"),
        24: ("Developed, High Intensity", "#ab0000"),
        31: ("Barren Land", "#b3ac9f"),
        41: ("Deciduous Forest", "#68ab5f"),
        42: ("Evergreen Forest", "#1c5f2c"),
        43: ("Mixed Forest", "#b5c58f"),
        51: ("Dwarf Scrub", "#af963c"),
        52: ("Shrub/Scrub", "#ccb879"),
        71: ("Grassland/Herbaceous", "#dfdfc2"),
        72: ("Sedge/Herbaceous", "#d1d182"),
        73: ("Lichens", "#a3cc51"),
        74: ("Moss", "#82ba9e"),
        81: ("Pasture/Hay", "#dcd939"),
        82: ("Cultivated Crops", "#ab6c28"),
        90: ("Woody Wetlands", "#b8d9eb"),
        95: ("Emergent Herbaceous Wetlands", "#6c9fb8")
    }
    
    def __init__(self):
        pass
    
    def classify_from_naip(
        self,
        naip_path: Path,
        dem_path: Optional[Path] = None,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Perform land cover classification from NAIP imagery
        
        Uses a simple unsupervised classification (K-means)
        For production, would use a trained ML model
        
        Args:
            naip_path: Path to NAIP image
            dem_path: Optional DEM for topographic features
            output_path: Output classification path
            
        Returns:
            Path to classified raster
        """
        from sklearn.cluster import KMeans
        
        with rasterio.open(naip_path) as src:
            # Read all bands
            data = src.read()
            profile = src.profile
            
            # Reshape for clustering
            n_bands, height, width = data.shape
            reshaped = data.reshape(n_bands, -1).T
            
            # Normalize
            reshaped = reshaped.astype(np.float32)
            for i in range(reshaped.shape[1]):
                band = reshaped[:, i]
                reshaped[:, i] = (band - band.min()) / (band.max() - band.min() + 1e-8)
            
            # K-means clustering
            n_classes = 8
            kmeans = KMeans(n_clusters=n_classes, random_state=42, n_init=10)
            labels = kmeans.fit_predict(reshaped)
            
            # Reshape back
            classified = labels.reshape(height, width).astype(np.uint8)
            
            # Write output
            if output_path is None:
                output_path = naip_path.parent / "land_cover.tif"
            
            profile.update({
                "count": 1,
                "dtype": "uint8",
                "compress": "lzw"
            })
            
            with rasterio.open(output_path, "w", **profile) as dst:
                dst.write(classified, 1)
                
                # Add colormap
                colors = {
                    i: tuple(int(c.lstrip('#')[j:j+2], 16) for j in (0, 2, 4))
                    for i, (_, c) in enumerate(self.NLCD_CLASSES.items())
                    if i < n_classes
                }
                dst.write_colormap(1, colors)
        
        logger.info(f"Land cover classification saved to {output_path}")
        return output_path


def main():
    """Example pipeline execution"""
    # Create pipeline configuration
    config = PipelineConfig(
        sources=[
            DataSource.USGS_3DEP,
            DataSource.NAIP
        ],
        processing_steps=[
            ProcessingStep.SLOPE,
            ProcessingStep.ASPECT,
            ProcessingStep.HILLSHADE,
            ProcessingStep.NDVI,
            ProcessingStep.NDWI
        ],
        output_dir=Path("/tmp/resilienceai_pipeline"),
        create_cogs=True,
        max_workers=2
    )
    
    # Create and run pipeline
    pipeline = GeospatialPipeline(config)
    
    # Run for Missouri test region
    result = pipeline.run(region_name="missouri_st_louis")
    
    # Print results
    print(f"\nPipeline {'succeeded' if result.success else 'failed'}")
    print(f"Execution time: {result.execution_time:.2f} seconds")
    print(f"\nData products:")
    for name, path in result.data_products.items():
        print(f"  - {name}: {path}")
    
    if result.errors:
        print(f"\nErrors:")
        for error in result.errors:
            print(f"  - {error}")
    
    # Save metadata
    metadata_path = pipeline.save_metadata(result.metadata, "missouri_st_louis")
    print(f"\nMetadata saved to: {metadata_path}")
    
    # List all products
    products = pipeline.list_products("missouri_st_louis")
    print(f"\nAvailable products: {products}")


if __name__ == "__main__":
    main()
