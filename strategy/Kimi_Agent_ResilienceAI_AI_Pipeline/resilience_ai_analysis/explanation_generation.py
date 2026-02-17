"""
Recommendation Explanation Generation for ResilienceAI
Generates human-readable explanations for recommendations
"""

from typing import List, Dict, Any, Optional
import numpy as np


class ExplanationGenerator:
    """Generates explanations for recommendations"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.explanation_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """Load explanation templates"""
        
        return {
            'similar_counties': [
                "{county_name} shares {similarity_percentage:.0%} similarity with your county based on {dimensions}",
                "These counties have similar {primary_characteristics} profiles",
                "Peer counties with comparable {key_metrics}"
            ],
            'interventions': [
                "This intervention has a predicted effectiveness of {effectiveness:.0%} for your county",
                "Similar counties achieved {avg_outcome:.0%} success with this intervention",
                "Addresses your priority risk: {primary_risk}"
            ],
            'collaborative_filtering': [
                "Counties similar to yours rated this {rating:.1f}/5.0",
                "Based on outcomes from {n_similar} comparable counties",
                "{success_rate:.0%} of similar counties reported positive outcomes"
            ],
            'content_based': [
                "Matches your county's {matching_features}",
                "Aligned with your {demographic_match} characteristics",
                "Suitable for counties with {risk_profile} risk profile"
            ],
            'hybrid': [
                "This recommendation combines insights from multiple approaches",
                "Weighted combination of collaborative and content-based signals",
                "Optimized for your county's unique profile"
            ],
            'resource_allocation': [
                "Allocated to maximize impact while ensuring equity",
                "Based on cost-effectiveness analysis for your region",
                "Prioritizes counties with highest risk-adjusted need"
            ]
        }
    
    def generate_explanation(
        self,
        recommendation_type: str,
        item: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Generate explanation for a recommendation"""
        
        templates = self.explanation_templates.get(recommendation_type, [])
        
        if not templates:
            return "Recommended based on analysis of your county profile"
        
        # Select template based on available data
        template = templates[0]
        
        # Fill in template
        try:
            explanation = template.format(**{**item, **context})
        except KeyError:
            explanation = template
        
        return explanation
    
    def generate_counterfactual_explanation(
        self,
        recommended_item: Dict[str, Any],
        alternative_item: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Generate counterfactual explanation"""
        
        score_diff = recommended_item.get('score', 0) - alternative_item.get('score', 0)
        
        explanation = (
            f"This intervention was chosen over {alternative_item.get('name', 'alternatives')} "
            f"because it has a {score_diff:.0%} higher predicted effectiveness "
            f"for counties with your profile."
        )
        
        return explanation
    
    def generate_feature_importance_explanation(
        self,
        item: Dict[str, Any],
        feature_importance: Dict[str, float]
    ) -> str:
        """Generate explanation based on feature importance"""
        
        # Sort features by importance
        sorted_features = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        top_features = [f.replace('_', ' ') for f, _ in sorted_features]
        
        explanation = (
            f"Key factors in this recommendation: {', '.join(top_features)}"
        )
        
        return explanation
    
    def generate_peer_comparison_explanation(
        self,
        county_id: str,
        similar_counties: List[Dict[str, Any]],
        intervention_id: str
    ) -> str:
        """Generate explanation comparing to peer counties"""
        
        if not similar_counties:
            return "No comparable counties available for comparison"
        
        # Calculate average outcome from similar counties
        avg_outcome = np.mean([c.get('outcome_score', 0) for c in similar_counties])
        success_count = sum(1 for c in similar_counties if c.get('success', False))
        success_rate = success_count / len(similar_counties)
        
        explanation = (
            f"{len(similar_counties)} similar counties implemented this intervention "
            f"with an average outcome score of {avg_outcome:.2f} "
            f"and a {success_rate:.0%} success rate."
        )
        
        return explanation
    
    def generate_risk_based_explanation(
        self,
        county_risks: Dict[str, float],
        intervention_target_risks: List[str]
    ) -> str:
        """Generate explanation based on risk alignment"""
        
        # Find matching risks
        matching_risks = []
        for risk in intervention_target_risks:
            risk_key = f"risk_{risk}"
            if risk_key in county_risks and county_risks[risk_key] > 0.3:
                matching_risks.append((risk, county_risks[risk_key]))
        
        if not matching_risks:
            return "This intervention provides general resilience benefits"
        
        # Sort by risk level
        matching_risks.sort(key=lambda x: x[1], reverse=True)
        
        top_risks = [r[0] for r in matching_risks[:2]]
        
        explanation = (
            f"This intervention directly addresses your county's "
            f"primary risks: {', '.join(top_risks)}"
        )
        
        return explanation
    
    def generate_cost_benefit_explanation(
        self,
        cost: float,
        expected_benefit: float,
        similar_costs: List[float]
    ) -> str:
        """Generate cost-benefit explanation"""
        
        roi = (expected_benefit - cost) / cost if cost > 0 else 0
        
        if similar_costs:
            avg_similar_cost = np.mean(similar_costs)
            cost_comparison = "below" if cost < avg_similar_cost else "above"
            
            explanation = (
                f"Expected ROI: {roi:.0%}. "
                f"Cost is {cost_comparison} average ({avg_similar_cost:,.0f}) "
                f"for similar interventions."
            )
        else:
            explanation = f"Expected ROI: {roi:.0%} based on projected benefits"
        
        return explanation
    
    def generate_full_explanation(
        self,
        recommendation_type: str,
        item: Dict[str, Any],
        context: Dict[str, Any],
        feature_importance: Optional[Dict[str, float]] = None,
        similar_counties: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, str]:
        """Generate comprehensive explanation with multiple components"""
        
        explanations = {
            'primary': self.generate_explanation(recommendation_type, item, context),
            'detail': '',
            'peer_comparison': '',
            'confidence': ''
        }
        
        # Add feature importance explanation if available
        if feature_importance:
            explanations['detail'] = self.generate_feature_importance_explanation(
                item, feature_importance
            )
        
        # Add peer comparison if available
        if similar_counties:
            explanations['peer_comparison'] = self.generate_peer_comparison_explanation(
                context.get('county_id', ''),
                similar_counties,
                item.get('intervention_id', '')
            )
        
        # Add confidence explanation
        score = item.get('score', 0) or item.get('similarity_score', 0)
        if score > 0.8:
            explanations['confidence'] = "High confidence recommendation"
        elif score > 0.6:
            explanations['confidence'] = "Moderate confidence recommendation"
        else:
            explanations['confidence'] = "Exploratory recommendation"
        
        return explanations


class ExplanationPresenter:
    """Presents explanations in user-friendly formats"""
    
    def __init__(self, style: str = 'detailed'):
        self.style = style
    
    def present(
        self,
        explanations: Dict[str, str],
        format: str = 'text'
    ) -> str:
        """Present explanations in specified format"""
        
        if format == 'text':
            return self._present_text(explanations)
        elif format == 'html':
            return self._present_html(explanations)
        elif format == 'json':
            return self._present_json(explanations)
        else:
            return self._present_text(explanations)
    
    def _present_text(self, explanations: Dict[str, str]) -> str:
        """Present as plain text"""
        
        parts = [explanations['primary']]
        
        if explanations.get('detail'):
            parts.append(f"Details: {explanations['detail']}")
        
        if explanations.get('peer_comparison'):
            parts.append(f"Peer insight: {explanations['peer_comparison']}")
        
        if explanations.get('confidence'):
            parts.append(f"Note: {explanations['confidence']}")
        
        return '\n'.join(parts)
    
    def _present_html(self, explanations: Dict[str, str]) -> str:
        """Present as HTML"""
        
        html = f"""
        <div class="recommendation-explanation">
            <p class="primary-explanation">{explanations['primary']}</p>
        """
        
        if explanations.get('detail'):
            html += f"<p class="detail-explanation">{explanations['detail']}</p>"
        
        if explanations.get('peer_comparison'):
            html += f"<p class="peer-comparison">{explanations['peer_comparison']}</p>"
        
        if explanations.get('confidence'):
            html += f"<p class="confidence-note">{explanations['confidence']}</p>"
        
        html += "</div>"
        
        return html
    
    def _present_json(self, explanations: Dict[str, str]) -> str:
        """Present as JSON"""
        import json
        return json.dumps(explanations, indent=2)


# Example usage
if __name__ == "__main__":
    # Create explanation generator
    generator = ExplanationGenerator()
    
    # Generate explanation for similar counties
    item = {
        'county_name': 'Riverside County',
        'similarity_score': 0.85,
        'similarity_percentage': 0.85
    }
    context = {
        'dimensions': 'demographics, economy, and risk factors',
        'primary_characteristics': 'population size and economic profile',
        'key_metrics': 'resilience indicators'
    }
    
    explanation = generator.generate_explanation('similar_counties', item, context)
    print(f"Similar County Explanation: {explanation}")
    
    # Generate explanation for intervention
    intervention_item = {
        'name': 'Flood Early Warning System',
        'effectiveness': 0.82,
        'primary_risk': 'flood'
    }
    intervention_context = {
        'avg_outcome': 0.75
    }
    
    intervention_explanation = generator.generate_explanation(
        'interventions', intervention_item, intervention_context
    )
    print(f"\nIntervention Explanation: {intervention_explanation}")
    
    # Generate full explanation
    feature_importance = {
        'risk_flood': 0.35,
        'population': 0.25,
        'median_income': 0.20,
        'historical_success': 0.20
    }
    
    similar_counties = [
        {'county_id': 'c1', 'outcome_score': 0.8, 'success': True},
        {'county_id': 'c2', 'outcome_score': 0.75, 'success': True},
        {'county_id': 'c3', 'outcome_score': 0.7, 'success': False}
    ]
    
    full_explanation = generator.generate_full_explanation(
        'interventions',
        intervention_item,
        intervention_context,
        feature_importance,
        similar_counties
    )
    
    print(f"\nFull Explanation:")
    for key, value in full_explanation.items():
        print(f"  {key}: {value}")
    
    # Present explanation
    presenter = ExplanationPresenter()
    presented = presenter.present(full_explanation, format='text')
    print(f"\nPresented Explanation:\n{presented}")
