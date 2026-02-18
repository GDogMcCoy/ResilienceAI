"""
ResilienceAI - Orchestration Tests
Comprehensive tests for the multi-agent orchestration system.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

from src.agents.base_agent import BaseAgent, AgentOutput, AgentStatus, ToolResult
from src.agents.langgraph_flow import (
    LangGraphFlow, OrchestratorState, IntentClassification, 
    AgentNode, ExecutionMode
)
from src.agents.orchestrator import AgentOrchestrator, OrchestratedResponse


class MockAgent(BaseAgent):
    """Mock agent for testing."""
    
    name = "mock_agent"
    description = "A mock agent for testing"
    version = "3.2.0"
    intent_keywords = ["mock", "test", "fake"]
    
    @property
    def system_prompt(self) -> str:
        return "You are a mock agent for testing."
    
    def __init__(self, tools_data: Dict = None):
        super().__init__()
        self._tools_data = tools_data or {}
        
    def get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "mock_tool",
                "description": "A mock tool for testing",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string"},
                        "fips": {"type": "string"}
                    }
                }
            },
            {
                "name": "another_tool",
                "description": "Another mock tool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "integer"}
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name in self._tools_data:
            return self._tools_data[tool_name]
        return {"error": f"Tool {tool_name} not found"}


class TestBaseAgent(unittest.TestCase):
    """Tests for BaseAgent."""
    
    def test_intent_match_exact(self):
        """Test exact keyword matching."""
        agent = MockAgent()
        score = agent.calculate_intent_match("This is a mock test query")
        self.assertGreater(score, 0.5)
        
    def test_intent_match_partial(self):
        """Test partial keyword matching."""
        agent = MockAgent()
        score = agent.calculate_intent_match("This is fake data")
        self.assertGreater(score, 0)
        self.assertLess(score, 1)
        
    def test_intent_match_none(self):
        """Test no keyword matching."""
        agent = MockAgent()
        score = agent.calculate_intent_match("Completely unrelated query")
        self.assertEqual(score, 0)
        
    def test_get_tool_names(self):
        """Test getting tool names."""
        agent = MockAgent()
        names = agent.get_tool_names()
        self.assertEqual(len(names), 2)
        self.assertIn("mock_tool", names)
        self.assertIn("another_tool", names)
        
    def test_can_handle_tool(self):
        """Test tool handling check."""
        agent = MockAgent()
        self.assertTrue(agent.can_handle_tool("mock_tool"))
        self.assertFalse(agent.can_handle_tool("unknown_tool"))
        
    def test_get_archia_config(self):
        """Test Archia config export."""
        agent = MockAgent()
        config = agent.get_archia_config()
        self.assertEqual(config["agent"]["name"], "mock_agent")
        self.assertEqual(len(config["agent"]["tools"]), 2)


class TestIntentClassification(unittest.TestCase):
    """Tests for IntentClassification."""
    
    def test_requires_multi_agent_true(self):
        """Test multi-agent detection when scores are close."""
        intent = IntentClassification(
            scores={"agent1": 0.8, "agent2": 0.7, "agent3": 0.3},
            primary="agent1",
            confidence=0.8
        )
        self.assertTrue(intent.requires_multi_agent(threshold=0.15))
        
    def test_requires_multi_agent_false(self):
        """Test multi-agent detection when scores are far apart."""
        intent = IntentClassification(
            scores={"agent1": 0.9, "agent2": 0.4, "agent3": 0.3},
            primary="agent1",
            confidence=0.9
        )
        self.assertFalse(intent.requires_multi_agent(threshold=0.15))
        
    def test_requires_multi_agent_single(self):
        """Test multi-agent detection with single agent."""
        intent = IntentClassification(
            scores={"agent1": 0.8},
            primary="agent1",
            confidence=0.8
        )
        self.assertFalse(intent.requires_multi_agent())


class TestLangGraphFlow(unittest.TestCase):
    """Tests for LangGraphFlow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agents = {
            "climate": MockAgent({"get_climate_trends": {"temp": 75}}),
            "vulnerability": MockAgent({"query_counties": [{"fips": "29019"}]}),
            "realtime": MockAgent({"get_weather_alerts": {"count": 5}}),
            "planning": MockAgent({"calculate_roi": {"roi": 2.5}}),
        }
        # Set distinct keywords for each agent
        self.agents["climate"].intent_keywords = ["climate", "temperature", "weather"]
        self.agents["vulnerability"].intent_keywords = ["vulnerability", "county", "risk"]
        self.agents["realtime"].intent_keywords = ["alert", "realtime", "current"]
        self.agents["planning"].intent_keywords = ["plan", "forecast", "roi"]
        
        self.flow = LangGraphFlow(self.agents)
        
    def test_classify_intent_single(self):
        """Test intent classification for single agent."""
        intent = self.flow.classify_intent("What is the climate in this county?")
        self.assertEqual(intent.primary, "climate")
        self.assertGreater(intent.confidence, 0)
        
    def test_classify_intent_multi(self):
        """Test intent classification for multi-agent."""
        intent = self.flow.classify_intent(
            "What is the climate vulnerability and plan for this county?"
        )
        # Should detect multiple intents
        self.assertGreaterEqual(len(intent.scores), 2)
        
    def test_classify_intent_default(self):
        """Test default intent when no match."""
        intent = self.flow.classify_intent("xyz123 nonsense query")
        self.assertEqual(intent.primary, "vulnerability")  # Default fallback
        
    def test_build_execution_graph_single(self):
        """Test building graph for single agent."""
        intent = IntentClassification(
            scores={"climate": 0.9},
            primary="climate",
            confidence=0.9
        )
        graph = self.flow.build_execution_graph(intent, "climate query")
        self.assertEqual(len(graph), 1)
        self.assertIn("climate", graph)
        
    def test_build_execution_graph_multi(self):
        """Test building graph for multiple agents."""
        intent = IntentClassification(
            scores={"climate": 0.8, "vulnerability": 0.75},
            primary="climate",
            confidence=0.8,
            secondary=["vulnerability"]
        )
        graph = self.flow.build_execution_graph(intent, "complex query")
        self.assertGreaterEqual(len(graph), 2)
        
    def test_topological_sort(self):
        """Test topological sorting of agents."""
        # Create graph with dependencies
        self.flow.execution_graph = {
            "vulnerability": AgentNode("vulnerability", [], []),
            "climate": AgentNode("climate", [], []),
            "planning": AgentNode("planning", [], ["climate", "vulnerability"]),
        }
        sorted_agents = self.flow._topological_sort()
        # Planning should come after its dependencies
        planning_idx = sorted_agents.index("planning")
        climate_idx = sorted_agents.index("climate")
        vuln_idx = sorted_agents.index("vulnerability")
        self.assertGreater(planning_idx, climate_idx)
        self.assertGreater(planning_idx, vuln_idx)
        
    def test_group_by_dependency_level(self):
        """Test grouping agents by dependency level."""
        self.flow.execution_graph = {
            "vulnerability": AgentNode("vulnerability", [], []),
            "climate": AgentNode("climate", [], []),
            "planning": AgentNode("planning", [], ["climate", "vulnerability"]),
        }
        sorted_agents = ["vulnerability", "climate", "planning"]
        levels = self.flow._group_by_dependency_level(sorted_agents)
        # First level should have vulnerability and climate (no deps)
        self.assertIn("vulnerability", levels[0])
        self.assertIn("climate", levels[0])
        # Second level should have planning
        self.assertIn("planning", levels[1])


class TestAgentOrchestrator(unittest.TestCase):
    """Tests for AgentOrchestrator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Patch the agent imports to avoid loading real data
        with patch.dict(sys.modules, {
            'src.climate_client': MagicMock(),
            'src.gee_client': MagicMock(),
            'src.agent': MagicMock(),
        }):
            self.orchestrator = AgentOrchestrator(use_archia_cloud=False)
            
    def test_build_tool_index(self):
        """Test tool index building."""
        # The index should map tool names to agent keys
        self.assertIn("mock_tool", self.orchestrator._tool_index)
        
    def test_route_query(self):
        """Test query routing."""
        routing = self.orchestrator.route_query("What is the climate?")
        self.assertIn("primary_agent", routing)
        self.assertIn("confidence", routing)
        self.assertIn("scores", routing)
        
    def test_get_agent_summary(self):
        """Test agent summary."""
        summary = self.orchestrator.get_agent_summary()
        self.assertEqual(summary["total_agents"], 4)
        self.assertIn("agents", summary)
        self.assertIn("climate", summary["agents"])
        
    def test_get_all_tools(self):
        """Test getting all tools."""
        tools = self.orchestrator.get_all_tools()
        self.assertIsInstance(tools, list)
        # Should have tools from all agents
        self.assertGreater(len(tools), 0)
        
    def test_get_execution_plan(self):
        """Test execution plan generation."""
        plan = self.orchestrator.get_execution_plan("Climate in county 29019")
        self.assertIn("query", plan)
        self.assertIn("intent_classification", plan)
        self.assertIn("execution_plan", plan)


class TestIntegration(unittest.TestCase):
    """Integration tests for the full orchestration pipeline."""
    
    @patch('src.agents.orchestrator.ClimateAgent')
    @patch('src.agents.orchestrator.VulnerabilityAgent')
    @patch('src.agents.orchestrator.RealtimeAgent')
    @patch('src.agents.orchestrator.PlanningAgent')
    def test_full_pipeline(self, MockPlanning, MockRealtime, MockVulnerability, MockClimate):
        """Test the full orchestration pipeline with mocked agents."""
        # Setup mocks
        mock_climate = Mock()
        mock_climate.name = "climate_agent"
        mock_climate.description = "Climate agent"
        mock_climate.calculate_intent_match.return_value = 0.9
        mock_climate.get_tool_names.return_value = ["get_climate_trends"]
        mock_climate.get_tools.return_value = [{"name": "get_climate_trends"}]
        mock_climate.execute.return_value = AgentOutput(
            agent_name="climate_agent",
            status=AgentStatus.COMPLETED,
            results=[ToolResult("get_climate_trends", True, {"temp": 75})],
            insights=["Temperature is rising"],
            confidence=0.9
        )
        MockClimate.return_value = mock_climate
        
        mock_vuln = Mock()
        mock_vuln.name = "vulnerability_agent"
        mock_vuln.calculate_intent_match.return_value = 0.3
        mock_vuln.get_tool_names.return_value = ["query_counties"]
        mock_vuln.get_tools.return_value = [{"name": "query_counties"}]
        MockVulnerability.return_value = mock_vuln
        
        mock_realtime = Mock()
        mock_realtime.name = "realtime_agent"
        mock_realtime.calculate_intent_match.return_value = 0.1
        mock_realtime.get_tool_names.return_value = ["get_alerts"]
        mock_realtime.get_tools.return_value = [{"name": "get_alerts"}]
        MockRealtime.return_value = mock_realtime
        
        mock_planning = Mock()
        mock_planning.name = "planning_agent"
        mock_planning.calculate_intent_match.return_value = 0.1
        mock_planning.get_tool_names.return_value = ["calculate_roi"]
        mock_planning.get_tools.return_value = [{"name": "calculate_roi"}]
        MockPlanning.return_value = mock_planning
        
        # Create orchestrator
        orchestrator = AgentOrchestrator(use_archia_cloud=False)
        
        # Test routing
        routing = orchestrator.route_query("What is the climate?")
        self.assertEqual(routing["primary_agent"], "climate")
        
        # Test execution plan
        plan = orchestrator.get_execution_plan("Climate trends")
        self.assertIn("intent_classification", plan)


class TestErrorHandling(unittest.TestCase):
    """Tests for error handling."""
    
    def test_tool_not_found(self):
        """Test handling of unknown tool."""
        agent = MockAgent()
        result = agent.execute_tool("unknown_tool", {})
        self.assertIn("error", result)
        
    def test_orchestrator_error_handling(self):
        """Test orchestrator error handling."""
        orchestrator = AgentOrchestrator(use_archia_cloud=False)
        result = orchestrator.execute_tool("nonexistent_tool", {})
        self.assertIn("error", result)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBaseAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestIntentClassification))
    suite.addTests(loader.loadTestsFromTestCase(TestLangGraphFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
