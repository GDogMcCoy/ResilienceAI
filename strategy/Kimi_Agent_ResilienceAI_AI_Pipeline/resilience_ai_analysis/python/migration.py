"""
ResilienceAI Data Migration Script
Migrates from CSV-based storage to Multi-Database Architecture
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Iterator
from datetime import datetime, date
import logging
import os
import sys
from pathlib import Path
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from db_connection import db_pool, bulk_insert_county_features, bulk_insert_metrics_history
from redis_cache import cache
from vector_db_pinecone import PineconeVectorStore, CountyVector, create_vector_from_features

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
COUNTY_FEATURES_CSV = os.getenv(
    'COUNTY_FEATURES_CSV', 
    'data/processed/county_features.csv'
)
BATCH_SIZE = int(os.getenv('MIGRATION_BATCH_SIZE', '500'))
VECTOR_DIMENSION = int(os.getenv('VECTOR_DIMENSION', '384'))

# Feature to domain mapping
FEATURE_DOMAIN_MAPPING = {
    # Climate features
    'disaster_count': 'climate',
    'disaster_flood': 'climate',
    'disaster_severe_storms': 'climate',
    'disaster_hurricane': 'climate',
    'disaster_fire': 'climate',
    'disaster_tornado': 'climate',
    'disaster_count_recent': 'climate',
    'disasters_2015_2025': 'climate',
    'disasters_2005_2014': 'climate',
    'disaster_acceleration': 'climate',
    
    # Health features
    'elderly_pct': 'health',
    'disability_pct': 'health',
    'uninsured_pct': 'health',
    'dist_nearest_hospitals_km': 'health',
    'dist_2nd_nearest_hospitals_km': 'health',
    'count_hospitals_50km': 'health',
    'density_hospitals_per10k': 'health',
    'dist_nearest_nursing_homes_km': 'health',
    'density_nursing_homes_per10k': 'health',
    'hospital_bed_count': 'health',
    
    # Infrastructure features
    'dist_nearest_fire_stations_km': 'infrastructure',
    'count_fire_stations_50km': 'infrastructure',
    'density_fire_stations_per10k': 'infrastructure',
    'dist_nearest_ems_km': 'infrastructure',
    'count_ems_50km': 'infrastructure',
    'density_ems_per10k': 'infrastructure',
    'emergency_response_time': 'infrastructure',
    
    # Socioeconomic features
    'median_household_income': 'socioeconomic',
    'poverty_pct': 'socioeconomic',
    'unemployment_rate': 'socioeconomic',
    'education_less_than_high_school': 'socioeconomic',
    'single_parent_households_pct': 'socioeconomic',
    'minority_population_pct': 'socioeconomic',
    'language_barrier_pct': 'socioeconomic',
    'housing_units_mobile_homes_pct': 'socioeconomic',
    'no_vehicle_households_pct': 'socioeconomic',
    'crowded_housing_pct': 'socioeconomic',
    
    # Agriculture features
    'farm_count': 'agriculture',
    'farm_acres': 'agriculture',
    'crop_diversity_index': 'agriculture',
    'irrigation_coverage_pct': 'agriculture',
    'agricultural_vulnerability_score': 'agriculture',
    
    # Composite features
    'svi_score': 'comprehensive',
    'resilience_score': 'comprehensive',
    'climate_risk_score': 'comprehensive',
    'health_risk_score': 'comprehensive',
    'infrastructure_risk_score': 'comprehensive',
    'overall_risk_score': 'comprehensive',
    'risk_percentile': 'comprehensive',
}


class DataMigrator:
    """
    Handles migration from CSV to multi-database architecture.
    Supports incremental and full migration modes.
    """
    
    def __init__(self, csv_path: str = COUNTY_FEATURES_CSV):
        """
        Initialize migrator.
        
        Args:
            csv_path: Path to county features CSV file
        """
        self.csv_path = csv_path
        self.df = None
        self.vector_store = None
        self.feature_id_map = {}
        self.county_id_map = {}
        
    def load_csv(self) -> pd.DataFrame:
        """
        Load county features CSV.
        
        Returns:
            DataFrame with county features
        """
        logger.info(f"Loading CSV from {self.csv_path}")
        
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        self.df = pd.read_csv(self.csv_path)
        
        # Ensure fips is string with leading zeros
        self.df['fips'] = self.df['fips'].astype(str).str.zfill(5)
        
        logger.info(f"Loaded {len(self.df)} counties with {len(self.df.columns)} features")
        return self.df
    
    def _get_feature_id_map(self) -> Dict[str, str]:
        """Get mapping of feature_key to feature_id from database"""
        if not self.feature_id_map:
            query = "SELECT id, feature_key FROM feature_definitions"
            with db_pool.get_cursor() as cursor:
                cursor.execute(query)
                self.feature_id_map = {
                    row['feature_key']: str(row['id']) 
                    for row in cursor.fetchall()
                }
        return self.feature_id_map
    
    def _get_county_id_map(self) -> Dict[str, str]:
        """Get mapping of fips_code to county_id from database"""
        if not self.county_id_map:
            query = "SELECT id, fips_code FROM counties"
            with db_pool.get_cursor() as cursor:
                cursor.execute(query)
                self.county_id_map = {
                    row['fips_code']: str(row['id']) 
                    for row in cursor.fetchall()
                }
        return self.county_id_map
    
    # ============================================
    # COUNTY MIGRATION
    # ============================================
    
    def migrate_counties(self, batch_size: int = BATCH_SIZE):
        """
        Migrate counties to PostgreSQL.
        
        Args:
            batch_size: Number of counties per batch
        """
        logger.info("Migrating counties...")
        
        if self.df is None:
            self.load_csv()
        
        # Extract unique counties
        counties_data = []
        for _, row in self.df.iterrows():
            fips = str(row['fips']).zfill(5)
            
            counties_data.append({
                'fips_code': fips,
                'state_fips': fips[:2],
                'county_fips': fips[2:],
                'county_name': row.get('county_name', row.get('name', '')),
                'state_name': row.get('state_name', ''),
                'state_abbrev': row.get('state', ''),
                'population': int(row.get('population', 0)) if pd.notna(row.get('population')) else 0,
            })
        
        # Insert in batches
        insert_query = """
        INSERT INTO counties (
            fips_code, state_fips, county_fips, county_name, 
            state_name, state_abbrev, population
        ) VALUES (
            %(fips_code)s, %(state_fips)s, %(county_fips)s, %(county_name)s,
            %(state_name)s, %(state_abbrev)s, %(population)s
        ) ON CONFLICT (fips_code) DO UPDATE SET
            county_name = EXCLUDED.county_name,
            population = EXCLUDED.population,
            last_updated = NOW()
        """
        
        for i in tqdm(range(0, len(counties_data), batch_size), desc="Migrating counties"):
            batch = counties_data[i:i + batch_size]
            with db_pool.get_cursor() as cursor:
                cursor.executemany(insert_query, batch)
        
        logger.info(f"Migrated {len(counties_data)} counties")
        
        # Refresh county ID map
        self.county_id_map = {}
        self._get_county_id_map()
    
    # ============================================
    # FEATURE VALUES MIGRATION
    # ============================================
    
    def migrate_county_features(self, batch_size: int = BATCH_SIZE):
        """
        Migrate county feature values to PostgreSQL.
        
        Args:
            batch_size: Number of records per batch
        """
        logger.info("Migrating county feature values...")
        
        if self.df is None:
            self.load_csv()
        
        # Get feature mappings
        feature_id_map = self._get_feature_id_map()
        county_id_map = self._get_county_id_map()
        
        # Identify feature columns
        feature_columns = [
            c for c in self.df.columns 
            if c not in ['fips', 'county_name', 'name', 'state', 'state_name', 'population']
        ]
        
        # Prepare feature values
        feature_values = []
        
        for _, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Preparing features"):
            county_fips = str(row['fips']).zfill(5)
            county_id = county_id_map.get(county_fips)
            
            if not county_id:
                logger.warning(f"County not found: {county_fips}")
                continue
            
            for feature_key in feature_columns:
                feature_id = feature_id_map.get(feature_key)
                if not feature_id:
                    continue
                
                value = row.get(feature_key)
                if pd.isna(value):
                    continue
                
                try:
                    numeric_value = float(value)
                except (ValueError, TypeError):
                    continue
                
                feature_values.append({
                    'county_id': county_id,
                    'feature_id': feature_id,
                    'numeric_value': numeric_value,
                    'effective_date': date.today()
                })
        
        # Insert in batches using bulk insert
        logger.info(f"Inserting {len(feature_values)} feature values...")
        
        for i in tqdm(range(0, len(feature_values), batch_size), desc="Inserting features"):
            batch = feature_values[i:i + batch_size]
            bulk_insert_county_features(batch)
        
        logger.info(f"Migrated {len(feature_values)} feature values")
    
    # ============================================
    # HISTORICAL METRICS MIGRATION
    # ============================================
    
    def migrate_historical_metrics(
        self, 
        historical_data_path: Optional[str] = None,
        batch_size: int = BATCH_SIZE
    ):
        """
        Migrate historical time-series data to TimescaleDB.
        
        Args:
            historical_data_path: Path to historical data CSV
            batch_size: Number of records per batch
        """
        if not historical_data_path:
            logger.info("No historical data path provided, skipping")
            return
        
        logger.info(f"Migrating historical metrics from {historical_data_path}")
        
        # Load historical data
        hist_df = pd.read_csv(historical_data_path)
        hist_df['fips'] = hist_df['fips'].astype(str).str.zfill(5)
        
        feature_id_map = self._get_feature_id_map()
        county_id_map = self._get_county_id_map()
        
        # Prepare metrics
        metrics = []
        for _, row in tqdm(hist_df.iterrows(), total=len(hist_df), desc="Preparing metrics"):
            county_id = county_id_map.get(row['fips'])
            if not county_id:
                continue
            
            # Assume columns are: fips, date, feature_key, value
            timestamp = pd.to_datetime(row.get('date', row.get('timestamp')))
            feature_key = row.get('feature_key')
            value = row.get('value')
            
            feature_id = feature_id_map.get(feature_key)
            if not feature_id or pd.isna(value):
                continue
            
            metrics.append({
                'time': timestamp,
                'county_id': county_id,
                'feature_id': feature_id,
                'value': float(value),
                'value_type': row.get('value_type', 'measured'),
                'confidence': row.get('confidence', 1.0),
                'data_source': row.get('data_source', 'migration')
            })
        
        # Bulk insert
        logger.info(f"Inserting {len(metrics)} historical metrics...")
        
        for i in tqdm(range(0, len(metrics), batch_size), desc="Inserting metrics"):
            batch = metrics[i:i + batch_size]
            bulk_insert_metrics_history(batch)
        
        logger.info(f"Migrated {len(metrics)} historical metrics")
    
    # ============================================
    # VECTOR EMBEDDINGS MIGRATION
    # ============================================
    
    def migrate_vectors(
        self, 
        vector_columns: Optional[List[str]] = None,
        metadata_columns: List[str] = None,
        namespace: str = "comprehensive"
    ):
        """
        Migrate vector embeddings to Pinecone.
        
        Args:
            vector_columns: Columns to use for vectors (None = auto-detect)
            metadata_columns: Columns to include as metadata
            namespace: Pinecone namespace
        """
        logger.info("Migrating vector embeddings...")
        
        if self.df is None:
            self.load_csv()
        
        # Initialize vector store
        self.vector_store = PineconeVectorStore()
        
        # Auto-detect vector columns if not specified
        if vector_columns is None:
            # Use numeric columns that might be features
            vector_columns = [
                c for c in self.df.columns 
                if c not in ['fips', 'county_name', 'name', 'state', 'state_name']
                and pd.api.types.is_numeric_dtype(self.df[c])
            ]
        
        if metadata_columns is None:
            metadata_columns = ['county_name', 'state', 'population']
        
        logger.info(f"Using {len(vector_columns)} columns for vectors")
        
        # Prepare vectors
        vectors = []
        for _, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Preparing vectors"):
            county_fips = str(row['fips']).zfill(5)
            
            # Extract vector values
            vector_values = []
            for col in vector_columns:
                val = row.get(col, 0)
                if pd.isna(val):
                    val = 0.0
                vector_values.append(float(val))
            
            # Normalize vector
            vector_values = self._normalize_vector(vector_values)
            
            # Pad or truncate to match dimension
            if len(vector_values) < VECTOR_DIMENSION:
                vector_values.extend([0.0] * (VECTOR_DIMENSION - len(vector_values)))
            vector_values = vector_values[:VECTOR_DIMENSION]
            
            # Build metadata
            metadata = {}
            for col in metadata_columns:
                if col in row:
                    val = row[col]
                    if pd.isna(val):
                        val = None
                    elif isinstance(val, (np.integer, np.floating)):
                        val = float(val)
                    metadata[col] = val
            
            vectors.append(CountyVector(
                id=county_fips,
                values=vector_values,
                metadata=metadata
            ))
            
            # Upsert in batches
            if len(vectors) >= 100:
                self.vector_store.upsert_counties(vectors, namespace=namespace)
                vectors = []
        
        # Upsert remaining
        if vectors:
            self.vector_store.upsert_counties(vectors, namespace=namespace)
        
        logger.info(f"Migrated {len(self.df)} vectors to namespace '{namespace}'")
    
    def migrate_domain_vectors(self):
        """Migrate vectors for each domain separately"""
        logger.info("Migrating domain-specific vectors...")
        
        if self.df is None:
            self.load_csv()
        
        self.vector_store = PineconeVectorStore()
        
        # Group features by domain
        domain_features = {}
        for feature, domain in FEATURE_DOMAIN_MAPPING.items():
            if feature in self.df.columns:
                if domain not in domain_features:
                    domain_features[domain] = []
                domain_features[domain].append(feature)
        
        # Migrate each domain
        for domain, features in domain_features.items():
            logger.info(f"Migrating {domain} domain with {len(features)} features")
            
            vectors = []
            for _, row in self.df.iterrows():
                county_fips = str(row['fips']).zfill(5)
                
                # Extract domain-specific features
                vector_values = []
                for feat in features:
                    val = row.get(feat, 0)
                    if pd.isna(val):
                        val = 0.0
                    vector_values.append(float(val))
                
                # Normalize and pad
                vector_values = self._normalize_vector(vector_values)
                if len(vector_values) < VECTOR_DIMENSION:
                    vector_values.extend([0.0] * (VECTOR_DIMENSION - len(vector_values)))
                vector_values = vector_values[:VECTOR_DIMENSION]
                
                vectors.append(CountyVector(
                    id=county_fips,
                    values=vector_values,
                    metadata={
                        'county_name': row.get('county_name', ''),
                        'state': row.get('state', ''),
                        'population': int(row.get('population', 0)) if pd.notna(row.get('population')) else 0
                    }
                ))
                
                if len(vectors) >= 100:
                    self.vector_store.upsert_counties(vectors, namespace=domain)
                    vectors = []
            
            if vectors:
                self.vector_store.upsert_counties(vectors, namespace=domain)
            
            logger.info(f"Migrated {len(self.df)} vectors to {domain} namespace")
    
    def _normalize_vector(self, vector: List[float]) -> List[float]:
        """L2 normalize a vector"""
        arr = np.array(vector)
        norm = np.linalg.norm(arr)
        if norm == 0:
            return vector
        return (arr / norm).tolist()
    
    # ============================================
    # CACHE WARMING
    # ============================================
    
    def warm_cache(self):
        """Pre-populate Redis cache with frequently accessed data"""
        logger.info("Warming cache...")
        
        # Cache feature definitions
        query = """
        SELECT fd.*, fc.category_name, fc.domain
        FROM feature_definitions fd
        JOIN feature_categories fc ON fd.category_id = fc.id
        WHERE fd.is_active = TRUE
        """
        features = db_pool.execute(query)
        cache.cache_feature_definitions(features)
        logger.info(f"Cached {len(features)} feature definitions")
        
        # Cache county lists by state
        states_query = "SELECT DISTINCT state_abbrev FROM counties WHERE state_abbrev IS NOT NULL"
        states = db_pool.execute(states_query)
        
        for state in tqdm(states, desc="Caching county lists"):
            state_abbrev = state['state_abbrev']
            counties = db_pool.execute(
                "SELECT fips_code, county_name, population FROM counties WHERE state_abbrev = %s",
                (state_abbrev,)
            )
            cache.cache_county_list(state_abbrev, counties)
        
        logger.info("Cache warming completed")
    
    # ============================================
    # FULL MIGRATION
    # ============================================
    
    def migrate_all(
        self,
        skip_counties: bool = False,
        skip_features: bool = False,
        skip_vectors: bool = False,
        skip_cache: bool = False
    ):
        """
        Run full migration.
        
        Args:
            skip_counties: Skip county migration
            skip_features: Skip feature values migration
            skip_vectors: Skip vector migration
            skip_cache: Skip cache warming
        """
        logger.info("Starting full migration...")
        start_time = datetime.now()
        
        # Load CSV
        self.load_csv()
        
        # Step 1: Migrate counties
        if not skip_counties:
            self.migrate_counties()
        
        # Step 2: Migrate feature values
        if not skip_features:
            self.migrate_county_features()
        
        # Step 3: Migrate vectors
        if not skip_vectors:
            self.migrate_vectors()
            self.migrate_domain_vectors()
        
        # Step 4: Warm cache
        if not skip_cache:
            self.warm_cache()
        
        duration = datetime.now() - start_time
        logger.info(f"Migration completed in {duration}")
    
    # ============================================
    # VERIFICATION
    # ============================================
    
    def verify_migration(self) -> Dict:
        """Verify migration by checking record counts"""
        logger.info("Verifying migration...")
        
        results = {}
        
        # Check counties
        county_count = db_pool.execute_one("SELECT COUNT(*) as count FROM counties")
        results['counties'] = {
            'csv_count': len(self.df) if self.df is not None else 0,
            'db_count': county_count['count'] if county_count else 0
        }
        
        # Check features
        feature_count = db_pool.execute_one("SELECT COUNT(*) as count FROM county_features")
        results['features'] = {
            'db_count': feature_count['count'] if feature_count else 0
        }
        
        # Check vectors
        if self.vector_store:
            stats = self.vector_store.get_namespace_stats("comprehensive")
            results['vectors'] = stats
        
        # Check cache
        cache_stats = cache.get_stats()
        results['cache'] = cache_stats
        
        logger.info(f"Verification results: {results}")
        return results


def main():
    """Main entry point for migration"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ResilienceAI Data Migration')
    parser.add_argument('--csv', default=COUNTY_FEATURES_CSV, help='Path to CSV file')
    parser.add_argument('--skip-counties', action='store_true', help='Skip county migration')
    parser.add_argument('--skip-features', action='store_true', help='Skip feature migration')
    parser.add_argument('--skip-vectors', action='store_true', help='Skip vector migration')
    parser.add_argument('--skip-cache', action='store_true', help='Skip cache warming')
    parser.add_argument('--verify-only', action='store_true', help='Only run verification')
    
    args = parser.parse_args()
    
    migrator = DataMigrator(csv_path=args.csv)
    
    if args.verify_only:
        migrator.load_csv()
        results = migrator.verify_migration()
        print(f"Verification results:\n{results}")
    else:
        migrator.migrate_all(
            skip_counties=args.skip_counties,
            skip_features=args.skip_features,
            skip_vectors=args.skip_vectors,
            skip_cache=args.skip_cache
        )
        
        # Run verification
        results = migrator.verify_migration()
        print(f"\nMigration completed. Verification results:\n{results}")


if __name__ == '__main__':
    main()
