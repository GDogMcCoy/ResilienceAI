"""
ResilienceAI Infrastructure Analysis - Gap Identification
Systematic infrastructure coverage gap identification and prioritization
"""

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class GapSeverity(str, Enum):
    """Severity levels for coverage gaps"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CoverageGap:
    """Represents an infrastructure coverage gap"""
    location_lat: float
    location_lon: float
    county_fips: str
    gap_type: str
    severity: GapSeverity
    nearest_facility_distance_km: float
    nearest_facility_id: Optional[str]
    population_affected: int
    benchmark_distance_km: float
    recommended_facilities: int
    priority_score: float


class GapIdentifier:
    """
    Systematic infrastructure gap identification using:
    - Population-weighted coverage analysis
    - Benchmark comparison
    - Multi-criteria prioritization
    """
    
    # Coverage benchmarks by facility type (km)
    DEFAULT_BENCHMARKS = {
        'hospitals': 25,        # 25km for hospitals
        'hospital': 25,
        'fire_stations': 15,    # 15km for fire stations
        'fire_station': 15,
        'ems_stations': 20,     # 20km for EMS
        'ems_station': 20,
        'nursing_homes': 30,    # 30km for nursing homes
        'nursing_home': 30,
        'urgent_care': 15,      # 15km for urgent care
        'clinic': 20,           # 20km for clinics
        'pharmacy': 10,         # 10km for pharmacies
        'shelter': 25,          # 25km for emergency shelters
    }
    
    def __init__(self, benchmarks: Optional[Dict[str, float]] = None):
        self.benchmarks = benchmarks or self.DEFAULT_BENCHMARKS
        self.facility_trees: Dict[str, cKDTree] = {}
        self.facility_data: Dict[str, pd.DataFrame] = {}
        
    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate haversine distance in kilometers"""
        R = 6371.0
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        return R * 2 * np.arcsin(np.sqrt(a))
    
    def add_facility_type(self, facility_type: str, 
                          facilities_df: pd.DataFrame) -> None:
        """Add facility type for gap analysis"""
        clean_df = facilities_df.dropna(subset=['latitude', 'longitude']).copy()
        
        if len(clean_df) > 0:
            coords = np.radians(clean_df[['latitude', 'longitude']].values)
            self.facility_trees[facility_type] = cKDTree(coords)
            self.facility_data[facility_type] = clean_df
            print(f"  Added {len(clean_df)} {facility_type} to gap analysis")
    
    def identify_gaps(self, county_df: pd.DataFrame,
                      population_col: str = 'population',
                      min_population: int = 1000,
                      facility_types: Optional[List[str]] = None) -> List[CoverageGap]:
        """
        Identify coverage gaps for all facility types
        
        Args:
            county_df: DataFrame with county data (must include latitude, longitude)
            population_col: Column name for population
            min_population: Minimum population to consider
            facility_types: List of facility types to check (default: all registered)
            
        Returns:
            List of CoverageGap objects
        """
        gaps = []
        
        types_to_check = facility_types or list(self.facility_trees.keys())
        
        for _, county in county_df.iterrows():
            pop = county.get(population_col, 0)
            if pop < min_population:
                continue
            
            # Check if county has required columns
            if 'latitude' not in county or 'longitude' not in county:
                continue
                
            for facility_type in types_to_check:
                if facility_type not in self.facility_trees:
                    continue
                
                gap = self._analyze_coverage_gap(
                    county, facility_type, population_col
                )
                
                if gap:  # Only add if there's an actual gap
                    gaps.append(gap)
        
        # Sort by priority score (descending)
        gaps.sort(key=lambda g: g.priority_score, reverse=True)
        return gaps
    
    def _analyze_coverage_gap(self, county: pd.Series,
                              facility_type: str,
                              population_col: str) -> Optional[CoverageGap]:
        """Analyze coverage gap for a specific location and facility type"""
        
        lat, lon = county['latitude'], county['longitude']
        county_coords = np.radians([[lat, lon]])
        
        tree = self.facility_trees[facility_type]
        
        # Find nearest facility
        dist_rad, idx = tree.query(county_coords, k=1)
        dist_km = dist_rad[0][0] * 6371.0
        
        # Get benchmark for this facility type
        benchmark_km = self.benchmarks.get(facility_type, 25)
        
        # If within benchmark, no gap
        if dist_km <= benchmark_km:
            return None
        
        # Get nearest facility ID
        nearest_id = None
        if idx[0][0] < len(self.facility_data[facility_type]):
            nearest_id = str(self.facility_data[facility_type].iloc[idx[0][0]].get('ID', 
                             self.facility_data[facility_type].iloc[idx[0][0]].get('OBJECTID', 
                             idx[0][0])))
        
        # Determine severity
        severity = self._determine_severity(dist_km, benchmark_km)
        
        # Calculate priority score
        population = county.get(population_col, 0)
        priority_score = self._calculate_priority_score(
            dist_km, benchmark_km, population, severity
        )
        
        # Recommend number of new facilities
        recommended = self._recommend_facilities(dist_km, benchmark_km, population)
        
        return CoverageGap(
            location_lat=lat,
            location_lon=lon,
            county_fips=str(county.get('fips', county.get('COUNTYFP', ''))),
            gap_type=facility_type,
            severity=severity,
            nearest_facility_distance_km=round(dist_km, 2),
            nearest_facility_id=nearest_id,
            population_affected=int(population),
            benchmark_distance_km=benchmark_km,
            recommended_facilities=recommended,
            priority_score=round(priority_score, 4)
        )
    
    def _determine_severity(self, distance_km: float, 
                           benchmark_km: float) -> GapSeverity:
        """Determine gap severity based on distance vs benchmark"""
        if benchmark_km <= 0:
            return GapSeverity.CRITICAL
        
        ratio = distance_km / benchmark_km
        
        if ratio > 3 or distance_km > 100:
            return GapSeverity.CRITICAL
        elif ratio > 2:
            return GapSeverity.HIGH
        elif ratio > 1.5:
            return GapSeverity.MEDIUM
        else:
            return GapSeverity.LOW
    
    def _calculate_priority_score(self, distance_km: float,
                                  benchmark_km: float,
                                  population: int,
                                  severity: GapSeverity) -> float:
        """
        Calculate priority score for gap remediation
        Higher score = higher priority
        """
        # Distance factor (further = higher priority)
        distance_factor = min(distance_km / max(benchmark_km, 1), 5)
        
        # Population factor (more people = higher priority)
        population_factor = np.log1p(population) / 10
        
        # Severity multiplier
        severity_multipliers = {
            GapSeverity.CRITICAL: 2.5,
            GapSeverity.HIGH: 1.8,
            GapSeverity.MEDIUM: 1.3,
            GapSeverity.LOW: 1.0
        }
        severity_mult = severity_multipliers.get(severity, 1.0)
        
        return distance_factor * population_factor * severity_mult
    
    def _recommend_facilities(self, distance_km: float,
                             benchmark_km: float,
                             population: int) -> int:
        """Recommend number of new facilities needed"""
        if distance_km <= benchmark_km:
            return 0
        
        # Base recommendation on coverage area ratio
        coverage_area = np.pi * (benchmark_km ** 2)
        uncovered_area = np.pi * ((distance_km * 0.8) ** 2) - coverage_area
        
        if uncovered_area <= 0:
            return 1
        
        # Population density factor
        facilities_needed = max(1, int(uncovered_area / (coverage_area * 2)))
        
        # Cap based on population (1 facility per 10K people max)
        max_facilities = max(1, int(population / 10000))
        
        return min(facilities_needed, max_facilities)
    
    def generate_gap_report(self, gaps: List[CoverageGap]) -> pd.DataFrame:
        """Generate structured gap report as DataFrame"""
        if not gaps:
            return pd.DataFrame()
        
        report_data = []
        for gap in gaps:
            report_data.append({
                'county_fips': gap.county_fips,
                'latitude': gap.location_lat,
                'longitude': gap.location_lon,
                'facility_type': gap.gap_type,
                'severity': gap.severity.value,
                'nearest_facility_km': gap.nearest_facility_distance_km,
                'population_affected': gap.population_affected,
                'benchmark_km': gap.benchmark_distance_km,
                'facilities_needed': gap.recommended_facilities,
                'priority_score': gap.priority_score
            })
        
        return pd.DataFrame(report_data)
    
    def get_summary_statistics(self, gaps: List[CoverageGap]) -> Dict:
        """Generate summary statistics for gaps"""
        if not gaps:
            return {
                'total_gaps': 0,
                'by_severity': {},
                'by_type': {},
                'total_population_affected': 0,
                'avg_distance_to_facility': 0
            }
        
        # Count by severity
        by_severity = {}
        for gap in gaps:
            sev = gap.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        # Count by type
        by_type = {}
        for gap in gaps:
            by_type[gap.gap_type] = by_type.get(gap.gap_type, 0) + 1
        
        # Population affected
        total_population = sum(gap.population_affected for gap in gaps)
        
        # Average distance
        avg_distance = np.mean([gap.nearest_facility_distance_km for gap in gaps])
        
        return {
            'total_gaps': len(gaps),
            'by_severity': by_severity,
            'by_type': by_type,
            'total_population_affected': total_population,
            'avg_distance_to_facility': round(avg_distance, 2),
            'critical_gaps': by_severity.get('critical', 0),
            'high_priority_gaps': by_severity.get('high', 0)
        }
    
    def get_top_priority_gaps(self, gaps: List[CoverageGap], 
                              n: int = 10,
                              min_severity: Optional[GapSeverity] = None) -> List[CoverageGap]:
        """Get top N priority gaps, optionally filtered by minimum severity"""
        filtered = gaps
        
        if min_severity:
            severity_order = ['critical', 'high', 'medium', 'low']
            min_idx = severity_order.index(min_severity.value)
            allowed = severity_order[:min_idx + 1]
            filtered = [g for g in gaps if g.severity.value in allowed]
        
        return filtered[:n]
