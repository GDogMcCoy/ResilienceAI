# ResilienceAI - API & Data Source Reference

## Working API Endpoints (Verified Feb 15, 2026)

### HIFLD Facilities (FEMA ArcGIS Hub)

**Base URL**: `https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services`

| Layer | Endpoint | Records |
|-------|----------|---------|
| Hospitals | `.../Hospitals/FeatureServer/0/query` | 7,496 |
| EMS Stations | `.../Structures_Medical_Emergency_Response_v1/FeatureServer/1/query` | 7,045 |
| Fire Stations | `.../Structures_Medical_Emergency_Response_v1/FeatureServer/2/query` | 52,051 |

**Query Parameters**:
```
?where=1%3D1&outFields=*&returnGeometry=true&outSR=4326&f=json&resultRecordCount=2000&resultOffset=0
```

**Pagination**: Max 2,000 records per page. Check `exceededTransferLimit` to know if more pages exist.

**Note**: The old HIFLD URLs (`services1.arcgis.com/Hp6G80Pky0om6HgQ`) return "Invalid URL" as of Feb 2026.

### CMS Medicare Nursing Homes

**URL**: `https://data.cms.gov/provider-data/api/1/datastore/query/4pq5-n9py/0`

**Parameters**: `?limit=1000&offset=0` (max limit is 1000, returns 400 for higher)

**Key fields**: `provider_name`, `latitude`, `longitude`, `state`, `countyparish`, `number_of_certified_beds`

### FEMA Disaster Declarations

**URL**: `https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries`

**Parameters**: `?$skip=0&$top=10000&$format=json`

**Key fields**: `fipsStateCode`, `fipsCountyCode`, `incidentType`, `declarationDate`, `disasterNumber`

**Incident types**: Flood, Hurricane, Fire, Tornado, Severe Storm(s), Snowstorm, etc.

### Census ACS 5-Year (2022)

**URL**: `https://api.census.gov/data/2022/acs/acs5`

**Parameters**: `?get=NAME,B01003_001E,...&for=county:*&in=state:*`

**No API key required** for basic queries (but rate-limited).

**Variable reference**: https://api.census.gov/data/2022/acs/acs5/variables.html

### Census Gazetteer (County Centroids)

**Per-state files**: `https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_gaz_counties_{FIPS}.txt`

**Note**: National file URLs 404. Must download per-state and concatenate. State FIPS: 01-56, 60, 66, 69, 72, 78.

## Dead/Broken Endpoints (Do Not Use)

| URL Pattern | Issue |
|-------------|-------|
| `services1.arcgis.com/Hp6G80Pky0om6HgQ/...` | Returns "Invalid URL" for all services |
| `maps.nccs.nasa.gov/mapping/rest/services/hifld_open/...` | Connection timeout (>30s) |
| `opendata.arcgis.com/api/v3/datasets/.../downloads/...` | Returns 500 |
| `www2.census.gov/.../2023_Gaz_counties_national.txt` | 404 |
| `www2.census.gov/.../2020_Gaz_counties_national.txt` | 404 |

## How to Discover New HIFLD Endpoints

If HIFLD URLs change again, search the ArcGIS Hub:

```python
import requests
r = requests.get('https://hub.arcgis.com/api/v3/datasets?q=hifld+hospitals')
for item in r.json()['data'][:5]:
    print(item['attributes']['name'], item['attributes']['url'])
```

Look for entries with source "U.S. Federal Maps and Apps" or "FEMA AGOL".
