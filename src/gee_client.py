"""
ResilienceAI - Google Earth Engine Client
Pre-compute + cache pattern: fetches county-level satellite indicators from GEE
and stores as local Parquet files. Dashboard reads cache only — never calls GEE live.

Requires: pip install earthengine-api
Auth:     python -c "import ee; ee.Authenticate()"
Env var:  GEE_PROJECT_ID=your-gcp-project-id
"""
import os
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Cache directory
GEE_CACHE_DIR = Path(__file__).parent.parent / "data" / "gee_cache"
GEE_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Try to import ee — graceful fallback if not installed
try:
    import ee
    EE_AVAILABLE = True
except ImportError:
    EE_AVAILABLE = False
    logger.info("earthengine-api not installed. GEE features disabled.")


# ── Dataset constants ────────────────────────────────────────────────

DATASETS = {
    "lst": {
        "id": "MODIS/061/MOD11A2",
        "band": "LST_Day_1km",
        "scale": 1000,
        "description": "Land Surface Temperature (MODIS 8-day, 1km)",
    },
    "ndvi": {
        "id": "MODIS/061/MOD13Q1",
        "band": "NDVI",
        "scale": 250,
        "description": "Vegetation Index (MODIS 16-day, 250m)",
    },
    "pdsi": {
        "id": "GRIDMET/DROUGHT",
        "band": "pdsi",
        "scale": 4000,
        "description": "Palmer Drought Severity Index (GRIDMET, 4km)",
    },
    "nightlights": {
        "id": "NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG",
        "band": "avg_rad",
        "scale": 500,
        "description": "Nighttime Lights (VIIRS monthly, 500m)",
    },
    "water": {
        "id": "JRC/GSW1_4/GlobalSurfaceWater",
        "band": "occurrence",
        "scale": 30,
        "description": "Surface Water Occurrence (JRC, 30m)",
    },
    "burn": {
        "id": "MODIS/061/MCD64A1",
        "band": "BurnDate",
        "scale": 500,
        "description": "Burned Area (MODIS monthly, 500m)",
    },
}

# Season date ranges (Northern Hemisphere)
SEASONS = {
    "spring": ("{year}-03-01", "{year}-05-31"),
    "summer": ("{year}-06-01", "{year}-08-31"),
    "fall": ("{year}-09-01", "{year}-11-30"),
    "winter": ("{year}-12-01", "{year_next}-02-28"),
    "annual": ("{year}-01-01", "{year}-12-31"),
}


class GEEClient:
    """Google Earth Engine client for county-level satellite indicator aggregation."""

    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.environ.get("GEE_PROJECT_ID", "")
        self._initialized = False

    def _ensure_init(self) -> bool:
        """Lazy-initialize Earth Engine. Returns True if ready."""
        if self._initialized:
            return True
        if not EE_AVAILABLE:
            logger.warning("earthengine-api not installed")
            return False
        try:
            if self.project_id:
                ee.Initialize(project=self.project_id)
            else:
                ee.Initialize()
            self._initialized = True
            logger.info("Earth Engine initialized successfully")
            return True
        except Exception as e:
            logger.warning(f"Earth Engine init failed: {e}")
            return False

    def _get_counties(self, state_fips: str) -> "ee.FeatureCollection":
        """Load TIGER county boundaries for a state."""
        counties = ee.FeatureCollection("TIGER/2018/Counties")
        return counties.filter(ee.Filter.eq("STATEFP", state_fips))

    def _reduce_by_county(
        self, image: "ee.Image", counties: "ee.FeatureCollection", scale: int
    ) -> pd.DataFrame:
        """Reduce an image over county polygons, return DataFrame with GEOID column."""
        reduced = image.reduceRegions(
            collection=counties,
            reducer=ee.Reducer.mean(),
            scale=scale,
        )
        # Fetch results — OK for single-state (~115 counties)
        features = reduced.getInfo()["features"]
        rows = []
        for f in features:
            props = f["properties"]
            rows.append({
                "fips": props.get("GEOID", ""),
                "county_name": props.get("NAME", ""),
                "state_fips": props.get("STATEFP", ""),
                "value": props.get("mean", None),
            })
        return pd.DataFrame(rows)

    # ── Indicator methods ────────────────────────────────────────────

    def get_land_surface_temp(
        self, state_fips: str, year: int, season: str = "summer"
    ) -> pd.DataFrame:
        """Get mean land surface temperature by county (°C)."""
        if not self._ensure_init():
            return pd.DataFrame()

        start, end = self._season_dates(year, season)
        counties = self._get_counties(state_fips)

        collection = (
            ee.ImageCollection(DATASETS["lst"]["id"])
            .filterDate(start, end)
            .select(DATASETS["lst"]["band"])
        )
        image = collection.mean()
        # Convert: scale factor 0.02, then Kelvin -> Celsius
        image = image.multiply(0.02).subtract(273.15)

        df = self._reduce_by_county(image, counties, DATASETS["lst"]["scale"])
        df = df.rename(columns={"value": "lst_celsius"})
        df["lst_fahrenheit"] = df["lst_celsius"] * 9 / 5 + 32
        df["year"] = year
        df["season"] = season
        df["indicator"] = "lst"
        return df

    def get_vegetation_index(
        self, state_fips: str, year: int, season: str = "summer"
    ) -> pd.DataFrame:
        """Get mean NDVI by county (scaled 0-1)."""
        if not self._ensure_init():
            return pd.DataFrame()

        start, end = self._season_dates(year, season)
        counties = self._get_counties(state_fips)

        collection = (
            ee.ImageCollection(DATASETS["ndvi"]["id"])
            .filterDate(start, end)
            .select(DATASETS["ndvi"]["band"])
        )
        image = collection.mean().multiply(0.0001)  # Scale factor

        df = self._reduce_by_county(image, counties, DATASETS["ndvi"]["scale"])
        df = df.rename(columns={"value": "ndvi"})
        df["year"] = year
        df["season"] = season
        df["indicator"] = "ndvi"
        return df

    def get_drought_index(
        self, state_fips: str, year: int, month: int = None
    ) -> pd.DataFrame:
        """Get mean Palmer Drought Severity Index by county."""
        if not self._ensure_init():
            return pd.DataFrame()

        if month:
            start = f"{year}-{month:02d}-01"
            end_month = month + 1 if month < 12 else 1
            end_year = year if month < 12 else year + 1
            end = f"{end_year}-{end_month:02d}-01"
        else:
            start, end = f"{year}-01-01", f"{year}-12-31"

        counties = self._get_counties(state_fips)

        collection = (
            ee.ImageCollection(DATASETS["pdsi"]["id"])
            .filterDate(start, end)
            .select(DATASETS["pdsi"]["band"])
        )
        image = collection.mean()

        df = self._reduce_by_county(image, counties, DATASETS["pdsi"]["scale"])
        df = df.rename(columns={"value": "pdsi"})
        df["year"] = year
        df["month"] = month
        df["indicator"] = "pdsi"
        return df

    def get_nighttime_lights(
        self, state_fips: str, year: int
    ) -> pd.DataFrame:
        """Get mean nighttime radiance by county (nW/cm2/sr)."""
        if not self._ensure_init():
            return pd.DataFrame()

        counties = self._get_counties(state_fips)

        collection = (
            ee.ImageCollection(DATASETS["nightlights"]["id"])
            .filterDate(f"{year}-01-01", f"{year}-12-31")
            .select(DATASETS["nightlights"]["band"])
        )
        image = collection.mean()

        df = self._reduce_by_county(image, counties, DATASETS["nightlights"]["scale"])
        df = df.rename(columns={"value": "avg_radiance"})
        df["year"] = year
        df["indicator"] = "nightlights"
        return df

    def get_surface_water(self, state_fips: str) -> pd.DataFrame:
        """Get surface water occurrence % by county (static dataset)."""
        if not self._ensure_init():
            return pd.DataFrame()

        counties = self._get_counties(state_fips)

        image = ee.Image(DATASETS["water"]["id"]).select(DATASETS["water"]["band"])

        df = self._reduce_by_county(image, counties, DATASETS["water"]["scale"])
        df = df.rename(columns={"value": "water_occurrence_pct"})
        df["indicator"] = "water"
        return df

    def get_burned_area(
        self, state_fips: str, year: int
    ) -> pd.DataFrame:
        """Get burned area pixel count by county for a given year."""
        if not self._ensure_init():
            return pd.DataFrame()

        counties = self._get_counties(state_fips)

        collection = (
            ee.ImageCollection(DATASETS["burn"]["id"])
            .filterDate(f"{year}-01-01", f"{year}-12-31")
            .select(DATASETS["burn"]["band"])
        )
        # BurnDate > 0 means burned; count burned pixels
        burned_mask = collection.max().gt(0).selfMask()

        # Use sum reducer to count burned pixels
        reduced = burned_mask.reduceRegions(
            collection=counties,
            reducer=ee.Reducer.sum(),
            scale=DATASETS["burn"]["scale"],
        )
        features = reduced.getInfo()["features"]
        rows = []
        for f in features:
            props = f["properties"]
            pixel_count = props.get("sum", 0) or 0
            # Each pixel = 500m x 500m = 0.25 km²
            rows.append({
                "fips": props.get("GEOID", ""),
                "county_name": props.get("NAME", ""),
                "state_fips": props.get("STATEFP", ""),
                "burned_pixels": int(pixel_count),
                "burned_area_km2": round(pixel_count * 0.25, 2),
            })
        df = pd.DataFrame(rows)
        df["year"] = year
        df["indicator"] = "burn"
        return df

    # ── Batch fetch + cache ──────────────────────────────────────────

    def fetch_all_indicators(
        self, state_fips: str, year: int, season: str = "summer"
    ) -> Dict[str, pd.DataFrame]:
        """Fetch all 6 indicators and save to Parquet cache."""
        results = {}
        fetchers = {
            "lst": lambda: self.get_land_surface_temp(state_fips, year, season),
            "ndvi": lambda: self.get_vegetation_index(state_fips, year, season),
            "pdsi": lambda: self.get_drought_index(state_fips, year),
            "nightlights": lambda: self.get_nighttime_lights(state_fips, year),
            "water": lambda: self.get_surface_water(state_fips),
            "burn": lambda: self.get_burned_area(state_fips, year),
        }

        for key, fetcher in fetchers.items():
            try:
                logger.info(f"Fetching {key} for state {state_fips}, year {year}...")
                df = fetcher()
                if not df.empty:
                    cache_path = self._cache_path(key, state_fips, year)
                    df.to_parquet(cache_path, index=False)
                    logger.info(f"  Cached {len(df)} rows -> {cache_path}")
                    results[key] = df
                else:
                    logger.warning(f"  {key}: empty result")
            except Exception as e:
                logger.error(f"  {key} failed: {e}")
                results[key] = pd.DataFrame()

        return results

    # ── Cache I/O ────────────────────────────────────────────────────

    @staticmethod
    def _cache_path(indicator: str, state_fips: str, year: int = None) -> Path:
        """Build cache file path."""
        if year:
            return GEE_CACHE_DIR / f"{indicator}_county_{state_fips}_{year}.parquet"
        return GEE_CACHE_DIR / f"{indicator}_county_{state_fips}.parquet"

    @staticmethod
    def load_cached(indicator: str, state_fips: str, year: int = None) -> pd.DataFrame:
        """Load a cached indicator from Parquet. Returns empty DataFrame if missing."""
        path = GEEClient._cache_path(indicator, state_fips, year)
        if path.exists():
            return pd.read_parquet(path)
        return pd.DataFrame()

    @staticmethod
    def load_all_cached(state_fips: str, year: int) -> Dict[str, pd.DataFrame]:
        """Load all cached indicators for a state/year."""
        results = {}
        for key in DATASETS:
            yr = year if key != "water" else None  # water is static
            df = GEEClient.load_cached(key, state_fips, yr)
            if not df.empty:
                results[key] = df
        return results

    @staticmethod
    def get_cache_status(state_fips: str, year: int) -> Dict[str, dict]:
        """Check which indicators are cached and when they were last updated."""
        status = {}
        for key in DATASETS:
            yr = year if key != "water" else None
            path = GEEClient._cache_path(key, state_fips, yr)
            if path.exists():
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                df = pd.read_parquet(path)
                status[key] = {
                    "cached": True,
                    "rows": len(df),
                    "last_updated": mtime.isoformat(),
                    "path": str(path),
                }
            else:
                status[key] = {"cached": False, "description": DATASETS[key]["description"]}
        return status

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _season_dates(year: int, season: str) -> tuple:
        """Return (start_date, end_date) strings for a season."""
        if season not in SEASONS:
            season = "annual"
        start_tpl, end_tpl = SEASONS[season]
        start = start_tpl.format(year=year, year_next=year + 1)
        end = end_tpl.format(year=year, year_next=year + 1)
        return start, end
