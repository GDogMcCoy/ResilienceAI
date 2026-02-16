# Agent Swarm Enhancement: FHIR Export, GeoJSON Export, and Spatial Analysis

## Summary

This PR adds 4 new MCP tools and 3 new modules to ResilienceAI, expanding the agent's capabilities for health system integration, GIS workflows, and spatial statistics.

## New MCP Tools (23 total, up from 19)

| Tool | Purpose | Use Case |
|------|---------|----------|
| `export_fhir` | Export vulnerability data as FHIR R4 Bundle | Health system EHR integration |
| `export_geojson` | Export as GeoJSON for GIS workflows | Mapping and spatial analysis |
| `analyze_spatial_autocorrelation` | Calculate Moran's I statistic | Detect spatial clustering patterns |
| `find_spatial_hotspots` | Getis-Ord Gi* hotspot analysis | Identify vulnerability hotspots/coldspots |

## New Modules

### `src/fhir_export.py`
- FHIR R4 compliant export format
- Generates Location, RiskAssessment, and Observation resources
- Supports county, state, and high-risk filtering
- CLI interface for batch exports

### `src/geojson_export.py`
- GeoJSON RFC 7946 compliant output
- Point geometries for all 3,222 counties
- Configurable property inclusion (minimal vs full)
- Filters: state, risk level, high-risk threshold, compound risk

### `src/spatial_stats.py`
- Moran's I for spatial autocorrelation detection
- Getis-Ord Gi* for hotspot/coldspot identification
- Configurable neighborhood radius
- Statistical significance testing (z-scores, p-values)

## Documentation Updates

- `docs/SETUP_GUIDE.md` - Comprehensive setup and development guide
- `docs/DATA_DICTIONARY.md` - Complete documentation of all 66 features

## Integration

All new tools are fully integrated into `ResilienceAgent` class:

```python
agent = ResilienceAgent()

# FHIR export
agent.export_fhir(fips="29019")  # Single county
agent.export_fhir(state="MO")    # Entire state
agent.export_fhir(high_risk_only=True, risk_threshold=0.7)

# GeoJSON export
agent.export_geojson(state="MO")
agent.export_geojson(compound_risk_min=3)

# Spatial analysis
agent.analyze_spatial_autocorrelation("risk_score")
agent.find_spatial_hotspots("vulnerability_index")
```

## Standards Compliance

- **FHIR R4** - HL7 FHIR Release 4 compliant
- **GeoJSON** - RFC 7946 compliant
- **OGC** - Open Geospatial Consortium standards for spatial analysis

## Testing

All modules include CLI interfaces for standalone testing:

```bash
# FHIR export
python src/fhir_export.py --county 29019
python src/fhir_export.py --state MO --high-risk

# GeoJSON export
python src/geojson_export.py --all
python src/geojson_export.py --compound-risk 3

# Spatial analysis
python src/spatial_stats.py --moran risk_score
python src/spatial_stats.py --hotspots risk_score
```

## Performance Notes

| Module | Memory | Speed | Notes |
|--------|--------|-------|-------|
| fhir_export.py | Medium | Fast | Loads dataset once |
| geojson_export.py | Low | Fast | Streaming possible |
| spatial_stats.py | High | Medium | O(n²) for Moran's I |

## Dependencies

No new dependencies required - uses existing:
- `scipy` (spatial distance calculations)
- `pandas` (data manipulation)
- `numpy` (numerical operations)

## Backward Compatibility

✅ All existing 19 MCP tools unchanged
✅ All existing functionality preserved
✅ New tools are additive only

## Related Issues

Addresses gaps identified in self-improvement analysis:
- Missing FHIR export capability
- Missing GIS integration
- Missing spatial statistics

## Checklist

- [x] New modules follow existing code style
- [x] Type hints for all public functions
- [x] Docstrings with Args/Returns
- [x] Error handling with meaningful messages
- [x] CLI interfaces for standalone use
- [x] Integration with ResilienceAgent
- [x] MCP tool definitions added
- [x] Documentation updated

---

**Branch:** `KIMI-2.5-Agent-Swarm`  
**Files Changed:** 7 (4 new modules, 1 updated agent.py, 2 new docs)  
**Lines Added:** ~2,500
