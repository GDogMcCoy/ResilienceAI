"""
ResilienceAI - Self-Recursive Improvement Engine
Agent evaluates its own responses, identifies gaps, and proposes improvements.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import datetime
from pathlib import Path
from config import DATA_DIR


IMPROVEMENT_LOG_PATH = DATA_DIR / "improvement_log.json"


def _load_log():
    """Load improvement log from disk."""
    if IMPROVEMENT_LOG_PATH.exists():
        with open(IMPROVEMENT_LOG_PATH, "r") as f:
            return json.load(f)
    return {"entries": [], "proposed_features": [], "proposed_tools": [],
            "proposed_data_sources": []}


def _save_log(log):
    """Save improvement log to disk."""
    IMPROVEMENT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(IMPROVEMENT_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2, default=str)


class ResponseEvaluator:
    """Evaluate agent response quality and identify gaps."""

    TOOL_NAMES = [
        "query_counties", "get_county_detail", "compare_counties",
        "get_statistics", "predict_risk", "find_compound_risk_counties",
        "get_gap_analysis", "get_disaster_trends", "find_zero_redundancy",
        "get_state_rankings", "prioritize_by_impact",
        "simulate_scenario", "analyze_cascade_risk",
        "calculate_intervention_roi", "generate_executive_brief",
        "get_equity_analysis", "benchmark_county", "get_real_time_alerts",
    ]

    def evaluate(self, query, response_summary, tools_used, data_available=True):
        """
        Evaluate a response and return confidence + identified gaps.

        Args:
            query: Original user query
            response_summary: Summary of what was returned
            tools_used: List of tool names that were invoked
            data_available: Whether data was available to answer

        Returns:
            dict with confidence score and gap analysis
        """
        confidence = 1.0
        gaps = []
        suggestions = []

        query_lower = query.lower()

        # Check data availability
        if not data_available:
            confidence -= 0.5
            gaps.append("Core data not loaded")
            suggestions.append("Ensure pipeline has been run to generate county_features.csv")

        # Check if query mentions capabilities we don't have
        missing_capabilities = {
            "real-time": "Real-time data integration (NOAA, NWS alerts)",
            "live": "Live data feed integration",
            "predict future": "Time-series forecasting model",
            "forecast": "Predictive forecasting capability",
            "social media": "Social media sentiment analysis",
            "satellite": "Satellite imagery analysis",
            "census tract": "Sub-county (census tract) level data",
            "zip code": "ZIP code level analysis",
            "climate change": "Climate projection integration (CMIP6)",
            "insurance": "Insurance/NFIP claims data",
            "economic impact": "Economic impact modeling (HAZUS)",
        }

        for keyword, capability in missing_capabilities.items():
            if keyword in query_lower:
                confidence -= 0.15
                gaps.append(f"Missing capability: {capability}")

        # Check tool coverage
        tools_not_used = set(self.TOOL_NAMES) - set(tools_used)
        potentially_useful = []

        tool_query_hints = {
            "simulate_scenario": ["what if", "scenario", "hurricane", "earthquake", "simulate"],
            "analyze_cascade_risk": ["cascade", "network", "failure", "infrastructure network"],
            "calculate_intervention_roi": ["roi", "cost", "investment", "intervention", "budget"],
            "get_equity_analysis": ["equity", "disparit", "fairness", "demographic gap"],
            "benchmark_county": ["benchmark", "compare to similar", "peer", "how does.*rank"],
            "get_real_time_alerts": ["alert", "threshold", "monitor", "warning"],
        }

        for tool, hints in tool_query_hints.items():
            if tool in tools_not_used:
                if any(h in query_lower for h in hints):
                    confidence -= 0.1
                    potentially_useful.append(tool)

        # Check response completeness
        if not response_summary or len(response_summary) < 20:
            confidence -= 0.3
            gaps.append("Response appears incomplete")

        confidence = max(0.0, min(1.0, confidence))

        return {
            "confidence": round(confidence, 3),
            "gaps": gaps,
            "potentially_useful_tools": potentially_useful,
            "suggestions": suggestions,
            "quality_tier": (
                "high" if confidence >= 0.8 else
                "medium" if confidence >= 0.5 else
                "low"
            ),
        }


class ImprovementLogger:
    """Track improvement suggestions across sessions."""

    def log_evaluation(self, query, response_summary, confidence, gaps,
                       tools_used, suggestions=None):
        """Log an evaluation result for pattern analysis."""
        log = _load_log()
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "query": query,
            "response_summary": response_summary[:200],
            "confidence": confidence,
            "gaps": gaps,
            "tools_used": tools_used,
            "suggestions": suggestions or [],
        }
        log["entries"].append(entry)

        # Keep last 100 entries
        if len(log["entries"]) > 100:
            log["entries"] = log["entries"][-100:]

        _save_log(log)
        return entry

    def propose_feature(self, name, description, rationale, priority="medium"):
        """Propose a new feature based on identified gaps."""
        log = _load_log()
        proposal = {
            "timestamp": datetime.datetime.now().isoformat(),
            "name": name,
            "description": description,
            "rationale": rationale,
            "priority": priority,
            "status": "proposed",
        }
        log["proposed_features"].append(proposal)
        _save_log(log)
        return proposal

    def propose_tool(self, name, description, parameters, rationale):
        """Propose a new MCP tool."""
        log = _load_log()
        proposal = {
            "timestamp": datetime.datetime.now().isoformat(),
            "name": name,
            "description": description,
            "parameters": parameters,
            "rationale": rationale,
            "status": "proposed",
        }
        log["proposed_tools"].append(proposal)
        _save_log(log)
        return proposal

    def propose_data_source(self, name, url, description, rationale):
        """Propose a new data source to integrate."""
        log = _load_log()
        proposal = {
            "timestamp": datetime.datetime.now().isoformat(),
            "name": name,
            "url": url,
            "description": description,
            "rationale": rationale,
            "status": "proposed",
        }
        log["proposed_data_sources"].append(proposal)
        _save_log(log)
        return proposal

    def get_improvement_summary(self):
        """Analyze improvement log for patterns."""
        log = _load_log()
        entries = log["entries"]

        if not entries:
            return {"total_evaluations": 0, "message": "No evaluations logged yet"}

        confidences = [e["confidence"] for e in entries]
        all_gaps = []
        for e in entries:
            all_gaps.extend(e["gaps"])

        # Count gap frequency
        gap_freq = {}
        for g in all_gaps:
            gap_freq[g] = gap_freq.get(g, 0) + 1

        top_gaps = sorted(gap_freq.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "total_evaluations": len(entries),
            "avg_confidence": round(sum(confidences) / len(confidences), 3),
            "min_confidence": round(min(confidences), 3),
            "low_confidence_count": sum(1 for c in confidences if c < 0.5),
            "top_recurring_gaps": [{"gap": g, "count": c} for g, c in top_gaps],
            "proposed_features": len(log["proposed_features"]),
            "proposed_tools": len(log["proposed_tools"]),
            "proposed_data_sources": len(log["proposed_data_sources"]),
        }


class SelfImproveEngine:
    """Main self-improvement engine combining evaluation and logging."""

    def __init__(self):
        self.evaluator = ResponseEvaluator()
        self.logger = ImprovementLogger()

    def evaluate_and_log(self, query, response_summary, tools_used,
                         data_available=True):
        """
        Full self-improvement cycle: evaluate response, log results,
        and auto-propose improvements if confidence is low.

        Returns:
            dict with evaluation results and any auto-proposals
        """
        eval_result = self.evaluator.evaluate(
            query, response_summary, tools_used, data_available
        )

        # Log the evaluation
        self.logger.log_evaluation(
            query=query,
            response_summary=response_summary,
            confidence=eval_result["confidence"],
            gaps=eval_result["gaps"],
            tools_used=tools_used,
            suggestions=eval_result.get("suggestions", []),
        )

        # Auto-propose improvements for low-confidence responses
        auto_proposals = []
        if eval_result["confidence"] < 0.5:
            for gap in eval_result["gaps"]:
                if "Missing capability" in gap:
                    capability = gap.replace("Missing capability: ", "")
                    proposal = self.logger.propose_feature(
                        name=f"Add {capability}",
                        description=f"Integrate {capability} to address user query gaps",
                        rationale=f"Low confidence ({eval_result['confidence']}) on query: {query[:100]}",
                        priority="high" if eval_result["confidence"] < 0.3 else "medium",
                    )
                    auto_proposals.append(proposal)

        return {
            **eval_result,
            "auto_proposals": auto_proposals,
            "improvement_summary": self.logger.get_improvement_summary(),
        }

    def get_status(self):
        """Get current self-improvement status."""
        return self.logger.get_improvement_summary()


if __name__ == "__main__":
    engine = SelfImproveEngine()

    # Simulate an evaluation
    result = engine.evaluate_and_log(
        query="Which Missouri counties are most vulnerable to hurricanes?",
        response_summary="Returned top 10 Missouri counties by risk score filtered for hurricane disasters",
        tools_used=["query_counties"],
        data_available=True,
    )
    print("Self-Improvement Evaluation:")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Quality: {result['quality_tier']}")
    print(f"  Gaps: {result['gaps']}")
    print(f"  Auto-proposals: {len(result['auto_proposals'])}")

    status = engine.get_status()
    print(f"\nImprovement Status:")
    print(f"  Total evaluations: {status['total_evaluations']}")
    print(f"  Avg confidence: {status['avg_confidence']}")
