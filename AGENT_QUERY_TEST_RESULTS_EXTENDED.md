# ResilienceAI Agent Query - Extended Test Results

**Test Date:** 2026-02-17 01:46:13

## Summary

- **Total Tests:** 47
- **Passed:** 47
- **Failed:** 0
- **Info:** 0

## Detailed Results

| Test | Status | Severity | Details |
|------|--------|----------|---------|
| Empty Query Detection | ✅ PASS | Info | Empty query properly detected |
| Special Query: What's the risk for O'Brien Co... | ✅ PASS | Info | Handled without crash |
| Special Query: Counties with risk > 0.5... | ✅ PASS | Info | Handled without crash |
| Special Query: Test "quoted" county... | ✅ PASS | Info | Handled without crash |
| Special Query: County; DROP TABLE... | ✅ PASS | Info | Handled without crash |
| Special Query: County
with
newlines... | ✅ PASS | Info | Handled without crash |
| Case Test: lowercase state | ✅ PASS | Info | Found 0 results |
| Case Test: uppercase state | ✅ PASS | Info | Found 0 results |
| Case Test: mixed case state | ✅ PASS | Info | Found 0 results |
| Case Test: abbreviation | ✅ PASS | Info | Found 5 results |
| Case Test: uppercase abbreviation | ✅ PASS | Info | Found 5 results |
| Large Result Request | ✅ PASS | Info | Returned 500 results gracefully |
| Invalid Param: {'max_results': -1} | ✅ PASS | Info | Handled gracefully |
| Invalid Param: {'max_results': 0} | ✅ PASS | Info | Handled gracefully |
| Invalid Param: {'min_risk_score': -0.5} | ✅ PASS | Info | Handled gracefully |
| Invalid Param: {'min_risk_score': 1.5} | ✅ PASS | Info | Handled gracefully |
| FIPS Test: '01001' | ✅ PASS | Info | Handled correctly |
| FIPS Test: '1' | ✅ PASS | Info | Handled correctly |
| FIPS Test: '0100101' | ✅ PASS | Info | Handled correctly |
| FIPS Test: 'invalid' | ✅ PASS | Info | Handled correctly |
| FIPS Test: '' | ✅ PASS | Info | Handled correctly |
| FIPS Test: '00000' | ✅ PASS | Info | Handled correctly |
| Tool Format: query_counties | ✅ PASS | Info | Returns list |
| Tool Format: get_county_detail | ✅ PASS | Info | Returns dict |
| Tool Format: find_compound_risk_counties | ✅ PASS | Info | Returns list |
| Tool Format: find_zero_redundancy | ✅ PASS | Info | Returns list |
| Tool Format: get_disaster_trends | ✅ PASS | Info | Returns list |
| Tool Format: get_state_rankings | ✅ PASS | Info | Returns list |
| Pattern Match: 'missouri flooding' | ✅ PASS | Info | Pattern matched |
| Pattern Match: 'mo vulnerable' | ✅ PASS | Info | Pattern matched |
| Pattern Match: 'accelerating' | ✅ PASS | Info | Pattern matched |
| Pattern Match: 'fastest' | ✅ PASS | Info | Pattern matched |
| Pattern Match: 'zero redundancy' | ✅ PASS | Info | Pattern matched |
| Pattern Match: 'hospital redundancy' | ✅ PASS | Info | Pattern matched |
| Pattern Match: 'compound risk' | ✅ PASS | Info | Pattern matched |
| Pattern Match: 'hotspot' | ✅ PASS | Info | Pattern matched |
| Session Var: agent_config | ✅ PASS | Info | Referenced in dashboard |
| Session Var: agent_history | ✅ PASS | Info | Referenced in dashboard |
| Session Var: last_response | ✅ PASS | Info | Referenced in dashboard |
| Session Var: local_agent | ✅ PASS | Info | Referenced in dashboard |
| Response Structure | ✅ PASS | Info | All required keys present |
| JSON Serialization | ✅ PASS | Info | Response is JSON serializable |
| Fallback Message | ✅ PASS | Info | Fallback message present |
| Fallback UI | ✅ PASS | Info | Fallback UI notification present |
| JSON Export | ✅ PASS | Info | Export option present |
| Markdown Export | ✅ PASS | Info | Export option present |
| Clipboard Copy | ✅ PASS | Info | Export option present |

## Failures

No failures recorded.

## Potential Bugs Identified

### High Priority
No high priority issues.

### Medium Priority
No medium priority issues.
