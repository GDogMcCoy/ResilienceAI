# /mnt/okcomputer/output/resilience_ai_analysis/code/example_workflow.py
"""
Complete archival workflow example for ResilienceAI.
"""

import asyncio
from datetime import datetime, timedelta


async def example_archive_workflow():
    """Example of complete archival workflow."""
    
    from archive_integration import ResilienceAIArchiveSystem
    
    # Initialize system
    archive_system = ResilienceAIArchiveSystem()
    
    # Example 1: Archive incident data
    incident_data = b"""{
        "incident_id": "INC-2024-001",
        "timestamp": "2024-01-15T10:30:00Z",
        "severity": "high",
        "description": "System anomaly detected in production",
        "affected_systems": ["api-gateway", "database-cluster"],
        "resolution": "Auto-remediation executed"
    }"""
    
    result = await archive_system.archive_data(
        data=incident_data,
        data_id="INC-2024-001",
        category="incident_data",
        owner="security-team@resilienceai.com",
        metadata={
            "compliance_standards": ["SOX", "ISO27001"],
            "retention_years": 7,
            "department": "Security",
            "project": "Incident Management"
        }
    )
    
    print(f"Archive result: {result}")
    
    # Example 2: Retrieve archived data
    retrieval_result = await archive_system.retrieve_data(
        data_id="INC-2024-001",
        requested_by="analyst@resilienceai.com",
        priority="standard"
    )
    
    print(f"Retrieval result: {retrieval_result}")
    
    # Example 3: Generate compliance report
    report = archive_system.generate_compliance_report(
        standard="SOX",
        start_date=datetime.now() - timedelta(days=90),
        end_date=datetime.now()
    )
    
    print(f"Compliance report: {report}")
    
    # Example 4: Evaluate lifecycle transitions
    transitions = archive_system.evaluate_lifecycle_transitions()
    
    print(f"Recommended transitions: {transitions}")


async def example_batch_archival():
    """Example of batch archival workflow."""
    
    from archive_integration import ResilienceAIArchiveSystem
    
    archive_system = ResilienceAIArchiveSystem()
    
    # Batch archive multiple incidents
    incidents = [
        {
            "id": f"INC-2024-{i:03d}",
            "data": f'{{"incident_id": "INC-2024-{i:03d}", "severity": "medium"}}'.encode()
        }
        for i in range(1, 11)
    ]
    
    results = []
    for incident in incidents:
        result = await archive_system.archive_data(
            data=incident["data"],
            data_id=incident["id"],
            category="incident_data",
            owner="security-team@resilienceai.com"
        )
        results.append(result)
    
    print(f"Batch archival completed: {len(results)} incidents archived")
    
    # Calculate total savings
    total_original = sum(r["original_size"] for r in results)
    total_compressed = sum(r["compressed_size"] for r in results)
    savings_percent = (1 - total_compressed / total_original) * 100
    
    print(f"Total original size: {total_original} bytes")
    print(f"Total compressed size: {total_compressed} bytes")
    print(f"Space savings: {savings_percent:.1f}%")


async def example_cost_analysis():
    """Example of cost analysis workflow."""
    
    from cost_optimizer import CostOptimizer
    
    optimizer = CostOptimizer()
    
    # Analyze cost for different data profiles
    data_profiles = [
        {"size_gb": 100, "access_frequency": "daily", "retention_years": 3},
        {"size_gb": 1000, "access_frequency": "weekly", "retention_years": 7},
        {"size_gb": 10000, "access_frequency": "monthly", "retention_years": 10},
    ]
    
    for profile in data_profiles:
        print(f"\nData profile: {profile['size_gb']}GB, {profile['access_frequency']} access, {profile['retention_years']} years retention")
        
        # Calculate lifecycle cost
        lifecycle_cost = optimizer.calculate_lifecycle_cost(profile)
        print(f"  Lifecycle cost: ${lifecycle_cost['total_lifecycle_cost']}")
        
        # Get optimization recommendation
        recommendation = optimizer.optimize_tier_selection(profile)
        print(f"  Optimal strategy: {recommendation['optimal_strategy']['strategy']}")
        print(f"  Potential savings: ${recommendation['potential_savings']}")


if __name__ == "__main__":
    print("ResilienceAI Archive Workflow Examples")
    print("=" * 50)
    
    # Run examples
    print("\n1. Archive Workflow Example")
    print("-" * 30)
    asyncio.run(example_archive_workflow())
    
    print("\n2. Batch Archival Example")
    print("-" * 30)
    asyncio.run(example_batch_archival())
    
    print("\n3. Cost Analysis Example")
    print("-" * 30)
    asyncio.run(example_cost_analysis())
