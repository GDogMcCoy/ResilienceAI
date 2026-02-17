"""
ResilienceAI Infrastructure Analysis - Configuration
Configuration settings for infrastructure analysis module
"""

from typing import Dict, List, Optional
from pathlib import Path


class InfrastructureConfig:
    """Configuration for infrastructure analysis"""
    
    # Facility types supported
    FACILITY_TYPES = [
        'hospitals',
        'fire_stations',
        'ems_stations',
        'nursing_homes',
        'urgent_care',
        'clinics',
        'pharmacies',
        'shelters'
    ]
    
    # Coverage benchmarks by facility type (km)
    COVERAGE_BENCHMARKS = {
        'hospitals': 25,
        'hospital': 25,
        'fire_stations': 15,
        'fire_station': 15,
        'ems_stations': 20,
        'ems_station': 20,
        'nursing_homes': 30,
        'nursing_home': 30,
        'urgent_care': 15,
        'clinic': 20,
        'pharmacy': 10,
        'shelter': 25,
    }
    
    # Estimated facility costs (in millions USD)
    FACILITY_COSTS = {
        'hospitals': 50.0,
        'hospital': 50.0,
        'fire_stations': 2.5,
        'fire_station': 2.5,
        'ems_stations': 1.5,
        'ems_station': 1.5,
        'nursing_homes': 10.0,
        'nursing_home': 10.0,
        'urgent_care': 3.0,
        'clinic': 1.0,
        'pharmacy': 0.5,
        'shelter': 1.0,
    }
    
    # Annual operating costs as % of capital cost
    OPERATING_COST_PCT = {
        'hospitals': 0.15,
        'hospital': 0.15,
        'fire_stations': 0.10,
        'fire_station': 0.10,
        'ems_stations': 0.12,
        'ems_station': 0.12,
        'nursing_homes': 0.20,
        'nursing_home': 0.20,
        'urgent_care': 0.15,
        'clinic': 0.12,
        'pharmacy': 0.10,
        'shelter': 0.08,
    }
    
    # Annual benefit per person served (USD)
    BENEFIT_PER_PERSON = {
        'hospitals': 500,
        'hospital': 500,
        'fire_stations': 200,
        'fire_station': 200,
        'ems_stations': 300,
        'ems_station': 300,
        'nursing_homes': 400,
        'nursing_home': 400,
        'urgent_care': 250,
        'clinic': 150,
        'pharmacy': 100,
        'shelter': 150,
    }
    
    # Network analysis defaults
    NETWORK_DEFAULTS = {
        'default_radius_km': 80,
        'connectivity_km': 50,
        'use_road_network': False,
        'max_edge_computation': 200,
    }
    
    # Gap identification defaults
    GAP_DEFAULTS = {
        'min_population': 1000,
        'critical_ratio': 3.0,
        'high_ratio': 2.0,
        'medium_ratio': 1.5,
    }
    
    # Investment optimization defaults
    INVESTMENT_DEFAULTS = {
        'default_budget_millions': 100.0,
        'time_horizon_years': 10,
        'discount_rate': 0.05,
        'min_population_per_facility': 10000,
    }
    
    # Vulnerability scoring weights
    VULNERABILITY_WEIGHTS = {
        'network_density': 0.25,
        'fragmentation': 0.20,
        'articulation_points': 0.20,
        'clustering': 0.15,
        'betweenness_concentration': 0.20,
    }
    
    # Real-time status sources
    STATUS_SOURCES = [
        {
            'name': 'hifld',
            'url': 'https://hifld-geoplatform.opendata.arcgis.com/api/',
            'update_interval': 86400,  # Daily
        },
        {
            'name': 'cms_nursing_homes',
            'url': 'https://data.cms.gov/provider-data/api/',
            'update_interval': 604800,  # Weekly
        }
    ]
    
    # File paths
    DEFAULT_PATHS = {
        'data_dir': 'data',
        'raw_dir': 'data/raw',
        'processed_dir': 'data/processed',
        'output_dir': 'outputs/infrastructure',
        'cache_dir': 'data/cache',
    }
    
    @classmethod
    def get_benchmark(cls, facility_type: str) -> float:
        """Get coverage benchmark for facility type"""
        return cls.COVERAGE_BENCHMARKS.get(facility_type, 25.0)
    
    @classmethod
    def get_facility_cost(cls, facility_type: str) -> float:
        """Get estimated cost for facility type"""
        return cls.FACILITY_COSTS.get(facility_type, 1.0)
    
    @classmethod
    def get_operating_cost_pct(cls, facility_type: str) -> float:
        """Get operating cost percentage for facility type"""
        return cls.OPERATING_COST_PCT.get(facility_type, 0.1)
    
    @classmethod
    def get_benefit_per_person(cls, facility_type: str) -> int:
        """Get annual benefit per person for facility type"""
        return cls.BENEFIT_PER_PERSON.get(facility_type, 200)
    
    @classmethod
    def create_default_config(cls) -> Dict:
        """Create default configuration dictionary"""
        return {
            'facility_types': cls.FACILITY_TYPES,
            'coverage_benchmarks': cls.COVERAGE_BENCHMARKS,
            'facility_costs': cls.FACILITY_COSTS,
            'operating_cost_pct': cls.OPERATING_COST_PCT,
            'benefit_per_person': cls.BENEFIT_PER_PERSON,
            'network': cls.NETWORK_DEFAULTS,
            'gap': cls.GAP_DEFAULTS,
            'investment': cls.INVESTMENT_DEFAULTS,
            'vulnerability_weights': cls.VULNERABILITY_WEIGHTS,
            'status_sources': cls.STATUS_SOURCES,
            'paths': cls.DEFAULT_PATHS,
        }


# Integration with existing ResilienceAI config
INFRASTRUCTURE_CONFIG_ADDITION = {
    'infrastructure': {
        'enabled': True,
        'facility_types': ['hospitals', 'fire_stations', 'ems_stations', 'nursing_homes'],
        'coverage_benchmarks': {
            'hospitals': 25,
            'fire_stations': 15,
            'ems_stations': 20,
            'nursing_homes': 30,
        },
        'network_analysis': {
            'default_radius_km': 80,
            'connectivity_km': 50,
            'use_road_network': False,
        },
        'gap_analysis': {
            'min_population': 1000,
            'severity_thresholds': {
                'critical': 3.0,
                'high': 2.0,
                'medium': 1.5,
            }
        },
        'investment_optimization': {
            'default_budget_millions': 100.0,
            'time_horizon_years': 10,
            'discount_rate': 0.05,
        },
        'real_time_status': {
            'enabled': False,
            'update_interval_minutes': 15,
            'sources': []
        }
    }
}


# API endpoint definitions for infrastructure module
INFRASTRUCTURE_API_ENDPOINTS = {
    'GET /api/v1/infrastructure/network/{county_fips}': {
        'description': 'Get network analysis for county',
        'parameters': {
            'county_fips': 'County FIPS code',
            'radius_km': 'Optional: Analysis radius (default: 80)'
        },
        'response': {
            'total_facilities': 'int',
            'network_density': 'float',
            'connected_components': 'int',
            'vulnerability_score': 'float',
            'critical_facilities': 'list'
        }
    },
    'GET /api/v1/infrastructure/gaps': {
        'description': 'Get all coverage gaps',
        'parameters': {
            'state': 'Optional: Filter by state',
            'severity': 'Optional: Filter by severity (critical, high, medium, low)',
            'facility_type': 'Optional: Filter by facility type'
        },
        'response': 'List of coverage gaps'
    },
    'POST /api/v1/infrastructure/optimize': {
        'description': 'Optimize infrastructure investments',
        'body': {
            'budget_millions': 'float',
            'objective': 'string (coverage, risk, roi, balanced)',
            'constraints': 'Optional: Additional constraints'
        },
        'response': 'Investment recommendations'
    },
    'GET /api/v1/infrastructure/status/{facility_id}': {
        'description': 'Get real-time facility status',
        'response': 'Facility status update'
    },
    'GET /api/v1/infrastructure/briefing/{state}': {
        'description': 'Get infrastructure briefing',
        'response': 'Natural language briefing (markdown)'
    },
    'POST /api/v1/infrastructure/analyze': {
        'description': 'Run infrastructure analysis for counties',
        'body': {
            'county_fips_list': 'list of FIPS codes',
            'analysis_type': 'string (network, gaps, full)'
        },
        'response': 'Analysis results'
    }
}


# Dashboard widget configuration
DASHBOARD_WIDGETS = {
    'infrastructure_network_map': {
        'title': 'Infrastructure Network',
        'type': 'map',
        'data_sources': ['network_analysis'],
        'visualization': 'network_graph'
    },
    'coverage_gap_heatmap': {
        'title': 'Coverage Gap Heatmap',
        'type': 'heatmap',
        'data_sources': ['gap_analysis'],
        'visualization': 'choropleth'
    },
    'vulnerability_scorecard': {
        'title': 'Vulnerability Scorecard',
        'type': 'scorecard',
        'data_sources': ['network_analysis'],
        'metrics': ['vulnerability_score', 'resilience_score', 'critical_facilities']
    },
    'investment_optimizer': {
        'title': 'Investment Optimizer',
        'type': 'interactive',
        'data_sources': ['investment_analysis'],
        'controls': ['budget_slider', 'objective_selector']
    },
    'facility_status_monitor': {
        'title': 'Facility Status Monitor',
        'type': 'real_time',
        'data_sources': ['status_tracker'],
        'alerts': ['overcapacity', 'closure', 'damage']
    }
}
