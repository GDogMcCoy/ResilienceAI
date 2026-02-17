"""
ResilienceAI Infrastructure Analysis - Infrastructure Agent
Agent for comprehensive infrastructure analysis and reporting
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import json
from datetime import datetime


class InfrastructureAnalysisAgent:
    """
    Agent for comprehensive infrastructure analysis
    Integrates with ResilienceAI agent orchestration
    """
    
    def __init__(self, network_analyzer=None, gap_identifier=None, 
                 investment_optimizer=None, status_tracker=None):
        self.network_analyzer = network_analyzer
        self.gap_identifier = gap_identifier
        self.investment_optimizer = investment_optimizer
        self.status_tracker = status_tracker
        
    def analyze_county_infrastructure(self, county_fips: str,
                                      county_data: pd.DataFrame) -> Dict:
        """
        Comprehensive infrastructure analysis for a county
        
        Args:
            county_fips: County FIPS code
            county_data: DataFrame with county information
            
        Returns:
            Complete infrastructure analysis results
        """
        # Get county info
        county = county_data[county_data['fips'] == county_fips]
        if county.empty:
            return {'error': f'County {county_fips} not found'}
        
        county_row = county.iloc[0]
        
        results = {
            'county_fips': county_fips,
            'county_name': county_row.get('county_name', 'Unknown'),
            'state': county_row.get('state', ''),
            'population': county_row.get('population', 0),
            'timestamp': datetime.now().isoformat()
        }
        
        # Network analysis
        if self.network_analyzer:
            try:
                network_result = self._analyze_network(county_row)
                results['network_analysis'] = network_result
            except Exception as e:
                results['network_analysis'] = {'error': str(e)}
        
        # Gap analysis
        if self.gap_identifier:
            try:
                gaps = self._analyze_gaps(county)
                results['coverage_gaps'] = gaps
            except Exception as e:
                results['coverage_gaps'] = {'error': str(e)}
        
        # Investment recommendations
        if self.investment_optimizer and 'coverage_gaps' in results:
            try:
                investments = self._generate_investments(results['coverage_gaps'])
                results['investment_recommendations'] = investments
            except Exception as e:
                results['investment_recommendations'] = {'error': str(e)}
        
        # Calculate overall scores
        results['vulnerability_score'] = self._calculate_vulnerability(results)
        results['resilience_score'] = 1 - results['vulnerability_score']
        
        return results
    
    def _analyze_network(self, county_row: pd.Series) -> Dict:
        """Analyze network for a county"""
        if not hasattr(self.network_analyzer, 'build_network'):
            return {}
        
        # Build network around county center
        G = self.network_analyzer.build_network(
            county_row['latitude'],
            county_row['longitude'],
            radius_km=50
        )
        
        # Calculate metrics
        metrics = self.network_analyzer.calculate_advanced_metrics()
        
        return {
            'total_facilities': metrics.get('total_facilities', 0),
            'network_density': round(metrics.get('network_density', 0), 4),
            'connected_components': metrics.get('connected_components', 0),
            'articulation_points': len(metrics.get('articulation_points', [])),
            'vulnerability_score': round(metrics.get('vulnerability_score', 1.0), 4),
            'resilience_score': round(metrics.get('resilience_score', 0.0), 4),
            'critical_facilities_count': len(metrics.get('critical_facilities', [])),
            'service_coverage': metrics.get('service_coverage', {})
        }
    
    def _analyze_gaps(self, county_df: pd.DataFrame) -> List[Dict]:
        """Analyze coverage gaps for a county"""
        if not hasattr(self.gap_identifier, 'identify_gaps'):
            return []
        
        gaps = self.gap_identifier.identify_gaps(county_df, min_population=0)
        
        # Convert to serializable format
        return [
            {
                'type': gap.gap_type,
                'severity': gap.severity.value,
                'distance_km': gap.nearest_facility_distance_km,
                'population_affected': gap.population_affected,
                'benchmark_km': gap.benchmark_distance_km,
                'facilities_needed': gap.recommended_facilities,
                'priority_score': gap.priority_score
            }
            for gap in gaps[:5]  # Top 5 gaps
        ]
    
    def _generate_investments(self, gaps: List[Dict]) -> List[Dict]:
        """Generate investment recommendations from gaps"""
        if not hasattr(self.investment_optimizer, 'add_investment_option'):
            return []
        
        # Clear previous options
        self.investment_optimizer.investment_options = []
        
        # Add gaps as investment options
        for gap in gaps:
            # Create a mock gap object
            class MockGap:
                pass
            mock_gap = MockGap()
            for key, value in gap.items():
                setattr(mock_gap, key, value)
            mock_gap.location_lat = 0  # Will be filled from county data
            mock_gap.location_lon = 0
            mock_gap.county_fips = ''
            mock_gap.gap_type = gap['type']
            mock_gap.recommended_facilities = gap.get('facilities_needed', 1)
            mock_gap.priority_score = gap.get('priority_score', 1.0)
            mock_gap.nearest_facility_distance_km = gap.get('distance_km', 50)
            mock_gap.benchmark_distance_km = gap.get('benchmark_km', 25)
            mock_gap.population_affected = gap.get('population_affected', 0)
            
            self.investment_optimizer.add_investment_option(mock_gap)
        
        # Optimize
        plan = self.investment_optimizer.optimize_investments(objective='balanced')
        
        return plan.get('recommended_investments', [])
    
    def _calculate_vulnerability(self, results: Dict) -> float:
        """Calculate overall vulnerability score from analysis results"""
        scores = []
        
        # Network vulnerability
        if 'network_analysis' in results and 'vulnerability_score' in results['network_analysis']:
            scores.append(results['network_analysis']['vulnerability_score'] * 0.5)
        
        # Gap severity
        if 'coverage_gaps' in results and results['coverage_gaps']:
            gap_count = len(results['coverage_gaps'])
            critical_gaps = sum(1 for g in results['coverage_gaps'] if g.get('severity') == 'critical')
            gap_score = min((gap_count * 0.1) + (critical_gaps * 0.2), 0.5)
            scores.append(gap_score)
        
        return sum(scores) if scores else 0.5
    
    def analyze_state_infrastructure(self, state: str,
                                     county_data: pd.DataFrame) -> Dict:
        """
        Analyze infrastructure for all counties in a state
        
        Args:
            state: State abbreviation (e.g., 'MO')
            county_data: DataFrame with all county data
            
        Returns:
            State-wide infrastructure analysis
        """
        # Filter to state
        state_counties = county_data[county_data['state'] == state]
        
        if state_counties.empty:
            return {'error': f'No counties found for state {state}'}
        
        # Analyze each county
        county_results = []
        for _, county in state_counties.iterrows():
            result = self.analyze_county_infrastructure(
                str(county['fips']),
                state_counties
            )
            if 'error' not in result:
                county_results.append(result)
        
        # Aggregate results
        return self._aggregate_state_results(state, county_results)
    
    def _aggregate_state_results(self, state: str, 
                                 county_results: List[Dict]) -> Dict:
        """Aggregate county results to state level"""
        if not county_results:
            return {'error': 'No valid county results'}
        
        # Calculate averages
        avg_vulnerability = sum(r.get('vulnerability_score', 0) for r in county_results) / len(county_results)
        avg_resilience = sum(r.get('resilience_score', 0) for r in county_results) / len(county_results)
        
        # Count gaps
        total_gaps = sum(len(r.get('coverage_gaps', [])) for r in county_results)
        critical_counties = [r for r in county_results if r.get('vulnerability_score', 0) > 0.7]
        
        # Aggregate facilities
        total_facilities = sum(
            r.get('network_analysis', {}).get('total_facilities', 0) 
            for r in county_results
        )
        
        return {
            'state': state,
            'counties_analyzed': len(county_results),
            'total_facilities': total_facilities,
            'avg_vulnerability_score': round(avg_vulnerability, 4),
            'avg_resilience_score': round(avg_resilience, 4),
            'total_coverage_gaps': total_gaps,
            'critical_counties': len(critical_counties),
            'county_results': county_results
        }
    
    def generate_infrastructure_briefing(self, state: str,
                                         analysis_results: List[Dict]) -> str:
        """
        Generate natural language briefing on infrastructure status
        
        Args:
            state: State name
            analysis_results: List of county analysis results
            
        Returns:
            Markdown-formatted briefing
        """
        # Aggregate metrics
        total_counties = len(analysis_results)
        avg_vulnerability = sum(r.get('vulnerability_score', 0) for r in analysis_results) / max(total_counties, 1)
        total_gaps = sum(len(r.get('coverage_gaps', [])) for r in analysis_results)
        
        # Critical counties
        critical_counties = [r for r in analysis_results if r.get('vulnerability_score', 0) > 0.7]
        high_vulnerability = [r for r in analysis_results if 0.5 <= r.get('vulnerability_score', 0) <= 0.7]
        
        briefing = f"""# Infrastructure Analysis Briefing: {state}

## Executive Summary
- **Counties Analyzed**: {total_counties}
- **Average Vulnerability Score**: {avg_vulnerability:.2f} (0=resilient, 1=vulnerable)
- **Total Coverage Gaps Identified**: {total_gaps}
- **Critical Counties**: {len(critical_counties)}
- **High Vulnerability Counties**: {len(high_vulnerability)}

## Vulnerability Assessment

### County Resilience Distribution
| Category | Count | Description |
|----------|-------|-------------|
| **Critical** (score > 0.7) | {len(critical_counties)} | Immediate intervention needed |
| **High** (0.5-0.7) | {len(high_vulnerability)} | Priority for improvement |
| **Moderate** (0.3-0.5) | {len([r for r in analysis_results if 0.3 <= r.get('vulnerability_score', 0) < 0.5])} | Monitor and plan |
| **Resilient** (< 0.3) | {len([r for r in analysis_results if r.get('vulnerability_score', 0) < 0.3])} | Maintain current state |

## Coverage Gap Analysis
"""
        
        # Add gap details
        all_gaps = []
        for result in analysis_results:
            county_name = result.get('county_name', 'Unknown')
            for gap in result.get('coverage_gaps', []):
                all_gaps.append({
                    'county': county_name,
                    'type': gap.get('type', 'unknown'),
                    'severity': gap.get('severity', 'low'),
                    'population': gap.get('population_affected', 0)
                })
        
        # Sort by severity and population
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_gaps.sort(key=lambda x: (severity_order.get(x['severity'], 4), -x['population']))
        
        # Gap summary by type
        gap_by_type = {}
        for gap in all_gaps:
            gap_type = gap['type']
            if gap_type not in gap_by_type:
                gap_by_type[gap_type] = {'count': 0, 'population': 0}
            gap_by_type[gap_type]['count'] += 1
            gap_by_type[gap_type]['population'] += gap['population']
        
        briefing += "\n### Gaps by Facility Type\n"
        briefing += "| Facility Type | Count | Population Affected |\n"
        briefing += "|--------------|-------|---------------------|\n"
        for gap_type, stats in sorted(gap_by_type.items(), key=lambda x: -x[1]['population']):
            briefing += f"| {gap_type.replace('_', ' ').title()} | {stats['count']} | {stats['population']:,} |\n"
        
        # Top priority gaps
        briefing += "\n### Top Priority Gaps\n"
        for i, gap in enumerate(all_gaps[:10], 1):
            briefing += f"{i}. **{gap['county']}**: {gap['type'].replace('_', ' ').title()} gap "
            briefing += f"affecting {gap['population']:,} people ({gap['severity'].upper()})\n"
        
        # Investment recommendations
        briefing += "\n## Investment Recommendations\n"
        
        # Collect all investment options
        all_investments = []
        for result in analysis_results:
            all_investments.extend(result.get('investment_recommendations', []))
        
        if all_investments:
            # Sort by cost efficiency
            all_investments.sort(key=lambda x: x.get('population_served', 0) / (x.get('cost_millions', 1) + 0.01), reverse=True)
            
            total_cost = sum(inv.get('cost_millions', 0) for inv in all_investments[:10])
            total_population = sum(inv.get('population_served', 0) for inv in all_investments[:10])
            
            briefing += f"""
### Summary
- **Estimated Investment Needed**: ${total_cost:.1f}M for top 10 priorities
- **People Served**: {total_population:,}
- **Average Cost per Person**: ${total_cost * 1_000_000 / total_population:.0f}

### Top 5 Investment Opportunities
"""
            for i, inv in enumerate(all_investments[:5], 1):
                briefing += f"{i}. **{inv['facility_type'].replace('_', ' ').title()}** in {inv['county_fips']}: "
                briefing += f"${inv['cost_millions']:.1f}M (serves {inv['population_served']:,}, "
                briefing += f"coverage +{inv['coverage_improvement']:.1%})\n"
        else:
            briefing += "\nNo specific investment recommendations generated.\n"
        
        # Critical counties section
        if critical_counties:
            briefing += "\n## Critical Counties Requiring Immediate Attention\n"
            for county in critical_counties[:5]:
                briefing += f"- **{county.get('county_name', 'Unknown')}** (FIPS: {county['county_fips']}): "
                briefing += f"Vulnerability score {county.get('vulnerability_score', 0):.2f}\n"
        
        briefing += f"""
## Recommendations

Based on the infrastructure analysis for {state}:

1. **Immediate Actions**: Address {len(critical_counties)} critical counties with vulnerability scores > 0.7
2. **Gap Remediation**: Prioritize closing {total_gaps} identified coverage gaps
3. **Investment Strategy**: Consider the top investment opportunities identified above
4. **Monitoring**: Implement real-time facility status tracking for early warning

---
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return briefing
    
    def export_results(self, results: Dict, output_path: str, 
                      format: str = 'json') -> None:
        """Export analysis results to file"""
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        elif format == 'csv':
            # Flatten results for CSV
            if 'county_results' in results:
                df = pd.json_normalize(results['county_results'])
                df.to_csv(output_path, index=False)
            else:
                pd.DataFrame([results]).to_csv(output_path, index=False)
