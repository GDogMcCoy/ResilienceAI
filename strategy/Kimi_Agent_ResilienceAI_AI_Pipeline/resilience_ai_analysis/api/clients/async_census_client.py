"""
Async Census ACS API Client
Handles American Community Survey data with batching and caching

File: src/api/clients/async_census_client.py
"""
import asyncio
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import aiohttp

# Import gateway if available
try:
    from src.api.gateway import APIGateway
    GATEWAY_AVAILABLE = True
except ImportError:
    GATEWAY_AVAILABLE = False


@dataclass
class CensusProfile:
    """County demographic profile from ACS"""
    fips: str
    county_name: str
    state: str
    population: int
    median_income: Optional[int]
    poverty_rate: Optional[float]
    unemployment_rate: Optional[float]
    median_age: Optional[float]
    disability_rate: Optional[float]
    no_vehicle_rate: Optional[float]
    no_insurance_rate: Optional[float]
    elderly_rate: Optional[float]  # 65+
    single_parent_rate: Optional[float]
    limited_english_rate: Optional[float]
    
    # Derived vulnerability metrics
    social_vulnerability_index: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'fips': self.fips,
            'county_name': self.county_name,
            'state': self.state,
            'population': self.population,
            'median_income': self.median_income,
            'poverty_rate': self.poverty_rate,
            'unemployment_rate': self.unemployment_rate,
            'median_age': self.median_age,
            'disability_rate': self.disability_rate,
            'no_vehicle_rate': self.no_vehicle_rate,
            'no_insurance_rate': self.no_insurance_rate,
            'elderly_rate': self.elderly_rate,
            'single_parent_rate': self.single_parent_rate,
            'limited_english_rate': self.limited_english_rate,
            'social_vulnerability_index': self.social_vulnerability_index
        }


@dataclass
class SVIComponents:
    """Social Vulnerability Index components"""
    socioeconomic: float  # Poverty, unemployment, income
    household_comp: float  # Age, single parent, disability
    minority_status: float  # Race, ethnicity, language
    housing_transport: float  # Housing type, vehicle access
    
    def overall_svi(self) -> float:
        """Calculate overall SVI (0-1, higher = more vulnerable)"""
        return (self.socioeconomic + self.household_comp + 
                self.minority_status + self.housing_transport) / 4


class AsyncCensusClient:
    """
    Async Census ACS API Client
    Features: Batch requests, field selection, derived metrics, SVI calculation
    
    Usage:
        async with AsyncCensusClient(api_key="your_key") as client:
            profile = await client.get_county_profile("29189")
    """
    
    BASE_URL = "https://api.census.gov/data/2022/acs/acs5"
    
    # ACS variable mappings
    VARIABLES = {
        # Population
        "population": "B01003_001E",
        "median_age": "B01002_001E",
        "elderly_pop": "B09020_001E",  # 65+
        
        # Income & Poverty
        "median_income": "B19013_001E",
        "poverty_count": "B17001_002E",
        
        # Employment
        "unemployed": "B23027_002E",
        "labor_force": "B23027_001E",
        
        # Disability
        "disability_count": "B18101_001E",
        
        # Transportation
        "no_vehicle": "B08201_002E",
        "households": "B08201_001E",
        
        # Insurance
        "no_insurance": "B27001_002E",
        "total_insurance": "B27001_001E",
        
        # Household composition
        "single_parent": "B11012_001E",
        "total_households": "B11012_010E",
        
        # Language
        "limited_english": "B16005_007E",
        "total_language": "B16005_001E",
        
        # Race/Ethnicity (for minority status)
        "white_alone": "B02001_002E",
        "total_race": "B02001_001E",
        
        # Housing
        "renter_occupied": "B25003_003E",
        "total_housing": "B25003_001E",
        "mobile_homes": "B25024_010E",
        "crowded_housing": "B25014_005E",  # >1 person per room
    }
    
    def __init__(self, api_key: Optional[str] = None, gateway=None):
        self.api_key = api_key
        self.gateway = gateway
        self._session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, tuple] = {}  # (profile, timestamp)
    
    async def __aenter__(self):
        if not self.gateway or not GATEWAY_AVAILABLE:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
    
    async def get_county_profile(self, fips: str, use_cache: bool = True) -> Optional[CensusProfile]:
        """
        Get demographic profile for single county
        
        Args:
            fips: 5-digit county FIPS code
            use_cache: Whether to use cached data
        """
        profiles = await self.get_county_profiles([fips], use_cache=use_cache)
        return profiles.get(fips)
    
    async def get_county_profiles(
        self,
        fips_list: List[str],
        batch_size: int = 50,
        use_cache: bool = True
    ) -> Dict[str, CensusProfile]:
        """
        Get profiles for multiple counties with batching
        
        Args:
            fips_list: List of 5-digit FIPS codes
            batch_size: Number of counties per request
            use_cache: Whether to use cached data
        """
        # Check cache first
        if use_cache:
            cached_profiles = {}
            uncached_fips = []
            
            for fips in fips_list:
                if fips in self._cache:
                    profile, timestamp = self._cache[fips]
                    # Cache valid for 24 hours
                    if (datetime.utcnow().timestamp() - timestamp) < 86400:
                        cached_profiles[fips] = profile
                        continue
                uncached_fips.append(fips)
            
            if not uncached_fips:
                return cached_profiles
            
            fips_list = uncached_fips
        
        # Split into batches
        batches = [
            fips_list[i:i + batch_size]
            for i in range(0, len(fips_list), batch_size)
        ]
        
        # Process batches concurrently
        tasks = [self._fetch_batch(batch) for batch in batches]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        profiles = {}
        for result in batch_results:
            if isinstance(result, Exception):
                print(f"Batch error: {result}")
                continue
            profiles.update(result)
        
        # Update cache
        if use_cache:
            for fips, profile in profiles.items():
                self._cache[fips] = (profile, datetime.utcnow().timestamp())
            profiles.update(cached_profiles)
        
        return profiles
    
    async def _fetch_batch(self, fips_list: List[str]) -> Dict[str, CensusProfile]:
        """Fetch a batch of counties"""
        # Build variable list
        vars_str = ",".join(self.VARIABLES.values())
        
        # Build FIPS filter - separate state and county
        county_filters = []
        for fips in fips_list:
            state_fips = fips[:2]
            county_fips = fips[2:]
            county_filters.append(f"{state_fips}:{county_fips}")
        
        # Use "in" parameter for multiple states
        unique_states = list(set(f[:2] for f in fips_list))
        
        params = {
            "get": f"NAME,{vars_str}",
            "for": f"county:*",
            "in": f"state:{','.join(unique_states)}"
        }
        
        if self.api_key:
            params["key"] = self.api_key
        
        try:
            if self.gateway and GATEWAY_AVAILABLE:
                result = await self.gateway.request(
                    service="census",
                    method="GET",
                    url=self.BASE_URL,
                    params=params,
                    cache_ttl=86400,  # 24 hour cache for census data
                    rate_limit_key="census"
                )
                data = result["data"]
            else:
                async with self._session.get(self.BASE_URL, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
            
            return self._parse_response(data, fips_list)
            
        except Exception as e:
            print(f"Error fetching census batch: {e}")
            return {}
    
    def _parse_response(
        self,
        data: List[List],
        requested_fips: List[str]
    ) -> Dict[str, CensusProfile]:
        """Parse Census API response into profiles"""
        if not data or len(data) < 2:
            return {}
        
        headers = data[0]
        profiles = {}
        
        for row in data[1:]:
            values = dict(zip(headers, row))
            
            # Extract FIPS
            state_fips = values.get("state", "").zfill(2)
            county_fips = values.get("county", "").zfill(3)
            fips = f"{state_fips}{county_fips}"
            
            # Skip if not in requested list
            if fips not in requested_fips:
                continue
            
            # Parse name
            name_parts = values.get("NAME", "").split(", ")
            county_name = name_parts[0].replace(" County", "").strip() if name_parts else ""
            state = name_parts[1] if len(name_parts) > 1 else ""
            
            # Parse population
            population = self._parse_int(values.get(self.VARIABLES["population"]))
            if not population:
                continue
            
            # Calculate rates
            poverty_count = self._parse_int(values.get(self.VARIABLES["poverty_count"]))
            unemployed = self._parse_int(values.get(self.VARIABLES["unemployed"]))
            labor_force = self._parse_int(values.get(self.VARIABLES["labor_force"]))
            households = self._parse_int(values.get(self.VARIABLES["households"]))
            elderly = self._parse_int(values.get(self.VARIABLES["elderly_pop"]))
            no_vehicle = self._parse_int(values.get(self.VARIABLES["no_vehicle"]))
            no_insurance = self._parse_int(values.get(self.VARIABLES["no_insurance"]))
            total_insurance = self._parse_int(values.get(self.VARIABLES["total_insurance"]))
            single_parent = self._parse_int(values.get(self.VARIABLES["single_parent"]))
            total_households = self._parse_int(values.get(self.VARIABLES["total_households"]))
            limited_english = self._parse_int(values.get(self.VARIABLES["limited_english"]))
            total_language = self._parse_int(values.get(self.VARIABLES["total_language"]))
            disability = self._parse_int(values.get(self.VARIABLES["disability_count"]))
            
            profile = CensusProfile(
                fips=fips,
                county_name=county_name,
                state=state,
                population=population,
                median_income=self._parse_int(values.get(self.VARIABLES["median_income"])),
                poverty_rate=(poverty_count / population * 100) if poverty_count else None,
                unemployment_rate=(unemployed / labor_force * 100) if labor_force else None,
                median_age=self._parse_float(values.get(self.VARIABLES["median_age"])),
                disability_rate=(disability / population * 100) if disability else None,
                no_vehicle_rate=(no_vehicle / households * 100) if households else None,
                no_insurance_rate=(no_insurance / total_insurance * 100) if total_insurance else None,
                elderly_rate=(elderly / population * 100) if elderly else None,
                single_parent_rate=(single_parent / total_households * 100) if total_households else None,
                limited_english_rate=(limited_english / total_language * 100) if total_language else None,
            )
            
            # Calculate SVI
            profile.social_vulnerability_index = self._calculate_svi(profile)
            
            profiles[fips] = profile
        
        return profiles
    
    def _parse_int(self, value: str) -> Optional[int]:
        """Safely parse integer"""
        try:
            return int(value) if value and value not in ("null", "", "None") else None
        except (ValueError, TypeError):
            return None
    
    def _parse_float(self, value: str) -> Optional[float]:
        """Safely parse float"""
        try:
            return float(value) if value and value not in ("null", "", "None") else None
        except (ValueError, TypeError):
            return None
    
    def _calculate_svi(self, profile: CensusProfile) -> Optional[float]:
        """
        Calculate Social Vulnerability Index (CDC-style)
        Returns percentile rank (0-1, higher = more vulnerable)
        """
        scores = []
        
        # Socioeconomic status
        if profile.poverty_rate is not None:
            scores.append(min(profile.poverty_rate / 30, 1.0))
        if profile.unemployment_rate is not None:
            scores.append(min(profile.unemployment_rate / 15, 1.0))
        if profile.median_income is not None:
            # Lower income = higher vulnerability
            income_score = max(0, 1 - (profile.median_income / 75000))
            scores.append(income_score)
        
        # Household composition
        if profile.elderly_rate is not None:
            scores.append(min(profile.elderly_rate / 25, 1.0))
        if profile.single_parent_rate is not None:
            scores.append(min(profile.single_parent_rate / 15, 1.0))
        if profile.disability_rate is not None:
            scores.append(min(profile.disability_rate / 20, 1.0))
        
        # Housing/Transportation
        if profile.no_vehicle_rate is not None:
            scores.append(min(profile.no_vehicle_rate / 15, 1.0))
        
        return sum(scores) / len(scores) if scores else None
    
    async def search_counties(
        self,
        query: str,
        state: Optional[str] = None
    ) -> List[CensusProfile]:
        """
        Search counties by name
        
        Args:
            query: Search query (county name)
            state: Optional state filter
        """
        # This would require a pre-loaded county list or separate search API
        # For now, return empty - implement with cached county list
        return []
    
    async def get_state_summary(self, state_fips: str) -> Dict[str, Any]:
        """
        Get summary statistics for a state
        
        Args:
            state_fips: 2-digit state FIPS
        """
        # Fetch all counties in state
        params = {
            "get": f"NAME,{','.join(self.VARIABLES.values())}",
            "for": "county:*",
            "in": f"state:{state_fips}"
        }
        
        if self.api_key:
            params["key"] = self.api_key
        
        try:
            if self.gateway and GATEWAY_AVAILABLE:
                result = await self.gateway.request(
                    service="census",
                    method="GET",
                    url=self.BASE_URL,
                    params=params,
                    cache_ttl=86400
                )
                data = result["data"]
            else:
                async with self._session.get(self.BASE_URL, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
            
            profiles = self._parse_response(data, [])
            
            # Calculate summary
            total_pop = sum(p.population for p in profiles.values())
            avg_poverty = sum(p.poverty_rate or 0 for p in profiles.values()) / len(profiles) if profiles else 0
            avg_svi = sum(p.social_vulnerability_index or 0 for p in profiles.values()) / len(profiles) if profiles else 0
            
            return {
                "total_counties": len(profiles),
                "total_population": total_pop,
                "avg_poverty_rate": avg_poverty,
                "avg_svi": avg_svi,
                "most_vulnerable": sorted(
                    profiles.values(),
                    key=lambda p: p.social_vulnerability_index or 0,
                    reverse=True
                )[:5]
            }
            
        except Exception as e:
            return {"error": str(e)}


# Backward compatibility wrapper
class CensusClientSync:
    """Synchronous wrapper for AsyncCensusClient"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def _run_async(self, coro):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)
    
    def get_county_profile(self, fips: str) -> Optional[CensusProfile]:
        async def _get():
            async with AsyncCensusClient(self.api_key) as client:
                return await client.get_county_profile(fips)
        return self._run_async(_get())


if __name__ == "__main__":
    async def test_client():
        async with AsyncCensusClient() as client:
            # Test single county
            profile = await client.get_county_profile("29189")  # St. Louis County, MO
            if profile:
                print(f"County: {profile.county_name}, {profile.state}")
                print(f"Population: {profile.population:,}")
                print(f"Median Income: ${profile.median_income:,}" if profile.median_income else "Median Income: N/A")
                print(f"Poverty Rate: {profile.poverty_rate:.1f}%" if profile.poverty_rate else "Poverty Rate: N/A")
                print(f"SVI: {profile.social_vulnerability_index:.3f}" if profile.social_vulnerability_index else "SVI: N/A")
            
            # Test batch
            profiles = await client.get_county_profiles(["29189", "29510"])  # St. Louis + St. Louis City
            print(f"\nBatch results: {len(profiles)} counties")
    
    asyncio.run(test_client())
