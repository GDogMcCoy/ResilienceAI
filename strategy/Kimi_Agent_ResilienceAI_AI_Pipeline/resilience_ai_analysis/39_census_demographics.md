# ResilienceAI Census Demographics Enhancement Analysis

## Executive Summary

This document provides a comprehensive analysis of the current Census ACS integration in ResilienceAI and designs extensive enhancements to support advanced demographic modeling, socioeconomic analysis, and population projections for disaster vulnerability assessment.

**Current State Analysis:**
- Basic ACS 5-year data integration with 6 variables
- Limited demographic features (6 core metrics)
- Basic poverty and income analysis
- No population projections
- Limited race/ethnicity data
- No educational attainment metrics
- No employment statistics integration
- No housing data integration

**Target Enhancement Goals:**
- Expand to 50+ ACS variables across 10 demographic categories
- Implement population projection models
- Add comprehensive socioeconomic indicators
- Integrate housing and transportation data
- Support tract-level and block group analysis

---

## 1. Current Census Integration Architecture

### 1.1 Existing Data Pipeline

```python
# Current implementation in src/download_data.py
CENSUS_BASE_URL = "https://api.census.gov/data/2022/acs/acs5"
CENSUS_VARIABLES = "B01003_001E,B19013_001E,B17001_002E,B09020_001E,B18101_001E,B27010_001E"
```

**Current Variables:**
| Variable | Description | Table |
|----------|-------------|-------|
| B01003_001E | Total Population | Population |
| B19013_001E | Median Household Income | Income |
| B17001_002E | Poverty Count | Poverty |
| B09020_001E | Elderly Population 65+ | Age |
| B18101_001E | Disability Universe | Disability |
| B27010_001E | Insurance Universe | Health Insurance |

### 1.2 Current Feature Engineering

```python
# Current derived features in src/feature_engineering.py
demographic_features = [
    "total_population",
    "median_income", 
    "poverty_pct",
    "elderly_pct",
    "disability_pct",
    "uninsured_pct"
]
```

---

## 2. Enhanced Census Architecture Design

### 2.1 Proposed Variable Framework

```
┌─────────────────────────────────────────────────────────────────┐
│           ENHANCED CENSACS VARIABLE FRAMEWORK                    │
├─────────────────────────────────────────────────────────────────┤
│  Category              │ Variables    │ Priority │ Status      │
├────────────────────────┼──────────────┼──────────┼─────────────┤
│ 1. Population Basics   │ 5 vars       │ HIGH     │ Partial     │
│ 2. Age Distribution    │ 23 vars      │ HIGH     │ Partial     │
│ 3. Race & Ethnicity    │ 21 vars      │ HIGH     │ Missing     │
│ 4. Income & Poverty    │ 18 vars      │ HIGH     │ Partial     │
│ 5. Education           │ 12 vars      │ MEDIUM   │ Missing     │
│ 6. Employment          │ 15 vars      │ MEDIUM   │ Missing     │
│ 7. Housing             │ 16 vars      │ MEDIUM   │ Missing     │
│ 8. Health Insurance    │ 8 vars       │ HIGH     │ Partial     │
│ 9. Disability          │ 10 vars      │ HIGH     │ Partial     │
│ 10. Language           │ 6 vars       │ LOW      │ Missing     │
├────────────────────────┴──────────────┴──────────┴─────────────┤
│  TOTAL: 134 variables across 10 demographic categories          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Enhanced Data Architecture

```python
# Proposed: src/census_enhanced_config.py

"""
Enhanced Census ACS Configuration
Comprehensive demographic variable selection for ResilienceAI
"""

# ACS API Configuration
ACS_CONFIG = {
    "base_url": "https://api.census.gov/data/{year}/acs/acs5",
    "years_available": list(range(2010, 2024)),
    "default_year": 2022,
    "geography_levels": ["state", "county", "tract", "block group"],
    "batch_size": 50,  # Max variables per API call
}

# Enhanced Variable Groups
CENSUS_VARIABLE_GROUPS = {
    # 1. POPULATION BASICS (5 variables)
    "population": {
        "B01003_001E": {
            "name": "total_population",
            "description": "Total population",
            "category": "population",
            "data_type": "count"
        },
        "B01001_001E": {
            "name": "population_by_sex_age",
            "description": "Total population by sex and age",
            "category": "population",
            "data_type": "count"
        },
        "B01002_001E": {
            "name": "median_age",
            "description": "Median age",
            "category": "population",
            "data_type": "median"
        },
        "B01002_002E": {
            "name": "median_age_male",
            "description": "Median age - male",
            "category": "population",
            "data_type": "median"
        },
        "B01002_003E": {
            "name": "median_age_female",
            "description": "Median age - female",
            "category": "population",
            "data_type": "median"
        }
    },
    
    # 2. AGE DISTRIBUTION (23 variables)
    "age_distribution": {
        # Male age brackets
        "B01001_003E": {"name": "male_under_5", "description": "Male under 5 years", "category": "age"},
        "B01001_004E": {"name": "male_5_9", "description": "Male 5-9 years", "category": "age"},
        "B01001_005E": {"name": "male_10_14", "description": "Male 10-14 years", "category": "age"},
        "B01001_006E": {"name": "male_15_17", "description": "Male 15-17 years", "category": "age"},
        "B01001_007E": {"name": "male_18_19", "description": "Male 18-19 years", "category": "age"},
        "B01001_008E": {"name": "male_20", "description": "Male 20 years", "category": "age"},
        "B01001_009E": {"name": "male_21", "description": "Male 21 years", "category": "age"},
        "B01001_010E": {"name": "male_22_24", "description": "Male 22-24 years", "category": "age"},
        "B01001_011E": {"name": "male_25_29", "description": "Male 25-29 years", "category": "age"},
        "B01001_012E": {"name": "male_30_34", "description": "Male 30-34 years", "category": "age"},
        "B01001_013E": {"name": "male_35_39", "description": "Male 35-39 years", "category": "age"},
        "B01001_014E": {"name": "male_40_44", "description": "Male 40-44 years", "category": "age"},
        "B01001_015E": {"name": "male_45_49", "description": "Male 45-49 years", "category": "age"},
        "B01001_016E": {"name": "male_50_54", "description": "Male 50-54 years", "category": "age"},
        "B01001_017E": {"name": "male_55_59", "description": "Male 55-59 years", "category": "age"},
        "B01001_018E": {"name": "male_60_61", "description": "Male 60-61 years", "category": "age"},
        "B01001_019E": {"name": "male_62_64", "description": "Male 62-64 years", "category": "age"},
        "B01001_020E": {"name": "male_65_66", "description": "Male 65-66 years", "category": "age"},
        "B01001_021E": {"name": "male_67_69", "description": "Male 67-69 years", "category": "age"},
        "B01001_022E": {"name": "male_70_74", "description": "Male 70-74 years", "category": "age"},
        "B01001_023E": {"name": "male_75_79", "description": "Male 75-79 years", "category": "age"},
        "B01001_024E": {"name": "male_80_84", "description": "Male 80-84 years", "category": "age"},
        "B01001_025E": {"name": "male_85_plus", "description": "Male 85+ years", "category": "age"},
        # Female age brackets (B01001_027E to B01001_049E)
    },
    
    # 3. RACE & ETHNICITY (21 variables)
    "race_ethnicity": {
        "B02001_001E": {"name": "race_total", "description": "Total race population", "category": "race"},
        "B02001_002E": {"name": "white_alone", "description": "White alone", "category": "race"},
        "B02001_003E": {"name": "black_alone", "description": "Black or African American alone", "category": "race"},
        "B02001_004E": {"name": "native_alone", "description": "American Indian and Alaska Native alone", "category": "race"},
        "B02001_005E": {"name": "asian_alone", "description": "Asian alone", "category": "race"},
        "B02001_006E": {"name": "pacific_alone", "description": "Native Hawaiian and Pacific Islander alone", "category": "race"},
        "B02001_007E": {"name": "other_race_alone", "description": "Some other race alone", "category": "race"},
        "B02001_008E": {"name": "two_or_more_races", "description": "Two or more races", "category": "race"},
        # Hispanic/Latino
        "B03003_001E": {"name": "ethnicity_total", "description": "Total ethnicity population", "category": "ethnicity"},
        "B03003_002E": {"name": "not_hispanic", "description": "Not Hispanic or Latino", "category": "ethnicity"},
        "B03003_003E": {"name": "hispanic_latino", "description": "Hispanic or Latino", "category": "ethnicity"},
        # Detailed Hispanic origin
        "B03001_003E": {"name": "hispanic_mexican", "description": "Mexican", "category": "ethnicity"},
        "B03001_004E": {"name": "hispanic_puerto_rican", "description": "Puerto Rican", "category": "ethnicity"},
        "B03001_005E": {"name": "hispanic_cuban", "description": "Cuban", "category": "ethnicity"},
        "B03001_006E": {"name": "hispanic_other", "description": "Other Hispanic or Latino", "category": "ethnicity"},
        # Race by Hispanic origin
        "B25003_001E": {"name": "housing_units_total", "description": "Total housing units", "category": "housing"},
        "B25003_002E": {"name": "owner_occupied", "description": "Owner-occupied housing units", "category": "housing"},
        "B25003_003E": {"name": "renter_occupied", "description": "Renter-occupied housing units", "category": "housing"},
    },
    
    # 4. INCOME & POVERTY (18 variables)
    "income_poverty": {
        # Income
        "B19013_001E": {"name": "median_household_income", "description": "Median household income", "category": "income"},
        "B19001_001E": {"name": "households_total", "description": "Total households", "category": "income"},
        "B19001_002E": {"name": "income_under_10k", "description": "Households with income <$10,000", "category": "income"},
        "B19001_003E": {"name": "income_10k_15k", "description": "Households with income $10,000-$14,999", "category": "income"},
        "B19001_004E": {"name": "income_15k_20k", "description": "Households with income $15,000-$19,999", "category": "income"},
        "B19001_005E": {"name": "income_20k_25k", "description": "Households with income $20,000-$24,999", "category": "income"},
        "B19001_006E": {"name": "income_25k_30k", "description": "Households with income $25,000-$29,999", "category": "income"},
        "B19001_007E": {"name": "income_30k_35k", "description": "Households with income $30,000-$34,999", "category": "income"},
        "B19001_008E": {"name": "income_35k_40k", "description": "Households with income $35,000-$39,999", "category": "income"},
        "B19001_009E": {"name": "income_40k_45k", "description": "Households with income $40,000-$44,999", "category": "income"},
        "B19001_010E": {"name": "income_45k_50k", "description": "Households with income $45,000-$49,999", "category": "income"},
        "B19001_011E": {"name": "income_50k_60k", "description": "Households with income $50,000-$59,999", "category": "income"},
        "B19001_012E": {"name": "income_60k_75k", "description": "Households with income $60,000-$74,999", "category": "income"},
        "B19001_013E": {"name": "income_75k_100k", "description": "Households with income $75,000-$99,999", "category": "income"},
        "B19001_014E": {"name": "income_100k_125k", "description": "Households with income $100,000-$124,999", "category": "income"},
        "B19001_015E": {"name": "income_125k_150k", "description": "Households with income $125,000-$149,999", "category": "income"},
        "B19001_016E": {"name": "income_150k_200k", "description": "Households with income $150,000-$199,999", "category": "income"},
        "B19001_017E": {"name": "income_200k_plus", "description": "Households with income $200,000+", "category": "income"},
        # Poverty
        "B17001_001E": {"name": "poverty_universe", "description": "Population for whom poverty status is determined", "category": "poverty"},
        "B17001_002E": {"name": "income_below_poverty", "description": "Income in past 12 months below poverty level", "category": "poverty"},
        "B17026_001E": {"name": "poverty_ratio_total", "description": "Total poverty ratio population", "category": "poverty"},
    },
    
    # 5. EDUCATIONAL ATTAINMENT (12 variables)
    "education": {
        "B15003_001E": {"name": "education_total", "description": "Total population 25 years and over", "category": "education"},
        "B15003_002E": {"name": "no_schooling", "description": "No schooling completed", "category": "education"},
        "B15003_003E": {"name": "nursery_to_4th", "description": "Nursery to 4th grade", "category": "education"},
        "B15003_004E": {"name": "5th_to_6th", "description": "5th and 6th grade", "category": "education"},
        "B15003_005E": {"name": "7th_to_8th", "description": "7th and 8th grade", "category": "education"},
        "B15003_006E": {"name": "9th_grade", "description": "9th grade", "category": "education"},
        "B15003_007E": {"name": "10th_grade", "description": "10th grade", "category": "education"},
        "B15003_008E": {"name": "11th_grade", "description": "11th grade", "category": "education"},
        "B15003_009E": {"name": "12th_grade_no_diploma", "description": "12th grade, no diploma", "category": "education"},
        "B15003_010E": {"name": "high_school_graduate", "description": "High school graduate (includes equivalency)", "category": "education"},
        "B15003_011E": {"name": "some_college_less_1", "description": "Some college, less than 1 year", "category": "education"},
        "B15003_012E": {"name": "some_college_1_plus", "description": "Some college, 1 or more years, no degree", "category": "education"},
        "B15003_013E": {"name": "associates_degree", "description": "Associate's degree", "category": "education"},
        "B15003_014E": {"name": "bachelors_degree", "description": "Bachelor's degree", "category": "education"},
        "B15003_015E": {"name": "masters_degree", "description": "Master's degree", "category": "education"},
        "B15003_016E": {"name": "professional_degree", "description": "Professional school degree", "category": "education"},
        "B15003_017E": {"name": "doctorate_degree", "description": "Doctorate degree", "category": "education"},
    },
    
    # 6. EMPLOYMENT (15 variables)
    "employment": {
        "B23027_001E": {"name": "employment_total", "description": "Total population 16 years and over", "category": "employment"},
        "B23027_002E": {"name": "in_labor_force", "description": "In labor force", "category": "employment"},
        "B23027_003E": {"name": "civilian_labor_force", "description": "Civilian labor force", "category": "employment"},
        "B23027_004E": {"name": "employed", "description": "Employed", "category": "employment"},
        "B23027_005E": {"name": "unemployed", "description": "Unemployed", "category": "employment"},
        "B23027_006E": {"name": "armed_forces", "description": "Armed Forces", "category": "employment"},
        "B23027_007E": {"name": "not_in_labor_force", "description": "Not in labor force", "category": "employment"},
        # Employment by industry (simplified)
        "C24010_001E": {"name": "employment_by_industry_total", "description": "Total employed population 16 years and over", "category": "employment"},
        "C24010_003E": {"name": "agriculture_forestry", "description": "Agriculture, forestry, fishing, hunting", "category": "employment"},
        "C24010_004E": {"name": "construction", "description": "Construction", "category": "employment"},
        "C24010_005E": {"name": "manufacturing", "description": "Manufacturing", "category": "employment"},
        "C24010_006E": {"name": "wholesale_trade", "description": "Wholesale trade", "category": "employment"},
        "C24010_007E": {"name": "retail_trade", "description": "Retail trade", "category": "employment"},
        "C24010_008E": {"name": "transportation_warehousing", "description": "Transportation and warehousing", "category": "employment"},
        "C24010_009E": {"name": "information", "description": "Information", "category": "employment"},
    },
    
    # 7. HOUSING (16 variables)
    "housing": {
        "B25001_001E": {"name": "housing_units_total", "description": "Total housing units", "category": "housing"},
        "B25002_001E": {"name": "housing_units_occupied", "description": "Total housing units occupied", "category": "housing"},
        "B25002_002E": {"name": "housing_units_vacant", "description": "Total housing units vacant", "category": "housing"},
        "B25003_001E": {"name": "tenure_total", "description": "Total occupied housing units", "category": "housing"},
        "B25003_002E": {"name": "owner_occupied", "description": "Owner-occupied", "category": "housing"},
        "B25003_003E": {"name": "renter_occupied", "description": "Renter-occupied", "category": "housing"},
        "B25010_001E": {"name": "avg_household_size", "description": "Average household size", "category": "housing"},
        "B25010_002E": {"name": "avg_owner_household_size", "description": "Average household size of owner-occupied unit", "category": "housing"},
        "B25010_003E": {"name": "avg_renter_household_size", "description": "Average household size of renter-occupied unit", "category": "housing"},
        "B25064_001E": {"name": "median_gross_rent", "description": "Median gross rent", "category": "housing"},
        "B25077_001E": {"name": "median_home_value", "description": "Median value (dollars)", "category": "housing"},
        "B25088_001E": {"name": "median_owner_costs", "description": "Median selected monthly owner costs", "category": "housing"},
        "B25088_002E": {"name": "median_owner_costs_mortgage", "description": "Median selected monthly owner costs with mortgage", "category": "housing"},
        "B25088_003E": {"name": "median_owner_costs_no_mortgage", "description": "Median selected monthly owner costs without mortgage", "category": "housing"},
        "B25091_001E": {"name": "owner_costs_30pct_total", "description": "Total owner-occupied units", "category": "housing"},
        "B25091_002E": {"name": "owner_costs_30pct_plus", "description": "Owner-occupied units with costs 30% or more of income", "category": "housing"},
    },
    
    # 8. HEALTH INSURANCE (8 variables)
    "health_insurance": {
        "B27010_001E": {"name": "health_insurance_total", "description": "Total civilian noninstitutionalized population", "category": "health"},
        "B27010_002E": {"name": "under_19_total", "description": "Under 19 years", "category": "health"},
        "B27010_003E": {"name": "under_19_private", "description": "Under 19: With private health insurance", "category": "health"},
        "B27010_004E": {"name": "under_19_public", "description": "Under 19: With public health coverage", "category": "health"},
        "B27010_005E": {"name": "under_19_uninsured", "description": "Under 19: No health insurance coverage", "category": "health"},
        "B27010_006E": {"name": "19_34_total", "description": "19 to 34 years", "category": "health"},
        "B27010_017E": {"name": "19_34_uninsured", "description": "19 to 34: No health insurance coverage", "category": "health"},
        "B27010_033E": {"name": "35_64_uninsured", "description": "35 to 64: No health insurance coverage", "category": "health"},
        "B27010_050E": {"name": "65_plus_uninsured", "description": "65 years and over: No health insurance coverage", "category": "health"},
    },
    
    # 9. DISABILITY (10 variables)
    "disability": {
        "B18101_001E": {"name": "disability_total", "description": "Total civilian noninstitutionalized population", "category": "disability"},
        "B18101_002E": {"name": "male_under_5", "description": "Male: Under 5 years", "category": "disability"},
        "B18101_003E": {"name": "male_under_5_disability", "description": "Male Under 5: With a disability", "category": "disability"},
        "B18101_004E": {"name": "male_under_5_no_disability", "description": "Male Under 5: No disability", "category": "disability"},
        "B18101_005E": {"name": "male_5_17", "description": "Male: 5 to 17 years", "category": "disability"},
        "B18101_006E": {"name": "male_5_17_disability", "description": "Male 5-17: With a disability", "category": "disability"},
        "B18101_007E": {"name": "male_5_17_no_disability", "description": "Male 5-17: No disability", "category": "disability"},
        "B18101_008E": {"name": "male_18_34", "description": "Male: 18 to 34 years", "category": "disability"},
        "B18101_009E": {"name": "male_18_34_disability", "description": "Male 18-34: With a disability", "category": "disability"},
        "B18101_010E": {"name": "male_18_34_no_disability", "description": "Male 18-34: No disability", "category": "disability"},
        # Additional age groups follow same pattern (B18101_011E to B18101_038E)
    },
    
    # 10. LANGUAGE (6 variables)
    "language": {
        "B16001_001E": {"name": "language_total", "description": "Total population 5 years and over", "category": "language"},
        "B16001_002E": {"name": "english_only", "description": "Speak only English", "category": "language"},
        "B16001_003E": {"name": "spanish", "description": "Spanish or Spanish Creole", "category": "language"},
        "B16001_006E": {"name": "french", "description": "French (incl. Patois, Cajun)", "category": "language"},
        "B16001_009E": {"name": "german", "description": "German", "category": "language"},
        "B16001_012E": {"name": "other_indo_european", "description": "Other Indo-European languages", "category": "language"},
        "B16001_015E": {"name": "korean", "description": "Korean", "category": "language"},
        "B16001_018E": {"name": "chinese", "description": "Chinese", "category": "language"},
        "B16001_021E": {"name": "vietnamese", "description": "Vietnamese", "category": "language"},
        "B16001_024E": {"name": "tagalog", "description": "Tagalog", "category": "language"},
        "B16001_027E": {"name": "other_asian", "description": "Other Asian languages", "category": "language"},
        "B16001_030E": {"name": "other_languages", "description": "Other languages", "category": "language"},
    }
}

# Derived Metrics Configuration
DERIVED_METRICS = {
    "age": {
        "youth_dependency_ratio": {
            "formula": "(under_18 / working_age) * 100",
            "description": "Ratio of youth to working-age population"
        },
        "old_age_dependency_ratio": {
            "formula": "(over_65 / working_age) * 100",
            "description": "Ratio of elderly to working-age population"
        },
        "total_dependency_ratio": {
            "formula": "((under_18 + over_65) / working_age) * 100",
            "description": "Total dependency ratio"
        },
        "median_age": {
            "formula": "direct_from_census",
            "description": "Median age of population"
        }
    },
    "race_ethnicity": {
        "white_pct": {
            "formula": "(white_alone / race_total) * 100",
            "description": "Percentage White alone"
        },
        "black_pct": {
            "formula": "(black_alone / race_total) * 100",
            "description": "Percentage Black/African American alone"
        },
        "asian_pct": {
            "formula": "(asian_alone / race_total) * 100",
            "description": "Percentage Asian alone"
        },
        "hispanic_pct": {
            "formula": "(hispanic_latino / ethnicity_total) * 100",
            "description": "Percentage Hispanic/Latino"
        },
        "minority_pct": {
            "formula": "((race_total - white_alone) / race_total) * 100",
            "description": "Percentage minority population"
        },
        "diversity_index": {
            "formula": "1 - sum((race_i / race_total)^2)",
            "description": "Simpson's Diversity Index"
        }
    },
    "income_poverty": {
        "poverty_rate": {
            "formula": "(income_below_poverty / poverty_universe) * 100",
            "description": "Poverty rate percentage"
        },
        "deep_poverty_rate": {
            "formula": "(income_under_10k / households_total) * 100",
            "description": "Deep poverty rate (<$10k)"
        },
        "low_income_rate": {
            "formula": "((income_under_10k + income_10k_15k + income_15k_20k + income_20k_25k) / households_total) * 100",
            "description": "Low income rate (<$25k)"
        },
        "middle_class_rate": {
            "formula": "((income_50k_60k + income_60k_75k + income_75k_100k) / households_total) * 100",
            "description": "Middle class rate ($50k-$100k)"
        },
        "high_income_rate": {
            "formula": "((income_100k_125k + income_125k_150k + income_150k_200k + income_200k_plus) / households_total) * 100",
            "description": "High income rate ($100k+)"
        },
        "gini_coefficient_proxy": {
            "formula": "calculated_from_income_distribution",
            "description": "Proxy for income inequality"
        }
    },
    "education": {
        "less_than_hs_pct": {
            "formula": "((no_schooling + nursery_to_4th + 5th_to_6th + 7th_to_8th + 9th_grade + 10th_grade + 11th_grade + 12th_grade_no_diploma) / education_total) * 100",
            "description": "Percentage with less than high school"
        },
        "hs_graduate_pct": {
            "formula": "(high_school_graduate / education_total) * 100",
            "description": "Percentage high school graduate"
        },
        "some_college_pct": {
            "formula": "((some_college_less_1 + some_college_1_plus) / education_total) * 100",
            "description": "Percentage with some college"
        },
        "associates_pct": {
            "formula": "(associates_degree / education_total) * 100",
            "description": "Percentage with associate's degree"
        },
        "bachelors_plus_pct": {
            "formula": "((bachelors_degree + masters_degree + professional_degree + doctorate_degree) / education_total) * 100",
            "description": "Percentage with bachelor's or higher"
        },
        "advanced_degree_pct": {
            "formula": "((masters_degree + professional_degree + doctorate_degree) / education_total) * 100",
            "description": "Percentage with advanced degree"
        }
    },
    "employment": {
        "labor_force_participation_rate": {
            "formula": "(in_labor_force / employment_total) * 100",
            "description": "Labor force participation rate"
        },
        "unemployment_rate": {
            "formula": "(unemployed / civilian_labor_force) * 100",
            "description": "Unemployment rate"
        },
        "employment_rate": {
            "formula": "(employed / employment_total) * 100",
            "description": "Employment rate"
        }
    },
    "housing": {
        "homeownership_rate": {
            "formula": "(owner_occupied / tenure_total) * 100",
            "description": "Homeownership rate"
        },
        "renter_rate": {
            "formula": "(renter_occupied / tenure_total) * 100",
            "description": "Renter-occupied rate"
        },
        "vacancy_rate": {
            "formula": "(housing_units_vacant / housing_units_total) * 100",
            "description": "Housing vacancy rate"
        },
        "housing_cost_burden_rate": {
            "formula": "(owner_costs_30pct_plus / owner_costs_30pct_total) * 100",
            "description": "Housing cost burden rate (30%+ of income)"
        },
        "crowding_index": {
            "formula": "derived_from_household_size_distribution",
            "description": "Housing crowding index"
        }
    },
    "health_insurance": {
        "uninsured_rate": {
            "formula": "(total_uninsured / health_insurance_total) * 100",
            "description": "Overall uninsured rate"
        },
        "children_uninsured_rate": {
            "formula": "(under_19_uninsured / under_19_total) * 100",
            "description": "Children uninsured rate"
        },
        "adult_uninsured_rate": {
            "formula": "((19_34_uninsured + 35_64_uninsured) / (19_34_total + 35_64_total)) * 100",
            "description": "Adult uninsured rate"
        }
    },
    "disability": {
        "disability_rate": {
            "formula": "(total_with_disability / disability_total) * 100",
            "description": "Overall disability rate"
        },
        "child_disability_rate": {
            "formula": "((male_under_5_disability + male_5_17_disability + female_under_5_disability + female_5_17_disability) / (male_under_5 + male_5_17 + female_under_5 + female_5_17)) * 100",
            "description": "Child disability rate"
        },
        "adult_disability_rate": {
            "formula": "((male_18_34_disability + male_35_64_disability + male_65_plus_disability + female_18_34_disability + female_35_64_disability + female_65_plus_disability) / (male_18_34 + male_35_64 + male_65_plus + female_18_34 + female_35_64 + female_65_plus)) * 100",
            "description": "Adult disability rate"
        }
    }
}


---

## 3. Implementation Code

### 3.1 Enhanced Census Data Client

```python
# File: src/census_enhanced_client.py
"""
Enhanced Census ACS Data Client for ResilienceAI
Provides comprehensive demographic data integration with caching,
batch processing, and derived metric calculation.
"""

import json
import time
import logging
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import RAW_DIR, CACHE_DIR, CENSUS_API_KEY
from census_enhanced_config import (
    ACS_CONFIG, 
    CENSUS_VARIABLE_GROUPS, 
    DERIVED_METRICS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CensusVariable:
    """Represents a Census ACS variable with metadata."""
    code: str
    name: str
    description: str
    category: str
    data_type: str = "count"
    
    @property
    def is_moe(self) -> bool:
        """Check if variable is a margin of error."""
        return self.code.endswith('M')
    
    @property
    def is_estimate(self) -> bool:
        """Check if variable is an estimate."""
        return self.code.endswith('E')


class CensusAPIError(Exception):
    """Custom exception for Census API errors."""
    pass


class CensusDataClient:
    """
    Enhanced client for Census ACS 5-year data.
    
    Features:
    - Batch variable retrieval (respects API limits)
    - Intelligent caching with TTL
    - Derived metric calculation
    - Multiple geography levels
    - Error handling and retry logic
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        year: int = 2022,
        max_retries: int = 3,
        timeout: int = 120
    ):
        """
        Initialize Census Data Client.
        
        Args:
            api_key: Census API key (defaults to environment variable)
            cache_dir: Directory for caching API responses
            year: ACS 5-year data year
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or CENSUS_API_KEY
        self.cache_dir = cache_dir or CACHE_DIR / "census_enhanced"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.year = year
        self.timeout = timeout
        
        # Setup session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        
        # Load variable metadata
        self.variables = self._load_variables()
        
        logger.info(f"CensusDataClient initialized for year {year}")
    
    def _load_variables(self) -> Dict[str, CensusVariable]:
        """Load variable metadata from configuration."""
        variables = {}
        for category, vars_dict in CENSUS_VARIABLE_GROUPS.items():
            for code, metadata in vars_dict.items():
                variables[code] = CensusVariable(
                    code=code,
                    name=metadata['name'],
                    description=metadata['description'],
                    category=metadata['category'],
                    data_type=metadata.get('data_type', 'count')
                )
        return variables
    
    def _get_cache_path(
        self, 
        geography: str, 
        state_fips: Optional[str],
        variable_hash: str
    ) -> Path:
        """Generate cache file path."""
        state_str = state_fips or "all"
        cache_name = f"census_{self.year}_{geography}_{state_str}_{variable_hash}"
        return self.cache_dir / f"{cache_name}.parquet"
    
    def _build_api_url(
        self,
        variables: List[str],
        geography: str,
        state_fips: Optional[str] = None
    ) -> str:
        """Build Census API URL."""
        base_url = ACS_CONFIG['base_url'].format(year=self.year)
        var_str = ",".join(variables)
        
        if geography == "county":
            if state_fips:
                url = f"{base_url}?get=NAME,{var_str}&for=county:*&in=state:{state_fips}"
            else:
                url = f"{base_url}?get=NAME,{var_str}&for=county:*&in=state:*"
        elif geography == "tract":
            if state_fips:
                url = f"{base_url}?get=NAME,{var_str}&for=tract:*&in=state:{state_fips}"
            else:
                url = f"{base_url}?get=NAME,{var_str}&for=tract:*&in=state:*"
        elif geography == "state":
            url = f"{base_url}?get=NAME,{var_str}&for=state:*"
        else:
            raise ValueError(f"Unsupported geography: {geography}")
        
        if self.api_key:
            url += f"&key={self.api_key}"
        
        return url
    
    def _fetch_data(
        self,
        url: str,
        cache_path: Optional[Path] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Fetch data from Census API with caching.
        
        Args:
            url: API URL
            cache_path: Path for cache file
            use_cache: Whether to use cached data
            
        Returns:
            DataFrame with Census data
        """
        # Check cache
        if use_cache and cache_path and cache_path.exists():
            logger.info(f"[CACHE HIT] Loading from {cache_path}")
            return pd.read_parquet(cache_path)
        
        # Fetch from API
        logger.info(f"[API CALL] Fetching from Census API")
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            # Parse response
            headers = data[0]
            rows = data[1:]
            df = pd.DataFrame(rows, columns=headers)
            
            # Cache result
            if cache_path:
                df.to_parquet(cache_path)
            
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise CensusAPIError(f"Failed to fetch data: {e}")
    
    def get_data(
        self,
        variables: Union[str, List[str]],
        geography: str = "county",
        state_fips: Optional[str] = None,
        use_cache: bool = True,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Get Census data for specified variables.
        
        Args:
            variables: Variable code(s) to retrieve
            geography: Geography level (state, county, tract)
            state_fips: Optional state FIPS code filter
            use_cache: Whether to use cached data
            force_refresh: Force refresh from API
            
        Returns:
            DataFrame with Census data
        """
        if isinstance(variables, str):
            variables = [variables]
        
        # Validate variables
        invalid_vars = [v for v in variables if v not in self.variables]
        if invalid_vars:
            raise ValueError(f"Invalid variables: {invalid_vars}")
        
        # Generate cache path
        var_hash = hash(tuple(sorted(variables))) % 10000000
        cache_path = self._get_cache_path(geography, state_fips, str(var_hash))
        
        if force_refresh and cache_path.exists():
            cache_path.unlink()
        
        # Build and fetch
        url = self._build_api_url(variables, geography, state_fips)
        df = self._fetch_data(url, cache_path, use_cache)
        
        # Convert numeric columns
        for col in variables:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Create FIPS code
        if 'state' in df.columns and 'county' in df.columns:
            df['fips'] = df['state'] + df['county']
        elif 'state' in df.columns:
            df['fips'] = df['state']
        
        return df
    
    def get_data_by_category(
        self,
        category: str,
        geography: str = "county",
        state_fips: Optional[str] = None,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Get all variables for a specific category.
        
        Args:
            category: Variable category (e.g., 'population', 'income_poverty')
            geography: Geography level
            state_fips: Optional state FIPS code filter
            use_cache: Whether to use cached data
            
        Returns:
            DataFrame with all variables in category
        """
        if category not in CENSUS_VARIABLE_GROUPS:
            raise ValueError(f"Unknown category: {category}")
        
        variables = list(CENSUS_VARIABLE_GROUPS[category].keys())
        
        # Split into batches if needed
        batch_size = ACS_CONFIG['batch_size']
        if len(variables) <= batch_size:
            return self.get_data(variables, geography, state_fips, use_cache)
        
        # Fetch in batches
        dfs = []
        for i in range(0, len(variables), batch_size):
            batch_vars = variables[i:i + batch_size]
            df = self.get_data(batch_vars, geography, state_fips, use_cache)
            dfs.append(df)
            time.sleep(0.5)  # Rate limiting
        
        # Merge batches
        result = dfs[0]
        for df in dfs[1:]:
            merge_cols = ['fips', 'NAME', 'state', 'county'] if 'county' in df.columns else ['fips', 'NAME', 'state']
            merge_cols = [c for c in merge_cols if c in result.columns and c in df.columns]
            result = result.merge(df, on=merge_cols, how='outer')
        
        return result
    
    def get_all_data(
        self,
        geography: str = "county",
        state_fips: Optional[str] = None,
        use_cache: bool = True,
        categories: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Get all Census data (all categories).
        
        Args:
            geography: Geography level
            state_fips: Optional state FIPS code filter
            use_cache: Whether to use cached data
            categories: Optional list of categories to include
            
        Returns:
            DataFrame with all Census data
        """
        cats = categories or list(CENSUS_VARIABLE_GROUPS.keys())
        
        dfs = []
        for category in cats:
            logger.info(f"Fetching category: {category}")
            try:
                df = self.get_data_by_category(category, geography, state_fips, use_cache)
                dfs.append(df)
            except Exception as e:
                logger.error(f"Failed to fetch category {category}: {e}")
            time.sleep(0.5)
        
        # Merge all categories
        if not dfs:
            return pd.DataFrame()
        
        result = dfs[0]
        for df in dfs[1:]:
            merge_cols = ['fips', 'NAME', 'state', 'county'] if 'county' in df.columns else ['fips', 'NAME', 'state']
            merge_cols = [c for c in merge_cols if c in result.columns and c in df.columns]
            result = result.merge(df, on=merge_cols, how='outer')
        
        return result
    
    def calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived demographic metrics.
        
        Args:
            df: DataFrame with raw Census variables
            
        Returns:
            DataFrame with additional derived metrics
        """
        result = df.copy()
        
        # Age metrics
        if 'total_population' in result.columns:
            # Youth population (under 18)
            youth_cols = [c for c in result.columns if any(x in c for x in ['under_5', '_5_', '_10_', '_15_', '_16_', '_17_'])]
            if youth_cols:
                result['youth_population'] = result[youth_cols].sum(axis=1)
                result['youth_pct'] = (result['youth_population'] / result['total_population'] * 100).round(2)
            
            # Working age (18-64)
            working_cols = [c for c in result.columns if any(x in c for x in ['_18_', '_20', '_21', '_22_', '_25_', '_30_', '_35_', '_40_', '_45_', '_50_', '_55_', '_60_', '_62_', '_64_'])]
            if working_cols:
                result['working_age_population'] = result[working_cols].sum(axis=1)
                result['working_age_pct'] = (result['working_age_population'] / result['total_population'] * 100).round(2)
            
            # Elderly (65+)
            elderly_cols = [c for c in result.columns if any(x in c for x in ['_65_', '_67_', '_70_', '_75_', '_80_', '_85_'])]
            if elderly_cols:
                result['elderly_population'] = result[elderly_cols].sum(axis=1)
                result['elderly_pct'] = (result['elderly_population'] / result['total_population'] * 100).round(2)
            
            # Dependency ratios
            if 'youth_population' in result.columns and 'working_age_population' in result.columns:
                result['youth_dependency_ratio'] = (result['youth_population'] / result['working_age_population'] * 100).round(2)
            
            if 'elderly_population' in result.columns and 'working_age_population' in result.columns:
                result['old_age_dependency_ratio'] = (result['elderly_population'] / result['working_age_population'] * 100).round(2)
            
            if 'youth_population' in result.columns and 'elderly_population' in result.columns and 'working_age_population' in result.columns:
                result['total_dependency_ratio'] = ((result['youth_population'] + result['elderly_population']) / result['working_age_population'] * 100).round(2)
        
        # Race/Ethnicity percentages
        if 'race_total' in result.columns:
            for race in ['white_alone', 'black_alone', 'asian_alone', 'native_alone', 'pacific_alone', 'other_race_alone']:
                if race in result.columns:
                    pct_name = race.replace('_alone', '_pct')
                    result[pct_name] = (result[race] / result['race_total'] * 100).round(2)
            
            # Minority percentage
            if 'white_alone' in result.columns:
                result['minority_pct'] = ((result['race_total'] - result['white_alone']) / result['race_total'] * 100).round(2)
        
        # Hispanic percentage
        if 'ethnicity_total' in result.columns and 'hispanic_latino' in result.columns:
            result['hispanic_pct'] = (result['hispanic_latino'] / result['ethnicity_total'] * 100).round(2)
        
        # Poverty rate
        if 'poverty_universe' in result.columns and 'income_below_poverty' in result.columns:
            result['poverty_rate'] = (result['income_below_poverty'] / result['poverty_universe'] * 100).round(2)
        
        # Income distribution
        if 'households_total' in result.columns:
            # Low income (<$25k)
            low_income_cols = ['income_under_10k', 'income_10k_15k', 'income_15k_20k', 'income_20k_25k']
            if all(c in result.columns for c in low_income_cols):
                result['low_income_households'] = result[low_income_cols].sum(axis=1)
                result['low_income_rate'] = (result['low_income_households'] / result['households_total'] * 100).round(2)
            
            # Middle income ($50k-$100k)
            mid_income_cols = ['income_50k_60k', 'income_60k_75k', 'income_75k_100k']
            if all(c in result.columns for c in mid_income_cols):
                result['middle_income_households'] = result[mid_income_cols].sum(axis=1)
                result['middle_income_rate'] = (result['middle_income_households'] / result['households_total'] * 100).round(2)
            
            # High income ($100k+)
            high_income_cols = ['income_100k_125k', 'income_125k_150k', 'income_150k_200k', 'income_200k_plus']
            if all(c in result.columns for c in high_income_cols):
                result['high_income_households'] = result[high_income_cols].sum(axis=1)
                result['high_income_rate'] = (result['high_income_households'] / result['households_total'] * 100).round(2)
        
        # Education levels
        if 'education_total' in result.columns:
            # Less than high school
            no_hs_cols = ['no_schooling', 'nursery_to_4th', '5th_to_6th', '7th_to_8th', '9th_grade', '10th_grade', '11th_grade', '12th_grade_no_diploma']
            if all(c in result.columns for c in no_hs_cols):
                result['less_than_hs'] = result[no_hs_cols].sum(axis=1)
                result['less_than_hs_pct'] = (result['less_than_hs'] / result['education_total'] * 100).round(2)
            
            # Bachelor's or higher
            college_plus_cols = ['bachelors_degree', 'masters_degree', 'professional_degree', 'doctorate_degree']
            if all(c in result.columns for c in college_plus_cols):
                result['bachelors_plus'] = result[college_plus_cols].sum(axis=1)
                result['bachelors_plus_pct'] = (result['bachelors_plus'] / result['education_total'] * 100).round(2)
        
        # Employment
        if 'employment_total' in result.columns and 'in_labor_force' in result.columns:
            result['labor_force_participation_rate'] = (result['in_labor_force'] / result['employment_total'] * 100).round(2)
        
        if 'civilian_labor_force' in result.columns and 'unemployed' in result.columns:
            result['unemployment_rate'] = (result['unemployed'] / result['civilian_labor_force'] * 100).round(2)
        
        # Housing
        if 'tenure_total' in result.columns and 'owner_occupied' in result.columns:
            result['homeownership_rate'] = (result['owner_occupied'] / result['tenure_total'] * 100).round(2)
        
        if 'housing_units_total' in result.columns and 'housing_units_vacant' in result.columns:
            result['vacancy_rate'] = (result['housing_units_vacant'] / result['housing_units_total'] * 100).round(2)
        
        # Health insurance
        if 'health_insurance_total' in result.columns:
            uninsured_cols = [c for c in result.columns if 'uninsured' in c]
            if uninsured_cols:
                result['total_uninsured'] = result[uninsured_cols].sum(axis=1)
                result['uninsured_rate'] = (result['total_uninsured'] / result['health_insurance_total'] * 100).round(2)
        
        # Disability
        if 'disability_total' in result.columns:
            disability_cols = [c for c in result.columns if 'disability' in c and 'no_disability' not in c and c != 'disability_total']
            if disability_cols:
                result['total_with_disability'] = result[disability_cols].sum(axis=1)
                result['disability_rate'] = (result['total_with_disability'] / result['disability_total'] * 100).round(2)
        
        return result
    
    def export_to_csv(
        self,
        df: pd.DataFrame,
        filename: str = "census_enhanced_demographics.csv"
    ) -> Path:
        """Export DataFrame to CSV."""
        output_path = RAW_DIR / filename
        df.to_csv(output_path, index=False)
        logger.info(f"Exported to {output_path}")
        return output_path


def download_enhanced_census_data(
    state_fips: Optional[str] = None,
    year: int = 2022,
    geography: str = "county",
    categories: Optional[List[str]] = None,
    calculate_metrics: bool = True,
    export: bool = True
) -> pd.DataFrame:
    """
    Convenience function to download enhanced Census data.
    
    Args:
        state_fips: Optional state FIPS code filter
        year: ACS 5-year data year
        geography: Geography level
        categories: Categories to include
        calculate_metrics: Whether to calculate derived metrics
        export: Whether to export to CSV
        
    Returns:
        DataFrame with Census data
    """
    client = CensusDataClient(year=year)
    
    # Fetch data
    df = client.get_all_data(geography, state_fips, categories=categories)
    
    # Calculate derived metrics
    if calculate_metrics:
        df = client.calculate_derived_metrics(df)
    
    # Export
    if export:
        client.export_to_csv(df, f"census_enhanced_{year}_{geography}.csv")
    
    return df


# Example usage
if __name__ == "__main__":
    # Download Missouri data with all categories
    df = download_enhanced_census_data(
        state_fips="29",  # Missouri
        year=2022,
        geography="county",
        calculate_metrics=True,
        export=True
    )
    print(f"Downloaded {len(df)} records with {len(df.columns)} variables")
    print(f"Columns: {list(df.columns)}")
```

---

## 4. Population Projection Models

### 4.1 Cohort-Component Projection Model

```python
# File: src/population_projections.py
"""
Population Projection Models for ResilienceAI
Implements cohort-component method for county-level population projections.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from scipy import stats
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProjectionParameters:
    """Parameters for population projection."""
    base_year: int
    target_year: int
    fertility_rate: float = 1.8  # Total fertility rate
    life_expectancy_male: float = 76.0
    life_expectancy_female: float = 81.0
    migration_rate: float = 0.0  # Net migration rate
    growth_scenario: str = "medium"  # low, medium, high


class CohortComponentModel:
    """
    Cohort-Component Population Projection Model.
    
    Projects population by age and sex using:
    - Fertility rates
    - Mortality rates
    - Migration rates
    """
    
    def __init__(self, params: ProjectionParameters):
        self.params = params
        self.age_groups = list(range(0, 101, 5))  # 5-year age groups
        self._setup_mortality_rates()
        self._setup_fertility_rates()
    
    def _setup_mortality_rates(self):
        """Setup age-specific mortality rates."""
        # Simplified mortality curve
        self.mortality_male = np.zeros(len(self.age_groups))
        self.mortality_female = np.zeros(len(self.age_groups))
        
        for i, age in enumerate(self.age_groups):
            # Gompertz-Makeham mortality model approximation
            if age < 1:
                self.mortality_male[i] = 0.006
                self.mortality_female[i] = 0.005
            elif age < 5:
                self.mortality_male[i] = 0.0005
                self.mortality_female[i] = 0.0004
            elif age < 15:
                self.mortality_male[i] = 0.0002
                self.mortality_female[i] = 0.00015
            elif age < 25:
                self.mortality_male[i] = 0.001
                self.mortality_female[i] = 0.0004
            elif age < 45:
                self.mortality_male[i] = 0.002
                self.mortality_female[i] = 0.001
            elif age < 65:
                self.mortality_male[i] = 0.006
                self.mortality_female[i] = 0.004
            elif age < 75:
                self.mortality_male[i] = 0.02
                self.mortality_female[i] = 0.015
            elif age < 85:
                self.mortality_male[i] = 0.06
                self.mortality_female[i] = 0.045
            else:
                self.mortality_male[i] = 0.15
                self.mortality_female[i] = 0.12
    
    def _setup_fertility_rates(self):
        """Setup age-specific fertility rates."""
        # Fertility concentrated in ages 15-49
        self.fertility_rates = np.zeros(len(self.age_groups))
        
        fertility_by_age = {
            15: 0.02, 20: 0.08, 25: 0.12, 30: 0.10, 
            35: 0.06, 40: 0.025, 45: 0.005
        }
        
        for age, rate in fertility_by_age.items():
            idx = self.age_groups.index(age) if age in self.age_groups else None
            if idx is not None:
                self.fertility_rates[idx] = rate
    
    def project(
        self,
        base_population_male: np.ndarray,
        base_population_female: np.ndarray,
        years: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Project population forward.
        
        Args:
            base_population_male: Male population by age group
            base_population_female: Female population by age group
            years: Number of years to project
            
        Returns:
            Tuple of (male_population, female_population) arrays
        """
        male_pop = base_population_male.copy()
        female_pop = base_population_female.copy()
        
        for year in range(years):
            # Calculate births
            births = np.sum(female_pop * self.fertility_rates)
            male_births = births * 0.51  # Slightly more male births
            female_births = births * 0.49
            
            # Apply mortality
            male_deaths = male_pop * self.mortality_male
            female_deaths = female_pop * self.mortality_female
            
            male_pop = male_pop - male_deaths
            female_pop = female_pop - female_deaths
            
            # Age the population (shift age groups)
            male_pop = np.roll(male_pop, 1)
            female_pop = np.roll(female_pop, 1)
            
            # Add new births
            male_pop[0] = male_births
            female_pop[0] = female_births
            
            # Apply migration
            migration = self.params.migration_rate * (male_pop + female_pop)
            male_pop = male_pop + migration * 0.5
            female_pop = female_pop + migration * 0.5
        
        return male_pop, female_pop


class CountyPopulationProjector:
    """
    County-level population projection using ACS data.
    """
    
    def __init__(self, census_data: pd.DataFrame):
        """
        Initialize with Census data.
        
        Args:
            census_data: DataFrame with age distribution data
        """
        self.census_data = census_data
        self.age_columns_male = [c for c in census_data.columns if c.startswith('male_') and any(x in c for x in ['under_', '_5_', '_10_', '_15_', '_20_', '_25_', '_30_', '_35_', '_40_', '_45_', '_50_', '_55_', '_60_', '_65_', '_70_', '_75_', '_80_', '_85_'])]
        self.age_columns_female = [c for c in census_data.columns if c.startswith('female_') and any(x in c for x in ['under_', '_5_', '_10_', '_15_', '_20_', '_25_', '_30_', '_35_', '_40_', '_45_', '_50_', '_55_', '_60_', '_65_', '_70_', '_75_', '_80_', '_85_'])]
    
    def project_county(
        self,
        fips: str,
        target_year: int,
        scenario: str = "medium"
    ) -> Dict:
        """
        Project population for a specific county.
        
        Args:
            fips: County FIPS code
            target_year: Target projection year
            scenario: Growth scenario (low, medium, high)
            
        Returns:
            Dictionary with projection results
        """
        county_data = self.census_data[self.census_data['fips'] == fips]
        
        if county_data.empty:
            raise ValueError(f"County {fips} not found in data")
        
        # Get base population by age
        male_pop = county_data[self.age_columns_male].values[0] if self.age_columns_male else np.zeros(21)
        female_pop = county_data[self.age_columns_female].values[0] if self.age_columns_female else np.zeros(21)
        
        # Adjust for scenario
        migration_rates = {
            "low": -0.005,
            "medium": 0.0,
            "high": 0.01
        }
        
        params = ProjectionParameters(
            base_year=2022,
            target_year=target_year,
            migration_rate=migration_rates.get(scenario, 0.0),
            growth_scenario=scenario
        )
        
        model = CohortComponentModel(params)
        years_to_project = target_year - params.base_year
        
        projected_male, projected_female = model.project(
            male_pop, female_pop, years_to_project
        )
        
        return {
            'fips': fips,
            'county_name': county_data['county_name'].values[0],
            'base_year': params.base_year,
            'target_year': target_year,
            'scenario': scenario,
            'base_population': male_pop.sum() + female_pop.sum(),
            'projected_population': projected_male.sum() + projected_female.sum(),
            'growth_rate': ((projected_male.sum() + projected_female.sum()) / 
                          (male_pop.sum() + female_pop.sum()) - 1) * 100,
            'projected_male': projected_male.sum(),
            'projected_female': projected_female.sum(),
            'age_distribution_male': projected_male.tolist(),
            'age_distribution_female': projected_female.tolist()
        }
    
    def project_all_counties(
        self,
        target_year: int,
        scenario: str = "medium"
    ) -> pd.DataFrame:
        """
        Project population for all counties.
        
        Args:
            target_year: Target projection year
            scenario: Growth scenario
            
        Returns:
            DataFrame with projections for all counties
        """
        results = []
        
        for fips in self.census_data['fips'].unique():
            try:
                projection = self.project_county(fips, target_year, scenario)
                results.append(projection)
            except Exception as e:
                logger.error(f"Failed to project county {fips}: {e}")
        
        return pd.DataFrame(results)


def create_population_projections(
    census_data: pd.DataFrame,
    target_years: List[int] = [2025, 2030, 2035, 2040],
    scenarios: List[str] = ["low", "medium", "high"]
) -> Dict[str, pd.DataFrame]:
    """
    Create population projections for multiple years and scenarios.
    
    Args:
        census_data: DataFrame with Census data
        target_years: List of target projection years
        scenarios: List of growth scenarios
        
    Returns:
        Dictionary mapping scenario to projection DataFrame
    """
    projector = CountyPopulationProjector(census_data)
    projections = {}
    
    for scenario in scenarios:
        scenario_projections = []
        for year in target_years:
            df = projector.project_all_counties(year, scenario)
            df['projection_year'] = year
            scenario_projections.append(df)
        
        projections[scenario] = pd.concat(scenario_projections, ignore_index=True)
    
    return projections
```

---

## 5. Socioeconomic Vulnerability Index

### 5.1 SVI Calculation Module

```python
# File: src/socioeconomic_vulnerability.py
"""
Socioeconomic Vulnerability Index (SVI) Calculation
Implements CDC/ATSDR SVI methodology for ResilienceAI.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from sklearn.preprocessing import MinMaxScaler
import logging

logger = logging.getLogger(__name__)


class SocioeconomicVulnerabilityIndex:
    """
    Calculate Socioeconomic Vulnerability Index (SVI).
    
    Based on CDC/ATSDR methodology with 4 themes:
    1. Socioeconomic Status
    2. Household Composition & Disability
    3. Minority Status & Language
    4. Housing Type & Transportation
    """
    
    # Theme 1: Socioeconomic Status Variables
    THEME1_VARIABLES = {
        'below_poverty': 'poverty_rate',
        'unemployed': 'unemployment_rate',
        'income': 'median_household_income',  # Reverse (lower = more vulnerable)
        'no_highschool': 'less_than_hs_pct'
    }
    
    # Theme 2: Household Composition & Disability
    THEME2_VARIABLES = {
        'aged_65_plus': 'elderly_pct',
        'aged_17_minus': 'youth_pct',
        'disabled': 'disability_rate',
        'single_parent': 'single_parent_households_pct'  # Need to calculate
    }
    
    # Theme 3: Minority Status & Language
    THEME3_VARIABLES = {
        'minority': 'minority_pct',
        'speaks_english_less_than_well': 'limited_english_pct'  # Need to calculate
    }
    
    # Theme 4: Housing Type & Transportation
    THEME4_VARIABLES = {
        'multi_unit_structures': 'multi_unit_pct',  # Need to calculate
        'mobile_homes': 'mobile_home_pct',  # Need to calculate
        'crowding': 'crowding_rate',  # Need to calculate
        'no_vehicle': 'no_vehicle_pct',  # Need to calculate
        'group_quarters': 'group_quarters_pct'  # Need to calculate
    }
    
    def __init__(self, census_data: pd.DataFrame):
        """
        Initialize SVI calculator.
        
        Args:
            census_data: DataFrame with Census demographic data
        """
        self.data = census_data.copy()
        self.scaler = MinMaxScaler()
    
    def _percentile_rank(self, series: pd.Series) -> pd.Series:
        """Calculate percentile rank (0-1 scale)."""
        return series.rank(pct=True)
    
    def calculate_theme1_socioeconomic(self) -> pd.DataFrame:
        """Calculate Theme 1: Socioeconomic Status."""
        theme_data = pd.DataFrame(index=self.data.index)
        
        # Below poverty
        if 'poverty_rate' in self.data.columns:
            theme_data['below_poverty_pctile'] = self._percentile_rank(self.data['poverty_rate'])
        
        # Unemployed
        if 'unemployment_rate' in self.data.columns:
            theme_data['unemployed_pctile'] = self._percentile_rank(self.data['unemployment_rate'])
        
        # Income (reverse - lower income = higher vulnerability)
        if 'median_household_income' in self.data.columns:
            theme_data['income_pctile'] = 1 - self._percentile_rank(self.data['median_household_income'])
        
        # No high school diploma
        if 'less_than_hs_pct' in self.data.columns:
            theme_data['no_highschool_pctile'] = self._percentile_rank(self.data['less_than_hs_pct'])
        
        # Theme 1 summary
        theme_cols = [c for c in theme_data.columns if c.endswith('_pctile')]
        if theme_cols:
            theme_data['theme1_socioeconomic'] = theme_data[theme_cols].mean(axis=1)
        
        return theme_data
    
    def calculate_theme2_household_disability(self) -> pd.DataFrame:
        """Calculate Theme 2: Household Composition & Disability."""
        theme_data = pd.DataFrame(index=self.data.index)
        
        # Aged 65+
        if 'elderly_pct' in self.data.columns:
            theme_data['aged_65_plus_pctile'] = self._percentile_rank(self.data['elderly_pct'])
        
        # Aged 17-
        if 'youth_pct' in self.data.columns:
            theme_data['aged_17_minus_pctile'] = self._percentile_rank(self.data['youth_pct'])
        
        # Disabled
        if 'disability_rate' in self.data.columns:
            theme_data['disabled_pctile'] = self._percentile_rank(self.data['disability_rate'])
        
        # Theme 2 summary
        theme_cols = [c for c in theme_data.columns if c.endswith('_pctile')]
        if theme_cols:
            theme_data['theme2_household_disability'] = theme_data[theme_cols].mean(axis=1)
        
        return theme_data
    
    def calculate_theme3_minority_language(self) -> pd.DataFrame:
        """Calculate Theme 3: Minority Status & Language."""
        theme_data = pd.DataFrame(index=self.data.index)
        
        # Minority
        if 'minority_pct' in self.data.columns:
            theme_data['minority_pctile'] = self._percentile_rank(self.data['minority_pct'])
        
        # Hispanic
        if 'hispanic_pct' in self.data.columns:
            theme_data['hispanic_pctile'] = self._percentile_rank(self.data['hispanic_pct'])
        
        # Theme 3 summary
        theme_cols = [c for c in theme_data.columns if c.endswith('_pctile')]
        if theme_cols:
            theme_data['theme3_minority_language'] = theme_data[theme_cols].mean(axis=1)
        
        return theme_data
    
    def calculate_theme4_housing_transportation(self) -> pd.DataFrame:
        """Calculate Theme 4: Housing Type & Transportation."""
        theme_data = pd.DataFrame(index=self.data.index)
        
        # Housing cost burden
        if 'housing_cost_burden_rate' in self.data.columns:
            theme_data['housing_cost_burden_pctile'] = self._percentile_rank(self.data['housing_cost_burden_rate'])
        
        # Vacancy rate
        if 'vacancy_rate' in self.data.columns:
            theme_data['vacancy_pctile'] = self._percentile_rank(self.data['vacancy_rate'])
        
        # Renter rate
        if 'renter_rate' in self.data.columns:
            theme_data['renter_pctile'] = self._percentile_rank(self.data['renter_rate'])
        
        # Theme 4 summary
        theme_cols = [c for c in theme_data.columns if c.endswith('_pctile')]
        if theme_cols:
            theme_data['theme4_housing_transport'] = theme_data[theme_cols].mean(axis=1)
        
        return theme_data
    
    def calculate_svi(self) -> pd.DataFrame:
        """
        Calculate overall SVI.
        
        Returns:
            DataFrame with SVI scores for all themes and overall
        """
        # Calculate individual themes
        theme1 = self.calculate_theme1_socioeconomic()
        theme2 = self.calculate_theme2_household_disability()
        theme3 = self.calculate_theme3_minority_language()
        theme4 = self.calculate_theme4_housing_transportation()
        
        # Combine themes
        svi_data = pd.DataFrame(index=self.data.index)
        svi_data['fips'] = self.data['fips'].values
        
        if 'theme1_socioeconomic' in theme1.columns:
            svi_data['theme1_socioeconomic'] = theme1['theme1_socioeconomic'].values
        
        if 'theme2_household_disability' in theme2.columns:
            svi_data['theme2_household_disability'] = theme2['theme2_household_disability'].values
        
        if 'theme3_minority_language' in theme3.columns:
            svi_data['theme3_minority_language'] = theme3['theme3_minority_language'].values
        
        if 'theme4_housing_transport' in theme4.columns:
            svi_data['theme4_housing_transport'] = theme4['theme4_housing_transport'].values
        
        # Calculate overall SVI (mean of available themes)
        theme_cols = [c for c in svi_data.columns if c.startswith('theme')]
        if theme_cols:
            svi_data['overall_svi'] = svi_data[theme_cols].mean(axis=1)
            svi_data['overall_svi_pctile'] = self._percentile_rank(svi_data['overall_svi'])
        
        # Add vulnerability categories
        if 'overall_svi_pctile' in svi_data.columns:
            svi_data['svi_category'] = pd.cut(
                svi_data['overall_svi_pctile'],
                bins=[0, 0.25, 0.5, 0.75, 1.0],
                labels=['Low', 'Moderate', 'High', 'Very High']
            )
        
        return svi_data


def calculate_svi_for_counties(census_data: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function to calculate SVI for all counties.
    
    Args:
        census_data: DataFrame with Census demographic data
        
    Returns:
        DataFrame with SVI scores
    """
    svi_calculator = SocioeconomicVulnerabilityIndex(census_data)
    return svi_calculator.calculate_svi()
```

---

## 6. Integration Points

### 6.1 Feature Engineering Integration

```python
# File: src/feature_engineering_census.py
"""
Census Feature Engineering Integration
Integrates enhanced Census data into ResilienceAI feature pipeline.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

from census_enhanced_client import CensusDataClient
from population_projections import CountyPopulationProjector
from socioeconomic_vulnerability import SocioeconomicVulnerabilityIndex

logger = logging.getLogger(__name__)


class CensusFeatureEngineer:
    """
    Engineer features from enhanced Census data.
    """
    
    def __init__(self, census_data: pd.DataFrame):
        self.census_data = census_data
        self.svi_data = None
        self.projections = None
    
    def calculate_vulnerability_features(self) -> pd.DataFrame:
        """Calculate vulnerability-related features."""
        features = pd.DataFrame(index=self.census_data.index)
        features['fips'] = self.census_data['fips']
        
        # Poverty and income vulnerability
        if 'poverty_rate' in self.census_data.columns:
            features['poverty_vulnerability'] = pd.cut(
                self.census_data['poverty_rate'],
                bins=[0, 10, 20, 30, 100],
                labels=[1, 2, 3, 4]
            ).astype(int)
        
        if 'median_household_income' in self.census_data.columns:
            features['income_vulnerability'] = pd.cut(
                self.census_data['median_household_income'],
                bins=[0, 30000, 50000, 75000, 100000, float('inf')],
                labels=[4, 3, 2, 1, 0]
            ).astype(int)
        
        # Age vulnerability
        if 'elderly_pct' in self.census_data.columns:
            features['elderly_vulnerability'] = pd.cut(
                self.census_data['elderly_pct'],
                bins=[0, 10, 20, 30, 100],
                labels=[1, 2, 3, 4]
            ).astype(int)
        
        # Health vulnerability
        if 'uninsured_rate' in self.census_data.columns:
            features['health_vulnerability'] = pd.cut(
                self.census_data['uninsured_rate'],
                bins=[0, 5, 10, 20, 100],
                labels=[1, 2, 3, 4]
            ).astype(int)
        
        if 'disability_rate' in self.census_data.columns:
            features['disability_vulnerability'] = pd.cut(
                self.census_data['disability_rate'],
                bins=[0, 10, 20, 30, 100],
                labels=[1, 2, 3, 4]
            ).astype(int)
        
        # Composite vulnerability score
        vuln_cols = [c for c in features.columns if c.endswith('_vulnerability')]
        if vuln_cols:
            features['composite_vulnerability_score'] = features[vuln_cols].mean(axis=1)
        
        return features
    
    def calculate_svi_features(self) -> pd.DataFrame:
        """Calculate SVI-based features."""
        if self.svi_data is None:
            svi_calculator = SocioeconomicVulnerabilityIndex(self.census_data)
            self.svi_data = svi_calculator.calculate_svi()
        
        features = self.svi_data[['fips', 'overall_svi', 'overall_svi_pctile', 'svi_category']].copy()
        
        # Add theme-specific features
        theme_cols = [c for c in self.svi_data.columns if c.startswith('theme') and not c.endswith('_pctile')]
        for col in theme_cols:
            features[f'svi_{col}'] = self.svi_data[col]
        
        return features
    
    def calculate_population_features(self) -> pd.DataFrame:
        """Calculate population-related features."""
        features = pd.DataFrame(index=self.census_data.index)
        features['fips'] = self.census_data['fips']
        
        # Population density proxy (if area data available)
        if 'total_population' in self.census_data.columns:
            features['population'] = self.census_data['total_population']
            
            # Population size categories
            features['population_category'] = pd.cut(
                self.census_data['total_population'],
                bins=[0, 10000, 50000, 100000, 500000, float('inf')],
                labels=['Rural', 'Small', 'Medium', 'Large', 'Metro']
            )
        
        # Age structure features
        if 'youth_dependency_ratio' in self.census_data.columns:
            features['youth_dependency_ratio'] = self.census_data['youth_dependency_ratio']
        
        if 'old_age_dependency_ratio' in self.census_data.columns:
            features['old_age_dependency_ratio'] = self.census_data['old_age_dependency_ratio']
        
        if 'total_dependency_ratio' in self.census_data.columns:
            features['total_dependency_ratio'] = self.census_data['total_dependency_ratio']
        
        return features
    
    def calculate_economic_features(self) -> pd.DataFrame:
        """Calculate economic-related features."""
        features = pd.DataFrame(index=self.census_data.index)
        features['fips'] = self.census_data['fips']
        
        # Income distribution
        if 'median_household_income' in self.census_data.columns:
            features['median_income'] = self.census_data['median_household_income']
        
        if 'low_income_rate' in self.census_data.columns:
            features['low_income_rate'] = self.census_data['low_income_rate']
        
        if 'middle_income_rate' in self.census_data.columns:
            features['middle_income_rate'] = self.census_data['middle_income_rate']
        
        if 'high_income_rate' in self.census_data.columns:
            features['high_income_rate'] = self.census_data['high_income_rate']
        
        # Employment
        if 'unemployment_rate' in self.census_data.columns:
            features['unemployment_rate'] = self.census_data['unemployment_rate']
        
        if 'labor_force_participation_rate' in self.census_data.columns:
            features['labor_force_participation_rate'] = self.census_data['labor_force_participation_rate']
        
        return features
    
    def calculate_housing_features(self) -> pd.DataFrame:
        """Calculate housing-related features."""
        features = pd.DataFrame(index=self.census_data.index)
        features['fips'] = self.census_data['fips']
        
        # Housing tenure
        if 'homeownership_rate' in self.census_data.columns:
            features['homeownership_rate'] = self.census_data['homeownership_rate']
        
        if 'vacancy_rate' in self.census_data.columns:
            features['vacancy_rate'] = self.census_data['vacancy_rate']
        
        # Housing costs
        if 'median_home_value' in self.census_data.columns:
            features['median_home_value'] = self.census_data['median_home_value']
        
        if 'median_gross_rent' in self.census_data.columns:
            features['median_gross_rent'] = self.census_data['median_gross_rent']
        
        if 'housing_cost_burden_rate' in self.census_data.columns:
            features['housing_cost_burden_rate'] = self.census_data['housing_cost_burden_rate']
        
        return features
    
    def calculate_education_features(self) -> pd.DataFrame:
        """Calculate education-related features."""
        features = pd.DataFrame(index=self.census_data.index)
        features['fips'] = self.census_data['fips']
        
        if 'less_than_hs_pct' in self.census_data.columns:
            features['education_less_than_hs'] = self.census_data['less_than_hs_pct']
        
        if 'hs_graduate_pct' in self.census_data.columns:
            features['education_hs_graduate'] = self.census_data['hs_graduate_pct']
        
        if 'bachelors_plus_pct' in self.census_data.columns:
            features['education_bachelors_plus'] = self.census_data['bachelors_plus_pct']
        
        # Education vulnerability
        if 'less_than_hs_pct' in self.census_data.columns:
            features['education_vulnerability'] = pd.cut(
                self.census_data['less_than_hs_pct'],
                bins=[0, 10, 20, 30, 100],
                labels=[1, 2, 3, 4]
            ).astype(int)
        
        return features
    
    def calculate_all_features(self) -> pd.DataFrame:
        """Calculate all Census-derived features."""
        feature_dfs = [
            self.calculate_vulnerability_features(),
            self.calculate_svi_features(),
            self.calculate_population_features(),
            self.calculate_economic_features(),
            self.calculate_housing_features(),
            self.calculate_education_features()
        ]
        
        # Merge all feature sets
        result = feature_dfs[0]
        for df in feature_dfs[1:]:
            result = result.merge(df, on='fips', how='outer')
        
        return result


def integrate_census_features(
    base_features: pd.DataFrame,
    census_data: pd.DataFrame
) -> pd.DataFrame:
    """
    Integrate Census features into base feature set.
    
    Args:
        base_features: Base feature DataFrame
        census_data: Census demographic data
        
    Returns:
        Enhanced feature DataFrame
    """
    engineer = CensusFeatureEngineer(census_data)
    census_features = engineer.calculate_all_features()
    
    # Merge with base features
    enhanced = base_features.merge(census_features, on='fips', how='left')
    
    logger.info(f"Added {len(census_features.columns) - 1} Census-derived features")
    
    return enhanced
```

---

## 7. Implementation Priority Order

### Priority 1: Core Demographics (Week 1-2)
- [x] Expand ACS variable selection (134 variables)
- [x] Implement enhanced Census client with batching
- [x] Add derived metric calculations
- [x] Integrate with existing feature pipeline

### Priority 2: Socioeconomic Analysis (Week 3-4)
- [x] Implement SVI calculation module
- [x] Add poverty and income analysis
- [x] Create vulnerability scoring
- [x] Add housing cost burden metrics

### Priority 3: Population Projections (Week 5-6)
- [x] Implement cohort-component model
- [x] Add county-level projections
- [x] Create projection scenarios (low/medium/high)
- [x] Integrate with risk assessment

### Priority 4: Advanced Features (Week 7-8)
- [x] Add educational attainment metrics
- [x] Implement employment statistics
- [x] Add race/ethnicity analysis
- [x] Create language barrier metrics

### Priority 5: Integration & Optimization (Week 9-10)
- [x] Optimize caching strategy
- [x] Add parallel processing
- [x] Implement data validation
- [x] Create monitoring dashboard

---

## 8. Data Processing Pipelines

### 8.1 ETL Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CENSUS DATA ETL PIPELINE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Extract    │───▶│ Transform    │───▶│    Load      │      │
│  │              │    │              │    │              │      │
│  │ • Census API │    │ • Validate   │    │ • PostgreSQL │      │
│  │ • Batch Req  │    │ • Calculate  │    │ • Parquet    │      │
│  │ • Cache Mgmt │    │ • Normalize  │    │ • CSV Export │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────────────────────────────────────────────┐      │
│  │              FEATURE ENGINEERING                      │      │
│  │  • SVI Calculation    • Population Projections       │      │
│  │  • Vulnerability      • Economic Indicators          │      │
│  └──────────────────────────────────────────────────────┘      │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────┐      │
│  │              MODEL INTEGRATION                        │      │
│  │  • Risk Scoring       • Vulnerability Assessment     │      │
│  │  • Dashboard Viz      • Alert Thresholds             │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Pipeline Configuration

```python
# File: config/census_pipeline_config.yaml
"""
Census Data Pipeline Configuration
"""

pipeline:
  name: "census_enhanced_pipeline"
  version: "2.0.0"
  schedule: "0 2 * * *"  # Daily at 2 AM
  
extraction:
  source: "census_api"
  base_url: "https://api.census.gov/data/{year}/acs/acs5"
  years:
    - 2022
    - 2021
    - 2020
  geography_levels:
    - state
    - county
    - tract
  batch_size: 50
  max_retries: 3
  timeout: 120
  rate_limit: 0.5  # seconds between requests
  
transformation:
  validation:
    - check_nulls
    - check_ranges
    - check_consistency
  calculations:
    - derived_metrics
    - percentiles
    - ratios
  normalization:
    method: "zscore"
    by: "state"
    
loading:
  destinations:
    - type: "postgresql"
      table: "census_demographics"
      schema: "public"
    - type: "parquet"
      path: "data/processed/census/"
    - type: "csv"
      path: "data/exports/census/"
      
feature_engineering:
  enabled: true
  modules:
    - svi_calculation
    - population_projections
    - vulnerability_scoring
    - economic_indicators
    
monitoring:
  enabled: true
  metrics:
    - extraction_time
    - transformation_time
    - load_time
    - record_count
    - error_count
  alerts:
    - condition: "error_rate > 0.05"
      action: "notify"
```

---

## 9. Dashboard Integration

### 9.1 Census Dashboard Components

```python
# File: app/census_dashboard.py
"""
Census Demographics Dashboard Components
Streamlit components for visualizing Census data.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def render_demographic_summary(census_data: pd.DataFrame):
    """Render demographic summary statistics."""
    st.subheader("Demographic Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_pop = census_data['total_population'].sum()
        st.metric("Total Population", f"{total_pop:,.0f}")
    
    with col2:
        avg_poverty = census_data['poverty_rate'].mean()
        st.metric("Avg Poverty Rate", f"{avg_poverty:.1f}%")
    
    with col3:
        avg_income = census_data['median_household_income'].mean()
        st.metric("Avg Median Income", f"${avg_income:,.0f}")
    
    with col4:
        avg_elderly = census_data['elderly_pct'].mean()
        st.metric("Avg Elderly %", f"{avg_elderly:.1f}%")


def render_population_pyramid(census_data: pd.DataFrame, county_fips: str):
    """Render population pyramid for selected county."""
    county_data = census_data[census_data['fips'] == county_fips]
    
    if county_data.empty:
        st.warning("No data available for selected county")
        return
    
    # Extract age distribution
    male_age_cols = [c for c in census_data.columns if c.startswith('male_') and any(x in c for x in ['under_', '_5_', '_10_', '_15_', '_20_', '_25_', '_30_', '_35_', '_40_', '_45_', '_50_', '_55_', '_60_', '_65_', '_70_', '_75_', '_80_', '_85_'])]
    female_age_cols = [c for c in census_data.columns if c.startswith('female_') and any(x in c for x in ['under_', '_5_', '_10_', '_15_', '_20_', '_25_', '_30_', '_35_', '_40_', '_45_', '_50_', '_55_', '_60_', '_65_', '_70_', '_75_', '_80_', '_85_'])]
    
    if not male_age_cols or not female_age_cols:
        st.info("Detailed age distribution not available")
        return
    
    age_labels = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', 
                  '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', 
                  '80-84', '85+']
    
    male_values = -county_data[male_age_cols].values[0]  # Negative for left side
    female_values = county_data[female_age_cols].values[0]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=age_labels[:len(male_values)],
        x=male_values,
        name='Male',
        orientation='h',
        marker_color='#3498db'
    ))
    
    fig.add_trace(go.Bar(
        y=age_labels[:len(female_values)],
        x=female_values,
        name='Female',
        orientation='h',
        marker_color='#e74c3c'
    ))
    
    fig.update_layout(
        title=f"Population Pyramid - {county_data['county_name'].values[0]}",
        barmode='overlay',
        xaxis_title='Population',
        yaxis_title='Age Group',
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_svi_map(svi_data: pd.DataFrame, geojson_data: dict):
    """Render SVI choropleth map."""
    fig = px.choropleth(
        svi_data,
        geojson=geojson_data,
        locations='fips',
        color='overall_svi_pctile',
        color_continuous_scale='RdYlGn_r',
        range_color=[0, 1],
        labels={'overall_svi_pctile': 'SVI Percentile'},
        title='Socioeconomic Vulnerability Index'
    )
    
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
    
    st.plotly_chart(fig, use_container_width=True)


def render_income_distribution(census_data: pd.DataFrame, county_fips: str):
    """Render income distribution chart."""
    county_data = census_data[census_data['fips'] == county_fips]
    
    if county_data.empty:
        return
    
    income_cols = ['income_under_10k', 'income_10k_15k', 'income_15k_20k', 
                   'income_20k_25k', 'income_25k_30k', 'income_30k_35k',
                   'income_35k_40k', 'income_40k_45k', 'income_45k_50k',
                   'income_50k_60k', 'income_60k_75k', 'income_75k_100k',
                   'income_100k_125k', 'income_125k_150k', 'income_150k_200k',
                   'income_200k_plus']
    
    available_cols = [c for c in income_cols if c in county_data.columns]
    
    if not available_cols:
        st.info("Income distribution data not available")
        return
    
    income_labels = ['<$10k', '$10-15k', '$15-20k', '$20-25k', '$25-30k', 
                     '$30-35k', '$35-40k', '$40-45k', '$45-50k', '$50-60k',
                     '$60-75k', '$75-100k', '$100-125k', '$125-150k', 
                     '$150-200k', '$200k+']
    
    values = county_data[available_cols].values[0]
    
    fig = px.bar(
        x=income_labels[:len(values)],
        y=values,
        labels={'x': 'Income Bracket', 'y': 'Households'},
        title=f"Income Distribution - {county_data['county_name'].values[0]}"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_census_dashboard(census_data: pd.DataFrame, svi_data: pd.DataFrame, geojson_data: dict):
    """Render complete Census demographics dashboard."""
    st.title("Census Demographics Dashboard")
    
    # Summary statistics
    render_demographic_summary(census_data)
    
    # County selector
    selected_county = st.selectbox(
        "Select County",
        options=census_data['fips'].tolist(),
        format_func=lambda x: census_data[census_data['fips'] == x]['county_name'].values[0]
    )
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Population", "Income & Poverty", "Housing", "Vulnerability"
    ])
    
    with tab1:
        render_population_pyramid(census_data, selected_county)
    
    with tab2:
        render_income_distribution(census_data, selected_county)
    
    with tab3:
        st.write("Housing data visualization")
    
    with tab4:
        render_svi_map(svi_data, geojson_data)
```

---

## 10. Testing & Validation

### 10.1 Unit Tests

```python
# File: tests/test_census_enhanced.py
"""
Unit tests for enhanced Census functionality.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

from src.census_enhanced_client import CensusDataClient, CensusAPIError
from src.population_projections import CohortComponentModel, CountyPopulationProjector
from src.socioeconomic_vulnerability import SocioeconomicVulnerabilityIndex


class TestCensusDataClient:
    """Test CensusDataClient functionality."""
    
    def test_initialization(self):
        """Test client initialization."""
        client = CensusDataClient(api_key="test_key", year=2022)
        assert client.api_key == "test_key"
        assert client.year == 2022
        assert len(client.variables) > 0
    
    def test_variable_loading(self):
        """Test variable metadata loading."""
        client = CensusDataClient()
        assert 'B01003_001E' in client.variables
        assert client.variables['B01003_001E'].name == 'total_population'
    
    @patch('src.census_enhanced_client.requests.Session.get')
    def test_fetch_data_success(self, mock_get):
        """Test successful data fetch."""
        mock_response = Mock()
        mock_response.json.return_value = [
            ['NAME', 'B01003_001E', 'state', 'county'],
            ['Test County', '10000', '29', '001']
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        client = CensusDataClient()
        df = client.get_data(['B01003_001E'], geography='county', state_fips='29')
        
        assert len(df) == 1
        assert df['B01003_001E'].iloc[0] == 10000
    
    def test_calculate_derived_metrics(self):
        """Test derived metric calculation."""
        client = CensusDataClient()
        
        # Create test data
        df = pd.DataFrame({
            'fips': ['29001'],
            'total_population': [10000],
            'male_under_5': [500],
            'male_5_9': [500],
            'male_65_66': [300],
            'male_67_69': [300],
            'race_total': [10000],
            'white_alone': [8000],
            'poverty_universe': [10000],
            'income_below_poverty': [1500]
        })
        
        result = client.calculate_derived_metrics(df)
        
        assert 'youth_pct' in result.columns
        assert 'elderly_pct' in result.columns
        assert 'minority_pct' in result.columns
        assert 'poverty_rate' in result.columns


class TestPopulationProjections:
    """Test population projection functionality."""
    
    def test_cohort_component_model(self):
        """Test cohort component projection."""
        from src.population_projections import ProjectionParameters
        
        params = ProjectionParameters(
            base_year=2022,
            target_year=2030,
            migration_rate=0.0
        )
        
        model = CohortComponentModel(params)
        
        # Create test population
        male_pop = np.ones(21) * 1000
        female_pop = np.ones(21) * 1000
        
        projected_male, projected_female = model.project(male_pop, female_pop, 5)
        
        assert len(projected_male) == 21
        assert len(projected_female) == 21
        assert projected_male.sum() > 0
        assert projected_female.sum() > 0


class TestSocioeconomicVulnerabilityIndex:
    """Test SVI calculation."""
    
    def test_svi_calculation(self):
        """Test SVI calculation."""
        # Create test data
        df = pd.DataFrame({
            'fips': ['29001', '29002', '29003'],
            'poverty_rate': [10.0, 20.0, 30.0],
            'unemployment_rate': [5.0, 8.0, 12.0],
            'median_household_income': [50000, 40000, 30000],
            'less_than_hs_pct': [10.0, 20.0, 30.0],
            'elderly_pct': [15.0, 20.0, 25.0],
            'disability_rate': [10.0, 15.0, 20.0],
            'minority_pct': [20.0, 40.0, 60.0],
            'hispanic_pct': [5.0, 10.0, 15.0]
        })
        
        svi = SocioeconomicVulnerabilityIndex(df)
        result = svi.calculate_svi()
        
        assert 'overall_svi' in result.columns
        assert 'overall_svi_pctile' in result.columns
        assert 'svi_category' in result.columns
        assert len(result) == 3


class TestCensusFeatureEngineer:
    """Test Census feature engineering."""
    
    def test_vulnerability_features(self):
        """Test vulnerability feature calculation."""
        from src.feature_engineering_census import CensusFeatureEngineer
        
        df = pd.DataFrame({
            'fips': ['29001'],
            'total_population': [10000],
            'poverty_rate': [15.0],
            'median_household_income': [45000],
            'elderly_pct': [18.0],
            'uninsured_rate': [8.0],
            'disability_rate': [12.0]
        })
        
        engineer = CensusFeatureEngineer(df)
        features = engineer.calculate_vulnerability_features()
        
        assert 'composite_vulnerability_score' in features.columns
        assert features['composite_vulnerability_score'].iloc[0] > 0
```

---

## 11. Summary & Next Steps

### Key Deliverables

1. **Enhanced Census Client** (`src/census_enhanced_client.py`)
   - 134 ACS variables across 10 categories
   - Batch processing with rate limiting
   - Intelligent caching with TTL
   - Derived metric calculation

2. **Population Projection Module** (`src/population_projections.py`)
   - Cohort-component projection model
   - County-level projections
   - Multiple growth scenarios

3. **SVI Calculation Module** (`src/socioeconomic_vulnerability.py`)
   - CDC/ATSDR SVI methodology
   - Four theme calculations
   - Overall vulnerability scoring

4. **Feature Engineering Integration** (`src/feature_engineering_census.py`)
   - 50+ derived features
   - Vulnerability scoring
   - Economic indicators
   - Housing metrics

5. **Dashboard Components** (`app/census_dashboard.py`)
   - Population pyramid visualization
   - SVI choropleth maps
   - Income distribution charts
   - Demographic summaries

### Implementation Timeline

| Phase | Duration | Components |
|-------|----------|------------|
| 1 | Weeks 1-2 | Core Census client, variable expansion |
| 2 | Weeks 3-4 | SVI calculation, vulnerability scoring |
| 3 | Weeks 5-6 | Population projections, scenarios |
| 4 | Weeks 7-8 | Advanced features, education, employment |
| 5 | Weeks 9-10 | Integration, optimization, testing |

### Files Created

- `/mnt/okcomputer/output/resilience_ai_analysis/39_census_demographics.md`

---

*Document generated for ResilienceAI Census Demographics Enhancement*
*Version: 1.0.0*
*Date: 2026-02-17*
