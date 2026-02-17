# ResilienceAI Export & Reporting Enhancement Analysis

## Executive Summary

This document provides a comprehensive analysis of the current export capabilities in ResilienceAI and proposes extensive enhancements for a world-class reporting platform. The analysis covers:

- Current state assessment of export modules
- Proposed advanced export capabilities
- Report generation pipeline architecture
- Template designs and automation
- Data anonymization strategies
- Batch processing infrastructure
- Integration points with existing codebase

---

## 1. Current State Analysis

### 1.1 Existing Export Capabilities

Based on analysis of the `claw-autonomous` branch, ResilienceAI currently has:

#### GeoJSON Export (`src/geojson_export.py`)
**File Location:** `/src/geojson_export.py` (305 lines, 12 KB)

**Current Features:**
- `GeoJSONExporter` class with comprehensive export methods
- Point geometry export for counties (longitude/latitude)
- Property filtering (minimal vs. full)
- State abbreviation to full name mapping (51 entries)
- Export methods:
  - `export_all()` - All counties
  - `export_state()` - By state (supports abbreviations)
  - `export_county()` - Single county by FIPS
  - `export_by_risk_level()` - Filter by Low/Medium/High
  - `export_high_risk()` - Threshold-based (default 0.7)
  - `export_compound_risk()` - Multi-dimensional risk
- CLI interface with argparse
- Summary statistics generation

**Exported Properties (28+ metrics):**
```python
# Core identifiers
- fips, county_name, state

# Risk metrics
- risk_score, risk_level, vulnerability_index, isolation_index

# Demographics
- total_population, poverty_pct, elderly_pct, disability_pct, uninsured_pct

# Infrastructure distances
- dist_nearest_hospitals_km, dist_nearest_fire_stations_km
- dist_nearest_ems_stations_km, dist_nearest_nursing_homes_km

# Infrastructure counts
- count_hospitals_50km, count_fire_stations_50km
- count_ems_stations_50km, count_nursing_homes_50km

# Infrastructure density
- density_hospitals_per10k, density_fire_stations_per10k
- density_ems_stations_per10k, density_nursing_homes_per10k

# Disaster history
- disaster_count, disaster_count_recent, disaster_flood
- disaster_hurricane, disaster_fire, disaster_tornado

# Advanced metrics
- disaster_acceleration, redundancy_score, pop_weighted_risk
- compound_risk_count, top_intervention

# Boolean flags
- compound_risk_flag, zero_redundancy_flag
```

**Output Format:**
```json
{
  "type": "FeatureCollection",
  "crs": {
    "type": "name",
    "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
  },
  "features": [...]
}
```

#### FHIR R4 Export (`src/fhir_export.py`)
**File Location:** `/src/fhir_export.py` (382 lines, 14.8 KB)

**Current Features:**
- `FHIRExporter` class for health system integration
- FHIR Version 4.0.1 compliant
- SDOH Clinical Care profile support
- Resource types generated:
  - `Bundle` - Container resource with metadata
  - `Location` - County geographic information
  - `RiskAssessment` - Composite risk scoring
  - `Observation` - Individual metrics (10 types)

**FHIR Resources Generated:**
```python
# Location Resource
- FIPS identifier with coding
- Geographic position (lat/lon)
- State address
- Community type coding

# RiskAssessment Resource
- Subject reference to Location
- Prediction with probability
- Qualitative risk coding (high/moderate/low)
- Basis references (vulnerability, isolation, disaster)
- Mitigation recommendation

# Observation Resources (10 metrics)
- vulnerability_index
- isolation_index
- poverty_pct
- elderly_pct
- disability_pct
- uninsured_pct
- disaster_count
- disaster_count_recent
- compound_risk_count
- dist_nearest_hospitals_km
```

**Export Methods:**
- `export_county()` - Single county
- `export_state()` - All counties in state
- `export_high_risk()` - Threshold-based filtering

#### Briefing Generator (`src/briefing_generator.py`)
**File Location:** `/src/briefing_generator.py` (414 lines, 16.1 KB)

**Current Features:**
- `BriefingGenerator` class for executive reports
- PDF generation (ReportLab)
- PowerPoint generation (python-pptx)
- Single-county briefings
- Risk visualization tables
- Intervention recommendations

**Dependencies:**
```python
HAS_REPORTLAB = True  # PDF generation
HAS_PPTX = True       # PowerPoint generation
```

### 1.2 Configuration Structure

**Base Directories (from `config.py`):**
```python
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = BASE_DIR / "outputs" / "figures"
```

### 1.3 Current Limitations

1. **No Excel/CSV Export** - Missing spreadsheet format exports
2. **No PDF Report Generation** - Briefing generator exists but limited
3. **No Advanced GeoJSON Features** - No polygon boundaries, styling
4. **No Report Scheduling** - Manual export only
5. **No Custom Templates** - Fixed report formats
6. **No Data Anonymization** - Direct data export
7. **No Batch Processing** - Single operations only
8. **No Report Distribution** - File-based only
9. **Limited FHIR Resources** - Only 3 resource types
10. **No Export API Endpoints** - CLI only

---

## 2. Proposed Export & Reporting Platform

### 2.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RESILIENCEAI EXPORT PLATFORM                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │   Export API    │  │ Report Scheduler│  │  Template Engine│              │
│  │    (REST)       │  │   (Celery)      │  │   (Jinja2)      │              │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘              │
│           │                    │                    │                        │
│           └────────────────────┼────────────────────┘                        │
│                                │                                             │
│                     ┌──────────┴──────────┐                                  │
│                     │   Export Pipeline   │                                  │
│                     │     Orchestrator    │                                  │
│                     └──────────┬──────────┘                                  │
│                                │                                             │
│  ┌─────────────────────────────┼─────────────────────────────┐              │
│  │                             │                             │              │
│  ▼                             ▼                             ▼              │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐          │
│  │  Data Layer  │    │  Format Engines  │    │  Distribution    │          │
│  │              │    │                  │    │                  │          │
│  │ • Anonymizer │    │ • GeoJSON Adv.   │    │ • Email          │          │
│  │ • Filter     │    │ • FHIR R4        │    │ • SFTP           │          │
│  │ • Transform  │    │ • PDF Report     │    │ • S3             │          │
│  │ • Validate   │    │ • Excel/CSV      │    │ • API Webhook    │          │
│  └──────────────┘    │ • Parquet        │    │ • File System    │          │
│                      └──────────────────┘    └──────────────────┘          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Proposed Folder Structure

```
resilienceai/
├── src/
│   ├── exports/                          # NEW: Export modules
│   │   ├── __init__.py
│   │   ├── base_exporter.py              # Abstract base class
│   │   ├── geojson_advanced.py           # Enhanced GeoJSON
│   │   ├── fhir_advanced.py              # Extended FHIR
│   │   ├── excel_exporter.py             # Excel workbooks
│   │   ├── csv_exporter.py               # CSV with formatting
│   │   ├── pdf_reporter.py               # PDF generation
│   │   ├── parquet_exporter.py           # Columnar format
│   │   └── kml_exporter.py               # Google Earth
│   │
│   ├── reports/                          # NEW: Report generation
│   │   ├── __init__.py
│   │   ├── report_engine.py              # Core engine
│   │   ├── template_manager.py           # Template handling
│   │   ├── schedulers/                   # Scheduled reports
│   │   │   ├── __init__.py
│   │   │   ├── celery_config.py
│   │   │   └── report_tasks.py
│   │   ├── templates/                    # Report templates
│   │   │   ├── executive_briefing.html
│   │   │   ├── county_profile.html
│   │   │   ├── state_summary.html
│   │   │   ├── risk_analysis.html
│   │   │   └── intervention_plan.html
│   │   └── generators/                   # Report generators
│   │       ├── __init__.py
│   │       ├── executive_generator.py
│   │       ├── technical_generator.py
│   │       └── compliance_generator.py
│   │
│   ├── anonymization/                    # NEW: Data privacy
│   │   ├── __init__.py
│   │   ├── anonymizer.py                 # Main anonymizer
│   │   ├── k_anonymity.py                # k-anonymity algorithm
│   │   ├── l_diversity.py                # l-diversity algorithm
│   │   ├── differential_privacy.py       # DP noise injection
│   │   └── policies/                     # Anonymization policies
│   │       ├── public_policy.yaml
│   │       ├── research_policy.yaml
│   │       └── internal_policy.yaml
│   │
│   ├── api/                              # NEW: Export API
│   │   ├── __init__.py
│   │   ├── routes.py                     # FastAPI routes
│   │   ├── models.py                     # Pydantic models
│   │   ├── dependencies.py               # Auth, rate limiting
│   │   └── middleware/                   # CORS, logging
│   │
│   └── batch/                            # NEW: Batch processing
│       ├── __init__.py
│       ├── batch_processor.py            # Core processor
│       ├── job_queue.py                  # Job management
│       └── workers/                      # Worker implementations
│
├── reports/                              # EXISTING: Output directory
│   ├── generated/                        # Auto-generated reports
│   ├── scheduled/                        # Scheduled report outputs
│   ├── templates/                        # Custom templates
│   └── archive/                          # Historical reports
│
├── exports/                              # NEW: Export outputs
│   ├── geojson/                          # GeoJSON files
│   ├── fhir/                             # FHIR bundles
│   ├── excel/                            # Excel workbooks
│   ├── pdf/                              # PDF reports
│   └── csv/                              # CSV exports
│
└── config/
    └── export_config.yaml                # Export configuration
```

---

## 3. Enhanced Export Modules

### 3.1 Advanced GeoJSON Export

**File:** `src/exports/geojson_advanced.py`

#### Features

```python
"""
Advanced GeoJSON Export Module
Extends basic GeoJSON with styling, clustering, and topology
"""

from typing import Dict, List, Optional, Literal
from dataclasses import dataclass
import json
import pandas as pd
from pathlib import Path


@dataclass
class GeoJSONStyle:
    """Styling configuration for GeoJSON features"""
    property: str  # Property to style by
    color_scale: Literal['viridis', 'plasma', 'rdylgn', 'rdylr']
    fill_opacity: float = 0.7
    stroke_color: str = '#333333'
    stroke_width: int = 1
    radius_range: tuple = (5, 25)  # For point features


@dataclass
class GeoJSONClusterConfig:
    """Configuration for point clustering"""
    enabled: bool = True
    distance: int = 50  # pixels
    max_zoom: int = 15
    min_points: int = 2


class AdvancedGeoJSONExporter:
    """
    Advanced GeoJSON exporter with styling, clustering, and topology support
    """
    
    def __init__(self, df=None, county_boundaries_path=None):
        """
        Initialize exporter
        
        Args:
            df: County features DataFrame
            county_boundaries_path: Path to GeoJSON with county polygons
        """
        self.df = df or self._load_default_data()
        self.boundaries = self._load_boundaries(county_boundaries_path)
        
    def export_with_polygons(
        self,
        fips_list: List[str],
        include_properties: bool = True,
        simplify_tolerance: float = 0.001
    ) -> Dict:
        """
        Export counties with polygon geometries
        
        Args:
            fips_list: List of FIPS codes to export
            include_properties: Include all properties
            simplify_tolerance: Simplification tolerance (0-1)
            
        Returns:
            GeoJSON FeatureCollection with Polygon/MultiPolygon geometries
        """
        features = []
        
        for fips in fips_list:
            county_data = self.df[self.df['fips'] == fips]
            if county_data.empty:
                continue
                
            row = county_data.iloc[0]
            geometry = self._get_county_geometry(fips, simplify_tolerance)
            
            feature = {
                "type": "Feature",
                "geometry": geometry,
                "properties": self._build_properties(row, include_properties)
            }
            features.append(feature)
            
        return {
            "type": "FeatureCollection",
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                }
            },
            "features": features
        }
    
    def export_with_styling(
        self,
        style_config: GeoJSONStyle,
        filter_query: Optional[str] = None
    ) -> Dict:
        """
        Export with Mapbox/Leaflet compatible styling
        
        Args:
            style_config: Styling configuration
            filter_query: Pandas query string for filtering
            
        Returns:
            GeoJSON with style properties embedded
        """
        df = self.df
        if filter_query:
            df = df.query(filter_query)
            
        # Calculate color scale
        values = df[style_config.property]
        min_val, max_val = values.min(), values.max()
        
        features = []
        for _, row in df.iterrows():
            # Calculate color based on value
            normalized = (row[style_config.property] - min_val) / (max_val - min_val)
            color = self._get_color_from_scale(normalized, style_config.color_scale)
            
            # Calculate radius for point features
            radius = self._interpolate_radius(
                normalized, 
                style_config.radius_range
            )
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        float(row['longitude']),
                        float(row['latitude'])
                    ]
                },
                "properties": {
                    **self._build_properties(row, True),
                    "style": {
                        "fillColor": color,
                        "fillOpacity": style_config.fill_opacity,
                        "color": style_config.stroke_color,
                        "weight": style_config.stroke_width,
                        "radius": radius
                    }
                }
            }
            features.append(feature)
            
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def export_clustered(
        self,
        cluster_config: GeoJSONClusterConfig,
        bbox: Optional[tuple] = None
    ) -> Dict:
        """
        Export with clustering metadata for efficient rendering
        
        Args:
            cluster_config: Clustering configuration
            bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
            
        Returns:
            GeoJSON with cluster metadata
        """
        df = self.df
        if bbox:
            df = df[
                (df['longitude'] >= bbox[0]) &
                (df['longitude'] <= bbox[2]) &
                (df['latitude'] >= bbox[1]) &
                (df['latitude'] <= bbox[3])
            ]
            
        # Perform clustering
        clusters = self._cluster_points(df, cluster_config)
        
        features = []
        for cluster in clusters:
            if cluster['count'] == 1:
                # Single point
                row = df[df['fips'] == cluster['fips']].iloc[0]
                feature = self._row_to_feature(row, True)
            else:
                # Cluster point
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [cluster['lon'], cluster['lat']]
                    },
                    "properties": {
                        "cluster": True,
                        "cluster_count": cluster['count'],
                        "cluster_risk_avg": cluster['avg_risk'],
                        "cluster_fips": cluster['fips_list']
                    }
                }
            features.append(feature)
            
        return {
            "type": "FeatureCollection",
            "cluster_config": {
                "enabled": cluster_config.enabled,
                "distance": cluster_config.distance,
                "max_zoom": cluster_config.max_zoom
            },
            "features": features
        }
    
    def export_time_series(
        self,
        fips: str,
        temporal_data: pd.DataFrame,
        time_column: str = 'date'
    ) -> Dict:
        """
        Export time-series data as animated GeoJSON
        
        Args:
            fips: County FIPS code
            temporal_data: DataFrame with time-series data
            time_column: Column containing timestamps
            
        Returns:
            GeoJSON with temporal properties
        """
        county_data = self.df[self.df['fips'] == fips]
        if county_data.empty:
            return {"error": f"County {fips} not found"}
            
        row = county_data.iloc[0]
        
        # Build temporal properties
        temporal_properties = []
        for _, t_row in temporal_data.iterrows():
            temporal_properties.append({
                "timestamp": t_row[time_column].isoformat(),
                "risk_score": float(t_row.get('risk_score', 0)),
                "vulnerability_index": float(t_row.get('vulnerability_index', 0)),
                "disaster_count": int(t_row.get('disaster_count', 0))
            })
            
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    float(row['longitude']),
                    float(row['latitude'])
                ]
            },
            "properties": {
                "fips": fips,
                "county_name": row['county_name'],
                "temporal_data": temporal_properties
            }
        }
    
    def export_topology(
        self,
        fips_list: List[str],
        include_neighbors: bool = True
    ) -> Dict:
        """
        Export with topological relationships
        
        Args:
            fips_list: List of FIPS codes
            include_neighbors: Include neighboring counties
            
        Returns:
            GeoJSON with topology references
        """
        features = []
        
        for fips in fips_list:
            county_data = self.df[self.df['fips'] == fips]
            if county_data.empty:
                continue
                
            row = county_data.iloc[0]
            
            # Get neighbors
            neighbors = []
            if include_neighbors:
                neighbors = self._get_neighbor_counties(fips)
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        float(row['longitude']),
                        float(row['latitude'])
                    ]
                },
                "properties": {
                    **self._build_properties(row, True),
                    "topology": {
                        "neighbors": neighbors,
                        "neighbor_count": len(neighbors),
                        "neighbor_avg_risk": self._get_neighbor_avg_risk(neighbors)
                    }
                }
            }
            features.append(feature)
            
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    # Helper methods
    def _load_default_data(self):
        """Load default county features"""
        from config import PROCESSED_DIR
        path = PROCESSED_DIR / "county_features.csv"
        if path.exists():
            return pd.read_csv(path, dtype={"fips": str})
        return None
    
    def _load_boundaries(self, path):
        """Load county boundary GeoJSON"""
        if path and Path(path).exists():
            with open(path) as f:
                return json.load(f)
        return None
    
    def _get_county_geometry(self, fips, simplify_tolerance):
        """Get polygon geometry for county"""
        if self.boundaries:
            for feature in self.boundaries['features']:
                if feature['properties'].get('GEOID') == fips:
                    geom = feature['geometry']
                    if simplify_tolerance > 0:
                        geom = self._simplify_geometry(geom, simplify_tolerance)
                    return geom
        # Fallback to point
        row = self.df[self.df['fips'] == fips].iloc[0]
        return {
            "type": "Point",
            "coordinates": [float(row['longitude']), float(row['latitude'])]
        }
    
    def _simplify_geometry(self, geometry, tolerance):
        """Simplify geometry using Douglas-Peucker"""
        # Implementation using shapely
        from shapely.geometry import shape, mapping
        geom = shape(geometry)
        simplified = geom.simplify(tolerance, preserve_topology=True)
        return mapping(simplified)
    
    def _build_properties(self, row, include_all):
        """Build properties dictionary"""
        properties = {
            "fips": str(row.get('fips', '')),
            "county_name": row.get('county_name', 'Unknown'),
            "risk_score": float(row.get('risk_score', 0)),
            "risk_level": row.get('risk_level', 'Low')
        }
        
        if include_all:
            # Add all available metrics
            numeric_cols = [
                'vulnerability_index', 'isolation_index',
                'poverty_pct', 'elderly_pct', 'disability_pct', 'uninsured_pct',
                'disaster_count', 'disaster_count_recent',
                'dist_nearest_hospitals_km', 'dist_nearest_fire_stations_km',
                'redundancy_score', 'pop_weighted_risk'
            ]
            for col in numeric_cols:
                if col in row and pd.notna(row[col]):
                    properties[col] = float(row[col])
                    
        return properties
    
    def _get_color_from_scale(self, normalized, scale_name):
        """Get color from color scale"""
        scales = {
            'viridis': ['#440154', '#31688e', '#35b779', '#fde725'],
            'plasma': ['#0d0887', '#7e03a8', '#cc4778', '#f0f921'],
            'rdylgn': ['#d73027', '#fee08b', '#d9ef8b', '#1a9850'],
            'rdylr': ['#ffffcc', '#fd8d3c', '#f03b20', '#bd0026']
        }
        colors = scales.get(scale_name, scales['viridis'])
        idx = int(normalized * (len(colors) - 1))
        return colors[min(idx, len(colors) - 1)]
    
    def _interpolate_radius(self, normalized, radius_range):
        """Interpolate radius based on normalized value"""
        min_r, max_r = radius_range
        return min_r + normalized * (max_r - min_r)
    
    def _cluster_points(self, df, config):
        """Perform point clustering"""
        # Implementation using sklearn or custom algorithm
        from sklearn.cluster import DBSCAN
        
        coords = df[['longitude', 'latitude']].values
        clustering = DBSCAN(
            eps=config.distance / 111320,  # Convert pixels to degrees (~111km)
            min_samples=config.min_points
        ).fit(coords)
        
        clusters = []
        for label in set(clustering.labels_):
            if label == -1:
                # Noise points (individual)
                for idx in df[clustering.labels_ == -1].index:
                    row = df.loc[idx]
                    clusters.append({
                        'count': 1,
                        'fips': row['fips'],
                        'lon': row['longitude'],
                        'lat': row['latitude'],
                        'fips_list': [row['fips']]
                    })
            else:
                # Cluster
                cluster_df = df[clustering.labels_ == label]
                clusters.append({
                    'count': len(cluster_df),
                    'fips': None,
                    'lon': cluster_df['longitude'].mean(),
                    'lat': cluster_df['latitude'].mean(),
                    'avg_risk': cluster_df['risk_score'].mean(),
                    'fips_list': cluster_df['fips'].tolist()
                })
                
        return clusters
    
    def _get_neighbor_counties(self, fips):
        """Get neighboring counties"""
        # Implementation using spatial index
        # This would use a pre-built adjacency list or spatial query
        pass
    
    def _get_neighbor_avg_risk(self, neighbors):
        """Calculate average risk of neighbors"""
        if not neighbors:
            return None
        neighbor_data = self.df[self.df['fips'].isin(neighbors)]
        return float(neighbor_data['risk_score'].mean()) if not neighbor_data.empty else None
```

---

## 4. Report Generation Pipeline

### 4.1 Report Engine Core

**File:** `src/reports/report_engine.py`

```python
"""
Report Generation Engine
Core engine for generating multi-format reports
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import json
import yaml
import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape


class ReportFormat(Enum):
    """Supported report formats"""
    PDF = "pdf"
    HTML = "html"
    DOCX = "docx"
    PPTX = "pptx"
    MARKDOWN = "md"
    JSON = "json"


class ReportType(Enum):
    """Report types"""
    EXECUTIVE_BRIEFING = "executive_briefing"
    COUNTY_PROFILE = "county_profile"
    STATE_SUMMARY = "state_summary"
    RISK_ANALYSIS = "risk_analysis"
    INTERVENTION_PLAN = "intervention_plan"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    TREND_REPORT = "trend_report"
    COMPLIANCE_REPORT = "compliance_report"


@dataclass
class ReportSection:
    """Report section definition"""
    name: str
    title: str
    template: str
    data_sources: List[str]
    charts: List[str] = field(default_factory=list)
    tables: List[str] = field(default_factory=list)
    conditional: Optional[str] = None  # Condition for inclusion


@dataclass
class ReportConfig:
    """Report configuration"""
    name: str
    type: ReportType
    formats: List[ReportFormat]
    sections: List[ReportSection]
    parameters: Dict[str, Any]
    styling: Dict[str, Any]
    distribution: List[str]  # Distribution channels


class ReportEngine:
    """
    Core report generation engine
    """
    
    def __init__(self, template_dir: str = "src/reports/templates"):
        """
        Initialize report engine
        
        Args:
            template_dir: Directory containing Jinja2 templates
        """
        self.template_dir = Path(template_dir)
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Register custom filters
        self._register_filters()
        
        # Data providers
        self.data_providers = {}
        
        # Chart generators
        self.chart_generators = {}
        
    def _register_filters(self):
        """Register custom Jinja2 filters"""
        self.jinja_env.filters['format_number'] = self._format_number
        self.jinja_env.filters['format_percent'] = self._format_percent
        self.jinja_env.filters['risk_badge'] = self._risk_badge
        self.jinja_env.filters['risk_color'] = self._risk_color
        self.jinja_env.filters['format_currency'] = self._format_currency
        
    def register_data_provider(self, name: str, provider: Callable):
        """Register a data provider function"""
        self.data_providers[name] = provider
        
    def register_chart_generator(self, name: str, generator: Callable):
        """Register a chart generator function"""
        self.chart_generators[name] = generator
        
    def generate_report(
        self,
        config: ReportConfig,
        output_dir: str,
        parameters: Optional[Dict] = None
    ) -> Dict[str, Path]:
        """
        Generate report in all configured formats
        
        Args:
            config: Report configuration
            output_dir: Output directory
            parameters: Runtime parameters
            
        Returns:
            Dictionary mapping format to output path
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Merge parameters
        params = {**config.parameters, **(parameters or {})}
        
        # Gather data for all sections
        section_data = {}
        for section in config.sections:
            section_data[section.name] = self._gather_section_data(section, params)
            
        # Generate charts
        charts = {}
        for section in config.sections:
            for chart_name in section.charts:
                charts[chart_name] = self._generate_chart(chart_name, section_data, params)
                
        # Generate tables
        tables = {}
        for section in config.sections:
            for table_name in section.tables:
                tables[table_name] = self._generate_table(table_name, section_data, params)
                
        # Render for each format
        outputs = {}
        for fmt in config.formats:
            output_path = self._render_format(
                config, section_data, charts, tables, params, fmt, output_dir
            )
            outputs[fmt.value] = output_path
            
        return outputs
    
    def _gather_section_data(
        self,
        section: ReportSection,
        parameters: Dict
    ) -> Dict:
        """Gather data for a report section"""
        data = {}
        
        for source_name in section.data_sources:
            if source_name in self.data_providers:
                data[source_name] = self.data_providers[source_name](parameters)
            else:
                data[source_name] = self._default_data_provider(source_name, parameters)
                
        return data
    
    def _generate_chart(
        self,
        chart_name: str,
        section_data: Dict,
        parameters: Dict
    ) -> Path:
        """Generate a chart"""
        if chart_name in self.chart_generators:
            return self.chart_generators[chart_name](section_data, parameters)
        return self._default_chart_generator(chart_name, section_data, parameters)
    
    def _generate_table(
        self,
        table_name: str,
        section_data: Dict,
        parameters: Dict
    ) -> pd.DataFrame:
        """Generate a data table"""
        # Implementation depends on table type
        pass
    
    def _render_format(
        self,
        config: ReportConfig,
        section_data: Dict,
        charts: Dict,
        tables: Dict,
        parameters: Dict,
        fmt: ReportFormat,
        output_dir: Path
    ) -> Path:
        """Render report in specific format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{config.name}_{timestamp}.{fmt.value}"
        output_path = output_dir / filename
        
        if fmt == ReportFormat.HTML:
            return self._render_html(config, section_data, charts, tables, parameters, output_path)
        elif fmt == ReportFormat.PDF:
            return self._render_pdf(config, section_data, charts, tables, parameters, output_path)
        elif fmt == ReportFormat.DOCX:
            return self._render_docx(config, section_data, charts, tables, parameters, output_path)
        elif fmt == ReportFormat.PPTX:
            return self._render_pptx(config, section_data, charts, tables, parameters, output_path)
        elif fmt == ReportFormat.MARKDOWN:
            return self._render_markdown(config, section_data, charts, tables, parameters, output_path)
        elif fmt == ReportFormat.JSON:
            return self._render_json(config, section_data, parameters, output_path)
        else:
            raise ValueError(f"Unsupported format: {fmt}")
    
    def _render_html(
        self,
        config: ReportConfig,
        section_data: Dict,
        charts: Dict,
        tables: Dict,
        parameters: Dict,
        output_path: Path
    ) -> Path:
        """Render HTML report"""
        template = self.jinja_env.get_template(f"{config.type.value}.html")
        
        html = template.render(
            config=config,
            sections=section_data,
            charts=charts,
            tables=tables,
            parameters=parameters,
            generated_at=datetime.now()
        )
        
        output_path.write_text(html, encoding='utf-8')
        return output_path
    
    def _render_pdf(
        self,
        config: ReportConfig,
        section_data: Dict,
        charts: Dict,
        tables: Dict,
        parameters: Dict,
        output_path: Path
    ) -> Path:
        """Render PDF report using WeasyPrint or ReportLab"""
        # First render HTML
        html_path = output_path.with_suffix('.html')
        self._render_html(config, section_data, charts, tables, parameters, html_path)
        
        # Convert to PDF
        try:
            from weasyprint import HTML, CSS
            html = HTML(filename=str(html_path))
            html.write_pdf(str(output_path))
        except ImportError:
            # Fallback to ReportLab
            self._render_pdf_reportlab(config, section_data, charts, tables, parameters, output_path)
            
        return output_path
    
    def _render_pdf_reportlab(
        self,
        config: ReportConfig,
        section_data: Dict,
        charts: Dict,
        tables: Dict,
        parameters: Dict,
        output_path: Path
    ) -> Path:
        """Render PDF using ReportLab"""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
        
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        story.append Paragraph(config.name, title_style)
        story.append(Spacer(1, 0.2*inch))
        
        # Sections
        for section in config.sections:
            story.append(Paragraph(section.title, styles['Heading2']))
            # Add section content
            story.append(Spacer(1, 0.1*inch))
            
        doc.build(story)
        return output_path
    
    def _render_docx(
        self,
        config: ReportConfig,
        section_data: Dict,
        charts: Dict,
        tables: Dict,
        parameters: Dict,
        output_path: Path
    ) -> Path:
        """Render Word document"""
        from docx import Document
        from docx.shared import Inches, Pt
        
        doc = Document()
        
        # Title
        title = doc.add_heading(config.name, 0)
        
        # Sections
        for section in config.sections:
            doc.add_heading(section.title, level=1)
            # Add section content
            
        doc.save(str(output_path))
        return output_path
    
    def _render_pptx(
        self,
        config: ReportConfig,
        section_data: Dict,
        charts: Dict,
        tables: Dict,
        parameters: Dict,
        output_path: Path
    ) -> Path:
        """Render PowerPoint presentation"""
        from pptx import Presentation
        from pptx.util import Inches
        
        prs = Presentation()
        
        # Title slide
        title_slide = prs.slides.add_slide(prs.slide_layouts[0])
        title = title_slide.shapes.title
        subtitle = title_slide.placeholders[1]
        
        title.text = config.name
        subtitle.text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Content slides
        for section in config.sections:
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = section.title
            # Add content
            
        prs.save(str(output_path))
        return output_path
    
    def _render_markdown(
        self,
        config: ReportConfig,
        section_data: Dict,
        charts: Dict,
        tables: Dict,
        parameters: Dict,
        output_path: Path
    ) -> Path:
        """Render Markdown report"""
        template = self.jinja_env.get_template(f"{config.type.value}.md")
        
        md = template.render(
            config=config,
            sections=section_data,
            charts=charts,
            tables=tables,
            parameters=parameters,
            generated_at=datetime.now()
        )
        
        output_path.write_text(md, encoding='utf-8')
        return output_path
    
    def _render_json(
        self,
        config: ReportConfig,
        section_data: Dict,
        parameters: Dict,
        output_path: Path
    ) -> Path:
        """Render JSON report"""
        report_data = {
            "name": config.name,
            "type": config.type.value,
            "generated_at": datetime.now().isoformat(),
            "parameters": parameters,
            "sections": section_data
        }
        
        output_path.write_text(json.dumps(report_data, indent=2, default=str))
        return output_path
    
    # Custom filter implementations
    def _format_number(self, value, decimals=2):
        """Format number with specified decimals"""
        return f"{value:,.{decimals}f}"
    
    def _format_percent(self, value, decimals=1):
        """Format as percentage"""
        return f"{value * 100:.{decimals}f}%"
    
    def _risk_badge(self, risk_level):
        """Generate risk level badge HTML"""
        colors = {
            'High': '#dc3545',
            'Medium': '#ffc107',
            'Low': '#28a745'
        }
        color = colors.get(risk_level, '#6c757d')
        return f'<span class="badge" style="background-color: {color}">{risk_level}</span>'
    
    def _risk_color(self, risk_score):
        """Get color for risk score"""
        if risk_score >= 0.7:
            return '#dc3545'
        elif risk_score >= 0.4:
            return '#ffc107'
        else:
            return '#28a745'
    
    def _format_currency(self, value, symbol='$'):
        """Format as currency"""
        return f"{symbol}{value:,.2f}"
```

---

## 5. Data Anonymization Module

### 5.1 Anonymizer Core

**File:** `src/anonymization/anonymizer.py`

```python
"""
Data Anonymization Module
Implements k-anonymity, l-diversity, and differential privacy
"""

from typing import Dict, List, Optional, Literal
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
from pathlib import Path
import yaml


class AnonymizationLevel(Enum):
    """Anonymization levels"""
    NONE = "none"
    MINIMAL = "minimal"  # Remove direct identifiers only
    STANDARD = "standard"  # k-anonymity
    STRICT = "strict"  # l-diversity + k-anonymity
    MAXIMUM = "maximum"  # Differential privacy


@dataclass
class AnonymizationPolicy:
    """Anonymization policy configuration"""
    level: AnonymizationLevel
    k: int = 5  # k-anonymity parameter
    l: int = 2  # l-diversity parameter
    epsilon: float = 1.0  # Differential privacy epsilon
    quasi_identifiers: List[str] = None
    sensitive_attributes: List[str] = None
    generalization_hierarchy: Dict = None


class DataAnonymizer:
    """
    Main anonymization class implementing multiple techniques
    """
    
    def __init__(self, policy: AnonymizationPolicy):
        """
        Initialize anonymizer with policy
        
        Args:
            policy: Anonymization policy configuration
        """
        self.policy = policy
        
    def anonymize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Anonymize dataframe according to policy
        
        Args:
            df: Input dataframe
            
        Returns:
            Anonymized dataframe
        """
        result = df.copy()
        
        if self.policy.level == AnonymizationLevel.NONE:
            return result
            
        if self.policy.level == AnonymizationLevel.MINIMAL:
            result = self._remove_direct_identifiers(result)
            
        elif self.policy.level == AnonymizationLevel.STANDARD:
            result = self._remove_direct_identifiers(result)
            result = self._apply_k_anonymity(result)
            
        elif self.policy.level == AnonymizationLevel.STRICT:
            result = self._remove_direct_identifiers(result)
            result = self._apply_k_anonymity(result)
            result = self._apply_l_diversity(result)
            
        elif self.policy.level == AnonymizationLevel.MAXIMUM:
            result = self._remove_direct_identifiers(result)
            result = self._apply_differential_privacy(result)
            
        return result
    
    def _remove_direct_identifiers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove direct identifiers (names, SSNs, etc.)"""
        direct_id_columns = ['name', 'ssn', 'email', 'phone', 'address']
        return df.drop(columns=[c for c in direct_id_columns if c in df.columns])
    
    def _apply_k_anonymity(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply k-anonymity using generalization
        
        Ensures each record is indistinguishable from at least k-1 others
        on quasi-identifier attributes
        """
        if not self.policy.quasi_identifiers:
            return df
            
        result = df.copy()
        
        # Group by quasi-identifiers
        grouped = result.groupby(self.policy.quasi_identifiers)
        
        # Find groups with less than k records
        small_groups = []
        for name, group in grouped:
            if len(group) < self.policy.k:
                small_groups.append(name)
                
        # Generalize small groups
        for group_key in small_groups:
            result = self._generalize_group(result, group_key)
            
        return result
    
    def _generalize_group(self, df: pd.DataFrame, group_key) -> pd.DataFrame:
        """Generalize a group to meet k-anonymity"""
        result = df.copy()
        
        # Apply generalization hierarchy
        for qi in self.policy.quasi_identifiers:
            if qi in self.policy.generalization_hierarchy:
                hierarchy = self.policy.generalization_hierarchy[qi]
                # Generalize to parent level
                result.loc[result[qi] == group_key, qi] = hierarchy.get('parent', '*')
                
        return result
    
    def _apply_l_diversity(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply l-diversity
        
        Ensures each equivalence class has at least l distinct values
        for sensitive attributes
        """
        if not self.policy.sensitive_attributes:
            return df
            
        result = df.copy()
        
        # Group by quasi-identifiers
        grouped = result.groupby(self.policy.quasi_identifiers)
        
        for name, group in grouped:
            for sa in self.policy.sensitive_attributes:
                if sa in group.columns:
                    unique_values = group[sa].nunique()
                    if unique_values < self.policy.l:
                        # Suppress or generalize
                        result.loc[group.index, sa] = '*'
                        
        return result
    
    def _apply_differential_privacy(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply differential privacy using Laplace mechanism
        
        Adds calibrated noise to numeric columns
        """
        result = df.copy()
        
        epsilon = self.policy.epsilon
        
        for col in df.select_dtypes(include=[np.number]).columns:
            if col in self.policy.sensitive_attributes:
                # Calculate sensitivity
                sensitivity = df[col].max() - df[col].min()
                
                # Add Laplace noise
                scale = sensitivity / epsilon
                noise = np.random.laplace(0, scale, len(df))
                result[col] = df[col] + noise
                
        return result
    
    def validate_anonymization(self, df: pd.DataFrame) -> Dict:
        """
        Validate anonymization results
        
        Returns:
            Dictionary with validation metrics
        """
        metrics = {
            'k_anonymity_satisfied': True,
            'l_diversity_satisfied': True,
            'records_anonymized': len(df),
            'equivalence_classes': 0,
            'avg_equivalence_class_size': 0
        }
        
        if self.policy.quasi_identifiers:
            grouped = df.groupby(self.policy.quasi_identifiers)
            metrics['equivalence_classes'] = len(grouped)
            metrics['avg_equivalence_class_size'] = len(df) / len(grouped)
            
            # Check k-anonymity
            min_group_size = grouped.size().min()
            metrics['k_anonymity_satisfied'] = min_group_size >= self.policy.k
            metrics['min_equivalence_class_size'] = min_group_size
            
        if self.policy.sensitive_attributes:
            # Check l-diversity
            grouped = df.groupby(self.policy.quasi_identifiers)
            for name, group in grouped:
                for sa in self.policy.sensitive_attributes:
                    if sa in group.columns:
                        if group[sa].nunique() < self.policy.l:
                            metrics['l_diversity_satisfied'] = False
                            
        return metrics


def load_policy_from_file(path: str) -> AnonymizationPolicy:
    """Load anonymization policy from YAML file"""
    with open(path) as f:
        config = yaml.safe_load(f)
        
    return AnonymizationPolicy(
        level=AnonymizationLevel(config['level']),
        k=config.get('k', 5),
        l=config.get('l', 2),
        epsilon=config.get('epsilon', 1.0),
        quasi_identifiers=config.get('quasi_identifiers', []),
        sensitive_attributes=config.get('sensitive_attributes', []),
        generalization_hierarchy=config.get('generalization_hierarchy', {})
    )
```

---

## 6. Batch Export Processing

### 6.1 Batch Processor

**File:** `src/batch/batch_processor.py`

```python
"""
Batch Export Processing Module
Handles large-scale export operations with job queuing
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import json
import hashlib
import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import pandas as pd


class JobStatus(Enum):
    """Job status states"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExportJob:
    """Export job definition"""
    id: str
    job_type: str
    parameters: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    progress: float = 0.0


class BatchProcessor:
    """
    Batch export processor with job management
    """
    
    def __init__(
        self,
        max_workers: int = 4,
        use_processes: bool = False,
        job_store_path: Optional[str] = None
    ):
        """
        Initialize batch processor
        
        Args:
            max_workers: Maximum parallel workers
            use_processes: Use process pool instead of thread pool
            job_store_path: Path to persist job state
        """
        self.max_workers = max_workers
        self.use_processes = use_processes
        self.job_store_path = Path(job_store_path) if job_store_path else None
        
        # Job registry
        self.jobs: Dict[str, ExportJob] = {}
        
        # Export handlers
        self.handlers: Dict[str, Callable] = {}
        
        # Executor
        self.executor = None
        
    def register_handler(self, job_type: str, handler: Callable):
        """Register an export handler"""
        self.handlers[job_type] = handler
        
    def create_job(
        self,
        job_type: str,
        parameters: Dict[str, Any]
    ) -> ExportJob:
        """
        Create a new export job
        
        Args:
            job_type: Type of export job
            parameters: Job parameters
            
        Returns:
            Created job
        """
        # Generate job ID
        job_data = f"{job_type}:{json.dumps(parameters, sort_keys=True)}"
        job_id = hashlib.sha256(job_data.encode()).hexdigest()[:16]
        
        job = ExportJob(
            id=job_id,
            job_type=job_type,
            parameters=parameters
        )
        
        self.jobs[job_id] = job
        self._persist_job(job)
        
        return job
    
    async def process_job(self, job_id: str) -> ExportJob:
        """
        Process a single job
        
        Args:
            job_id: Job identifier
            
        Returns:
            Completed job
        """
        job = self.jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
            
        if job.status not in [JobStatus.PENDING, JobStatus.QUEUED]:
            raise ValueError(f"Job {job_id} is not in processable state")
            
        handler = self.handlers.get(job.job_type)
        if not handler:
            raise ValueError(f"No handler for job type: {job.job_type}")
            
        # Update status
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        self._persist_job(job)
        
        try:
            # Execute handler
            if asyncio.iscoroutinefunction(handler):
                result = await handler(job.parameters, self._progress_callback(job))
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self._get_executor(),
                    handler,
                    job.parameters,
                    self._progress_callback(job)
                )
                
            # Update job
            job.status = JobStatus.COMPLETED
            job.result = result
            job.progress = 1.0
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            
        job.completed_at = datetime.now()
        self._persist_job(job)
        
        return job
    
    async def process_batch(
        self,
        job_ids: List[str],
        max_concurrent: Optional[int] = None
    ) -> List[ExportJob]:
        """
        Process multiple jobs with concurrency control
        
        Args:
            job_ids: List of job IDs to process
            max_concurrent: Maximum concurrent jobs
            
        Returns:
            List of completed jobs
        """
        semaphore = asyncio.Semaphore(max_concurrent or self.max_workers)
        
        async def process_with_limit(job_id):
            async with semaphore:
                return await self.process_job(job_id)
                
        tasks = [process_with_limit(jid) for jid in job_ids]
        return await asyncio.gather(*tasks)
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get job status"""
        job = self.jobs.get(job_id)
        if not job:
            return None
            
        return {
            'id': job.id,
            'type': job.job_type,
            'status': job.status.value,
            'progress': job.progress,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'result': job.result,
            'error': job.error
        }
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or queued job"""
        job = self.jobs.get(job_id)
        if job and job.status in [JobStatus.PENDING, JobStatus.QUEUED]:
            job.status = JobStatus.CANCELLED
            self._persist_job(job)
            return True
        return False
    
    def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        job_type: Optional[str] = None
    ) -> List[Dict]:
        """List jobs with optional filtering"""
        jobs = self.jobs.values()
        
        if status:
            jobs = [j for j in jobs if j.status == status]
        if job_type:
            jobs = [j for j in jobs if j.job_type == job_type]
            
        return [self.get_job_status(j.id) for j in jobs]
    
    def _get_executor(self):
        """Get or create executor"""
        if self.executor is None:
            if self.use_processes:
                self.executor = ProcessPoolExecutor(max_workers=self.max_workers)
            else:
                self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        return self.executor
    
    def _progress_callback(self, job: ExportJob):
        """Create progress callback for job"""
        def callback(progress: float):
            job.progress = progress
            self._persist_job(job)
        return callback
    
    def _persist_job(self, job: ExportJob):
        """Persist job state to disk"""
        if self.job_store_path:
            self.job_store_path.mkdir(parents=True, exist_ok=True)
            job_file = self.job_store_path / f"{job.id}.json"
            job_file.write_text(json.dumps({
                'id': job.id,
                'job_type': job.job_type,
                'parameters': job.parameters,
                'status': job.status.value,
                'created_at': job.created_at.isoformat(),
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'result': job.result,
                'error': job.error,
                'progress': job.progress
            }, indent=2))


# Pre-defined export handlers

async def export_geojson_handler(params: Dict, progress_callback: Callable) -> Dict:
    """Handler for GeoJSON batch exports"""
    from exports.geojson_advanced import AdvancedGeoJSONExporter
    
    exporter = AdvancedGeoJSONExporter()
    
    export_type = params.get('export_type', 'all')
    output_dir = Path(params.get('output_dir', 'exports/geojson'))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if export_type == 'all':
        data = exporter.export_all(params.get('include_properties', True))
        output_path = output_dir / f"all_counties_{datetime.now().strftime('%Y%m%d')}.geojson"
    elif export_type == 'state':
        data = exporter.export_state(params['state'], params.get('include_properties', True))
        output_path = output_dir / f"{params['state']}_{datetime.now().strftime('%Y%m%d')}.geojson"
    elif export_type == 'high_risk':
        data = exporter.export_high_risk(params.get('threshold', 0.7))
        output_path = output_dir / f"high_risk_{datetime.now().strftime('%Y%m%d')}.geojson"
    else:
        raise ValueError(f"Unknown export type: {export_type}")
        
    import json
    output_path.write_text(json.dumps(data, indent=2))
    
    progress_callback(1.0)
    
    return {
        'output_path': str(output_path),
        'feature_count': len(data.get('features', [])),
        'export_type': export_type
    }


async def export_excel_handler(params: Dict, progress_callback: Callable) -> Dict:
    """Handler for Excel batch exports"""
    from exports.excel_exporter import ExcelExporter
    
    exporter = ExcelExporter()
    
    output_dir = Path(params.get('output_dir', 'exports/excel'))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    result = exporter.export_workbook(
        params.get('sheets', ['summary', 'counties', 'risk_analysis']),
        str(output_path),
        params.get('filters', {})
    )
    
    progress_callback(1.0)
    
    return result


async def generate_report_handler(params: Dict, progress_callback: Callable) -> Dict:
    """Handler for report generation"""
    from reports.report_engine import ReportEngine, ReportConfig
    
    engine = ReportEngine()
    
    config = ReportConfig(
        name=params['name'],
        type=params['report_type'],
        formats=params.get('formats', ['pdf']),
        sections=params.get('sections', []),
        parameters=params.get('parameters', {}),
        styling=params.get('styling', {}),
        distribution=params.get('distribution', [])
    )
    
    output_dir = params.get('output_dir', 'reports/generated')
    
    outputs = engine.generate_report(config, output_dir, params.get('runtime_params', {}))
    
    progress_callback(1.0)
    
    return {
        'outputs': {k: str(v) for k, v in outputs.items()},
        'report_name': config.name
    }
```

---

## 7. Export API Endpoints

### 7.1 FastAPI Routes

**File:** `src/api/routes.py`

```python
"""
Export API Routes
FastAPI endpoints for export operations
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path
import json

from batch.batch_processor import BatchProcessor, ExportJob
from anonymization.anonymizer import DataAnonymizer, AnonymizationPolicy


router = APIRouter(prefix="/api/v1/exports", tags=["exports"])

# Initialize processor
processor = BatchProcessor(max_workers=4)

# Register handlers
processor.register_handler('geojson', export_geojson_handler)
processor.register_handler('excel', export_excel_handler)
processor.register_handler('report', generate_report_handler)


# Pydantic models

class GeoJSONExportRequest(BaseModel):
    """GeoJSON export request"""
    export_type: str = Field(..., description="Type: all, state, county, high_risk, compound_risk")
    state: Optional[str] = Field(None, description="State abbreviation (for state export)")
    county_fips: Optional[str] = Field(None, description="County FIPS (for county export)")
    risk_threshold: float = Field(0.7, description="Risk threshold (for high_risk export)")
    include_properties: bool = Field(True, description="Include all properties")
    anonymize: bool = Field(False, description="Apply anonymization")
    anonymization_level: str = Field("standard", description="Anonymization level")


class ExcelExportRequest(BaseModel):
    """Excel export request"""
    sheets: List[str] = Field(default=["summary", "counties", "risk_analysis"])
    filters: Dict[str, Any] = Field(default_factory=dict)
    include_charts: bool = Field(True)
    format_numbers: bool = Field(True)


class ReportGenerationRequest(BaseModel):
    """Report generation request"""
    name: str
    report_type: str
    formats: List[str] = Field(default=["pdf"])
    parameters: Dict[str, Any] = Field(default_factory=dict)
    distribution: List[str] = Field(default_factory=list)


class ExportResponse(BaseModel):
    """Export response"""
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    """Job status response"""
    id: str
    type: str
    status: str
    progress: float
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    result: Optional[Dict]
    error: Optional[str]


# Routes

@router.post("/geojson", response_model=ExportResponse)
async def export_geojson(
    request: GeoJSONExportRequest,
    background_tasks: BackgroundTasks
):
    """
    Export data as GeoJSON
    
    Creates an export job that generates GeoJSON files
    """
    params = {
        'export_type': request.export_type,
        'state': request.state,
        'county_fips': request.county_fips,
        'risk_threshold': request.risk_threshold,
        'include_properties': request.include_properties,
        'anonymize': request.anonymize,
        'anonymization_level': request.anonymization_level
    }
    
    job = processor.create_job('geojson', params)
    
    # Process in background
    background_tasks.add_task(processor.process_job, job.id)
    
    return ExportResponse(
        job_id=job.id,
        status=job.status.value,
        message=f"GeoJSON export job created. Use /jobs/{job.id}/status to track progress."
    )


@router.post("/excel", response_model=ExportResponse)
async def export_excel(
    request: ExcelExportRequest,
    background_tasks: BackgroundTasks
):
    """
    Export data as Excel workbook
    
    Creates an export job that generates formatted Excel files
    """
    params = {
        'sheets': request.sheets,
        'filters': request.filters,
        'include_charts': request.include_charts,
        'format_numbers': request.format_numbers
    }
    
    job = processor.create_job('excel', params)
    background_tasks.add_task(processor.process_job, job.id)
    
    return ExportResponse(
        job_id=job.id,
        status=job.status.value,
        message=f"Excel export job created. Use /jobs/{job.id}/status to track progress."
    )


@router.post("/report", response_model=ExportResponse)
async def generate_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate formatted report
    
    Creates a report generation job
    """
    params = {
        'name': request.name,
        'report_type': request.report_type,
        'formats': request.formats,
        'parameters': request.parameters,
        'distribution': request.distribution
    }
    
    job = processor.create_job('report', params)
    background_tasks.add_task(processor.process_job, job.id)
    
    return ExportResponse(
        job_id=job.id,
        status=job.status.value,
        message=f"Report generation job created. Use /jobs/{job.id}/status to track progress."
    )


@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get job status and results"""
    status = processor.get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return JobStatusResponse(**status)


@router.get("/jobs", response_model=List[JobStatusResponse])
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    job_type: Optional[str] = Query(None, description="Filter by type")
):
    """List all export jobs"""
    jobs = processor.list_jobs(
        status=JobStatus(status) if status else None,
        job_type=job_type
    )
    return [JobStatusResponse(**j) for j in jobs]


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a pending job"""
    if processor.cancel_job(job_id):
        return {"message": f"Job {job_id} cancelled"}
    raise HTTPException(status_code=400, detail=f"Cannot cancel job {job_id}")


@router.get("/download/{job_id}")
async def download_export(job_id: str):
    """Download completed export"""
    job = processor.jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
    if job.status.value != 'completed':
        raise HTTPException(status_code=400, detail=f"Job {job_id} is not completed")
        
    output_path = job.result.get('output_path')
    if not output_path:
        raise HTTPException(status_code=404, detail="No output file available")
        
    return FileResponse(
        output_path,
        filename=Path(output_path).name,
        media_type='application/octet-stream'
    )


@router.get("/formats")
async def list_export_formats():
    """List available export formats"""
    return {
        "formats": [
            {
                "id": "geojson",
                "name": "GeoJSON",
                "description": "Geographic data format for mapping",
                "content_types": ["application/geo+json"],
                "extensions": [".geojson"]
            },
            {
                "id": "excel",
                "name": "Excel Workbook",
                "description": "Multi-sheet Excel file with formatting",
                "content_types": ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
                "extensions": [".xlsx"]
            },
            {
                "id": "csv",
                "name": "CSV",
                "description": "Comma-separated values",
                "content_types": ["text/csv"],
                "extensions": [".csv"]
            },
            {
                "id": "pdf",
                "name": "PDF Report",
                "description": "Formatted PDF document",
                "content_types": ["application/pdf"],
                "extensions": [".pdf"]
            },
            {
                "id": "fhir",
                "name": "FHIR R4",
                "description": "FHIR R4 Bundle for health systems",
                "content_types": ["application/fhir+json"],
                "extensions": [".json"]
            },
            {
                "id": "parquet",
                "name": "Apache Parquet",
                "description": "Columnar storage format",
                "content_types": ["application/octet-stream"],
                "extensions": [".parquet"]
            }
        ]
    }
```

---

## 8. Implementation Priority Order

### Phase 1: Core Export Infrastructure (Weeks 1-2)

1. **Base Exporter Framework**
   - Create `src/exports/base_exporter.py`
   - Define abstract base class for all exporters
   - Implement common utility functions

2. **Enhanced CSV/Excel Export**
   - Create `src/exports/csv_exporter.py`
   - Create `src/exports/excel_exporter.py`
   - Add formatting, formulas, charts

3. **Advanced GeoJSON**
   - Enhance `src/exports/geojson_advanced.py`
   - Add polygon support, styling, clustering

### Phase 2: Report Generation (Weeks 3-4)

1. **Report Engine Core**
   - Create `src/reports/report_engine.py`
   - Implement Jinja2 template system
   - Add multi-format rendering

2. **Report Templates**
   - Create HTML templates
   - Create Markdown templates
   - Add executive briefing template

3. **PDF Generation**
   - Integrate WeasyPrint/ReportLab
   - Add chart embedding
   - Implement page layouts

### Phase 3: Data Privacy (Week 5)

1. **Anonymization Framework**
   - Create `src/anonymization/anonymizer.py`
   - Implement k-anonymity
   - Add l-diversity support

2. **Differential Privacy**
   - Implement Laplace mechanism
   - Add noise calibration
   - Create privacy budgets

### Phase 4: Batch Processing (Week 6)

1. **Batch Processor**
   - Create `src/batch/batch_processor.py`
   - Implement job queue
   - Add progress tracking

2. **Export Handlers**
   - Create handler functions
   - Add parallel processing
   - Implement error handling

### Phase 5: API & Integration (Week 7)

1. **FastAPI Routes**
   - Create `src/api/routes.py`
   - Implement export endpoints
   - Add job management

2. **Authentication & Rate Limiting**
   - Add API key authentication
   - Implement rate limiting
   - Add request logging

### Phase 6: Scheduling & Distribution (Week 8)

1. **Report Scheduler**
   - Integrate Celery
   - Create scheduled tasks
   - Add cron expressions

2. **Distribution Channels**
   - Email delivery
   - SFTP upload
   - S3 integration
   - Webhook notifications

---

## 9. Dependencies

### Required Packages

```txt
# Export formats
openpyxl>=3.1.0          # Excel export
xlsxwriter>=3.1.0        # Excel charts
python-docx>=0.8.11      # Word documents
python-pptx>=0.6.21      # PowerPoint
WeasyPrint>=59.0         # PDF generation
reportlab>=4.0.0         # Alternative PDF
pyarrow>=12.0.0          # Parquet export
fastkml>=1.0.0           # KML export

# API Framework
fastapi>=0.100.0
uvicorn>=0.23.0
python-multipart>=0.0.6

# Task Queue
celery>=5.3.0
redis>=4.6.0

# Templating
jinja2>=3.1.0
markdown>=3.4.0

# Data Processing
shapely>=2.0.0           # Geometry operations
sklearn>=1.3.0           # Clustering

# Privacy
diffprivlib>=0.6.0       # Differential privacy
```

---

## 10. Integration Points

### Existing Code Integration

```python
# In src/agent.py - Add export tools

EXPORT_TOOLS = [
    {
        "name": "export_geojson",
        "description": "Export data as GeoJSON",
        "parameters": {
            "export_type": {"type": "string"},
            "state": {"type": "string"},
            "output_format": {"type": "string", "enum": ["file", "json"]}
        }
    },
    {
        "name": "export_excel",
        "description": "Export data as Excel workbook",
        "parameters": {
            "sheets": {"type": "array"},
            "filters": {"type": "object"}
        }
    },
    {
        "name": "generate_report",
        "description": "Generate formatted report",
        "parameters": {
            "report_type": {"type": "string"},
            "formats": {"type": "array"},
            "parameters": {"type": "object"}
        }
    },
    {
        "name": "schedule_report",
        "description": "Schedule recurring report",
        "parameters": {
            "report_config": {"type": "object"},
            "schedule": {"type": "string"},
            "distribution": {"type": "array"}
        }
    }
]

# In modern_ui.py - Add export buttons

export_buttons = {
    "GeoJSON": st.download_button(
        label="Download GeoJSON",
        data=geojson_data,
        file_name="export.geojson",
        mime="application/geo+json"
    ),
    "Excel": st.download_button(
        label="Download Excel",
        data=excel_data,
        file_name="export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ),
    "PDF Report": st.download_button(
        label="Download PDF",
        data=pdf_data,
        file_name="report.pdf",
        mime="application/pdf"
    )
}
```

---

## 11. Summary

This comprehensive export and reporting enhancement plan provides:

1. **Advanced GeoJSON Export** - Polygon support, styling, clustering, topology
2. **Enhanced FHIR R4** - Extended resource types, bulk export
3. **Excel/CSV Export** - Formatted workbooks with charts
4. **PDF Report Generation** - Multi-format reports with templates
5. **Data Anonymization** - k-anonymity, l-diversity, differential privacy
6. **Batch Processing** - Job queue with parallel processing
7. **Export API** - REST endpoints for all export operations
8. **Report Scheduling** - Automated recurring reports
9. **Distribution** - Email, SFTP, S3, webhooks

The implementation follows a phased approach over 8 weeks, with clear priorities and integration points with the existing ResilienceAI codebase.

---

*Document generated for ResilienceAI claw-autonomous branch analysis*
*Analysis Date: 2026-02-17*
