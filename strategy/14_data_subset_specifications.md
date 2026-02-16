# Data Subset Specifications for USA-Focused 1m Resolution Analysis

This document provides specific data subset selections for USGS and Google Earth Engine sources, optimized for high-resolution (1m) geospatial analysis with a focus on the United States, particularly Missouri and CONUS regions.

---

## USGS Data Sources

### 1. 3DEP 1m DEM

#### Dataset Overview
- **Dataset Name**: USGS 3D Elevation Program (3DEP) 1-meter Digital Elevation Model
- **Product**: DTM (Digital Terrain Model) - bare earth surface
- **Alternative**: DSM (Digital Surface Model) - includes vegetation and structures

#### Collection ID
```
USGS 3DEP 1m DEM
Product ID: USGS 1/3 arc-second DEM (converted to 1m)
Direct Download: https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Elevation/1m/
```

#### Selection Criteria
| Parameter | Value | Notes |
|-----------|-------|-------|
| Resolution | 1 meter | Native resolution |
| Vertical Datum | NAVD88 | North American Vertical Datum 1988 |
| Horizontal Datum | NAD83 / UTM | North American Datum 1983 |
| Format | GeoTIFF (.tif) | Standard format |
| Projection | UTM zone appropriate | Varies by location |

#### Recommended Spatial Subset
- **Primary Focus**: Missouri (state-wide coverage)
- **Secondary**: CONUS (Continental United States) for comparative analysis
- **Specific Areas**: 
  - St. Louis metropolitan area
  - Kansas City metropolitan area
  - Missouri River corridor
  - Ozark Highlands

#### Temporal Subset
- **Available Years**: 2015-present (ongoing collection)
- **Recommended**: Most recent available data (2020-2024)
- **Note**: 3DEP is updated periodically; use latest available for each tile

#### Band Selection
- **Single Band**: Elevation (meters)
- **Data Type**: Float32
- **No Data Value**: -9999 or -3.4028234663852886e+38

#### Preprocessing Steps
```python
import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling

def preprocess_3dep_dem(input_path, output_path, target_crs='EPSG:4326'):
    """
    Preprocess 3DEP 1m DEM
    """
    with rasterio.open(input_path) as src:
        # Read elevation data
        elevation = src.read(1)
        
        # Handle no-data values
        elevation = np.where(elevation < -1000, np.nan, elevation)
        
        # Reproject if needed
        if src.crs.to_string() != target_crs:
            # Reproject to target CRS
            pass  # Implementation depends on target resolution
        
        # Calculate derived products
        slope = calculate_slope(elevation, src.transform)
        aspect = calculate_aspect(elevation, src.transform)
        hillshade = calculate_hillshade(elevation, src.transform)
        
        # Save processed data
        profile = src.profile.copy()
        profile.update(dtype=rasterio.float32, nodata=np.nan)
        
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(elevation.astype(rasterio.float32), 1)
    
    return elevation, slope, aspect, hillshade

def calculate_slope(dem, transform):
    """Calculate slope in degrees"""
    from numpy import gradient, arctan, sqrt, degrees
    dx, dy = transform[0], -transform[4]
    gy, gx = gradient(dem, dy, dx)
    slope = degrees(arctan(sqrt(gx**2 + gy**2)))
    return slope

def calculate_hillshade(dem, transform, azimuth=315, altitude=45):
    """Calculate hillshade"""
    from numpy import gradient, pi, sin, cos, sqrt, arctan2, degrees
    dx, dy = transform[0], -transform[4]
    gy, gx = gradient(dem, dy, dx)
    
    slope = arctan(sqrt(gx**2 + gy**2))
    aspect = arctan2(-gy, gx)
    
    azimuth_rad = (360 - azimuth + 90) * pi / 180
    altitude_rad = altitude * pi / 180
    
    hillshade = 255 * ((cos(altitude_rad) * cos(slope)) + 
                       (sin(altitude_rad) * sin(slope) * cos(azimuth_rad - aspect)))
    return hillshade
```

#### Use Cases
- Flood modeling and hydrological analysis
- Terrain analysis for infrastructure planning
- Slope stability assessment
- Watershed delineation
- Line-of-sight studies

---

### 2. NAIP (National Agriculture Imagery Program)

#### Dataset Overview
- **Dataset Name**: USDA NAIP Digital Ortho Photo
- **Products**: 4-band (RGB + NIR) or 3-band (RGB only)
- **Resolution**: 0.3m - 1m (varies by year)

#### Collection ID
```
USDA NAIP
Product ID: NAIP
Direct Download: https://naip-usdaonline.hub.arcgis.com/
AWS Open Data: s3://naip-analytic/
```

#### Selection Criteria
| Parameter | Value | Notes |
|-----------|-------|-------|
| Resolution | 0.6m (2017-2022) | Higher resolution available |
| Resolution | 1m (pre-2017) | Older acquisitions |
| Bands | 4-band (R,G,B,NIR) | Recommended for analysis |
| Format | GeoTIFF | Compressed or uncompressed |
| Compression | JPEG2000 or None | Varies by year |

#### Recommended Spatial Subset
- **Primary Focus**: Missouri state-wide
- **CONUS Coverage**: Available for all states
- **Priority Areas**: 
  - Agricultural regions
  - Urban development zones
  - Riparian corridors

#### Temporal Subset
| Year Range | Resolution | Bands | Notes |
|------------|------------|-------|-------|
| 2022-2024 | 0.6m | 4-band | Most recent, highest quality |
| 2019-2021 | 0.6m | 4-band | Good coverage |
| 2017-2018 | 0.6m | 4-band | Recent baseline |
| 2015-2016 | 1m | 4-band | Change detection baseline |
| 2013-2014 | 1m | 4-band | Historical reference |

**Recommended**: 2022-2024 for current analysis; 2015-2016 for change detection

#### Band Selection
| Band | Wavelength | Use Case |
|------|------------|----------|
| Red | 0.64-0.67 µm | Vegetation health, built structures |
| Green | 0.53-0.59 µm | Vegetation vigor, water bodies |
| Blue | 0.45-0.51 µm | Water depth, atmospheric correction |
| NIR | 0.77-0.88 µm | Vegetation biomass, water stress |

**Indices to Calculate:**
- NDVI = (NIR - Red) / (NIR + Red)
- NDWI = (Green - NIR) / (Green + NIR)
- SAVI = ((NIR - Red) / (NIR + Red + L)) * (1 + L)

#### Preprocessing Steps
```python
import rasterio
import numpy as np
from rasterio.mask import mask

def preprocess_naip(input_path, output_path, aoi_geometry=None):
    """
    Preprocess NAIP 4-band imagery
    """
    with rasterio.open(input_path) as src:
        # Read all bands
        red = src.read(1).astype(float)
        green = src.read(2).astype(float)
        blue = src.read(3).astype(float)
        nir = src.read(4).astype(float)
        
        # Clip to AOI if provided
        if aoi_geometry:
            red, transform = mask(src, [aoi_geometry], crop=True, indexes=1)
            green, _ = mask(src, [aoi_geometry], crop=True, indexes=2)
            blue, _ = mask(src, [aoi_geometry], crop=True, indexes=3)
            nir, _ = mask(src, [aoi_geometry], crop=True, indexes=4)
        
        # Calculate vegetation indices
        ndvi = calculate_ndvi(nir, red)
        ndwi = calculate_ndwi(green, nir)
        
        # Create composite
        composite = np.stack([red, green, blue, nir, ndvi, ndwi])
        
        # Save processed data
        profile = src.profile.copy()
        profile.update(
            count=6,
            dtype=rasterio.float32,
            compress='lzw'
        )
        
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(composite.astype(rasterio.float32))
            dst.set_band_description(1, 'Red')
            dst.set_band_description(2, 'Green')
            dst.set_band_description(3, 'Blue')
            dst.set_band_description(4, 'NIR')
            dst.set_band_description(5, 'NDVI')
            dst.set_band_description(6, 'NDWI')
    
    return composite

def calculate_ndvi(nir, red):
    """Calculate NDVI with safe division"""
    ndvi = np.zeros_like(nir)
    valid = (nir + red) > 0
    ndvi[valid] = (nir[valid] - red[valid]) / (nir[valid] + red[valid])
    return ndvi

def calculate_ndwi(green, nir):
    """Calculate NDWI (Water Index)"""
    ndwi = np.zeros_like(green)
    valid = (green + nir) > 0
    ndwi[valid] = (green[valid] - nir[valid]) / (green[valid] + nir[valid])
    return ndwi
```

#### Use Cases
- Land cover classification
- Agricultural monitoring
- Vegetation health assessment
- Urban growth analysis
- Change detection (multi-temporal)
- Impervious surface mapping

---

### 3. National Hydrography Dataset (NHDPlus HR)

#### Dataset Overview
- **Dataset Name**: NHDPlus High Resolution (NHDPlus HR)
- **Product**: Comprehensive hydrography dataset with flow direction and accumulation
- **Scale**: 1:24,000 (High Resolution)

#### Collection ID
```
USGS NHDPlus HR
Product ID: nhdplushr
Download Portal: https://www.usgs.gov/national-hydrography/access-national-hydrography-products
Direct Download: https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/Hydrography/NHDPlusHR/
```

#### Selection Criteria
| Parameter | Value | Notes |
|-----------|-------|-------|
| Scale | 1:24,000 | High resolution |
| Version | 2.0 | Current version |
| Format | File Geodatabase (.gdb) or Shapefile | GDB recommended |
| Projection | NAD83 / Albers Equal Area | Standard projection |

#### Recommended Spatial Subset
- **Primary Focus**: Missouri (4-digit HUCs: 1028, 1029, 1030, 1031, 1101)
- **Secondary**: Mississippi River Basin
- **Specific**: 
  - 8-digit HUCs covering study area
  - NHDPlus HR Vector Processing Units (VPUs)

#### Temporal Subset
- **Current Version**: NHDPlus HR 2.0 (2023 release)
- **Snapshot Date**: Data reflects conditions at time of collection
- **Updates**: Quarterly updates available

#### Feature Classes to Select
| Feature Class | Description | Use Case |
|---------------|-------------|----------|
| NHDFlowline | Stream/river centerlines | Hydrologic network |
| NHDWaterbody | Lakes, ponds, reservoirs | Water storage |
| NHDArea | Wide rivers, glaciers | Areal water features |
| NHDLine | Dams, waterfalls, rapids | Hydraulic structures |
| NHDPoint | Springs, wells, sinks | Point water features |
| NHDPlusCatchment | Catchment polygons | Watershed boundaries |
| NHDPlusFlowlineVAA | Value-added attributes | Flow characteristics |

#### Key Attributes
| Attribute | Description | Units |
|-----------|-------------|-------|
| COMID | Common identifier | - |
| LENGTHKM | Feature length | kilometers |
| AREASQKM | Catchment area | square kilometers |
| SLOPE | Channel slope | m/m |
| STREAMORDE | Strahler stream order | - |
| FROMNODE | Upstream node | - |
| TONODE | Downstream node | - |

#### Preprocessing Steps
```python
import geopandas as gpd
import pandas as pd
import networkx as nx

def preprocess_nhdplus_hr(gdb_path, output_dir, huc4_list=None):
    """
    Preprocess NHDPlus HR data
    """
    # Read flowlines
    flowlines = gpd.read_file(gdb_path, layer='NHDFlowline')
    
    # Read value-added attributes
    vaa = gpd.read_file(gdb_path, layer='NHDPlusFlowlineVAA')
    
    # Read catchments
    catchments = gpd.read_file(gdb_path, layer='Catchment')
    
    # Read waterbodies
    waterbodies = gpd.read_file(gdb_path, layer='NHDWaterbody')
    
    # Merge flowlines with VAA
    flowlines_enhanced = flowlines.merge(
        vaa[['NHDPlusID', 'StreamOrder', 'Slope', 'LengthKm', 'TotDASqKm']],
        on='NHDPlusID',
        how='left'
    )
    
    # Filter by stream order if needed
    # flowlines_enhanced = flowlines_enhanced[flowlines_enhanced['StreamOrder'] >= 1]
    
    # Build network topology
    G = build_network_graph(flowlines_enhanced)
    
    # Calculate upstream drainage for selected points
    # upstream_comids = get_upstream_comids(G, target_comid)
    
    # Save processed layers
    flowlines_enhanced.to_file(f"{output_dir}/flowlines_processed.shp")
    catchments.to_file(f"{output_dir}/catchments.shp")
    waterbodies.to_file(f"{output_dir}/waterbodies.shp")
    
    return flowlines_enhanced, catchments, waterbodies, G

def build_network_graph(flowlines):
    """Build directed graph from flowlines"""
    G = nx.DiGraph()
    
    for _, row in flowlines.iterrows():
        G.add_edge(
            row['FromNode'],
            row['ToNode'],
            comid=row['NHDPlusID'],
            length=row['LengthKm'],
            order=row.get('StreamOrder', 0)
        )
    
    return G

def get_upstream_comids(G, target_comid, flowlines_df):
    """Get all upstream COMIDs for a given COMID"""
    # Find the edge with this COMID
    for u, v, data in G.edges(data=True):
        if data['comid'] == target_comid:
            # Get all predecessors
            upstream_nodes = nx.ancestors(G, u)
            upstream_nodes.add(u)
            
            # Find all edges from these nodes
            upstream_comids = []
            for node in upstream_nodes:
                for _, _, edge_data in G.out_edges(node, data=True):
                    upstream_comids.append(edge_data['comid'])
            
            return upstream_comids
    
    return []
```

#### Use Cases
- Watershed delineation
- Stream network analysis
- Floodplain mapping
- Water quality modeling
- Habitat connectivity studies
- Drainage area calculations

---

### 4. National Land Cover Database (NLCD)

#### Dataset Overview
- **Dataset Name**: National Land Cover Database (NLCD)
- **Product**: Land cover classification at 30m resolution
- **Versions**: NLCD 2019, 2021 (most recent)

#### Collection ID
```
USGS NLCD
Product ID: NLCD
Download Portal: https://www.mrlc.gov/data
Direct Download: https://prd-tnm.s3.amazonaws.com/index.html?prefix=StagedProducts/NLCD/
```

#### Selection Criteria
| Parameter | Value | Notes |
|-----------|-------|-------|
| Resolution | 30 meters | Native resolution |
| Version | NLCD 2021 | Most recent |
| Projection | Albers Equal Area CONUS | NAD83 |
| Format | GeoTIFF | Standard format |

#### Recommended Spatial Subset
- **Primary Focus**: CONUS (full coverage)
- **Secondary**: Missouri state boundary clip
- **Note**: 30m resolution; resample to 1m if combining with other datasets

#### Temporal Subset
| Product | Year | Description |
|---------|------|-------------|
| NLCD 2021 Land Cover | 2021 | Current land cover |
| NLCD 2019 Land Cover | 2019 | Recent baseline |
| NLCD 2016 Land Cover | 2016 | Change detection |
| NLCD 2013 Land Cover | 2013 | Historical reference |
| NLCD 2001-2021 Change | Multi | Change products |
| NLCD Impervious | 2021 | Impervious surface |
| NLCD Tree Canopy | 2021 | Percent tree cover |

**Recommended**: NLCD 2021 for current conditions; multi-temporal for change analysis

#### Land Cover Classes (Key Classes)
| Value | Class | Description |
|-------|-------|-------------|
| 11 | Open Water | Lakes, rivers, oceans |
| 21 | Developed, Open Space | <20% impervious |
| 22 | Developed, Low Intensity | 20-49% impervious |
| 23 | Developed, Medium Intensity | 50-79% impervious |
| 24 | Developed, High Intensity | 80-100% impervious |
| 31 | Barren Land | Rock, sand, clay |
| 41 | Deciduous Forest | >20% canopy |
| 42 | Evergreen Forest | >20% canopy |
| 43 | Mixed Forest | >20% canopy |
| 52 | Shrub/Scrub | <5m height |
| 71 | Grassland/Herbaceous | Non-woody |
| 81 | Pasture/Hay | Cultivated |
| 82 | Cultivated Crops | Row crops |
| 90 | Woody Wetlands | Forested wetlands |
| 95 | Emergent Herbaceous Wetlands | Marsh, bog |

#### Preprocessing Steps
```python
import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling
from rasterio.features import rasterize
import geopandas as gpd

def preprocess_nlcd(input_path, output_path, target_crs='EPSG:4326', target_resolution=None):
    """
    Preprocess NLCD land cover data
    """
    with rasterio.open(input_path) as src:
        # Read land cover data
        landcover = src.read(1)
        
        # Create binary masks for key classes
        developed_mask = np.isin(landcover, [21, 22, 23, 24])
        forest_mask = np.isin(landcover, [41, 42, 43])
        water_mask = (landcover == 11)
        wetland_mask = np.isin(landcover, [90, 95])
        agriculture_mask = np.isin(landcover, [81, 82])
        
        # Stack masks as bands
        masks = np.stack([
            landcover,
            developed_mask.astype(np.uint8),
            forest_mask.astype(np.uint8),
            water_mask.astype(np.uint8),
            wetland_mask.astype(np.uint8),
            agriculture_mask.astype(np.uint8)
        ])
        
        # Reproject if needed
        if src.crs.to_string() != target_crs:
            # Implementation for reprojection
            pass
        
        # Save processed data
        profile = src.profile.copy()
        profile.update(
            count=6,
            dtype=rasterio.uint8,
            compress='lzw'
        )
        
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(masks)
            dst.set_band_description(1, 'LandCover_Class')
            dst.set_band_description(2, 'Developed')
            dst.set_band_description(3, 'Forest')
            dst.set_band_description(4, 'Water')
            dst.set_band_description(5, 'Wetland')
            dst.set_band_description(6, 'Agriculture')
        
        # Create statistics
        stats = {
            'total_pixels': landcover.size,
            'developed_pct': np.sum(developed_mask) / landcover.size * 100,
            'forest_pct': np.sum(forest_mask) / landcover.size * 100,
            'water_pct': np.sum(water_mask) / landcover.size * 100,
            'wetland_pct': np.sum(wetland_mask) / landcover.size * 100,
            'agriculture_pct': np.sum(agriculture_mask) / landcover.size * 100
        }
        
        return masks, stats

def resample_nlcd_to_highres(nlcd_path, reference_raster_path, output_path):
    """
    Resample NLCD (30m) to match high-resolution reference (e.g., 1m)
    Uses nearest neighbor to preserve class values
    """
    with rasterio.open(nlcd_path) as src_nlcd:
        with rasterio.open(reference_raster_path) as src_ref:
            # Get reference profile
            profile = src_ref.profile.copy()
            profile.update(
                dtype=src_nlcd.dtype,
                count=1,
                compress='lzw'
            )
            
            # Reproject NLCD to match reference
            landcover_resampled = np.empty((src_ref.height, src_ref.width), dtype=src_nlcd.dtype)
            
            reproject(
                source=rasterio.band(src_nlcd, 1),
                destination=landcover_resampled,
                src_transform=src_nlcd.transform,
                src_crs=src_nlcd.crs,
                dst_transform=src_ref.transform,
                dst_crs=src_ref.crs,
                resampling=Resampling.nearest  # Preserve class values
            )
            
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(landcover_resampled, 1)
    
    return landcover_resampled
```

#### Use Cases
- Land cover change detection
- Impervious surface mapping
- Forest cover analysis
- Urban growth modeling
- Hydrologic modeling input
- Habitat suitability assessment

---

## Google Earth Engine Data Sources

### 1. USGS 3DEP Collection

#### Collection ID
```javascript
// USGS 3DEP DEM Collection
var dem_collection = ee.ImageCollection('USGS/3DEP/1m');

// Or for 10m (where 1m not available)
var dem_10m = ee.Image('USGS/3DEP/10m');
```

#### Selection Criteria
| Parameter | Value | Notes |
|-----------|-------|-------|
| Collection | USGS/3DEP/1m | 1-meter DEM |
| Alternative | USGS/3DEP/10m | 10-meter coverage |
| Bands | elevation | Single band |

#### Spatial Subset
```javascript
// Missouri state boundary
var missouri = ee.FeatureCollection('TIGER/2018/States')
  .filter(ee.Filter.eq('NAME', 'Missouri'));

// Or custom AOI
var aoi = ee.Geometry.Polygon([[
  [-95.7, 35.9],  // SW
  [-95.7, 40.6],  // NW
  [-89.1, 40.6],  // NE
  [-89.1, 35.9],  // SE
  [-95.7, 35.9]   // Close
]]);
```

#### Temporal Subset
- **Static Dataset**: No temporal filtering needed
- **Collection Date**: Varies by location (2015-present)

#### Band Selection
```javascript
// Single elevation band
var elevation = dem.select('elevation');
```

#### Preprocessing Code (GEE)
```javascript
// USGS 3DEP DEM Preprocessing
var dem = ee.Image('USGS/3DEP/1m');

// Clip to AOI
var dem_clipped = dem.clip(aoi);

// Calculate derived products
var slope = ee.Terrain.slope(dem_clipped);
var aspect = ee.Terrain.aspect(dem_clipped);
var hillshade = ee.Terrain.hillshade(dem_clipped);

// Calculate topographic position index (TPI)
var kernel = ee.Kernel.circle({radius: 5, units: 'pixels'});
var meanElevation = dem_clipped.reduceNeighborhood({
  reducer: ee.Reducer.mean(),
  kernel: kernel
});
var tpi = dem_clipped.subtract(meanElevation);

// Stack all products
var demStack = ee.Image.cat([
  dem_clipped.rename('elevation'),
  slope.rename('slope'),
  aspect.rename('aspect'),
  hillshade.rename('hillshade'),
  tpi.rename('tpi')
]);

// Export
Export.image.toDrive({
  image: demStack,
  description: '3DEP_DEM_Products',
  region: aoi,
  scale: 1,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});
```

#### Use Cases
- High-resolution terrain analysis
- Flood inundation mapping
- Slope failure assessment
- Precision agriculture

---

### 2. USDA NAIP Collection

#### Collection ID
```javascript
// USDA NAIP Image Collection
var naip = ee.ImageCollection('USDA/NAIP/DOQQ');
```

#### Selection Criteria
| Parameter | Value | Notes |
|-----------|-------|-------|
| Collection | USDA/NAIP/DOQQ | Quarter-quad tiles |
| Bands | R, G, B, N | 4-band imagery |
| Resolution | 0.6-1m | Varies by year |

#### Spatial Subset
```javascript
// Missouri AOI
var missouri = ee.FeatureCollection('TIGER/2018/States')
  .filter(ee.Filter.eq('NAME', 'Missouri'));

// Or specific counties
var counties = ee.FeatureCollection('TIGER/2018/Counties')
  .filter(ee.Filter.eq('STATEFP', '29')); // Missouri FIPS code
```

#### Temporal Subset
```javascript
// Filter by date range
var naip_2022 = naip
  .filterBounds(aoi)
  .filterDate('2022-01-01', '2022-12-31')
  .filter(ee.Filter.lt('CLOUD_COVER', 10));

// Or multi-year composite
var naip_recent = naip
  .filterBounds(aoi)
  .filterDate('2020-01-01', '2024-12-31')
  .mosaic();
```

#### Band Selection
```javascript
// Band names in NAIP
// 'R' - Red (0.64-0.67 µm)
// 'G' - Green (0.53-0.59 µm)
// 'B' - Blue (0.45-0.51 µm)
// 'N' - Near Infrared (0.77-0.88 µm)

// Select all bands
var naip_bands = naip_image.select(['R', 'G', 'B', 'N']);

// Calculate indices
var ndvi = naip_image.normalizedDifference(['N', 'R']).rename('NDVI');
var ndwi = naip_image.normalizedDifference(['G', 'N']).rename('NDWI');
```

#### Preprocessing Code (GEE)
```javascript
// USDA NAIP Preprocessing
var naip = ee.ImageCollection('USDA/NAIP/DOQQ');

// Filter and mosaic
var naip_filtered = naip
  .filterBounds(aoi)
  .filterDate('2022-01-01', '2023-12-31')
  .mosaic()
  .clip(aoi);

// Calculate vegetation indices
var ndvi = naip_filtered.normalizedDifference(['N', 'R']).rename('NDVI');
var ndwi = naip_filtered.normalizedDifference(['G', 'N']).rename('NDWI');
var ndbi = naip_filtered.normalizedDifference(['R', 'N']).rename('NDBI'); // Built-up index

// Texture analysis (optional)
var texture = naip_filtered.select('N').entropy(ee.Kernel.square(3));

// Stack all bands
var naip_stack = ee.Image.cat([
  naip_filtered.select(['R', 'G', 'B', 'N']),
  ndvi,
  ndwi,
  texture.rename('texture')
]);

// Export
Export.image.toDrive({
  image: naip_stack,
  description: 'NAIP_2022_Processed',
  region: aoi,
  scale: 1,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});
```

#### Use Cases
- High-resolution land cover classification
- Agricultural monitoring
- Urban tree canopy assessment
- Impervious surface detection
- Change detection

---

### 3. Sentinel-2 Collection

#### Collection ID
```javascript
// Sentinel-2 Surface Reflectance (Recommended)
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED');

// Sentinel-2 Top of Atmosphere (L1C)
var s2_toa = ee.ImageCollection('COPERNICUS/S2_HARMONIZED');
```

#### Product Selection: L2A (SR) vs L1C (TOA)
| Product | Use Case | Recommendation |
|---------|----------|----------------|
| L2A (SR) | Land cover, vegetation analysis | **Recommended** |
| L1C (TOA) | Atmospheric studies, custom correction | Advanced users |

#### Selection Criteria
| Parameter | Value | Notes |
|-----------|-------|-------|
| Collection | COPERNICUS/S2_SR_HARMONIZED | Surface reflectance |
| Resolution | 10m (B2, B3, B4, B8) | 10m bands |
| Resolution | 20m (B5-B7, B8A, B11-B12) | 20m bands |
| Resolution | 60m (B1, B9, B10) | Atmospheric bands |
| Cloud Cover | <20% | Filter threshold |

#### Spatial Subset
```javascript
// Missouri or CONUS
var aoi = ee.Geometry.Rectangle([-95.7, 35.9, -89.1, 40.6]); // Missouri
```

#### Temporal Subset
```javascript
// Growing season composite (best for vegetation)
var s2_growing = s2
  .filterBounds(aoi)
  .filterDate('2023-04-01', '2023-09-30')  // Growing season
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20));

// Or specific month
var s2_july = s2
  .filterBounds(aoi)
  .filterDate('2023-07-01', '2023-07-31')
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10));
```

#### Band Selection
| Band | Name | Resolution | Use Case |
|------|------|------------|----------|
| B2 | Blue | 10m | Water, atmospheric |
| B3 | Green | 10m | Vegetation health |
| B4 | Red | 10m | Vegetation, soil |
| B5 | Red Edge 1 | 20m | Chlorophyll content |
| B6 | Red Edge 2 | 20m | Chlorophyll content |
| B7 | Red Edge 3 | 20m | Chlorophyll content |
| B8 | NIR | 10m | Vegetation biomass |
| B8A | Narrow NIR | 20m | Vegetation stress |
| B11 | SWIR 1 | 20m | Moisture content |
| B12 | SWIR 2 | 20m | Moisture content |

#### Preprocessing Code (GEE)
```javascript
// Sentinel-2 Preprocessing
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED');

// Filter collection
var s2_filtered = s2
  .filterBounds(aoi)
  .filterDate('2023-04-01', '2023-09-30')
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
  .map(maskS2clouds);  // Apply cloud mask

// Cloud masking function
function maskS2clouds(image) {
  var qa = image.select('QA60');
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;
  var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
    .and(qa.bitwiseAnd(cirrusBitMask).eq(0));
  return image.updateMask(mask).divide(10000);
}

// Create median composite
var s2_composite = s2_filtered.median().clip(aoi);

// Calculate indices
var ndvi = s2_composite.normalizedDifference(['B8', 'B4']).rename('NDVI');
var ndwi = s2_composite.normalizedDifference(['B3', 'B8']).rename('NDWI');
var ndbi = s2_composite.normalizedDifference(['B11', 'B8']).rename('NDBI');
var evi = s2_composite.expression(
  '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))', {
    'NIR': s2_composite.select('B8'),
    'RED': s2_composite.select('B4'),
    'BLUE': s2_composite.select('B2')
  }).rename('EVI');

// Stack bands
var s2_stack = ee.Image.cat([
  s2_composite.select(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']),
  ndvi,
  ndwi,
  evi
]);

// Export
Export.image.toDrive({
  image: s2_stack,
  description: 'Sentinel2_2023_Composite',
  region: aoi,
  scale: 10,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});
```

#### Use Cases
- Regional land cover classification
- Vegetation health monitoring
- Agricultural assessment
- Water quality estimation
- Burn severity mapping

---

### 4. Landsat Collection 2

#### Collection ID
```javascript
// Landsat 8-9 Surface Reflectance
var l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2');
var l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2');

// Landsat 7 ETM+
var l7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2');

// Landsat 4-5 TM
var l5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2');
```

#### Selection Criteria
| Parameter | Value | Notes |
|-----------|-------|-------|
| Collection | LANDSAT/LC08/C02/T1_L2 | Landsat 8-9 SR |
| Resolution | 30m (multispectral) | Standard resolution |
| Resolution | 15m (panchromatic) | Pan-sharpening |
| Temporal | 16-day repeat | Frequent coverage |
| Archive | 1984-present | Long-term record |

#### Spatial Subset
```javascript
// Missouri or broader CONUS
var aoi = ee.Geometry.Rectangle([-95.7, 35.9, -89.1, 40.6]);
```

#### Temporal Subset
```javascript
// Recent data
var l8_recent = l8
  .filterBounds(aoi)
  .filterDate('2023-01-01', '2023-12-31')
  .filter(ee.Filter.lt('CLOUD_COVER', 20));

// Multi-year for change detection
var l8_2013 = l8.filterDate('2013-01-01', '2013-12-31').filterBounds(aoi);
var l8_2023 = l8.filterDate('2023-01-01', '2023-12-31').filterBounds(aoi);
```

#### Band Selection
| Band | Name | Wavelength | Use Case |
|------|------|------------|----------|
| B1 | Coastal Aerosol | 0.43-0.45 µm | Atmospheric correction |
| B2 | Blue | 0.45-0.51 µm | Water penetration |
| B3 | Green | 0.53-0.59 µm | Vegetation health |
| B4 | Red | 0.64-0.67 µm | Vegetation discrimination |
| B5 | NIR | 0.85-0.88 µm | Vegetation biomass |
| B6 | SWIR 1 | 1.57-1.65 µm | Moisture content |
| B7 | SWIR 2 | 2.11-2.29 µm | Mineral mapping |
| B10 | Thermal | 10.6-11.2 µm | Surface temperature |
| B11 | Thermal | 11.5-12.5 µm | Surface temperature |

#### Preprocessing Code (GEE)
```javascript
// Landsat Collection 2 Preprocessing
var l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2');

// Scale factors for Collection 2
function applyScaleFactors(image) {
  var opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
  var thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0);
  return image.addBands(opticalBands, null, true)
    .addBands(thermalBands, null, true);
}

// Cloud mask
function maskL8clouds(image) {
  var qa = image.select('QA_PIXEL');
  var cloudShadowBitMask = 1 << 4;
  var cloudsBitMask = 1 << 3;
  var mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0)
    .and(qa.bitwiseAnd(cloudsBitMask).eq(0));
  return image.updateMask(mask);
}

// Process collection
var l8_processed = l8
  .filterBounds(aoi)
  .filterDate('2023-01-01', '2023-12-31')
  .filter(ee.Filter.lt('CLOUD_COVER', 20))
  .map(applyScaleFactors)
  .map(maskL8clouds);

// Create composite
var l8_composite = l8_processed.median().clip(aoi);

// Calculate indices
var ndvi = l8_composite.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI');
var ndwi = l8_composite.normalizedDifference(['SR_B3', 'SR_B5']).rename('NDWI');
var nbr = l8_composite.normalizedDifference(['SR_B5', 'SR_B7']).rename('NBR');
var ndbi = l8_composite.normalizedDifference(['SR_B6', 'SR_B5']).rename('NDBI');

// Land Surface Temperature
var lst = l8_composite.select('ST_B10').rename('LST');

// Stack
var l8_stack = ee.Image.cat([
  l8_composite.select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']),
  ndvi,
  ndwi,
  nbr,
  ndbi,
  lst
]);

// Export
Export.image.toDrive({
  image: l8_stack,
  description: 'Landsat8_2023_Composite',
  region: aoi,
  scale: 30,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});
```

#### Use Cases
- Long-term change detection (1984-present)
- Regional land cover mapping
- Surface temperature analysis
- Burn severity assessment
- Water body monitoring
- Urban heat island studies

---

### 5. Dynamic World

#### Collection ID
```javascript
// Dynamic World Near Real-Time Land Cover
var dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1');

// Or specific image
var dw_image = ee.Image('GOOGLE/DYNAMICWORLD/V1/20230101');
```

#### Selection Criteria
| Parameter | Value | Notes |
|-----------|-------|-------|
| Collection | GOOGLE/DYNAMICWORLD/V1 | Near real-time |
| Resolution | 10m | Sentinel-2 based |
| Update Frequency | 2-5 days | Frequent updates |
| Temporal Range | 2015-present | Sentinel-2 era |

#### Spatial Subset
```javascript
var aoi = ee.Geometry.Rectangle([-95.7, 35.9, -89.1, 40.6]); // Missouri
```

#### Temporal Subset
```javascript
// Specific date
var dw_date = dw
  .filterBounds(aoi)
  .filterDate('2023-07-01', '2023-07-31')
  .mode();  // Most common class

// Annual mode
var dw_2023 = dw
  .filterBounds(aoi)
  .filterDate('2023-01-01', '2023-12-31')
  .select('label')
  .mode();
```

#### Band Selection (Probabilities)
| Band | Class | Description |
|------|-------|-------------|
| water | Water | Rivers, lakes, ocean |
| trees | Trees | Forest, woodland |
| grass | Grass | Grassland, pasture |
| flooded_vegetation | Flooded Vegetation | Wetlands, rice |
| crops | Crops | Agriculture |
| shrub_and_scrub | Shrub/Scrub | Low vegetation |
| built | Built | Urban, infrastructure |
| bare | Bare | Soil, rock, sand |
| snow_and_ice | Snow/Ice | Permanent snow |
| label | Label | Predicted class (0-8) |

#### Class Labels
| Value | Class |
|-------|-------|
| 0 | Water |
| 1 | Trees |
| 2 | Grass |
| 3 | Flooded Vegetation |
| 4 | Crops |
| 5 | Shrub/Scrub |
| 6 | Built |
| 7 | Bare |
| 8 | Snow/Ice |

#### Preprocessing Code (GEE)
```javascript
// Dynamic World Preprocessing
var dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1');

// Filter and get mode (most common class)
var dw_filtered = dw
  .filterBounds(aoi)
  .filterDate('2023-01-01', '2023-12-31');

// Get annual mode for label
var dw_label = dw_filtered.select('label').mode().clip(aoi);

// Get mean probabilities
var dw_probs = dw_filtered.select([
  'water', 'trees', 'grass', 'flooded_vegetation',
  'crops', 'shrub_and_scrub', 'built', 'bare', 'snow_and_ice'
]).mean().clip(aoi);

// Create binary masks for key classes
var water_mask = dw_label.eq(0);
var forest_mask = dw_label.eq(1);
var crop_mask = dw_label.eq(4);
var built_mask = dw_label.eq(6);

// Stack
var dw_stack = ee.Image.cat([
  dw_label.rename('label'),
  dw_probs,
  water_mask.rename('water_mask'),
  forest_mask.rename('forest_mask'),
  crop_mask.rename('crop_mask'),
  built_mask.rename('built_mask')
]);

// Export
Export.image.toDrive({
  image: dw_stack,
  description: 'DynamicWorld_2023',
  region: aoi,
  scale: 10,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});
```

#### Use Cases
- Near real-time land cover monitoring
- Agricultural tracking
- Flood detection
- Deforestation alerts
- Urban growth monitoring
- Change detection

---

### 6. Microsoft Building Footprints

#### Collection ID
```javascript
// Microsoft Building Footprints (USA)
var buildings = ee.FeatureCollection('USGS/WBD/2017/HUC12');

// Alternative: Use direct import
// Note: Microsoft Building Footprints available as vector dataset
// Import URL: https://github.com/microsoft/USBuildingFootprints
```

#### Selection Criteria
| Parameter | Value | Notes |
|-----------|-------|-------|
| Source | Microsoft/USBuildingFootprints | ML-derived |
| Coverage | USA | Full coverage |
| Format | GeoJSON | Vector polygons |
| Accuracy | >99% precision | ML validated |

#### Spatial Subset
```javascript
// Missouri AOI
var missouri = ee.FeatureCollection('TIGER/2018/States')
  .filter(ee.Filter.eq('NAME', 'Missouri'));

// Or specific county
var st_louis = ee.FeatureCollection('TIGER/2018/Counties')
  .filter(ee.Filter.eq('NAME', 'St. Louis'));
```

#### Temporal Subset
- **Static Dataset**: 2018-2020 compilation
- **No temporal filtering**: Single snapshot

#### Attribute Selection
| Attribute | Description |
|-----------|-------------|
| geometry | Building polygon |
| confidence | Detection confidence |

#### Preprocessing Code (GEE)
```javascript
// Microsoft Building Footprints Preprocessing
// Note: Import the building footprints as an asset first

// Assuming buildings are imported as a FeatureCollection
var buildings = ee.FeatureCollection('users/your_username/buildings_missouri');

// Filter by area (remove small artifacts)
var min_area = 20;  // square meters
var buildings_filtered = buildings.filter(
  ee.Filter.gte('area', min_area)
);

// Calculate building density raster
var building_raster = buildings_filtered.reduceToImage({
  properties: ['confidence'],
  reducer: ee.Reducer.mean()
});

// Create building count per grid cell
var grid = building_raster.reproject({
  crs: 'EPSG:4326',
  scale: 30
});

// Calculate building density (buildings per km2)
var building_density = buildings_filtered
  .map(function(f) {
    return f.set('count', 1);
  })
  .reduceToImage({
    properties: ['count'],
    reducer: ee.Reducer.sum()
  })
  .reproject({
    crs: 'EPSG:4326',
    scale: 100
  });

// Export vector
Export.table.toDrive({
  collection: buildings_filtered,
  description: 'Buildings_Missouri',
  fileFormat: 'GeoJSON'
});

// Export raster density
Export.image.toDrive({
  image: building_density,
  description: 'Building_Density',
  region: aoi,
  scale: 100,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});
```

#### Alternative: Direct Download and Processing
```python
import geopandas as gpd
import pandas as pd

def process_building_footprints(state_abbr='MO', output_path=None):
    """
    Process Microsoft Building Footprints for a state
    """
    # Download URL for state
    url = f"https://usbuildingdata.blob.core.windows.net/usbuildings-v2/{state_abbr}.geojson.zip"
    
    # Read buildings
    buildings = gpd.read_file(url)
    
    # Calculate area
    buildings['area'] = buildings.geometry.area
    buildings['centroid'] = buildings.geometry.centroid
    
    # Filter by area
    buildings_filtered = buildings[buildings['area'] >= 20]
    
    # Calculate statistics
    stats = {
        'total_buildings': len(buildings_filtered),
        'total_area_sqkm': buildings_filtered['area'].sum() / 1e6,
        'avg_building_area': buildings_filtered['area'].mean(),
        'median_building_area': buildings_filtered['area'].median()
    }
    
    # Create building density raster (optional)
    # Requires rasterio and rasterization
    
    if output_path:
        buildings_filtered.to_file(output_path)
    
    return buildings_filtered, stats
```

#### Use Cases
- Urban density mapping
- Population estimation
- Flood exposure assessment
- Solar potential analysis
- Infrastructure planning
- Impervious surface estimation

---

## Summary Table

| Data Source | Resolution | Best For | Temporal Range |
|-------------|------------|----------|----------------|
| USGS 3DEP 1m | 1m | Terrain, hydrology | 2015-present |
| USDA NAIP | 0.6-1m | Land cover, vegetation | 2003-present |
| NHDPlus HR | 1:24k | Hydrography, watersheds | Current |
| NLCD | 30m | Land cover change | 2001-2021 |
| GEE 3DEP | 1m | Terrain analysis | Static |
| GEE NAIP | 0.6-1m | High-res land cover | 2003-present |
| Sentinel-2 | 10m | Regional vegetation | 2015-present |
| Landsat C2 | 30m | Long-term change | 1984-present |
| Dynamic World | 10m | Near real-time LC | 2015-present |
| MS Buildings | Vector | Building inventory | 2018-2020 |

---

## Recommended Data Combinations

### For 1m Resolution Analysis (Missouri Focus)
1. **Base Elevation**: USGS 3DEP 1m DEM
2. **High-Resolution Imagery**: NAIP 2022-2024 (4-band)
3. **Hydrology**: NHDPlus HR
4. **Land Cover Context**: NLCD 2021 (resampled) + Dynamic World
5. **Buildings**: Microsoft Building Footprints

### For Regional Analysis (CONUS)
1. **Base Elevation**: 3DEP 10m or 1m where available
2. **Imagery**: Sentinel-2 (10m) + Landsat (30m) time series
3. **Land Cover**: Dynamic World + NLCD
4. **Change Detection**: Landsat Collection 2 (1984-present)

---

*Document Version: 1.0*
*Last Updated: 2024*
*Focus: USA, Missouri, 1m resolution analysis*
