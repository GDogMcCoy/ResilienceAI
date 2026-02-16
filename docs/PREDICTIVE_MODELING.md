# Predictive Risk Modeling - Implementation Summary

## Overview
This module adds comprehensive predictive risk modeling capabilities to ResilienceAI, enabling time-series forecasting, climate scenario modeling, and risk trajectory analysis.

## Files Created/Modified

### 1. `src/predictive_models.py` (NEW)
Main predictive modeling module containing:

#### Classes:
- **`TimeSeriesForecaster`**: Time-series forecasting using Prophet and ARIMA
  - Prophet integration with customizable seasonality
  - ARIMA with auto-parameter selection using AIC
  - Cross-validation support
  - Confidence interval generation

- **`DisasterPredictor`**: Machine learning models for disaster prediction
  - Gradient Boosting and Random Forest models
  - Feature engineering with lag variables and rolling statistics
  - Probability predictions with confidence levels

- **`ClimateScenarioModeler`**: IPCC climate scenario projections
  - SSP1-1.9 (1.5°C sustainability)
  - SSP2-4.5 (2.7°C middle road)
  - SSP5-8.5 (4.4°C high emissions)
  - Risk projections with infrastructure degradation modeling

- **`RiskTrajectoryAnalyzer`**: Comprehensive trajectory analysis
  - Combines historical trends, forecasts, and climate projections
  - Acceleration detection
  - Multi-scenario comparison

- **`PredictiveModelManager`**: Model persistence and batch operations
  - Save/load trained models
  - Batch forecasting for multiple counties

### 2. `src/agent.py` (MODIFIED)
Added 7 new MCP tools:
1. `forecast_risk_trajectory`: Generate time-series forecasts for counties
2. `analyze_risk_trajectory`: Complete trajectory analysis
3. `project_climate_risk`: Climate scenario projections
4. `detect_disaster_acceleration`: Detect increasing disaster frequency
5. `predict_disaster_probability`: ML-based disaster probability
6. `batch_forecast_counties`: Multi-county batch forecasting
7. `get_climate_adaptation_recommendations`: Adaptation recommendations

Updated system prompt to include predictive modeling capabilities.

### 3. `app/dashboard.py` (MODIFIED)
Added new dashboard tab "🔮 Predictive Risk" with 4 sub-tabs:
1. **Risk Forecast**: Interactive Prophet/ARIMA forecasting
2. **Climate Scenarios**: IPCC SSP scenario comparison
3. **Disaster Acceleration**: Acceleration detection analysis
4. **Batch Forecasts**: Multi-county regional forecasting

## Key Features

### Time-Series Forecasting
- Prophet model with yearly/monthly seasonality
- ARIMA with automatic parameter selection
- 95% confidence intervals
- Cross-validation metrics

### Climate Scenario Modeling
- Based on IPCC AR6 Shared Socioeconomic Pathways
- Temperature, precipitation, and extreme event multipliers
- Infrastructure degradation modeling
- Year-by-year risk projections

### Machine Learning Predictions
- Gradient Boosting for disaster probability
- Feature importance analysis
- Monthly probability decay
- Confidence levels based on data quality

### Visualization
- Interactive forecast charts with confidence bands
- Scenario comparison visualizations
- Acceleration detection charts
- Batch forecast distribution pie charts

## Usage Examples

### Python API
```python
from src.predictive_models import TimeSeriesForecaster, ClimateScenarioModeler

# Time-series forecast
forecaster = TimeSeriesForecaster(model_type='prophet')
forecaster.fit_prophet(df, date_col='date', value_col='risk_score')
result = forecaster.forecast(periods=12)

# Climate projection
modeler = ClimateScenarioModeler(baseline_data)
projections = modeler.project_risk('ssp2_45', years_ahead=30)
```

### MCP Tool Usage
```python
# Via ResilienceAgent
agent = ResilienceAgent()

# Forecast county risk
forecast = agent.forecast_risk_trajectory(
    fips='29189',
    model_type='prophet',
    forecast_years=10
)

# Climate scenario analysis
climate = agent.project_climate_risk(
    fips='29189',
    scenario='ssp5_85',
    compare_all_scenarios=True
)
```

### Dashboard
Navigate to the "🔮 Predictive Risk" tab in the Streamlit dashboard for interactive analysis.

## Dependencies
- `prophet`: Facebook's forecasting tool
- `statsmodels`: ARIMA and statistical tests
- `scikit-learn`: Machine learning models
- `plotly`: Interactive visualizations
- `pandas`, `numpy`: Data manipulation

## References
- Prophet: Taylor & Letham (2018) - Forecasting at Scale
- ARIMA: Box-Jenkins methodology
- IPCC AR6: Shared Socioeconomic Pathways (SSPs)
- Climate scenarios: WG1 Contribution to AR6

## Next Steps
1. Integrate real historical time-series data from FEMA
2. Add LSTM/Transformer models for deep learning forecasting
3. Implement ensemble methods combining multiple models
4. Add uncertainty quantification with Bayesian methods
5. Create automated retraining pipelines
