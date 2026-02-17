# High-Resolution Geospatial Data Sources for Sub-Kilometer Analysis

## Executive Summary

This document catalogs advanced open-source geospatial data sources capable of supporting analysis at **sub-kilometer resolution** (30m, 10m, or better). The focus is on data sources relevant to **climate risk assessment**, **infrastructure analysis**, and **vulnerability assessment**.

---

## 1. Google Earth Engine (GEE) High-Resolution Datasets

### 1.1 Landsat Collection (30m Resolution)
| Dataset | Resolution | Temporal Coverage | Key Features |
|---------|------------|-------------------|--------------|
| **Landsat 8/9 OLI** | 30m multispectral, 15m panchromatic | 2013-present | 11 spectral bands, thermal infrared |
| **Landsat 7 ETM+** | 30m | 1999-present | SLC-off gaps post-2003 |
| **Landsat 4-5 TM** | 30m | 1982-2012 | Historical archive for change detection |
| **Landsat Collection 2 Level 2** | 30m | 1972-present | Surface reflectance, atmospherically corrected |

**Access:** `ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')`

### 1.2 Sentinel-2 (10m Resolution)
| Dataset | Resolution | Temporal Coverage | Key Features |
|---------|------------|-------------------|--------------|
| **Sentinel-2 MSI Level-2A** | 10m (RGB+NIR), 20m (red edge), 60m (atmospheric) | 2015-present | 13 spectral bands, 5-day revisit with twin satellites |
| **Sentinel-2 Cloud Probability** | 10m | 2015-present | ML-based cloud masking |
| **Harmonized Sentinel-2** | 10m | 2015-present | Consistent radiometry across missions |

**Access:** `ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')`

### 1.3 MODIS (250m-1km - Coarse but Frequent)
| Dataset | Resolution | Temporal Coverage | Use Case |
|---------|------------|-------------------|----------|
| **MOD09GQ** | 250m | 2000-present | Daily surface reflectance |
| **MOD13Q1** | 250m | 2000-present | 16-day NDVI/EVI |
| **MCD43A4** | 500m | 2000-present | Daily BRDF-adjusted reflectance |

### 1.4 Other High-Resolution GEE Datasets
| Dataset | Resolution | Coverage | Description |
|---------|------------|----------|-------------|
| **USGS 3DEP 1m** | 1m | USA | LiDAR-derived DEM |
| **USGS 3DEP 10m** | 10m | USA | Seamless national DEM |
| **NASA SRTM** | 30m | Global (60°N-56°S) | Shuttle Radar Topography Mission |
| **NASADEM** | 30m | Global | Improved SRTM with ASTER GDEM |
| **ALOS AW3D30** | 30m | Global | JAXA global DSM |
| **Copernicus DEM GLO-30** | 30m | Global | ESA global digital elevation model |
| **Dynamic World** | 10m | Global | Near real-time LULC (9 classes) |
| **ESA WorldCover** | 10m | Global | Annual land cover (11 classes) |
| **JRC Global Surface Water** | 30m | Global | 1984-2021 surface water history |
| **Hansen Global Forest Change** | 30m | Global | 2000-2023 forest loss/gain |

---

## 2. Sub-100m Resolution Sources

### 2.1 30m Resolution (Global Coverage)
| Source | Type | Coverage | Access |
|--------|------|----------|--------|
| **Landsat 8/9** | Optical | Global | Free (USGS/GEE) |
| **Sentinel-1 SAR** | Radar | Global | Free (ESA/GEE) |
| **NASA SRTM** | DEM | 60°N-56°S | Free (USGS/GEE) |
| **Copernicus DEM** | DEM | Global | Free (ESA) |
| **ALOS AW3D30** | DEM | Global | Free (JAXA) |
| **Hansen Forest Change** | Thematic | Global | Free (UMD/GEE) |
| **GlobCover** | Land Cover | Global | Free (ESA) |
| **MCD12Q1** | Land Cover | Global | Free (NASA) |

### 2.2 10m Resolution (Global/Regional)
| Source | Type | Coverage | Access |
|--------|------|----------|--------|
| **Sentinel-2** | Optical | Global | Free (ESA/GEE) |
| **Dynamic World** | LULC | Global | Free (Google/GEE) |
| **ESA WorldCover** | Land Cover | Global | Free (ESA) |
| **ESA WorldCereal** | Crop Maps | Global | Free (ESA) |
| **JRC Global Forest Cover** | Forest | Global | Free (EC JRC) |

### 2.3 5m Resolution
| Source | Type | Coverage | Access |
|--------|------|----------|--------|
| **Australia 5m DEM** | DEM | Australia | Free (Geoscience Australia) |
| **PALSAR-2 ScanSAR** | Radar | Global | Free (JAXA) |
| **ArcticDEM** | DEM | Arctic (>60°N) | Free (PGC) |

### 2.4 1m Resolution (Regional)
| Source | Type | Coverage | Access |
|--------|------|----------|--------|
| **USGS 3DEP 1m** | DEM | USA (partial) | Free (USGS) |
| **USDA NAIP** | Aerial | USA (3-year cycle) | Free (USDA) |
| **England 1m DTM/DSM** | DEM | England | Free (Environment Agency) |
| **Netherlands AHN** | DEM | Netherlands | Free (Dutch Gov) |
| **France RGE ALTI 1m** | DEM | France | Free (IGN) |
| **Switzerland SWISSIMAGE** | Aerial | Switzerland | Free (Swisstopo) |

### 2.5 Sub-Meter Resolution (Limited Coverage)
| Source | Resolution | Coverage | Access |
|--------|------------|----------|--------|
| **USGS 3DEP 1m** | 1m | USA (growing) | Free |
| **USDA NAIP** | 0.3-0.6m | USA | Free |
| **Planet NICFI** | 4.77m | Tropical forests | Free (non-commercial) |
| **Maxar Open Data** | 0.3-0.5m | Disaster areas | Free (limited) |
| **Open Buildings** | Variable | Global | Free (Microsoft) |

---

## 3. LiDAR and DEM Data

### 3.1 USGS 3DEP (USA)
| Product | Resolution | Coverage | Description |
|---------|------------|----------|-------------|
| **3DEP 1m** | 1m | Project-based | Highest resolution standard DEM |
| **3DEP 1/3 arc-sec** | ~10m | CONUS, AK, HI, territories | Seamless national coverage |
| **3DEP 1 arc-sec** | ~30m | CONUS + AK | Lower resolution seamless |
| **3DEP 5m** | 5m | Alaska only | IfSAR-derived for AK |
| **LiDAR Point Cloud** | Variable | Project-based | Raw point cloud data |

**Access:** 
- GEE: `ee.ImageCollection('USGS/3DEP/1m')`
- USGS National Map: https://apps.nationalmap.gov/downloader/
- OpenTopography: https://portal.opentopography.org/

### 3.2 Global DEM Sources
| Dataset | Resolution | Coverage | Vertical Accuracy | Source |
|---------|------------|----------|-------------------|--------|
| **Copernicus DEM GLO-30** | 30m | Global | ~4m | ESA/WorldDEM |
| **Copernicus DEM GLO-90** | 90m | Global | ~4m | ESA/WorldDEM |
| **NASA SRTM** | 30m (1 arc-sec) | 60°N-56°S | ~16m | NASA |
| **NASADEM** | 30m | Global | ~10m | NASA (improved SRTM) |
| **ALOS AW3D30** | 30m | Global | ~5m | JAXA |
| **MERIT DEM** | 90m | Global | ~2-5m | Improved SRTM/AW3D |
| **TanDEM-X** | 12m, 30m, 90m | Global | ~2-10m | DLR/Airbus (commercial) |
| **ArcticDEM** | 2m, 8m | Arctic (>60°N) | ~2m | PGC |
| **REMA** | 2m, 8m | Antarctica | ~2m | PGC |

### 3.3 OpenTopography
- **Coverage:** Global (aggregated datasets)
- **Resolution:** Variable (1m to 30m+)
- **Access:** https://portal.opentopography.org/
- **Features:** High-resolution topography data, point clouds, DEMs
- **Academic Use:** Free for research and education

---

## 4. Very High-Resolution Satellite

### 4.1 Planet Labs NICFI (Tropical Forests)
| Aspect | Details |
|--------|---------|
| **Resolution** | 4.77m (visual), ~5m effective |
| **Coverage** | Tropical regions (23.5°N to 23.5°S) |
| **Temporal** | Monthly and bi-annual mosaics (2015-2025) |
| **Access** | Free for non-commercial use |
| **Registration** | Required via Planet |
| **GEE Access** | `projects/planet-nicfi/assets/basemaps/...` |

**Use Cases:** Deforestation monitoring, REDD+ MRV, land use change

### 4.2 Maxar (Sample/Open Data)
| Aspect | Details |
|--------|---------|
| **Resolution** | 30-50cm (panchromatic), 1.2m (multispectral) |
| **Coverage** | Global |
| **Open Data** | Disaster response, select research |
| **Commercial** | Full archive available for purchase |

**Open Data Program:** https://www.maxar.com/open-data

### 4.3 Sentinel-2 (10m) - Free Global Workhorse
- **Revisit:** 5 days (2 satellites)
- **Bands:** 13 spectral bands
- **Best For:** Vegetation monitoring, agriculture, land cover
- **Limitation:** Cloud cover in tropical regions

### 4.4 SkySat (Planet)
| Aspect | Details |
|--------|---------|
| **Resolution** | 0.8m (panchromatic), 1m (multispectral) |
| **Coverage** | Tasked (on-demand) |
| **Access** | Commercial (limited open samples) |
| **Archive** | Some public samples via GEE |

---

## 5. Aerial Imagery

### 5.1 USDA NAIP (USA)
| Aspect | Details |
|--------|---------|
| **Resolution** | 0.3m (coastal), 0.6m (standard), 1m (historical) |
| **Coverage** | CONUS + territories (3-year cycle) |
| **Spectral** | 4-band (RGB + NIR) |
| **Temporal** | Growing season (leaf-on) |
| **Access** | Free |
| **Formats** | GeoTIFF, JPEG2000 |

**Access Points:**
- USDA Geospatial Data Gateway
- USGS EarthExplorer
- GEE: `USDA/NAIP/DOQQ`

### 5.2 State/Local Open Data Portals (USA Examples)
| State/Region | Resolution | Coverage | Portal |
|--------------|------------|----------|--------|
| **California** | 1m | Statewide | CA Spatial Data Library |
| **New York** | 1ft-2ft | Statewide | NY State GIS Clearinghouse |
| **Texas** | 1m | Statewide | TNRIS |
| **Florida** | 1ft | Statewide | FDEP |

### 5.3 International Aerial Programs
| Country | Program | Resolution | Access |
|---------|---------|------------|--------|
| **UK** | Environment Agency | 25cm | Free (Open Government) |
| **Netherlands** | PDOK | 25cm | Free |
| **Switzerland** | SWISSIMAGE | 10cm | Free |
| **France** | IGN Orthophoto | 20cm | Free |
| **Germany** | DOP | 20cm | Free (state-dependent) |
| **Australia** | NationalMap | Variable | Free |

---

## 6. Urban Data

### 6.1 Microsoft Building Footprints
| Aspect | Details |
|--------|---------|
| **Total Buildings** | 1.4 billion (as of 2025) |
| **Coverage** | Global |
| **Format** | GeoJSON (line-delimited) |
| **License** | ODbL (Open Database License) |
| **Height Data** | Available for ~174M buildings |
| **Confidence Scores** | Included |

**Access:** https://github.com/microsoft/GlobalMLBuildingFootprints

**Coverage by Region:**
- North America: Comprehensive
- Europe: Comprehensive
- India: 110M+ buildings
- Brazil: 43M+ buildings
- Africa: Growing coverage

### 6.2 Google Open Buildings
| Aspect | Details |
|--------|---------|
| **Total Buildings** | 1.8 billion |
| **Coverage** | Africa, South Asia, Latin America, Caribbean |
| **Resolution** | Variable (derived from high-res imagery) |
| **Format** | GeoJSON, CSV |
| **License** | CC-BY |

**Access:** https://sites.research.google/open-buildings/

### 6.3 OpenStreetMap (OSM) Building Data
| Aspect | Details |
|--------|---------|
| **Coverage** | Global (variable completeness) |
| **Data** | Building footprints, heights (where tagged) |
| **License** | ODbL |
| **Access** | Overpass API, Geofabrik, GEE |

**GEE Access:** `ee.FeatureCollection('OSM/...')`

**Quality Notes:**
- Urban areas: Generally good to excellent
- Rural areas: Variable, often incomplete
- Height data: Sparse (~5% of buildings)

### 6.4 OpenBuildingMap
| Aspect | Details |
|--------|---------|
| **Total Buildings** | 2.7 billion |
| **Sources** | OSM + Google + Microsoft (conflated) |
| **Attributes** | Height, occupancy type, floorspace |
| **Taxonomy** | GEM Building Taxonomy |
| **Use Case** | Disaster risk assessment |

**GEE Access:** `projects/sat-io/open-datasets/OPEN-BUILDING-MAPS/...`

### 6.5 GHSL (Global Human Settlement Layer)
| Dataset | Resolution | Description |
|---------|------------|-------------|
| **GHSL Built-up Surface** | 10m | Built-up area from S2 |
| **GHSL Settlement Characteristics** | 10m | Building height, volume |
| **GHSL Population** | 100m | Population grids |
| **GHSL Urban Centers** | Vector | Urban boundaries |

---

## 7. Summary: Finest Free Resolution by Category

### 7.1 Finest Resolution FREELY Available
| Category | Finest Free Resolution | Source |
|----------|------------------------|--------|
| **Optical Imagery (Global)** | 10m | Sentinel-2 |
| **Radar Imagery (Global)** | 10m | Sentinel-1 |
| **DEM (Global)** | 30m | Copernicus DEM, SRTM, AW3D30 |
| **DEM (USA)** | 1m | USGS 3DEP |
| **Aerial Imagery (USA)** | 0.3m | USDA NAIP |
| **Aerial Imagery (Europe)** | 10-25cm | National programs (varies) |
| **Building Footprints (Global)** | Variable | Microsoft (1.4B buildings) |
| **Land Cover (Global)** | 10m | ESA WorldCover, Dynamic World |
| **Tropical Forests** | 4.77m | Planet NICFI |

### 7.2 What Requires Academic/Research Access
| Data Source | Access Model | Notes |
|-------------|--------------|-------|
| **PlanetScope (daily)** | Commercial / Research grants | 3-5m resolution |
| **SkySat** | Commercial / Research grants | 0.8m resolution |
| **TanDEM-X 12m** | Commercial | High-res global DEM |
| **Maxar Archive** | Commercial | 30-50cm |
| **Airbus SPOT** | Commercial / NICFI (tropics only) | 1.5-20m |
| **LiDAR (most sources)** | Academic/research agreements | High-res point clouds |

### 7.3 Coverage Limitations
| Region | Limitations | Best Available |
|--------|-------------|--------------|
| **USA** | Excellent coverage | 1m DEM (3DEP), 0.3m aerial (NAIP) |
| **Europe** | Good to excellent | 10-30m DEM, 10-50cm aerial (varies) |
| **Tropical Forests** | Cloud cover (optical) | NICFI (4.77m), Sentinel-1 SAR |
| **Arctic** | Limited high-res | ArcticDEM (2-8m) |
| **Antarctica** | Limited | REMA (2-8m) |
| **Africa** | Variable building data | Microsoft footprints, Google Open Buildings |
| **Oceania** | Good | State-level LiDAR in AU/NZ |

### 7.4 Temporal Frequency at High Resolution
| Source | Resolution | Revisit Frequency |
|--------|------------|-------------------|
| **Sentinel-2** | 10m | 5 days (global) |
| **Sentinel-1** | 10m | 6 days (global) |
| **Landsat 8/9** | 30m | 16 days (global) |
| **PlanetScope** | 3-5m | Daily (commercial) |
| **MODIS** | 250m-1km | Daily (global) |
| **NAIP** | 0.3-1m | 3-year cycle (USA) |
| **NICFI** | 4.77m | Monthly mosaics (tropics) |

---

## 8. Recommended Data Stacks for Climate Risk & Infrastructure Analysis

### 8.1 Global Analysis (30m)
- **Base Imagery:** Sentinel-2 (10m) + Landsat (30m archive)
- **Elevation:** Copernicus DEM GLO-30 or NASADEM
- **Land Cover:** ESA WorldCover (10m) or Dynamic World
- **Buildings:** Microsoft Building Footprints
- **Water:** JRC Global Surface Water
- **Forest:** Hansen Global Forest Change

### 8.2 USA Analysis (1-10m)
- **Base Imagery:** NAIP (0.3-1m) + Sentinel-2
- **Elevation:** USGS 3DEP (1m where available, 10m seamless)
- **Land Cover:** NLCD (30m) + NAIP-derived
- **Buildings:** Microsoft + OSM
- **Hydrology:** NHDPlus High Resolution

### 8.3 Tropical Forest Analysis (5-10m)
- **Base Imagery:** Planet NICFI (4.77m) + Sentinel-2
- **Radar:** Sentinel-1 (all-weather)
- **Forest Change:** Hansen + NICFI
- **Elevation:** Copernicus DEM

### 8.4 Urban/Sub-Urban Analysis (1-10m)
- **Imagery:** Sentinel-2 (10m) + NAIP/Local aerial (where available)
- **Buildings:** Microsoft Footprints + OSM + Google Open Buildings
- **Elevation:** 3DEP (USA) or Copernicus DEM (global)
- **Land Cover:** Dynamic World (10m) + manual interpretation

---

## 9. Key URLs and Access Points

### Google Earth Engine Data Catalog
https://developers.google.com/earth-engine/datasets/catalog

### USGS 3DEP
https://www.usgs.gov/3d-elevation-program

### OpenTopography
https://portal.opentopography.org/

### Planet NICFI
https://www.planet.com/nicfi/

### Microsoft Building Footprints
https://github.com/microsoft/GlobalMLBuildingFootprints

### Google Open Buildings
https://sites.research.google/open-buildings/

### USDA NAIP
https://www.fsa.usda.gov/programs-and-services/aerial-photography/imagery-programs/naip-imagery/

### Copernicus Data Space
https://dataspace.copernicus.eu/

### Sentinel Hub
https://www.sentinel-hub.com/

---

## 10. Data Selection Decision Matrix

| Use Case | Recommended Resolution | Primary Source | Secondary Source |
|----------|------------------------|----------------|------------------|
| **National climate risk assessment** | 30m | Landsat/Sentinel-2 | Copernicus DEM |
| **Regional flood modeling** | 10-30m | Sentinel-2 | Copernicus DEM |
| **Urban heat island analysis** | 10-30m | Landsat (thermal) | Sentinel-2 |
| **Building-level vulnerability** | 1-10m | Microsoft Footprints | 3DEP/Local LiDAR |
| **Infrastructure monitoring** | 3-10m | Sentinel-2 | NICFI (tropics) |
| **Deforestation detection** | 10-30m | Sentinel-2 | NICFI (tropics) |
| **Agricultural monitoring** | 10m | Sentinel-2 | Landsat archive |
| **Disaster response** | 10m+ | Sentinel-1/2 | Maxar Open Data |

---

*Document compiled: February 2025*
*Focus: Sub-kilometer resolution geospatial data for climate risk, infrastructure, and vulnerability assessment*
