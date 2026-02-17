# /mnt/okcomputer/output/resilience_ai_analysis/code/cost_optimizer.py
"""
Cost Optimizer for ResilienceAI
Provides cost analysis and optimization for archival storage.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum


class StorageTier(Enum):
    """Storage tier enumeration for cost optimization."""
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    GLACIER = "glacier"
    DEEP_ARCHIVE = "deep_archive"


@dataclass
class CostModel:
    """Cost model for storage tier."""
    tier: StorageTier
    storage_cost_per_gb_month: float
    put_cost_per_1000: float
    get_cost_per_1000: float
    transition_cost_per_1000: float
    retrieval_cost_per_gb: float
    min_storage_days: int
    early_deletion_fee_per_gb: float


class CostOptimizer:
    """Cost optimization engine for ResilienceAI archival storage."""
    
    def __init__(self):
        self.cost_models = {
            StorageTier.HOT: CostModel(
                tier=StorageTier.HOT,
                storage_cost_per_gb_month=2.50,
                put_cost_per_1000=0.005,
                get_cost_per_1000=0.0004,
                transition_cost_per_1000=0.01,
                retrieval_cost_per_gb=0.0,
                min_storage_days=0,
                early_deletion_fee_per_gb=0.0
            ),
            StorageTier.WARM: CostModel(
                tier=StorageTier.WARM,
                storage_cost_per_gb_month=0.50,
                put_cost_per_1000=0.005,
                get_cost_per_1000=0.001,
                transition_cost_per_1000=0.01,
                retrieval_cost_per_gb=0.01,
                min_storage_days=30,
                early_deletion_fee_per_gb=0.50
            ),
            StorageTier.COLD: CostModel(
                tier=StorageTier.COLD,
                storage_cost_per_gb_month=0.023,
                put_cost_per_1000=0.005,
                get_cost_per_1000=0.001,
                transition_cost_per_1000=0.01,
                retrieval_cost_per_gb=0.01,
                min_storage_days=30,
                early_deletion_fee_per_gb=0.023
            ),
            StorageTier.GLACIER: CostModel(
                tier=StorageTier.GLACIER,
                storage_cost_per_gb_month=0.004,
                put_cost_per_1000=0.05,
                get_cost_per_1000=0.001,
                transition_cost_per_1000=0.05,
                retrieval_cost_per_gb=0.02,
                min_storage_days=90,
                early_deletion_fee_per_gb=0.12
            ),
            StorageTier.DEEP_ARCHIVE: CostModel(
                tier=StorageTier.DEEP_ARCHIVE,
                storage_cost_per_gb_month=0.00099,
                put_cost_per_1000=0.05,
                get_cost_per_1000=0.001,
                transition_cost_per_1000=0.05,
                retrieval_cost_per_gb=0.10,
                min_storage_days=180,
                early_deletion_fee_per_gb=0.18
            )
        }
    
    def calculate_storage_cost(self, storage_gb: float, tier: StorageTier,
                              months: int = 12) -> Dict:
        """Calculate storage cost for given tier."""
        model = self.cost_models[tier]
        
        storage_cost = storage_gb * model.storage_cost_per_gb_month * months
        
        return {
            "tier": tier.value,
            "storage_gb": storage_gb,
            "duration_months": months,
            "storage_cost": round(storage_cost, 2),
            "cost_per_gb_month": model.storage_cost_per_gb_month,
            "retrieval_cost_per_gb": model.retrieval_cost_per_gb,
            "min_storage_days": model.min_storage_days
        }
    
    def calculate_lifecycle_cost(self, data_profile: Dict) -> Dict:
        """Calculate cost for data through its lifecycle."""
        size_gb = data_profile["size_gb"]
        hot_months = data_profile.get("hot_months", 1)
        warm_months = data_profile.get("warm_months", 2)
        cold_months = data_profile.get("cold_months", 12)
        glacier_months = data_profile.get("glacier_months", 60)
        
        hot_cost = self.calculate_storage_cost(size_gb, StorageTier.HOT, hot_months)
        warm_cost = self.calculate_storage_cost(size_gb, StorageTier.WARM, warm_months)
        cold_cost = self.calculate_storage_cost(size_gb, StorageTier.COLD, cold_months)
        glacier_cost = self.calculate_storage_cost(size_gb, StorageTier.GLACIER, glacier_months)
        
        total_cost = (hot_cost["storage_cost"] + warm_cost["storage_cost"] + 
                     cold_cost["storage_cost"] + glacier_cost["storage_cost"])
        
        # Add transition costs
        transitions = 3  # Hot->Warm, Warm->Cold, Cold->Glacier
        transition_cost = transitions * self.cost_models[StorageTier.HOT].transition_cost_per_1000 / 1000
        
        return {
            "data_profile": data_profile,
            "cost_breakdown": {
                "hot": hot_cost,
                "warm": warm_cost,
                "cold": cold_cost,
                "glacier": glacier_cost
            },
            "total_storage_cost": round(total_cost, 2),
            "transition_cost": round(transition_cost, 2),
            "total_lifecycle_cost": round(total_cost + transition_cost, 2)
        }
    
    def optimize_tier_selection(self, data_profile: Dict) -> Dict:
        """Recommend optimal tier based on access patterns."""
        size_gb = data_profile["size_gb"]
        access_frequency = data_profile.get("access_frequency", "monthly")
        retention_years = data_profile.get("retention_years", 7)
        
        recommendations = []
        
        # Calculate costs for different strategies
        strategies = [
            {"name": "Always Hot", "tiers": [(StorageTier.HOT, retention_years * 12)]},
            {"name": "Immediate Archive", "tiers": [(StorageTier.GLACIER, retention_years * 12)]},
            {"name": "Lifecycle Optimized", "tiers": [
                (StorageTier.HOT, 1),
                (StorageTier.WARM, 2),
                (StorageTier.COLD, 12),
                (StorageTier.GLACIER, retention_years * 12 - 15)
            ]}
        ]
        
        for strategy in strategies:
            total_cost = 0
            for tier, months in strategy["tiers"]:
                cost = self.calculate_storage_cost(size_gb, tier, months)
                total_cost += cost["storage_cost"]
            
            recommendations.append({
                "strategy": strategy["name"],
                "estimated_cost": round(total_cost, 2),
                "tiers": [t[0].value for t in strategy["tiers"]]
            })
        
        # Sort by cost
        recommendations.sort(key=lambda x: x["estimated_cost"])
        
        return {
            "data_profile": data_profile,
            "recommendations": recommendations,
            "optimal_strategy": recommendations[0],
            "potential_savings": round(recommendations[-1]["estimated_cost"] - recommendations[0]["estimated_cost"], 2)
        }
    
    def calculate_compression_savings(self, data_profile: Dict) -> Dict:
        """Calculate savings from compression."""
        original_size_gb = data_profile["size_gb"]
        compression_ratio = data_profile.get("compression_ratio", 3.0)
        
        compressed_size_gb = original_size_gb / compression_ratio
        savings_gb = original_size_gb - compressed_size_gb
        
        # Calculate cost savings over lifecycle
        original_cost = self.calculate_lifecycle_cost(data_profile)
        compressed_profile = data_profile.copy()
        compressed_profile["size_gb"] = compressed_size_gb
        compressed_cost = self.calculate_lifecycle_cost(compressed_profile)
        
        cost_savings = original_cost["total_lifecycle_cost"] - compressed_cost["total_lifecycle_cost"]
        
        return {
            "original_size_gb": original_size_gb,
            "compressed_size_gb": round(compressed_size_gb, 2),
            "compression_ratio": compression_ratio,
            "space_savings_gb": round(savings_gb, 2),
            "space_savings_percent": round((savings_gb / original_size_gb) * 100, 1),
            "cost_savings": round(cost_savings, 2)
        }
    
    def generate_cost_report(self, storage_inventory: List[Dict]) -> Dict:
        """Generate comprehensive cost report."""
        total_size_gb = sum(item["size_gb"] for item in storage_inventory)
        total_objects = len(storage_inventory)
        
        # Calculate current costs
        current_costs = {}
        for tier in StorageTier:
            tier_objects = [i for i in storage_inventory if i.get("tier") == tier.value]
            tier_size = sum(i["size_gb"] for i in tier_objects)
            cost = self.calculate_storage_cost(tier_size, tier, 12)
            current_costs[tier.value] = cost
        
        total_annual_cost = sum(c["storage_cost"] for c in current_costs.values())
        
        # Optimization opportunities
        optimization_opportunities = []
        for item in storage_inventory:
            if item.get("tier") == StorageTier.HOT.value:
                if item.get("age_days", 0) > 30:
                    optimization_opportunities.append({
                        "object_id": item["object_id"],
                        "current_tier": item["tier"],
                        "recommended_tier": StorageTier.COLD.value,
                        "potential_savings": self.calculate_storage_cost(
                            item["size_gb"], 
                            StorageTier.HOT, 12
                        )["storage_cost"] - self.calculate_storage_cost(
                            item["size_gb"],
                            StorageTier.COLD, 12
                        )["storage_cost"]
                    })
        
        return {
            "report_date": datetime.now().isoformat(),
            "summary": {
                "total_objects": total_objects,
                "total_size_gb": round(total_size_gb, 2),
                "total_annual_cost": round(total_annual_cost, 2)
            },
            "current_costs": current_costs,
            "optimization_opportunities": optimization_opportunities[:100],  # Top 100
            "potential_annual_savings": round(sum(o["potential_savings"] for o in optimization_opportunities), 2)
        }


if __name__ == "__main__":
    # Example usage
    optimizer = CostOptimizer()
    
    # Calculate storage costs for different tiers
    print("Storage Costs for 1TB over 12 months:")
    print("=" * 50)
    
    for tier in StorageTier:
        cost = optimizer.calculate_storage_cost(1024, tier, 12)  # 1TB for 12 months
        print(f"\n{tier.value}:")
        print(f"  Cost: ${cost['storage_cost']}/year")
        print(f"  Per GB/month: ${cost['cost_per_gb_month']}")
    
    # Calculate lifecycle cost
    data_profile = {
        "size_gb": 100,  # 100GB
        "hot_months": 1,
        "warm_months": 2,
        "cold_months": 12,
        "glacier_months": 60
    }
    
    lifecycle_cost = optimizer.calculate_lifecycle_cost(data_profile)
    print(f"\n\nLifecycle cost for 100GB:")
    print(f"  Total: ${lifecycle_cost['total_lifecycle_cost']}")
    print(f"  Breakdown: {lifecycle_cost['cost_breakdown']}")
    
    # Optimization recommendation
    recommendation = optimizer.optimize_tier_selection({
        "size_gb": 100,
        "access_frequency": "monthly",
        "retention_years": 7
    })
    
    print(f"\n\nOptimization recommendation:")
    print(f"  Optimal strategy: {recommendation['optimal_strategy']['strategy']}")
    print(f"  Estimated cost: ${recommendation['optimal_strategy']['estimated_cost']}")
    print(f"  Potential savings: ${recommendation['potential_savings']}")
