"""
Temporal Feature Engineering for ResilienceAI
Time-based features for disaster prediction and trend analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from scipy import stats
from sklearn.linear_model import LinearRegression

class TemporalFeatureEngineer:
    """
    Generate temporal features from time-series disaster data.
    """
    
    def __init__(self, reference_year: int = 2025):
        self.reference_year = reference_year
    
    def compute_all_temporal_features(
        self,
        fema_df: pd.DataFrame,
        county_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Compute all temporal features for counties.
        
        Args:
            fema_df: FEMA disaster declarations DataFrame
            county_df: County features DataFrame
            
        Returns:
            County DataFrame with temporal features added
        """
        df = county_df.copy()
        
        # Prepare FEMA data
        fema = self._prepare_fema_data(fema_df)
        
        # Compute features
        print("Computing temporal features...")
        
        # Trend features
        df = self._compute_trend_features(df, fema)
        
        # Recency features
        df = self._compute_recency_features(df, fema)
        
        # Seasonality features
        df = self._compute_seasonality_features(df, fema)
        
        # Interarrival features
        df = self._compute_interarrival_features(df, fema)
        
        # Acceleration features
        df = self._compute_acceleration_features(df, fema)
        
        print(f"  Added {len([c for c in df.columns if 'temp_' in c or 'trend_' in c or 'accel_' in c])} temporal features")
        
        return df
    
    def _prepare_fema_data(self, fema_df: pd.DataFrame) -> pd.DataFrame:
        """Prepare FEMA data for temporal analysis."""
        fema = fema_df.copy()
        
        # Create FIPS if not exists
        if 'fips' not in fema.columns:
            fema['fips'] = (
                fema['fipsStateCode'].astype(str).str.zfill(2) +
                fema['fipsCountyCode'].astype(str).str.zfill(3)
            )
        
        # Parse dates
        fema['declarationDate'] = pd.to_datetime(fema['declarationDate'], errors='coerce')
        fema['year'] = fema['declarationDate'].dt.year
        fema['month'] = fema['declarationDate'].dt.month
        
        return fema
    
    def _compute_trend_features(
        self,
        df: pd.DataFrame,
        fema: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute disaster trend features."""
        
        def compute_trend(county_fips: str) -> Tuple[float, float]:
            """Compute trend slope and R² for a county."""
            county_disasters = fema[fema['fips'] == county_fips]
            
            if len(county_disasters) < 3:
                return 0.0, 0.0
            
            # Group by year
            yearly = county_disasters.groupby('year').size().reset_index(name='count')
            
            # Linear regression
            X = yearly['year'].values.reshape(-1, 1)
            y = yearly['count'].values
            
            model = LinearRegression().fit(X, y)
            slope = model.coef_[0]
            r2 = model.score(X, y)
            
            return slope, r2
        
        # Compute for each county
        trends = []
        for fips in df['fips']:
            slope, r2 = compute_trend(fips)
            trends.append({'fips': fips, 'trend_slope': slope, 'trend_r2': r2})
        
        trends_df = pd.DataFrame(trends)
        df = df.merge(trends_df, on='fips', how='left')
        
        return df
    
    def _compute_recency_features(
        self,
        df: pd.DataFrame,
        fema: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute recency-weighted disaster features."""
        
        # Years to consider
        recent_years = [self.reference_year - i for i in range(5)]
        
        # Compute recency-weighted count
        def compute_recency_score(county_fips: str) -> float:
            county_disasters = fema[fema['fips'] == county_fips]
            
            score = 0.0
            for i, year in enumerate(reversed(recent_years)):
                weight = 0.5 + (i * 0.125)  # [0.5, 0.625, 0.75, 0.875, 1.0]
                count = len(county_disasters[county_disasters['year'] == year])
                score += count * weight
            
            return score
        
        df['recency_weighted_disasters'] = df['fips'].apply(compute_recency_score)
        
        # Years since last disaster
        def years_since_last(county_fips: str) -> int:
            county_disasters = fema[fema['fips'] == county_fips]
            if len(county_disasters) == 0:
                return 999
            last_year = county_disasters['year'].max()
            return self.reference_year - last_year
        
        df['years_since_last_disaster'] = df['fips'].apply(years_since_last)
        
        return df
    
    def _compute_seasonality_features(
        self,
        df: pd.DataFrame,
        fema: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute disaster seasonality features."""
        
        # Peak disaster month
        def get_peak_month(county_fips: str) -> int:
            county_disasters = fema[fema['fips'] == county_fips]
            if len(county_disasters) < 3:
                return 0
            
            monthly = county_disasters.groupby('month').size()
            return monthly.idxmax() if len(monthly) > 0 else 0
        
        df['disaster_peak_month'] = df['fips'].apply(get_peak_month)
        
        # Seasonality strength (coefficient of variation)
        def get_seasonality_strength(county_fips: str) -> float:
            county_disasters = fema[fema['fips'] == county_fips]
            if len(county_disasters) < 12:
                return 0.0
            
            monthly = county_disasters.groupby('month').size()
            if monthly.mean() > 0:
                return monthly.std() / monthly.mean()
            return 0.0
        
        df['disaster_seasonality_cv'] = df['fips'].apply(get_seasonality_strength)
        
        return df
    
    def _compute_interarrival_features(
        self,
        df: pd.DataFrame,
        fema: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute interarrival time features."""
        
        def compute_interarrival_stats(county_fips: str) -> Tuple[float, float]:
            county_disasters = fema[fema['fips'] == county_fips]
            if len(county_disasters) < 2:
                return 999.0, 0.0
            
            # Sort by date
            dates = county_disasters['declarationDate'].sort_values()
            
            # Compute interarrival times in days
            interarrival = (dates.diff().dt.days).dropna()
            
            return interarrival.mean(), interarrival.std()
        
        interarrival_data = []
        for fips in df['fips']:
            mean_ia, std_ia = compute_interarrival_stats(fips)
            interarrival_data.append({
                'fips': fips,
                'interarrival_mean_days': mean_ia,
                'interarrival_std_days': std_ia
            })
        
        interarrival_df = pd.DataFrame(interarrival_data)
        df = df.merge(interarrival_df, on='fips', how='left')
        
        return df
    
    def _compute_acceleration_features(
        self,
        df: pd.DataFrame,
        fema: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute disaster acceleration features."""
        
        # Compare recent 5 years vs previous 5 years
        recent_period = (fema['year'] >= self.reference_year - 4) & (fema['year'] <= self.reference_year)
        prior_period = (fema['year'] >= self.reference_year - 9) & (fema['year'] <= self.reference_year - 5)
        
        recent_counts = fema[recent_period].groupby('fips').size().reset_index(name='disasters_recent_5yr')
        prior_counts = fema[prior_period].groupby('fips').size().reset_index(name='disasters_prior_5yr')
        
        df = df.merge(recent_counts, on='fips', how='left')
        df = df.merge(prior_counts, on='fips', how='left')
        
        df['disasters_recent_5yr'] = df['disasters_recent_5yr'].fillna(0)
        df['disasters_prior_5yr'] = df['disasters_prior_5yr'].fillna(0)
        
        # Acceleration ratio
        df['disaster_5yr_acceleration'] = df['disasters_recent_5yr'] / (df['disasters_prior_5yr'] + 1)
        
        return df


def add_temporal_features(
    county_df: pd.DataFrame,
    fema_df: pd.DataFrame,
    reference_year: int = 2025
) -> pd.DataFrame:
    """
    Convenience function to add all temporal features.
    
    Args:
        county_df: County features DataFrame
        fema_df: FEMA disaster data
        reference_year: Reference year for recency calculations
        
    Returns:
        DataFrame with temporal features added
    """
    engineer = TemporalFeatureEngineer(reference_year=reference_year)
    return engineer.compute_all_temporal_features(fema_df, county_df)
