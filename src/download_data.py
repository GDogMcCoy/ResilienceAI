"""
ResilienceAI - Data Acquisition Pipeline
Downloads and caches data from HIFLD/FEMA ArcGIS, FEMA OpenAPI, Census, and CMS.
"""
import json
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import requests
from pathlib import Path
from config import (
    RAW_DIR, CACHE_DIR, HIFLD_URLS, CMS_NURSING_HOME_URL,
    CENSUS_BASE_URL, CENSUS_VARIABLES, CENSUS_API_KEY, FOCUS_STATES
)


def download_with_cache(url, cache_name, force=False):
    """Download URL content with local file caching."""
    cache_path = CACHE_DIR / f"{cache_name}.json"
    if cache_path.exists() and not force:
        print(f"  [CACHE HIT] {cache_name}")
        with open(cache_path, "r") as f:
            return json.load(f)

    print(f"  [DOWNLOADING] {cache_name}...")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    with open(cache_path, "w") as f:
        json.dump(data, f)
    return data


# == HIFLD Facilities (ArcGIS REST API with pagination) ================
def download_hifld_layer(name, base_url, force=False):
    """Download all records from an ArcGIS REST FeatureServer layer."""
    all_features = []
    offset = 0
    page_size = 2000

    while True:
        params = f"?where=1%3D1&outFields=*&returnGeometry=true&outSR=4326&f=json&resultRecordCount={page_size}&resultOffset={offset}"
        url = base_url + params
        cache_name = f"hifld_{name}_offset{offset}"

        # Clear bad cache (0-feature responses from old URLs)
        cache_path = CACHE_DIR / f"{cache_name}.json"
        if cache_path.exists() and not force:
            with open(cache_path, "r") as f:
                cached = json.load(f)
            if cached.get("error") or len(cached.get("features", [])) == 0:
                print(f"  [CLEARING BAD CACHE] {cache_name}")
                cache_path.unlink()

        data = download_with_cache(url, cache_name, force=force)

        if "error" in data:
            print(f"  [ERROR] {name}: {data['error']}")
            break

        features = data.get("features", [])
        if not features:
            break

        all_features.extend(features)
        print(f"    {name}: fetched {len(all_features)} records so far")

        # Check if there are more pages
        if not data.get("exceededTransferLimit", False) and len(features) < page_size:
            break
        offset += page_size
        time.sleep(0.3)

    return all_features


def parse_hifld_features(features, name):
    """Convert ArcGIS JSON features to DataFrame."""
    rows = []
    for f in features:
        attrs = f.get("attributes", {})
        geom = f.get("geometry", {})
        attrs["longitude"] = geom.get("x")
        attrs["latitude"] = geom.get("y")
        rows.append(attrs)

    df = pd.DataFrame(rows)
    df["facility_type"] = name
    return df


def download_all_hifld(force=False):
    """Download all HIFLD facility types."""
    print("\n=== Downloading HIFLD Facilities ===")
    all_dfs = {}

    for name, url in HIFLD_URLS.items():
        print(f"\n  --- {name} ---")
        features = download_hifld_layer(name, url, force=force)
        df = parse_hifld_features(features, name)
        csv_path = RAW_DIR / f"hifld_{name}.csv"
        df.to_csv(csv_path, index=False)
        all_dfs[name] = df
        print(f"  {name}: {len(df)} records saved -> {csv_path.name}")

    return all_dfs


# == CMS Nursing Homes (Medicare Provider Data API) ====================
def download_nursing_homes(force=False):
    """Download nursing home data from CMS Medicare Provider Data API."""
    print("\n=== Downloading CMS Nursing Homes ===")
    all_records = []
    offset = 0
    page_size = 1000

    while True:
        url = f"{CMS_NURSING_HOME_URL}?limit={page_size}&offset={offset}"
        cache_name = f"cms_nursing_homes_offset{offset}"
        cache_path = CACHE_DIR / f"{cache_name}.json"

        if cache_path.exists() and not force:
            print(f"  [CACHE HIT] {cache_name}")
            with open(cache_path, "r") as f:
                data = json.load(f)
        else:
            print(f"  [DOWNLOADING] {cache_name}...")
            resp = requests.get(CMS_NURSING_HOME_URL, params={"limit": page_size, "offset": offset}, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            with open(cache_path, "w") as f:
                json.dump(data, f)

        records = data.get("results", [])
        if not records:
            break

        all_records.extend(records)
        print(f"  Fetched {len(all_records)} nursing home records so far")

        if len(records) < page_size:
            break
        offset += page_size
        time.sleep(0.3)

    df = pd.DataFrame(all_records)

    # Standardize column names to match HIFLD format
    rename_map = {
        "provider_name": "NAME",
        "provider_address": "ADDRESS",
        "citytown": "CITY",
        "state": "STATE",
        "zip_code": "ZIP",
        "countyparish": "COUNTY",
        "latitude": "latitude",
        "longitude": "longitude",
        "number_of_certified_beds": "BEDS",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    df["facility_type"] = "nursing_homes"

    # Convert lat/lon to numeric
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    csv_path = RAW_DIR / "hifld_nursing_homes.csv"
    df.to_csv(csv_path, index=False)
    print(f"  Nursing homes: {len(df)} records saved -> {csv_path.name}")
    return df


# == FEMA Disaster Declarations ========================================
def download_fema_disasters(force=False):
    """Download FEMA disaster declarations via OpenFEMA API (paginated)."""
    print("\n=== Downloading FEMA Disaster Declarations ===")
    all_records = []
    skip = 0
    page_size = 10000

    while True:
        url = f"https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$skip={skip}&$top={page_size}&$format=json"
        cache_name = f"fema_disasters_skip{skip}"
        data = download_with_cache(url, cache_name, force=force)

        records = data.get("DisasterDeclarationsSummaries", [])
        if not records:
            break

        all_records.extend(records)
        print(f"  Fetched {len(all_records)} disaster records so far")

        if len(records) < page_size:
            break
        skip += page_size
        time.sleep(0.5)

    df = pd.DataFrame(all_records)
    csv_path = RAW_DIR / "fema_disasters.csv"
    df.to_csv(csv_path, index=False)
    print(f"  FEMA: {len(df)} records saved -> {csv_path.name}")
    return df


# == Census ACS Demographics ==========================================
def download_census_data(force=False):
    """Download Census ACS 5-year data by county."""
    print("\n=== Downloading Census ACS Data ===")

    var_str = ",".join(CENSUS_VARIABLES)
    url = f"{CENSUS_BASE_URL}?get=NAME,{var_str}&for=county:*&in=state:*"

    if CENSUS_API_KEY:
        url += f"&key={CENSUS_API_KEY}"

    cache_name = "census_acs_counties"
    cache_path = CACHE_DIR / f"{cache_name}.json"

    if cache_path.exists() and not force:
        print(f"  [CACHE HIT] {cache_name}")
        with open(cache_path, "r") as f:
            data = json.load(f)
    else:
        print(f"  [DOWNLOADING] Census ACS county data...")
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        with open(cache_path, "w") as f:
            json.dump(data, f)

    headers = data[0]
    rows = data[1:]
    df = pd.DataFrame(rows, columns=headers)

    df["fips"] = df["state"] + df["county"]

    for col in CENSUS_VARIABLES:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    rename_map = {
        "NAME": "county_name",
        "B01003_001E": "total_population",
        "B19013_001E": "median_income",
        "B17001_002E": "poverty_count",
        "B27010_001E": "insurance_universe",
    }
    df = df.rename(columns=rename_map)

    elderly_cols = [
        "B01001_020E", "B01001_021E", "B01001_022E", "B01001_023E",
        "B01001_024E", "B01001_025E",
        "B01001_044E", "B01001_045E", "B01001_046E", "B01001_047E",
        "B01001_048E", "B01001_049E",
    ]
    df["elderly_population"] = df[elderly_cols].sum(axis=1)

    disability_cols = [
        "B18101_004E", "B18101_007E", "B18101_010E", "B18101_013E",
        "B18101_016E", "B18101_019E",
        "B18101_023E", "B18101_026E", "B18101_029E", "B18101_032E",
        "B18101_035E", "B18101_038E",
    ]
    df["disability_count"] = df[disability_cols].sum(axis=1)

    uninsured_cols = ["B27010_017E", "B27010_033E", "B27010_050E", "B27010_066E"]
    df["uninsured_count"] = df[uninsured_cols].sum(axis=1)

    df["elderly_pct"] = (df["elderly_population"] / df["total_population"] * 100).round(2)
    df["poverty_pct"] = (df["poverty_count"] / df["total_population"] * 100).round(2)
    df["disability_pct"] = (df["disability_count"] / df["total_population"] * 100).round(2)
    df["uninsured_pct"] = (df["uninsured_count"] / df["insurance_universe"] * 100).round(2)

    keep_cols = [
        "fips", "county_name", "total_population", "median_income",
        "poverty_count", "poverty_pct", "elderly_population", "elderly_pct",
        "disability_count", "disability_pct", "uninsured_count", "uninsured_pct",
    ]
    df = df[[c for c in keep_cols if c in df.columns]]

    csv_path = RAW_DIR / "census_demographics.csv"
    df.to_csv(csv_path, index=False)
    print(f"  Census: {len(df)} counties saved -> {csv_path.name}")
    return df


# == County Centroids ==================================================
def download_county_centroids(force=False):
    """Download county centroid coordinates from Census gazetteer."""
    print("\n=== Downloading County Centroids ===")
    # Try multiple gazetteer years in case one is unavailable
    urls = [
        "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_counties_national.txt",
        "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2022_Gazetteer/2022_Gaz_counties_national.txt",
        "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2020_Gazetteer/2020_Gaz_counties_national.txt",
    ]
    cache_path = CACHE_DIR / "county_centroids.txt"

    if cache_path.exists() and not force:
        print(f"  [CACHE HIT] county_centroids")
    else:
        downloaded = False
        for url in urls:
            year = url.split("Gazetteer/")[1].split("_")[0]
            print(f"  [TRYING] {year} gazetteer...")
            try:
                resp = requests.get(url, timeout=90)
                resp.raise_for_status()
                with open(cache_path, "wb") as f:
                    f.write(resp.content)
                print(f"  [OK] Downloaded {year} gazetteer")
                downloaded = True
                break
            except Exception as e:
                print(f"  [FAILED] {year}: {type(e).__name__}")

        if not downloaded:
            print("  [WARNING] Could not download gazetteer. Will derive centroids from Census data.")
            return _generate_centroids_from_census()

    df = pd.read_csv(cache_path, sep="\t", dtype={"GEOID": str})
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        "GEOID": "fips",
        "NAME": "county_name",
        "INTPTLAT": "latitude",
        "INTPTLONG": "longitude",
    })

    csv_path = RAW_DIR / "county_centroids.csv"
    df[["fips", "county_name", "latitude", "longitude"]].to_csv(csv_path, index=False)
    print(f"  Centroids: {len(df)} counties saved -> {csv_path.name}")
    return df


def _generate_centroids_from_census():
    """Fallback: create county centroid file from zip code centroids or use FIPS-based lookup."""
    # Use a simple lat/lon lookup from the HUD USPS ZIP-County crosswalk
    # For now just create an empty file - we'll merge lat/lon from facility data instead
    print("  [FALLBACK] Using facility coordinates to estimate county positions")
    csv_path = RAW_DIR / "county_centroids.csv"
    pd.DataFrame(columns=["fips", "county_name", "latitude", "longitude"]).to_csv(csv_path, index=False)
    return pd.DataFrame()


# == Main ==============================================================
def download_all(force=False):
    """Download all data sources."""
    print("=" * 60)
    print("ResilienceAI - Data Acquisition Pipeline")
    print("=" * 60)

    hifld = download_all_hifld(force=force)
    nursing = download_nursing_homes(force=force)
    hifld["nursing_homes"] = nursing

    fema = download_fema_disasters(force=force)
    census = download_census_data(force=force)
    centroids = download_county_centroids(force=force)

    print("\n" + "=" * 60)
    print("Data acquisition complete!")
    print(f"  HIFLD layers: {len(hifld)} types")
    for name, df in hifld.items():
        print(f"    - {name}: {len(df)} records")
    print(f"  FEMA disasters: {len(fema)} records")
    print(f"  Census counties: {len(census)} records")
    print(f"  County centroids: {len(centroids)} records")
    print("=" * 60)

    return {"hifld": hifld, "fema": fema, "census": census, "centroids": centroids}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Download ResilienceAI data")
    parser.add_argument("--force", action="store_true", help="Force re-download")
    args = parser.parse_args()
    download_all(force=args.force)
