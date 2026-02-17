# ResilienceAI Agent Swarm Feature Test Protocol

## System Under Test
ResilienceAI is an agentic disaster vulnerability intelligence platform with:
- **16 MCP tools** querying real data across 3,222 US counties
- **Gemini 2.5 Pro** LLM backend with tool-calling reasoning loop
- **Streamlit dashboard** at `https://patchworky-unnoisy-maverick.ngrok-free.dev`
- **Data sources**: FEMA, Census ACS, HIFLD, CMS, ACIS/PRISM, USGS, NOAA, US Drought Monitor

## Available Tools
| # | Tool | Input | Returns |
|---|------|-------|---------|
| 1 | `query_counties` | state (2-letter), max_results | Top N counties ranked by risk_score with demographics + infrastructure |
| 2 | `get_county_detail` | fips (5-digit) | Full 66-feature county profile |
| 3 | `get_state_rankings` | state (2-letter) | Top 10 highest-risk counties in state |
| 4 | `analyze_risk_contagion` | fips, radius_km | Neighbor risk analysis: count, high-risk neighbors, amplification factor |
| 5 | `calculate_pop_weighted_impact` | state (optional) | Counties ranked by risk_score × population |
| 6 | `get_infrastructure_density` | fips | Hospitals, EMS, fire, nursing homes per 10k population |
| 7 | `get_mo_health_disparities` | focus_metric | Top 10 Missouri counties by disparity index |
| 8 | `calculate_intervention_roi` | fips | Ranked interventions by cost per person helped |
| 9 | `simulate_scenario` | scenario, epicenter_fips | Disaster simulation: affected counties, population at risk, damage |
| 10 | `get_climate_trends` | fips, start_year, end_year | Temperature/precipitation trends with slopes |
| 11 | `get_hazard_risk_profile` | fips | FEMA NRI: 18 hazard types, Expected Annual Loss, Social Vulnerability |
| 12 | `get_flood_frequency` | fips | USGS streamflow, flood recurrence intervals (2-100yr) |
| 13 | `get_severe_weather_history` | fips, hazard_type, start_year | NOAA tornado/hail/wind event counts and summary |
| 14 | `get_drought_history` | fips, start_date, end_date | US Drought Monitor D0-D4 classifications over time |
| 15 | `compare_climate_trends` | fips_list, start_year | Side-by-side climate trajectories for multiple counties |
| 16 | `project_climate_risk_enhanced` | fips, scenario (ssp1_19/ssp2_45/ssp5_85), horizon_years | Future climate projection with risk implications |

## Reference FIPS Codes (Missouri)
- Boone County: 29019 (Columbia, university town, moderate risk)
- Jackson County: 29095 (Kansas City, urban, high population)
- St. Louis County: 29189 (metro, dense infrastructure)
- New Madrid County: 29143 (seismic zone, rural, high risk)
- Ozark County: 29153 (rural, isolated, high poverty)
- Greene County: 29077 (Springfield, mid-size)
- Pemiscot County: 29155 (Mississippi Delta, very high risk)
- Shannon County: 29203 (extremely rural, high vulnerability)

---

## TEST CASES

### Category A: Single-Tool Accuracy (8 tests)

**A1 — County Rankings**
- Query: "What are the top 5 most vulnerable counties in Missouri?"
- Expected tools: `query_counties` OR `get_state_rankings`
- Expected output: 5 counties with risk_score, risk_level, population, and brief explanation of WHY each is vulnerable
- Visual: Horizontal bar chart of risk scores + data table

**A2 — County Detail**
- Query: "Give me the full profile for Boone County, MO (FIPS 29019)"
- Expected tools: `get_county_detail`
- Expected output: Population, risk score, poverty %, uninsured %, hospital distance, disaster count
- Visual: 6 metric cards (population, risk, poverty, uninsured, hospital dist, disasters)

**A3 — Infrastructure Density**
- Query: "What is the emergency infrastructure density for Ozark County, MO (FIPS 29153)?"
- Expected tools: `get_infrastructure_density`
- Expected output: 4 density values (hospitals, EMS, fire, nursing per 10k)
- Visual: 4 metric cards

**A4 — Health Disparities**
- Query: "What are the worst health disparity zones in Missouri based on uninsured rates?"
- Expected tools: `get_mo_health_disparities`
- Expected output: 10 counties ranked by disparity index with specific uninsured percentages
- Visual: Horizontal bar chart of disparity index

**A5 — Intervention ROI**
- Query: "What is the most cost-effective intervention for Ozark County, Missouri (FIPS 29153)?"
- Expected tools: `calculate_intervention_roi`
- Expected output: Ranked list of interventions with cost per person and risk reduction estimate
- Visual: Horizontal bar chart of cost-effectiveness

**A6 — Scenario Simulation**
- Query: "Simulate a 7.0 earthquake centered on New Madrid County, MO (FIPS 29143)"
- Expected tools: `simulate_scenario` with scenario="earthquake_7.0", epicenter_fips="29143"
- Expected output: Counties affected, population at risk, infrastructure damage, cascading effects
- Visual: 3 impact metric cards + affected counties table

**A7 — Risk Contagion**
- Query: "Analyze risk contagion for St. Louis County, MO (FIPS 29189)"
- Expected tools: `analyze_risk_contagion`
- Expected output: Neighbor count, high-risk neighbors, amplification factor with interpretation
- Visual: 3 metric cards

**A8 — Population-Weighted Impact**
- Query: "Which Missouri counties have the highest population-weighted disaster risk?"
- Expected tools: `calculate_pop_weighted_impact`
- Expected output: Counties ranked by risk × population, showing how rankings shift vs raw risk
- Visual: Horizontal bar chart of weighted impact

### Category B: Climate Intelligence (6 tests)

**B1 — Climate Trends**
- Query: "What are the temperature and precipitation trends for Boone County, MO (FIPS 29019)?"
- Expected tools: `get_climate_trends`
- Expected output: Average temperature, trend slope (°F/decade), precipitation mean, direction of change
- Visual: 3 metric cards (avg temp, temp trend, avg precip)

**B2 — Hazard Risk Profile**
- Query: "What is the FEMA hazard risk profile for New Madrid County, MO (FIPS 29143)?"
- Expected tools: `get_hazard_risk_profile`
- Expected output: Risk rating, Expected Annual Loss, Social Vulnerability, top hazard types with scores
- Visual: 3 metric cards + hazard table

**B3 — Flood Frequency**
- Query: "What are the flood frequency estimates for New Madrid County, MO (FIPS 29143)?"
- Expected tools: `get_flood_frequency`
- Expected output: Recurrence interval flow rates (2, 5, 10, 25, 50, 100-year levels)
- Visual: Recurrence interval table

**B4 — Severe Weather History**
- Query: "What is the severe weather history for Greene County, MO (FIPS 29077)?"
- Expected tools: `get_severe_weather_history`
- Expected output: Tornado, hail, wind event counts with summary statistics
- Visual: Summary metric cards

**B5 — Drought History**
- Query: "Analyze drought history for Ozark County, MO (FIPS 29153)"
- Expected tools: `get_drought_history`
- Expected output: D0-D4 drought classification frequencies, worst drought periods
- Visual: Summary metric cards

**B6 — Climate Projection**
- Query: "Project climate risk for Jackson County, MO (FIPS 29095) under the worst-case SSP5-8.5 scenario over 30 years"
- Expected tools: `project_climate_risk_enhanced` with scenario="ssp5_85"
- Expected output: Projected temperature change, precipitation change %, extreme event multiplier
- Visual: 3 projection metric cards

### Category C: Multi-Tool Cross-Domain Reasoning (6 tests)

**C1 — Vulnerability + Infrastructure**
- Query: "For the 5 highest-risk counties in Missouri, what is their emergency infrastructure density? Are the most vulnerable counties also the most underserved?"
- Expected tools: `get_state_rankings` → then `get_infrastructure_density` for top counties
- Expected output: Cross-referenced analysis showing correlation (or lack) between risk and infrastructure gaps
- Minimum tool calls: 2+

**C2 — Climate + Vulnerability**
- Query: "What are the climate trends for Boone County, MO (FIPS 29019)? How do temperature trends and hazard risks interact with its existing vulnerability profile?"
- Expected tools: `get_climate_trends` + `get_hazard_risk_profile` + `get_county_detail`
- Expected output: Integrated analysis connecting climate trajectory to current vulnerability factors
- Minimum tool calls: 2+

**C3 — Triage Priority**
- Query: "If Missouri had $10M for disaster resilience, which 3 counties should receive funding first? Use risk scores, population impact, and infrastructure gaps to justify."
- Expected tools: `get_state_rankings` + `calculate_pop_weighted_impact` + `get_infrastructure_density` + `calculate_intervention_roi`
- Expected output: Ranked recommendation with specific dollar allocations and expected outcomes
- Minimum tool calls: 3+

**C4 — Cross-State Comparison**
- Query: "Compare the top 3 most vulnerable counties in Missouri vs Arkansas. What structural differences explain the gap?"
- Expected tools: `query_counties` (MO) + `query_counties` (AR)
- Expected output: Side-by-side comparison with specific metrics and structural analysis
- Minimum tool calls: 2

**C5 — Compound Risk Assessment**
- Query: "For Pemiscot County, MO (FIPS 29155), analyze the compound risk: combine its flood frequency, severe weather history, climate trajectory, and infrastructure gaps into a comprehensive threat assessment."
- Expected tools: `get_county_detail` + `get_flood_frequency` + `get_severe_weather_history` + `get_climate_trends` + `get_infrastructure_density`
- Expected output: Integrated compound risk narrative with data from all sources
- Minimum tool calls: 3+

**C6 — Scenario + Intervention Planning**
- Query: "Simulate a 500-year flood hitting New Madrid County, MO (FIPS 29143), then recommend the most cost-effective interventions for the 3 most affected counties."
- Expected tools: `simulate_scenario` → then `calculate_intervention_roi` for affected counties
- Expected output: Simulation results followed by targeted intervention recommendations
- Minimum tool calls: 2+

### Category D: Edge Cases & Robustness (5 tests)

**D1 — Ambiguous Query**
- Query: "Tell me about Missouri"
- Expected: Should call `query_counties` or `get_state_rankings` for MO, not hallucinate
- FAIL if: Makes up data without calling any tool

**D2 — Invalid FIPS**
- Query: "What is the risk profile for FIPS 99999?"
- Expected: Tool returns error, agent gracefully reports county not found
- FAIL if: Hallucinates data for non-existent county

**D3 — Non-Missouri Query**
- Query: "What are the top 5 most vulnerable counties in California?"
- Expected: `query_counties` with state="CA", returns valid California data
- FAIL if: Returns Missouri data or says it can only handle Missouri

**D4 — No-Tool Query**
- Query: "What methodology does ResilienceAI use to calculate risk scores?"
- Expected: Answers from system prompt knowledge without calling tools
- FAIL if: Calls tools unnecessarily

**D5 — Effort Slider Impact**
- Query: "Analyze Boone County" at Low vs High effort
- Expected Low: 1 tool call, 2-3 sentence answer
- Expected High: 3+ tool calls, detailed multi-paragraph analysis with cross-references
- FAIL if: Same depth regardless of effort setting

---

## OUTPUT FORMAT

For each test case, report in this exact format:

```json
{
  "test_id": "A1",
  "query": "What are the top 5 most vulnerable counties in Missouri?",
  "status": "PASS" | "FAIL" | "PARTIAL",
  "tools_called": ["query_counties"],
  "tools_expected": ["query_counties", "get_state_rankings"],
  "tool_match": true,
  "response_quality": {
    "has_specific_numbers": true,
    "has_county_names": true,
    "has_recommendations": true,
    "reasoning_leaked": false,
    "hallucinated_data": false
  },
  "visual_rendered": {
    "chart_type": "horizontal_bar",
    "data_table": true,
    "metric_cards": false
  },
  "response_time_seconds": 8.2,
  "answer_preview": "First 200 characters of the answer...",
  "issues": ["Any problems observed"],
  "severity": "none" | "minor" | "major" | "critical"
}
```

## AGGREGATE SUMMARY FORMAT

After all tests, produce:

```json
{
  "total_tests": 25,
  "passed": 20,
  "failed": 3,
  "partial": 2,
  "pass_rate": "80%",
  "categories": {
    "A_single_tool": {"passed": 7, "total": 8},
    "B_climate": {"passed": 5, "total": 6},
    "C_cross_domain": {"passed": 4, "total": 6},
    "D_edge_cases": {"passed": 4, "total": 5}
  },
  "critical_issues": [
    "Description of any critical failures"
  ],
  "recommended_fixes": [
    "Priority-ordered list of fixes needed"
  ],
  "avg_response_time_seconds": 9.4,
  "visual_render_rate": "76%"
}
```

## AGENT SWARM DEPLOYMENT — 100 AGENTS REQUIRED

This test protocol MUST deploy exactly **100 agents** across the test matrix. No fewer than 100 agents may be used. The swarm operates in 3 waves:

### Wave 1: Primary Testing (25 agents)
- **1 agent per test case** (25 tests × 1 agent = 25 agents)
- Each agent executes its assigned test case and produces the JSON output
- Agents A1-A8 handle Category A, B1-B6 handle Category B, C1-C6 handle Category C, D1-D5 handle Category D

### Wave 2: Consensus Validation (50 agents)
- **2 additional agents per test case** (25 tests × 2 agents = 50 agents)
- Each agent independently re-runs the same test case as Wave 1
- Purpose: catch flaky responses, validate consistency, detect non-deterministic failures
- If 2/3 agents disagree on PASS/FAIL, flag as **INCONSISTENT** for manual review

### Wave 3: Adversarial & Stress Testing (25 agents)
- **25 agents** running adversarial variations of the original test queries:
  - Agents 76-80: Rephrase Category A queries with different wording (e.g., "most at-risk" instead of "most vulnerable")
  - Agents 81-85: Run Category B queries with different FIPS codes (use Shannon 29203, Pemiscot 29155, Greene 29077)
  - Agents 86-90: Run Category C queries at **Low** effort and verify reduced tool usage
  - Agents 91-95: Run Category C queries at **High** effort and verify increased depth
  - Agents 96-100: Submit malformed, misspelled, and edge-case queries:
    - "top countees in mizouri" (typo tolerance)
    - "FIPS 29019 risk" (minimal query)
    - "" (empty query)
    - "What about climate change?" (vague, no location)
    - "Compare every county in the US" (scope overload)

### Deployment Rules
1. All 100 agents MUST be deployed — partial deployment is not acceptable
2. Each agent reports independently using the JSON output format below
3. Wave 2 agents must NOT see Wave 1 results before testing (independent validation)
4. Wave 3 agents must document both the original and modified query
5. A **Swarm Coordinator** (agent #0, not counted in 100) aggregates all results into the final summary

### Dashboard Access
- URL: `https://patchworky-unnoisy-maverick.ngrok-free.dev`
- NOTE: First visit shows an ngrok interstitial page — click "Visit Site" to proceed
- Ensure **Gemini 2.5 Pro (Cloud)** is selected in sidebar
- Set **Reasoning Effort** to **Medium** unless the test specifies otherwise
- For each test: paste the query, click Analyze, wait for response
- Record: tools called (visible in reasoning trace expander), response quality, visual output
- Screenshot any failures for debugging

### Completion Criteria
- All 100 agents have reported results
- Swarm Coordinator has produced the aggregate summary
- Any test with 2/3 or 3/3 FAIL across waves is flagged as **CRITICAL**
- Any test with inconsistent results (split vote) is flagged for manual review
