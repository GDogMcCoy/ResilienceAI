---
title: Changelog
description: Version history and release notes for ResilienceAI
---

# Changelog

All notable changes to ResilienceAI are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New features in development

### Changed
- Changes to existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security improvements

---

## [2.0.0] - 2026-02-17

### 🎯 Release Highlights

ResilienceAI 2.0 "Claw" introduces multi-agent orchestration, Google Earth Engine integration, and expands from 45 to 56 MCP tools. This release represents a major architectural evolution from single-agent to multi-agent system.

### ✨ Added

#### Multi-Agent Orchestration
- **4 Specialist Agents**: Climate, Vulnerability, Realtime, and Planning agents
- **Agent Orchestrator**: Central routing and coordination system
- **Tool Distribution**: 56 MCP tools across 4 agents
- **Inter-Agent Communication**: Shared state and message passing

#### Google Earth Engine Integration
- **Satellite Intelligence**: 30m-4km resolution imagery
- **Land Surface Temperature (LST)**: Thermal monitoring
- **NDVI Vegetation Index**: Crop and vegetation health
- **PDSI Drought Index**: Palmer Drought Severity Index
- **Nighttime Lights**: Economic activity proxy
- **Surface Water**: Water body detection
- **Burned Area**: Fire scar mapping

#### Climate Intelligence
- **RCC-ACIS Integration**: 4km PRISM grid climate data
- **High-Resolution Trends**: Daily temperature and precipitation
- **Degree Day Calculations**: Heating and cooling degree days
- **Extreme Event Tracking**: Heat waves, cold snaps, heavy precipitation

#### New Data Sources
- **FEMA National Risk Index**: 18 hazard types, expected annual loss
- **USGS NWIS**: Streamflow and flood frequency data
- **US Drought Monitor**: Weekly D0-D4 drought classification
- **NOAA SWDI/SPC**: Severe weather event database

#### Agricultural Vulnerability
- **USDA NASS Integration**: Crop yield and production data
- **Crop-Specific Analysis**: Corn, soybeans, wheat, cotton
- **Agricultural Risk Scoring**: Climate + market vulnerability
- **Yield Forecasting**: Seasonal production predictions

#### Real-Time Alert System
- **Multi-Channel Notifications**: Webhook, email, SMS
- **Configurable Thresholds**: Customizable risk alert levels
- **Subscription Management**: County-level alert subscriptions
- **Alert History**: Historical alert tracking and analysis

#### Executive Briefings
- **Auto-Generated Reports**: PDF, PPTX, and text formats
- **Customizable Templates**: Branded report generation
- **Multi-County Briefings**: Regional and state-level summaries
- **Scheduled Delivery**: Automated report distribution

### 🔧 Changed

#### Feature Engineering
- **37 → 66 Features**: 78% increase in vulnerability metrics
- **New Composite Indices**: Compound risk, infrastructure redundancy
- **Population-Weighted Metrics**: Lives-affected prioritization
- **State Percentile Rankings**: Contextual risk comparison
- **Disaster Acceleration**: Frequency trend detection

#### Machine Learning
- **Enhanced Ensemble**: Improved model performance
- **New Predictive Models**: Climate scenario projections
- **Batch Forecasting**: Multi-county simultaneous predictions
- **Model Versioning**: Tracked model artifacts

#### Dashboard
- **16 Tabs**: Comprehensive analysis interface
- **3D Visualizations**: Three-dimensional risk mapping
- **Choropleth Maps**: County-level color-coded maps
- **Interactive Charts**: Plotly-powered visualizations
- **Export Integration**: Direct export from dashboard

### 🐛 Fixed

- **County Filtering**: Fixed Missouri focus filtering
- **3D Visualization**: Resolved stability issues
- **ACIS Grid Parsing**: Corrected coordinate handling
- **State Filter Bug**: Fixed multi-state query issues
- **ZIP-to-County Lookup**: Improved geocoding accuracy

### 🔒 Security

- **API Key Rotation**: Support for rotating external API keys
- **Enhanced Validation**: Stricter input validation
- **Audit Logging**: Security event tracking
- **Dependency Updates**: Security patch updates

### 📊 Performance

- **Caching Layer**: Redis-compatible caching
- **Lazy Loading**: On-demand data fetching
- **Query Optimization**: Faster county lookups
- **Memory Management**: Reduced memory footprint

### 📚 Documentation

- **Comprehensive API Reference**: All 56 MCP tools documented
- **Architecture Diagrams**: System design visualization
- **Video Tutorials**: Step-by-step video guides
- **Data Dictionary**: Complete feature documentation
- **Deployment Guides**: Production deployment instructions

---

## [1.1.0] - 2026-02-15

### Added
- **Intervention ROI Calculator**: Cost-effectiveness analysis for 6 intervention types
- **Scenario Simulator**: What-if disaster modeling
- **Network Analysis**: Infrastructure cascade failure modeling
- **Executive Briefings**: PDF and PPTX generation
- **Spatial Statistics**: Spatial autocorrelation analysis

### Changed
- Improved ensemble model accuracy by 12%
- Enhanced dashboard performance
- Updated dependencies to latest versions

### Fixed
- Memory leak in feature engineering pipeline
- Race condition in concurrent data downloads
- Incorrect risk score calculation for edge cases

---

## [1.0.0] - 2026-02-14

### 🎉 Initial Release

First public release of ResilienceAI for the MUIDSI Hackathon 2026.

### ✨ Features

#### Core Platform
- **45 MCP Tools**: Composable analysis tools
- **Single-Agent Architecture**: Unified agent system
- **5 Data Sources**: FEMA, Census, HIFLD, CMS, NOAA
- **County-Level Analysis**: 3,222 US counties
- **66 Features**: Comprehensive vulnerability metrics

#### Data Integration
- **FEMA Disaster Declarations**: 69,615 historical records
- **Census ACS 5-Year**: 2022 demographic data
- **HIFLD Infrastructure**: 81,305 facilities
- **CMS Nursing Homes**: 14,713 facilities
- **NOAA NWS**: Real-time weather alerts

#### Machine Learning
- **Ensemble Models**: Logistic Regression, Random Forest, Gradient Boosting, Neural Network
- **Prophet Forecasting**: Time-series risk prediction
- **ARIMA Models**: Alternative forecasting approach
- **Soft Voting**: Combined model predictions

#### Dashboard
- **Streamlit Interface**: Interactive web dashboard
- **Missouri Focus**: 115 Missouri counties prioritized
- **Risk Visualization**: Maps, charts, and tables
- **Export Formats**: FHIR R4, GeoJSON

#### Agent System
- **Natural Language Queries**: Conversational interface
- **Tool Composition**: Chain multiple tools
- **Context Awareness**: Multi-turn conversations
- **Archia Integration**: LLM-powered responses

### 📚 Documentation
- README with quick start guide
- Basic API reference for external data sources
- Setup and installation guide
- Data dictionary for 66 features

---

## Version History Summary

| Version | Date | Codename | Key Features |
|---------|------|----------|--------------|
| 2.0.0 | 2026-02-17 | "Claw" | Multi-agent, GEE integration, 56 tools |
| 1.1.0 | 2026-02-15 | - | ROI calculator, scenario simulation |
| 1.0.0 | 2026-02-14 | "Genesis" | Initial release, 45 tools |

---

## Release Schedule

| Version | Target Date | Focus Area |
|---------|-------------|------------|
| 2.1.0 | 2026-03-01 | Performance optimization |
| 2.2.0 | 2026-03-15 | Additional data sources |
| 3.0.0 | 2026-04-01 | API v2, breaking changes |

---

## Deprecation Notices

### Deprecated in 2.0.0
- `single_agent_mode` parameter (use `orchestrator_mode` instead)
- `legacy_risk_score` calculation method
- Direct agent instantiation (use AgentOrchestrator)

### Planned for Removal in 3.0.0
- Python 3.9 support
- Deprecated API endpoints
- Legacy export formats

---

## Migration Guides

### Upgrading from 1.x to 2.0

See [Migration Guide](https://resilienceai.readthedocs.io/reference/migration-1-to-2.html) for detailed instructions.

Key changes:
1. Use `AgentOrchestrator` instead of direct agent instantiation
2. Update tool calls to use new agent-specific routing
3. Configure GEE credentials for satellite features
4. Update dashboard configuration for 16-tab layout

---

*For upcoming features, see the [Roadmap](roadmap.md)*
