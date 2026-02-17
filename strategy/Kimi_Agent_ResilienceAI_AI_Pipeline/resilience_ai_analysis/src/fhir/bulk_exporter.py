"""
Bulk FHIR Export Module
Handles large-scale FHIR data export in NDJSON format.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

from fhir_exporter_enhanced import EnhancedFHIRExporter
from fhir_auth import FHIRServerClient, FHIRConfig

logger = logging.getLogger(__name__)


class BulkFHIRExporter:
    """
    Bulk FHIR export handler for large-scale data sharing.
    
    Implements FHIR Bulk Data Access (Flat FHIR) specification.
    """
    
    def __init__(self, exporter: EnhancedFHIRExporter, client: FHIRServerClient):
        """
        Initialize bulk FHIR exporter.
        
        Args:
            exporter: Enhanced FHIR exporter instance
            client: FHIR server client
        """
        self.exporter = exporter
        self.client = client
    
    def export_county_ndjson(
        self, 
        fips: str, 
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Export county data as NDJSON (Newline Delimited JSON).
        
        Args:
            fips: County FIPS code
            output_dir: Output directory
            
        Returns:
            Export summary
        """
        if self.exporter.df is None:
            return {"error": "Data not loaded"}
        
        match = self.exporter.df[self.exporter.df["fips"] == str(fips)]
        if match.empty:
            return {"error": f"County {fips} not found"}
        
        row = match.iloc[0].to_dict()
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        resources_by_type = {}
        
        # Generate all resource types
        resources_by_type["Location"] = [self.exporter.create_location(row)]
        resources_by_type["Organization"] = [self.exporter.create_organization(row)]
        resources_by_type["Group"] = [self.exporter.create_group(row)]
        resources_by_type["RiskAssessment"] = [self.exporter.create_risk_assessment(row)]
        resources_by_type["CarePlan"] = [self.exporter.create_care_plan(row)]
        resources_by_type["Consent"] = [self.exporter.create_consent(row)]
        
        # Generate observations
        observations = self._create_county_observations(row)
        resources_by_type["Observation"] = observations
        
        # Generate conditions
        conditions = self._create_county_conditions(row)
        resources_by_type["Condition"] = conditions
        
        # Write NDJSON files
        files_created = []
        for resource_type, resources in resources_by_type.items():
            if resources:
                file_path = output_dir / f"{resource_type}.ndjson"
                with open(file_path, 'w') as f:
                    for resource in resources:
                        f.write(json.dumps(resource) + '\n')
                files_created.append(str(file_path))
        
        return {
            "status": "success",
            "fips": fips,
            "county_name": row.get("county_name"),
            "files_created": files_created,
            "resource_counts": {rt: len(rs) for rt, rs in resources_by_type.items()}
        }
    
    def _create_county_observations(self, row: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create all observations for a county."""
        observations = []
        
        obs_definitions = [
            ("vulnerability_index", "Vulnerability Index", "{:.3f}", None, "survey"),
            ("isolation_index", "Infrastructure Isolation Index", "{:.3f}", None, "survey"),
            ("poverty_pct", "Poverty Rate", "{:.1f}", "%", "social-history"),
            ("elderly_pct", "Elderly Population Percentage", "{:.1f}", "%", "survey"),
            ("disability_pct", "Disability Rate", "{:.1f}", "%", "survey"),
            ("uninsured_pct", "Uninsured Rate", "{:.1f}", "%", "social-history"),
            ("disaster_count", "Historical Disaster Count", "{:d}", None, "survey"),
            ("disaster_count_recent", "Recent Disaster Count (2015+)", "{:d}", None, "survey"),
            ("compound_risk_count", "Compound Risk Dimensions", "{:d}", None, "survey"),
            ("dist_nearest_hospitals_km", "Distance to Nearest Hospital", "{:.1f}", "km", "survey"),
            ("dist_2nd_nearest_hospitals_km", "Distance to 2nd Nearest Hospital", "{:.1f}", "km", "survey"),
            ("count_hospitals_50km", "Hospitals Within 50km", "{:d}", None, "survey"),
            ("dist_nearest_fire_stations_km", "Distance to Nearest Fire Station", "{:.1f}", "km", "survey"),
            ("dist_nearest_ems_stations_km", "Distance to Nearest EMS Station", "{:.1f}", "km", "survey"),
            ("population", "Population", "{:d}", None, "survey"),
            ("population_density", "Population Density", "{:.1f}", "per km2", "survey"),
            ("median_income", "Median Household Income", "{:.0f}", "USD", "survey"),
            ("housing_stress_pct", "Housing Cost Burden", "{:.1f}", "%", "social-history"),
        ]
        
        for col, display, fmt, unit, category in obs_definitions:
            if col in row and pd.notna(row[col]):
                value = row[col]
                
                # Determine interpretation
                interpretation = None
                if col == "poverty_pct":
                    interpretation = "high" if value > 20 else "normal" if value > 10 else "low"
                elif col == "uninsured_pct":
                    interpretation = "high" if value > 15 else "normal" if value > 8 else "low"
                
                obs = self.exporter.create_observation(
                    row, col, display, value, unit, category, interpretation
                )
                observations.append(obs)
        
        return observations
    
    def _create_county_conditions(self, row: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create SDOH conditions for a county."""
        conditions = []
        
        # Check thresholds for SDOH conditions
        sdoh_thresholds = {
            "housing_instability": ("housing_stress_pct", 30),
            "food_insecurity": ("poverty_pct", 25),
            "transportation_insecurity": ("dist_nearest_hospitals_km", 30),
            "social_isolation": ("isolation_index", 0.6),
            "utility_insecurity": ("poverty_pct", 20)
        }
        
        for condition_type, (metric, threshold) in sdoh_thresholds.items():
            if metric in row and pd.notna(row[metric]):
                if row[metric] > threshold:
                    condition = self.exporter.create_condition(row, condition_type)
                    conditions.append(condition)
        
        return conditions
    
    def export_state_ndjson(
        self, 
        state_abbrev: str, 
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Export all counties in a state as NDJSON.
        
        Args:
            state_abbrev: State abbreviation
            output_dir: Output directory
            
        Returns:
            Export summary
        """
        if self.exporter.df is None:
            return {"error": "Data not loaded"}
        
        # State mapping
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
        
        state_name = state_mapping.get(state_abbrev.upper(), state_abbrev)
        
        state_df = self.exporter.df[self.exporter.df["county_name"].str.contains(
            f", {state_name}$", regex=True, na=False
        )]
        
        if state_df.empty:
            return {"error": f"No counties found for state {state_abbrev}"}
        
        output_dir = Path(output_dir) / f"state_{state_abbrev.lower()}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Aggregate resources by type
        all_resources = {
            "Location": [],
            "Organization": [],
            "Group": [],
            "RiskAssessment": [],
            "Observation": [],
            "Condition": [],
            "CarePlan": [],
            "Consent": [],
            "Provenance": []
        }
        
        for _, row in state_df.iterrows():
            row_dict = row.to_dict()
            fips = row_dict.get("fips", "")
            
            all_resources["Location"].append(self.exporter.create_location(row_dict))
            all_resources["Organization"].append(self.exporter.create_organization(row_dict))
            all_resources["Group"].append(self.exporter.create_group(row_dict))
            all_resources["RiskAssessment"].append(self.exporter.create_risk_assessment(row_dict))
            all_resources["Observation"].extend(self._create_county_observations(row_dict))
            all_resources["Condition"].extend(self._create_county_conditions(row_dict))
            all_resources["CarePlan"].append(self.exporter.create_care_plan(row_dict))
            all_resources["Consent"].append(self.exporter.create_consent(row_dict))
            
            # Create provenance with references to all resources for this county
            resource_refs = [
                f"Location/location-{fips}",
                f"Organization/org-{fips}",
                f"Group/group-{fips}",
                f"RiskAssessment/risk-{fips}",
                f"CarePlan/careplan-{fips}",
                f"Consent/consent-{fips}"
            ]
            all_resources["Provenance"].append(
                self.exporter.create_provenance(row_dict, resource_refs)
            )
        
        # Write NDJSON files
        files_created = []
        for resource_type, resources in all_resources.items():
            if resources:
                file_path = output_dir / f"{resource_type}.ndjson"
                with open(file_path, 'w') as f:
                    for resource in resources:
                        f.write(json.dumps(resource) + '\n')
                files_created.append(str(file_path))
        
        return {
            "status": "success",
            "state": state_abbrev,
            "state_name": state_name,
            "counties": len(state_df),
            "output_directory": str(output_dir),
            "files_created": files_created,
            "resource_counts": {rt: len(rs) for rt, rs in all_resources.items()}
        }
    
    def create_export_manifest(
        self, 
        export_result: Dict[str, Any], 
        output_path: Path
    ) -> None:
        """
        Create FHIR Bulk Data Export manifest.
        
        Args:
            export_result: Export result dictionary
            output_path: Path for manifest file
        """
        manifest = {
            "transactionTime": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
            "request": f"$export?state={export_result.get('state', 'unknown')}",
            "requiresAccessToken": False,
            "output": [],
            "error": []
        }
        
        # Add output files
        for resource_type, count in export_result.get("resource_counts", {}).items():
            if count > 0:
                manifest["output"].append({
                    "type": resource_type,
                    "url": f"./{resource_type}.ndjson",
                    "count": count
                })
        
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)


if __name__ == "__main__":
    # Example usage
    exporter = EnhancedFHIRExporter()
    
    # Configure client
    config = FHIRConfig(server_base_url="http://localhost:8080/fhir")
    client = FHIRServerClient(config)
    
    # Initialize bulk exporter
    bulk_exporter = BulkFHIRExporter(exporter, client)
    
    # Export single county
    result = bulk_exporter.export_county_ndjson("29189", Path("./bulk_export"))
    print(json.dumps(result, indent=2))
