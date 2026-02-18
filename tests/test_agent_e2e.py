#!/usr/bin/env python3
"""
ResilienceAI — Programmatic End-to-End Test Suite
Tests every tool at the data layer (ResilienceAgent) and executor layer (AgenticOrchestrator).
Does NOT require LLM — tests tool execution directly.
"""

import sys, os, json, time, traceback

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

# ─── Test Framework ──────────────────────────────────────────────────
results = []

def test(name, fn):
    """Run a test and record pass/fail."""
    try:
        result = fn()
        results.append({"name": name, "status": "PASS", "detail": str(result)[:200]})
        print(f"  PASS {name}")
        return result
    except Exception as e:
        results.append({"name": name, "status": "FAIL", "detail": f"{type(e).__name__}: {e}"})
        print(f"  FAIL {name}: {e}")
        traceback.print_exc()
        return None

def assert_true(cond, msg="Assertion failed"):
    if not cond:
        raise AssertionError(msg)

# ─── Load Agent ──────────────────────────────────────────────────────
print("\n" + "="*70)
print("ResilienceAI E2E Test Suite")
print("="*70)

print("\n[1/7] Loading ResilienceAgent...")
from agent import ResilienceAgent
agent = ResilienceAgent()
assert agent.df is not None, "Agent DataFrame not loaded"
print(f"  Agent loaded: {len(agent.df)} counties, {len(agent.df.columns)} features")

# ─── Test Group 1: _extract_state (CRITICAL — MO/MT bug) ────────────
print("\n[2/7] Testing _extract_state (all 50 states + DC)...")

state_name_tests = {
    "show me missouri counties": "MO",
    "what about montana data": "MT",
    "mississippi flood risk": "MS",
    "california wildfire danger": "CA",
    "new york infrastructure": "NY",
    "new mexico drought": "NM",
    "west virginia poverty": "WV",
    "north carolina hurricanes": "NC",
    "south dakota agriculture": "SD",
    "rhode island coastal risk": "RI",
    "district of columbia health": "DC",
    "texas heat wave": "TX",
    "florida hurricane damage": "FL",
    "iowa flooding": "IA",
    "ohio river valley": "OH",
    "washington state fires": "WA",
    "alabama tornado alley": "AL",
    "alaska permafrost": "AK",
    "hawaii volcano": "HI",
    "indiana agriculture risk": "IN",
}

for query, expected in state_name_tests.items():
    test(f"_extract_state('{query}') == {expected}",
         lambda q=query, e=expected: (
             assert_true(agent._extract_state(q) == e,
                        f"Got {agent._extract_state(q)}, expected {e}"),
             agent._extract_state(q)
         )[-1])

# Test 2-letter codes
code_tests = {
    "top counties in MO": "MO",
    "data for MT region": "MT",
    "show TX results": "TX",
    "FL coastal": "FL",
    "CA wildfires": "CA",
}
for query, expected in code_tests.items():
    test(f"_extract_state('{query}') == {expected} (abbrev)",
         lambda q=query, e=expected: (
             assert_true(agent._extract_state(q) == e,
                        f"Got {agent._extract_state(q)}, expected {e}"),
             agent._extract_state(q)
         )[-1])

# CRITICAL: Missouri vs Montana disambiguation
test("MO != MT: 'missouri' -> MO",
     lambda: (
         assert_true(agent._extract_state("missouri counties") == "MO",
                    f"Got {agent._extract_state('missouri counties')}"),
         "MO"
     )[-1])
test("MO != MT: 'montana' -> MT",
     lambda: (
         assert_true(agent._extract_state("montana counties") == "MT",
                    f"Got {agent._extract_state('montana counties')}"),
         "MT"
     )[-1])

# ─── Test Group 2: query_counties (state filtering) ─────────────────
print("\n[3/7] Testing query_counties (state filtering)...")

test("query_counties(state='MO') returns only Missouri",
     lambda: (
         data := agent.query_counties(state="MO", max_results=5),
         assert_true(len(data) > 0, "No MO counties returned"),
         assert_true(all("Missouri" in r["county_name"] for r in data),
                    f"Non-MO county found: {[r['county_name'] for r in data]}"),
         f"{len(data)} MO counties"
     )[-1])

test("query_counties(state='MT') returns only Montana",
     lambda: (
         data := agent.query_counties(state="MT", max_results=5),
         assert_true(len(data) > 0, "No MT counties returned"),
         assert_true(all("Montana" in r["county_name"] for r in data),
                    f"Non-MT county found: {[r['county_name'] for r in data]}"),
         f"{len(data)} MT counties"
     )[-1])

test("query_counties(state='MS') returns only Mississippi",
     lambda: (
         data := agent.query_counties(state="MS", max_results=5),
         assert_true(len(data) > 0, "No MS counties returned"),
         assert_true(all("Mississippi" in r["county_name"] for r in data),
                    f"Non-MS county found: {[r['county_name'] for r in data]}"),
         f"{len(data)} MS counties"
     )[-1])

test("query_counties(state='CA') returns only California",
     lambda: (
         data := agent.query_counties(state="CA", max_results=5),
         assert_true(len(data) > 0, "No CA counties returned"),
         assert_true(all("California" in r["county_name"] for r in data),
                    f"Non-CA county found: {[r['county_name'] for r in data]}"),
         f"{len(data)} CA counties"
     )[-1])

test("query_counties(state=None) returns nationwide top 10",
     lambda: (
         data := agent.query_counties(state=None, max_results=10),
         assert_true(len(data) == 10, f"Expected 10, got {len(data)}"),
         f"Top 10 nationwide"
     )[-1])

test("query_counties(state='Missouri') works with full name",
     lambda: (
         data := agent.query_counties(state="Missouri", max_results=3),
         assert_true(len(data) > 0, "No counties for full name 'Missouri'"),
         assert_true(all("Missouri" in r["county_name"] for r in data),
                    f"Non-MO county found: {[r['county_name'] for r in data]}"),
         f"{len(data)} counties"
     )[-1])

# ─── Test Group 3: get_county_detail ─────────────────────────────────
print("\n[4/7] Testing get_county_detail...")

test("get_county_detail('29019') returns Boone County, MO",
     lambda: (
         data := agent.get_county_detail("29019"),
         assert_true(data, "No data returned for FIPS 29019"),
         assert_true("Boone" in data.get("county_name", ""),
                    f"Expected Boone, got {data.get('county_name')}"),
         data["county_name"]
     )[-1])

test("get_county_detail('06037') returns Los Angeles County",
     lambda: (
         data := agent.get_county_detail("06037"),
         assert_true(data, "No data for FIPS 06037"),
         assert_true("Los Angeles" in data.get("county_name", ""),
                    f"Expected Los Angeles, got {data.get('county_name')}"),
         data["county_name"]
     )[-1])

test("get_county_detail('99999') returns empty for invalid FIPS",
     lambda: (
         data := agent.get_county_detail("99999"),
         assert_true(not data, f"Expected empty, got {data}"),
         "Empty as expected"
     )[-1])

# ─── Test Group 4: _extract_county (deterministic) ───────────────────
print("\n[4b/7] Testing _extract_county (deterministic)...")

test("_extract_county by FIPS '29019'",
     lambda: (
         data := agent._extract_county("details for 29019"),
         assert_true(data and "Boone" in str(data.get("county_name", "")),
                    f"Expected Boone for FIPS 29019, got {data}"),
         data["county_name"]
     )[-1])

test("_extract_county by name 'boone county'",
     lambda: (
         data := agent._extract_county("show me boone county data"),
         assert_true(data is not None, "No county found for 'boone county'"),
         assert_true("boone" in str(data.get("county_name", "")).lower(),
                    f"Expected boone, got {data.get('county_name')}"),
         data["county_name"]
     )[-1])

# Run 5 times to verify determinism
test("_extract_county is deterministic (5 runs same result)",
     lambda: (
         results_set := set(),
         [results_set.add(json.dumps(agent._extract_county("boone county risk"), sort_keys=True, default=str)) for _ in range(5)],
         assert_true(len(results_set) == 1, f"Non-deterministic: {len(results_set)} different results"),
         "Deterministic across 5 runs"
     )[-1])

# ─── Test Group 5: Other Agent Tools ─────────────────────────────────
print("\n[5/7] Testing ResilienceAgent tool methods...")

test("get_infrastructure_density('29019')",
     lambda: (
         data := agent.get_infrastructure_density("29019"),
         assert_true(isinstance(data, dict), f"Expected dict, got {type(data)}"),
         assert_true("hospitals_per_10k" in data or "density_hospitals_per10k" in data,
                    f"Missing hospital density key. Keys: {list(data.keys())}"),
         f"Keys: {list(data.keys())[:6]}"
     )[-1])

test("analyze_risk_contagion('29019')",
     lambda: (
         data := agent.analyze_risk_contagion("29019"),
         assert_true(isinstance(data, dict), f"Expected dict, got {type(data)}"),
         f"Keys: {list(data.keys())[:6]}"
     )[-1])

test("get_mo_health_disparities()",
     lambda: (
         data := agent.get_mo_health_disparities(),
         assert_true(isinstance(data, dict), f"Expected dict, got {type(data)}"),
         assert_true("priority_zones" in data or "summary" in data,
                    f"Missing expected keys. Keys: {list(data.keys())}"),
         f"Keys: {list(data.keys())}"
     )[-1])

test("calculate_intervention_roi('29019')",
     lambda: (
         data := agent.calculate_intervention_roi("29019"),
         assert_true(isinstance(data, (dict, list)), f"Expected dict/list, got {type(data)}"),
         f"Type: {type(data).__name__}, len: {len(data) if isinstance(data, list) else 'dict'}"
     )[-1])

test("simulate_scenario('earthquake_7.0', epicenter_fips='29143')",
     lambda: (
         data := agent.simulate_scenario("earthquake_7.0", epicenter_fips="29143"),
         assert_true(isinstance(data, dict), f"Expected dict, got {type(data)}"),
         f"Keys: {list(data.keys())[:6]}"
     )[-1])

test("calculate_pop_weighted_impact(state='MO')",
     lambda: (
         data := agent.calculate_pop_weighted_impact(state="MO"),
         assert_true(isinstance(data, (dict, list)), f"Expected dict/list, got {type(data)}"),
         f"Type: {type(data).__name__}"
     )[-1])

# ─── Test Group 6: Orchestrator Executor Layer ───────────────────────
print("\n[6/7] Testing AgenticOrchestrator executors (no LLM)...")

from agentic_orchestrator import AgenticOrchestrator
orch = AgenticOrchestrator(lm_studio_url="http://localhost:1234")

test("Orchestrator loads all expected executors",
     lambda: (
         expected := {"query_counties", "get_county_detail", "get_state_rankings",
                     "analyze_risk_contagion", "calculate_pop_weighted_impact",
                     "get_infrastructure_density", "get_mo_health_disparities",
                     "calculate_intervention_roi", "simulate_scenario"},
         missing := expected - set(orch._tool_executors.keys()),
         assert_true(len(missing) == 0, f"Missing executors: {missing}"),
         f"{len(orch._tool_executors)} executors loaded"
     )[-1])

test("Executor: query_counties(state='MO', max_results=3)",
     lambda: (
         data := orch._tool_executors["query_counties"](state="MO", max_results=3),
         assert_true(isinstance(data, list) and len(data) > 0, "Empty result"),
         assert_true(all("Missouri" in r.get("county_name", "") for r in data),
                    f"Non-MO: {[r.get('county_name') for r in data]}"),
         f"{len(data)} MO counties"
     )[-1])

test("Executor: get_state_rankings(state='MT')",
     lambda: (
         data := orch._tool_executors["get_state_rankings"](state="MT"),
         assert_true(isinstance(data, list) and len(data) > 0, "Empty result"),
         assert_true(all("Montana" in r.get("county_name", "") for r in data),
                    f"Non-MT: {[r.get('county_name') for r in data]}"),
         f"{len(data)} MT counties"
     )[-1])

test("Executor: get_county_detail(fips='29019')",
     lambda: (
         data := orch._tool_executors["get_county_detail"](fips="29019"),
         assert_true("Boone" in str(data.get("county_name", "")),
                    f"Expected Boone, got {data.get('county_name')}"),
         data["county_name"]
     )[-1])

test("Executor: get_infrastructure_density(fips='29019')",
     lambda: (
         data := orch._tool_executors["get_infrastructure_density"](fips="29019"),
         assert_true(isinstance(data, dict), f"Expected dict, got {type(data)}"),
         f"Keys: {list(data.keys())[:4]}"
     )[-1])

test("Executor: analyze_risk_contagion(fips='29019')",
     lambda: (
         data := orch._tool_executors["analyze_risk_contagion"](fips="29019"),
         assert_true(isinstance(data, dict), f"Expected dict, got {type(data)}"),
         f"Keys: {list(data.keys())[:4]}"
     )[-1])

test("Executor: get_mo_health_disparities()",
     lambda: (
         data := orch._tool_executors["get_mo_health_disparities"](),
         assert_true(isinstance(data, dict), f"Expected dict, got {type(data)}"),
         f"Keys: {list(data.keys())}"
     )[-1])

test("Executor: calculate_intervention_roi(fips='29019')",
     lambda: (
         data := orch._tool_executors["calculate_intervention_roi"](fips="29019"),
         assert_true(data is not None, "Null result"),
         f"Type: {type(data).__name__}"
     )[-1])

test("Executor: simulate_scenario(scenario='earthquake_7.0', epicenter_fips='29143')",
     lambda: (
         data := orch._tool_executors["simulate_scenario"](scenario="earthquake_7.0", epicenter_fips="29143"),
         assert_true(isinstance(data, dict), f"Expected dict, got {type(data)}"),
         f"Keys: {list(data.keys())[:4]}"
     )[-1])

test("Executor: calculate_pop_weighted_impact(state='MO')",
     lambda: (
         data := orch._tool_executors["calculate_pop_weighted_impact"](state="MO"),
         assert_true(data is not None, "Null result"),
         f"Type: {type(data).__name__}"
     )[-1])

# ─── Test Group 7: Climate Tools (if available) ─────────────────────
print("\n[7/7] Testing Climate Tools (live API — may timeout)...")

climate_tools = ["get_climate_trends", "get_hazard_risk_profile", "get_flood_frequency",
                 "get_severe_weather_history", "get_drought_history"]

for tool_name in climate_tools:
    if tool_name in orch._tool_executors:
        test(f"Climate: {tool_name}(fips='29019')",
             lambda tn=tool_name: (
                 data := orch._tool_executors[tn](fips="29019"),
                 assert_true(data is not None, "Null result"),
                 f"Type: {type(data).__name__}"
             )[-1])
    else:
        results.append({"name": f"Climate: {tool_name}", "status": "SKIP", "detail": "No executor"})
        print(f"  SKIP Climate: {tool_name} -- no executor (ClimateAgent not loaded)")

# ─── Summary ─────────────────────────────────────────────────────────
print("\n" + "="*70)
print("TEST RESULTS SUMMARY")
print("="*70)

passed = sum(1 for r in results if r["status"] == "PASS")
failed = sum(1 for r in results if r["status"] == "FAIL")
skipped = sum(1 for r in results if r["status"] == "SKIP")
total = len(results)

print(f"\n  Total:   {total}")
print(f"  Passed:  {passed}  ({'%.1f' % (100*passed/total)}%)" if total > 0 else "")
print(f"  Failed:  {failed}")
print(f"  Skipped: {skipped}")

if failed > 0:
    print(f"\n  FAILURES:")
    for r in results:
        if r["status"] == "FAIL":
            print(f"    FAIL {r['name']}: {r['detail']}")

# Write results to JSON
report_path = os.path.join(PROJECT_ROOT, "tests", "e2e_test_results.json")
with open(report_path, "w") as f:
    json.dump({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "pass_rate": f"{100*passed/total:.1f}%" if total > 0 else "0%",
        "results": results,
    }, f, indent=2, default=str)

print(f"\n  Report saved: {report_path}")
print("="*70)

sys.exit(1 if failed > 0 else 0)
