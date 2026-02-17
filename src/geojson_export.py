"""
ResilienceAI - GeoJSON Export Module
Export vulnerability data as GeoJSON for GIS workflows.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pandas as pd
from pathlib import Path
from config import PROCESSED_DIR, REPORTS_DIR


class GeoJSONExporter:
    """Export county vulnerability data as GeoJSON."""

    def __init__(self, df=None):
        if df is None:
            path = PROCESSED_DIR / "county_features.csv"
            if path.exists():
                self.df = pd.read_csv(path, dtype={"fips": str})
            else:
                self.df = None
        else:
            self.df = df

    def _create_feature_collection(self, features):
        """Create a GeoJSON FeatureCollection."""
        return {
            "type": "FeatureCollection",
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                }
            },
            "features": features
        }

    def _row_to_feature(self, row, include_all_properties=True):
        """Convert a DataFrame row to a GeoJSON Feature."""
        fips = str(row.get("fips", ""))
        county_name = row.get("county_name", "Unknown")

        # Basic properties (always included)
        properties = {
            "fips": fips,
            "county_name": county_name,
            "state": county_name.split(", ")[-1] if ", " in county_name else "",
            "risk_score": float(row.get("risk_score", 0)),
            "risk_level": row.get("risk_level", "Low"),
            "total_population": int(row.get("total_population", 0)) if pd.notna(row.get("total_population")) else 0,
        }

        if include_all_properties:
            # Add all available metrics
            numeric_cols = [
                "vulnerability_index", "isolation_index",
                "poverty_pct", "elderly_pct", "disability_pct", "uninsured_pct",
                "disaster_count", "disaster_count_recent",
                "compound_risk_count",
                "dist_nearest_hospitals_km", "dist_nearest_fire_stations_km",
                "dist_nearest_ems_stations_km", "dist_nearest_nursing_homes_km",
                "count_hospitals_50km", "count_fire_stations_50km",
                "count_ems_stations_50km", "count_nursing_homes_50km",
                "density_hospitals_per10k", "density_fire_stations_per10k",
                "density_ems_stations_per10k", "density_nursing_homes_per10k",
                "disaster_flood", "disaster_hurricane", "disaster_fire", "disaster_tornado",
                "disaster_acceleration",
                "redundancy_score",
                "pop_weighted_risk",
            ]

            for col in numeric_cols:
                if col in row and pd.notna(row[col]):
                    properties[col] = float(row[col])

            # String properties
            string_cols = ["top_intervention"]
            for col in string_cols:
                if col in row and pd.notna(row[col]):
                    properties[col] = str(row[col])

            # Boolean flags
            flag_cols = ["compound_risk_flag", "zero_redundancy_flag"]
            for col in flag_cols:
                if col in row and pd.notna(row[col]):
                    properties[col] = bool(row[col])

        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    float(row.get("longitude", 0)),
                    float(row.get("latitude", 0))
                ]
            },
            "properties": properties
        }

    def export_all(self, include_all_properties=True):
        """Export all counties as GeoJSON."""
        if self.df is None:
            return {"error": "Data not loaded"}

        features = []
        for _, row in self.df.iterrows():
            features.append(self._row_to_feature(row, include_all_properties))

        return self._create_feature_collection(features)

    def export_state(self, state_abbrev, include_all_properties=True):
        """Export all counties in a state."""
        if self.df is None:
            return {"error": "Data not loaded"}

        # Support both full state names and abbreviations
        state_mapping = {
            'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
            'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
            'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
            'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
            'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
            'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
            'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
            'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
            'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
            'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
            'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
            'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
            'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
        }
        
        # Convert abbreviation to full name if needed
        state_name = state_mapping.get(state_abbrev.upper(), state_abbrev)
        
        state_df = self.df[self.df["county_name"].str.contains(
            f", {state_name}$", regex=True, na=False
        )]

        if state_df.empty:
            return {"error": f"No counties found for state {state_abbrev}"}

        features = []
        for _, row in state_df.iterrows():
            features.append(self._row_to_feature(row, include_all_properties))

        return self._create_feature_collection(features)

    def export_county(self, fips, include_all_properties=True):
        """Export a single county."""
        if self.df is None:
            return {"error": "Data not loaded"}

        match = self.df[self.df["fips"] == str(fips)]
        if match.empty:
            return {"error": f"County {fips} not found"}

        feature = self._row_to_feature(match.iloc[0], include_all_properties)
        return self._create_feature_collection([feature])

    def export_by_risk_level(self, risk_level, include_all_properties=True):
        """Export counties filtered by risk level."""
        if self.df is None:
            return {"error": "Data not loaded"}

        filtered_df = self.df[self.df["risk_level"] == risk_level]

        features = []
        for _, row in filtered_df.iterrows():
            features.append(self._row_to_feature(row, include_all_properties))

        return self._create_feature_collection(features)

    def export_high_risk(self, threshold=0.7, include_all_properties=True):
        """Export counties with risk score above threshold."""
        if self.df is None:
            return {"error": "Data not loaded"}

        filtered_df = self.df[self.df["risk_score"] >= threshold]

        features = []
        for _, row in filtered_df.iterrows():
            features.append(self._row_to_feature(row, include_all_properties))

        return self._create_feature_collection(features)

    def export_compound_risk(self, min_dimensions=3, include_all_properties=True):
        """Export counties with compound risk (high on multiple dimensions)."""
        if self.df is None:
            return {"error": "Data not loaded"}

        if "compound_risk_count" not in self.df.columns:
            return {"error": "compound_risk_count feature not available"}

        filtered_df = self.df[self.df["compound_risk_count"] >= min_dimensions]

        features = []
        for _, row in filtered_df.iterrows():
            features.append(self._row_to_feature(row, include_all_properties))

        return self._create_feature_collection(features)

    def export_to_file(self, geojson_data, filename=None):
        """Export GeoJSON data to a file."""
        if filename is None:
            filename = f"resilienceai-export-{pd.Timestamp.now().strftime('%Y%m%d-%H%M%S')}.geojson"

        output_path = REPORTS_DIR / filename

        with open(output_path, "w") as f:
            json.dump(geojson_data, f, indent=2)

        return str(output_path)

    def get_summary(self):
        """Get summary statistics for the dataset."""
        if self.df is None:
            return {"error": "Data not loaded"}

        return {
            "total_counties": len(self.df),
            "states": self.df["county_name"].str.extract(r', ([\w ]+)$')[0].nunique(),
            "risk_distribution": self.df["risk_level"].value_counts().to_dict(),
            "avg_risk_score": float(self.df["risk_score"].mean()),
            "high_risk_counties": int((self.df["risk_score"] >= 0.7).sum()),
            "bounds": {
                "lat_min": float(self.df["latitude"].min()),
                "lat_max": float(self.df["latitude"].max()),
                "lon_min": float(self.df["longitude"].min()),
                "lon_max": float(self.df["longitude"].max()),
            }
        }


def main():
    """CLI for GeoJSON export."""
    import argparse

    parser = argparse.ArgumentParser(description="Export ResilienceAI data as GeoJSON")
    parser.add_argument("--all", action="store_true", help="Export all counties")
    parser.add_argument("--state", help="Export specific state")
    parser.add_argument("--county", help="Export specific county by FIPS")
    parser.add_argument("--risk-level", choices=["Low", "Medium", "High"],
                        help="Filter by risk level")
    parser.add_argument("--high-risk", action="store_true",
                        help="Export high-risk counties (score >= 0.7)")
    parser.add_argument("--compound-risk", type=int, metavar="N",
                        help="Export counties with N+ compound risk dimensions")
    parser.add_argument("--minimal", action="store_true",
                        help="Export minimal properties (faster, smaller file)")
    parser.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    exporter = GeoJSONExporter()

    if exporter.df is None:
        print("Error: County data not found. Run pipeline first.")
        return

    include_props = not args.minimal

    if args.all:
        data = exporter.export_all(include_props)
        filename = args.output or "resilienceai-all-counties.geojson"
    elif args.state:
        data = exporter.export_state(args.state, include_props)
        filename = args.output or f"resilienceai-{args.state}.geojson"
    elif args.county:
        data = exporter.export_county(args.county, include_props)
        filename = args.output or f"resilienceai-county-{args.county}.geojson"
    elif args.risk_level:
        data = exporter.export_by_risk_level(args.risk_level, include_props)
        filename = args.output or f"resilienceai-risk-{args.risk_level.lower()}.geojson"
    elif args.high_risk:
        data = exporter.export_high_risk(include_all_properties=include_props)
        filename = args.output or "resilienceai-high-risk.geojson"
    elif args.compound_risk:
        data = exporter.export_compound_risk(args.compound_risk, include_props)
        filename = args.output or f"resilienceai-compound-risk-{args.compound_risk}.geojson"
    else:
        print("Usage: python geojson_export.py --all | --state STATE | --county FIPS | --risk-level LEVEL | --high-risk | --compound-risk N")
        return

    if "error" in data:
        print(f"Error: {data['error']}")
        return

    output_path = exporter.export_to_file(data, filename)
    feature_count = len(data["features"])

    print(f"Exported {feature_count} counties to: {output_path}")

    # Print summary
    summary = exporter.get_summary()
    print(f"\nDataset Summary:")
    print(f"  Total counties: {summary['total_counties']}")
    print(f"  States: {summary['states']}")
    print(f"  Risk distribution: {summary['risk_distribution']}")


if __name__ == "__main__":
    main()
