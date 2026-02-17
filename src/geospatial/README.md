# Geospatial Pipeline for ResilienceAI

High-resolution geospatial data pipeline integrating USGS 3DEP 1m DEM, USDA NAIP 0.3-1m aerial imagery, and Google Earth Engine Sentinel-2 data for climate resilience analysis.

## Features

### Data Sources
- **USGS 3DEP**: 1-meter Digital Elevation Model (DEM) data
- **USDA NAIP**: 0.3-1m aerial imagery (4-band: RGB + NIR)
- **Google Earth Engine**: Sentinel-2 (10m) multispectral data
- **Microsoft Buildings**: Building footprint dataset

### Processing Capabilities

#### DEM Processing
- Slope calculation (degrees or percent)
- Aspect calculation (0-360 degrees)
- Hillshade generation
- Topographic Position Index (TPI)

#### Imagery Processing
- NDVI (Normalized Difference Vegetation Index)
- NDWI (Normalized Difference Water Index)
- Texture analysis
- False color composites
- Water body detection

#### Advanced Features
- Building footprint extraction
- Land cover classification
- Cloud-Optimized GeoTIFF (COG) generation
- Automatic tile stitching for large areas

## Installation

```bash
# Install dependencies
pip install rasterio numpy scipy scikit-image requests

# Optional: Install Google Earth Engine Python API
pip install earthengine-api

# For land cover classification
pip install scikit-learn geopandas
```

## Quick Start

### Basic Usage

```python
from geospatial.pipeline import GeospatialPipeline, PipelineConfig

# Create pipeline with default config
pipeline = GeospatialPipeline()

# Run pipeline for Missouri test region (St. Louis area)
result = pipeline.run(region_name="missouri_st_louis")

# Access results
print(f"Success: {result.success}")
print(f"Products: {list(result.data_products.keys())}")
```

### Custom Configuration

```python
from geospatial.pipeline import (
    GeospatialPipeline, 
    PipelineConfig,
    DataSource,
    ProcessingStep
)
from pathlib import Path

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
    output_dir=Path("/data/resilienceai"),
    create_cogs=True,
    max_workers=4
)

pipeline = GeospatialPipeline(config)
result = pipeline.run(region_name="my_region")
```

### Custom Bounding Box

```python
from geospatial.usgs_3dep import BoundingBox

# Define custom area
bbox = BoundingBox(
    min_x=-90.5,  # West
    min_y=38.5,   # South
    max_x=-90.0,  # East
    max_y=39.0    # North
)

result = pipeline.run(bbox=bbox, region_name="custom_area")
```

## Module Reference

### USGS 3DEP Handler (`usgs_3dep.py`)

```python
from geospatial.usgs_3dep import USGS3DEPClient, DEMProcessor, BoundingBox

# Search for DEM products
client = USGS3DEPClient()
products = client.search_products(bbox)

# Download DEMs
downloaded = client.download_area(bbox, output_dir)

# Process DEM
with DEMProcessor(dem_path) as processor:
    processor.calculate_slope("slope.tif")
    processor.calculate_aspect("aspect.tif")
    processor.calculate_hillshade("hillshade.tif")
    processor.calculate_tpi("tpi.tif")
    
    # Get statistics
    stats = processor.get_elevation_stats()
```

### NAIP Handler (`naip.py`)

```python
from geospatial.naip import NAIPClient, NAIPProcessor

# Search for NAIP imagery
client = NAIPClient()
items = client.search_stac(bbox, max_items=10)

# Download imagery
downloaded = client.download_area(bbox, output_dir)

# Process imagery
with NAIPProcessor(naip_path) as processor:
    processor.calculate_ndvi("ndvi.tif")
    processor.calculate_ndwi("ndwi.tif")
    processor.calculate_texture("texture.tif")
    processor.detect_water_bodies("water.tif")
```

### GEE Integration (`gee_integration.py`)

```python
from geospatial.gee_integration import get_gee_client

# Get GEE client (auto-falls back to mock if not authenticated)
client = get_gee_client()

# Search Sentinel-2 collection
collection = client.get_sentinel2_collection(
    bbox={"west": -90.5, "south": 38.5, "east": -90.0, "north": 39.0},
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# Create mosaic
mosaic = client.calculate_sentinel2_mosaic(
    bbox=bbox,
    start_date="2023-01-01",
    end_date="2023-12-31",
    mosaic_type="median"
)

# Calculate indices
ndvi = client.calculate_ndvi_sentinel2(mosaic)
ndwi = client.calculate_ndwi_sentinel2(mosaic)
```

## Testing

Run the test suite:

```bash
cd /root/.openclaw/workspace/ResilienceAI
python -m pytest tests/test_geospatial_pipeline.py -v

# Or run directly
python tests/test_geospatial_pipeline.py
```

## Missouri Test Region

The pipeline includes a default test region in Missouri (St. Louis area):

```python
from geospatial.usgs_3dep import USGS3DEPClient

bbox = USGS3DEPClient.MISSOURI_TEST_BBOX
# BoundingBox(min_x=-90.5, min_y=38.5, max_x=-90.0, max_y=39.0)
```

## Output Structure

```
/output_dir/
└── {region_name}/
    ├── dem/
    │   └── merged_dem.tif
    ├── naip/
    │   └── merged_naip.tif
    ├── processed/
    │   ├── slope.tif
    │   ├── aspect.tif
    │   ├── hillshade.tif
    │   ├── tpi.tif
    │   ├── ndvi.tif
    │   ├── ndwi.tif
    │   └── texture.tif
    ├── cog/
    │   ├── dem_cog.tif
    │   ├── slope_cog.tif
    │   └── ...
    └── metadata.json
```

## Cloud-Optimized GeoTIFFs

All products can be converted to COG format for efficient web visualization:

```python
# COGs are automatically created when create_cogs=True
config = PipelineConfig(create_cogs=True)

# Or create manually
from geospatial.usgs_3dep import USGS3DEPClient

client = USGS3DEPClient()
client.create_cloud_optimized_geotiff(
    input_path="dem.tif",
    output_path="dem_cog.tif"
)
```

## API Keys & Authentication

### USGS National Map
No API key required for basic access.

### NAIP (Microsoft Planetary Computer)
No authentication required for public data.

### Google Earth Engine
```bash
# Authenticate
earthengine authenticate

# Or use service account
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

## Visualization

The generated COGs can be visualized in web applications using:

- **Leaflet** with `L.tileLayer.wms()` or `L.tileLayer()`
- **Mapbox GL JS** with raster sources
- **Cesium** for 3D terrain visualization
- **TiTiler** for dynamic tiling

Example Leaflet configuration:
```javascript
L.tileLayer('https://your-titiler-endpoint/cog/tiles/{z}/{x}/{y}?url={cog_url}', {
    maxZoom: 20
}).addTo(map);
```

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request
