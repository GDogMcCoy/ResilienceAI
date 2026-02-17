"""
ResilienceAI - CSV Export Module
Export vulnerability data as formatted CSV files
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from config import PROCESSED_DIR, REPORTS_DIR


class CSVExporter:
    """Export county vulnerability data as formatted CSV files"""
    
    # Column display names
    COLUMN_NAMES = {
        'fips': 'FIPS Code',
        'county_name': 'County Name',
        'state': 'State',
        'risk_score': 'Risk Score',
        'risk_level': 'Risk Level',
        'vulnerability_index': 'Vulnerability Index',
        'isolation_index': 'Isolation Index',
        'total_population': 'Total Population',
        'poverty_pct': 'Poverty Rate (%)',
        'elderly_pct': 'Elderly Population (%)',
        'disability_pct': 'Disability Rate (%)',
        'uninsured_pct': 'Uninsured Rate (%)',
        'disaster_count': 'Total Disasters',
        'disaster_count_recent': 'Recent Disasters (2015+)',
        'disaster_flood': 'Flood Disasters',
        'disaster_hurricane': 'Hurricane Disasters',
        'disaster_fire': 'Fire Disasters',
        'disaster_tornado': 'Tornado Disasters',
        'dist_nearest_hospitals_km': 'Distance to Nearest Hospital (km)',
        'dist_nearest_fire_stations_km': 'Distance to Nearest Fire Station (km)',
        'dist_nearest_ems_stations_km': 'Distance to Nearest EMS (km)',
        'dist_nearest_nursing_homes_km': 'Distance to Nearest Nursing Home (km)',
        'count_hospitals_50km': 'Hospitals Within 50km',
        'count_fire_stations_50km': 'Fire Stations Within 50km',
        'count_ems_stations_50km': 'EMS Stations Within 50km',
        'count_nursing_homes_50km': 'Nursing Homes Within 50km',
        'density_hospitals_per10k': 'Hospital Density (per 10k)',
        'density_fire_stations_per10k': 'Fire Station Density (per 10k)',
        'density_ems_stations_per10k': 'EMS Density (per 10k)',
        'density_nursing_homes_per10k': 'Nursing Home Density (per 10k)',
        'compound_risk_count': 'Compound Risk Dimensions',
        'compound_risk_flag': 'Compound Risk Flag',
        'zero_redundancy_flag': 'Zero Redundancy Flag',
        'redundancy_score': 'Redundancy Score',
        'pop_weighted_risk': 'Population-Weighted Risk',
        'disaster_acceleration': 'Disaster Acceleration',
        'top_intervention': 'Top Recommended Intervention',
        'latitude': 'Latitude',
        'longitude': 'Longitude'
    }
    
    # Predefined column sets
    COLUMN_SETS = {
        'minimal': ['fips', 'county_name', 'risk_score', 'risk_level'],
        'standard': [
            'fips', 'county_name', 'state', 'risk_score', 'risk_level',
            'vulnerability_index', 'isolation_index', 'total_population'
        ],
        'full': None,  # All available columns
        'demographics': [
            'fips', 'county_name', 'total_population',
            'poverty_pct', 'elderly_pct', 'disability_pct', 'uninsured_pct'
        ],
        'infrastructure': [
            'fips', 'county_name',
            'dist_nearest_hospitals_km', 'dist_nearest_fire_stations_km',
            'dist_nearest_ems_stations_km', 'count_hospitals_50km',
            'count_fire_stations_50km', 'count_ems_stations_50km',
            'redundancy_score', 'zero_redundancy_flag'
        ],
        'disaster': [
            'fips', 'county_name', 'disaster_count', 'disaster_count_recent',
            'disaster_flood', 'disaster_hurricane', 'disaster_fire',
            'disaster_tornado', 'disaster_acceleration'
        ],
        'risk': [
            'fips', 'county_name', 'risk_score', 'risk_level',
            'vulnerability_index', 'isolation_index',
            'compound_risk_count', 'compound_risk_flag',
            'pop_weighted_risk', 'top_intervention'
        ]
    }
    
    def __init__(self, df=None):
        """Initialize exporter with county data"""
        if df is None:
            path = PROCESSED_DIR / "county_features.csv"
            if path.exists():
                self.df = pd.read_csv(path, dtype={"fips": str})
            else:
                self.df = None
        else:
            self.df = df
    
    def export(
        self,
        output_path: str = None,
        columns: List[str] = None,
        column_set: str = 'standard',
        filters: Dict[str, Any] = None,
        format_numbers: bool = True,
        include_header: bool = True,
        delimiter: str = ',',
        encoding: str = 'utf-8',
        compression: Optional[str] = None
    ) -> Dict:
        """
        Export data as CSV
        
        Args:
            output_path: Output file path
            columns: Specific columns to export
            column_set: Predefined column set ('minimal', 'standard', 'full', etc.)
            filters: Filters to apply
            format_numbers: Format numeric columns
            include_header: Include column headers
            delimiter: Field delimiter
            encoding: File encoding
            compression: Compression type ('gzip', 'bz2', 'zip', 'xz')
            
        Returns:
            Dictionary with export metadata
        """
        if self.df is None:
            return {"error": "Data not loaded"}
        
        # Apply filters
        df = self.df.copy()
        if filters:
            df = self._apply_filters(df, filters)
        
        # Select columns
        if columns:
            # Use specified columns
            available_cols = [c for c in columns if c in df.columns]
            df = df[available_cols]
        elif column_set and column_set in self.COLUMN_SETS:
            # Use predefined column set
            if self.COLUMN_SETS[column_set] is not None:
                available_cols = [c for c in self.COLUMN_SETS[column_set] if c in df.columns]
                df = df[available_cols]
        
        # Format numbers
        if format_numbers:
            df = self._format_numbers(df)
        
        # Rename columns for display
        if include_header:
            df = df.rename(columns={k: v for k, v in self.COLUMN_NAMES.items() if k in df.columns})
        
        # Create output path
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = REPORTS_DIR / f"resilienceai_export_{timestamp}.csv"
        
        output_path = Path(output_path)
        
        # Handle compression
        if compression:
            if compression not in ['gzip', 'bz2', 'zip', 'xz']:
                return {"error": f"Unsupported compression: {compression}"}
            output_path = output_path.with_suffix(f'.csv.{compression}')
        
        # Export to CSV
        df.to_csv(
            output_path,
            index=False,
            header=include_header,
            sep=delimiter,
            encoding=encoding,
            compression=compression
        )
        
        return {
            "output_path": str(output_path),
            "row_count": len(df),
            "column_count": len(df.columns),
            "filters_applied": filters,
            "compression": compression
        }
    
    def export_multiple(
        self,
        output_dir: str,
        splits: List[Dict[str, Any]]
    ) -> List[Dict]:
        """
        Export multiple CSV files based on splits
        
        Args:
            output_dir: Output directory
            splits: List of split configurations
                Each split: {'name': str, 'filter': dict, 'columns': list}
                
        Returns:
            List of export metadata
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        for split in splits:
            name = split.get('name', f"split_{len(results)}")
            output_path = output_dir / f"{name}.csv"
            
            result = self.export(
                output_path=output_path,
                columns=split.get('columns'),
                column_set=split.get('column_set', 'standard'),
                filters=split.get('filter'),
                format_numbers=split.get('format_numbers', True)
            )
            
            result['split_name'] = name
            results.append(result)
        
        return results
    
    def export_by_state(
        self,
        output_dir: str,
        column_set: str = 'standard'
    ) -> List[Dict]:
        """
        Export separate CSV file for each state
        
        Args:
            output_dir: Output directory
            column_set: Column set to use
            
        Returns:
            List of export metadata
        """
        if self.df is None:
            return [{"error": "Data not loaded"}]
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract state from county_name
        df = self.df.copy()
        df['state'] = df['county_name'].str.extract(r', ([\w ]+)$')[0]
        
        results = []
        
        for state in df['state'].dropna().unique():
            state_df = df[df['state'] == state]
            
            # Create safe filename
            safe_state = state.replace(' ', '_')
            output_path = output_dir / f"{safe_state}.csv"
            
            # Create temporary exporter for state data
            state_exporter = CSVExporter(state_df)
            result = state_exporter.export(
                output_path=output_path,
                column_set=column_set
            )
            
            result['state'] = state
            results.append(result)
        
        return results
    
    def export_by_risk_level(
        self,
        output_dir: str,
        column_set: str = 'standard'
    ) -> List[Dict]:
        """
        Export separate CSV file for each risk level
        
        Args:
            output_dir: Output directory
            column_set: Column set to use
            
        Returns:
            List of export metadata
        """
        if self.df is None:
            return [{"error": "Data not loaded"}]
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        for risk_level in ['High', 'Medium', 'Low']:
            risk_df = self.df[self.df['risk_level'] == risk_level]
            
            if len(risk_df) == 0:
                continue
            
            output_path = output_dir / f"risk_{risk_level.lower()}.csv"
            
            risk_exporter = CSVExporter(risk_df)
            result = risk_exporter.export(
                output_path=output_path,
                column_set=column_set
            )
            
            result['risk_level'] = risk_level
            results.append(result)
        
        return results
    
    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to dataframe"""
        result = df.copy()
        
        if 'state' in filters:
            state = filters['state']
            result = result[result['county_name'].str.contains(f', {state}$', regex=True, na=False)]
        
        if 'risk_level' in filters:
            result = result[result['risk_level'] == filters['risk_level']]
        
        if 'min_risk_score' in filters:
            result = result[result['risk_score'] >= filters['min_risk_score']]
        
        if 'max_risk_score' in filters:
            result = result[result['risk_score'] <= filters['max_risk_score']]
        
        if 'compound_risk' in filters and filters['compound_risk']:
            result = result[result['compound_risk_flag'] == True]
        
        if 'zero_redundancy' in filters and filters['zero_redundancy']:
            result = result[result['zero_redundancy_flag'] == True]
        
        if 'min_population' in filters:
            result = result[result['total_population'] >= filters['min_population']]
        
        if 'max_population' in filters:
            result = result[result['total_population'] <= filters['max_population']]
        
        if 'fips_list' in filters:
            result = result[result['fips'].isin(filters['fips_list'])]
        
        return result
    
    def _format_numbers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Format numeric columns"""
        result = df.copy()
        
        # Format percentages
        pct_cols = [c for c in df.columns if c.endswith('_pct')]
        for col in pct_cols:
            result[col] = result[col].round(2)
        
        # Format indices
        index_cols = [c for c in df.columns if c.endswith('_index')]
        for col in index_cols:
            result[col] = result[col].round(3)
        
        # Format risk score
        if 'risk_score' in result.columns:
            result['risk_score'] = result['risk_score'].round(3)
        
        # Format distances
        dist_cols = [c for c in df.columns if c.startswith('dist_')]
        for col in dist_cols:
            result[col] = result[col].round(2)
        
        return result
    
    def get_column_info(self) -> Dict[str, Dict]:
        """Get information about available columns"""
        if self.df is None:
            return {"error": "Data not loaded"}
        
        info = {}
        
        for col in self.df.columns:
            info[col] = {
                'display_name': self.COLUMN_NAMES.get(col, col),
                'dtype': str(self.df[col].dtype),
                'null_count': int(self.df[col].isna().sum()),
                'null_pct': float(self.df[col].isna().sum() / len(self.df) * 100)
            }
            
            # Add statistics for numeric columns
            if pd.api.types.is_numeric_dtype(self.df[col]):
                info[col].update({
                    'min': float(self.df[col].min()),
                    'max': float(self.df[col].max()),
                    'mean': float(self.df[col].mean()),
                    'median': float(self.df[col].median())
                })
            
            # Add unique values for categorical columns
            elif self.df[col].nunique() < 50:
                info[col]['unique_values'] = self.df[col].dropna().unique().tolist()
        
        return info
    
    def preview(
        self,
        columns: List[str] = None,
        column_set: str = 'standard',
        filters: Dict[str, Any] = None,
        n_rows: int = 10
    ) -> pd.DataFrame:
        """
        Preview export data
        
        Args:
            columns: Specific columns
            column_set: Predefined column set
            filters: Filters to apply
            n_rows: Number of rows to preview
            
        Returns:
            Preview DataFrame
        """
        if self.df is None:
            return pd.DataFrame()
        
        # Apply filters
        df = self.df.copy()
        if filters:
            df = self._apply_filters(df, filters)
        
        # Select columns
        if columns:
            available_cols = [c for c in columns if c in df.columns]
            df = df[available_cols]
        elif column_set and column_set in self.COLUMN_SETS:
            if self.COLUMN_SETS[column_set] is not None:
                available_cols = [c for c in self.COLUMN_SETS[column_set] if c in df.columns]
                df = df[available_cols]
        
        # Rename columns
        df = df.rename(columns={k: v for k, v in self.COLUMN_NAMES.items() if k in df.columns})
        
        return df.head(n_rows)


def main():
    """CLI for CSV export"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Export ResilienceAI data as CSV")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--column-set", default='standard',
                        choices=list(CSVExporter.COLUMN_SETS.keys()),
                        help="Predefined column set")
    parser.add_argument("--columns", nargs="+", help="Specific columns to export")
    parser.add_argument("--state", help="Filter by state")
    parser.add_argument("--risk-level", choices=["Low", "Medium", "High"],
                        help="Filter by risk level")
    parser.add_argument("--min-risk", type=float, help="Minimum risk score")
    parser.add_argument("--delimiter", default=",", help="Field delimiter")
    parser.add_argument("--compression", choices=['gzip', 'bz2', 'zip', 'xz'],
                        help="Compression type")
    parser.add_argument("--preview", action="store_true", help="Preview data only")
    parser.add_argument("--split-by-state", action="store_true",
                        help="Export separate file per state")
    parser.add_argument("--split-by-risk", action="store_true",
                        help="Export separate file per risk level")
    
    args = parser.parse_args()
    
    exporter = CSVExporter()
    
    if exporter.df is None:
        print("Error: County data not found. Run pipeline first.")
        return
    
    if args.preview:
        filters = {}
        if args.state:
            filters['state'] = args.state
        if args.risk_level:
            filters['risk_level'] = args.risk_level
        if args.min_risk:
            filters['min_risk_score'] = args.min_risk
        
        preview = exporter.preview(
            columns=args.columns,
            column_set=args.column_set,
            filters=filters if filters else None,
            n_rows=10
        )
        print(preview.to_string())
        return
    
    filters = {}
    if args.state:
        filters['state'] = args.state
    if args.risk_level:
        filters['risk_level'] = args.risk_level
    if args.min_risk:
        filters['min_risk_score'] = args.min_risk
    
    if args.split_by_state:
        output_dir = args.output or REPORTS_DIR / 'csv_by_state'
        results = exporter.export_by_state(output_dir, args.column_set)
        for r in results:
            if 'error' in r:
                print(f"Error: {r['error']}")
            else:
                print(f"Exported {r['state']}: {r['output_path']} ({r['row_count']} rows)")
    
    elif args.split_by_risk:
        output_dir = args.output or REPORTS_DIR / 'csv_by_risk'
        results = exporter.export_by_risk_level(output_dir, args.column_set)
        for r in results:
            if 'error' in r:
                print(f"Error: {r['error']}")
            else:
                print(f"Exported {r['risk_level']}: {r['output_path']} ({r['row_count']} rows)")
    
    else:
        result = exporter.export(
            output_path=args.output,
            columns=args.columns,
            column_set=args.column_set,
            filters=filters if filters else None,
            delimiter=args.delimiter,
            compression=args.compression
        )
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Exported to: {result['output_path']}")
            print(f"Rows: {result['row_count']}")
            print(f"Columns: {result['column_count']}")


if __name__ == "__main__":
    main()
