"""
ResilienceAI - GEE Pre-Compute Pipeline
Fetches county-level satellite indicators from Google Earth Engine and caches as Parquet.

Usage:
    python src/pipeline/gee_fetch.py --state 29 --year 2024
    python src/pipeline/gee_fetch.py --state 29 --year 2024 --indicator lst
    python src/pipeline/gee_fetch.py --state 29 --year 2024 --season summer
    python src/pipeline/gee_fetch.py --status --state 29 --year 2024

Requires:
    pip install earthengine-api
    python -c "import ee; ee.Authenticate()"
    export GEE_PROJECT_ID=your-gcp-project-id
"""
import sys
import os
import argparse
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.gee_client import GEEClient, DATASETS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Fetch GEE satellite indicators for ResilienceAI")
    parser.add_argument("--state", default="29", help="State FIPS code (default: 29 = Missouri)")
    parser.add_argument("--year", type=int, default=2024, help="Year to fetch (default: 2024)")
    parser.add_argument("--season", default="summer", choices=["spring", "summer", "fall", "winter", "annual"],
                        help="Season for LST/NDVI (default: summer)")
    parser.add_argument("--indicator", choices=list(DATASETS.keys()),
                        help="Fetch a single indicator (default: all)")
    parser.add_argument("--status", action="store_true", help="Show cache status and exit")
    parser.add_argument("--project", help="GEE project ID (overrides GEE_PROJECT_ID env var)")
    args = parser.parse_args()

    if args.status:
        status = GEEClient.get_cache_status(args.state, args.year)
        print(f"\nGEE Cache Status — State {args.state}, Year {args.year}")
        print("-" * 60)
        for key, info in status.items():
            if info.get("cached"):
                print(f"  {key:12s}  {info['rows']:4d} rows  updated {info['last_updated']}")
            else:
                print(f"  {key:12s}  NOT CACHED  ({info.get('description', '')})")
        return

    client = GEEClient(project_id=args.project)

    if args.indicator:
        # Single indicator
        indicator = args.indicator
        logger.info(f"Fetching {indicator} for state {args.state}, year {args.year}, season {args.season}")
        fetchers = {
            "lst": lambda: client.get_land_surface_temp(args.state, args.year, args.season),
            "ndvi": lambda: client.get_vegetation_index(args.state, args.year, args.season),
            "pdsi": lambda: client.get_drought_index(args.state, args.year),
            "nightlights": lambda: client.get_nighttime_lights(args.state, args.year),
            "water": lambda: client.get_surface_water(args.state),
            "burn": lambda: client.get_burned_area(args.state, args.year),
        }
        df = fetchers[indicator]()
        if not df.empty:
            yr = args.year if indicator != "water" else None
            path = GEEClient._cache_path(indicator, args.state, yr)
            df.to_parquet(path, index=False)
            logger.info(f"Saved {len(df)} rows -> {path}")
        else:
            logger.warning("No data returned")
    else:
        # All indicators
        logger.info(f"Fetching ALL indicators for state {args.state}, year {args.year}")
        results = client.fetch_all_indicators(args.state, args.year, args.season)
        logger.info(f"\nDone. Cached {len(results)} indicators:")
        for key, df in results.items():
            logger.info(f"  {key}: {len(df)} rows")


if __name__ == "__main__":
    main()
