"""
ResilienceAI - Intent Recognizer
Classifies user queries into predefined intents using hybrid approach.

File: src/nl_interface/intent_recognizer.py
"""

import re
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Try to import transformers
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class Intent(Enum):
    """Supported user intents."""
    QUERY_VULNERABILITY = "query_vulnerability"
    COMPARE_COUNTIES = "compare_counties"
    FIND_HOTSPOTS = "find_hotspots"
    GET_FORECAST = "get_forecast"
    SIMULATE_SCENARIO = "simulate_scenario"
    GENERATE_BRIEFING = "generate_briefing"
    SET_ALERT = "set_alert"
    EXPLAIN_DATA = "explain_data"
    NAVIGATE = "navigate"
    CLARIFY = "clarify"
    GREETING = "greeting"
    GOODBYE = "goodbye"
    UNKNOWN = "unknown"


@dataclass
class IntentClassification:
    """Result of intent classification."""
    intent: Intent
    confidence: float
    alternatives: List[Tuple[Intent, float]]


class IntentRecognizer:
    """
    Intent recognition using hybrid approach:
    1. Rule-based patterns for common queries
    2. BERT-based classifier for complex queries
    3. Context-aware disambiguation
    """
    
    # Intent patterns for rule-based classification
    PATTERNS = {
        Intent.QUERY_VULNERABILITY: [
            r"show me.*risk.*(in|for|at)",
            r"what.*risk.*(in|for|at)",
            r"how vulnerable is",
            r"tell me about.*county",
            r"risk (score|level|index).*",
            r"vulnerability.*(in|for)",
            r"disaster.*history.*",
            r"flood risk.*",
            r"tornado.*risk.*",
            r"hospital.*access.*",
            r"infrastructure.*gap.*",
        ],
        Intent.COMPARE_COUNTIES: [
            r"compare.*(to|with|and)",
            r"(difference|differences).*between",
            r"which.*(higher|lower|worse|better)",
            r"(vs|versus)",
            r"how does.*compare",
            r"side.by.side",
            r"rank.*counties",
        ],
        Intent.FIND_HOTSPOTS: [
            r"find.*(high risk|hotspot|vulnerable)",
            r"show.*(top|highest|worst)",
            r"where.*(highest|most|worst).*risk",
            r"compound risk.*",
            r"critical.*counties",
            r"priority.*areas",
            r"which.*(need|require).*attention",
        ],
        Intent.GET_FORECAST: [
            r"forecast.*",
            r"predict.*",
            r"what will.*(be|happen)",
            r"future.*risk.*",
            r"projection.*",
            r"trajectory.*",
            r"next (year|5 years|decade)",
            r"by (2025|2030|2050)",
        ],
        Intent.SIMULATE_SCENARIO: [
            r"simulate.*",
            r"what if.*",
            r"scenario.*",
            r"(hurricane|earthquake|flood|tornado|wildfire).*hit",
            r"impact of.*",
            r"model.*disaster",
        ],
        Intent.GENERATE_BRIEFING: [
            r"(generate|create|make).*briefing",
            r"executive.*report",
            r"summary.*for",
            r"overview.*of",
            r"report.*on",
            r"export.*(pdf|pptx|document)",
        ],
        Intent.SET_ALERT: [
            r"(set|create|configure).*alert",
            r"notify me.*",
            r"watch.*for",
            r"monitor.*",
            r"alert.*when",
            r"subscribe.*",
        ],
        Intent.EXPLAIN_DATA: [
            r"(what|how).*mean",
            r"explain.*",
            r"what is.*index",
            r"how.*calculated",
            r"why.*(high|low|risk)",
            r"definition.*of",
        ],
        Intent.NAVIGATE: [
            r"(show|go to|open|switch to).*tab",
            r"(show|display).*map",
            r"(show|display).*chart",
            r"navigate.*to",
        ],
        Intent.GREETING: [
            r"^(hi|hello|hey|greetings)",
            r"^good (morning|afternoon|evening)",
        ],
        Intent.GOODBYE: [
            r"(bye|goodbye|see you|thanks|thank you).*",
            r"^done$",
            r"^exit$",
        ],
    }
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize intent recognizer."""
        self.model = None
        self.tokenizer = None
        
        if TRANSFORMERS_AVAILABLE and model_path:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
                self.model.eval()
            except Exception as e:
                print(f"Could not load BERT model: {e}. Using rule-based only.")
    
    def recognize(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
        history: Optional[List[Any]] = None
    ) -> str:
        """
        Classify user text into an intent.
        
        Returns:
            Intent string value
        """
        text_lower = text.lower().strip()
        
        # Step 1: Rule-based pattern matching
        pattern_scores = {}
        for intent, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    pattern_scores[intent] = pattern_scores.get(intent, 0) + 1
        
        # Step 2: BERT classification if available
        if self.model and self.tokenizer:
            bert_intent, bert_confidence = self._bert_classify(text)
            if bert_confidence > 0.7:
                return bert_intent.value
        
        # Step 3: Select best intent from patterns
        if pattern_scores:
            best_intent = max(pattern_scores, key=pattern_scores.get)
            best_intent = self._disambiguate_with_context(best_intent, text, context, history)
            return best_intent.value
        
        # Default to query_vulnerability for data-related queries
        if any(word in text_lower for word in ["county", "risk", "vulnerable", "disaster"]):
            return Intent.QUERY_VULNERABILITY.value
        
        return Intent.UNKNOWN.value
    
    def _bert_classify(self, text: str) -> Tuple[Intent, float]:
        """Classify using BERT model."""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=1)
            confidence, predicted_class = torch.max(probabilities, dim=1)
        
        intent_map = {i: intent for i, intent in enumerate(Intent)}
        return intent_map.get(predicted_class.item(), Intent.UNKNOWN), confidence.item()
    
    def _disambiguate_with_context(
        self,
        intent: Intent,
        text: str,
        context: Optional[Dict[str, Any]],
        history: Optional[List[Any]]
    ) -> Intent:
        """Use conversation context to disambiguate intent."""
        if not context or not history:
            return intent
        
        text_lower = text.lower()
        
        # Check for anaphoric references
        anaphoric_words = ["those", "them", "these", "they", "it", "that", "this"]
        has_anaphora = any(word in text_lower for word in anaphoric_words)
        
        if has_anaphora:
            if "compare" in text_lower or "versus" in text_lower:
                return Intent.COMPARE_COUNTIES
            elif "forecast" in text_lower or "predict" in text_lower:
                return Intent.GET_FORECAST
        
        return intent
    
    def get_intent_description(self, intent_value: str) -> str:
        """Get human-readable description of an intent."""
        try:
            intent = Intent(intent_value)
        except ValueError:
            return "Unknown intent"
            
        descriptions = {
            Intent.QUERY_VULNERABILITY: "Query vulnerability data for counties",
            Intent.COMPARE_COUNTIES: "Compare multiple counties",
            Intent.FIND_HOTSPOTS: "Find high-risk areas and hotspots",
            Intent.GET_FORECAST: "Get risk forecasts and predictions",
            Intent.SIMULATE_SCENARIO: "Simulate disaster scenarios",
            Intent.GENERATE_BRIEFING: "Generate executive briefings",
            Intent.SET_ALERT: "Configure monitoring alerts",
            Intent.EXPLAIN_DATA: "Explain data and metrics",
            Intent.NAVIGATE: "Navigate the dashboard",
            Intent.CLARIFY: "Request clarification",
            Intent.GREETING: "Greeting",
            Intent.GOODBYE: "Farewell",
            Intent.UNKNOWN: "Unknown intent",
        }
        return descriptions.get(intent, "Unknown")
