"""
Geospatial Feature Engineering for ResilienceAI
Advanced spatial features for disaster vulnerability analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from scipy.spatial import cKDTree
from scipy.spatial.distance import pdist, squareform

class GeospatialFeatureEngineer:
    """
    Generate advanced geospatial features for county analysis.
    """
    
    def __init__(self, max_distance_km: float = 100.0):
        self.max_distance_km = max_distance_km
    
    def compute_all_geospatial_features(
        self,
        county_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Compute all geospatial features for counties.
        
        Args:
            county_df: County features DataFrame with lat/lon
            
        Returns:
            County DataFrame with geospatial features added
        """
        df = county_df.copy()
        
        print("Computing geospatial features...")
        
        # Spatial clustering features
        df = self._compute_spatial_clustering(df)
        
        # Network connectivity features
        df = self._compute_network_features(df)
        
        # Accessibility features
        df = self._compute_accessibility_features(df)
        
        # Regional context features
        df = self._compute_regional_context(df)
        
        print(f"  Added {len([c for c in df.columns if 'geo_' in c or 'spatial_' in c or 'moran' in c])} geospatial features")
        
        return df
    
    def _compute_spatial_clustering(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute spatial autocorrelation features (Moran's I)."""
        
        # Get coordinates
        coords = df[['latitude', 'longitude']].values
        n = len(coords)
        
        # Build distance matrix (in km)
        dist_matrix = self._haversine_distance_matrix(coords)
        
        # Create weight matrix (inverse distance)
        weights = np.where(
            (dist_matrix > 0) & (dist_matrix <= self.max_distance_km),
            1 / (dist_matrix + 1),
            0
        )
        np.fill_diagonal(weights, 0)
        
        # Row-standardize weights
        row_sums = weights.sum(axis=1)
        row_sums[row_sums == 0] = 1
        weights = weights / row_sums[:, np.newaxis]
        
        # Compute Moran's I for risk_score
        if 'risk_score' in df.columns:
            df['spatial_moran_risk'] = self._local_morans_i(
                df['risk_score'].values, weights
            )
        
        # Compute Moran's I for vulnerability_index
        if 'vulnerability_index' in df.columns:
            df['spatial_moran_vulnerability'] = self._local_morans_i(
                df['vulnerability_index'].values, weights
            )
        
        # Compute Moran's I for disaster_count
        if 'disaster_count' in df.columns:
            df['spatial_moran_disaster'] = self._local_morans_i(
                df['disaster_count'].fillna(0).values, weights
            )
        
        return df
    
    def _compute_network_features(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute network connectivity features."""
        
        # Get coordinates
        coords = df[['latitude', 'longitude']].values
        
        # Build KD-tree for efficient neighbor queries
        coords_rad = np.radians(coords)
        tree = cKDTree(coords_rad)
        
        # Find neighbors within max_distance_km
        radius_rad = self.max_distance_km / 6371.0
        neighbors = tree.query_ball_tree(tree, r=radius_rad)
        
        # Network degree (number of neighbors)
        df['geo_network_degree'] = [len(n) - 1 for n in neighbors]  # Exclude self
        
        # Network density (connected counties / total possible)
        n = len(df)
        max_possible = n - 1
        df['geo_network_density'] = df['geo_network_degree'] / max_possible
        
        # Average distance to neighbors
        avg_neighbor_distances = []
        for i, neighbor_list in enumerate(neighbors):
            if len(neighbor_list) <= 1:
                avg_neighbor_distances.append(self.max_distance_km)
            else:
                # Get distances to neighbors (excluding self)
                neighbor_dists = []
                for j in neighbor_list:
                    if i != j:
                        dist_km = self._haversine_km(
                            coords[i][0], coords[i][1],
                            coords[j][0], coords[j][1]
                        )
                        neighbor_dists.append(dist_km)
                avg_neighbor_distances.append(np.mean(neighbor_dists) if neighbor_dists else self.max_distance_km)
        
        df['geo_avg_neighbor_distance_km'] = avg_neighbor_distances
        
        return df
    
    def _compute_accessibility_features(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute accessibility and reachability features."""
        
        # Healthcare accessibility score (gravity model)
        if 'count_hospitals_50km' in df.columns and 'dist_nearest_hospitals_km' in df.columns:
            # Gravity model: sum of (capacity / distance^2)
            df['geo_healthcare_accessibility'] = (
                df['count_hospitals_50km'] / (df['dist_nearest_hospitals_km'] ** 2 + 1)
            )
        
        # Emergency response time estimate
        if 'dist_nearest_ems_stations_km' in df.columns:
            # Assume average ambulance speed of 60 km/h
            df['geo_estimated_response_time_min'] = (
                df['dist_nearest_ems_stations_km'] / 60 * 60
            )
        
        # Multi-facility accessibility
        facility_cols = [c for c in df.columns if c.startswith('count_') and c.endswith('_50km')]
        if facility_cols:
            df['geo_total_facilities_50km'] = df[facility_cols].sum(axis=1)
        
        # Facility diversity (number of different facility types)
        df['geo_facility_diversity'] = len(facility_cols) if facility_cols else 0
        
        return df
    
    def _compute_regional_context(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute regional context features."""
        
        # State-level aggregation
        if 'state_fips' not in df.columns:
            df['state_fips'] = df['fips'].str[:2]
        
        # Regional risk context
        if 'risk_score' in df.columns:
            state_risk_stats = df.groupby('state_fips')['risk_score'].agg(['mean', 'std']).reset_index()
            state_risk_stats.columns = ['state_fips', 'state_risk_mean', 'state_risk_std']
            df = df.merge(state_risk_stats, on='state_fips', how='left')
            
            # County vs state average
            df['geo_risk_vs_state_avg'] = df['risk_score'] - df['state_risk_mean']
        
        # Regional vulnerability context
        if 'vulnerability_index' in df.columns:
            state_vuln_stats = df.groupby('state_fips')['vulnerability_index'].agg(['mean', 'std']).reset_index()
            state_vuln_stats.columns = ['state_fips', 'state_vuln_mean', 'state_vuln_std']
            df = df.merge(state_vuln_stats, on='state_fips', how='left')
            
            # County vs state average
            df['geo_vuln_vs_state_avg'] = df['vulnerability_index'] - df['state_vuln_mean']
        
        # Population density proxy (if population and area available)
        if 'total_population' in df.columns:
            # Use network degree as proxy for area/density
            if 'geo_network_degree' in df.columns:
                df['geo_population_density_proxy'] = (
                    df['total_population'] / (df['geo_network_degree'] + 1)
                )
        
        return df
    
    def _haversine_km(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate haversine distance between two points in km."""
        R = 6371.0
        lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
        lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c
    
    def _haversine_distance_matrix(self, coords: np.ndarray) -> np.ndarray:
        """Compute haversine distance matrix for coordinates."""
        n = len(coords)
        dist_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                dist = self._haversine_km(
                    coords[i][0], coords[i][1],
                    coords[j][0], coords[j][1]
                )
                dist_matrix[i][j] = dist
                dist_matrix[j][i] = dist
        
        return dist_matrix
    
    def _local_morans_i(
        self,
        values: np.ndarray,
        weights: np.ndarray
    ) -> np.ndarray:
        """
        Compute local Moran's I for spatial autocorrelation.
        
        Formula: I_i = (x_i - x̄) * Σ w_ij (x_j - x̄)
        """
        # Standardize values
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        if std_val == 0:
            return np.zeros_like(values)
        
        z = (values - mean_val) / std_val
        
        # Compute local Moran's I
        local_moran = z * (weights @ z)
        
        return local_moran


def add_geospatial_features(
    county_df: pd.DataFrame,
    max_distance_km: float = 100.0
) -> pd.DataFrame:
    """
    Convenience function to add all geospatial features.
    
    Args:
        county_df: County features DataFrame
        max_distance_km: Maximum distance for neighbor analysis
        
    Returns:
        DataFrame with geospatial features added
    """
    engineer = GeospatialFeatureEngineer(max_distance_km=max_distance_km)
    return engineer.compute_all_geospatial_features(county_df)
