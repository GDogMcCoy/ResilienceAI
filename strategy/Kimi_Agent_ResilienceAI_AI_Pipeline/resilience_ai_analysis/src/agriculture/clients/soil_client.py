"""
NRCS Soil Survey Client for ResilienceAI
Provides soil quality and property data
"""
import requests
from typing import Dict, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SoilProperties:
    """Soil properties for a location"""
    mukey: str
    musym: str
    muname: str
    aws100: Optional[float] = None  # Available water storage 0-100cm
    ph1to1h2o: Optional[float] = None  # pH in water
    claytotal: Optional[float] = None
    silttotal: Optional[float] = None
    sandtotal: Optional[float] = None
    om: Optional[float] = None  # Organic matter %
    cec: Optional[float] = None  # Cation exchange capacity


class NRCSSoilClient:
    """Client for NRCS Soil Survey Geographic Database (SSURGO)"""
    
    BASE_URL = "https://sdmdataaccess.nrcs.usda.gov"
    
    def __init__(self):
        self.session = requests.Session()
        
    def get_soil_properties_by_coords(self, lat: float, lon: float) -> Optional[SoilProperties]:
        """Get soil properties for a specific coordinate"""
        query = f"""
        SELECT mu.mukey, mu.musym, mu.muname, c.aws100, c.ph1to1h2o,
               c.claytotal, c.silttotal, c.sandtotal, c.om, c.cec
        FROM mapunit mu
        JOIN component c ON mu.mukey = c.mukey
        WHERE mu.mukey IN (
            SELECT mukey FROM SDA_Get_Mukey_from_intersection_with_WktWgs84(
                'POINT({lon} {lat})'
            )
        )
        AND c.comppct_r = (SELECT MAX(comppct_r) FROM component WHERE mukey = mu.mukey)
        """
        
        try:
            response = self.session.post(
                f"{self.BASE_URL}/Tabular/SDMTabularService/post.rest",
                json={"query": query, "format": "json"},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('Table') and len(data['Table']) > 0:
                row = data['Table'][0]
                return SoilProperties(
                    mukey=str(row.get('mukey', '')),
                    musym=str(row.get('musym', '')),
                    muname=str(row.get('muname', '')),
                    aws100=self._parse_float(row.get('aws100')),
                    ph1to1h2o=self._parse_float(row.get('ph1to1h2o')),
                    claytotal=self._parse_float(row.get('claytotal')),
                    silttotal=self._parse_float(row.get('silttotal')),
                    sandtotal=self._parse_float(row.get('sandtotal')),
                    om=self._parse_float(row.get('om')),
                    cec=self._parse_float(row.get('cec'))
                )
            return None
        except Exception as e:
            logger.error(f"Error fetching soil data: {e}")
            return None
    
    def calculate_soil_quality_index(self, properties: SoilProperties) -> float:
        """Calculate a soil quality index (0-100)"""
        score = 0
        
        # Water storage (0-30 points)
        if properties.aws100:
            if properties.aws100 >= 25: score += 30
            elif properties.aws100 >= 20: score += 25
            elif properties.aws100 >= 15: score += 20
            elif properties.aws100 >= 10: score += 15
            else: score += 10
        
        # pH (0-20 points) - optimal around 6.5
        if properties.ph1to1h2o:
            ph_diff = abs(properties.ph1to1h2o - 6.5)
            if ph_diff <= 0.5: score += 20
            elif ph_diff <= 1.0: score += 15
            elif ph_diff <= 1.5: score += 10
            else: score += 5
        
        # Organic matter (0-25 points)
        if properties.om:
            if properties.om >= 5: score += 25
            elif properties.om >= 3: score += 20
            elif properties.om >= 2: score += 15
            elif properties.om >= 1: score += 10
            else: score += 5
        
        # Texture balance (0-25 points)
        if all([properties.claytotal, properties.silttotal, properties.sandtotal]):
            clay_score = max(0, 25 - abs(properties.claytotal - 20))
            silt_score = max(0, 25 - abs(properties.silttotal - 40))
            sand_score = max(0, 25 - abs(properties.sandtotal - 40))
            score += (clay_score + silt_score + sand_score) / 3
        
        return min(100, score)
    
    def _parse_float(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
