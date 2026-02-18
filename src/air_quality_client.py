"""
ResilienceAI - EPA AirNow API Client for Air Quality Data
Provides current AQI and forecasts for ZIP codes and counties.

Data Source: EPA AirNow API (https://www.airnowapi.org/)
No API key required for basic usage, but recommended for higher rate limits.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from config import CACHE_DIR


# ── Dataclass Response Types ───────────────────────────────────────────

@dataclass
class AQIDatum:
    """Single AQI observation."""
    aqi: int
    category: str
    pollutant: str
    health_message: str
    date: str
    source: str = "AirNow"

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AQIForecast:
    """AQI forecast for a specific date."""
    date: str
    aqi: int
    category: str
    pollutant: str
    discussion: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


# ── AirNow API Client ──────────────────────────────────────────────────

class AirNowClient:
    """
    EPA AirNow API client for air quality data.
    
    Provides:
    - Current AQI by ZIP code
    - Current AQI by lat/lon
    - AQI forecasts
    - Health recommendations
    
    API Docs: https://docs.airnowapi.org/
    """
    
    BASE_URL = "https://www.airnowapi.org/aq"
    CACHE_DIR = CACHE_DIR / "air_quality"
    CACHE_TTL_HOURS = 1  # AQI data updates hourly
    
    # AQI category mapping with health recommendations
    AQI_CATEGORIES = {
        (0, 50): ("Good", "Air quality is satisfactory, and air pollution poses little or no risk."),
        (51, 100): ("Moderate", "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution."),
        (101, 150): ("Unhealthy for Sensitive Groups", "Members of sensitive groups may experience health effects. The general public is less likely to be affected."),
        (151, 200): ("Unhealthy", "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects."),
        (201, 300): ("Very Unhealthy", "Health alert: The risk of health effects is increased for everyone."),
        (301, 500): ("Hazardous", "Health warning of emergency conditions: everyone is more likely to be affected."),
    }
    
    # Pollutant code mapping
    POLLUTANT_NAMES = {
        "PM2.5": "Fine Particulate Matter",
        "PM10": "Coarse Particulate Matter", 
        "O3": "Ozone",
        "NO2": "Nitrogen Dioxide",
        "SO2": "Sulfur Dioxide",
        "CO": "Carbon Monoxide",
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AirNow client.
        
        Args:
            api_key: Optional EPA AirNow API key (obtain from airnowapi.org)
        """
        self.api_key = api_key or os.getenv("AIRNOW_API_KEY", "")
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate cache key from endpoint and parameters."""
        param_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(f"{endpoint}:{param_str}".encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Retrieve data from cache if not expired."""
        cache_file = self.CACHE_DIR / f"{cache_key}.json"
        if not cache_file.exists():
            return None
        
        # Check cache TTL
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        if file_age > timedelta(hours=self.CACHE_TTL_HOURS):
            return None
        
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save data to cache."""
        cache_file = self.CACHE_DIR / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except IOError:
            pass  # Fail silently on cache write errors
    
    def _get_aqi_category(self, aqi: int) -> tuple:
        """Get category name and health message for AQI value."""
        for (low, high), (category, message) in self.AQI_CATEGORIES.items():
            if low <= aqi <= high:
                return category, message
        return "Unknown", "AQI value out of expected range."
    
    def _make_request(self, endpoint: str, params: Dict) -> Optional[List[Dict]]:
        """Make API request with caching."""
        cache_key = self._get_cache_key(endpoint, params)
        
        # Check cache first
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached.get("data")
        
        # Add API key if available
        if self.api_key:
            params["API_KEY"] = self.api_key
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Handle both single object and list responses
            if isinstance(data, dict):
                data = [data]
            
            # Save to cache
            self._save_to_cache(cache_key, {"data": data, "timestamp": datetime.now().isoformat()})
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"AirNow API request failed: {e}")
            return None
        except json.JSONDecodeError:
            print("AirNow API returned invalid JSON")
            return None
    
    def get_current_aqi(self, zip_code: str) -> Optional[Dict]:
        """
        Get current AQI for a ZIP code.
        
        Args:
            zip_code: 5-digit US ZIP code
            
        Returns:
            Dict with keys: aqi, category, pollutant, health_message, date
            or None if request fails
        """
        if not zip_code or len(zip_code) != 5 or not zip_code.isdigit():
            return {"error": "Invalid ZIP code. Please provide a 5-digit ZIP code."}
        
        params = {
            "zipCode": zip_code,
            "format": "application/json",
            "distance": 25,  # Search radius in miles
        }
        
        data = self._make_request("observation/latLong/current", params)
        
        if data is None:
            return None
        
        if not data:
            return {"error": f"No air quality data available for ZIP code {zip_code}"}
        
        # Find the highest AQI observation (worst air quality)
        worst_observation = max(data, key=lambda x: x.get("AQI", 0))
        
        aqi = worst_observation.get("AQI", 0)
        pollutant_code = worst_observation.get("ParameterName", "Unknown")
        date = worst_observation.get("DateObserved", datetime.now().strftime("%Y-%m-%d"))
        
        category, health_message = self._get_aqi_category(aqi)
        pollutant = self.POLLUTANT_NAMES.get(pollutant_code, pollutant_code)
        
        result = AQIDatum(
            aqi=aqi,
            category=category,
            pollutant=pollutant,
            health_message=health_message,
            date=date
        )
        
        return result.to_dict()
    
    def get_aqi_by_latlon(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Get current AQI for a latitude/longitude coordinate.
        
        Args:
            latitude: Decimal latitude
            longitude: Decimal longitude
            
        Returns:
            Dict with AQI data or None if request fails
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "format": "application/json",
            "distance": 25,
        }
        
        data = self._make_request("observation/latLong/current", params)
        
        if data is None:
            return None
        
        if not data:
            return {"error": f"No air quality data available for coordinates ({latitude}, {longitude})"}
        
        worst_observation = max(data, key=lambda x: x.get("AQI", 0))
        
        aqi = worst_observation.get("AQI", 0)
        pollutant_code = worst_observation.get("ParameterName", "Unknown")
        date = worst_observation.get("DateObserved", datetime.now().strftime("%Y-%m-%d"))
        
        category, health_message = self._get_aqi_category(aqi)
        pollutant = self.POLLUTANT_NAMES.get(pollutant_code, pollutant_code)
        
        return AQIDatum(
            aqi=aqi,
            category=category,
            pollutant=pollutant,
            health_message=health_message,
            date=date
        ).to_dict()
    
    def get_aqi_by_county(self, fips: str) -> Optional[Dict]:
        """
        Get AQI using county FIPS code.
        
        Note: AirNow API doesn't directly support FIPS, so this uses
        the county's centroid coordinates. Requires geocoding lookup.
        
        Args:
            fips: 5-digit county FIPS code
            
        Returns:
            Dict with AQI data or None if request fails
        """
        # Get county centroid from our dataset
        try:
            import pandas as pd
            from config import PROCESSED_DIR
            
            county_file = PROCESSED_DIR / "county_features.csv"
            if not county_file.exists():
                return {"error": "County data not available for FIPS lookup"}
            
            df = pd.read_csv(county_file, dtype={"fips": str})
            match = df[df["fips"] == str(fips)]
            
            if match.empty:
                return {"error": f"County with FIPS {fips} not found"}
            
            county = match.iloc[0]
            lat = county.get("latitude")
            lon = county.get("longitude")
            county_name = county.get("county_name", f"FIPS {fips}")
            
            if pd.isna(lat) or pd.isna(lon):
                return {"error": f"Coordinates not available for {county_name}"}
            
            result = self.get_aqi_by_latlon(float(lat), float(lon))
            if result:
                result["county_name"] = county_name
                result["fips"] = fips
            return result
            
        except Exception as e:
            return {"error": f"Failed to lookup county coordinates: {str(e)}"}
    
    def get_forecast(self, zip_code: str, date: Optional[str] = None) -> List[Dict]:
        """
        Get AQI forecast for a ZIP code.
        
        Args:
            zip_code: 5-digit US ZIP code
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            List of forecast dicts with keys: date, aqi, category, pollutant
        """
        if not zip_code or len(zip_code) != 5 or not zip_code.isdigit():
            return [{"error": "Invalid ZIP code. Please provide a 5-digit ZIP code."}]
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        params = {
            "zipCode": zip_code,
            "date": date,
            "format": "application/json",
            "distance": 25,
        }
        
        data = self._make_request("forecast/zipCode", params)
        
        if data is None:
            return []
        
        if not data:
            return [{"message": f"No forecast available for ZIP code {zip_code}"}]
        
        forecasts = []
        for item in data:
            aqi = item.get("AQI", 0)
            category, _ = self._get_aqi_category(aqi)
            pollutant_code = item.get("ParameterName", "Unknown")
            
            forecast = AQIForecast(
                date=item.get("DateForecast", date),
                aqi=aqi,
                category=category,
                pollutant=self.POLLUTANT_NAMES.get(pollutant_code, pollutant_code),
                discussion=item.get("Discussion", None)
            )
            forecasts.append(forecast.to_dict())
        
        return forecasts
    
    def get_health_recommendations(self, aqi: int) -> Dict[str, str]:
        """
        Get health recommendations for a given AQI value.
        
        Args:
            aqi: Air Quality Index value (0-500)
            
        Returns:
            Dict with recommendations for different groups
        """
        category, general_message = self._get_aqi_category(aqi)
        
        recommendations = {
            "Good": {
                "general": "Enjoy your outdoor activities.",
                "sensitive": "No precautions needed.",
                "activity": "Perfect conditions for all outdoor activities."
            },
            "Moderate": {
                "general": "Air quality is acceptable for most people.",
                "sensitive": "If you are sensitive to air pollution, consider reducing prolonged outdoor exertion.",
                "activity": "Most outdoor activities are fine. Sensitive individuals should watch for symptoms."
            },
            "Unhealthy for Sensitive Groups": {
                "general": "Reduce prolonged outdoor exertion if you have respiratory issues.",
                "sensitive": "People with heart or lung disease, older adults, and children should reduce prolonged or heavy exertion.",
                "activity": "Consider indoor activities or shorter outdoor sessions."
            },
            "Unhealthy": {
                "general": "Avoid prolonged outdoor exertion. Everyone may begin to experience health effects.",
                "sensitive": "People with heart or lung disease, older adults, and children should avoid prolonged or heavy exertion. Everyone else should reduce prolonged exertion.",
                "activity": "Move activities indoors. If outside, take frequent breaks."
            },
            "Very Unhealthy": {
                "general": "Avoid all outdoor exertion. Health alert for everyone.",
                "sensitive": "Everyone should avoid prolonged or heavy exertion. Sensitive groups should remain indoors.",
                "activity": "All outdoor activities should be moved indoors or postponed."
            },
            "Hazardous": {
                "general": "Emergency conditions. Everyone should avoid all outdoor exertion.",
                "sensitive": "Remain indoors and keep activity levels low. Follow emergency instructions.",
                "activity": "Avoid all outdoor physical activity. Stay indoors with windows closed."
            }
        }
        
        recs = recommendations.get(category, recommendations["Good"])
        
        return {
            "aqi": aqi,
            "category": category,
            "general_message": general_message,
            **recs
        }


# ── Convenience Functions ──────────────────────────────────────────────

def get_current_aqi(zip_code: str) -> Optional[Dict]:
    """Convenience function to get current AQI."""
    return AirNowClient().get_current_aqi(zip_code)


def get_air_quality_summary(zip_code: str) -> Dict:
    """
    Get comprehensive air quality summary including current AQI and forecast.
    
    Args:
        zip_code: 5-digit US ZIP code
        
    Returns:
        Dict with current AQI, forecast, and health recommendations
    """
    client = AirNowClient()
    
    current = client.get_current_aqi(zip_code)
    forecast = client.get_forecast(zip_code)
    
    result = {
        "zip_code": zip_code,
        "current": current,
        "forecast": forecast[:3] if forecast else [],  # Next 3 days
    }
    
    if current and "aqi" in current:
        result["health_recommendations"] = client.get_health_recommendations(current["aqi"])
    
    return result


# ── Module Test ────────────────────────────────────────────────────────

if __name__ == "__main__":
    client = AirNowClient()
    
    # Test with a sample ZIP code
    test_zip = "20500"  # Washington DC
    
    print(f"Testing AirNow API with ZIP code: {test_zip}")
    print("=" * 60)
    
    # Current AQI
    current = client.get_current_aqi(test_zip)
    if current:
        print(f"\nCurrent AQI for {test_zip}:")
        print(f"  AQI: {current.get('aqi')}")
        print(f"  Category: {current.get('category')}")
        print(f"  Primary Pollutant: {current.get('pollutant')}")
        print(f"  Health Message: {current.get('health_message')}")
    else:
        print("Failed to retrieve current AQI")
    
    # Forecast
    forecast = client.get_forecast(test_zip)
    if forecast:
        print(f"\nForecast for {test_zip}:")
        for day in forecast[:3]:
            print(f"  {day.get('date')}: AQI {day.get('aqi')} ({day.get('category')})")
    
    # Health recommendations
    if current and "aqi" in current:
        print(f"\nHealth Recommendations:")
        recs = client.get_health_recommendations(current["aqi"])
        print(f"  General: {recs.get('general')}")
        print(f"  Sensitive Groups: {recs.get('sensitive')}")
