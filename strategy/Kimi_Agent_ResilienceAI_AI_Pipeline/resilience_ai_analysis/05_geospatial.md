# ResilienceAI Geospatial Analysis & Enhancement Design

## Executive Summary

This document provides a comprehensive analysis of the current geospatial capabilities in the ResilienceAI platform and designs advanced AI-powered geospatial enhancements. The analysis covers both the `main` and `claw-autonomous` branches, identifying gaps and proposing cutting-edge geospatial features for disaster vulnerability assessment.

---

## 1. Current Geospatial Capabilities Analysis

### 1.1 Existing Geospatial Components

#### Core Files (Main Branch)

| File | Location | Lines | Purpose |
|------|----------|-------|---------|
| `geo_visualizations.py` | `src/geo_visualizations.py` | 386 | Choropleth, hexbin, 3D visualizations |
| `gee_client.py` | `src/gee_client.py` | 390 | Google Earth Engine satellite data |
| `geojson_export.py` | `src/geojson_export.py` | 285 | GeoJSON export for GIS workflows |
| `network_analysis.py` | `src/network_analysis.py` | 276 | Infrastructure network analysis |
| `spatial_stats.py` | `src/spatial_stats.py` | 345 | Spatial autocorrelation analysis |

#### Enhanced Geospatial (Claw-Autonomous Branch)

| File | Location | Lines | Purpose |
|------|----------|-------|---------|
| `pipeline.py` | `src/geospatial/pipeline.py` | 758 | Main geospatial pipeline |
| `gee_integration.py` | `src/geospatial/gee_integration.py` | 623 | Advanced GEE integration |
| `naip.py` | `src/geospatial/naip.py` | ~400 | USDA NAIP aerial imagery |
| `usgs_3dep.py` | `src/geospatial/usgs_3dep.py` | ~350 | USGS 3DEP 1m DEM data |
| `README.md` | `src/geospatial/README.md` | - | Documentation |

### 1.2 Current Visualization Capabilities

```python
# Current GeoVisualizer class capabilities
class GeoVisualizer:
    - create_choropleth_map()      # County-level choropleth
    - create_hexbin_map()          # H3 hexagon aggregation
    - create_3d_risk_landscape()   # 3D scatter plot
    - create_state_choropleth()    # Single state focus
    - create_heatmap()             # 2D density heatmap
    - create_deckgl_map()          # Deck.gl heatmap layer
```

### 1.3 Current GEE Capabilities

```python
# GEEClient datasets (main branch)
DATASETS = {
    "lst": "MODIS/061/MOD11A2",      # Land Surface Temperature (1km)
    "ndvi": "MODIS/061/MOD13Q1",     # Vegetation Index (250m)
    "pdsi": "GRIDMET/DROUGHT",       # Palmer Drought Index (4km)
    "nightlights": "NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG",  # Night lights (500m)
    "water": "JRC/GSW1_4/GlobalSurfaceWater",  # Surface water (30m)
    "burn": "MODIS/061/MCD64A1",     # Burned area (500m)
}
```

### 1.4 Current Spatial Statistics

```python
# SpatialAnalyzer class capabilities
class SpatialAnalyzer:
    - morans_i()           # Moran's I spatial autocorrelation
    - getis_ord_gi()       # Getis-Ord Gi* hotspot analysis
    - local_morans_i()     # Local Moran's I (LISA)
    - create_spatial_weights()  # Distance-based weights
```

### 1.5 Current Network Analysis

```python
# InfrastructureNetwork class capabilities
class InfrastructureNetwork:
    - build_facility_network()     # NetworkX graph construction
    - calculate_centrality()       # Node importance metrics
    - simulate_cascade_failure()   # Cascade failure simulation
    - find_critical_nodes()        # Bottleneck identification
    - haversine_km()              # Distance calculations
```

---

## 2. Gap Analysis & Enhancement Opportunities

### 2.1 Identified Gaps

| Category | Current State | Gap | Priority |
|----------|--------------|-----|----------|
| **3D Visualization** | Basic 3D scatter | True 3D terrain, extruded polygons | High |
| **Satellite Imagery** | GEE MODIS/Sentinel-2 | Real-time, high-res, change detection | High |
| **Spatial ML** | Basic autocorrelation | Geospatial prediction models | High |
| **Hotspot Analysis** | Getis-Ord Gi* | Space-time clustering, emerging hotspots | Medium |
| **Network Analysis** | Facility networks | Multi-modal, dynamic, supply chain | Medium |
| **Mobile Interface** | Desktop only | Responsive, offline-capable mobile | Medium |
| **AR/VR** | None | Immersive geospatial exploration | Low |
| **Real-time Weather** | NOAA API | Radar overlay, storm tracking | High |

### 2.2 Technology Stack Gaps

| Current | Missing | Purpose |
|---------|---------|---------|
| GeoPandas, Shapely | xarray, rioxarray | Multi-dimensional raster analysis |
| Folium, Plotly | Mapbox GL JS, Cesium | Advanced 3D web mapping |
| NetworkX | OSMnx, igraph | Large-scale network analysis |
| scikit-learn | PySAL, splot | Spatial econometrics |
| Rasterio | xarray-spatial | Scalable raster operations |

---

## 3. Proposed Geospatial Enhancements

### 3.1 Enhancement Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GEOSPATIAL ENHANCEMENT LAYER                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   3D VIZ     │  │   GEE ADV    │  │  SPATIAL ML  │          │
│  │  (PyDeck,    │  │  (Sentinel,  │  │  (PySAL,     │          │
│  │   Cesium)    │  │   NAIP)      │  │   GeoAI)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   HOTSPOT    │  │   NETWORK    │  │   MOBILE     │          │
│  │  ANALYSIS    │  │   ANALYSIS   │  │   INTERFACE  │          │
│  │  (Space-Time)│  │  (Multi-Mode)│  │  (PWA, AR)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
├─────────────────────────────────────────────────────────────────┤
│                    EXISTING GEOSPATIAL CORE                      │
│         (GeoPandas, Rasterio, GEE, NetworkX, Plotly)            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Detailed Enhancement Specifications

### 4.1 3D Geospatial Visualizations

#### 4.1.1 PyDeck Integration

```python
# File: src/geospatial/visualizations_3d.py
"""
3D Geospatial Visualizations using PyDeck and Deck.gl
"""
import pydeck as pdk
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import geopandas as gpd

class Deck3DVisualizer:
    """
    Advanced 3D geospatial visualizations using PyDeck
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.default_view = pdk.ViewState(
            latitude=37.8,
            longitude=-92.5,
            zoom=6,
            pitch=45,
            bearing=0
        )
    
    def create_extruded_choropleth(
        self, 
        geojson_path: str,
        value_column: str = 'risk_score',
        elevation_column: str = 'total_population',
        color_column: str = 'risk_level'
    ) -> pdk.Deck:
        """
        Create 3D extruded choropleth map
        
        Args:
            geojson_path: Path to county boundaries GeoJSON
            value_column: Column for color intensity
            elevation_column: Column for extrusion height
            color_column: Column for color categories
        """
        # Load GeoJSON
        gdf = gpd.read_file(geojson_path)
        
        # Merge with data
        gdf = gdf.merge(
            self.df[['fips', value_column, elevation_column, color_column]],
            left_on='GEOID',
            right_on='fips',
            how='left'
        )
        
        # Create GeoJsonLayer with extrusion
        layer = pdk.Layer(
            'GeoJsonLayer',
            data=gdf.__geo_interface__,
            pickable=True,
            extruded=True,
            get_elevation=f'properties.{elevation_column}',
            elevation_scale=0.01,
            get_fill_color=f'properties.{color_column}',
            get_line_color=[255, 255, 255],
            line_width_min_pixels=1,
            opacity=0.8
        )
        
        return pdk.Deck(
            layers=[layer],
            initial_view_state=self.default_view,
            tooltip={
                'html': '<b>{properties.NAME}</b><br/>'
                        f'Risk: {{{{properties.{value_column}}}}}<br/>'
                        f'Population: {{{{properties.{elevation_column}}}}}',
                'style': {'color': 'white'}
            }
        )
    
    def create_terrain_mesh(self, dem_path: str) -> pdk.Deck:
        """
        Create 3D terrain visualization from DEM
        
        Args:
            dem_path: Path to Digital Elevation Model raster
        """
        import rasterio
        
        with rasterio.open(dem_path) as src:
            elevation = src.read(1)
            transform = src.transform
            bounds = src.bounds
        
        # Create terrain layer
        terrain_layer = pdk.Layer(
            'TerrainLayer',
            elevation_data=dem_path,
            texture='https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryTopo/MapServer/tile/{z}/{y}/{x}',
            bounds=[bounds.left, bounds.bottom, bounds.right, bounds.top],
            elevation_decoder={
                'rScaler': 256,
                'gScaler': 1,
                'bScaler': 1/256,
                'offset': -32768
            },
            mesh_max_error=4,
            wireframe=False,
            color=[255, 255, 255]
        )
        
        return pdk.Deck(
            layers=[terrain_layer],
            initial_view_state=pdk.ViewState(
                latitude=(bounds.top + bounds.bottom) / 2,
                longitude=(bounds.left + bounds.right) / 2,
                zoom=10,
                pitch=60,
                bearing=30
            )
        )
    
    def create_heatmap_3d(
        self,
        value_column: str = 'risk_score',
        radius: int = 10000,
        intensity: float = 1.0
    ) -> pdk.Deck:
        """
        Create 3D heatmap visualization
        """
        plot_df = self.df[['latitude', 'longitude', value_column]].dropna()
        
        layer = pdk.Layer(
            'HeatmapLayer',
            data=plot_df,
            get_position=['longitude', 'latitude'],
            get_weight=value_column,
            radius=radius,
            intensity=intensity,
            threshold=0.05
        )
        
        return pdk.Deck(
            layers=[layer],
            initial_view_state=self.default_view
        )
    
    def create_column_chart_3d(
        self,
        value_column: str = 'risk_score',
        radius: int = 5000,
        elevation_scale: float = 100
    ) -> pdk.Deck:
        """
        Create 3D column chart on map
        """
        plot_df = self.df[['latitude', 'longitude', value_column, 'county_name']].dropna()
        
        layer = pdk.Layer(
            'ColumnLayer',
            data=plot_df,
            get_position=['longitude', 'latitude'],
            get_elevation=value_column,
            elevation_scale=elevation_scale,
            radius=radius,
            get_fill_color=[255, 140, 0, 200],
            pickable=True,
            auto_highlight=True
        )
        
        return pdk.Deck(
            layers=[layer],
            initial_view_state=self.default_view,
            tooltip={
                'html': '<b>{county_name}</b><br/>Risk: {' + value_column + '}',
                'style': {'color': 'white'}
            }
        )
```

#### 4.1.2 Cesium 3D Tiles Integration

```python
# File: src/geospatial/cesium_integration.py
"""
Cesium 3D Tiles integration for high-resolution terrain and buildings
"""
import cesiumpy
import numpy as np
from typing import Dict, List, Optional

class Cesium3DVisualizer:
    """
    Cesium-based 3D visualization for immersive geospatial exploration
    """
    
    def __init__(self, ion_token: Optional[str] = None):
        self.ion_token = ion_token or os.environ.get('CESIUM_ION_TOKEN')
        self.viewer = None
    
    def create_terrain_viewer(
        self,
        center_lat: float = 37.8,
        center_lon: float = -92.5,
        zoom_level: int = 10
    ) -> cesiumpy.Viewer:
        """
        Create Cesium viewer with terrain
        """
        self.viewer = cesiumpy.Viewer(
            terrainProvider=cesiumpy.CesiumTerrainProvider(
                url='https://assets.agi.com/stk-terrain/v1/tilesets/world/tiles'
            )
        )
        
        # Set camera position
        self.viewer.camera.flyTo(
            destination=cesiumpy.Cartesian3.fromDegrees(
                center_lon, center_lat, 10000
            ),
            orientation=cesiumpy.HeadingPitchRoll(
                heading=0.0,
                pitch=-45.0,
                roll=0.0
            )
        )
        
        return self.viewer
    
    def add_3d_buildings(self, osm_buildings: bool = True):
        """
        Add 3D buildings from OSM
        """
        if osm_buildings and self.viewer:
            tileset = cesiumpy.Cesium3DTileset(
                url='https://assets.cesium.com/96188/tileset.json'
            )
            self.viewer.scene.primitives.add(tileset)
    
    def add_risk_extrusions(
        self,
        df: pd.DataFrame,
        height_column: str = 'risk_score',
        color_column: str = 'risk_level'
    ):
        """
        Add extruded risk polygons
        """
        color_map = {
            'Low': cesiumpy.Color.GREEN,
            'Medium': cesiumpy.Color.YELLOW,
            'High': cesiumpy.Color.ORANGE,
            'Critical': cesiumpy.Color.RED
        }
        
        for _, row in df.iterrows():
            if 'geometry' in row and row['geometry'] is not None:
                # Create extruded polygon
                polygon = cesiumpy.PolygonGeometry(
                    polygon=row['geometry'],
                    extrudedHeight=row[height_column] * 1000,  # Scale for visibility
                    material=color_map.get(row[color_column], cesiumpy.Color.GRAY),
                    outline=True,
                    outlineColor=cesiumpy.Color.BLACK
                )
                self.viewer.entities.add(polygon)
```

### 4.2 Advanced Google Earth Engine Integration

#### 4.2.1 Enhanced GEE Client

```python
# File: src/geospatial/gee_advanced.py
"""
Advanced Google Earth Engine integration with real-time and change detection
"""
import ee
import geemap
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)

class AdvancedGEEClient:
    """
    Advanced GEE client with real-time monitoring and change detection
    """
    
    # Enhanced dataset catalog
    DATASETS = {
        # Optical Imagery
        'sentinel2': 'COPERNICUS/S2_SR_HARMONIZED',  # 10m, 5-day revisit
        'landsat8': 'LANDSAT/LC08/C02/T1_L2',        # 30m, 16-day revisit
        'landsat9': 'LANDSAT/LC09/C02/T1_L2',
        'modis': 'MODIS/061/MOD13Q1',                # 250m, 16-day
        
        # SAR (All-weather)
        'sentinel1': 'COPERNICUS/S1_GRD',            # 10m, 6-day revisit
        
        # Weather
        'era5': 'ECMWF/ERA5_LAND/HOURLY',            # 9km, hourly
        'gpm': 'NASA/GPM_L3/IMERG_V06',              # 0.1°, 30-min
        
        # Climate
        'chirps': 'UCSB-CHG/CHIRPS/DAILY',           # 0.05°, daily precipitation
        'terraclimate': 'IDAHO_EPSCOR/TERRACLIMATE', # 4km, monthly
        
        # Land Cover
        'dynamic_world': 'GOOGLE/DYNAMICWORLD/V1',   # 10m, near-real-time
        'esa_worldcover': 'ESA/WorldCover/v200',     # 10m, 2021
        
        # Fire
        'modis_fire': 'MODIS/061/MOD14A1',           # 1km, daily
        'viirs_fire': 'NOAA/VIIRS/001/VNP14A1',      # 375m, daily
        
        # Water
        'jrc_water': 'JRC/GSW1_4/GlobalSurfaceWater', # 30m, monthly
        'grace': 'NASA/GRACE/MASS_GRIDS_V04/MASCON',  # Monthly water storage
    }
    
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.environ.get('GEE_PROJECT_ID')
        self._initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Earth Engine"""
        if not self._initialized:
            try:
                if self.project_id:
                    ee.Initialize(project=self.project_id)
                else:
                    ee.Initialize()
                self._initialized = True
                logger.info("GEE initialized successfully")
            except Exception as e:
                logger.error(f"GEE initialization failed: {e}")
                raise
    
    def get_sentinel2_composite(
        self,
        region: ee.Geometry,
        start_date: str,
        end_date: str,
        cloud_threshold: float = 20
    ) -> ee.Image:
        """
        Create cloud-free Sentinel-2 composite
        
        Args:
            region: Area of interest
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            cloud_threshold: Maximum cloud percentage
        
        Returns:
            Median composite image
        """
        collection = (ee.ImageCollection(self.DATASETS['sentinel2'])
            .filterBounds(region)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_threshold))
            .map(self._mask_clouds_s2))
        
        return collection.median().clip(region)
    
    def _mask_clouds_s2(self, image: ee.Image) -> ee.Image:
        """Mask clouds in Sentinel-2 imagery"""
        qa = image.select('QA60')
        cloud_bit_mask = 1 << 10
        cirrus_bit_mask = 1 << 11
        mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
            qa.bitwiseAnd(cirrus_bit_mask).eq(0))
        return image.updateMask(mask)
    
    def calculate_ndvi(self, image: ee.Image) -> ee.Image:
        """Calculate NDVI from Sentinel-2"""
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        return image.addBands(ndvi)
    
    def calculate_ndwi(self, image: ee.Image) -> ee.Image:
        """Calculate NDWI (Water Index)"""
        ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
        return image.addBands(ndwi)
    
    def detect_changes(
        self,
        region: ee.Geometry,
        date_before: str,
        date_after: str,
        threshold: float = 2.0
    ) -> ee.Image:
        """
        Detect changes between two time periods using Sentinel-2
        
        Args:
            region: Area of interest
            date_before: Date before event (YYYY-MM-DD)
            date_after: Date after event (YYYY-MM-DD)
            threshold: Change detection threshold (standard deviations)
        
        Returns:
            Change detection image
        """
        # Get before and after composites
        before = self.get_sentinel2_composite(
            region, 
            (datetime.strptime(date_before, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d'),
            date_before
        )
        
        after = self.get_sentinel2_composite(
            region,
            date_after,
            (datetime.strptime(date_after, '%Y-%m-%d') + timedelta(days=30)).strftime('%Y-%m-%d')
        )
        
        # Calculate spectral change vector
        before_ndvi = self.calculate_ndvi(before).select('NDVI')
        after_ndvi = self.calculate_ndvi(after).select('NDVI')
        
        ndvi_change = after_ndvi.subtract(before_ndvi).rename('NDVI_change')
        
        # Detect significant changes
        mean_change = ndvi_change.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=30,
            maxPixels=1e9
        ).get('NDVI_change')
        
        std_change = ndvi_change.reduceRegion(
            reducer=ee.Reducer.stdDev(),
            geometry=region,
            scale=30,
            maxPixels=1e9
        ).get('NDVI_change')
        
        # Create change mask
        change_mask = ndvi_change.abs().gt(
            ee.Number(mean_change).add(ee.Number(std_change).multiply(threshold))
        )
        
        return ndvi_change.updateMask(change_mask)
    
    def monitor_flood_extent(
        self,
        region: ee.Geometry,
        flood_date: str,
        pre_flood_months: int = 3
    ) -> ee.Image:
        """
        Monitor flood extent using Sentinel-1 SAR (all-weather)
        
        Args:
            region: Area of interest
            flood_date: Flood event date (YYYY-MM-DD)
            pre_flood_months: Months of pre-flood data
        
        Returns:
            Flood extent mask
        """
        flood_dt = datetime.strptime(flood_date, '%Y-%m-%d')
        pre_start = (flood_dt - timedelta(days=pre_flood_months*30)).strftime('%Y-%m-%d')
        
        # Get pre-flood reference
        pre_collection = (ee.ImageCollection(self.DATASETS['sentinel1'])
            .filterBounds(region)
            .filterDate(pre_start, flood_date)
            .filter(ee.Filter.eq('instrumentMode', 'IW'))
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')))
        
        pre_flood = pre_collection.select('VV').median()
        
        # Get during-flood image
        flood_collection = (ee.ImageCollection(self.DATASETS['sentinel1'])
            .filterBounds(region)
            .filterDate(flood_date, (flood_dt + timedelta(days=7)).strftime('%Y-%m-%d'))
            .filter(ee.Filter.eq('instrumentMode', 'IW'))
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')))
        
        flood_image = flood_collection.select('VV').median()
        
        # Detect water (lower backscatter = water)
        water_threshold = -20  # dB
        flood_extent = flood_image.lt(water_threshold).And(
            pre_flood.gt(water_threshold)
        )
        
        return flood_extent.rename('flood_extent')
    
    def get_real_time_weather_overlay(
        self,
        region: ee.Geometry,
        product: str = 'gpm'
    ) -> ee.Image:
        """
        Get real-time weather data overlay
        
        Args:
            region: Area of interest
            product: 'gpm' (precipitation), 'era5' (temperature/wind)
        
        Returns:
            Weather overlay image
        """
        if product == 'gpm':
            # GPM precipitation (mm/hr)
            collection = ee.ImageCollection(self.DATASETS['gpm'])
            latest = collection.filterBounds(region).sort('system:time_start', False).first()
            return latest.select('precipitationCal').clip(region)
        
        elif product == 'era5':
            # ERA5 temperature (K)
            collection = ee.ImageCollection(self.DATASETS['era5'])
            latest = collection.filterBounds(region).sort('system:time_start', False).first()
            return latest.select('temperature_2m').clip(region)
        
        else:
            raise ValueError(f"Unknown product: {product}")
    
    def export_to_geotiff(
        self,
        image: ee.Image,
        region: ee.Geometry,
        filename: str,
        scale: int = 30
    ) -> str:
        """
        Export Earth Engine image to GeoTIFF
        
        Args:
            image: EE Image to export
            region: Export region
            filename: Output filename
            scale: Resolution in meters
        
        Returns:
            Path to exported file
        """
        import geemap
        
        output_path = f"/tmp/{filename}.tif"
        geemap.ee_export_image(
            image,
            filename=output_path,
            scale=scale,
            region=region,
            file_per_band=False
        )
        
        return output_path
    
    def create_time_series_chart(
        self,
        collection: ee.ImageCollection,
        region: ee.Geometry,
        band: str,
        reducer: str = 'mean'
    ) -> pd.DataFrame:
        """
        Create time series from image collection
        
        Args:
            collection: EE ImageCollection
            region: Area of interest
            band: Band to extract
            reducer: Reduction method ('mean', 'median', 'sum')
        
        Returns:
            DataFrame with time series
        """
        reducer_map = {
            'mean': ee.Reducer.mean(),
            'median': ee.Reducer.median(),
            'sum': ee.Reducer.sum(),
            'stdDev': ee.Reducer.stdDev()
        }
        
        # Create time series
        def extract_date_value(image):
            date = image.date().format('YYYY-MM-dd')
            value = image.select(band).reduceRegion(
                reducer=reducer_map.get(reducer, ee.Reducer.mean()),
                geometry=region,
                scale=100,
                maxPixels=1e9
            ).get(band)
            return ee.Feature(None, {'date': date, 'value': value})
        
        time_series = collection.map(extract_date_value)
        
        # Convert to DataFrame
        features = time_series.getInfo()['features']
        data = [
            {'date': f['properties']['date'], 'value': f['properties']['value']}
            for f in features
        ]
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        return df
```

### 4.3 Spatial Autocorrelation & Hotspot Analysis

#### 4.3.1 Advanced Spatial Statistics

```python
# File: src/geospatial/spatial_analysis_advanced.py
"""
Advanced spatial statistics with PySAL integration
"""
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.spatial.distance import cdist
from scipy import stats
from typing import Dict, List, Optional, Tuple, Union
import warnings

# Optional PySAL imports
try:
    import libpysal
    from libpysal.weights import Queen, Rook, KNN, DistanceBand
    from esda import Moran, Moran_Local, Geary, GetisOrd_G, GetisOrd_G_Local
    from esda import space_time_knox, space_time_knox_from_dataframe
    from splot.esda import moran_scatterplot, lisa_cluster
    PYSAL_AVAILABLE = True
except ImportError:
    PYSAL_AVAILABLE = False
    warnings.warn("PySAL not available. Using fallback implementations.")

class AdvancedSpatialAnalyzer:
    """
    Advanced spatial statistics for vulnerability hotspot detection
    """
    
    def __init__(self, gdf: gpd.GeoDataFrame):
        self.gdf = gdf
        self.weights = None
        self._build_weights()
    
    def _build_weights(
        self,
        weight_type: str = 'queen',
        k: int = 4,
        threshold: float = None
    ):
        """
        Build spatial weights matrix
        
        Args:
            weight_type: 'queen', 'rook', 'knn', 'distance'
            k: Number of nearest neighbors (for KNN)
            threshold: Distance threshold in km (for distance-based)
        """
        if not PYSAL_AVAILABLE:
            self.weights = None
            return
        
        if weight_type == 'queen':
            self.weights = Queen.from_dataframe(self.gdf)
        elif weight_type == 'rook':
            self.weights = Rook.from_dataframe(self.gdf)
        elif weight_type == 'knn':
            self.weights = KNN.from_dataframe(self.gdf, k=k)
        elif weight_type == 'distance':
            if threshold is None:
                threshold = self._calculate_threshold()
            self.weights = DistanceBand.from_dataframe(
                self.gdf, threshold=threshold, binary=True
            )
        
        # Row-standardize weights
        self.weights.transform = 'r'
    
    def _calculate_threshold(self) -> float:
        """Calculate natural distance threshold"""
        centroids = self.gdf.geometry.centroid
        coords = np.column_stack([centroids.x, centroids.y])
        
        # Calculate pairwise distances
        distances = cdist(coords, coords)
        
        # Use mean of k-nearest neighbor distances
        k = min(4, len(coords) - 1)
        knn_distances = np.partition(distances, k, axis=1)[:, 1:k+1]
        threshold = np.mean(knn_distances) * 1.5
        
        return threshold
    
    def morans_i_analysis(
        self,
        variable: str,
        permutations: int = 999
    ) -> Dict:
        """
        Comprehensive Moran's I analysis
        
        Args:
            variable: Variable to analyze
            permutations: Number of permutations for significance
        
        Returns:
            Dictionary with Moran's I statistics
        """
        if not PYSAL_AVAILABLE or self.weights is None:
            return self._morans_i_fallback(variable)
        
        y = self.gdf[variable].values
        
        # Global Moran's I
        mi = Moran(y, self.weights, permutations=permutations)
        
        # Local Moran's I (LISA)
        lisa = Moran_Local(y, self.weights, permutations=permutations)
        
        # Create results
        results = {
            'global_morans_i': mi.I,
            'expected_i': mi.EI,
            'z_score': mi.z_norm,
            'p_value': mi.p_norm,
            'interpretation': self._interpret_morans_i(mi.I, mi.p_norm),
            'local_morans_i': lisa.Is,
            'local_p_values': lisa.p_sim,
            'quadrant': lisa.q,  # 1=HH, 2=LH, 3=LL, 4=HL
            'significant': lisa.p_sim < 0.05
        }
        
        # Add cluster labels to GeoDataFrame
        self.gdf[f'{variable}_lisa_cluster'] = self._get_lisa_labels(lisa)
        
        return results
    
    def _morans_i_fallback(self, variable: str) -> Dict:
        """Fallback Moran's I calculation without PySAL"""
        y = self.gdf[variable].values
        n = len(y)
        
        # Standardize
        y_std = (y - np.mean(y)) / np.std(y)
        
        # Build distance-based weights
        centroids = self.gdf.geometry.centroid
        coords = np.column_stack([centroids.x, centroids.y])
        distances = cdist(coords, coords)
        
        # Binary weights (neighbors within threshold)
        threshold = np.percentile(distances[distances > 0], 25)
        w = (distances <= threshold).astype(float)
        np.fill_diagonal(w, 0)
        
        # Row standardize
        row_sums = w.sum(axis=1)
        row_sums[row_sums == 0] = 1
        w = w / row_sums[:, np.newaxis]
        
        # Calculate Moran's I
        numerator = np.sum(w * np.outer(y_std, y_std))
        denominator = np.sum(y_std ** 2)
        
        I = (n / w.sum()) * (numerator / denominator)
        
        # Expected value
        EI = -1 / (n - 1)
        
        return {
            'global_morans_i': I,
            'expected_i': EI,
            'z_score': None,
            'p_value': None,
            'interpretation': self._interpret_morans_i(I, 0.05),
            'local_morans_i': None,
            'local_p_values': None,
            'quadrant': None,
            'significant': None
        }
    
    def _interpret_morans_i(self, I: float, p_value: float) -> str:
        """Interpret Moran's I value"""
        if p_value > 0.05:
            return "Random spatial distribution (not significant)"
        elif I > 0.3:
            return "Strong positive spatial autocorrelation (clustered)"
        elif I > 0:
            return "Weak positive spatial autocorrelation"
        elif I < -0.3:
            return "Strong negative spatial autocorrelation (dispersed)"
        else:
            return "Weak negative spatial autocorrelation"
    
    def _get_lisa_labels(self, lisa) -> List[str]:
        """Convert LISA quadrants to labels"""
        labels = []
        for q, sig in zip(lisa.q, lisa.p_sim < 0.05):
            if not sig:
                labels.append('Not Significant')
            elif q == 1:
                labels.append('High-High (Hotspot)')
            elif q == 2:
                labels.append('Low-High (Outlier)')
            elif q == 3:
                labels.append('Low-Low (Coldspot)')
            elif q == 4:
                labels.append('High-Low (Outlier)')
        return labels
    
    def getis_ord_gi_star(
        self,
        variable: str,
        permutations: int = 999
    ) -> Dict:
        """
        Getis-Ord Gi* hotspot analysis
        
        Args:
            variable: Variable to analyze
            permutations: Number of permutations
        
        Returns:
            Dictionary with Gi* statistics
        """
        if not PYSAL_AVAILABLE or self.weights is None:
            return self._gi_star_fallback(variable)
        
        y = self.gdf[variable].values
        
        # Calculate Gi*
        gi_star = GetisOrd_G_Local(y, self.weights, permutations=permutations)
        
        results = {
            'gi_star_values': gi_star.Zs,
            'p_values': gi_star.p_sim,
            'hotspots': gi_star.Zs > 1.96,  # p < 0.05
            'coldspots': gi_star.Zs < -1.96,
            'significant': np.abs(gi_star.Zs) > 1.96
        }
        
        # Add to GeoDataFrame
        self.gdf[f'{variable}_gi_star'] = gi_star.Zs
        self.gdf[f'{variable}_gi_pvalue'] = gi_star.p_sim
        self.gdf[f'{variable}_hotspot'] = [
            'Hotspot' if h else 'Coldspot' if c else 'Not Significant'
            for h, c in zip(results['hotspots'], results['coldspots'])
        ]
        
        return results
    
    def _gi_star_fallback(self, variable: str) -> Dict:
        """Fallback Gi* calculation"""
        y = self.gdf[variable].values
        n = len(y)
        
        # Build weights
        centroids = self.gdf.geometry.centroid
        coords = np.column_stack([centroids.x, centroids.y])
        distances = cdist(coords, coords)
        
        threshold = np.percentile(distances[distances > 0], 25)
        w = (distances <= threshold).astype(float)
        np.fill_diagonal(w, 0)
        
        # Calculate Gi* (simplified)
        w_sum = w.sum(axis=1)
        gi = np.array([np.sum(w[i] * y) for i in range(n)])
        
        # Standardize
        gi_z = (gi - np.mean(gi)) / np.std(gi)
        
        return {
            'gi_star_values': gi_z,
            'p_values': None,
            'hotspots': gi_z > 1.96,
            'coldspots': gi_z < -1.96,
            'significant': np.abs(gi_z) > 1.96
        }
    
    def emerging_hotspot_analysis(
        self,
        variable: str,
        time_column: str = 'year',
        n_time_periods: int = 5
    ) -> gpd.GeoDataFrame:
        """
        Emerging hotspot analysis (space-time clustering)
        
        Args:
            variable: Variable to analyze
            time_column: Time period column
            n_time_periods: Number of time periods to analyze
        
        Returns:
            GeoDataFrame with hotspot classifications
        """
        # Group by time periods
        time_groups = self.gdf.groupby(time_column)
        
        # Calculate Gi* for each time period
        gi_results = []
        for time, group in time_groups:
            analyzer = AdvancedSpatialAnalyzer(group)
            gi = analyzer.getis_ord_gi_star(variable)
            gi['time'] = time
            gi_results.append(gi)
        
        # Classify patterns
        classifications = self._classify_hotspot_trends(gi_results)
        
        self.gdf['hotspot_trend'] = classifications
        
        return self.gdf
    
    def _classify_hotspot_trends(self, gi_results: List[Dict]) -> List[str]:
        """
        Classify hotspot trends based on Gi* patterns
        
        Categories (from ArcGIS Emerging Hot Spot Analysis):
        - New Hotspot: Significant only in final time period
        - Consecutive Hotspot: Significant in final 2+ periods
        - Sporadic Hotspot: Significant in some periods
        - Historical Hotspot: Significant in early periods, not recent
        - Diminishing Hotspot: Significant and decreasing
        - Coldspot: Negative Gi* values
        """
        # Simplified classification
        n = len(gi_results[0]['gi_star_values'])
        classifications = []
        
        for i in range(n):
            gi_values = [r['gi_star_values'][i] for r in gi_results]
            significant = [r['significant'][i] for r in gi_results]
            
            if not any(significant):
                classifications.append('Not Significant')
            elif all(significant) and all(g > 0 for g in gi_values):
                classifications.append('Persistent Hotspot')
            elif significant[-1] and gi_values[-1] > 0:
                classifications.append('New Hotspot')
            elif any(significant) and not significant[-1]:
                classifications.append('Historical Hotspot')
            else:
                classifications.append('Sporadic Hotspot')
        
        return classifications
    
    def gearys_c(self, variable: str) -> Dict:
        """
        Calculate Geary's c statistic
        
        Geary's c ranges from 0 (clustered) to ~2 (dispersed)
        Values near 1 indicate random distribution
        """
        if not PYSAL_AVAILABLE or self.weights is None:
            return {'gearys_c': None, 'interpretation': 'PySAL not available'}
        
        y = self.gdf[variable].values
        gc = Geary(y, self.weights)
        
        interpretation = (
            "Clustered" if gc.C < 0.7 else
            "Random" if gc.C < 1.3 else
            "Dispersed"
        )
        
        return {
            'gearys_c': gc.C,
            'expected_c': gc.EC,
            'z_score': gc.z_norm,
            'p_value': gc.p_norm,
            'interpretation': interpretation
        }
```

### 4.4 Network Analysis for Infrastructure

#### 4.4.1 Advanced Network Analysis

```python
# File: src/geospatial/network_analysis_advanced.py
"""
Advanced infrastructure network analysis with multi-modal support
"""
import numpy as np
import pandas as pd
import geopandas as gpd
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import warnings

try:
    import networkx as nx
    from networkx.algorithms import approximation as approx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

try:
    import osmnx as ox
    OSMNX_AVAILABLE = True
except ImportError:
    OSMNX_AVAILABLE = False

try:
    import igraph as ig
    IGRAPH_AVAILABLE = True
except ImportError:
    IGRAPH_AVAILABLE = False

class NetworkMode(Enum):
    """Transportation network modes"""
    ROAD = "road"
    RAIL = "rail"
    POWER = "power"
    WATER = "water"
    TELECOM = "telecom"
    MULTI = "multi"

@dataclass
class Facility:
    """Infrastructure facility"""
    id: str
    name: str
    facility_type: str
    latitude: float
    longitude: float
    capacity: float
    status: str = "operational"
    criticality_score: float = 0.0

@dataclass
class NetworkEdge:
    """Network edge with vulnerability attributes"""
    source: str
    target: str
    mode: NetworkMode
    distance_km: float
    capacity: float
    vulnerability: float = 0.0
    restoration_time: float = 0.0

class MultiModalNetworkAnalyzer:
    """
    Multi-modal infrastructure network analysis
    """
    
    def __init__(self):
        self.networks: Dict[NetworkMode, nx.Graph] = {}
        self.facilities: Dict[str, Facility] = {}
        self.intermodal_connections: List[Tuple[str, str]] = []
    
    def build_road_network(
        self,
        place: str,
        network_type: str = 'drive'
    ) -> nx.Graph:
        """
        Build road network from OpenStreetMap
        
        Args:
            place: Location name (e.g., "St. Louis, Missouri, USA")
            network_type: 'drive', 'walk', 'bike', 'all'
        
        Returns:
            NetworkX graph
        """
        if not OSMNX_AVAILABLE:
            raise ImportError("OSMnx required for road network analysis")
        
        G = ox.graph_from_place(place, network_type=network_type)
        
        # Add vulnerability attributes
        for u, v, data in G.edges(data=True):
            # Calculate vulnerability based on road type
            highway = data.get('highway', 'unclassified')
            vulnerability_map = {
                'motorway': 0.1,
                'trunk': 0.15,
                'primary': 0.2,
                'secondary': 0.3,
                'tertiary': 0.4,
                'residential': 0.5,
                'unclassified': 0.6
            }
            data['vulnerability'] = vulnerability_map.get(highway, 0.5)
            data['restoration_time'] = data['vulnerability'] * 24  # hours
        
        self.networks[NetworkMode.ROAD] = G
        return G
    
    def build_facility_network(
        self,
        facilities_df: pd.DataFrame,
        connection_distance_km: float = 50
    ) -> nx.Graph:
        """
        Build facility-to-facility network
        
        Args:
            facilities_df: DataFrame with facility data
            connection_distance_km: Maximum connection distance
        
        Returns:
            NetworkX graph
        """
        G = nx.Graph()
        
        # Add nodes
        for _, row in facilities_df.iterrows():
            facility = Facility(
                id=str(row.get('id', row.name)),
                name=row.get('name', 'Unknown'),
                facility_type=row.get('type', 'general'),
                latitude=row['latitude'],
                longitude=row['longitude'],
                capacity=row.get('capacity', 100)
            )
            
            self.facilities[facility.id] = facility
            G.add_node(
                facility.id,
                **facility.__dict__
            )
        
        # Add edges based on distance
        facility_list = list(self.facilities.values())
        for i, f1 in enumerate(facility_list):
            for f2 in facility_list[i+1:]:
                dist = self._haversine_km(
                    f1.latitude, f1.longitude,
                    f2.latitude, f2.longitude
                )
                
                if dist <= connection_distance_km:
                    G.add_edge(
                        f1.id, f2.id,
                        distance_km=dist,
                        weight=dist,
                        vulnerability=dist / connection_distance_km
                    )
        
        self.networks[NetworkMode.MULTI] = G
        return G
    
    def _haversine_km(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """Calculate haversine distance in km"""
        R = 6371  # Earth radius
        
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        return R * 2 * np.arcsin(np.sqrt(a))
    
    def calculate_centrality_measures(
        self,
        network_mode: NetworkMode = NetworkMode.MULTI
    ) -> pd.DataFrame:
        """
        Calculate multiple centrality measures
        
        Returns:
            DataFrame with centrality scores
        """
        G = self.networks.get(network_mode)
        if G is None:
            raise ValueError(f"Network {network_mode} not built")
        
        centrality_measures = {}
        
        # Degree centrality
        centrality_measures['degree'] = nx.degree_centrality(G)
        
        # Betweenness centrality (bottleneck detection)
        centrality_measures['betweenness'] = nx.betweenness_centrality(
            G, weight='distance_km'
        )
        
        # Closeness centrality (accessibility)
        centrality_measures['closeness'] = nx.closeness_centrality(G)
        
        # Eigenvector centrality (influence)
        try:
            centrality_measures['eigenvector'] = nx.eigenvector_centrality(
                G, weight='distance_km', max_iter=1000
            )
        except:
            centrality_measures['eigenvector'] = {n: 0 for n in G.nodes()}
        
        # PageRank
        centrality_measures['pagerank'] = nx.pagerank(
            G, weight='distance_km'
        )
        
        # Convert to DataFrame
        df = pd.DataFrame(centrality_measures)
        df['node_id'] = df.index
        
        # Calculate composite criticality score
        df['criticality_score'] = (
            df['degree'] * 0.2 +
            df['betweenness'] * 0.3 +
            df['closeness'] * 0.2 +
            df['eigenvector'] * 0.15 +
            df['pagerank'] * 0.15
        )
        
        return df.sort_values('criticality_score', ascending=False)
    
    def find_critical_nodes(
        self,
        network_mode: NetworkMode = NetworkMode.MULTI,
        top_n: int = 10
    ) -> List[Dict]:
        """
        Find most critical nodes in the network
        
        Args:
            network_mode: Network to analyze
            top_n: Number of top critical nodes
        
        Returns:
            List of critical node information
        """
        G = self.networks.get(network_mode)
        if G is None:
            return []
        
        # Calculate centrality
        centrality_df = self.calculate_centrality_measures(network_mode)
        
        # Get top critical nodes
        critical_nodes = []
        for _, row in centrality_df.head(top_n).iterrows():
            node_id = row['node_id']
            node_data = G.nodes[node_id]
            
            critical_nodes.append({
                'id': node_id,
                'name': node_data.get('name', 'Unknown'),
                'type': node_data.get('facility_type', 'Unknown'),
                'criticality_score': row['criticality_score'],
                'betweenness': row['betweenness'],
                'impact_if_lost': self._estimate_node_impact(G, node_id)
            })
        
        return critical_nodes
    
    def _estimate_node_impact(
        self,
        G: nx.Graph,
        node: str
    ) -> Dict:
        """Estimate impact of losing a node"""
        # Create copy without the node
        G_removed = G.copy()
        G_removed.remove_node(node)
        
        # Calculate network degradation
        original_connected = nx.is_connected(G)
        removed_connected = nx.is_connected(G_removed)
        
        if original_connected and not removed_connected:
            # Node was critical for connectivity
            n_components = nx.number_connected_components(G_removed)
            largest_component = len(max(nx.connected_components(G_removed), key=len))
            
            return {
                'connectivity_lost': True,
                'n_components_after': n_components,
                'largest_component_size': largest_component,
                'impact_level': 'Critical'
            }
        
        # Calculate average shortest path increase
        try:
            original_avg_path = nx.average_shortest_path_length(G)
            removed_avg_path = nx.average_shortest_path_length(G_removed)
            path_increase = (removed_avg_path - original_avg_path) / original_avg_path
            
            return {
                'connectivity_lost': False,
                'avg_path_increase_pct': path_increase * 100,
                'impact_level': 'High' if path_increase > 0.2 else 'Medium'
            }
        except:
            return {
                'connectivity_lost': False,
                'impact_level': 'Low'
            }
    
    def simulate_cascade_failure(
        self,
        initial_failures: List[str],
        network_mode: NetworkMode = NetworkMode.MULTI,
        cascade_threshold: float = 0.7
    ) -> Dict:
        """
        Simulate cascade failure scenario
        
        Args:
            initial_failures: List of initially failing nodes
            network_mode: Network to simulate
            cascade_threshold: Load threshold for cascade
        
        Returns:
            Cascade simulation results
        """
        G = self.networks.get(network_mode)
        if G is None:
            raise ValueError(f"Network {network_mode} not built")
        
        failed_nodes = set(initial_failures)
        cascade_steps = [{ 'step': 0, 'failed': list(initial_failures) }]
        
        step = 0
        while True:
            step += 1
            newly_failed = []
            
            # Check neighbors of failed nodes
            for failed_node in cascade_steps[-1]['failed']:
                for neighbor in G.neighbors(failed_node):
                    if neighbor in failed_nodes:
                        continue
                    
                    # Calculate load on neighbor
                    neighbor_load = self._calculate_node_load(G, neighbor, failed_nodes)
                    neighbor_capacity = G.nodes[neighbor].get('capacity', 100)
                    
                    if neighbor_load / neighbor_capacity > cascade_threshold:
                        newly_failed.append(neighbor)
                        failed_nodes.add(neighbor)
            
            if not newly_failed:
                break
            
            cascade_steps.append({
                'step': step,
                'failed': newly_failed,
                'cumulative_failed': len(failed_nodes)
            })
        
        # Calculate impact metrics
        total_nodes = len(G.nodes())
        failure_rate = len(failed_nodes) / total_nodes
        
        # Check network fragmentation
        G_remaining = G.copy()
        G_remaining.remove_nodes_from(failed_nodes)
        
        if len(G_remaining) > 0:
            n_components = nx.number_connected_components(G_remaining)
            largest_component_ratio = len(max(
                nx.connected_components(G_remaining), key=len
            )) / len(G_remaining)
        else:
            n_components = 0
            largest_component_ratio = 0
        
        return {
            'initial_failures': initial_failures,
            'total_failed': len(failed_nodes),
            'failure_rate': failure_rate,
            'cascade_steps': cascade_steps,
            'n_components_after': n_components,
            'largest_component_ratio': largest_component_ratio,
            'network_survivability': 1 - failure_rate
        }
    
    def _calculate_node_load(
        self,
        G: nx.Graph,
        node: str,
        failed_nodes: Set[str]
    ) -> float:
        """Calculate load on a node considering failures"""
        # Simplified load calculation
        load = 0
        for neighbor in G.neighbors(node):
            if neighbor not in failed_nodes:
                load += G.edges[node, neighbor].get('weight', 1)
        return load
    
    def find_minimum_spanning_tree(
        self,
        network_mode: NetworkMode = NetworkMode.MULTI
    ) -> nx.Graph:
        """
        Find minimum spanning tree for efficient network design
        """
        G = self.networks.get(network_mode)
        if G is None:
            raise ValueError(f"Network {network_mode} not built")
        
        return nx.minimum_spanning_tree(G, weight='distance_km')
    
    def calculate_network_resilience(
        self,
        network_mode: NetworkMode = NetworkMode.MULTI,
        n_random_failures: int = 100
    ) -> Dict:
        """
        Calculate network resilience through random failure simulation
        
        Args:
            network_mode: Network to analyze
            n_random_failures: Number of random failure scenarios
        
        Returns:
            Resilience metrics
        """
        G = self.networks.get(network_mode)
        if G is None:
            raise ValueError(f"Network {network_mode} not built")
        
        nodes = list(G.nodes())
        resilience_scores = []
        
        for _ in range(n_random_failures):
            # Random node failure
            failed_node = np.random.choice(nodes)
            
            # Calculate impact
            impact = self._estimate_node_impact(G, failed_node)
            
            # Convert impact to resilience score
            if impact.get('connectivity_lost'):
                resilience_scores.append(0)
            else:
                resilience_scores.append(1 - impact.get('avg_path_increase_pct', 0) / 100)
        
        return {
            'mean_resilience': np.mean(resilience_scores),
            'std_resilience': np.std(resilience_scores),
            'min_resilience': np.min(resilience_scores),
            'max_resilience': np.max(resilience_scores),
            'resilience_distribution': resilience_scores
        }
```

### 4.5 Geospatial Prediction Models

#### 4.5.1 Spatial Machine Learning

```python
# File: src/geospatial/spatial_ml.py
"""
Geospatial prediction models with spatial cross-validation
"""
import numpy as np
import pandas as pd
import geopandas as gpd
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from typing import Dict, List, Optional, Tuple, Union
import warnings

try:
    from sklearn.model_selection import GroupKFold
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class SpatialCrossValidator:
    """
    Spatial cross-validation to prevent data leakage
    """
    
    def __init__(
        self,
        gdf: gpd.GeoDataFrame,
        n_splits: int = 5,
        buffer_distance_km: float = 50
    ):
        self.gdf = gdf
        self.n_splits = n_splits
        self.buffer_distance_km = buffer_distance_km
        self.buffer_distance_deg = buffer_distance_km / 111  # Approximate
    
    def split(self, X: np.ndarray, y: np.ndarray):
        """
        Generate spatially-aware train/test splits
        
        Yields:
            train_indices, test_indices
        """
        # Create spatial clusters using k-means on centroids
        from sklearn.cluster import KMeans
        
        centroids = self.gdf.geometry.centroid
        coords = np.column_stack([centroids.x, centroids.y])
        
        kmeans = KMeans(n_clusters=self.n_splits, random_state=42)
        clusters = kmeans.fit_predict(coords)
        
        # Yield splits ensuring spatial separation
        for i in range(self.n_splits):
            test_mask = clusters == i
            
            # Create buffer around test set
            test_coords = coords[test_mask]
            train_mask = np.ones(len(coords), dtype=bool)
            
            for test_point in test_coords:
                distances = np.sqrt(
                    (coords[:, 0] - test_point[0])**2 +
                    (coords[:, 1] - test_point[1])**2
                )
                train_mask &= distances > self.buffer_distance_deg
            
            train_mask &= ~test_mask
            
            yield np.where(train_mask)[0], np.where(test_mask)[0]

class GeospatialPredictor:
    """
    Geospatial prediction models with spatial features
    """
    
    def __init__(self, gdf: gpd.GeoDataFrame):
        self.gdf = gdf
        self.model = None
        self.feature_importance = None
        self.spatial_cv_scores = None
    
    def engineer_spatial_features(
        self,
        target_variable: str,
        neighbor_features: List[str],
        n_neighbors: int = 5
    ) -> gpd.GeoDataFrame:
        """
        Engineer spatial features from neighboring areas
        
        Args:
            target_variable: Variable to predict
            neighbor_features: Features to aggregate from neighbors
            n_neighbors: Number of nearest neighbors
        
        Returns:
            GeoDataFrame with spatial features
        """
        from scipy.spatial import cKDTree
        
        # Get centroids
        centroids = self.gdf.geometry.centroid
        coords = np.column_stack([centroids.x, centroids.y])
        
        # Build KD-tree
        tree = cKDTree(coords)
        
        # Find neighbors
        distances, indices = tree.query(coords, k=n_neighbors+1)
        
        # Create spatial features
        for feature in neighbor_features:
            # Neighbor mean
            neighbor_means = []
            for i, neighbors in enumerate(indices):
                # Exclude self (first neighbor)
                neighbor_values = self.gdf.iloc[neighbors[1:]][feature].values
                neighbor_means.append(np.mean(neighbor_values))
            
            self.gdf[f'{feature}_neighbor_mean'] = neighbor_means
            
            # Neighbor std
            neighbor_stds = []
            for i, neighbors in enumerate(indices):
                neighbor_values = self.gdf.iloc[neighbors[1:]][feature].values
                neighbor_stds.append(np.std(neighbor_values))
            
            self.gdf[f'{feature}_neighbor_std'] = neighbor_stds
            
            # Spatial lag (weighted by inverse distance)
            spatial_lags = []
            for i, (dists, neighbors) in enumerate(zip(distances, indices)):
                weights = 1 / (dists[1:] + 0.001)  # Avoid division by zero
                weights = weights / weights.sum()
                neighbor_values = self.gdf.iloc[neighbors[1:]][feature].values
                spatial_lags.append(np.sum(weights * neighbor_values))
            
            self.gdf[f'{feature}_spatial_lag'] = spatial_lags
        
        # Distance to nearest hotspot
        if 'risk_score' in self.gdf.columns:
            high_risk_mask = self.gdf['risk_score'] > self.gdf['risk_score'].quantile(0.8)
            high_risk_coords = coords[high_risk_mask]
            
            if len(high_risk_coords) > 0:
                high_risk_tree = cKDTree(high_risk_coords)
                distances_to_hotspot, _ = high_risk_tree.query(coords, k=1)
                self.gdf['distance_to_hotspot_km'] = distances_to_hotspot * 111
        
        return self.gdf
    
    def train(
        self,
        target_variable: str,
        feature_columns: List[str],
        model_type: str = 'random_forest',
        use_spatial_cv: bool = True
    ) -> Dict:
        """
        Train geospatial prediction model
        
        Args:
            target_variable: Variable to predict
            feature_columns: Feature columns to use
            model_type: 'random_forest' or 'gradient_boosting'
            use_spatial_cv: Use spatial cross-validation
        
        Returns:
            Training results
        """
        # Prepare data
        X = self.gdf[feature_columns].fillna(0).values
        y = self.gdf[target_variable].values
        
        # Select model
        if model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Cross-validation
        if use_spatial_cv:
            cv = SpatialCrossValidator(self.gdf, n_splits=5)
            cv_scores = []
            
            for train_idx, test_idx in cv.split(X, y):
                X_train, X_test = X[train_idx], X[test_idx]
                y_train, y_test = y[train_idx], y[test_idx]
                
                self.model.fit(X_train, y_train)
                y_pred = self.model.predict(X_test)
                
                cv_scores.append({
                    'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                    'mae': mean_absolute_error(y_test, y_pred),
                    'r2': r2_score(y_test, y_pred)
                })
            
            self.spatial_cv_scores = cv_scores
        
        # Train on full data
        self.model.fit(X, y)
        
        # Feature importance
        self.feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Predictions
        y_pred = self.model.predict(X)
        
        return {
            'model_type': model_type,
            'n_samples': len(y),
            'n_features': len(feature_columns),
            'rmse': np.sqrt(mean_squared_error(y, y_pred)),
            'mae': mean_absolute_error(y, y_pred),
            'r2': r2_score(y, y_pred),
            'spatial_cv_scores': self.spatial_cv_scores,
            'feature_importance': self.feature_importance.to_dict()
        }
    
    def predict(self, new_gdf: gpd.GeoDataFrame) -> np.ndarray:
        """
        Make predictions on new data
        
        Args:
            new_gdf: New GeoDataFrame with same features
        
        Returns:
            Predictions
        """
        if self.model is None:
            raise ValueError("Model not trained")
        
        feature_columns = self.feature_importance['feature'].tolist()
        X = new_gdf[feature_columns].fillna(0).values
        
        return self.model.predict(X)
    
    def predict_spatial_interpolation(
        self,
        grid_resolution_km: float = 10
    ) -> gpd.GeoDataFrame:
        """
        Create spatial interpolation prediction grid
        
        Args:
            grid_resolution_km: Grid resolution in km
        
        Returns:
            GeoDataFrame with interpolated predictions
        """
        # Get bounds
        bounds = self.gdf.total_bounds
        
        # Create grid
        resolution_deg = grid_resolution_km / 111
        x_grid = np.arange(bounds[0], bounds[2], resolution_deg)
        y_grid = np.arange(bounds[1], bounds[3], resolution_deg)
        xx, yy = np.meshgrid(x_grid, y_grid)
        
        # Create grid GeoDataFrame
        from shapely.geometry import Point
        grid_points = [Point(x, y) for x, y in zip(xx.ravel(), yy.ravel())]
        grid_gdf = gpd.GeoDataFrame(geometry=grid_points, crs=self.gdf.crs)
        
        # Interpolate features to grid
        from scipy.interpolate import Rbf
        
        centroids = self.gdf.geometry.centroid
        x = centroids.x.values
        y = centroids.y.values
        
        feature_columns = self.feature_importance['feature'].tolist()
        for feature in feature_columns:
            if feature in self.gdf.columns:
                z = self.gdf[feature].values
                rbf = Rbf(x, y, z, function='linear')
                grid_gdf[feature] = rbf(
                    grid_gdf.geometry.x.values,
                    grid_gdf.geometry.y.values
                )
            else:
                grid_gdf[feature] = 0
        
        # Predict
        grid_gdf['predicted_risk'] = self.predict(grid_gdf)
        
        return grid_gdf
```

### 4.6 Interactive Map Layers

#### 4.6.1 Layer Management System

```python
# File: src/geospatial/layer_manager.py
"""
Interactive map layer management system
"""
import folium
from folium import plugins
import geopandas as gpd
import pandas as pd
from typing import Dict, List, Optional, Callable, Any
import json

class LayerManager:
    """
    Manage interactive map layers for ResilienceAI dashboard
    """
    
    def __init__(self, center: List[float] = [37.8, -92.5], zoom: int = 6):
        self.center = center
        self.zoom = zoom
        self.layers: Dict[str, Any] = {}
        self.map = None
    
    def create_base_map(
        self,
        base_tiles: str = 'cartodbpositron'
    ) -> folium.Map:
        """
        Create base map with multiple tile options
        """
        self.map = folium.Map(
            location=self.center,
            zoom_start=self.zoom,
            tiles=base_tiles
        )
        
        # Add tile layer options
        folium.TileLayer(
            'OpenStreetMap',
            name='OpenStreetMap'
        ).add_to(self.map)
        
        folium.TileLayer(
            'CartoDB dark_matter',
            name='Dark Matter'
        ).add_to(self.map)
        
        folium.TileLayer(
            'CartoDB positron',
            name='Light',
            default=True
        ).add_to(self.map)
        
        # Add satellite imagery
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite',
            overlay=False,
            control=True
        ).add_to(self.map)
        
        return self.map
    
    def add_choropleth_layer(
        self,
        gdf: gpd.GeoDataFrame,
        value_column: str,
        layer_name: str,
        color_scheme: str = 'YlOrRd',
        bins: int = 5,
        legend_name: str = None
    ):
        """
        Add choropleth layer
        """
        if legend_name is None:
            legend_name = value_column.replace('_', ' ').title()
        
        # Create choropleth
        choropleth = folium.Choropleth(
            geo_data=gdf.__geo_interface__,
            data=gdf,
            columns=['GEOID', value_column],
            key_on='feature.properties.GEOID',
            fill_color=color_scheme,
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=legend_name,
            bins=bins,
            highlight=True,
            name=layer_name
        )
        
        # Add tooltips
        choropleth.geojson.add_child(
            folium.features.GeoJsonTooltip(
                fields=['NAME', value_column],
                aliases=['County:', legend_name + ':'],
                localize=True
            )
        )
        
        choropleth.add_to(self.map)
        self.layers[layer_name] = choropleth
    
    def add_heatmap_layer(
        self,
        df: pd.DataFrame,
        lat_column: str = 'latitude',
        lon_column: str = 'longitude',
        value_column: str = 'risk_score',
        layer_name: str = 'Heatmap',
        radius: int = 15,
        blur: int = 25
    ):
        """
        Add heatmap layer
        """
        heat_data = df[[lat_column, lon_column, value_column]].dropna().values.tolist()
        
        heatmap = plugins.HeatMap(
            heat_data,
            radius=radius,
            blur=blur,
            max_zoom=10,
            name=layer_name
        )
        
        heatmap.add_to(self.map)
        self.layers[layer_name] = heatmap
    
    def add_marker_cluster_layer(
        self,
        df: pd.DataFrame,
        lat_column: str = 'latitude',
        lon_column: str = 'longitude',
        popup_columns: List[str] = None,
        layer_name: str = 'Facilities',
        icon_color: str = 'red'
    ):
        """
        Add marker cluster layer for facilities
        """
        marker_cluster = plugins.MarkerCluster(name=layer_name)
        
        for _, row in df.iterrows():
            popup_html = '<b>{}</b><br/>'.format(row.get('name', 'Facility'))
            
            if popup_columns:
                for col in popup_columns:
                    if col in row:
                        popup_html += '{}: {}<br/>'.format(
                            col.replace('_', ' ').title(),
                            row[col]
                        )
            
            folium.Marker(
                location=[row[lat_column], row[lon_column]],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=icon_color, icon='info-sign')
            ).add_to(marker_cluster)
        
        marker_cluster.add_to(self.map)
        self.layers[layer_name] = marker_cluster
    
    def add_wms_layer(
        self,
        url: str,
        layer_name: str,
        display_name: str,
        transparent: bool = True,
        opacity: float = 0.7
    ):
        """
        Add WMS layer (e.g., weather radar)
        """
        wms = folium.WmsTileLayer(
            url=url,
            layers=layer_name,
            fmt='image/png',
            transparent=transparent,
            opacity=opacity,
            name=display_name
        )
        
        wms.add_to(self.map)
        self.layers[display_name] = wms
    
    def add_weather_radar_layer(self):
        """
        Add NOAA weather radar overlay
        """
        self.add_wms_layer(
            url='https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi',
            layer_name='nexrad-n0r-900913',
            display_name='Weather Radar',
            transparent=True,
            opacity=0.6
        )
    
    def add_draw_control(self):
        """
        Add drawing control for user annotations
        """
        draw = plugins.Draw(
            export=True,
            filename='user_drawn_features.geojson',
            position='topleft',
            draw_options={
                'polyline': True,
                'polygon': True,
                'circle': True,
                'marker': True,
                'circlemarker': False
            },
            edit_options={'edit': True}
        )
        
        draw.add_to(self.map)
    
    def add_measure_control(self):
        """
        Add measurement control
        """
        measure = plugins.MeasureControl(
            position='topleft',
            primary_length_unit='kilometers',
            secondary_length_unit='miles',
            primary_area_unit='hectares',
            secondary_area_unit='acres'
        )
        
        measure.add_to(self.map)
    
    def add_mini_map(self):
        """
        Add overview mini map
        """
        minimap = plugins.MiniMap()
        minimap.add_to(self.map)
    
    def add_search_control(self, gdf: gpd.GeoDataFrame, search_column: str = 'NAME'):
        """
        Add search control for finding locations
        """
        search = plugins.Search(
            layer=folium.GeoJson(gdf.__geo_interface__),
            search_label=search_column,
            position='topright',
            collapsed=False
        )
        
        search.add_to(self.map)
    
    def add_fullscreen_control(self):
        """
        Add fullscreen control
        """
        plugins.Fullscreen(position='topright').add_to(self.map)
    
    def add_layer_control(self):
        """
        Add layer control for toggling layers
        """
        folium.LayerControl().add_to(self.map)
    
    def save(self, filepath: str):
        """
        Save map to HTML file
        """
        self.map.save(filepath)
    
    def get_html(self) -> str:
        """
        Get map HTML representation
        """
        return self.map._repr_html_()
```

### 4.7 Mobile Geospatial Interface

#### 4.7.1 Progressive Web App (PWA) Components

```python
# File: src/geospatial/mobile_interface.py
"""
Mobile-optimized geospatial interface components
"""
import streamlit as st
from streamlit_folium import st_folium
import folium
from typing import Dict, List, Optional
import json

class MobileGeospatialInterface:
    """
    Mobile-optimized geospatial interface for field use
    """
    
    def __init__(self):
        self.is_mobile = self._detect_mobile()
    
    def _detect_mobile(self) -> bool:
        """Detect if user is on mobile device"""
        # Streamlit doesn't provide direct user agent access
        # This is a simplified check
        return st.session_state.get('viewport_width', 1024) < 768
    
    def render_mobile_map(
        self,
        center: List[float] = [37.8, -92.5],
        zoom: int = 6,
        layers: Dict = None
    ):
        """
        Render mobile-optimized map
        """
        # Create compact map
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles='CartoDB positron',
            control_scale=True
        )
        
        # Add geolocation button
        plugins.LocateControl().add_to(m)
        
        # Display map
        st_folium(m, width=350, height=500, returned_objects=[])
    
    def render_offline_sync_panel(self):
        """
        Render offline data synchronization panel
        """
        st.subheader("📱 Offline Sync")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Cached Maps", "5 regions")
            st.metric("Last Sync", "2 hours ago")
        
        with col2:
            if st.button("🔄 Sync Now"):
                st.success("Sync initiated!")
            
            if st.button("💾 Download Offline"):
                st.info("Select regions to download")
    
    def render_quick_actions(self):
        """
        Render quick action buttons for mobile
        """
        st.subheader("Quick Actions")
        
        cols = st.columns(4)
        
        with cols[0]:
            if st.button("📍 My Location"):
                st.session_state['center_map'] = True
        
        with cols[1]:
            if st.button("🔍 Search"):
                st.session_state['show_search'] = True
        
        with cols[2]:
            if st.button("📸 Report"):
                st.session_state['show_report'] = True
        
        with cols[3]:
            if st.button("🚨 Alert"):
                st.session_state['show_alert'] = True
    
    def render_gps_tracking(self):
        """
        Render GPS tracking component
        """
        st.subheader("GPS Tracking")
        
        # Get GPS coordinates (would use browser geolocation in production)
        gps_data = st.session_state.get('gps_data', [])
        
        if gps_data:
            df = pd.DataFrame(gps_data, columns=['lat', 'lon', 'timestamp'])
            st.map(df)
        else:
            st.info("Enable GPS to start tracking")
            if st.button("Start Tracking"):
                st.session_state['tracking'] = True
```

### 4.8 AR/VR Geospatial Exploration

#### 4.8.1 AR Visualization Components

```python
# File: src/geospatial/ar_vr_integration.py
"""
AR/VR geospatial exploration components
"""
import json
from typing import Dict, List, Optional, Tuple
import numpy as np

class ARGeospatialExporter:
    """
    Export geospatial data for AR/VR applications
    """
    
    def __init__(self, gdf: gpd.GeoDataFrame):
        self.gdf = gdf
    
    def export_to_geo_ar(
        self,
        output_path: str,
        anchor_point: Tuple[float, float],
        scale: float = 1.0
    ):
        """
        Export to GeoAR format (for AR.js, 8th Wall)
        
        Args:
            output_path: Output file path
            anchor_point: (lat, lon) anchor for AR positioning
            scale: Scale factor for AR display
        """
        features = []
        
        for _, row in self.gdf.iterrows():
            # Calculate relative position from anchor
            centroid = row.geometry.centroid
            rel_lat = (centroid.y - anchor_point[0]) * 111000  # meters
            rel_lon = (centroid.x - anchor_point[1]) * 111000 * np.cos(np.radians(anchor_point[0]))
            
            feature = {
                'type': 'Feature',
                'properties': {
                    'name': row.get('county_name', 'Unknown'),
                    'risk_score': row.get('risk_score', 0),
                    'risk_level': row.get('risk_level', 'Low'),
                    'ar_position': {
                        'x': rel_lon * scale,
                        'y': row.get('risk_score', 0) * 10,  # Height based on risk
                        'z': -rel_lat * scale  # Negative for AR coordinate system
                    }
                },
                'geometry': row.geometry.__geo_interface__
            }
            
            features.append(feature)
        
        geo_ar = {
            'type': 'FeatureCollection',
            'anchor': {
                'latitude': anchor_point[0],
                'longitude': anchor_point[1]
            },
            'scale': scale,
            'features': features
        }
        
        with open(output_path, 'w') as f:
            json.dump(geo_ar, f, indent=2)
    
    def export_to_three_js(
        self,
        output_path: str,
        extrusion_column: str = 'risk_score'
    ):
        """
        Export to Three.js compatible format
        
        Args:
            output_path: Output file path
            extrusion_column: Column for extrusion height
        """
        geometries = []
        
        for _, row in self.gdf.iterrows():
            geom = row.geometry
            
            if geom.geom_type == 'Polygon':
                coords = list(geom.exterior.coords)
                
                # Convert to Three.js format
                vertices = []
                for lon, lat in coords:
                    vertices.extend([lon, lat, 0])
                
                geometries.append({
                    'type': 'extruded_polygon',
                    'vertices': vertices,
                    'height': row.get(extrusion_column, 0) * 1000,
                    'color': self._risk_to_color(row.get('risk_level', 'Low')),
                    'properties': {
                        'name': row.get('county_name', 'Unknown'),
                        'risk_score': row.get('risk_score', 0)
                    }
                })
        
        with open(output_path, 'w') as f:
            json.dump({'geometries': geometries}, f, indent=2)
    
    def _risk_to_color(self, risk_level: str) -> str:
        """Convert risk level to hex color"""
        colors = {
            'Low': '#2ecc71',
            'Medium': '#f1c40f',
            'High': '#e67e22',
            'Critical': '#e74c3c'
        }
        return colors.get(risk_level, '#95a5a6')
    
    def export_to_a_frame(
        self,
        output_path: str,
        center: Tuple[float, float]
    ):
        """
        Export to A-Frame HTML for WebVR
        
        Args:
            output_path: Output HTML file path
            center: Center coordinates for scene
        """
        html_template = '''<!DOCTYPE html>
<html>
<head>
    <script src="https://aframe.io/releases/1.4.0/aframe.min.js"></script>
    <script src="https://unpkg.com/aframe-geojson-component/dist/aframe-geojson-component.min.js"></script>
</head>
<body>
    <a-scene>
        <a-sky color="#ECECEC"></a-sky>
        
        <!-- Camera -->
        <a-entity position="0 50 100">
            <a-camera look-controls wasd-controls></a-camera>
        </a-entity>
        
        <!-- Lighting -->
        <a-light type="ambient" color="#BBB"></a-light>
        <a-light type="directional" color="#FFF" intensity="0.6" position="-0.5 1 1"></a-light>
        
        <!-- Terrain base -->
        <a-plane position="0 0 0" rotation="-90 0 0" width="200" height="200" color="#7BC8A4"></a-plane>
        
        <!-- Risk Extrusions -->
        {extrusions}
        
    </a-scene>
</body>
</html>'''
        
        extrusions = []
        for _, row in self.gdf.iterrows():
            centroid = row.geometry.centroid
            rel_x = (centroid.x - center[1]) * 1000
            rel_z = -(centroid.y - center[0]) * 1000
            height = row.get('risk_score', 0) * 10
            color = self._risk_to_color(row.get('risk_level', 'Low'))
            
            extrusion = f'''
        <a-box position="{rel_x} {height/2} {rel_z}" 
               width="5" height="{height}" depth="5" 
               color="{color}">
            <a-text value="{row.get('county_name', 'Unknown')}" 
                    position="0 {height/2 + 2} 0" 
                    align="center"></a-text>
        </a-box>'''
            
            extrusions.append(extrusion)
        
        html = html_template.format(extrusions='\n'.join(extrusions))
        
        with open(output_path, 'w') as f:
            f.write(html)
```

---

## 5. Implementation Roadmap

### 5.1 Phase 1: Core Enhancements (Weeks 1-2)

| Task | File | Priority | Effort |
|------|------|----------|--------|
| PyDeck 3D visualizations | `src/geospatial/visualizations_3d.py` | High | 3 days |
| Advanced GEE integration | `src/geospatial/gee_advanced.py` | High | 4 days |
| PySAL spatial statistics | `src/geospatial/spatial_analysis_advanced.py` | High | 3 days |
| Layer management system | `src/geospatial/layer_manager.py` | Medium | 2 days |

### 5.2 Phase 2: Network & ML (Weeks 3-4)

| Task | File | Priority | Effort |
|------|------|----------|--------|
| Multi-modal network analysis | `src/geospatial/network_analysis_advanced.py` | High | 4 days |
| Spatial ML models | `src/geospatial/spatial_ml.py` | High | 4 days |
| Cascade failure simulation | Extend network analysis | Medium | 2 days |
| Hotspot trend analysis | Extend spatial stats | Medium | 2 days |

### 5.3 Phase 3: Mobile & AR/VR (Weeks 5-6)

| Task | File | Priority | Effort |
|------|------|----------|--------|
| Mobile interface components | `src/geospatial/mobile_interface.py` | Medium | 3 days |
| PWA offline capabilities | Service workers | Medium | 2 days |
| AR export formats | `src/geospatial/ar_vr_integration.py` | Low | 3 days |
| WebVR exploration | A-Frame integration | Low | 2 days |

### 5.4 Phase 4: Integration & Testing (Week 7)

| Task | Description | Effort |
|------|-------------|--------|
| Dashboard integration | Add new components to Streamlit | 3 days |
| Performance optimization | Caching, lazy loading | 2 days |
| End-to-end testing | Unit and integration tests | 2 days |
| Documentation | API docs, user guides | 2 days |

---

## 6. Technology Stack

### 6.1 Core Dependencies

```txt
# Existing (from requirements.txt)
geopandas>=0.14.0
shapely>=2.0.0
earthengine-api>=1.4.0

# New additions
pydeck>=0.8.0
pysal>=23.0
libpysal>=4.7
esda>=2.5
splot>=1.1
osmnx>=1.6
xarray>=2023.0
rioxarray>=0.15
rasterio>=1.3
geemap>=0.30
```

### 6.2 Optional Dependencies

```txt
# 3D visualization
pydeck>=0.8.0
cesiumpy>=0.3

# Advanced spatial analysis
igraph>=0.10
pandana>=0.6

# AR/VR
# (Browser-based, no Python deps)

# Mobile
# (PWA via service workers)
```

---

## 7. Integration Points

### 7.1 Dashboard Integration

```python
# In app/dashboard.py - Add new geospatial tab

def render_advanced_geospatial_tab(df: pd.DataFrame, gdf: gpd.GeoDataFrame):
    """Render advanced geospatial analysis tab"""
    st.header("🗺️ Advanced Geospatial Analysis")
    
    # Layer selection
    layer_tabs = st.tabs([
        "3D Visualization",
        "Satellite Imagery",
        "Hotspot Analysis",
        "Network Analysis",
        "Prediction Map"
    ])
    
    with layer_tabs[0]:
        render_3d_visualization_tab(gdf)
    
    with layer_tabs[1]:
        render_satellite_imagery_tab(gdf)
    
    with layer_tabs[2]:
        render_hotspot_analysis_tab(gdf)
    
    with layer_tabs[3]:
        render_network_analysis_tab(gdf)
    
    with layer_tabs[4]:
        render_prediction_map_tab(gdf)
```

### 7.2 Agent Integration

```python
# In src/agent.py - Add geospatial tools

GEOSPATIAL_TOOLS = [
    {
        "name": "analyze_spatial_autocorrelation",
        "description": "Analyze spatial autocorrelation using Moran's I",
        "parameters": {
            "variable": "Variable to analyze (e.g., risk_score)",
            "county_fips": "Optional: Focus on specific county"
        }
    },
    {
        "name": "detect_hotspots",
        "description": "Detect vulnerability hotspots using Getis-Ord Gi*",
        "parameters": {
            "variable": "Variable for hotspot detection",
            "significance_level": "P-value threshold (default: 0.05)"
        }
    },
    {
        "name": "get_satellite_imagery",
        "description": "Retrieve satellite imagery from GEE",
        "parameters": {
            "dataset": "Dataset name (sentinel2, landsat8, etc.)",
            "date_range": "Date range for imagery",
            "county_fips": "County to focus on"
        }
    },
    {
        "name": "analyze_infrastructure_network",
        "description": "Analyze critical infrastructure network",
        "parameters": {
            "facility_types": "List of facility types to include",
            "analysis_type": "centrality, cascade, or resilience"
        }
    }
]
```

---

## 8. File Structure

```
resilience_ai/
├── src/
│   ├── geospatial/                    # NEW: Advanced geospatial module
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── requirements.txt
│   │   ├── pipeline.py               # Main geospatial pipeline
│   │   ├── gee_integration.py        # GEE integration
│   │   ├── gee_advanced.py           # NEW: Advanced GEE
│   │   ├── naip.py                   # NAIP imagery
│   │   ├── usgs_3dep.py              # USGS 3DEP DEM
│   │   ├── visualizations_3d.py      # NEW: 3D visualizations
│   │   ├── spatial_analysis_advanced.py  # NEW: Advanced spatial stats
│   │   ├── network_analysis_advanced.py  # NEW: Network analysis
│   │   ├── spatial_ml.py             # NEW: Spatial ML
│   │   ├── layer_manager.py          # NEW: Layer management
│   │   ├── mobile_interface.py       # NEW: Mobile interface
│   │   ├── ar_vr_integration.py      # NEW: AR/VR export
│   │   └── cesium_integration.py     # NEW: Cesium 3D
│   ├──
│   ├── geo_visualizations.py         # EXISTING: Basic visualizations
│   ├── gee_client.py                 # EXISTING: Basic GEE
│   ├── geojson_export.py             # EXISTING: GeoJSON export
│   ├── network_analysis.py           # EXISTING: Basic network
│   └── spatial_stats.py              # EXISTING: Basic spatial stats
├── app/
│   └── dashboard.py                  # UPDATE: Add geospatial tab
├── data/
│   └── gee_cache/                    # GEE data cache
└── tests/
    └── geospatial/                   # NEW: Geospatial tests
```

---

## 9. Performance Considerations

### 9.1 Caching Strategy

```python
# File: src/geospatial/cache_manager.py

import streamlit as st
from functools import lru_cache
import hashlib
import json

class GeospatialCache:
    """Cache manager for geospatial operations"""
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def get_gee_image(dataset: str, region: str, date: str):
        """Cache GEE image requests"""
        # Implementation
        pass
    
    @staticmethod
    @st.cache_data(ttl=86400)
    def get_spatial_weights(gdf_hash: str, weight_type: str):
        """Cache spatial weights matrices"""
        # Implementation
        pass
    
    @staticmethod
    def hash_gdf(gdf: gpd.GeoDataFrame) -> str:
        """Create hash of GeoDataFrame for caching"""
        data = gdf.geometry.wkb.tobytes()
        return hashlib.md5(data).hexdigest()
```

### 9.2 Lazy Loading

```python
# Implement lazy loading for heavy components

class LazyGeoComponent:
    """Lazy loading for geospatial components"""
    
    def __init__(self):
        self._gee_client = None
        self._spatial_analyzer = None
    
    @property
    def gee_client(self):
        if self._gee_client is None:
            from .gee_advanced import AdvancedGEEClient
            self._gee_client = AdvancedGEEClient()
        return self._gee_client
```

---

## 10. Conclusion

This comprehensive geospatial enhancement plan for ResilienceAI provides:

1. **3D Visualizations**: PyDeck, Cesium, and Three.js integration for immersive geospatial exploration
2. **Advanced GEE**: Real-time satellite imagery, change detection, and multi-sensor fusion
3. **Spatial Statistics**: PySAL integration for Moran's I, Getis-Ord Gi*, and emerging hotspot analysis
4. **Network Analysis**: Multi-modal infrastructure networks with cascade failure simulation
5. **Spatial ML**: Geospatial prediction models with spatial cross-validation
6. **Interactive Layers**: Folium-based layer management with weather overlays
7. **Mobile Interface**: PWA components for field use
8. **AR/VR Export**: WebAR and WebVR compatibility

The implementation follows a phased approach, prioritizing high-impact features while maintaining backward compatibility with existing code. The modular design allows for incremental adoption and future extensibility.

---

## Appendix A: Code Examples

### A.1 Complete 3D Choropleth Example

```python
import geopandas as gpd
import pandas as pd
from src.geospatial.visualizations_3d import Deck3DVisualizer

# Load data
gdf = gpd.read_file('data/counties.geojson')
df = pd.read_csv('data/county_risk.csv')
gdf = gdf.merge(df, on='GEOID')

# Create 3D visualization
viz = Deck3DVisualizer(gdf)
deck = viz.create_extruded_choropleth(
    geojson_path='data/counties.geojson',
    value_column='risk_score',
    elevation_column='total_population',
    color_column='risk_level'
)

# Display in Streamlit
import streamlit as st
st.pydeck_chart(deck)
```

### A.2 Complete Hotspot Analysis Example

```python
from src.geospatial.spatial_analysis_advanced import AdvancedSpatialAnalyzer

# Analyze hotspots
analyzer = AdvancedSpatialAnalyzer(gdf)

# Moran's I
moran_results = analyzer.morans_i_analysis('risk_score')
print(f"Moran's I: {moran_results['global_morans_i']:.3f}")
print(f"Interpretation: {moran_results['interpretation']}")

# Getis-Ord Gi*
gi_results = analyzer.getis_ord_gi_star('risk_score')
hotspots = gdf[gi_results['hotspots']]
print(f"Found {len(hotspots)} hotspots")

# Export with classifications
gdf.to_file('data/hotspot_analysis.geojson')
```

### A.3 Complete Network Analysis Example

```python
from src.geospatial.network_analysis_advanced import MultiModalNetworkAnalyzer

# Build network
analyzer = MultiModalNetworkAnalyzer()
G = analyzer.build_facility_network(facilities_df)

# Find critical nodes
critical = analyzer.find_critical_nodes(top_n=10)
for node in critical:
    print(f"{node['name']}: {node['criticality_score']:.3f}")

# Simulate cascade
cascade = analyzer.simulate_cascade_failure(
    initial_failures=['facility_001'],
    cascade_threshold=0.7
)
print(f"Cascade affected {cascade['total_failed']} facilities")
```

---

*Document Version: 1.0*
*Last Updated: February 2026*
*Author: Geospatial Analysis Team*
