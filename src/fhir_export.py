"""
ResilienceAI - FHIR Export Module
Export vulnerability data in FHIR R4 format for health system integration.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pandas as pd
import datetime
from pathlib import Path
from config import PROCESSED_DIR, REPORTS_DIR


class FHIRExporter:
    """Export county vulnerability data as FHIR R4 resources."""

    FHIR_VERSION = "4.0.1"
    PROFILE_URL = "http://hl7.org/fhir/us/sdoh-clinicalcare/StructureDefinition/SDOHCC-Condition"

    def __init__(self, df=None):
        if df is None:
            path = PROCESSED_DIR / "county_features.csv"
            if path.exists():
                self.df = pd.read_csv(path, dtype={"fips": str})
            else:
                self.df = None
        else:
            self.df = df

    def _create_bundle(self, resources, bundle_type="collection"):
        """Create a FHIR Bundle resource."""
        return {
            "resourceType": "Bundle",
            "id": f"resilienceai-export-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "meta": {
                "versionId": "1",
                "lastUpdated": datetime.datetime.now().isoformat() + "Z"
            },
            "identifier": {
                "system": "https://resilienceai.io/fhir/bundle-id",
                "value": f"rai-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
            },
            "type": bundle_type,
            "timestamp": datetime.datetime.now().isoformat() + "Z",
            "entry": [{"resource": r} for r in resources]
        }

    def _risk_level_to_coding(self, risk_level):
        """Map risk level to FHIR coding."""
        mapping = {
            "High": {
                "system": "http://hl7.org/fhir/risk-assessment-severity",
                "code": "high",
                "display": "High Risk"
            },
            "Medium": {
                "system": "http://hl7.org/fhir/risk-assessment-severity",
                "code": "moderate",
                "display": "Moderate Risk"
            },
            "Low": {
                "system": "http://hl7.org/fhir/risk-assessment-severity",
                "code": "low",
                "display": "Low Risk"
            }
        }
        return mapping.get(risk_level, mapping["Low"])

    def county_to_location(self, row):
        """Convert county data to FHIR Location resource."""
        fips = row.get("fips", "")
        county_name = row.get("county_name", "Unknown")
        state = county_name.split(", ")[-1] if ", " in county_name else ""

        return {
            "resourceType": "Location",
            "id": f"location-county-{fips}",
            "identifier": [{
                "system": "https://www.census.gov/geographies/reference-files.html",
                "value": fips,
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "FIPS",
                        "display": "FIPS County Code"
                    }]
                }
            }],
            "status": "active",
            "name": county_name,
            "description": f"US County - {county_name}",
            "mode": "instance",
            "type": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                    "code": "COMM",
                    "display": "Community"
                }]
            }],
            "address": {
                "country": "USA",
                "state": state
            },
            "position": {
                "longitude": float(row.get("longitude", 0)),
                "latitude": float(row.get("latitude", 0))
            }
        }

    def county_to_risk_assessment(self, row):
        """Convert county data to FHIR RiskAssessment resource."""
        fips = row.get("fips", "")
        county_name = row.get("county_name", "Unknown")
        risk_score = float(row.get("risk_score", 0))
        risk_level = row.get("risk_level", "Low")

        # Build prediction basis
        basis = []

        # Vulnerability component
        vuln_idx = float(row.get("vulnerability_index", 0))
        basis.append({
            "reference": f"#vuln-{fips}",
            "display": f"Vulnerability Index: {vuln_idx:.3f}"
        })

        # Isolation component
        iso_idx = float(row.get("isolation_index", 0))
        basis.append({
            "reference": f"#iso-{fips}",
            "display": f"Isolation Index: {iso_idx:.3f}"
        })

        # Disaster history
        disaster_count = int(row.get("disaster_count", 0))
        basis.append({
            "reference": f"#disaster-{fips}",
            "display": f"Historical Disasters: {disaster_count}"
        })

        return {
            "resourceType": "RiskAssessment",
            "id": f"risk-county-{fips}",
            "identifier": [{
                "system": "https://resilienceai.io/fhir/risk-id",
                "value": f"rai-risk-{fips}"
            }],
            "status": "final",
            "subject": {
                "reference": f"Location/location-county-{fips}",
                "display": county_name
            },
            "occurrenceDateTime": datetime.datetime.now().isoformat() + "Z",
            "method": {
                "coding": [{
                    "system": "https://resilienceai.io/fhir/risk-method",
                    "code": "composite-ml",
                    "display": "Composite ML Risk Score"
                }],
                "text": "Weighted composite of vulnerability (40%), isolation (30%), and disaster exposure (30%)"
            },
            "basis": basis,
            "prediction": [{
                "outcome": {
                    "coding": [{
                        "system": "http://snomed.info/sct",
                        "code": "102455003",
                        "display": "Disaster vulnerability"
                    }],
                    "text": "Disaster Vulnerability Risk"
                },
                "probabilityDecimal": risk_score,
                "qualitativeRisk": self._risk_level_to_coding(risk_level),
                "rationale": f"Risk score {risk_score:.3f} based on demographic vulnerability, infrastructure access, and historical disaster frequency"
            }],
            "mitigation": row.get("top_intervention", "No specific intervention identified")
        }

    def county_to_observations(self, row):
        """Convert county metrics to FHIR Observation resources."""
        fips = row.get("fips", "")
        county_name = row.get("county_name", "Unknown")
        observations = []

        # Define observations to export
        obs_definitions = [
            ("vulnerability_index", "Vulnerability Index", "{:.3f}", None),
            ("isolation_index", "Infrastructure Isolation Index", "{:.3f}", None),
            ("poverty_pct", "Poverty Rate", "{:.1f}", "%"),
            ("elderly_pct", "Elderly Population Percentage", "{:.1f}", "%"),
            ("disability_pct", "Disability Rate", "{:.1f}", "%"),
            ("uninsured_pct", "Uninsured Rate", "{:.1f}", "%"),
            ("disaster_count", "Historical Disaster Count", "{:d}", None),
            ("disaster_count_recent", "Recent Disaster Count (2015+)", "{:d}", None),
            ("compound_risk_count", "Compound Risk Dimensions", "{:d}", None),
            ("dist_nearest_hospitals_km", "Distance to Nearest Hospital", "{:.1f}", "km"),
        ]

        for col, display, fmt, unit in obs_definitions:
            if col in row and pd.notna(row[col]):
                value = row[col]
                value_str = fmt.format(value)

                obs = {
                    "resourceType": "Observation",
                    "id": f"obs-{col}-{fips}",
                    "status": "final",
                    "category": [{
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "survey",
                            "display": "Survey"
                        }]
                    }],
                    "code": {
                        "coding": [{
                            "system": "https://resilienceai.io/fhir/observation-code",
                            "code": col,
                            "display": display
                        }],
                        "text": display
                    },
                    "subject": {
                        "reference": f"Location/location-county-{fips}",
                        "display": county_name
                    },
                    "effectiveDateTime": datetime.datetime.now().isoformat() + "Z",
                    "valueQuantity": {
                        "value": float(value),
                        "unit": unit if unit else "1",
                        "system": "http://unitsofmeasure.org",
                        "code": unit if unit else "1"
                    }
                }
                observations.append(obs)

        return observations

    def export_county(self, fips, format="json"):
        """Export a single county as FHIR resources."""
        if self.df is None:
            return {"error": "Data not loaded"}

        match = self.df[self.df["fips"] == str(fips)]
        if match.empty:
            return {"error": f"County {fips} not found"}

        row = match.iloc[0]

        # Generate resources
        resources = []
        resources.append(self.county_to_location(row))
        resources.append(self.county_to_risk_assessment(row))
        resources.extend(self.county_to_observations(row))

        bundle = self._create_bundle(resources)

        if format == "json":
            return bundle
        elif format == "file":
            output_path = REPORTS_DIR / f"fhir-county-{fips}.json"
            with open(output_path, "w") as f:
                json.dump(bundle, f, indent=2)
            return {"output_path": str(output_path), "resources": len(resources)}
        else:
            return bundle

    def export_state(self, state_abbrev, format="json"):
        """Export all counties in a state as FHIR resources."""
        if self.df is None:
            return {"error": "Data not loaded"}

        state_df = self.df[self.df["county_name"].str.contains(
            f", {state_abbrev}$", regex=True, na=False
        )]

        if state_df.empty:
            return {"error": f"No counties found for state {state_abbrev}"}

        all_resources = []
        for _, row in state_df.iterrows():
            all_resources.append(self.county_to_location(row))
            all_resources.append(self.county_to_risk_assessment(row))
            all_resources.extend(self.county_to_observations(row))

        bundle = self._create_bundle(all_resources)

        if format == "json":
            return bundle
        elif format == "file":
            output_path = REPORTS_DIR / f"fhir-state-{state_abbrev}.json"
            with open(output_path, "w") as f:
                json.dump(bundle, f, indent=2)
            return {
                "output_path": str(output_path),
                "counties": len(state_df),
                "resources": len(all_resources)
            }
        else:
            return bundle

    def export_high_risk(self, risk_threshold=0.7, format="json"):
        """Export all high-risk counties as FHIR resources."""
        if self.df is None:
            return {"error": "Data not loaded"}

        high_risk_df = self.df[self.df["risk_score"] >= risk_threshold]

        all_resources = []
        for _, row in high_risk_df.iterrows():
            all_resources.append(self.county_to_location(row))
            all_resources.append(self.county_to_risk_assessment(row))
            all_resources.extend(self.county_to_observations(row))

        bundle = self._create_bundle(all_resources)

        if format == "json":
            return bundle
        elif format == "file":
            output_path = REPORTS_DIR / f"fhir-high-risk-{risk_threshold}.json"
            with open(output_path, "w") as f:
                json.dump(bundle, f, indent=2)
            return {
                "output_path": str(output_path),
                "counties": len(high_risk_df),
                "resources": len(all_resources)
            }
        else:
            return bundle


def main():
    """CLI for FHIR export."""
    import argparse

    parser = argparse.ArgumentParser(description="Export ResilienceAI data as FHIR R4")
    parser.add_argument("--county", help="Export specific county by FIPS")
    parser.add_argument("--state", help="Export all counties in state")
    parser.add_argument("--high-risk", action="store_true", help="Export high-risk counties")
    parser.add_argument("--threshold", type=float, default=0.7, help="Risk threshold")
    parser.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    exporter = FHIRExporter()

    if args.county:
        result = exporter.export_county(args.county, format="file")
        print(f"Exported to: {result.get('output_path', 'N/A')}")
    elif args.state:
        result = exporter.export_state(args.state, format="file")
        print(f"Exported {result.get('counties', 0)} counties to: {result.get('output_path', 'N/A')}")
    elif args.high_risk:
        result = exporter.export_high_risk(args.threshold, format="file")
        print(f"Exported {result.get('counties', 0)} high-risk counties to: {result.get('output_path', 'N/A')}")
    else:
        print("Usage: python fhir_export.py --county FIPS | --state STATE | --high-risk")


if __name__ == "__main__":
    main()
