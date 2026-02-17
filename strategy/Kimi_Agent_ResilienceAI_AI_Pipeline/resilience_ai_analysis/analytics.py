"""
Digital Twin Analytics and Insights Engine
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from collections import defaultdict
import statistics


@dataclass
class Insight:
    """Analytics insight"""
    insight_id: str
    category: str
    severity: str
    title: str
    description: str
    affected_assets: List[str]
    recommended_actions: List[str]
    confidence: float
    generated_at: datetime


class AnalyticsEngine:
    """Generate insights from digital twin data"""
    
    def __init__(self, county_twin: Any):
        self.county_twin = county_twin
        self.insights: List[Insight] = []
        self.metrics_history: List[Dict] = []
    
    def generate_health_insights(self) -> List[Insight]:
        """Generate infrastructure health insights"""
        insights = []
        
        poor_condition_assets = [
            (aid, a) for aid, a in self.county_twin.assets.items()
            if a.get("condition_index", 1.0) < 0.4
        ]
        
        if poor_condition_assets:
            insights.append(Insight(
                insight_id=f"health_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                category="infrastructure_health",
                severity="critical",
                title=f"{len(poor_condition_assets)} Assets in Critical Condition",
                description=f"Found {len(poor_condition_assets)} assets with condition index below 0.4",
                affected_assets=[aid for aid, _ in poor_condition_assets],
                recommended_actions=[
                    "Schedule immediate inspections",
                    "Prioritize maintenance funding",
                    "Consider temporary restrictions on use"
                ],
                confidence=0.95,
                generated_at=datetime.now()
            ))
        
        aging_assets = [
            (aid, a) for aid, a in self.county_twin.assets.items()
            if a.get("age_years", 0) > 50 and a.get("condition_index", 1.0) < 0.6
        ]
        
        if aging_assets:
            insights.append(Insight(
                insight_id=f"aging_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                category="asset_lifecycle",
                severity="warning",
                title=f"{len(aging_assets)} Aging Assets Need Attention",
                description="Assets over 50 years old with declining condition",
                affected_assets=[aid for aid, _ in aging_assets],
                recommended_actions=[
                    "Develop replacement schedule",
                    "Increase inspection frequency",
                    "Budget for replacements"
                ],
                confidence=0.85,
                generated_at=datetime.now()
            ))
        
        return insights
    
    def generate_risk_insights(self) -> List[Insight]:
        """Generate risk-related insights"""
        insights = []
        risk_clusters = self._identify_risk_clusters()
        
        for cluster in risk_clusters:
            insights.append(Insight(
                insight_id=f"risk_{cluster['id']}",
                category="risk_concentration",
                severity="warning" if cluster['risk_score'] > 0.6 else "info",
                title=f"Risk Cluster: {cluster['name']}",
                description=f"Area with {len(cluster['assets'])} high-risk assets",
                affected_assets=cluster['assets'],
                recommended_actions=[
                    "Conduct area-wide risk assessment",
                    "Develop mitigation strategies",
                    "Consider infrastructure hardening"
                ],
                confidence=cluster['confidence'],
                generated_at=datetime.now()
            ))
        
        return insights
    
    def generate_network_insights(self) -> List[Insight]:
        """Generate network connectivity insights"""
        insights = []
        
        for network_type, network in self.county_twin.networks.items():
            connectivity = network.calculate_connectivity()
            
            if connectivity < 0.5:
                insights.append(Insight(
                    insight_id=f"net_{network_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    category="network_connectivity",
                    severity="critical" if connectivity < 0.3 else "warning",
                    title=f"Low {network_type.title()} Network Connectivity",
                    description=f"Connectivity score: {connectivity:.2f}. Network may be vulnerable to single points of failure.",
                    affected_assets=[n['id'] for n in network.nodes],
                    recommended_actions=[
                        "Identify critical nodes",
                        "Plan redundancy improvements",
                        "Develop backup routes"
                    ],
                    confidence=0.9,
                    generated_at=datetime.now()
                ))
        
        return insights
    
    def generate_cost_insights(self) -> List[Insight]:
        """Generate cost optimization insights"""
        insights = []
        maintenance_costs = defaultdict(float)
        
        for asset in self.county_twin.assets.values():
            asset_type = asset.get("asset_type", "unknown")
            maintenance_costs[asset_type] += asset.get("replacement_cost", 1000000) * 0.02
        
        avg_cost = statistics.mean(maintenance_costs.values()) if maintenance_costs else 0
        
        for asset_type, cost in maintenance_costs.items():
            if cost > avg_cost * 2:
                insights.append(Insight(
                    insight_id=f"cost_{asset_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    category="cost_optimization",
                    severity="info",
                    title=f"High Maintenance Cost: {asset_type.title()}",
                    description=f"Annual maintenance cost ${cost:,.0f} is {cost/avg_cost:.1f}x average",
                    affected_assets=[],
                    recommended_actions=[
                        "Review maintenance strategies",
                        "Consider asset replacement",
                        "Evaluate preventive maintenance ROI"
                    ],
                    confidence=0.75,
                    generated_at=datetime.now()
                ))
        
        return insights
    
    def _identify_risk_clusters(self) -> List[Dict]:
        """Identify clusters of high-risk assets"""
        clusters = []
        grid_size = 0.01
        grid_cells = defaultdict(list)
        
        for asset_id, asset in self.county_twin.assets.items():
            lat = asset.get("latitude", 0)
            lon = asset.get("longitude", 0)
            grid_x = int(lon / grid_size)
            grid_y = int(lat / grid_size)
            
            risk_score = (
                asset.get("flood_risk", 0) * 0.3 +
                asset.get("seismic_risk", 0) * 0.3 +
                (1 - asset.get("condition_index", 1)) * 0.4
            )
            
            grid_cells[(grid_x, grid_y)].append({
                "asset_id": asset_id,
                "risk_score": risk_score
            })
        
        for (gx, gy), assets in grid_cells.items():
            avg_risk = np.mean([a["risk_score"] for a in assets])
            if avg_risk > 0.5 and len(assets) > 2:
                clusters.append({
                    "id": f"{gx}_{gy}",
                    "name": f"Grid ({gx}, {gy})",
                    "assets": [a["asset_id"] for a in assets],
                    "risk_score": avg_risk,
                    "confidence": min(0.95, 0.5 + len(assets) * 0.05)
                })
        
        return sorted(clusters, key=lambda x: x["risk_score"], reverse=True)
    
    def get_insights_summary(self) -> Dict:
        """Get summary of all insights"""
        all_insights = (
            self.generate_health_insights() +
            self.generate_risk_insights() +
            self.generate_network_insights() +
            self.generate_cost_insights()
        )
        
        by_severity = defaultdict(int)
        by_category = defaultdict(int)
        
        for insight in all_insights:
            by_severity[insight.severity] += 1
            by_category[insight.category] += 1
        
        return {
            "total_insights": len(all_insights),
            "by_severity": dict(by_severity),
            "by_category": dict(by_category),
            "critical_insights": [i for i in all_insights if i.severity == "critical"],
            "latest_insights": sorted(all_insights, key=lambda x: x.generated_at, reverse=True)[:10]
        }
