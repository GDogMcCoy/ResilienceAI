---
title: Code Documentation Standards
description: Standards and guidelines for documenting ResilienceAI code
category: Developer Guide
version: 2.0.0
---

# Code Documentation Standards

## Overview

This document defines the documentation standards for ResilienceAI code. Following these standards ensures that our codebase is maintainable, accessible to new contributors, and can be automatically processed by documentation tools.

## Docstring Format

ResilienceAI uses the **Google Python Style Guide** for docstrings.

### Module Docstrings

Every module should begin with a module-level docstring:

```python
"""Brief one-line description of the module.

More detailed description explaining the module's purpose, functionality,
and any important implementation details. This can span multiple lines.

Example:
    Basic usage of the module:

    >>> from src.feature_engineering import FeatureEngineer
    >>> engineer = FeatureEngineer()
    >>> features = engineer.transform(raw_data)

Attributes:
    MODULE_CONSTANT: Description of module-level constant.
    DEFAULT_CONFIG: Default configuration dictionary.

Todo:
    * Add support for Puerto Rico (FIPS 72)
    * Implement caching for expensive computations
    * Optimize memory usage for large datasets

.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html
"""
```

### Class Docstrings

Every public class must have a comprehensive docstring:

```python
class FeatureEngineer:
    """Engineers features for disaster vulnerability assessment.
    
    This class transforms raw data from multiple sources (FEMA, Census, HIFLD)
    into a standardized feature set for machine learning models.
    
    The engineered features include:
    - Demographics: Population, income, elderly percentage
    - Infrastructure: Distance to hospitals, fire stations, EMS
    - Disaster History: Total declarations, recent activity
    - Composite Indices: Vulnerability, isolation, risk scores
    
    Attributes:
        features_df: DataFrame containing engineered features.
        n_features: Number of features engineered (default: 66).
        n_counties: Number of counties in dataset.
        
    Example:
        >>> engineer = FeatureEngineer()
        >>> engineer.fit(raw_data)
        >>> features = engineer.transform(raw_data)
        >>> print(f"Engineered {features.shape[1]} features")
        Engineered 66 features
        
    Note:
        This class is not thread-safe. Create separate instances
        for concurrent processing.
        
    See Also:
        DataPipeline: For data acquisition and preprocessing.
        ModelTrainer: For training models on engineered features.
    """
```

### Function/Method Docstrings

Every public function and method must be documented:

```python
def calculate_vulnerability_index(
    demographics: pd.DataFrame,
    infrastructure: pd.DataFrame,
    weights: Optional[Dict[str, float]] = None,
    normalize: bool = True
) -> pd.Series:
    """Calculate composite vulnerability index for counties.
    
    Computes a weighted vulnerability score based on demographic and
    infrastructure factors. Higher scores indicate greater vulnerability.
    
    The index is calculated as:
    
    .. math::
        V_i = \\sum_{j} w_j \\cdot \\frac{x_{ij} - \\min(x_j)}{\\max(x_j) - \\min(x_j)}
    
    Where:
    - V_i is the vulnerability score for county i
    - w_j is the weight for factor j
    - x_{ij} is the value of factor j for county i
    
    Args:
        demographics: DataFrame with demographic features including
            'poverty_pct', 'elderly_pct', 'disability_pct', 'uninsured_pct'.
        infrastructure: DataFrame with infrastructure features including
            'dist_nearest_hospitals_km', 'hospitals_per_10k'.
        weights: Optional dictionary of factor weights. If None, uses
            default weights from config.VULNERABILITY_WEIGHTS.
        normalize: Whether to normalize scores to [0, 1] range.
            Defaults to True.
            
    Returns:
        Series with vulnerability index values for each county.
        Values range from 0 (low vulnerability) to 1 (high vulnerability).
        
    Raises:
        ValueError: If required columns are missing or contain invalid values.
        TypeError: If inputs are not DataFrames.
        
    Example:
        >>> import pandas as pd
        >>> demographics = pd.DataFrame({
        ...     'poverty_pct': [15.0, 20.0],
        ...     'elderly_pct': [12.0, 18.0]
        ... })
        >>> infrastructure = pd.DataFrame({
        ...     'dist_nearest_hospitals_km': [10.0, 25.0]
        ... })
        >>> vuln_index = calculate_vulnerability_index(demographics, infrastructure)
        >>> print(vuln_index)
        0    0.234
        1    0.567
        dtype: float64
        
    See Also:
        calculate_isolation_index: For infrastructure isolation scoring.
        calculate_risk_score: For combined risk assessment.
        
    References:
        - CDC Social Vulnerability Index (SVI): https://www.atsdr.cdc.gov/placeandhealth/svi/
        - FEMA National Risk Index: https://hazards.fema.gov/nri/
    """
```

## Type Hints

All function parameters and return values must have type hints:

```python
from typing import Dict, List, Optional, Union, Tuple, Any
import pandas as pd
import numpy as np

# Custom type aliases
CountyFIPS = str  # 5-digit FIPS code
RiskScore = float  # Normalized risk score [0, 1]
GeoCoordinates = Tuple[float, float]  # (latitude, longitude)

def analyze_county_risk(
    county_fips: CountyFIPS,
    features: pd.DataFrame,
    model: Optional[Any] = None,
    include_forecast: bool = False,
    forecast_horizon: int = 30
) -> Dict[str, Union[RiskScore, pd.DataFrame, str]]:
    """Analyze disaster risk for a specific county."""
    pass
```

## Documentation Sections

### Required Sections

| Section | When Required |
|---------|---------------|
| `Args` | All functions with parameters |
| `Returns` | All functions with return values |
| `Raises` | Functions that raise exceptions |
| `Example` | All public functions |
| `Note` | Important implementation details |
| `See Also` | Related functions/classes |

### Optional Sections

| Section | When to Use |
|---------|-------------|
| `Attributes` | Classes with public attributes |
| `Todo` | Known future improvements |
| `References` | Academic papers, standards |
| `Warning` | Potential pitfalls |
| `Deprecated` | Deprecated functions |

## Inline Comments

Use inline comments sparingly and only when necessary:

```python
# Good: Explains WHY, not WHAT
# Apply log transform to handle skewed income distribution
df['log_income'] = np.log1p(df['median_income'])

# Bad: Restates the obvious
df['log_income'] = np.log1p(df['median_income'])  # Log transform income
```

## Documentation Coverage Requirements

| Component | Minimum Coverage |
|-----------|------------------|
| Public modules | 100% |
| Public classes | 100% |
| Public methods | 100% |
| Private methods | 50% |
| Module-level constants | 100% |

## Checking Documentation Coverage

Use `interrogate` to check coverage:

```bash
# Install
pip install interrogate

# Check coverage
interrogate src/ --verbose --fail-under=80

# Generate badge
interrogate src/ --generate-badge=svg --badge-style=flat
```

## Documentation Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `pydocstyle` | Docstring style checker | `pydocstyle src/` |
| `darglint` | Argument documentation linter | `darglint src/` |
| `interrogate` | Coverage checker | `interrogate src/` |
| `mkdocstrings` | API doc generation | Auto-generated in build |

## Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pycqa/pydocstyle
    rev: 6.3.0
    hooks:
      - id: pydocstyle
        args: ['--convention=google']
        files: ^src/
  
  - repo: https://github.com/econchick/interrogate
    rev: 1.5.0
    hooks:
      - id: interrogate
        args: [--quiet, --fail-under=80]
        files: ^src/
```

## Best Practices

1. **Document as you code**: Write docstrings when writing functions, not after
2. **Keep examples simple**: Use minimal, runnable examples
3. **Update with changes**: Update docstrings when changing code
4. **Use active voice**: "Returns the risk score" not "The risk score is returned"
5. **Be specific**: Include units, ranges, and constraints
6. **Link related docs**: Use `See Also` and cross-references

## Example: Complete Module

```python
"""Weather alert client for NOAA NWS API.

This module provides real-time weather alert monitoring and notification
capabilities for US counties using the NOAA National Weather Service API.

Example:
    Basic usage:

    >>> from src.weather_client import NOAAWeatherClient
    >>> client = NOAAWeatherClient()
    >>> alerts = client.get_alerts_for_county("29019")
    >>> print(f"Found {len(alerts)} active alerts")
    Found 2 active alerts

Attributes:
    DEFAULT_TIMEOUT: Default HTTP request timeout in seconds (30).
    ALERT_SEVERITY_ORDER: Severity ranking from lowest to highest.

Todo:
    * Add support for weather forecast data
    * Implement alert deduplication
    * Add historical alert querying
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
import pandas as pd

DEFAULT_TIMEOUT = 30
ALERT_SEVERITY_ORDER = ['Minor', 'Moderate', 'Severe', 'Extreme']


class NOAAWeatherClient:
    """Client for NOAA National Weather Service API.
    
    Provides methods for fetching and processing weather alerts
    for US counties. Supports filtering by severity, type, and time.
    
    Attributes:
        base_url: NOAA API base URL.
        timeout: Request timeout in seconds.
        session: Requests session for connection pooling.
        
    Example:
        >>> client = NOAAWeatherClient(timeout=60)
        >>> alerts = client.get_alerts_for_county(
        ...     county_fips="29019",
        ...     severity=["Severe", "Extreme"]
        ... )
        >>> for alert in alerts:
        ...     print(f"{alert['event']}: {alert['severity']}")
    """
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        """Initialize the NOAA weather client.
        
        Args:
            timeout: HTTP request timeout in seconds. Defaults to 30.
            
        Raises:
            ValueError: If timeout is not a positive integer.
        """
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError("timeout must be a positive integer")
            
        self.base_url = "https://api.weather.gov"
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ResilienceAI/2.0 (support@resilienceai.dev)'
        })
```

---

*For questions about documentation standards, please [open an issue](https://github.com/GDogMcCoy/ResilienceAI/issues)*
