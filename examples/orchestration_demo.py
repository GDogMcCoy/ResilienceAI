"""
ResilienceAI - Orchestration Example
Demonstrates the multi-agent orchestration system.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.orchestrator import AgentOrchestrator


def demo_routing():
    """Demonstrate query routing."""
    print("="*60)
    print("Query Routing Demo")
    print("="*60)
    
    orchestrator = AgentOrchestrator(use_archia_cloud=False)
    
    queries = [
        "What are the climate trends in Boone County?",
        "Show me the most vulnerable counties in Missouri",
        "Are there any active weather alerts?",
        "What intervention would be most cost-effective?",
        "Compare climate and vulnerability for this county",
    ]
    
    for query in queries:
        routing = orchestrator.route_query(query)
        print(f"\n📝 {query}")
        print(f"   → Primary: {routing['primary_agent']} (confidence: {routing['confidence']:.2f})")
        print(f"   → Multi-agent: {routing['multi_agent']}")
        if routing['secondary_agents']:
            print(f"   → Secondary: {', '.join(routing['secondary_agents'])}")


def demo_execution_plan():
    """Demonstrate execution planning."""
    print("\n" + "="*60)
    print("Execution Plan Demo")
    print("="*60)
    
    orchestrator = AgentOrchestrator(use_archia_cloud=False)
    
    query = "What are the climate trends and vulnerability for county 29019?"
    plan = orchestrator.get_execution_plan(query)
    
    print(f"\n📝 Query: {query}")
    print(f"\n📊 Intent Classification:")
    print(f"   Primary: {plan['intent_classification']['primary']}")
    print(f"   Confidence: {plan['intent_classification']['confidence']:.2f}")
    print(f"   Scores: {plan['intent_classification']['scores']}")
    
    print(f"\n🔧 Execution Plan:")
    for agent_name, config in plan['execution_plan']['agents'].items():
        print(f"   [{agent_name}]")
        print(f"     Tools: {', '.join(config['tools'][:3])}{'...' if len(config['tools']) > 3 else ''}")
        if config['dependencies']:
            print(f"     Dependencies: {', '.join(config['dependencies'])}")
    
    print(f"\n⚡ Parallel Groups: {plan['execution_plan']['parallel_groups']}")


def demo_full_execution():
    """Demonstrate full query execution."""
    print("\n" + "="*60)
    print("Full Execution Demo")
    print("="*60)
    
    orchestrator = AgentOrchestrator(use_archia_cloud=False)
    
    query = "What are the most vulnerable counties in Missouri?"
    print(f"\n📝 Query: {query}")
    
    response = orchestrator.execute_query(query, context={"state": "MO"})
    
    print(f"\n✅ Response:")
    print(f"{response.response}")
    
    if response.insights:
        print(f"\n💡 Insights:")
        for insight in response.insights:
            print(f"   • {insight}")
    
    print(f"\n🔍 Follow-up Suggestions:")
    for suggestion in response.follow_up_queries:
        print(f"   • {suggestion}")
    
    print(f"\n⏱️  Execution time: {response.execution_time_ms:.1f}ms")
    print(f"🎯 Confidence: {response.confidence:.2f}")
    print(f"🔧 Mode: {response.archia_mode}")


def demo_archia_configs():
    """Demonstrate Archia configuration export."""
    print("\n" + "="*60)
    print("Archia Configuration Export")
    print("="*60)
    
    orchestrator = AgentOrchestrator(use_archia_cloud=False)
    configs = orchestrator.export_archia_configs()
    
    for agent_name, config in configs.items():
        agent_config = config['agent']
        print(f"\n📦 {agent_name}")
        print(f"   Name: {agent_config['name']}")
        print(f"   Description: {agent_config['description'][:50]}...")
        print(f"   Tools: {len(agent_config['tools'])}")


def demo_agent_summary():
    """Demonstrate agent summary."""
    print("\n" + "="*60)
    print("Agent System Summary")
    print("="*60)
    
    orchestrator = AgentOrchestrator(use_archia_cloud=False)
    summary = orchestrator.get_agent_summary()
    
    print(f"\n📊 System Overview:")
    print(f"   Total Agents: {summary['total_agents']}")
    print(f"   Total Tools: {summary['total_tools']}")
    print(f"   Mode: {summary['archia_mode']}")
    
    print(f"\n🤖 Agents:")
    for key, info in summary['agents'].items():
        print(f"   [{key}] {info['name']} v{info['version']}")
        print(f"      {info['description']}")
        print(f"      Tools: {info['tool_count']}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("ResilienceAI Multi-Agent Orchestration Demo")
    print("="*60)
    
    demo_agent_summary()
    demo_routing()
    demo_execution_plan()
    demo_full_execution()
    demo_archia_configs()
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60)
