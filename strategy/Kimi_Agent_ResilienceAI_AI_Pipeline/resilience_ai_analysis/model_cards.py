"""
ResilienceAI Model Cards
=========================
Model card generation and management.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class ModelCard:
    """Comprehensive model card structure."""
    model_name: str
    model_version: str
    model_type: str
    model_description: str
    intended_use_cases: List[str]
    out_of_scope_uses: List[str]
    factors: Dict[str, List[str]]
    performance_metrics: Dict[str, float]
    fairness_metrics: Dict[str, Dict[str, float]]
    training_data: Dict[str, Any]
    evaluation_data: Dict[str, Any]
    ethical_considerations: List[str]
    caveats: List[str]
    recommendations: List[str]
    model_owner: str
    contact_info: str
    last_updated: str
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    def to_markdown(self) -> str:
        md = f"""# Model Card: {self.model_name}

## Model Details
- **Name**: {self.model_name}
- **Version**: {self.model_version}
- **Type**: {self.model_type}
- **Description**: {self.model_description}
- **Owner**: {self.model_owner}
- **Last Updated**: {self.last_updated}
- **Contact**: {self.contact_info}

## Intended Use
### Use Cases
"""
        for use_case in self.intended_use_cases:
            md += f"- {use_case}\n"
        
        md += "\n### Out of Scope Uses\n"
        for out_of_scope in self.out_of_scope_uses:
            md += f"- {out_of_scope}\n"
        
        md += "\n## Performance Metrics\n"
        for metric, value in self.performance_metrics.items():
            md += f"- **{metric}**: {value:.4f}\n"
        
        md += "\n## Fairness Metrics\n"
        for metric, group_values in self.fairness_metrics.items():
            md += f"- **{metric}**: {group_values}\n"
        
        return md


class ModelCardGenerator:
    """Generator for model cards."""
    
    def __init__(self, model_name: str, model_version: str):
        self.model_name = model_name
        self.model_version = model_version
    
    def generate_card(self, model_type: str, model_description: str,
                      intended_uses: List[str], out_of_scope: List[str],
                      factors: Dict[str, List[str]],
                      performance_metrics: Dict[str, float],
                      fairness_metrics: Dict[str, Dict[str, float]],
                      training_data_info: Dict[str, Any],
                      evaluation_data_info: Dict[str, Any],
                      ethical_considerations: List[str],
                      caveats: List[str], recommendations: List[str],
                      model_owner: str, contact_info: str) -> ModelCard:
        return ModelCard(
            model_name=self.model_name, model_version=self.model_version,
            model_type=model_type, model_description=model_description,
            intended_use_cases=intended_uses, out_of_scope_uses=out_of_scope,
            factors=factors, performance_metrics=performance_metrics,
            fairness_metrics=fairness_metrics, training_data=training_data_info,
            evaluation_data=evaluation_data_info,
            ethical_considerations=ethical_considerations,
            caveats=caveats, recommendations=recommendations,
            model_owner=model_owner, contact_info=contact_info,
            last_updated=datetime.now().isoformat()
        )


class ModelCardRegistry:
    """Registry for managing model cards."""
    
    def __init__(self):
        self.cards: Dict[str, ModelCard] = {}
    
    def register(self, model_id: str, card: ModelCard):
        self.cards[model_id] = card
    
    def get(self, model_id: str) -> Optional[ModelCard]:
        return self.cards.get(model_id)
    
    def list_models(self) -> List[str]:
        return list(self.cards.keys())


if __name__ == "__main__":
    generator = ModelCardGenerator("ResilienceAI-Risk-Model", "v1.0.0")
    
    card = generator.generate_card(
        model_type="Gradient Boosting Classifier",
        model_description="Predicts disaster risk levels",
        intended_uses=["Emergency response", "Risk assessment"],
        out_of_scope=["Individual predictions", "Medical triage"],
        factors={"Geographic": ["Region", "Urban/Rural"]},
        performance_metrics={"accuracy": 0.87, "f1": 0.86},
        fairness_metrics={"demographic_parity": {"urban": 0.52, "rural": 0.48}},
        training_data_info={"size": 500000, "source": "Historical records"},
        evaluation_data_info={"size": 50000, "source": "Test set"},
        ethical_considerations=["May have reduced accuracy for rare events"],
        caveats=["Performance degrades outside training distribution"],
        recommendations=["Validate with domain experts"],
        model_owner="ResilienceAI Team",
        contact_info="ai-ethics@resilienceai.org"
    )
    
    print(card.to_markdown())
