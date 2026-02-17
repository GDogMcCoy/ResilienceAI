"""
ResilienceAI Infrastructure Analysis - Pipeline Integration
End-to-end infrastructure analysis pipeline
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional, List
import json
from datetime import datetime

# Import our modules
from advanced_network import AdvancedInfrastructureNetwork
from gap_identifier import GapIdentifier
from investment_optimizer import InvestmentOptimizer
from infrastructure_agent import InfrastructureAnalysisAgent


class InfrastructurePipeline:
    """
    End-to-end infrastructure analysis pipeline
    Integrates with existing ResilienceAI pipeline
    """
    
    def __init__(self, data_dir: Path, output_dir: Path):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.network_analyzer = AdvancedInfrastructureNetwork(use_road_network=False)
        self.gap_identifier = GapIdentifier()
        self.investment_optimizer = InvestmentOptimizer()
        
        # Create agent
        self.agent = InfrastructureAnalysisAgent(
            self.network_analyzer,
            self.gap_identifier,
            self.investment_optimizer,
            status_tracker=None
        )
        
        self.results = {}
        
    def run_full_pipeline(self, county_df: pd.DataFrame,
                         state_filter: Optional[str] = None,
                         sample_counties: Optional[int] = None) -> Dict:
        """
        Run complete infrastructure analysis pipeline
        
        Steps:
        1. Load facility data
        2. Build networks for each county
        3. Identify coverage gaps
        4. Generate investment recommendations
        5. Compile results
        
        Args:
            county_df: DataFrame with county data
            state_filter: Optional state to filter by
            sample_counties: Optional number of counties to sample (for testing)
            
        Returns:
            Pipeline results summary
        """
        print("=" * 70)
        print("ResilienceAI Infrastructure Analysis Pipeline")
        print("=" * 70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Load facilities
        print("\n[1/6] Loading facility data...")
        self._load_facilities()
        
        # Step 2: Filter counties if needed
        if state_filter:
            county_df = county_df[county_df['state'] == state_filter]
            print(f"\n  Filtered to {state_filter}: {len(county_df)} counties")
        
        # Sample for testing if specified
        if sample_counties and len(county_df) > sample_counties:
            county_df = county_df.sample(n=sample_counties, random_state=42)
            print(f"\n  Sampled {sample_counties} counties for analysis")
        
        # Step 3: Analyze each county
        print(f"\n[2/6] Analyzing {len(county_df)} counties...")
        county_results = []
        for i, (_, county) in enumerate(county_df.iterrows(), 1):
            if i % 10 == 0 or i == len(county_df):
                print(f"  Progress: {i}/{len(county_df)} counties analyzed")
            
            result = self._analyze_county(county)
            if 'error' not in result:
                county_results.append(result)
        
        self.results['county_results'] = county_results
        
        # Step 4: Identify gaps
        print("\n[3/6] Identifying coverage gaps...")
        gaps = self.gap_identifier.identify_gaps(county_df, min_population=1000)
        self.results['coverage_gaps'] = gaps
        print(f"  Identified {len(gaps)} coverage gaps")
        
        # Step 5: Generate investment plan
        print("\n[4/6] Generating investment recommendations...")
        for gap in gaps:
            self.investment_optimizer.add_investment_option(gap)
        
        investment_plan = self.investment_optimizer.optimize_investments(objective='balanced')
        self.results['investment_plan'] = investment_plan
        
        if 'error' not in investment_plan:
            print(f"  Generated {investment_plan.get('investments_count', 0)} investment recommendations")
            print(f"  Total investment: ${investment_plan.get('total_investment', 0):.1f}M")
        
        # Step 6: Aggregate results
        print("\n[5/6] Aggregating results...")
        summary = self._generate_summary(county_results, gaps, investment_plan)
        self.results['summary'] = summary
        
        # Step 7: Save results
        print("\n[6/6] Saving results...")
        self._save_results()
        
        print("\n" + "=" * 70)
        print("Pipeline Complete!")
        print("=" * 70)
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return {
            'counties_analyzed': len(county_results),
            'gaps_identified': len(gaps),
            'investment_plan': investment_plan,
            'summary': summary
        }
    
    def _load_facilities(self) -> None:
        """Load all facility types from data directory"""
        facility_types = ['hospitals', 'fire_stations', 'ems_stations', 'nursing_homes']
        raw_dir = self.data_dir / 'raw'
        
        for ftype in facility_types:
            file_path = raw_dir / f'hifld_{ftype}.csv'
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    
                    # Ensure required columns exist
                    if 'latitude' not in df.columns and 'LATITUDE' in df.columns:
                        df['latitude'] = df['LATITUDE']
                    if 'longitude' not in df.columns and 'LONGITUDE' in df.columns:
                        df['longitude'] = df['LONGITUDE']
                    
                    # Load into network analyzer
                    self.network_analyzer.load_facilities(df, ftype)
                    
                    # Add to gap identifier
                    self.gap_identifier.add_facility_type(ftype, df)
                    
                    print(f"  Loaded {len(df)} {ftype}")
                except Exception as e:
                    print(f"  Warning: Could not load {ftype}: {e}")
            else:
                print(f"  Warning: {file_path} not found")
    
    def _analyze_county(self, county: pd.Series) -> Dict:
        """Analyze infrastructure for a single county"""
        try:
            return self.agent.analyze_county_infrastructure(
                str(county['fips']),
                pd.DataFrame([county])
            )
        except Exception as e:
            return {
                'county_fips': str(county.get('fips', 'unknown')),
                'error': str(e)
            }
    
    def _generate_summary(self, county_results: List[Dict], 
                         gaps: List, investment_plan: Dict) -> Dict:
        """Generate summary statistics"""
        # Filter out errors
        valid_results = [r for r in county_results if 'error' not in r]
        
        if not valid_results:
            return {'error': 'No valid results to summarize'}
        
        # Calculate vulnerability distribution
        vulnerability_scores = [r.get('vulnerability_score', 0) for r in valid_results]
        
        summary = {
            'total_counties': len(valid_results),
            'avg_vulnerability': round(sum(vulnerability_scores) / len(vulnerability_scores), 4),
            'avg_resilience': round(sum(r.get('resilience_score', 0) for r in valid_results) / len(valid_results), 4),
            'critical_counties': len([s for s in vulnerability_scores if s > 0.7]),
            'high_vulnerability': len([s for s in vulnerability_scores if 0.5 <= s <= 0.7]),
            'moderate_vulnerability': len([s for s in vulnerability_scores if 0.3 <= s < 0.5]),
            'resilient_counties': len([s for s in vulnerability_scores if s < 0.3]),
            'total_gaps': len(gaps),
            'total_population_affected': sum(g.population_affected for g in gaps) if gaps else 0
        }
        
        # Add investment summary
        if 'error' not in investment_plan:
            summary['total_investment_millions'] = investment_plan.get('total_investment', 0)
            summary['investments_count'] = investment_plan.get('investments_count', 0)
            summary['population_served'] = investment_plan.get('population_served', 0)
            
            roi = investment_plan.get('roi_metrics', {})
            summary['benefit_cost_ratio'] = roi.get('benefit_cost_ratio', 0)
            summary['people_served_per_million'] = roi.get('people_served_per_million', 0)
        
        return summary
    
    def _save_results(self) -> None:
        """Save all results to output directory"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save county analyses
        if 'county_results' in self.results:
            county_path = self.output_dir / f'county_infrastructure_{timestamp}.json'
            with open(county_path, 'w') as f:
                json.dump(self.results['county_results'], f, indent=2, default=str)
            print(f"  County results: {county_path}")
        
        # Save gaps
        if 'coverage_gaps' in self.results and self.results['coverage_gaps']:
            gaps_df = self.gap_identifier.generate_gap_report(self.results['coverage_gaps'])
            gaps_path = self.output_dir / f'coverage_gaps_{timestamp}.csv'
            gaps_df.to_csv(gaps_path, index=False)
            print(f"  Coverage gaps: {gaps_path}")
        
        # Save investment plan
        if 'investment_plan' in self.results:
            investment_path = self.output_dir / f'investment_plan_{timestamp}.json'
            with open(investment_path, 'w') as f:
                json.dump(self.results['investment_plan'], f, indent=2, default=str)
            print(f"  Investment plan: {investment_path}")
        
        # Save summary
        if 'summary' in self.results:
            summary_path = self.output_dir / f'summary_{timestamp}.json'
            with open(summary_path, 'w') as f:
                json.dump(self.results['summary'], f, indent=2, default=str)
            print(f"  Summary: {summary_path}")
        
        # Save comprehensive report
        report_path = self.output_dir / f'infrastructure_report_{timestamp}.json'
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"  Full report: {report_path}")
    
    def generate_briefing(self, state: str = None) -> str:
        """Generate infrastructure briefing"""
        if 'county_results' not in self.results:
            return "No results available. Run pipeline first."
        
        state_name = state or "Analyzed Region"
        
        return self.agent.generate_infrastructure_briefing(
            state_name,
            self.results['county_results']
        )
    
    def get_gap_summary(self) -> Dict:
        """Get summary of identified gaps"""
        if 'coverage_gaps' not in self.results:
            return {'error': 'No gap analysis available'}
        
        return self.gap_identifier.get_summary_statistics(self.results['coverage_gaps'])
    
    def compare_optimization_objectives(self) -> pd.DataFrame:
        """Compare different optimization objectives"""
        if not self.investment_optimizer.investment_options:
            return pd.DataFrame({'error': ['No investment options available']})
        
        return self.investment_optimizer.compare_objectives()
    
    def run_sensitivity_analysis(self, budget_range: tuple = (50, 200, 25)) -> pd.DataFrame:
        """Run sensitivity analysis on budget"""
        if not self.investment_optimizer.investment_options:
            return pd.DataFrame({'error': ['No investment options available']})
        
        return self.investment_optimizer.sensitivity_analysis(budget_range)


def run_pipeline_example():
    """Example usage of the infrastructure pipeline"""
    # Setup paths
    data_dir = Path('/mnt/okcomputer/data')
    output_dir = Path('/mnt/okcomputer/output/infrastructure_analysis')
    
    # Create pipeline
    pipeline = InfrastructurePipeline(data_dir, output_dir)
    
    # Example county data (would normally come from ResilienceAI)
    example_counties = pd.DataFrame({
        'fips': ['29001', '29003', '29005'],
        'county_name': ['Adair', 'Andrew', 'Atchison'],
        'state': ['MO', 'MO', 'MO'],
        'latitude': [40.1903, 39.9847, 40.4328],
        'longitude': [-92.6008, -94.8019, -95.4293],
        'population': [25300, 17200, 5300]
    })
    
    # Run pipeline
    results = pipeline.run_full_pipeline(
        example_counties,
        state_filter='MO'
    )
    
    # Generate briefing
    briefing = pipeline.generate_briefing('Missouri')
    print("\n" + briefing)
    
    return results


if __name__ == '__main__':
    run_pipeline_example()
