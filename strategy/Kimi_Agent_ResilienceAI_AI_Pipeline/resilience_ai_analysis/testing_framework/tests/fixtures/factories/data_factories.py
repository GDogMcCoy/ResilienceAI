"""
Test data factories for ResilienceAI

Provides factories for generating realistic test data using
the factory_boy pattern.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import random
import json


@dataclass
class CountyDataFactory:
    """Factory for generating test county data."""
    
    num_counties: int = 115  # Missouri counties
    state_fips: str = "29"
    random_seed: int = 42
    
    def __post_init__(self):
        np.random.seed(self.random_seed)
        random.seed(self.random_seed)
    
    def generate(self) -> pd.DataFrame:
        """Generate county data DataFrame."""
        counties = self._get_missouri_counties()
        
        # Generate correlated features
        population = np.random.lognormal(10, 1.5, self.num_counties).astype(int)
        uninsured_pct = np.clip(np.random.normal(12, 5, self.num_counties), 3, 35)
        poverty_rate = np.clip(np.random.normal(15, 7, self.num_counties), 5, 45)
        median_income = np.random.lognormal(10.8, 0.4, self.num_counties).astype(int)
        
        # Healthcare features (inversely correlated with poverty)
        physician_per_1000 = np.clip(
            3.0 - (poverty_rate / 20) + np.random.normal(0, 0.5, self.num_counties),
            0.2, 5.0
        )
        hospital_distance_miles = np.clip(
            10 + (poverty_rate / 2) + np.random.exponential(5, self.num_counties),
            2, 100
        )
        
        # Disaster risk features
        flood_risk_score = np.clip(np.random.beta(2, 5, self.num_counties) * 100, 0, 100)
        tornado_risk_score = np.clip(np.random.beta(3, 3, self.num_counties) * 100, 0, 100)
        historical_disaster_count = np.random.poisson(3, self.num_counties)
        
        # Demographic features
        elderly_pct = np.clip(np.random.normal(16, 4, self.num_counties), 5, 35)
        single_parent_pct = np.clip(np.random.normal(25, 8, self.num_counties), 10, 50)
        
        return pd.DataFrame({
            'fips': [f'{self.state_fips}{i:03d}' for i in range(1, self.num_counties + 1)],
            'county_name': [f"{c}, Missouri" for c in counties[:self.num_counties]],
            'latitude': np.random.uniform(36, 40.5, self.num_counties),
            'longitude': np.random.uniform(-95.7, -89, self.num_counties),
            'population': population,
            'uninsured_pct': uninsured_pct,
            'poverty_rate': poverty_rate,
            'median_income': median_income,
            'physician_per_1000': physician_per_1000,
            'hospital_distance_miles': hospital_distance_miles,
            'flood_risk_score': flood_risk_score,
            'tornado_risk_score': tornado_risk_score,
            'historical_disaster_count': historical_disaster_count,
            'elderly_pct': elderly_pct,
            'single_parent_pct': single_parent_pct,
        })
    
    def generate_with_engineered_features(self) -> pd.DataFrame:
        """Generate county data with engineered features."""
        df = self.generate()
        
        # Calculate healthcare gap score
        df['healthcare_gap_score'] = self._calculate_healthcare_gap_score(df)
        
        # Calculate disaster risk score
        df['disaster_risk_score'] = self._calculate_disaster_risk_score(df)
        
        # Calculate vulnerability index
        df['vulnerability_index'] = self._calculate_vulnerability_index(df)
        
        # Classify risk level
        df['risk_level'] = pd.cut(
            df['vulnerability_index'],
            bins=[0, 25, 50, 75, 100],
            labels=['Low', 'Medium', 'High', 'Critical']
        )
        
        return df
    
    def _calculate_healthcare_gap_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate healthcare gap score."""
        uninsured_norm = df['uninsured_pct'] / 35 * 40  # Max 40 points
        physician_norm = (5 - df['physician_per_1000']) / 5 * 35  # Max 35 points
        distance_norm = df['hospital_distance_miles'] / 100 * 25  # Max 25 points
        
        return np.clip(uninsured_norm + physician_norm + distance_norm, 0, 100)
    
    def _calculate_disaster_risk_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate disaster risk score."""
        flood_norm = df['flood_risk_score'] * 0.4
        tornado_norm = df['tornado_risk_score'] * 0.4
        history_norm = np.clip(df['historical_disaster_count'] / 10 * 20, 0, 20)
        
        return np.clip(flood_norm + tornado_norm + history_norm, 0, 100)
    
    def _calculate_vulnerability_index(self, df: pd.DataFrame) -> pd.Series:
        """Calculate overall vulnerability index."""
        healthcare_weight = 0.35
        disaster_weight = 0.35
        poverty_weight = 0.30
        
        poverty_norm = df['poverty_rate'] / 45 * 100
        
        return np.clip(
            df['healthcare_gap_score'] * healthcare_weight +
            df['disaster_risk_score'] * disaster_weight +
            poverty_norm * poverty_weight,
            0, 100
        )
    
    def _get_missouri_counties(self) -> List[str]:
        """Return list of Missouri county names."""
        return [
            "Adair", "Andrew", "Atchison", "Audrain", "Barry", "Barton", "Bates",
            "Benton", "Bollinger", "Boone", "Buchanan", "Butler", "Caldwell",
            "Callaway", "Camden", "Cape Girardeau", "Carroll", "Carter", "Cass",
            "Cedar", "Chariton", "Christian", "Clark", "Clay", "Clinton", "Cole",
            "Cooper", "Crawford", "Dade", "Dallas", "Daviess", "DeKalb", "Dent",
            "Douglas", "Dunklin", "Franklin", "Gasconade", "Gentry", "Greene",
            "Grundy", "Harrison", "Henry", "Hickory", "Holt", "Howard", "Howell",
            "Iron", "Jackson", "Jasper", "Jefferson", "Johnson", "Knox", "Laclede",
            "Lafayette", "Lawrence", "Lewis", "Lincoln", "Linn", "Livingston",
            "Macon", "Madison", "Maries", "Marion", "McDonald", "Mercer", "Miller",
            "Mississippi", "Moniteau", "Monroe", "Montgomery", "Morgan", "New Madrid",
            "Newton", "Nodaway", "Oregon", "Osage", "Ozark", "Pemiscot", "Perry",
            "Pettis", "Phelps", "Pike", "Platte", "Polk", "Pulaski", "Putnam",
            "Ralls", "Randolph", "Ray", "Reynolds", "Ripley", "Saline", "Schuyler",
            "Scotland", "Scott", "Shannon", "Shelby", "St. Charles", "St. Clair",
            "St. Francois", "St. Louis", "St. Louis City", "Ste. Genevieve",
            "Stoddard", "Stone", "Sullivan", "Taney", "Texas", "Vernon", "Warren",
            "Washington", "Wayne", "Webster", "Worth", "Wright"
        ]


@dataclass
class WeatherAlertFactory:
    """Factory for generating test weather alerts."""
    
    num_alerts: int = 5
    states: List[str] = field(default_factory=lambda: ["MO"])
    
    def generate(self) -> List[Dict[str, Any]]:
        """Generate list of weather alerts."""
        events = [
            'Tornado Warning', 'Severe Thunderstorm Warning', 
            'Flash Flood Warning', 'Winter Storm Warning',
            'Heat Advisory', 'Wind Advisory'
        ]
        severities = ['Minor', 'Moderate', 'Severe', 'Extreme']
        
        alerts = []
        for i in range(self.num_alerts):
            effective = datetime.utcnow()
            expires = effective + timedelta(hours=np.random.randint(1, 6))
            
            alerts.append({
                'id': f'alert-{i:04d}',
                'event': np.random.choice(events),
                'severity': np.random.choice(severities),
                'areaDesc': f'Test County {i}, {np.random.choice(self.states)}',
                'effective': effective.isoformat() + 'Z',
                'expires': expires.isoformat() + 'Z',
                'senderName': 'NWS Test Office',
                'headline': f'{np.random.choice(events)} issued for Test County {i}',
                'description': f'This is a test alert description for alert {i}. '
                              f'Please take appropriate precautions.',
                'instruction': 'Seek shelter immediately.',
                'parameters': {
                    'tornadoDetection': 'RADAR INDICATED' if 'Tornado' in np.random.choice(events) else None,
                    'hailSize': '1.00' if 'Thunderstorm' in np.random.choice(events) else None,
                }
            })
        
        return alerts
    
    def generate_geojson(self) -> Dict[str, Any]:
        """Generate GeoJSON format alerts."""
        alerts = self.generate()
        
        return {
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'properties': alert,
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [self._generate_polygon_coords(i)]
                    }
                }
                for i, alert in enumerate(alerts)
            ]
        }
    
    def _generate_polygon_coords(self, index: int) -> List[List[float]]:
        """Generate polygon coordinates for alert area."""
        base_lat = 38.6 + (index % 5) * 0.1
        base_lon = -90.5 + (index // 5) * 0.1
        
        return [
            [base_lon, base_lat],
            [base_lon + 0.1, base_lat],
            [base_lon + 0.1, base_lat + 0.1],
            [base_lon, base_lat + 0.1],
            [base_lon, base_lat]
        ]


@dataclass
class ModelPredictionFactory:
    """Factory for generating model predictions."""
    
    num_samples: int = 100
    num_features: int = 66
    random_seed: int = 42
    
    def __post_init__(self):
        np.random.seed(self.random_seed)
    
    def generate_features(self) -> pd.DataFrame:
        """Generate feature matrix."""
        feature_names = [
            'population', 'uninsured_pct', 'poverty_rate', 'median_income',
            'physician_per_1000', 'hospital_distance_miles', 'flood_risk_score',
            'tornado_risk_score', 'historical_disaster_count', 'elderly_pct',
            'single_parent_pct'
        ]
        
        # Add more features to reach num_features
        for i in range(len(feature_names), self.num_features):
            feature_names.append(f'feature_{i}')
        
        return pd.DataFrame(
            np.random.randn(self.num_samples, self.num_features),
            columns=feature_names[:self.num_features]
        )
    
    def generate_predictions(self) -> np.ndarray:
        """Generate prediction probabilities."""
        return np.random.beta(2, 2, self.num_samples)
    
    def generate_with_labels(self) -> tuple:
        """Generate features and labels."""
        X = self.generate_features()
        
        # Generate labels with some correlation to features
        y = np.random.binomial(1, 0.3, self.num_samples)
        
        return X, y
    
    def generate_prediction_results(self) -> pd.DataFrame:
        """Generate complete prediction results."""
        X = self.generate_features()
        predictions = self.generate_predictions()
        
        return pd.DataFrame({
            'sample_id': range(self.num_samples),
            'predicted_probability': predictions,
            'predicted_class': (predictions > 0.5).astype(int),
            'confidence': np.abs(predictions - 0.5) * 2,
        })


@dataclass
class AgentQueryFactory:
    """Factory for generating agent queries."""
    
    num_queries: int = 10
    
    def generate(self) -> List[Dict[str, Any]]:
        """Generate agent queries."""
        query_templates = [
            "What is the vulnerability score for {county}?",
            "Assess disaster risk in {county}",
            "Show healthcare gaps in {county}",
            "Compare {county1} and {county2} vulnerability",
            "What are the top risk factors for {county}?",
            "Generate a report for {county}",
            "What disasters have affected {county}?",
            "Show me the weather alerts for {county}",
            "Predict risk for {county} next year",
            "What interventions are recommended for {county}?",
        ]
        
        counties = ['St. Louis', 'Jackson', 'Greene', 'Clay', 'Jefferson', 
                   'Boone', 'Jasper', 'Cape Girardeau']
        
        queries = []
        for i in range(self.num_queries):
            template = np.random.choice(query_templates)
            county = np.random.choice(counties)
            
            query = template.format(
                county=county,
                county1=county,
                county2=np.random.choice(counties)
            )
            
            queries.append({
                'id': f'query-{i:04d}',
                'query': query,
                'timestamp': datetime.utcnow().isoformat(),
                'context': {
                    'state': 'Missouri',
                    'county': county
                }
            })
        
        return queries


@dataclass
class FHIRResourceFactory:
    """Factory for generating FHIR resources."""
    
    num_resources: int = 10
    
    def generate_patient(self, index: int) -> Dict[str, Any]:
        """Generate a FHIR Patient resource."""
        return {
            "resourceType": "Patient",
            "id": f"patient-{index:04d}",
            "identifier": [
                {
                    "system": "http://hospital.smarthealthit.org",
                    "value": f"{index:08d}"
                }
            ],
            "name": [
                {
                    "use": "official",
                    "family": f"TestFamily{index}",
                    "given": [f"TestGiven{index}"]
                }
            ],
            "gender": np.random.choice(['male', 'female']),
            "birthDate": f"{np.random.randint(1940, 2010)}-{np.random.randint(1, 13):02d}-{np.random.randint(1, 29):02d}",
            "address": [
                {
                    "use": "home",
                    "line": [f"{np.random.randint(100, 9999)} Test St"],
                    "city": "Test City",
                    "state": "MO",
                    "postalCode": f"{np.random.randint(63000, 66000)}"
                }
            ]
        }
    
    def generate_observation(self, patient_id: str, index: int) -> Dict[str, Any]:
        """Generate a FHIR Observation resource."""
        observation_types = [
            ("8302-2", "Body Height", "cm", np.random.randint(150, 200)),
            ("29463-7", "Body Weight", "kg", np.random.randint(50, 120)),
            ("39156-5", "BMI", "kg/m2", np.random.uniform(18, 35)),
        ]
        
        obs_type = np.random.choice(observation_types)
        
        return {
            "resourceType": "Observation",
            "id": f"observation-{index:04d}",
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": obs_type[0],
                        "display": obs_type[1]
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": datetime.utcnow().isoformat(),
            "valueQuantity": {
                "value": obs_type[3],
                "unit": obs_type[2],
                "system": "http://unitsofmeasure.org"
            }
        }
    
    def generate_bundle(self) -> Dict[str, Any]:
        """Generate a FHIR Bundle."""
        entries = []
        
        for i in range(self.num_resources):
            patient = self.generate_patient(i)
            entries.append({
                "fullUrl": f"Patient/{patient['id']}",
                "resource": patient
            })
            
            # Add some observations
            for j in range(np.random.randint(1, 4)):
                obs = self.generate_observation(patient['id'], i * 10 + j)
                entries.append({
                    "fullUrl": f"Observation/{obs['id']}",
                    "resource": obs
                })
        
        return {
            "resourceType": "Bundle",
            "id": "test-bundle",
            "type": "collection",
            "entry": entries
        }


# Utility functions
def save_test_data(df: pd.DataFrame, filename: str, output_dir: str = "tests/fixtures/data"):
    """Save test data to CSV file."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False)
    print(f"Saved test data to {filepath}")


def load_test_data(filename: str, input_dir: str = "tests/fixtures/data") -> pd.DataFrame:
    """Load test data from CSV file."""
    import os
    filepath = os.path.join(input_dir, filename)
    return pd.read_csv(filepath)


def generate_all_fixtures():
    """Generate all test fixtures."""
    # County data
    county_factory = CountyDataFactory()
    counties = county_factory.generate_with_engineered_features()
    save_test_data(counties, "county_features.csv")
    
    # Weather alerts
    weather_factory = WeatherAlertFactory()
    alerts = weather_factory.generate()
    with open("tests/fixtures/data/weather_alerts.json", 'w') as f:
        json.dump(alerts, f, indent=2)
    
    # Model predictions
    model_factory = ModelPredictionFactory()
    predictions = model_factory.generate_prediction_results()
    save_test_data(predictions, "model_predictions.csv")
    
    print("All fixtures generated successfully!")


if __name__ == "__main__":
    generate_all_fixtures()
