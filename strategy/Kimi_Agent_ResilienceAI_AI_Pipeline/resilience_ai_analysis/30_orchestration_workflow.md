# ResilienceAI Orchestration & Workflow Enhancement Design

## Executive Summary

This document provides a comprehensive analysis of the current orchestration capabilities in the ResilienceAI repository and designs a next-generation workflow orchestration platform. The proposed system integrates Apache Airflow, Prefect, and custom DAG-based orchestration to enable sophisticated pipeline management, parallel execution, and dynamic workflow generation.

---

## 1. Current State Analysis

### 1.1 Existing Orchestration Components

| Component | File Path | Purpose | Current Limitations |
|-----------|-----------|---------|---------------------|
| Pipeline Runner | `run_pipeline.py` | Sequential data pipeline execution | No parallel execution, limited error handling |
| Agent Orchestrator | `src/agents/orchestrator.py` | Multi-agent query routing | No DAG visualization, limited retry logic |
| LangGraph Flow | `src/agents/langgraph_flow.py` | State machine for agent routing | No persistence, no scheduling |
| Real-time Pipeline | `src/realtime_pipeline.py` | WebSocket-based event streaming | No workflow state management |
| Agent Orchestrator (Legacy) | `src/agent_orchestrator.py` | Tool execution orchestration | Sequential only, no dependency tracking |

### 1.2 Current Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Current Sequential Pipeline                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ download │───▶│ features │───▶│   eda    │───▶│  train   │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │                                               │         │
│       ▼                                               ▼         │
│  [HIFLD/FEMA]                                    ┌──────────┐  │
│  [Census/CMS]                                    │  agent   │  │
│                                                  └──────────┘  │
│                                                                  │
│  Execution: Sequential, Blocking, No Parallelism                 │
│  Error Handling: Basic try/except, No Retries                    │
│  State Management: In-memory only                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Current Agent Orchestration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   Current Agent Orchestration                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ User Query  │───▶│ Intent Class │───▶│ Agent Router │       │
│  └─────────────┘    └──────────────┘    └──────────────┘       │
│                                                │                 │
│                    ┌───────────────────────────┼───┐            │
│                    ▼                           ▼   ▼            │
│              ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│              │ Climate  │  │Vulnerability│ │ Realtime │          │
│              │  Agent   │  │   Agent    │  │  Agent   │          │
│              └──────────┘  └──────────┘  └──────────┘          │
│                    │                           │                 │
│                    └───────────┬───────────────┘                 │
│                                ▼                                 │
│                         ┌──────────┐                            │
│                         │ Synthesis│                            │
│                         └──────────┘                            │
│                                                                  │
│  Parallel Execution: Limited (ThreadPoolExecutor)                │
│  Dependency Management: Basic (LangGraph)                        │
│  State Persistence: None                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Proposed Orchestration Architecture

### 2.1 High-Level System Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ResilienceAI Workflow Orchestration Platform              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Orchestration API Layer                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│  │  │  Workflow   │  │   Task      │  │   DAG       │  │  Schedule  │ │   │
│  │  │   Service   │  │   Service   │  │   Service   │  │   Service  │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Workflow Engine Core                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │   │
│  │  │   DAG       │  │   State     │  │   Retry     │  │  Parallel  │ │   │
│  │  │  Compiler   │  │   Manager   │  │   Handler   │  │  Executor  │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                    ┌───────────────┼───────────────┐                        │
│                    ▼               ▼               ▼                        │
│  ┌─────────────────────┐ ┌─────────────────┐ ┌─────────────────────┐       │
│  │   Apache Airflow    │ │     Prefect     │ │  Custom Executor    │       │
│  │   (Scheduling)      │ │   (Modern)      │ │  (Lightweight)      │       │
│  └─────────────────────┘ └─────────────────┘ └─────────────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Proposed Folder Structure

```
resilience_ai/
├── orchestration/                    # NEW: Core orchestration module
│   ├── __init__.py
│   ├── core/                         # Core orchestration engine
│   │   ├── __init__.py
│   │   ├── dag.py                    # DAG definition and compilation
│   │   ├── task.py                   # Task abstraction
│   │   ├── workflow.py               # Workflow management
│   │   ├── state.py                  # State management
│   │   └── executor.py               # Execution engine
│   ├── engines/                      # Pluggable execution engines
│   │   ├── __init__.py
│   │   ├── airflow_engine.py         # Apache Airflow integration
│   │   ├── prefect_engine.py         # Prefect integration
│   │   ├── local_engine.py           # Local execution engine
│   │   └── celery_engine.py          # Distributed Celery engine
│   ├── schedulers/                   # Workflow schedulers
│   │   ├── __init__.py
│   │   ├── cron_scheduler.py         # Cron-based scheduling
│   │   ├── event_scheduler.py        # Event-driven scheduling
│   │   └── interval_scheduler.py     # Interval-based scheduling
│   ├── monitors/                     # Monitoring and observability
│   │   ├── __init__.py
│   │   ├── workflow_monitor.py       # Workflow execution monitoring
│   │   ├── task_monitor.py           # Task-level monitoring
│   │   ├── metrics.py                # Metrics collection
│   │   └── alerts.py                 # Alert management
│   ├── retry/                        # Retry mechanisms
│   │   ├── __init__.py
│   │   ├── policies.py               # Retry policies
│   │   ├── backoff.py                # Backoff strategies
│   │   └── circuit_breaker.py        # Circuit breaker pattern
│   ├── versioning/                   # Workflow versioning
│   │   ├── __init__.py
│   │   ├── version_manager.py        # Version management
│   │   └── migrations.py             # Workflow migrations
│   └── dags/                         # DAG definitions
│       ├── __init__.py
│       ├── data_pipeline_dag.py      # Data pipeline DAG
│       ├── agent_pipeline_dag.py     # Agent pipeline DAG
│       ├── realtime_pipeline_dag.py  # Real-time pipeline DAG
│       └── composite_dag.py          # Composite workflows
├── dags/                             # Airflow DAGs (compatibility)
│   ├── data_pipeline.py
│   ├── agent_orchestration.py
│   └── monitoring.py
├── flows/                            # Prefect flows (compatibility)
│   ├── data_pipeline_flow.py
│   └── agent_flow.py
└── config/
    ├── orchestration.yaml            # Orchestration configuration
    ├── airflow.cfg                   # Airflow configuration
    └── prefect.yaml                  # Prefect configuration
```

---

## 3. Pipeline DAG Design

### 3.1 Data Pipeline DAG

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/orchestration/dags/data_pipeline_dag.py

"""
ResilienceAI Data Pipeline DAG
Comprehensive data acquisition and processing workflow.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import asyncio
from pathlib import Path

from orchestration.core.dag import DAG, Task, TaskDependency
from orchestration.core.task import TaskResult, TaskStatus
from orchestration.retry.policies import ExponentialBackoffRetry


@dataclass
class DataPipelineConfig:
    """Configuration for data pipeline."""
    force_download: bool = False
    focus_states: List[str] = field(default_factory=lambda: ["MO"])
    cache_enabled: bool = True
    parallel_downloads: bool = True
    max_retries: int = 3
    retry_delay: int = 5


class DataPipelineDAG:
    """
    DAG for the complete data acquisition and processing pipeline.
    
    Pipeline Stages:
    1. Data Acquisition (Parallel)
       - HIFLD facilities (hospitals, nursing homes, etc.)
       - CMS nursing home data
       - FEMA disaster declarations
       - Census demographics
       - County centroids
    
    2. Feature Engineering (Sequential)
       - Merge datasets
       - Calculate risk scores
       - Generate features
    
    3. Exploratory Data Analysis (Parallel)
       - Statistical analysis
       - Visualization generation
       - Correlation analysis
    
    4. Model Training (Sequential)
       - Train predictive models
       - Evaluate performance
       - Save artifacts
    
    5. Agent Configuration (Sequential)
       - Export agent configs
       - Validate outputs
    """
    
    def __init__(self, config: DataPipelineConfig = None):
        self.config = config or DataPipelineConfig()
        self.dag = self._build_dag()
    
    def _build_dag(self) -> DAG:
        """Build the complete data pipeline DAG."""
        dag = DAG(
            name="resilience_data_pipeline",
            description="Complete data acquisition and processing pipeline",
            schedule_interval="0 2 * * *",  # Daily at 2 AM
            catchup=False,
            max_active_runs=1,
            default_retry_policy=ExponentialBackoffRetry(
                max_retries=self.config.max_retries,
                base_delay=self.config.retry_delay
            )
        )
        
        # Stage 1: Data Acquisition (Parallel Tasks)
        download_hifld = Task(
            name="download_hifld",
            task_type="python",
            python_callable=self._download_hifld,
            retries=self.config.max_retries,
            retry_delay=timedelta(seconds=self.config.retry_delay),
            timeout=300
        )
        
        download_cms = Task(
            name="download_cms",
            task_type="python",
            python_callable=self._download_cms,
            retries=self.config.max_retries,
            retry_delay=timedelta(seconds=self.config.retry_delay),
            timeout=300
        )
        
        download_fema = Task(
            name="download_fema",
            task_type="python",
            python_callable=self._download_fema,
            retries=self.config.max_retries,
            retry_delay=timedelta(seconds=self.config.retry_delay),
            timeout=600
        )
        
        download_census = Task(
            name="download_census",
            task_type="python",
            python_callable=self._download_census,
            retries=self.config.max_retries,
            retry_delay=timedelta(seconds=self.config.retry_delay),
            timeout=300
        )
        
        download_centroids = Task(
            name="download_centroids",
            task_type="python",
            python_callable=self._download_centroids,
            retries=self.config.max_retries,
            retry_delay=timedelta(seconds=self.config.retry_delay),
            timeout=120
        )
        
        # Stage 2: Feature Engineering (Depends on all downloads)
        feature_engineering = Task(
            name="feature_engineering",
            task_type="python",
            python_callable=self._run_feature_engineering,
            retries=2,
            retry_delay=timedelta(seconds=10),
            timeout=600
        )
        
        # Stage 3: EDA (Parallel, depends on features)
        eda_statistics = Task(
            name="eda_statistics",
            task_type="python",
            python_callable=self._run_eda_statistics,
            timeout=300
        )
        
        eda_visualizations = Task(
            name="eda_visualizations",
            task_type="python",
            python_callable=self._run_eda_visualizations,
            timeout=300
        )
        
        eda_correlation = Task(
            name="eda_correlation",
            task_type="python",
            python_callable=self._run_eda_correlation,
            timeout=300
        )
        
        # Stage 4: Model Training (Depends on features)
        train_models = Task(
            name="train_models",
            task_type="python",
            python_callable=self._train_models,
            retries=1,
            timeout=900
        )
        
        # Stage 5: Agent Configuration (Depends on models)
        agent_config = Task(
            name="agent_config",
            task_type="python",
            python_callable=self._export_agent_config,
            timeout=60
        )
        
        # Add tasks to DAG
        dag.add_tasks([
            download_hifld, download_cms, download_fema,
            download_census, download_centroids,
            feature_engineering,
            eda_statistics, eda_visualizations, eda_correlation,
            train_models,
            agent_config
        ])
        
        # Define dependencies
        # Stage 1: All downloads are parallel (no dependencies)
        
        # Stage 2: Feature engineering depends on all downloads
        dag.add_dependency(feature_engineering, [download_hifld, download_cms, 
                                                  download_fema, download_census, 
                                                  download_centroids])
        
        # Stage 3: EDA tasks depend on feature engineering (parallel)
        dag.add_dependency(eda_statistics, feature_engineering)
        dag.add_dependency(eda_visualizations, feature_engineering)
        dag.add_dependency(eda_correlation, feature_engineering)
        
        # Stage 4: Model training depends on feature engineering
        dag.add_dependency(train_models, feature_engineering)
        
        # Stage 5: Agent config depends on model training
        dag.add_dependency(agent_config, train_models)
        
        return dag
    
    # Task implementations
    def _download_hifld(self, context: Dict[str, Any]) -> TaskResult:
        """Download HIFLD facility data."""
        from src.download_data import download_all_hifld
        try:
            result = download_all_hifld(force=self.config.force_download)
            return TaskResult(
                status=TaskStatus.SUCCESS,
                data={"facilities": {k: len(v) for k, v in result.items()}},
                message=f"Downloaded {len(result)} facility types"
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                message="HIFLD download failed"
            )
    
    def _download_cms(self, context: Dict[str, Any]) -> TaskResult:
        """Download CMS nursing home data."""
        from src.download_data import download_nursing_homes
        try:
            result = download_nursing_homes(force=self.config.force_download)
            return TaskResult(
                status=TaskStatus.SUCCESS,
                data={"records": len(result)},
                message=f"Downloaded {len(result)} nursing home records"
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                message="CMS download failed"
            )
    
    def _download_fema(self, context: Dict[str, Any]) -> TaskResult:
        """Download FEMA disaster declarations."""
        from src.download_data import download_fema_disasters
        try:
            result = download_fema_disasters(force=self.config.force_download)
            return TaskResult(
                status=TaskStatus.SUCCESS,
                data={"disasters": len(result)},
                message=f"Downloaded {len(result)} disaster records"
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                message="FEMA download failed"
            )
    
    def _download_census(self, context: Dict[str, Any]) -> TaskResult:
        """Download Census demographic data."""
        from src.download_data import download_census_data
        try:
            result = download_census_data(force=self.config.force_download)
            return TaskResult(
                status=TaskStatus.SUCCESS,
                data={"counties": len(result)},
                message=f"Downloaded {len(result)} county records"
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                message="Census download failed"
            )
    
    def _download_centroids(self, context: Dict[str, Any]) -> TaskResult:
        """Download county centroid data."""
        from src.download_data import download_county_centroids
        try:
            result = download_county_centroids(force=self.config.force_download)
            return TaskResult(
                status=TaskStatus.SUCCESS,
                data={"centroids": len(result)},
                message=f"Downloaded {len(result)} county centroids"
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                message="Centroid download failed"
            )
    
    def _run_feature_engineering(self, context: Dict[str, Any]) -> TaskResult:
        """Run feature engineering pipeline."""
        from src.feature_engineering import run_feature_engineering
        try:
            result = run_feature_engineering()
            return TaskResult(
                status=TaskStatus.SUCCESS,
                data={"features": result},
                message="Feature engineering completed"
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                message="Feature engineering failed"
            )
    
    def _run_eda_statistics(self, context: Dict[str, Any]) -> TaskResult:
        """Run statistical EDA."""
        from src.pipeline.eda import run_eda_statistics
        try:
            result = run_eda_statistics()
            return TaskResult(
                status=TaskStatus.SUCCESS,
                data={"statistics": result},
                message="Statistical EDA completed"
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                message="EDA statistics failed"
            )
    
    def _run_eda_visualizations(self, context: Dict[str, Any]) -> TaskResult:
        """Generate EDA visualizations."""
        from src.pipeline.eda import run_eda_visualizations
        try:
            result = run_eda_visualizations()
            return TaskResult(
                status=TaskStatus.SUCCESS,
                data={"visualizations": result},
                message="EDA visualizations completed"
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                message="EDA visualizations failed"
            )
    
    def _run_eda_correlation(self, context: Dict[str, Any]) -> TaskResult:
        """Run correlation analysis."""
        from src.pipeline.eda import run_correlation_analysis
        try:
            result = run_correlation_analysis()
            return TaskResult(
                status=TaskStatus.SUCCESS,
                data={"correlations": result},
                message="Correlation analysis completed"
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                message="Correlation analysis failed"
            )
    
    def _train_models(self, context: Dict[str, Any]) -> TaskResult:
        """Train predictive models."""
        from src.train_models import train_and_evaluate
        try:
            result = train_and_evaluate()
            return TaskResult(
                status=TaskStatus.SUCCESS,
                data={"models": result},
                message="Model training completed"
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                message="Model training failed"
            )
    
    def _export_agent_config(self, context: Dict[str, Any]) -> TaskResult:
        """Export agent configuration."""
        from src.agent import export_agent_config
        try:
            result = export_agent_config()
            return TaskResult(
                status=TaskStatus.SUCCESS,
                data={"config": result},
                message="Agent configuration exported"
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                message="Agent config export failed"
            )
    
    def get_dag(self) -> DAG:
        """Get the compiled DAG."""
        return self.dag
    
    def visualize(self, output_path: str = None):
        """Generate DAG visualization."""
        return self.dag.visualize(output_path)


# DAG Visualization
"""
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Data Pipeline DAG Visualization                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Stage 1: Data Acquisition (Parallel)                                        │
│  ╔═══════════════╗  ╔═══════════════╗  ╔═══════════════╗                    │
│  ║ download_hifld║  ║ download_cms  ║  ║ download_fema ║                    │
│  ║    [Task]     ║  ║    [Task]     ║  ║    [Task]     ║                    │
│  ╚═══════╤═══════╝  ╚═══════╤═══════╝  ╚═══════╤═══════╝                    │
│          │                   │                   │                           │
│  ╔═══════╧═══════╗  ╔═══════╧═══════╗          │                           │
│  ║download_census║  ║download_centro║◄─────────┘                           │
│  ║    [Task]     ║  ║    ids[Task]  ║                                      │
│  ╚═══════╤═══════╝  ╚═══════════════╝                                      │
│          │                                                                   │
│          ▼                                                                   │
│  Stage 2: Feature Engineering                                                │
│  ╔═══════════════════════════════════════════════════════════╗              │
│  ║              feature_engineering [Task]                   ║              │
│  ╚═══════════════════════════════════════════════════════════╝              │
│          │                                                                   │
│          ▼                                                                   │
│  Stage 3: EDA (Parallel)                                                     │
│  ╔═══════════════════╗  ╔═══════════════════╗  ╔═══════════════════╗       │
│  ║ eda_statistics    ║  ║ eda_visualizations║  ║ eda_correlation   ║       │
│  ║     [Task]        ║  ║     [Task]        ║  ║     [Task]        ║       │
│  ╚═══════════════════╝  ╚═══════════════════╝  ╚═══════════════════╝       │
│          │                                                                   │
│          ▼                                                                   │
│  Stage 4: Model Training                                                     │
│  ╔═══════════════════════════════════════════════════════════╗              │
│  ║                  train_models [Task]                      ║              │
│  ╚═══════════════════════════════════════════════════════════╝              │
│          │                                                                   │
│          ▼                                                                   │
│  Stage 5: Agent Configuration                                                │
│  ╔═══════════════════════════════════════════════════════════╗              │
│  ║                  agent_config [Task]                      ║              │
│  ╚═══════════════════════════════════════════════════════════╝              │
│                                                                              │
│  Legend: [Task] = Executable Task, ───▶ = Dependency                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
"""


### 3.2 Agent Pipeline DAG

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/orchestration/dags/agent_pipeline_dag.py

"""
ResilienceAI Agent Pipeline DAG
Multi-agent orchestration with parallel execution and dependency management.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor

from orchestration.core.dag import DAG, Task, TaskDependency, BranchCondition
from orchestration.core.task import TaskResult, TaskStatus
from orchestration.retry.policies import ExponentialBackoffRetry, LinearRetry


class AgentType(Enum):
    """Types of specialized agents."""
    CLIMATE = "climate"
    VULNERABILITY = "vulnerability"
    REALTIME = "realtime"
    PLANNING = "planning"


@dataclass
class AgentPipelineConfig:
    """Configuration for agent pipeline."""
    max_parallel_agents: int = 4
    enable_multi_agent: bool = True
    multi_agent_threshold: float = 0.15
    intent_classification_threshold: float = 0.2
    synthesis_timeout: int = 30
    use_archia_cloud: bool = False


class AgentPipelineDAG:
    """
    DAG for multi-agent orchestration pipeline.
    
    Pipeline Stages:
    1. Query Intake & Validation
       - Parse and validate user query
       - Extract context (FIPS, state, etc.)
    
    2. Intent Classification (Parallel agents)
       - Climate agent scoring
       - Vulnerability agent scoring
       - Realtime agent scoring
       - Planning agent scoring
    
    3. Agent Selection & Routing
       - Determine primary agent
       - Identify secondary agents (if multi-agent)
       - Build execution graph
    
    4. Agent Execution (Parallel where possible)
       - Execute selected agents
       - Collect results
    
    5. Result Synthesis
       - Combine agent outputs
       - Generate insights
       - Create follow-up suggestions
    
    6. Response Formatting
       - Format final response
       - Add metadata
    """
    
    def __init__(self, config: AgentPipelineConfig = None):
        self.config = config or AgentPipelineConfig()
        self.dag = self._build_dag()
    
    def _build_dag(self) -> DAG:
        """Build the agent orchestration DAG."""
        dag = DAG(
            name="resilience_agent_pipeline",
            description="Multi-agent orchestration pipeline",
            schedule_interval=None,  # Event-driven
            catchup=False,
            max_active_runs=10,
            default_retry_policy=LinearRetry(max_retries=2, delay=1)
        )
        
        # Stage 1: Query Intake
        query_intake = Task(
            name="query_intake",
            task_type="python",
            python_callable=self._query_intake,
            timeout=10
        )
        
        # Stage 2: Intent Classification (Parallel)
        classify_climate = Task(
            name="classify_climate",
            task_type="python",
            python_callable=self._classify_climate_intent,
            timeout=5
        )
        
        classify_vulnerability = Task(
            name="classify_vulnerability",
            task_type="python",
            python_callable=self._classify_vulnerability_intent,
            timeout=5
        )
        
        classify_realtime = Task(
            name="classify_realtime",
            task_type="python",
            python_callable=self._classify_realtime_intent,
            timeout=5
        )
        
        classify_planning = Task(
            name="classify_planning",
            task_type="python",
            python_callable=self._classify_planning_intent,
            timeout=5
        )
        
        # Stage 3: Agent Selection
        agent_selection = Task(
            name="agent_selection",
            task_type="python",
            python_callable=self._select_agents,
            timeout=5
        )
        
        # Stage 4: Agent Execution (Dynamic - created at runtime)
        execute_climate = Task(
            name="execute_climate",
            task_type="python",
            python_callable=self._execute_climate_agent,
            timeout=30,
            trigger_rule="all_done"  # Run even if other agents fail
        )
        
        execute_vulnerability = Task(
            name="execute_vulnerability",
            task_type="python",
            python_callable=self._execute_vulnerability_agent,
            timeout=30,
            trigger_rule="all_done"
        )
        
        execute_realtime = Task(
            name="execute_realtime",
            task_type="python",
            python_callable=self._execute_realtime_agent,
            timeout=30,
            trigger_rule="all_done"
        )
        
        execute_planning = Task(
            name="execute_planning",
            task_type="python",
            python_callable=self._execute_planning_agent,
            timeout=30,
            trigger_rule="all_done"
        )
        
        # Stage 5: Result Synthesis
        synthesize_results = Task(
            name="synthesize_results",
            task_type="python",
            python_callable=self._synthesize_results,
            timeout=self.config.synthesis_timeout
        )
        
        # Stage 6: Response Formatting
        format_response = Task(
            name="format_response",
            task_type="python",
            python_callable=self._format_response,
            timeout=10
        )
        
        # Add tasks
        dag.add_tasks([
            query_intake,
            classify_climate, classify_vulnerability, 
            classify_realtime, classify_planning,
            agent_selection,
            execute_climate, execute_vulnerability,
            execute_realtime, execute_planning,
            synthesize_results,
            format_response
        ])
        
        # Define dependencies
        # Stage 2 depends on Stage 1
        dag.add_dependency(classify_climate, query_intake)
        dag.add_dependency(classify_vulnerability, query_intake)
        dag.add_dependency(classify_realtime, query_intake)
        dag.add_dependency(classify_planning, query_intake)
        
        # Stage 3 depends on all classification tasks
        dag.add_dependency(agent_selection, [
            classify_climate, classify_vulnerability,
            classify_realtime, classify_planning
        ])
        
        # Stage 4 depends on agent selection
        dag.add_dependency(execute_climate, agent_selection)
        dag.add_dependency(execute_vulnerability, agent_selection)
        dag.add_dependency(execute_realtime, agent_selection)
        dag.add_dependency(execute_planning, agent_selection)
        
        # Stage 5 depends on all agent executions
        dag.add_dependency(synthesize_results, [
            execute_climate, execute_vulnerability,
            execute_realtime, execute_planning
        ])
        
        # Stage 6 depends on synthesis
        dag.add_dependency(format_response, synthesize_results)
        
        # Add conditional branching for agent execution
        # Only execute agents that were selected
        dag.add_branch_condition(execute_climate, self._should_execute_climate)
        dag.add_branch_condition(execute_vulnerability, self._should_execute_vulnerability)
        dag.add_branch_condition(execute_realtime, self._should_execute_realtime)
        dag.add_branch_condition(execute_planning, self._should_execute_planning)
        
        return dag
    
    # Task implementations
    def _query_intake(self, context: Dict[str, Any]) -> TaskResult:
        """Process incoming query and extract context."""
        query = context.get("query", "")
        
        # Extract FIPS codes
        import re
        fips_matches = re.findall(r'\b\d{5}\b', query)
        
        # Extract state codes
        state_pattern = r'\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b'
        state_matches = re.findall(state_pattern, query.upper())
        
        # Extract county names
        county_pattern = r'in\s+([\w\s]+)\s+county'
        county_matches = re.findall(county_pattern, query.lower())
        
        return TaskResult(
            status=TaskStatus.SUCCESS,
            data={
                "query": query,
                "fips_codes": fips_matches,
                "states": state_matches,
                "counties": [c.strip().title() for c in county_matches],
                "extracted_context": True
            },
            message="Query intake completed"
        )
    
    def _classify_climate_intent(self, context: Dict[str, Any]) -> TaskResult:
        """Classify climate-related intent."""
        query = context.get("query", "").lower()
        
        climate_keywords = [
            "climate", "temperature", "precipitation", "drought", "flood",
            "weather", "trend", "projection", "scenario", "rcp", "ssp"
        ]
        
        score = sum(1 for kw in climate_keywords if kw in query) / len(climate_keywords)
        score = min(score * 3, 1.0)  # Scale up, cap at 1.0
        
        return TaskResult(
            status=TaskStatus.SUCCESS,
            data={"agent": "climate", "score": round(score, 3)},
            message=f"Climate intent score: {score:.3f}"
        )
    
    def _classify_vulnerability_intent(self, context: Dict[str, Any]) -> TaskResult:
        """Classify vulnerability-related intent."""
        query = context.get("query", "").lower()
        
        vulnerability_keywords = [
            "vulnerable", "vulnerability", "risk", "risky", "hospital",
            "healthcare", "infrastructure", "demographic", "population",
            "elderly", "poverty", "disability", "isolation", "compound"
        ]
        
        score = sum(1 for kw in vulnerability_keywords if kw in query) / len(vulnerability_keywords)
        score = min(score * 3, 1.0)
        
        return TaskResult(
            status=TaskStatus.SUCCESS,
            data={"agent": "vulnerability", "score": round(score, 3)},
            message=f"Vulnerability intent score: {score:.3f}"
        )
    
    def _classify_realtime_intent(self, context: Dict[str, Any]) -> TaskResult:
        """Classify real-time alert intent."""
        query = context.get("query", "").lower()
        
        realtime_keywords = [
            "alert", "warning", "current", "now", "today", "active",
            "happening", "storm", "tornado", "flood warning", "emergency"
        ]
        
        score = sum(1 for kw in realtime_keywords if kw in query) / len(realtime_keywords)
        score = min(score * 3, 1.0)
        
        return TaskResult(
            status=TaskStatus.SUCCESS,
            data={"agent": "realtime", "score": round(score, 3)},
            message=f"Realtime intent score: {score:.3f}"
        )
    
    def _classify_planning_intent(self, context: Dict[str, Any]) -> TaskResult:
        """Classify planning/intervention intent."""
        query = context.get("query", "").lower()
        
        planning_keywords = [
            "plan", "planning", "intervention", "roi", "cost", "effective",
            "recommendation", "strategy", "forecast", "predict", "future",
            "improve", "mitigate", "reduce risk"
        ]
        
        score = sum(1 for kw in planning_keywords if kw in query) / len(planning_keywords)
        score = min(score * 3, 1.0)
        
        return TaskResult(
            status=TaskStatus.SUCCESS,
            data={"agent": "planning", "score": round(score, 3)},
            message=f"Planning intent score: {score:.3f}"
        )
    
    def _select_agents(self, context: Dict[str, Any]) -> TaskResult:
        """Select agents based on intent scores."""
        # Collect scores from upstream tasks
        scores = {}
        for task_name in ["classify_climate", "classify_vulnerability", 
                          "classify_realtime", "classify_planning"]:
            if task_name in context:
                task_data = context[task_name].get("data", {})
                agent = task_data.get("agent")
                score = task_data.get("score", 0)
                if agent and score >= self.config.intent_classification_threshold:
                    scores[agent] = score
        
        if not scores:
            # Default to vulnerability
            scores = {"vulnerability": 0.5}
        
        # Sort by score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_scores[0][0]
        primary_score = sorted_scores[0][1]
        
        # Determine secondary agents
        secondary = []
        if self.config.enable_multi_agent and len(sorted_scores) > 1:
            for agent, score in sorted_scores[1:]:
                if (primary_score - score) < self.config.multi_agent_threshold:
                    secondary.append(agent)
        
        return TaskResult(
            status=TaskStatus.SUCCESS,
            data={
                "primary_agent": primary,
                "primary_score": primary_score,
                "secondary_agents": secondary,
                "all_scores": scores,
                "multi_agent": len(secondary) > 0
            },
            message=f"Selected primary: {primary}, secondary: {secondary}"
        )
    
    def _execute_climate_agent(self, context: Dict[str, Any]) -> TaskResult:
        """Execute climate agent."""
        from src.agents.climate_agent import ClimateAgent
        
        try:
            agent = ClimateAgent()
            query = context.get("query_intake", {}).get("data", {}).get("query", "")
            result = agent.execute(query, context)
            
            return TaskResult(
                status=TaskStatus.SUCCESS,
                data={"agent": "climate", "output": result},
                message="Climate agent executed successfully"
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                message="Climate agent execution failed"
            )
    
    def _execute_vulnerability_agent(self, context: Dict[str, Any]) -> TaskResult:
        """Execute vulnerability agent."""
        from src.agents.vulnerability_agent import VulnerabilityAgent
        
        try:
            agent = VulnerabilityAgent()
            query = context.get("query_intake", {}).get("data", {}).get("query", "")
            result = agent.execute(query, context)
            
            return TaskResult(
                status=TaskStatus.SUCCESS,
                data={"agent": "vulnerability", "output": result},
                message="Vulnerability agent executed successfully"
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                message="Vulnerability agent execution failed"
            )
    
    def _execute_realtime_agent(self, context: Dict[str, Any]) -> TaskResult:
        """Execute realtime agent."""
        from src.agents.realtime_agent import RealtimeAgent
        
        try:
            agent = RealtimeAgent()
            query = context.get("query_intake", {}).get("data", {}).get("query", "")
            result = agent.execute(query, context)
            
            return TaskResult(
                status=TaskStatus.SUCCESS,
                data={"agent": "realtime", "output": result},
                message="Realtime agent executed successfully"
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                message="Realtime agent execution failed"
            )
    
    def _execute_planning_agent(self, context: Dict[str, Any]) -> TaskResult:
        """Execute planning agent."""
        from src.agents.planning_agent import PlanningAgent
        
        try:
            agent = PlanningAgent()
            query = context.get("query_intake", {}).get("data", {}).get("query", "")
            result = agent.execute(query, context)
            
            return TaskResult(
                status=TaskStatus.SUCCESS,
                data={"agent": "planning", "output": result},
                message="Planning agent executed successfully"
            )
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                message="Planning agent execution failed"
            )
    
    def _synthesize_results(self, context: Dict[str, Any]) -> TaskResult:
        """Synthesize results from all executed agents."""
        outputs = {}
        
        for agent in ["climate", "vulnerability", "realtime", "planning"]:
            task_name = f"execute_{agent}"
            if task_name in context:
                task_data = context[task_name].get("data", {})
                if task_data.get("agent") == agent:
                    outputs[agent] = task_data.get("output", {})
        
        # Generate cross-domain insights
        insights = self._generate_insights(outputs)
        
        # Generate follow-up queries
        follow_ups = self._generate_follow_ups(context.get("query_intake", {}).get("data", {}).get("query", ""), outputs)
        
        return TaskResult(
            status=TaskStatus.SUCCESS,
            data={
                "outputs": outputs,
                "insights": insights,
                "follow_up_queries": follow_ups
            },
            message=f"Synthesized results from {len(outputs)} agents"
        )
    
    def _format_response(self, context: Dict[str, Any]) -> TaskResult:
        """Format final response."""
        synthesis = context.get("synthesize_results", {}).get("data", {})
        
        outputs = synthesis.get("outputs", {})
        insights = synthesis.get("insights", [])
        follow_ups = synthesis.get("follow_up_queries", [])
        
        # Build response
        response_parts = []
        
        for agent, output in outputs.items():
            if isinstance(output, dict) and "response" in output:
                response_parts.append(output["response"])
        
        response = "\n\n".join(response_parts)
        
        if insights:
            response += "\n\n**Cross-Domain Insights:**\n"
            for insight in insights:
                response += f"• {insight}\n"
        
        return TaskResult(
            status=TaskStatus.SUCCESS,
            data={
                "response": response,
                "insights": insights,
                "follow_up_queries": follow_ups,
                "agents_used": list(outputs.keys())
            },
            message="Response formatted successfully"
        )
    
    # Branch condition functions
    def _should_execute_climate(self, context: Dict[str, Any]) -> bool:
        """Determine if climate agent should execute."""
        selection = context.get("agent_selection", {}).get("data", {})
        primary = selection.get("primary_agent")
        secondary = selection.get("secondary_agents", [])
        return primary == "climate" or "climate" in secondary
    
    def _should_execute_vulnerability(self, context: Dict[str, Any]) -> bool:
        """Determine if vulnerability agent should execute."""
        selection = context.get("agent_selection", {}).get("data", {})
        primary = selection.get("primary_agent")
        secondary = selection.get("secondary_agents", [])
        return primary == "vulnerability" or "vulnerability" in secondary
    
    def _should_execute_realtime(self, context: Dict[str, Any]) -> bool:
        """Determine if realtime agent should execute."""
        selection = context.get("agent_selection", {}).get("data", {})
        primary = selection.get("primary_agent")
        secondary = selection.get("secondary_agents", [])
        return primary == "realtime" or "realtime" in secondary
    
    def _should_execute_planning(self, context: Dict[str, Any]) -> bool:
        """Determine if planning agent should execute."""
        selection = context.get("agent_selection", {}).get("data", {})
        primary = selection.get("primary_agent")
        secondary = selection.get("secondary_agents", [])
        return primary == "planning" or "planning" in secondary
    
    def _generate_insights(self, outputs: Dict[str, Any]) -> List[str]:
        """Generate cross-domain insights."""
        insights = []
        
        if "climate" in outputs and "vulnerability" in outputs:
            insights.append(
                "Climate projections combined with vulnerability patterns "
                "reveal potential compound risk scenarios."
            )
        
        if "realtime" in outputs and "vulnerability" in outputs:
            insights.append(
                "Weather alerts are weighted by underlying county vulnerability "
                "for enhanced risk assessment."
            )
        
        if "planning" in outputs and "climate" in outputs:
            insights.append(
                "Climate scenarios inform long-term intervention planning "
                "and ROI projections."
            )
        
        return insights
    
    def _generate_follow_ups(self, query: str, outputs: Dict[str, Any]) -> List[str]:
        """Generate follow-up query suggestions."""
        suggestions = []
        
        if "county" in query.lower():
            suggestions.append("What interventions would be most cost-effective for this county?")
            suggestions.append("How does this county compare to state averages?")
        
        if "state" in query.lower():
            suggestions.append("Which counties in this state have the highest compound risk?")
        
        if not suggestions:
            suggestions = [
                "Which counties have the highest compound risk?",
                "Show me counties with zero hospital redundancy.",
                "What are the current weather alerts for Missouri?"
            ]
        
        return suggestions[:3]
    
    def get_dag(self) -> DAG:
        """Get the compiled DAG."""
        return self.dag


# Agent Pipeline DAG Visualization
"""
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Agent Pipeline DAG Visualization                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Stage 1: Query Intake                                                       │
│  ╔═══════════════════════════════════════════════════════════╗              │
│  ║                  query_intake [Task]                      ║              │
│  ╚═══════════════════════════╤═══════════════════════════════╝              │
│                              │                                               │
│                              ▼                                               │
│  Stage 2: Intent Classification (Parallel)                                   │
│  ╔═════════════════╗  ╔═════════════════╗  ╔═════════════════╗              │
│  ║ classify_climate║  ║classify_vulnerab║  ║ classify_realtime             │
│  ║     [Task]      ║  ║    ility[Task]  ║  ║     [Task]      ║              │
│  ╚════════╤════════╝  ╚════════╤════════╝  ╚════════╤════════╝              │
│           │                    │                    │                        │
│           │         ╔══════════╧══════════╗         │                        │
│           │         ║ classify_planning   ║         │                        │
│           │         ║       [Task]        ║         │                        │
│           │         ╚══════════╤══════════╝         │                        │
│           │                    │                    │                        │
│           └────────────────────┼────────────────────┘                        │
│                                ▼                                             │
│  Stage 3: Agent Selection                                                    │
│  ╔═══════════════════════════════════════════════════════════╗              │
│  ║                 agent_selection [Task]                    ║              │
│  ╚═══════════════════════════╤═══════════════════════════════╝              │
│                              │                                               │
│              ┌───────────────┼───────────────┐                              │
│              ▼               ▼               ▼                              │
│  Stage 4: Agent Execution (Conditional)                                      │
│  ╔═════════════════╗  ╔═════════════════╗  ╔═════════════════╗              │
│  ║ execute_climate ║  ║execute_vulnerab ║  ║ execute_realtime║              │
│  ║    [Task]       ║  ║    ility[Task]  ║  ║     [Task]      ║              │
│  ║   [Branch]      ║  ║    [Branch]     ║  ║    [Branch]     ║              │
│  ╚════════╤════════╝  ╚════════╤════════╝  ╚════════╤════════╝              │
│           │                    │                    │                        │
│           │         ╔══════════╧══════════╗         │                        │
│           │         ║  execute_planning   ║         │                        │
│           │         ║       [Task]        ║         │                        │
│           │         ║      [Branch]       ║         │                        │
│           │         ╚══════════╤══════════╝         │                        │
│           │                    │                    │                        │
│           └────────────────────┼────────────────────┘                        │
│                                ▼                                             │
│  Stage 5: Result Synthesis                                                   │
│  ╔═══════════════════════════════════════════════════════════╗              │
│  ║               synthesize_results [Task]                   ║              │
│  ╚═══════════════════════════╤═══════════════════════════════╝              │
│                              │                                               │
│                              ▼                                               │
│  Stage 6: Response Formatting                                                │
│  ╔═══════════════════════════════════════════════════════════╗              │
│  ║                format_response [Task]                     ║              │
│  ╚═══════════════════════════════════════════════════════════╝              │
│                                                                              │
│  Legend: [Task] = Task, [Branch] = Conditional Branch, ───▶ = Dependency    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
"""


---

## 4. Core Orchestration Components

### 4.1 DAG Core Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/orchestration/core/dag.py

"""
Core DAG (Directed Acyclic Graph) implementation for workflow orchestration.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum, auto
import json
import hashlib
from collections import defaultdict
import graphviz


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    SKIPPED = auto()
    UPSTREAM_FAILED = auto()
    RETRYING = auto()


class TriggerRule(Enum):
    """Task trigger rules."""
    ALL_SUCCESS = auto()      # All upstream tasks must succeed
    ALL_FAILED = auto()       # All upstream tasks must fail
    ALL_DONE = auto()         # All upstream tasks must complete (any status)
    ONE_SUCCESS = auto()      # At least one upstream task must succeed
    ONE_FAILED = auto()       # At least one upstream task must fail
    NONE_FAILED = auto()      # No upstream tasks failed
    NONE_SKIPPED = auto()     # No upstream tasks skipped
    ALWAYS = auto()           # Always trigger


@dataclass
class TaskResult:
    """Result of task execution."""
    status: TaskStatus
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    message: str = ""
    execution_time_ms: float = 0.0
    retry_count: int = 0


@dataclass
class Task:
    """Task definition for DAG execution."""
    name: str
    task_type: str  # 'python', 'bash', 'http', 'sensor'
    python_callable: Optional[Callable] = None
    bash_command: Optional[str] = None
    http_endpoint: Optional[str] = None
    retries: int = 0
    retry_delay: timedelta = field(default_factory=lambda: timedelta(seconds=0))
    retry_exponential_backoff: bool = False
    max_retry_delay: Optional[timedelta] = None
    timeout: int = 300
    trigger_rule: TriggerRule = TriggerRule.ALL_SUCCESS
    pool: Optional[str] = None
    pool_slots: int = 1
    priority_weight: int = 1
    queue: str = "default"
    resources: Dict[str, Any] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    depends_on_past: bool = False
    wait_for_downstream: bool = False
    
    def __post_init__(self):
        self.task_id = self._generate_task_id()
        self.created_at = datetime.utcnow()
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID."""
        content = f"{self.name}_{self.created_at.isoformat() if hasattr(self, 'created_at') else datetime.utcnow().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def execute(self, context: Dict[str, Any]) -> TaskResult:
        """Execute the task."""
        import time
        start_time = time.time()
        
        try:
            if self.task_type == "python" and self.python_callable:
                result = self.python_callable(context)
                if not isinstance(result, TaskResult):
                    result = TaskResult(
                        status=TaskStatus.SUCCESS,
                        data={"result": result},
                        message="Task completed successfully"
                    )
            elif self.task_type == "bash" and self.bash_command:
                import subprocess
                result = subprocess.run(
                    self.bash_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                if result.returncode == 0:
                    result = TaskResult(
                        status=TaskStatus.SUCCESS,
                        data={"stdout": result.stdout},
                        message="Bash command completed"
                    )
                else:
                    result = TaskResult(
                        status=TaskStatus.FAILED,
                        error=result.stderr,
                        message="Bash command failed"
                    )
            else:
                result = TaskResult(
                    status=TaskStatus.FAILED,
                    error="Invalid task configuration",
                    message="Task type or callable not specified"
                )
            
            result.execution_time_ms = (time.time() - start_time) * 1000
            return result
            
        except Exception as e:
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                message=f"Task execution failed: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000
            )


@dataclass
class BranchCondition:
    """Conditional branch for task execution."""
    condition: Callable[[Dict[str, Any]], bool]
    description: str = ""


@dataclass
class DAG:
    """Directed Acyclic Graph for workflow orchestration."""
    name: str
    description: str = ""
    schedule_interval: Optional[str] = None  # Cron expression
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    catchup: bool = False
    max_active_runs: int = 1
    concurrency: int = 16
    default_args: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    default_retry_policy: Optional[Any] = None
    
    def __post_init__(self):
        self.tasks: Dict[str, Task] = {}
        self.dependencies: Dict[str, List[str]] = defaultdict(list)
        self.downstream: Dict[str, List[str]] = defaultdict(list)
        self.branch_conditions: Dict[str, BranchCondition] = {}
        self.created_at = datetime.utcnow()
        self.version = "1.0.0"
    
    def add_task(self, task: Task) -> 'DAG':
        """Add a task to the DAG."""
        if task.name in self.tasks:
            raise ValueError(f"Task '{task.name}' already exists in DAG")
        self.tasks[task.name] = task
        return self
    
    def add_tasks(self, tasks: List[Task]) -> 'DAG':
        """Add multiple tasks to the DAG."""
        for task in tasks:
            self.add_task(task)
        return self
    
    def add_dependency(self, task: Union[Task, str], upstream: Union[Task, str, List[Union[Task, str]]]) -> 'DAG':
        """Add a dependency between tasks."""
        task_name = task.name if isinstance(task, Task) else task
        
        if isinstance(upstream, list):
            for up in upstream:
                up_name = up.name if isinstance(up, Task) else up
                self.dependencies[task_name].append(up_name)
                self.downstream[up_name].append(task_name)
        else:
            up_name = upstream.name if isinstance(upstream, Task) else upstream
            self.dependencies[task_name].append(up_name)
            self.downstream[up_name].append(task_name)
        
        # Check for cycles
        if self._has_cycle():
            raise ValueError("Adding this dependency would create a cycle in the DAG")
        
        return self
    
    def add_branch_condition(self, task: Union[Task, str], condition: Callable[[Dict[str, Any]], bool]) -> 'DAG':
        """Add a conditional branch for task execution."""
        task_name = task.name if isinstance(task, Task) else task
        self.branch_conditions[task_name] = BranchCondition(
            condition=condition,
            description=f"Branch condition for {task_name}"
        )
        return self
    
    def _has_cycle(self) -> bool:
        """Check if the DAG has a cycle using DFS."""
        visited = set()
        rec_stack = set()
        
        def has_cycle_util(task_name: str) -> bool:
            visited.add(task_name)
            rec_stack.add(task_name)
            
            for dep in self.dependencies.get(task_name, []):
                if dep not in visited:
                    if has_cycle_util(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(task_name)
            return False
        
        for task_name in self.tasks:
            if task_name not in visited:
                if has_cycle_util(task_name):
                    return True
        
        return False
    
    def get_upstream_tasks(self, task_name: str) -> List[str]:
        """Get all upstream tasks for a given task."""
        return self.dependencies.get(task_name, [])
    
    def get_downstream_tasks(self, task_name: str) -> List[str]:
        """Get all downstream tasks for a given task."""
        return self.downstream.get(task_name, [])
    
    def get_root_tasks(self) -> List[str]:
        """Get tasks with no dependencies (root tasks)."""
        return [name for name in self.tasks if not self.dependencies.get(name)]
    
    def get_leaf_tasks(self) -> List[str]:
        """Get tasks with no downstream tasks (leaf tasks)."""
        return [name for name in self.tasks if not self.downstream.get(name)]
    
    def topological_sort(self) -> List[str]:
        """Return tasks in topological order."""
        in_degree = {name: len(self.dependencies.get(name, [])) for name in self.tasks}
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            task_name = queue.pop(0)
            result.append(task_name)
            
            for downstream in self.downstream.get(task_name, []):
                in_degree[downstream] -= 1
                if in_degree[downstream] == 0:
                    queue.append(downstream)
        
        if len(result) != len(self.tasks):
            raise ValueError("DAG has a cycle")
        
        return result
    
    def get_execution_levels(self) -> List[List[str]]:
        """Group tasks by execution level for parallel execution."""
        levels = []
        remaining = set(self.tasks.keys())
        completed = set()
        
        while remaining:
            current_level = []
            for task_name in list(remaining):
                deps = set(self.dependencies.get(task_name, []))
                if deps <= completed:
                    current_level.append(task_name)
            
            if not current_level:
                raise ValueError("Cannot determine execution levels - possible cycle")
            
            levels.append(current_level)
            completed.update(current_level)
            remaining -= set(current_level)
        
        return levels
    
    def should_execute_task(self, task_name: str, context: Dict[str, Any]) -> bool:
        """Check if a task should execute based on branch conditions."""
        if task_name not in self.branch_conditions:
            return True
        
        condition = self.branch_conditions[task_name]
        try:
            return condition.condition(context)
        except Exception as e:
            # Log error and default to executing
            return True
    
    def visualize(self, output_path: str = None) -> str:
        """Generate a visual representation of the DAG."""
        dot = graphviz.Digraph(comment=self.name)
        dot.attr(rankdir='TB')
        dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
        
        # Add nodes
        for task_name in self.tasks:
            if task_name in self.branch_conditions:
                dot.node(task_name, f"{task_name}\n[Branch]", fillcolor='lightyellow')
            else:
                dot.node(task_name, task_name)
        
        # Add edges
        for task_name, upstream_tasks in self.dependencies.items():
            for upstream in upstream_tasks:
                dot.edge(upstream, task_name)
        
        if output_path:
            dot.render(output_path, format='png', cleanup=True)
        
        return dot.source
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DAG to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "schedule_interval": self.schedule_interval,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "catchup": self.catchup,
            "max_active_runs": self.max_active_runs,
            "concurrency": self.concurrency,
            "tasks": [
                {
                    "name": task.name,
                    "task_type": task.task_type,
                    "retries": task.retries,
                    "timeout": task.timeout,
                    "trigger_rule": task.trigger_rule.name
                }
                for task in self.tasks.values()
            ],
            "dependencies": dict(self.dependencies),
            "created_at": self.created_at.isoformat()
        }
    
    def to_json(self) -> str:
        """Convert DAG to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


# Example usage
if __name__ == "__main__":
    # Create a simple DAG
    dag = DAG(
        name="example_pipeline",
        description="Example data pipeline",
        schedule_interval="0 0 * * *"
    )
    
    # Create tasks
    task_a = Task(name="task_a", task_type="python", python_callable=lambda ctx: TaskResult(TaskStatus.SUCCESS))
    task_b = Task(name="task_b", task_type="python", python_callable=lambda ctx: TaskResult(TaskStatus.SUCCESS))
    task_c = Task(name="task_c", task_type="python", python_callable=lambda ctx: TaskResult(TaskStatus.SUCCESS))
    
    # Add tasks and dependencies
    dag.add_tasks([task_a, task_b, task_c])
    dag.add_dependency(task_b, task_a)
    dag.add_dependency(task_c, [task_a, task_b])
    
    # Print topological sort
    print("Topological order:", dag.topological_sort())
    
    # Print execution levels
    print("Execution levels:", dag.get_execution_levels())
    
    # Generate visualization
    print("\nDOT representation:")
    print(dag.visualize())
```

### 4.2 State Management

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/orchestration/core/state.py

"""
State management for workflow orchestration.
Supports multiple backends: memory, file, database, Redis.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
import json
import pickle
from pathlib import Path
import sqlite3
from contextlib import contextmanager


class StateBackend(Enum):
    """State storage backends."""
    MEMORY = auto()
    FILE = auto()
    SQLITE = auto()
    REDIS = auto()
    POSTGRES = auto()


@dataclass
class WorkflowState:
    """Complete state of a workflow execution."""
    workflow_id: str
    dag_name: str
    run_id: str
    status: str  # 'running', 'success', 'failed', 'paused'
    start_time: datetime
    end_time: Optional[datetime] = None
    task_states: Dict[str, 'TaskState'] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "dag_name": self.dag_name,
            "run_id": self.run_id,
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "task_states": {k: v.to_dict() for k, v in self.task_states.items()},
            "context": self.context,
            "metadata": self.metadata
        }


@dataclass
class TaskState:
    """State of a single task execution."""
    task_name: str
    status: str  # 'pending', 'running', 'success', 'failed', 'skipped', 'retrying'
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    retry_count: int = 0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_name": self.task_name,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "retry_count": self.retry_count,
            "result": self.result,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms
        }


class StateManager:
    """Manages workflow and task state."""
    
    def __init__(self, backend: StateBackend = StateBackend.MEMORY, 
                 connection_string: str = None):
        self.backend = backend
        self.connection_string = connection_string
        
        # Initialize backend
        if backend == StateBackend.MEMORY:
            self._memory_store: Dict[str, WorkflowState] = {}
        elif backend == StateBackend.FILE:
            self._file_path = Path(connection_string or "./state")
            self._file_path.mkdir(parents=True, exist_ok=True)
        elif backend == StateBackend.SQLITE:
            self._db_path = connection_string or "./state.db"
            self._init_sqlite()
        elif backend == StateBackend.REDIS:
            import redis
            self._redis = redis.from_url(connection_string or "redis://localhost:6379")
    
    def _init_sqlite(self):
        """Initialize SQLite database."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workflow_states (
                    workflow_id TEXT PRIMARY KEY,
                    dag_name TEXT,
                    run_id TEXT,
                    status TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    state_data BLOB
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_states (
                    workflow_id TEXT,
                    task_name TEXT,
                    status TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    state_data BLOB,
                    PRIMARY KEY (workflow_id, task_name)
                )
            """)
            conn.commit()
    
    def save_workflow_state(self, state: WorkflowState):
        """Save workflow state."""
        if self.backend == StateBackend.MEMORY:
            self._memory_store[state.workflow_id] = state
        
        elif self.backend == StateBackend.FILE:
            file_path = self._file_path / f"{state.workflow_id}.pkl"
            with open(file_path, 'wb') as f:
                pickle.dump(state, f)
        
        elif self.backend == StateBackend.SQLITE:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO workflow_states 
                    (workflow_id, dag_name, run_id, status, start_time, end_time, state_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        state.workflow_id,
                        state.dag_name,
                        state.run_id,
                        state.status,
                        state.start_time.isoformat(),
                        state.end_time.isoformat() if state.end_time else None,
                        pickle.dumps(state)
                    )
                )
                conn.commit()
        
        elif self.backend == StateBackend.REDIS:
            self._redis.set(
                f"workflow:{state.workflow_id}",
                pickle.dumps(state),
                ex=86400 * 7  # 7 days TTL
            )
    
    def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get workflow state by ID."""
        if self.backend == StateBackend.MEMORY:
            return self._memory_store.get(workflow_id)
        
        elif self.backend == StateBackend.FILE:
            file_path = self._file_path / f"{workflow_id}.pkl"
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
            return None
        
        elif self.backend == StateBackend.SQLITE:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute(
                    "SELECT state_data FROM workflow_states WHERE workflow_id = ?",
                    (workflow_id,)
                )
                row = cursor.fetchone()
                if row:
                    return pickle.loads(row[0])
                return None
        
        elif self.backend == StateBackend.REDIS:
            data = self._redis.get(f"workflow:{workflow_id}")
            if data:
                return pickle.loads(data)
            return None
    
    def save_task_state(self, workflow_id: str, state: TaskState):
        """Save task state."""
        workflow_state = self.get_workflow_state(workflow_id)
        if workflow_state:
            workflow_state.task_states[state.task_name] = state
            self.save_workflow_state(workflow_state)
    
    def get_task_state(self, workflow_id: str, task_name: str) -> Optional[TaskState]:
        """Get task state."""
        workflow_state = self.get_workflow_state(workflow_id)
        if workflow_state:
            return workflow_state.task_states.get(task_name)
        return None
    
    def list_workflows(self, dag_name: str = None, status: str = None) -> List[WorkflowState]:
        """List workflow states with optional filtering."""
        workflows = []
        
        if self.backend == StateBackend.MEMORY:
            for state in self._memory_store.values():
                if (dag_name is None or state.dag_name == dag_name) and \
                   (status is None or state.status == status):
                    workflows.append(state)
        
        elif self.backend == StateBackend.SQLITE:
            with sqlite3.connect(self._db_path) as conn:
                query = "SELECT state_data FROM workflow_states WHERE 1=1"
                params = []
                if dag_name:
                    query += " AND dag_name = ?"
                    params.append(dag_name)
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                cursor = conn.execute(query, params)
                for row in cursor.fetchall():
                    workflows.append(pickle.loads(row[0]))
        
        return workflows
    
    def delete_workflow_state(self, workflow_id: str):
        """Delete workflow state."""
        if self.backend == StateBackend.MEMORY:
            self._memory_store.pop(workflow_id, None)
        
        elif self.backend == StateBackend.FILE:
            file_path = self._file_path / f"{workflow_id}.pkl"
            if file_path.exists():
                file_path.unlink()
        
        elif self.backend == StateBackend.SQLITE:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute("DELETE FROM workflow_states WHERE workflow_id = ?", (workflow_id,))
                conn.execute("DELETE FROM task_states WHERE workflow_id = ?", (workflow_id,))
                conn.commit()
        
        elif self.backend == StateBackend.REDIS:
            self._redis.delete(f"workflow:{workflow_id}")


# XCom (Cross-Communication) for task data sharing
class XComManager:
    """Manages cross-task communication (XCom)."""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
    
    def push(self, workflow_id: str, task_name: str, key: str, value: Any):
        """Push data to XCom."""
        workflow_state = self.state_manager.get_workflow_state(workflow_id)
        if workflow_state:
            if "xcom" not in workflow_state.context:
                workflow_state.context["xcom"] = {}
            if task_name not in workflow_state.context["xcom"]:
                workflow_state.context["xcom"][task_name] = {}
            workflow_state.context["xcom"][task_name][key] = value
            self.state_manager.save_workflow_state(workflow_state)
    
    def pull(self, workflow_id: str, task_name: str, key: str) -> Any:
        """Pull data from XCom."""
        workflow_state = self.state_manager.get_workflow_state(workflow_id)
        if workflow_state and "xcom" in workflow_state.context:
            return workflow_state.context["xcom"].get(task_name, {}).get(key)
        return None
    
    def pull_from_upstream(self, workflow_id: str, upstream_task: str, key: str) -> Any:
        """Pull data from an upstream task."""
        return self.pull(workflow_id, upstream_task, key)
```


### 4.3 Retry Mechanisms

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/orchestration/retry/policies.py

"""
Retry policies for workflow orchestration.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Type
import random
import time


class RetryPolicy(ABC):
    """Abstract base class for retry policies."""
    
    @abstractmethod
    def get_delay(self, retry_count: int) -> float:
        """Get the delay before the next retry attempt."""
        pass
    
    @abstractmethod
    def should_retry(self, retry_count: int, exception: Exception) -> bool:
        """Determine if another retry should be attempted."""
        pass


@dataclass
class FixedDelayRetry(RetryPolicy):
    """Retry with fixed delay between attempts."""
    max_retries: int = 3
    delay: float = 5.0
    retryable_exceptions: Optional[List[Type[Exception]]] = None
    
    def get_delay(self, retry_count: int) -> float:
        return self.delay
    
    def should_retry(self, retry_count: int, exception: Exception) -> bool:
        if retry_count >= self.max_retries:
            return False
        
        if self.retryable_exceptions:
            return any(isinstance(exception, exc_type) for exc_type in self.retryable_exceptions)
        
        return True


@dataclass
class LinearRetry(RetryPolicy):
    """Retry with linearly increasing delay."""
    max_retries: int = 3
    base_delay: float = 1.0
    increment: float = 2.0
    max_delay: Optional[float] = None
    retryable_exceptions: Optional[List[Type[Exception]]] = None
    
    def get_delay(self, retry_count: int) -> float:
        delay = self.base_delay + (retry_count * self.increment)
        if self.max_delay:
            delay = min(delay, self.max_delay)
        return delay
    
    def should_retry(self, retry_count: int, exception: Exception) -> bool:
        if retry_count >= self.max_retries:
            return False
        
        if self.retryable_exceptions:
            return any(isinstance(exception, exc_type) for exc_type in self.retryable_exceptions)
        
        return True


@dataclass
class ExponentialBackoffRetry(RetryPolicy):
    """Retry with exponential backoff."""
    max_retries: int = 3
    base_delay: float = 1.0
    exponential_base: float = 2.0
    max_delay: Optional[float] = None
    jitter: bool = True
    retryable_exceptions: Optional[List[Type[Exception]]] = None
    
    def get_delay(self, retry_count: int) -> float:
        delay = self.base_delay * (self.exponential_base ** retry_count)
        
        if self.jitter:
            # Add random jitter (±25%)
            jitter_amount = delay * 0.25
            delay = delay + random.uniform(-jitter_amount, jitter_amount)
        
        if self.max_delay:
            delay = min(delay, self.max_delay)
        
        return max(0, delay)
    
    def should_retry(self, retry_count: int, exception: Exception) -> bool:
        if retry_count >= self.max_retries:
            return False
        
        if self.retryable_exceptions:
            return any(isinstance(exception, exc_type) for exc_type in self.retryable_exceptions)
        
        return True


@dataclass
class FibonacciRetry(RetryPolicy):
    """Retry with Fibonacci sequence delays."""
    max_retries: int = 5
    base_delay: float = 1.0
    max_delay: Optional[float] = None
    retryable_exceptions: Optional[List[Type[Exception]]] = None
    
    def _fibonacci(self, n: int) -> int:
        """Calculate nth Fibonacci number."""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    def get_delay(self, retry_count: int) -> float:
        delay = self.base_delay * self._fibonacci(retry_count + 1)
        if self.max_delay:
            delay = min(delay, self.max_delay)
        return delay
    
    def should_retry(self, retry_count: int, exception: Exception) -> bool:
        if retry_count >= self.max_retries:
            return False
        
        if self.retryable_exceptions:
            return any(isinstance(exception, exc_type) for exc_type in self.retryable_exceptions)
        
        return True


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "half-open"
                return True
            return False
        
        return True  # half-open
    
    def record_success(self):
        """Record a successful execution."""
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        """Record a failed execution."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
    
    def __call__(self, func):
        """Decorator for circuit breaker."""
        def wrapper(*args, **kwargs):
            if not self.can_execute():
                raise Exception("Circuit breaker is open")
            
            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result
            except self.expected_exception:
                self.record_failure()
                raise
        
        return wrapper


# Retry executor
class RetryExecutor:
    """Execute tasks with retry logic."""
    
    def __init__(self, policy: RetryPolicy):
        self.policy = policy
    
    def execute(self, func, *args, **kwargs):
        """Execute function with retry logic."""
        retry_count = 0
        last_exception = None
        
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if not self.policy.should_retry(retry_count, e):
                    break
                
                delay = self.policy.get_delay(retry_count)
                time.sleep(delay)
                retry_count += 1
        
        raise last_exception


# Example usage
if __name__ == "__main__":
    # Exponential backoff retry
    retry_policy = ExponentialBackoffRetry(
        max_retries=3,
        base_delay=1.0,
        exponential_base=2.0,
        jitter=True
    )
    
    # Simulate a failing function
    def flaky_function():
        import random
        if random.random() < 0.7:
            raise Exception("Random failure")
        return "Success!"
    
    executor = RetryExecutor(retry_policy)
    try:
        result = executor.execute(flaky_function)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Failed after retries: {e}")
```

---

## 5. Workflow Scheduling

### 5.1 Scheduler Implementation

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/orchestration/schedulers/cron_scheduler.py

"""
Cron-based workflow scheduler.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from croniter import croniter
import threading
import time
from queue import PriorityQueue


@dataclass(order=True)
class ScheduledJob:
    """A scheduled job."""
    next_run_time: datetime
    dag_name: str = field(compare=False)
    schedule: str = field(compare=False)  # Cron expression
    last_run_time: Optional[datetime] = field(default=None, compare=False)
    max_runs: Optional[int] = field(default=None, compare=False)
    run_count: int = field(default=0, compare=False)
    job_id: str = field(default="", compare=False)
    
    def __post_init__(self):
        if not self.job_id:
            self.job_id = f"{self.dag_name}_{datetime.utcnow().timestamp()}"


class CronScheduler:
    """
    Cron-based workflow scheduler.
    
    Features:
    - Cron expression support
    - Priority queue for job execution
    - Concurrent job execution
    - Job history tracking
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.jobs: Dict[str, ScheduledJob] = {}
        self.job_queue = PriorityQueue()
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.executor_threads: List[threading.Thread] = []
        self.job_history: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._callbacks: Dict[str, Callable] = {}
    
    def schedule(self, dag_name: str, schedule: str, max_runs: int = None) -> str:
        """
        Schedule a DAG for execution.
        
        Args:
            dag_name: Name of the DAG to schedule
            schedule: Cron expression (e.g., "0 2 * * *" for daily at 2 AM)
            max_runs: Maximum number of executions (None for unlimited)
        
        Returns:
            Job ID
        """
        # Calculate next run time
        cron = croniter(schedule, datetime.utcnow())
        next_run = cron.get_next(datetime)
        
        job = ScheduledJob(
            next_run_time=next_run,
            dag_name=dag_name,
            schedule=schedule,
            max_runs=max_runs
        )
        
        with self._lock:
            self.jobs[job.job_id] = job
            self.job_queue.put(job)
        
        return job.job_id
    
    def unschedule(self, job_id: str) -> bool:
        """Remove a scheduled job."""
        with self._lock:
            if job_id in self.jobs:
                del self.jobs[job_id]
                return True
        return False
    
    def register_callback(self, dag_name: str, callback: Callable[[str], None]):
        """Register a callback for DAG execution."""
        self._callbacks[dag_name] = callback
    
    def start(self):
        """Start the scheduler."""
        if self.running:
            return
        
        self.running = True
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        # Start executor threads
        for i in range(self.max_workers):
            thread = threading.Thread(target=self._executor_loop, daemon=True)
            thread.start()
            self.executor_threads.append(thread)
        
        print(f"Scheduler started with {self.max_workers} workers")
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        for thread in self.executor_threads:
            thread.join(timeout=5)
        
        print("Scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.running:
            now = datetime.utcnow()
            
            with self._lock:
                # Check for jobs ready to run
                jobs_to_run = []
                temp_queue = PriorityQueue()
                
                while not self.job_queue.empty():
                    job = self.job_queue.get()
                    if job.next_run_time <= now:
                        jobs_to_run.append(job)
                    else:
                        temp_queue.put(job)
                
                # Restore jobs not ready yet
                while not temp_queue.empty():
                    self.job_queue.put(temp_queue.get())
                
                # Update and reschedule jobs that ran
                for job in jobs_to_run:
                    # Update job
                    job.last_run_time = now
                    job.run_count += 1
                    
                    # Calculate next run time
                    cron = croniter(job.schedule, now)
                    job.next_run_time = cron.get_next(datetime)
                    
                    # Check if job should continue
                    if job.max_runs is None or job.run_count < job.max_runs:
                        self.job_queue.put(job)
                    else:
                        del self.jobs[job.job_id]
                    
                    # Execute job
                    self._execute_job(job)
            
            time.sleep(1)  # Check every second
    
    def _executor_loop(self):
        """Executor thread loop."""
        while self.running:
            time.sleep(0.1)
    
    def _execute_job(self, job: ScheduledJob):
        """Execute a scheduled job."""
        print(f"Executing job: {job.dag_name} (run #{job.run_count})")
        
        # Record in history
        self.job_history.append({
            "job_id": job.job_id,
            "dag_name": job.dag_name,
            "run_time": job.last_run_time.isoformat(),
            "run_number": job.run_count
        })
        
        # Call registered callback
        if job.dag_name in self._callbacks:
            try:
                self._callbacks[job.dag_name](job.dag_name)
            except Exception as e:
                print(f"Error executing job {job.dag_name}: {e}")
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a scheduled job."""
        with self._lock:
            job = self.jobs.get(job_id)
            if job:
                return {
                    "job_id": job.job_id,
                    "dag_name": job.dag_name,
                    "schedule": job.schedule,
                    "next_run_time": job.next_run_time.isoformat(),
                    "last_run_time": job.last_run_time.isoformat() if job.last_run_time else None,
                    "run_count": job.run_count,
                    "max_runs": job.max_runs
                }
        return None
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all scheduled jobs."""
        with self._lock:
            return [
                {
                    "job_id": job.job_id,
                    "dag_name": job.dag_name,
                    "schedule": job.schedule,
                    "next_run_time": job.next_run_time.isoformat()
                }
                for job in self.jobs.values()
            ]
    
    def get_history(self, dag_name: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get job execution history."""
        history = self.job_history
        if dag_name:
            history = [h for h in history if h["dag_name"] == dag_name]
        return history[-limit:]


# Event-driven scheduler
class EventScheduler:
    """Event-driven workflow scheduler."""
    
    def __init__(self):
        self.event_handlers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
    
    def on(self, event_type: str, handler: Callable):
        """Register an event handler."""
        with self._lock:
            if event_type not in self.event_handlers:
                self.event_handlers[event_type] = []
            self.event_handlers[event_type].append(handler)
    
    def emit(self, event_type: str, data: Dict[str, Any] = None):
        """Emit an event."""
        with self._lock:
            handlers = self.event_handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                handler(data or {})
            except Exception as e:
                print(f"Error in event handler for {event_type}: {e}")
    
    def off(self, event_type: str, handler: Callable = None):
        """Unregister an event handler."""
        with self._lock:
            if event_type in self.event_handlers:
                if handler:
                    self.event_handlers[event_type] = [
                        h for h in self.event_handlers[event_type] if h != handler
                    ]
                else:
                    del self.event_handlers[event_type]


# Example usage
if __name__ == "__main__":
    # Create scheduler
    scheduler = CronScheduler(max_workers=2)
    
    # Register callback
    def on_dag_execute(dag_name: str):
        print(f"Executing DAG: {dag_name}")
    
    scheduler.register_callback("data_pipeline", on_dag_execute)
    
    # Schedule jobs
    job1 = scheduler.schedule("data_pipeline", "*/1 * * * *")  # Every minute
    print(f"Scheduled job: {job1}")
    
    # Start scheduler
    scheduler.start()
    
    # Run for a while
    try:
        time.sleep(130)  # Run for 2+ minutes
    except KeyboardInterrupt:
        pass
    
    # Stop scheduler
    scheduler.stop()
    
    # Print history
    print("\nJob History:")
    for entry in scheduler.get_history():
        print(f"  {entry['dag_name']} at {entry['run_time']}")
```


---

## 6. Parallel Execution

### 6.1 Parallel Executor

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/orchestration/core/executor.py

"""
Parallel execution engine for workflow orchestration.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from enum import Enum, auto
import threading
import multiprocessing
from queue import Queue, Empty
import time

from orchestration.core.dag import DAG, Task, TaskStatus, TaskResult
from orchestration.core.state import StateManager, WorkflowState, TaskState


class ExecutorType(Enum):
    """Types of executors."""
    THREAD = auto()
    PROCESS = auto()
    ASYNC = auto()


@dataclass
class ExecutionConfig:
    """Configuration for execution."""
    executor_type: ExecutorType = ExecutorType.THREAD
    max_workers: int = 4
    timeout: int = 300
    fail_fast: bool = False
    continue_on_error: bool = True


class ParallelExecutor:
    """
    Parallel execution engine for DAGs.
    
    Features:
    - Multi-threaded execution
    - Multi-process execution
    - Async/await support
    - Dependency-aware scheduling
    - State management
    """
    
    def __init__(self, config: ExecutionConfig = None, 
                 state_manager: StateManager = None):
        self.config = config or ExecutionConfig()
        self.state_manager = state_manager or StateManager()
        self._execution_count = 0
        self._lock = threading.Lock()
    
    def execute_dag(self, dag: DAG, initial_context: Dict[str, Any] = None) -> WorkflowState:
        """
        Execute a DAG with parallel task execution.
        
        Args:
            dag: The DAG to execute
            initial_context: Initial context for execution
        
        Returns:
            Final workflow state
        """
        # Create workflow state
        workflow_id = self._generate_workflow_id(dag.name)
        workflow_state = WorkflowState(
            workflow_id=workflow_id,
            dag_name=dag.name,
            run_id=workflow_id,
            status="running",
            start_time=datetime.utcnow(),
            context=initial_context or {}
        )
        
        # Save initial state
        self.state_manager.save_workflow_state(workflow_state)
        
        try:
            # Get execution levels (tasks grouped by dependencies)
            execution_levels = dag.get_execution_levels()
            
            # Execute each level
            for level in execution_levels:
                self._execute_level(dag, level, workflow_state)
                
                # Check for failures
                if self.config.fail_fast:
                    failed_tasks = [
                        name for name in level
                        if workflow_state.task_states.get(name, TaskState(task_name=name, status="pending")).status == "failed"
                    ]
                    if failed_tasks:
                        workflow_state.status = "failed"
                        workflow_state.end_time = datetime.utcnow()
                        self.state_manager.save_workflow_state(workflow_state)
                        return workflow_state
            
            # Mark as successful
            workflow_state.status = "success"
            workflow_state.end_time = datetime.utcnow()
            
        except Exception as e:
            workflow_state.status = "failed"
            workflow_state.end_time = datetime.utcnow()
            workflow_state.metadata["error"] = str(e)
        
        # Save final state
        self.state_manager.save_workflow_state(workflow_state)
        
        return workflow_state
    
    def _execute_level(self, dag: DAG, level: List[str], 
                       workflow_state: WorkflowState):
        """Execute all tasks in a level (in parallel)."""
        if self.config.executor_type == ExecutorType.THREAD:
            self._execute_level_threaded(dag, level, workflow_state)
        elif self.config.executor_type == ExecutorType.PROCESS:
            self._execute_level_multiprocess(dag, level, workflow_state)
        else:
            self._execute_level_async(dag, level, workflow_state)
    
    def _execute_level_threaded(self, dag: DAG, level: List[str], 
                                 workflow_state: WorkflowState):
        """Execute level using thread pool."""
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all tasks
            futures = {}
            for task_name in level:
                task = dag.tasks[task_name]
                
                # Check branch conditions
                if not dag.should_execute_task(task_name, workflow_state.context):
                    # Skip this task
                    task_state = TaskState(
                        task_name=task_name,
                        status="skipped"
                    )
                    workflow_state.task_states[task_name] = task_state
                    continue
                
                # Check trigger rule
                if not self._check_trigger_rule(dag, task, workflow_state):
                    task_state = TaskState(
                        task_name=task_name,
                        status="upstream_failed"
                    )
                    workflow_state.task_states[task_name] = task_state
                    continue
                
                # Submit task
                future = executor.submit(
                    self._execute_task,
                    task,
                    workflow_state
                )
                futures[future] = task_name
            
            # Collect results
            for future in as_completed(futures):
                task_name = futures[future]
                try:
                    result = future.result(timeout=self.config.timeout)
                    task_state = TaskState(
                        task_name=task_name,
                        status="success" if result.status == TaskStatus.SUCCESS else "failed",
                        result=result.data if result.status == TaskStatus.SUCCESS else None,
                        error=result.error if result.status == TaskStatus.FAILED else None,
                        execution_time_ms=result.execution_time_ms
                    )
                except Exception as e:
                    task_state = TaskState(
                        task_name=task_name,
                        status="failed",
                        error=str(e)
                    )
                
                workflow_state.task_states[task_name] = task_state
                
                # Update context with task result
                if task_state.status == "success" and task_state.result:
                    workflow_state.context[task_name] = task_state.result
                
                # Save state after each task
                self.state_manager.save_workflow_state(workflow_state)
    
    def _execute_level_multiprocess(self, dag: DAG, level: List[str], 
                                     workflow_state: WorkflowState):
        """Execute level using process pool."""
        with ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = {}
            for task_name in level:
                task = dag.tasks[task_name]
                
                if not dag.should_execute_task(task_name, workflow_state.context):
                    task_state = TaskState(
                        task_name=task_name,
                        status="skipped"
                    )
                    workflow_state.task_states[task_name] = task_state
                    continue
                
                # Submit task
                future = executor.submit(
                    self._execute_task_process,
                    task,
                    workflow_state.context
                )
                futures[future] = task_name
            
            # Collect results
            for future in as_completed(futures):
                task_name = futures[future]
                try:
                    result = future.result(timeout=self.config.timeout)
                    task_state = TaskState(
                        task_name=task_name,
                        status=result.get("status", "failed"),
                        result=result.get("data"),
                        error=result.get("error"),
                        execution_time_ms=result.get("execution_time_ms", 0)
                    )
                except Exception as e:
                    task_state = TaskState(
                        task_name=task_name,
                        status="failed",
                        error=str(e)
                    )
                
                workflow_state.task_states[task_name] = task_state
                self.state_manager.save_workflow_state(workflow_state)
    
    def _execute_level_async(self, dag: DAG, level: List[str], 
                              workflow_state: WorkflowState):
        """Execute level using async/await."""
        import asyncio
        
        async def run_async():
            tasks = []
            for task_name in level:
                task = dag.tasks[task_name]
                
                if not dag.should_execute_task(task_name, workflow_state.context):
                    task_state = TaskState(
                        task_name=task_name,
                        status="skipped"
                    )
                    workflow_state.task_states[task_name] = task_state
                    continue
                
                # Create async task
                async_task = self._execute_task_async(task, workflow_state)
                tasks.append((task_name, async_task))
            
            # Execute all tasks concurrently
            results = await asyncio.gather(
                *[t[1] for t in tasks],
                return_exceptions=True
            )
            
            # Process results
            for (task_name, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    task_state = TaskState(
                        task_name=task_name,
                        status="failed",
                        error=str(result)
                    )
                else:
                    task_state = TaskState(
                        task_name=task_name,
                        status="success" if result.status == TaskStatus.SUCCESS else "failed",
                        result=result.data if result.status == TaskStatus.SUCCESS else None,
                        error=result.error if result.status == TaskStatus.FAILED else None,
                        execution_time_ms=result.execution_time_ms
                    )
                
                workflow_state.task_states[task_name] = task_state
                self.state_manager.save_workflow_state(workflow_state)
        
        asyncio.run(run_async())
    
    def _execute_task(self, task: Task, workflow_state: WorkflowState) -> TaskResult:
        """Execute a single task."""
        task_state = TaskState(
            task_name=task.name,
            status="running",
            start_time=datetime.utcnow()
        )
        
        # Execute with retries
        retry_count = 0
        last_result = None
        
        while retry_count <= task.retries:
            result = task.execute(workflow_state.context)
            last_result = result
            
            if result.status == TaskStatus.SUCCESS:
                break
            
            retry_count += 1
            if retry_count <= task.retries:
                delay = task.retry_delay.total_seconds()
                if task.retry_exponential_backoff:
                    delay *= (2 ** (retry_count - 1))
                if task.max_retry_delay:
                    delay = min(delay, task.max_retry_delay.total_seconds())
                time.sleep(delay)
        
        task_state.end_time = datetime.utcnow()
        task_state.retry_count = retry_count
        
        return last_result
    
    def _execute_task_process(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task in a separate process."""
        result = task.execute(context)
        return {
            "status": "success" if result.status == TaskStatus.SUCCESS else "failed",
            "data": result.data,
            "error": result.error,
            "execution_time_ms": result.execution_time_ms
        }
    
    async def _execute_task_async(self, task: Task, 
                                   workflow_state: WorkflowState) -> TaskResult:
        """Execute task asynchronously."""
        import asyncio
        
        # Run task in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._execute_task,
            task,
            workflow_state
        )
    
    def _check_trigger_rule(self, dag: DAG, task: Task, 
                            workflow_state: WorkflowState) -> bool:
        """Check if task should trigger based on its trigger rule."""
        upstream_tasks = dag.get_upstream_tasks(task.name)
        
        if not upstream_tasks:
            return True
        
        upstream_statuses = [
            workflow_state.task_states.get(name, TaskState(task_name=name, status="pending")).status
            for name in upstream_tasks
        ]
        
        from orchestration.core.dag import TriggerRule
        
        if task.trigger_rule == TriggerRule.ALL_SUCCESS:
            return all(s == "success" for s in upstream_statuses)
        
        elif task.trigger_rule == TriggerRule.ALL_FAILED:
            return all(s == "failed" for s in upstream_statuses)
        
        elif task.trigger_rule == TriggerRule.ALL_DONE:
            return all(s in ["success", "failed", "skipped"] for s in upstream_statuses)
        
        elif task.trigger_rule == TriggerRule.ONE_SUCCESS:
            return any(s == "success" for s in upstream_statuses)
        
        elif task.trigger_rule == TriggerRule.ONE_FAILED:
            return any(s == "failed" for s in upstream_statuses)
        
        elif task.trigger_rule == TriggerRule.NONE_FAILED:
            return not any(s == "failed" for s in upstream_statuses)
        
        elif task.trigger_rule == TriggerRule.NONE_SKIPPED:
            return not any(s == "skipped" for s in upstream_statuses)
        
        elif task.trigger_rule == TriggerRule.ALWAYS:
            return True
        
        return True
    
    def _generate_workflow_id(self, dag_name: str) -> str:
        """Generate unique workflow ID."""
        with self._lock:
            self._execution_count += 1
            return f"{dag_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{self._execution_count}"
    
    def get_execution_status(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get execution status."""
        return self.state_manager.get_workflow_state(workflow_id)


# Dynamic task generation
class DynamicTaskGenerator:
    """Generate tasks dynamically during workflow execution."""
    
    def __init__(self, dag: DAG):
        self.dag = dag
    
    def generate_for_each(self, task_name: str, items: List[Any], 
                          task_factory: Callable[[Any], Task]) -> List[str]:
        """Generate a task for each item in a list."""
        generated_tasks = []
        
        for i, item in enumerate(items):
            task = task_factory(item)
            task.name = f"{task_name}_{i}"
            self.dag.add_task(task)
            generated_tasks.append(task.name)
        
        return generated_tasks
    
    def generate_conditional(self, task_name: str, condition: Callable[[], bool],
                             true_task: Task, false_task: Task = None) -> Optional[str]:
        """Generate a task conditionally."""
        if condition():
            true_task.name = f"{task_name}_true"
            self.dag.add_task(true_task)
            return true_task.name
        elif false_task:
            false_task.name = f"{task_name}_false"
            self.dag.add_task(false_task)
            return false_task.name
        return None


# Example usage
if __name__ == "__main__":
    from orchestration.core.dag import DAG, Task
    
    # Create a DAG
    dag = DAG(name="test_parallel")
    
    # Create tasks
    def task_func(ctx):
        import time
        time.sleep(1)
        return TaskResult(status=TaskStatus.SUCCESS, data={"result": "ok"})
    
    tasks = [
        Task(name=f"task_{i}", task_type="python", python_callable=task_func)
        for i in range(5)
    ]
    
    dag.add_tasks(tasks)
    
    # Execute with parallel executor
    config = ExecutionConfig(
        executor_type=ExecutorType.THREAD,
        max_workers=3
    )
    
    executor = ParallelExecutor(config)
    workflow_state = executor.execute_dag(dag)
    
    print(f"Workflow status: {workflow_state.status}")
    print(f"Execution time: {(workflow_state.end_time - workflow_state.start_time).total_seconds():.2f}s")
    print(f"Tasks completed: {len([t for t in workflow_state.task_states.values() if t.status == 'success'])}")
```


---

## 7. Workflow Monitoring

### 7.1 Monitoring System

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/orchestration/monitors/workflow_monitor.py

"""
Workflow monitoring and observability system.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import json
import threading
import time
from collections import defaultdict, deque


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = auto()
    GAUGE = auto()
    HISTOGRAM = auto()
    TIMER = auto()


@dataclass
class Metric:
    """A metric data point."""
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.metric_type.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags
        }


@dataclass
class WorkflowEvent:
    """A workflow execution event."""
    event_type: str  # 'workflow_start', 'workflow_end', 'task_start', 'task_end', etc.
    workflow_id: str
    dag_name: str
    task_name: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "workflow_id": self.workflow_id,
            "dag_name": self.dag_name,
            "task_name": self.task_name,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }


class MetricsCollector:
    """Collects and stores metrics."""
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.metrics: deque = deque()
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def counter(self, name: str, value: float = 1, tags: Dict[str, str] = None):
        """Increment a counter metric."""
        with self._lock:
            self.counters[name] += value
            self.metrics.append(Metric(
                name=name,
                metric_type=MetricType.COUNTER,
                value=self.counters[name],
                timestamp=datetime.utcnow(),
                tags=tags or {}
            ))
    
    def gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric."""
        with self._lock:
            self.gauges[name] = value
            self.metrics.append(Metric(
                name=name,
                metric_type=MetricType.GAUGE,
                value=value,
                timestamp=datetime.utcnow(),
                tags=tags or {}
            ))
    
    def histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram value."""
        with self._lock:
            self.histograms[name].append(value)
            self.metrics.append(Metric(
                name=name,
                metric_type=MetricType.HISTOGRAM,
                value=value,
                timestamp=datetime.utcnow(),
                tags=tags or {}
            ))
    
    def timer(self, name: str, duration_ms: float, tags: Dict[str, str] = None):
        """Record a timer metric."""
        self.histogram(name, duration_ms, tags)
    
    def get_counter(self, name: str) -> float:
        """Get current counter value."""
        with self._lock:
            return self.counters.get(name, 0)
    
    def get_gauge(self, name: str) -> float:
        """Get current gauge value."""
        with self._lock:
            return self.gauges.get(name, 0)
    
    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """Get histogram statistics."""
        with self._lock:
            values = self.histograms.get(name, [])
            if not values:
                return {}
            
            sorted_values = sorted(values)
            n = len(sorted_values)
            
            return {
                "count": n,
                "min": sorted_values[0],
                "max": sorted_values[-1],
                "mean": sum(sorted_values) / n,
                "p50": sorted_values[int(n * 0.5)],
                "p95": sorted_values[int(n * 0.95)],
                "p99": sorted_values[int(n * 0.99)]
            }
    
    def get_metrics(self, name: str = None, metric_type: MetricType = None,
                    since: datetime = None) -> List[Metric]:
        """Get metrics with optional filtering."""
        with self._lock:
            result = []
            for metric in self.metrics:
                if name and metric.name != name:
                    continue
                if metric_type and metric.metric_type != metric_type:
                    continue
                if since and metric.timestamp < since:
                    continue
                result.append(metric)
            return result
    
    def cleanup_old_metrics(self):
        """Remove metrics older than retention period."""
        cutoff = datetime.utcnow() - timedelta(hours=self.retention_hours)
        with self._lock:
            while self.metrics and self.metrics[0].timestamp < cutoff:
                self.metrics.popleft()


class EventLogger:
    """Logs workflow events."""
    
    def __init__(self, max_events: int = 10000):
        self.max_events = max_events
        self.events: deque = deque(maxlen=max_events)
        self._lock = threading.Lock()
        self._handlers: List[Callable[[WorkflowEvent], None]] = []
    
    def add_handler(self, handler: Callable[[WorkflowEvent], None]):
        """Add an event handler."""
        self._handlers.append(handler)
    
    def log_event(self, event: WorkflowEvent):
        """Log an event."""
        with self._lock:
            self.events.append(event)
        
        # Call handlers
        for handler in self._handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler: {e}")
    
    def get_events(self, event_type: str = None, workflow_id: str = None,
                   dag_name: str = None, since: datetime = None,
                   limit: int = 100) -> List[WorkflowEvent]:
        """Get events with optional filtering."""
        with self._lock:
            result = []
            for event in reversed(self.events):
                if event_type and event.event_type != event_type:
                    continue
                if workflow_id and event.workflow_id != workflow_id:
                    continue
                if dag_name and event.dag_name != dag_name:
                    continue
                if since and event.timestamp < since:
                    continue
                result.append(event)
                if len(result) >= limit:
                    break
            return result
    
    def get_workflow_events(self, workflow_id: str) -> List[WorkflowEvent]:
        """Get all events for a workflow."""
        return self.get_events(workflow_id=workflow_id, limit=self.max_events)


class WorkflowMonitor:
    """
    Comprehensive workflow monitoring system.
    
    Features:
    - Real-time metrics collection
    - Event logging
    - Performance tracking
    - Alert generation
    - Dashboard data export
    """
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.events = EventLogger()
        self._alert_handlers: List[Callable[[str, Dict], None]] = []
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start monitoring."""
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def stop(self):
        """Stop monitoring."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self._running:
            # Cleanup old metrics
            self.metrics.cleanup_old_metrics()
            time.sleep(60)  # Run every minute
    
    # Workflow lifecycle events
    def on_workflow_start(self, workflow_id: str, dag_name: str):
        """Record workflow start."""
        self.metrics.counter("workflows_started", tags={"dag_name": dag_name})
        self.metrics.gauge("active_workflows", 
                          self.metrics.get_counter("workflows_started") - 
                          self.metrics.get_counter("workflows_completed"))
        
        self.events.log_event(WorkflowEvent(
            event_type="workflow_start",
            workflow_id=workflow_id,
            dag_name=dag_name
        ))
    
    def on_workflow_end(self, workflow_id: str, dag_name: str, 
                        status: str, duration_ms: float):
        """Record workflow end."""
        self.metrics.counter("workflows_completed", tags={"dag_name": dag_name, "status": status})
        self.metrics.timer("workflow_duration", duration_ms, tags={"dag_name": dag_name})
        
        self.events.log_event(WorkflowEvent(
            event_type="workflow_end",
            workflow_id=workflow_id,
            dag_name=dag_name,
            data={"status": status, "duration_ms": duration_ms}
        ))
        
        # Check for alerts
        if status == "failed":
            self._trigger_alert("workflow_failed", {
                "workflow_id": workflow_id,
                "dag_name": dag_name,
                "duration_ms": duration_ms
            })
    
    def on_task_start(self, workflow_id: str, dag_name: str, task_name: str):
        """Record task start."""
        self.metrics.counter("tasks_started", tags={"dag_name": dag_name, "task_name": task_name})
        
        self.events.log_event(WorkflowEvent(
            event_type="task_start",
            workflow_id=workflow_id,
            dag_name=dag_name,
            task_name=task_name
        ))
    
    def on_task_end(self, workflow_id: str, dag_name: str, task_name: str,
                    status: str, duration_ms: float):
        """Record task end."""
        self.metrics.counter("tasks_completed", tags={
            "dag_name": dag_name, 
            "task_name": task_name,
            "status": status
        })
        self.metrics.timer("task_duration", duration_ms, tags={
            "dag_name": dag_name,
            "task_name": task_name
        })
        
        self.events.log_event(WorkflowEvent(
            event_type="task_end",
            workflow_id=workflow_id,
            dag_name=dag_name,
            task_name=task_name,
            data={"status": status, "duration_ms": duration_ms}
        ))
        
        # Alert on slow tasks
        if duration_ms > 60000:  # 1 minute
            self._trigger_alert("slow_task", {
                "workflow_id": workflow_id,
                "dag_name": dag_name,
                "task_name": task_name,
                "duration_ms": duration_ms
            })
    
    def on_task_retry(self, workflow_id: str, dag_name: str, task_name: str,
                      retry_count: int):
        """Record task retry."""
        self.metrics.counter("task_retries", tags={
            "dag_name": dag_name,
            "task_name": task_name
        })
        
        self.events.log_event(WorkflowEvent(
            event_type="task_retry",
            workflow_id=workflow_id,
            dag_name=dag_name,
            task_name=task_name,
            data={"retry_count": retry_count}
        ))
    
    def register_alert_handler(self, handler: Callable[[str, Dict], None]):
        """Register an alert handler."""
        self._alert_handlers.append(handler)
    
    def _trigger_alert(self, alert_type: str, data: Dict):
        """Trigger an alert."""
        for handler in self._alert_handlers:
            try:
                handler(alert_type, data)
            except Exception as e:
                print(f"Error in alert handler: {e}")
    
    # Dashboard data export
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard."""
        return {
            "workflows": {
                "started": self.metrics.get_counter("workflows_started"),
                "completed": self.metrics.get_counter("workflows_completed"),
                "active": self.metrics.get_gauge("active_workflows")
            },
            "tasks": {
                "started": self.metrics.get_counter("tasks_started"),
                "completed": self.metrics.get_counter("tasks_completed"),
                "retries": self.metrics.get_counter("task_retries")
            },
            "durations": {
                "workflow": self.metrics.get_histogram_stats("workflow_duration"),
                "task": self.metrics.get_histogram_stats("task_duration")
            },
            "recent_events": [
                e.to_dict() for e in self.events.get_events(limit=10)
            ]
        }
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in various formats."""
        if format == "json":
            return json.dumps({
                "counters": dict(self.metrics.counters),
                "gauges": dict(self.metrics.gauges),
                "histograms": {
                    name: self.metrics.get_histogram_stats(name)
                    for name in self.metrics.histograms.keys()
                }
            }, indent=2)
        
        elif format == "prometheus":
            lines = []
            for name, value in self.metrics.counters.items():
                lines.append(f'{name}_total {value}')
            for name, value in self.metrics.gauges.items():
                lines.append(f'{name} {value}')
            return '\n'.join(lines)
        
        return ""


# Health check system
class HealthChecker:
    """System health checker."""
    
    def __init__(self):
        self.checks: Dict[str, Callable[[], Dict[str, Any]]] = {}
    
    def register_check(self, name: str, check_fn: Callable[[], Dict[str, Any]]):
        """Register a health check."""
        self.checks[name] = check_fn
    
    def run_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {}
        overall_status = "healthy"
        
        for name, check_fn in self.checks.items():
            try:
                result = check_fn()
                results[name] = result
                if result.get("status") != "healthy":
                    overall_status = "degraded"
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}
                overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": results
        }


# Example usage
if __name__ == "__main__":
    # Create monitor
    monitor = WorkflowMonitor()
    
    # Register alert handler
    def on_alert(alert_type: str, data: Dict):
        print(f"ALERT: {alert_type} - {data}")
    
    monitor.register_alert_handler(on_alert)
    
    # Start monitoring
    monitor.start()
    
    # Simulate workflow execution
    workflow_id = "test_workflow_001"
    dag_name = "test_dag"
    
    monitor.on_workflow_start(workflow_id, dag_name)
    
    # Simulate tasks
    for i in range(3):
        task_name = f"task_{i}"
        monitor.on_task_start(workflow_id, dag_name, task_name)
        time.sleep(0.1)
        monitor.on_task_end(workflow_id, dag_name, task_name, "success", 100)
    
    monitor.on_workflow_end(workflow_id, dag_name, "success", 500)
    
    # Print dashboard data
    print("\nDashboard Data:")
    print(json.dumps(monitor.get_dashboard_data(), indent=2))
    
    # Stop monitoring
    monitor.stop()
```


---

## 8. Integration with Airflow and Prefect

### 8.1 Apache Airflow Integration

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/dags/data_pipeline.py

"""
Apache Airflow DAG for ResilienceAI data pipeline.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Default arguments
default_args = {
    'owner': 'resilienceai',
    'depends_on_past': False,
    'email': ['admin@resilienceai.org'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}

# DAG definition
dag = DAG(
    'resilienceai_data_pipeline',
    default_args=default_args,
    description='ResilienceAI complete data pipeline',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=['resilienceai', 'data', 'pipeline'],
)

# Task functions
def download_hifld_task(**context):
    """Download HIFLD facility data."""
    from src.download_data import download_all_hifld
    force = Variable.get("force_download", default_var=False)
    result = download_all_hifld(force=force)
    return {"facilities": {k: len(v) for k, v in result.items()}}

def download_cms_task(**context):
    """Download CMS nursing home data."""
    from src.download_data import download_nursing_homes
    force = Variable.get("force_download", default_var=False)
    result = download_nursing_homes(force=force)
    return {"records": len(result)}

def download_fema_task(**context):
    """Download FEMA disaster declarations."""
    from src.download_data import download_fema_disasters
    force = Variable.get("force_download", default_var=False)
    result = download_fema_disasters(force=force)
    return {"disasters": len(result)}

def download_census_task(**context):
    """Download Census demographic data."""
    from src.download_data import download_census_data
    force = Variable.get("force_download", default_var=False)
    result = download_census_data(force=force)
    return {"counties": len(result)}

def download_centroids_task(**context):
    """Download county centroid data."""
    from src.download_data import download_county_centroids
    force = Variable.get("force_download", default_var=False)
    result = download_county_centroids(force=force)
    return {"centroids": len(result)}

def feature_engineering_task(**context):
    """Run feature engineering."""
    from src.feature_engineering import run_feature_engineering
    result = run_feature_engineering()
    return {"features": result}

def eda_task(**context):
    """Run exploratory data analysis."""
    from src.pipeline.eda import run_eda
    result = run_eda()
    return {"eda": result}

def train_models_task(**context):
    """Train predictive models."""
    from src.train_models import train_and_evaluate
    result = train_and_evaluate()
    return {"models": result}

def export_agent_config_task(**context):
    """Export agent configuration."""
    from src.agent import export_agent_config
    result = export_agent_config()
    return {"config": result}

def notify_completion_task(**context):
    """Send notification on completion."""
    ti = context['ti']
    
    # Get task results
    hifld_result = ti.xcom_pull(task_ids='download_hifld')
    cms_result = ti.xcom_pull(task_ids='download_cms')
    fema_result = ti.xcom_pull(task_ids='download_fema')
    census_result = ti.xcom_pull(task_ids='download_census')
    
    message = f"""
    ResilienceAI Data Pipeline Complete
    
    HIFLD Facilities: {hifld_result}
    CMS Records: {cms_result}
    FEMA Disasters: {fema_result}
    Census Counties: {census_result}
    """
    
    print(message)
    return {"notification_sent": True}

# Stage 1: Data Acquisition (Parallel)
with TaskGroup("data_acquisition", dag=dag) as data_acquisition:
    download_hifld = PythonOperator(
        task_id='download_hifld',
        python_callable=download_hifld_task,
        pool='download_pool',
    )
    
    download_cms = PythonOperator(
        task_id='download_cms',
        python_callable=download_cms_task,
        pool='download_pool',
    )
    
    download_fema = PythonOperator(
        task_id='download_fema',
        python_callable=download_fema_task,
        pool='download_pool',
    )
    
    download_census = PythonOperator(
        task_id='download_census',
        python_callable=download_census_task,
        pool='download_pool',
    )
    
    download_centroids = PythonOperator(
        task_id='download_centroids',
        python_callable=download_centroids_task,
        pool='download_pool',
    )

# Stage 2: Feature Engineering
feature_engineering = PythonOperator(
    task_id='feature_engineering',
    python_callable=feature_engineering_task,
    dag=dag,
)

# Stage 3: EDA
eda = PythonOperator(
    task_id='eda',
    python_callable=eda_task,
    dag=dag,
)

# Stage 4: Model Training
train_models = PythonOperator(
    task_id='train_models',
    python_callable=train_models_task,
    dag=dag,
)

# Stage 5: Agent Configuration
export_agent_config = PythonOperator(
    task_id='export_agent_config',
    python_callable=export_agent_config_task,
    dag=dag,
)

# Stage 6: Notification
notify_completion = PythonOperator(
    task_id='notify_completion',
    python_callable=notify_completion_task,
    trigger_rule='all_done',
    dag=dag,
)

# Define dependencies
data_acquisition >> feature_engineering >> [eda, train_models]
train_models >> export_agent_config >> notify_completion
eda >> notify_completion
```

### 8.2 Prefect Integration

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/flows/data_pipeline_flow.py

"""
Prefect flow for ResilienceAI data pipeline.
"""

from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from prefect.cache_policies import INPUTS
from datetime import timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Tasks with caching
@task(cache_policy=INPUTS, cache_expiration=timedelta(hours=24))
def download_hifld(force: bool = False) -> dict:
    """Download HIFLD facility data."""
    logger = get_run_logger()
    logger.info("Downloading HIFLD facilities...")
    
    from src.download_data import download_all_hifld
    result = download_all_hifld(force=force)
    
    logger.info(f"Downloaded {len(result)} facility types")
    return {"facilities": {k: len(v) for k, v in result.items()}}


@task(cache_policy=INPUTS, cache_expiration=timedelta(hours=24))
def download_cms(force: bool = False) -> dict:
    """Download CMS nursing home data."""
    logger = get_run_logger()
    logger.info("Downloading CMS nursing homes...")
    
    from src.download_data import download_nursing_homes
    result = download_nursing_homes(force=force)
    
    logger.info(f"Downloaded {len(result)} nursing home records")
    return {"records": len(result)}


@task(cache_policy=INPUTS, cache_expiration=timedelta(hours=24))
def download_fema(force: bool = False) -> dict:
    """Download FEMA disaster declarations."""
    logger = get_run_logger()
    logger.info("Downloading FEMA disasters...")
    
    from src.download_data import download_fema_disasters
    result = download_fema_disasters(force=force)
    
    logger.info(f"Downloaded {len(result)} disaster records")
    return {"disasters": len(result)}


@task(cache_policy=INPUTS, cache_expiration=timedelta(hours=24))
def download_census(force: bool = False) -> dict:
    """Download Census demographic data."""
    logger = get_run_logger()
    logger.info("Downloading Census data...")
    
    from src.download_data import download_census_data
    result = download_census_data(force=force)
    
    logger.info(f"Downloaded {len(result)} county records")
    return {"counties": len(result)}


@task(cache_policy=INPUTS, cache_expiration=timedelta(hours=24))
def download_centroids(force: bool = False) -> dict:
    """Download county centroid data."""
    logger = get_run_logger()
    logger.info("Downloading county centroids...")
    
    from src.download_data import download_county_centroids
    result = download_county_centroids(force=force)
    
    logger.info(f"Downloaded {len(result)} county centroids")
    return {"centroids": len(result)}


@task(retries=2, retry_delay_seconds=10)
def feature_engineering() -> dict:
    """Run feature engineering."""
    logger = get_run_logger()
    logger.info("Running feature engineering...")
    
    from src.feature_engineering import run_feature_engineering
    result = run_feature_engineering()
    
    logger.info("Feature engineering complete")
    return {"features": result}


@task
def eda_statistics() -> dict:
    """Run statistical EDA."""
    logger = get_run_logger()
    logger.info("Running EDA statistics...")
    
    from src.pipeline.eda import run_eda_statistics
    result = run_eda_statistics()
    
    return {"statistics": result}


@task
def eda_visualizations() -> dict:
    """Generate EDA visualizations."""
    logger = get_run_logger()
    logger.info("Generating EDA visualizations...")
    
    from src.pipeline.eda import run_eda_visualizations
    result = run_eda_visualizations()
    
    return {"visualizations": result}


@task(retries=1)
def train_models() -> dict:
    """Train predictive models."""
    logger = get_run_logger()
    logger.info("Training models...")
    
    from src.train_models import train_and_evaluate
    result = train_and_evaluate()
    
    logger.info("Model training complete")
    return {"models": result}


@task
def export_agent_config() -> dict:
    """Export agent configuration."""
    logger = get_run_logger()
    logger.info("Exporting agent config...")
    
    from src.agent import export_agent_config
    result = export_agent_config()
    
    logger.info("Agent config exported")
    return {"config": result}


# Main flow
@flow(name="resilienceai_data_pipeline", log_prints=True)
def data_pipeline_flow(force_download: bool = False):
    """
    ResilienceAI data pipeline flow.
    
    Args:
        force_download: Force re-download of all data
    """
    logger = get_run_logger()
    logger.info("Starting ResilienceAI data pipeline...")
    
    # Stage 1: Data Acquisition (Parallel)
    logger.info("Stage 1: Data Acquisition")
    
    hifld = download_hifld.submit(force=force_download)
    cms = download_cms.submit(force=force_download)
    fema = download_fema.submit(force=force_download)
    census = download_census.submit(force=force_download)
    centroids = download_centroids.submit(force=force_download)
    
    # Wait for all downloads
    hifld_result = hifld.result()
    cms_result = cms.result()
    fema_result = fema.result()
    census_result = census.result()
    centroids_result = centroids.result()
    
    logger.info(f"Downloaded: HIFLD={hifld_result}, CMS={cms_result}, "
                f"FEMA={fema_result}, Census={census_result}, Centroids={centroids_result}")
    
    # Stage 2: Feature Engineering
    logger.info("Stage 2: Feature Engineering")
    features = feature_engineering()
    
    # Stage 3: EDA (Parallel)
    logger.info("Stage 3: Exploratory Data Analysis")
    
    stats = eda_statistics.submit()
    viz = eda_visualizations.submit()
    
    stats_result = stats.result()
    viz_result = viz.result()
    
    # Stage 4: Model Training
    logger.info("Stage 4: Model Training")
    models = train_models()
    
    # Stage 5: Agent Configuration
    logger.info("Stage 5: Agent Configuration")
    config = export_agent_config()
    
    logger.info("Data pipeline complete!")
    
    return {
        "downloads": {
            "hifld": hifld_result,
            "cms": cms_result,
            "fema": fema_result,
            "census": census_result,
            "centroids": centroids_result
        },
        "features": features,
        "eda": {
            "statistics": stats_result,
            "visualizations": viz_result
        },
        "models": models,
        "config": config
    }


# Agent orchestration flow
@flow(name="resilienceai_agent_orchestration", log_prints=True)
def agent_orchestration_flow(query: str, context: dict = None):
    """
    Multi-agent orchestration flow.
    
    Args:
        query: User query
        context: Additional context
    """
    logger = get_run_logger()
    logger.info(f"Processing query: {query}")
    
    from src.agents.orchestrator import AgentOrchestrator
    
    orchestrator = AgentOrchestrator()
    response = orchestrator.execute_query(query, context)
    
    logger.info(f"Response generated in {response.execution_time_ms:.1f}ms")
    
    return {
        "query": response.query,
        "response": response.response,
        "insights": response.insights,
        "agents_used": response.routing_path,
        "execution_time_ms": response.execution_time_ms,
        "confidence": response.confidence
    }


if __name__ == "__main__":
    # Run data pipeline
    result = data_pipeline_flow(force_download=False)
    print(f"Pipeline result: {result}")
```

### 8.3 Integration Adapters

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/orchestration/engines/airflow_engine.py

"""
Apache Airflow engine adapter.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from orchestration.core.dag import DAG as CoreDAG, Task as CoreTask, TaskStatus, TaskResult
from orchestration.core.state import StateManager, WorkflowState


class AirflowEngineAdapter:
    """
    Adapter for running custom DAGs on Apache Airflow.
    
    Converts custom DAG definitions to Airflow-compatible format.
    """
    
    def __init__(self, airflow_dag_folder: str = "/opt/airflow/dags"):
        self.dag_folder = airflow_dag_folder
    
    def convert_to_airflow(self, dag: CoreDAG) -> str:
        """
        Convert a custom DAG to Airflow Python code.
        
        Returns:
            Python code string for Airflow DAG
        """
        lines = [
            "\"\"\"",
            f"Airflow DAG: {dag.name}",
            f"Description: {dag.description}",
            f"Generated: {datetime.utcnow().isoformat()}",
            "\"\"\"",
            "",
            "from datetime import datetime, timedelta",
            "from airflow import DAG",
            "from airflow.operators.python import PythonOperator",
            "from airflow.operators.bash import BashOperator",
            "",
            "default_args = {",
            f"    'owner': 'resilienceai',",
            f"    'retries': {dag.default_args.get('retries', 3)},",
            f"    'retry_delay': timedelta(seconds={dag.default_args.get('retry_delay', 300)}),",
            "}",
            "",
            f"dag = DAG(",
            f"    '{dag.name}',",
            f"    default_args=default_args,",
            f"    description='{dag.description}',",
            f"    schedule_interval='{dag.schedule_interval or None}',",
            f"    start_date=datetime(2024, 1, 1),",
            f"    catchup={dag.catchup},",
            f"    max_active_runs={dag.max_active_runs},",
            f"    tags={dag.tags or ['resilienceai']},",
            ")",
            "",
        ]
        
        # Generate task functions
        for task_name, task in dag.tasks.items():
            lines.extend(self._generate_task_function(task))
        
        # Generate task operators
        task_var_names = {}
        for i, (task_name, task) in enumerate(dag.tasks.items()):
            var_name = f"task_{i}"
            task_var_names[task_name] = var_name
            
            if task.task_type == "python":
                lines.append(
                    f"{var_name} = PythonOperator("
                )
                lines.append(f"    task_id='{task.name}',")
                lines.append(f"    python_callable=task_fn_{task.name},")
                lines.append(f"    retries={task.retries},")
                lines.append(f"    dag=dag,")
                lines.append(")")
            elif task.task_type == "bash":
                lines.append(
                    f"{var_name} = BashOperator("
                )
                lines.append(f"    task_id='{task.name}',")
                lines.append(f"    bash_command='{task.bash_command}',")
                lines.append(f"    dag=dag,")
                lines.append(")")
            lines.append("")
        
        # Generate dependencies
        for task_name, upstream_tasks in dag.dependencies.items():
            if upstream_tasks:
                upstream_vars = [task_var_names[t] for t in upstream_tasks]
                lines.append(
                    f"{task_var_names[task_name]} >> [{', '.join(upstream_vars)}]"
                )
        
        return "\n".join(lines)
    
    def _generate_task_function(self, task: CoreTask) -> List[str]:
        """Generate a task function for Airflow."""
        lines = [
            f"def task_fn_{task.name}(**context):",
            "    \"\"\"Task implementation.\"\"\"",
        ]
        
        if task.python_callable:
            # Get function source (simplified)
            import inspect
            try:
                source = inspect.getsource(task.python_callable)
                lines.append(f"    # Original function source:")
                for line in source.split("\n"):
                    lines.append(f"    # {line}")
            except:
                lines.append("    # Function source not available")
        
        lines.append("    pass")
        lines.append("")
        
        return lines
    
    def save_dag(self, dag: CoreDAG, filename: str = None):
        """Save DAG to Airflow DAG folder."""
        import os
        
        if not filename:
            filename = f"{dag.name}.py"
        
        filepath = os.path.join(self.dag_folder, filename)
        code = self.convert_to_airflow(dag)
        
        with open(filepath, 'w') as f:
            f.write(code)
        
        return filepath


class PrefectEngineAdapter:
    """
    Adapter for running custom DAGs on Prefect.
    """
    
    def __init__(self):
        pass
    
    def convert_to_prefect(self, dag: CoreDAG) -> str:
        """
        Convert a custom DAG to Prefect flow code.
        
        Returns:
            Python code string for Prefect flow
        """
        lines = [
            "\"\"\"",
            f"Prefect Flow: {dag.name}",
            f"Description: {dag.description}",
            f"Generated: {datetime.utcnow().isoformat()}",
            "\"\"\"",
            "",
            "from prefect import flow, task, get_run_logger",
            "from datetime import timedelta",
            "",
            f"@flow(name='{dag.name}')",
            f"def {dag.name}_flow():",
            "    logger = get_run_logger()",
            "    logger.info('Starting flow...')",
            "",
        ]
        
        # Generate tasks
        for task_name, task in dag.tasks.items():
            lines.extend(self._generate_prefect_task(task))
        
        # Generate flow body based on execution levels
        execution_levels = dag.get_execution_levels()
        
        for level in execution_levels:
            if len(level) == 1:
                task_name = level[0]
                lines.append(f"    result_{task_name} = task_{task_name}()")
            else:
                # Parallel execution
                for task_name in level:
                    lines.append(f"    {task_name}_future = task_{task_name}.submit()")
                lines.append("")
                for task_name in level:
                    lines.append(f"    result_{task_name} = {task_name}_future.result()")
            lines.append("")
        
        lines.append("    logger.info('Flow complete!')")
        lines.append("")
        lines.append("if __name__ == '__main__':")
        lines.append(f"    {dag.name}_flow()")
        
        return "\n".join(lines)
    
    def _generate_prefect_task(self, task: CoreTask) -> List[str]:
        """Generate a Prefect task."""
        lines = [
            "",
            f"@task",
            f"def task_{task.name}():",
            f"    \"\"\"{task.name} task.\"\"\"",
        ]
        
        if task.python_callable:
            lines.append("    # Task implementation")
            lines.append("    pass")
        
        return lines
```


---

## 9. Workflow Versioning

### 9.1 Version Management System

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/orchestration/versioning/version_manager.py

"""
Workflow versioning and migration system.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
import hashlib
import json
from pathlib import Path
import semver


class VersionStatus(Enum):
    """Version status."""
    DRAFT = auto()
    ACTIVE = auto()
    DEPRECATED = auto()
    ARCHIVED = auto()


@dataclass
class WorkflowVersion:
    """A version of a workflow."""
    version: str  # Semantic version (e.g., "1.2.3")
    dag_name: str
    dag_hash: str
    created_at: datetime
    status: VersionStatus
    changelog: str = ""
    author: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_version: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "dag_name": self.dag_name,
            "dag_hash": self.dag_hash,
            "created_at": self.created_at.isoformat(),
            "status": self.status.name,
            "changelog": self.changelog,
            "author": self.author,
            "metadata": self.metadata,
            "parent_version": self.parent_version
        }


@dataclass
class Migration:
    """A workflow migration."""
    from_version: str
    to_version: str
    migration_fn: Callable[[Dict], Dict]
    description: str = ""
    
    def apply(self, data: Dict) -> Dict:
        """Apply migration to data."""
        return self.migration_fn(data)


class VersionManager:
    """
    Manages workflow versions and migrations.
    
    Features:
    - Semantic versioning
    - Version history tracking
    - Migration management
    - Rollback support
    """
    
    def __init__(self, storage_path: str = "./versions"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.versions: Dict[str, List[WorkflowVersion]] = {}
        self.migrations: Dict[str, List[Migration]] = {}
        self._load_versions()
    
    def _load_versions(self):
        """Load version history from storage."""
        versions_file = self.storage_path / "versions.json"
        if versions_file.exists():
            with open(versions_file, 'r') as f:
                data = json.load(f)
                for dag_name, versions_data in data.items():
                    self.versions[dag_name] = [
                        WorkflowVersion(
                            version=v["version"],
                            dag_name=v["dag_name"],
                            dag_hash=v["dag_hash"],
                            created_at=datetime.fromisoformat(v["created_at"]),
                            status=VersionStatus[v["status"]],
                            changelog=v.get("changelog", ""),
                            author=v.get("author", ""),
                            metadata=v.get("metadata", {}),
                            parent_version=v.get("parent_version")
                        )
                        for v in versions_data
                    ]
    
    def _save_versions(self):
        """Save version history to storage."""
        versions_file = self.storage_path / "versions.json"
        data = {
            dag_name: [v.to_dict() for v in versions]
            for dag_name, versions in self.versions.items()
        }
        with open(versions_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def calculate_dag_hash(self, dag: 'DAG') -> str:
        """Calculate a hash of the DAG structure."""
        dag_dict = dag.to_dict()
        dag_json = json.dumps(dag_dict, sort_keys=True)
        return hashlib.sha256(dag_json.encode()).hexdigest()[:16]
    
    def register_version(self, dag: 'DAG', version: str,
                         changelog: str = "", author: str = "") -> WorkflowVersion:
        """
        Register a new version of a DAG.
        
        Args:
            dag: The DAG to version
            version: Semantic version string
            changelog: Description of changes
            author: Author of the version
        
        Returns:
            The registered version
        """
        dag_hash = self.calculate_dag_hash(dag)
        dag_name = dag.name
        
        # Check if version already exists
        if dag_name in self.versions:
            existing = [v for v in self.versions[dag_name] if v.version == version]
            if existing:
                raise ValueError(f"Version {version} already exists for {dag_name}")
        
        # Get parent version
        parent_version = None
        if dag_name in self.versions and self.versions[dag_name]:
            # Find the latest active version
            active_versions = [v for v in self.versions[dag_name] 
                             if v.status == VersionStatus.ACTIVE]
            if active_versions:
                parent_version = max(active_versions, key=lambda v: v.created_at).version
        
        # Create version
        workflow_version = WorkflowVersion(
            version=version,
            dag_name=dag_name,
            dag_hash=dag_hash,
            created_at=datetime.utcnow(),
            status=VersionStatus.DRAFT,
            changelog=changelog,
            author=author,
            parent_version=parent_version
        )
        
        # Store version
        if dag_name not in self.versions:
            self.versions[dag_name] = []
        self.versions[dag_name].append(workflow_version)
        
        # Save DAG definition
        dag_file = self.storage_path / f"{dag_name}_{version}.json"
        with open(dag_file, 'w') as f:
            json.dump(dag.to_dict(), f, indent=2)
        
        self._save_versions()
        
        return workflow_version
    
    def activate_version(self, dag_name: str, version: str):
        """Activate a version."""
        if dag_name not in self.versions:
            raise ValueError(f"No versions found for {dag_name}")
        
        # Deactivate current active version
        for v in self.versions[dag_name]:
            if v.status == VersionStatus.ACTIVE:
                v.status = VersionStatus.DEPRECATED
        
        # Activate new version
        for v in self.versions[dag_name]:
            if v.version == version:
                v.status = VersionStatus.ACTIVE
                break
        else:
            raise ValueError(f"Version {version} not found for {dag_name}")
        
        self._save_versions()
    
    def get_active_version(self, dag_name: str) -> Optional[WorkflowVersion]:
        """Get the currently active version."""
        if dag_name not in self.versions:
            return None
        
        for v in self.versions[dag_name]:
            if v.status == VersionStatus.ACTIVE:
                return v
        
        return None
    
    def get_version(self, dag_name: str, version: str) -> Optional[WorkflowVersion]:
        """Get a specific version."""
        if dag_name not in self.versions:
            return None
        
        for v in self.versions[dag_name]:
            if v.version == version:
                return v
        
        return None
    
    def list_versions(self, dag_name: str) -> List[WorkflowVersion]:
        """List all versions of a DAG."""
        return sorted(
            self.versions.get(dag_name, []),
            key=lambda v: semver.VersionInfo.parse(v.version),
            reverse=True
        )
    
    def compare_versions(self, dag_name: str, version1: str, 
                         version2: str) -> Dict[str, Any]:
        """Compare two versions."""
        v1 = self.get_version(dag_name, version1)
        v2 = self.get_version(dag_name, version2)
        
        if not v1 or not v2:
            raise ValueError("One or both versions not found")
        
        # Load DAG definitions
        dag1_file = self.storage_path / f"{dag_name}_{version1}.json"
        dag2_file = self.storage_path / f"{dag_name}_{version2}.json"
        
        with open(dag1_file, 'r') as f:
            dag1 = json.load(f)
        with open(dag2_file, 'r') as f:
            dag2 = json.load(f)
        
        # Compare
        return {
            "version1": version1,
            "version2": version2,
            "hash_match": v1.dag_hash == v2.dag_hash,
            "task_changes": self._compare_tasks(dag1, dag2),
            "dependency_changes": self._compare_dependencies(dag1, dag2),
            "schedule_changes": dag1.get("schedule_interval") != dag2.get("schedule_interval")
        }
    
    def _compare_tasks(self, dag1: Dict, dag2: Dict) -> Dict[str, Any]:
        """Compare tasks between two DAGs."""
        tasks1 = {t["name"]: t for t in dag1.get("tasks", [])}
        tasks2 = {t["name"]: t for t in dag2.get("tasks", [])}
        
        added = [name for name in tasks2 if name not in tasks1]
        removed = [name for name in tasks1 if name not in tasks2]
        modified = []
        
        for name in tasks1:
            if name in tasks2 and tasks1[name] != tasks2[name]:
                modified.append(name)
        
        return {
            "added": added,
            "removed": removed,
            "modified": modified
        }
    
    def _compare_dependencies(self, dag1: Dict, dag2: Dict) -> Dict[str, Any]:
        """Compare dependencies between two DAGs."""
        deps1 = dag1.get("dependencies", {})
        deps2 = dag2.get("dependencies", {})
        
        added = {k: v for k, v in deps2.items() if k not in deps1 or deps1[k] != v}
        removed = {k: v for k, v in deps1.items() if k not in deps2}
        
        return {
            "added": added,
            "removed": removed
        }
    
    def register_migration(self, dag_name: str, from_version: str,
                           to_version: str, migration_fn: Callable[[Dict], Dict],
                           description: str = ""):
        """Register a migration between versions."""
        key = f"{dag_name}:{from_version}->{to_version}"
        
        if key not in self.migrations:
            self.migrations[key] = []
        
        self.migrations[key].append(Migration(
            from_version=from_version,
            to_version=to_version,
            migration_fn=migration_fn,
            description=description
        ))
    
    def migrate_data(self, dag_name: str, data: Dict,
                     from_version: str, to_version: str) -> Dict:
        """Migrate data from one version to another."""
        # Find migration path
        path = self._find_migration_path(dag_name, from_version, to_version)
        
        # Apply migrations
        result = data
        for migration in path:
            result = migration.apply(result)
        
        return result
    
    def _find_migration_path(self, dag_name: str, from_version: str,
                             to_version: str) -> List[Migration]:
        """Find the migration path between versions."""
        # Simple implementation - direct migration
        key = f"{dag_name}:{from_version}->{to_version}"
        
        if key in self.migrations:
            return self.migrations[key]
        
        raise ValueError(f"No migration path from {from_version} to {to_version}")


# Example usage
if __name__ == "__main__":
    from orchestration.core.dag import DAG, Task
    
    # Create version manager
    version_manager = VersionManager()
    
    # Create a DAG
    dag = DAG(name="test_dag", description="Test DAG")
    dag.add_task(Task(name="task_a", task_type="python"))
    dag.add_task(Task(name="task_b", task_type="python"))
    
    # Register version
    version = version_manager.register_version(
        dag=dag,
        version="1.0.0",
        changelog="Initial version",
        author="developer"
    )
    
    print(f"Registered version: {version.version}")
    
    # Activate version
    version_manager.activate_version("test_dag", "1.0.0")
    
    # Get active version
    active = version_manager.get_active_version("test_dag")
    print(f"Active version: {active.version}")
    
    # List versions
    versions = version_manager.list_versions("test_dag")
    print(f"Versions: {[v.version for v in versions]}")
```

---

## 10. Dynamic Workflow Generation

### 10.1 Dynamic DAG Builder

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/orchestration/core/dynamic_builder.py

"""
Dynamic workflow generation system.
"""

from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
import json

from orchestration.core.dag import DAG, Task, TaskStatus, TaskResult


@dataclass
class DynamicTaskTemplate:
    """Template for dynamically generated tasks."""
    name_pattern: str  # e.g., "process_{item_id}"
    task_type: str
    python_callable: Optional[Callable] = None
    params_template: Dict[str, Any] = field(default_factory=dict)


class DynamicDAGBuilder:
    """
    Builds DAGs dynamically based on runtime data.
    
    Features:
    - Dynamic task generation
    - Conditional branching
    - Loop unrolling
    - Parameterized workflows
    """
    
    def __init__(self, base_dag: DAG):
        self.base_dag = base_dag
        self.dynamic_tasks: Dict[str, DynamicTaskTemplate] = {}
        self.conditions: Dict[str, Callable[[Dict], bool]] = {}
    
    def add_dynamic_task_template(self, name: str, template: DynamicTaskTemplate):
        """Add a dynamic task template."""
        self.dynamic_tasks[name] = template
    
    def add_condition(self, name: str, condition_fn: Callable[[Dict], bool]):
        """Add a condition function."""
        self.conditions[name] = condition_fn
    
    def generate_for_each(self, template_name: str, items: List[Any],
                          upstream_task: str = None) -> List[str]:
        """
        Generate tasks for each item in a list.
        
        Args:
            template_name: Name of the task template
            items: List of items to generate tasks for
            upstream_task: Optional upstream task for dependencies
        
        Returns:
            List of generated task names
        """
        template = self.dynamic_tasks.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        generated_tasks = []
        
        for i, item in enumerate(items):
            # Generate task name
            task_name = template.name_pattern.format(
                item_id=i,
                item=item if isinstance(item, (str, int)) else i
            )
            
            # Generate parameters
            params = self._generate_params(template.params_template, item, i)
            
            # Create task
            task = Task(
                name=task_name,
                task_type=template.task_type,
                python_callable=lambda ctx, p=params, fn=template.python_callable: fn(ctx, p),
                params=params
            )
            
            self.base_dag.add_task(task)
            
            # Add dependency if specified
            if upstream_task:
                self.base_dag.add_dependency(task, upstream_task)
            
            generated_tasks.append(task_name)
        
        return generated_tasks
    
    def generate_conditional(self, condition_name: str,
                             true_template: DynamicTaskTemplate,
                             false_template: DynamicTaskTemplate = None,
                             context: Dict = None) -> Optional[str]:
        """
        Generate a task conditionally.
        
        Args:
            condition_name: Name of the condition
            true_template: Template to use if condition is true
            false_template: Optional template if condition is false
            context: Context for condition evaluation
        
        Returns:
            Generated task name or None
        """
        condition_fn = self.conditions.get(condition_name)
        if not condition_fn:
            raise ValueError(f"Condition '{condition_name}' not found")
        
        if condition_fn(context or {}):
            template = true_template
            suffix = "_true"
        elif false_template:
            template = false_template
            suffix = "_false"
        else:
            return None
        
        task_name = f"{condition_name}{suffix}"
        
        task = Task(
            name=task_name,
            task_type=template.task_type,
            python_callable=template.python_callable,
            params=template.params_template
        )
        
        self.base_dag.add_task(task)
        
        return task_name
    
    def generate_map_reduce(self, map_template: DynamicTaskTemplate,
                            items: List[Any],
                            reduce_task: Task,
                            upstream_task: str = None) -> str:
        """
        Generate a map-reduce pattern.
        
        Args:
            map_template: Template for map tasks
            items: Items to process
            reduce_task: Task to reduce results
            upstream_task: Optional upstream task
        
        Returns:
            Reduce task name
        """
        # Generate map tasks
        map_tasks = self.generate_for_each(
            map_template.name_pattern,
            items,
            upstream_task
        )
        
        # Add reduce task dependency on all map tasks
        self.base_dag.add_dependency(reduce_task, map_tasks)
        
        return reduce_task.name
    
    def generate_branch(self, condition_name: str,
                        branches: Dict[str, List[Task]],
                        context: Dict = None) -> List[str]:
        """
        Generate conditional branches.
        
        Args:
            condition_name: Name of the condition function
            branches: Dictionary of branch name -> list of tasks
            context: Context for condition evaluation
        
        Returns:
            List of tasks in the selected branch
        """
        condition_fn = self.conditions.get(condition_name)
        if not condition_fn:
            raise ValueError(f"Condition '{condition_name}' not found")
        
        # Evaluate condition for each branch
        selected_branch = None
        for branch_name, tasks in branches.items():
            branch_context = {**context, "branch": branch_name}
            if condition_fn(branch_context):
                selected_branch = branch_name
                break
        
        if not selected_branch:
            # Default to first branch
            selected_branch = list(branches.keys())[0]
        
        # Add tasks from selected branch
        for task in branches[selected_branch]:
            self.base_dag.add_task(task)
        
        return [t.name for t in branches[selected_branch]]
    
    def _generate_params(self, template: Dict[str, Any], item: Any, 
                         index: int) -> Dict[str, Any]:
        """Generate parameters from template."""
        params = {}
        
        for key, value in template.items():
            if isinstance(value, str):
                # Replace placeholders
                params[key] = value.format(
                    item=item if isinstance(item, (str, int)) else json.dumps(item),
                    index=index
                )
            else:
                params[key] = value
        
        return params
    
    def get_dag(self) -> DAG:
        """Get the built DAG."""
        return self.base_dag


# Workflow factory
class WorkflowFactory:
    """Factory for creating pre-configured workflows."""
    
    def __init__(self):
        self.templates: Dict[str, Callable[[Dict], DAG]] = {}
    
    def register_template(self, name: str, builder_fn: Callable[[Dict], DAG]):
        """Register a workflow template."""
        self.templates[name] = builder_fn
    
    def create_workflow(self, template_name: str, params: Dict = None) -> DAG:
        """Create a workflow from a template."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        return self.templates[template_name](params or {})
    
    def list_templates(self) -> List[str]:
        """List available templates."""
        return list(self.templates.keys())


# Example usage
if __name__ == "__main__":
    from orchestration.core.dag import DAG, Task, TaskStatus, TaskResult
    
    # Create base DAG
    base_dag = DAG(name="dynamic_test")
    
    # Create builder
    builder = DynamicDAGBuilder(base_dag)
    
    # Add dynamic task template
    template = DynamicTaskTemplate(
        name_pattern="process_{item_id}",
        task_type="python",
        python_callable=lambda ctx, params: TaskResult(
            status=TaskStatus.SUCCESS,
            data={"processed": params.get("item")}
        ),
        params_template={"item": "{item}"}
    )
    
    builder.add_dynamic_task_template("processor", template)
    
    # Generate tasks for items
    items = ["A", "B", "C"]
    task_names = builder.generate_for_each("processor", items)
    
    print(f"Generated tasks: {task_names}")
    
    # Get the DAG
    dag = builder.get_dag()
    print(f"DAG has {len(dag.tasks)} tasks")
```


---

## 11. Implementation Priority Order

### 11.1 Phase 1: Foundation (Weeks 1-2)

| Priority | Component | Effort | Impact | Files |
|----------|-----------|--------|--------|-------|
| 1 | Core DAG Implementation | Medium | High | `orchestration/core/dag.py` |
| 2 | State Management (Memory) | Low | High | `orchestration/core/state.py` |
| 3 | Basic Retry Policies | Low | Medium | `orchestration/retry/policies.py` |
| 4 | Sequential Executor | Low | High | `orchestration/core/executor.py` |
| 5 | Enhanced run_pipeline.py | Low | High | `run_pipeline.py` (update) |

**Phase 1 Goals:**
- Replace basic sequential pipeline with DAG-based execution
- Add state tracking for workflow execution
- Implement retry mechanisms for failed tasks
- Maintain backward compatibility with existing code

### 11.2 Phase 2: Parallel Execution (Weeks 3-4)

| Priority | Component | Effort | Impact | Files |
|----------|-----------|--------|--------|-------|
| 1 | ThreadPool Executor | Medium | High | `orchestration/core/executor.py` |
| 2 | Dependency-aware Scheduling | Medium | High | `orchestration/core/dag.py` |
| 3 | Data Pipeline DAG | Medium | High | `orchestration/dags/data_pipeline_dag.py` |
| 4 | Agent Pipeline DAG | Medium | High | `orchestration/dags/agent_pipeline_dag.py` |
| 5 | XCom for Data Sharing | Medium | Medium | `orchestration/core/state.py` |

**Phase 2 Goals:**
- Enable parallel task execution where dependencies allow
- Create comprehensive DAGs for data and agent pipelines
- Implement cross-task communication (XCom)
- Improve pipeline performance through parallelism

### 11.3 Phase 3: Scheduling & Monitoring (Weeks 5-6)

| Priority | Component | Effort | Impact | Files |
|----------|-----------|--------|--------|-------|
| 1 | Cron Scheduler | Medium | High | `orchestration/schedulers/cron_scheduler.py` |
| 2 | Event Scheduler | Medium | Medium | `orchestration/schedulers/event_scheduler.py` |
| 3 | Metrics Collection | Medium | Medium | `orchestration/monitors/workflow_monitor.py` |
| 4 | Event Logging | Low | Medium | `orchestration/monitors/workflow_monitor.py` |
| 5 | Dashboard Data Export | Low | Low | `orchestration/monitors/workflow_monitor.py` |

**Phase 3 Goals:**
- Add workflow scheduling capabilities
- Implement comprehensive monitoring
- Create metrics and event tracking
- Enable observability and debugging

### 11.4 Phase 4: Integration (Weeks 7-8)

| Priority | Component | Effort | Impact | Files |
|----------|-----------|--------|--------|-------|
| 1 | Airflow DAG Export | Medium | High | `dags/data_pipeline.py` |
| 2 | Prefect Flow Export | Medium | High | `flows/data_pipeline_flow.py` |
| 3 | Integration Adapters | Medium | Medium | `orchestration/engines/` |
| 4 | State Backend (SQLite) | Low | Medium | `orchestration/core/state.py` |
| 5 | Health Checks | Low | Low | `orchestration/monitors/workflow_monitor.py` |

**Phase 4 Goals:**
- Enable deployment on Airflow and Prefect
- Create integration adapters for different engines
- Add persistent state backends
- Implement health check system

### 11.5 Phase 5: Advanced Features (Weeks 9-10)

| Priority | Component | Effort | Impact | Files |
|----------|-----------|--------|--------|-------|
| 1 | Version Management | Medium | Medium | `orchestration/versioning/version_manager.py` |
| 2 | Dynamic DAG Builder | Medium | Medium | `orchestration/core/dynamic_builder.py` |
| 3 | Workflow Factory | Low | Low | `orchestration/core/dynamic_builder.py` |
| 4 | State Backend (Redis) | Low | Low | `orchestration/core/state.py` |
| 5 | Circuit Breaker | Low | Low | `orchestration/retry/policies.py` |

**Phase 5 Goals:**
- Add workflow versioning
- Enable dynamic workflow generation
- Support multiple state backends
- Implement advanced fault tolerance

---

## 12. Integration Points with Existing Code

### 12.1 Current Code Integration

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/integration_example.py

"""
Example integration of new orchestration with existing ResilienceAI code.
"""

from orchestration.core.dag import DAG, Task, TaskStatus, TaskResult
from orchestration.core.executor import ParallelExecutor, ExecutionConfig, ExecutorType
from orchestration.core.state import StateManager, StateBackend
from orchestration.retry.policies import ExponentialBackoffRetry


def integrate_with_existing_pipeline():
    """
    Integrate new orchestration with existing run_pipeline.py.
    """
    from orchestration.dags.data_pipeline_dag import DataPipelineDAG, DataPipelineConfig
    
    # Create pipeline DAG
    config = DataPipelineConfig(
        force_download=False,
        parallel_downloads=True,
        max_retries=3
    )
    
    pipeline = DataPipelineDAG(config)
    dag = pipeline.get_dag()
    
    # Create executor with parallel execution
    executor_config = ExecutionConfig(
        executor_type=ExecutorType.THREAD,
        max_workers=4,
        fail_fast=False
    )
    
    # Use SQLite for state persistence
    state_manager = StateManager(
        backend=StateBackend.SQLITE,
        connection_string="./workflow_state.db"
    )
    
    executor = ParallelExecutor(executor_config, state_manager)
    
    # Execute pipeline
    workflow_state = executor.execute_dag(dag)
    
    print(f"Pipeline status: {workflow_state.status}")
    print(f"Execution time: {(workflow_state.end_time - workflow_state.start_time).total_seconds():.2f}s")
    
    return workflow_state


def integrate_with_existing_agent_orchestrator():
    """
    Integrate new orchestration with existing agent orchestrator.
    """
    from orchestration.dags.agent_pipeline_dag import AgentPipelineDAG, AgentPipelineConfig
    
    # Create agent pipeline DAG
    config = AgentPipelineConfig(
        max_parallel_agents=4,
        enable_multi_agent=True,
        synthesis_timeout=30
    )
    
    pipeline = AgentPipelineDAG(config)
    dag = pipeline.get_dag()
    
    # Execute with query context
    executor_config = ExecutionConfig(
        executor_type=ExecutorType.THREAD,
        max_workers=4
    )
    
    executor = ParallelExecutor(executor_config)
    
    initial_context = {
        "query": "Which Missouri counties are most vulnerable?",
        "state": "MO"
    }
    
    workflow_state = executor.execute_dag(dag, initial_context)
    
    # Extract response from context
    response = workflow_state.context.get("format_response", {}).get("data", {}).get("response", "")
    
    print(f"Agent response: {response}")
    
    return workflow_state


def integrate_with_realtime_pipeline():
    """
    Integrate new orchestration with existing realtime pipeline.
    """
    from orchestration.dags.realtime_pipeline_dag import RealtimePipelineDAG
    
    # Create realtime pipeline DAG
    pipeline = RealtimePipelineDAG()
    dag = pipeline.get_dag()
    
    # Execute with event-driven scheduling
    executor_config = ExecutionConfig(
        executor_type=ExecutorType.THREAD,
        max_workers=2
    )
    
    executor = ParallelExecutor(executor_config)
    
    # Run continuously
    import time
    while True:
        workflow_state = executor.execute_dag(dag)
        print(f"Realtime cycle complete: {workflow_state.status}")
        time.sleep(60)  # Run every minute


# Backward compatibility wrapper
def run_pipeline_backward_compatible(steps=None, force_download=False):
    """
    Backward-compatible wrapper for existing run_pipeline.py.
    
    Maintains the same interface as the original function.
    """
    from orchestration.dags.data_pipeline_dag import DataPipelineDAG, DataPipelineConfig
    from orchestration.core.executor import ParallelExecutor, ExecutionConfig, ExecutorType
    
    # Map old step names to new DAG
    step_mapping = {
        "download": ["download_hifld", "download_cms", "download_fema", "download_census", "download_centroids"],
        "features": ["feature_engineering"],
        "eda": ["eda_statistics", "eda_visualizations", "eda_correlation"],
        "train": ["train_models"],
        "agent": ["agent_config"]
    }
    
    # Determine which tasks to run
    if steps is None:
        steps = ["download", "features", "eda", "train", "agent"]
    
    # Create DAG
    config = DataPipelineConfig(force_download=force_download)
    pipeline = DataPipelineDAG(config)
    dag = pipeline.get_dag()
    
    # Execute
    executor_config = ExecutionConfig(
        executor_type=ExecutorType.THREAD,
        max_workers=4
    )
    
    executor = ParallelExecutor(executor_config)
    workflow_state = executor.execute_dag(dag)
    
    # Return compatible result
    return {
        "status": workflow_state.status,
        "execution_time": (workflow_state.end_time - workflow_state.start_time).total_seconds(),
        "tasks_completed": len([t for t in workflow_state.task_states.values() if t.status == "success"]),
        "workflow_id": workflow_state.workflow_id
    }


if __name__ == "__main__":
    # Test integration
    result = integrate_with_existing_pipeline()
    print(f"Integration test result: {result.status}")
```

---

## 13. Configuration Files

### 13.1 Orchestration Configuration

```yaml
# File: /mnt/okcomputer/output/resilience_ai_analysis/config/orchestration.yaml

# ResilienceAI Orchestration Configuration

# Execution Settings
execution:
  default_executor: thread  # thread, process, async
  max_workers: 4
  timeout: 300
  fail_fast: false
  continue_on_error: true

# State Management
state:
  backend: sqlite  # memory, file, sqlite, redis, postgres
  connection_string: "./workflow_state.db"
  retention_hours: 168  # 7 days

# Retry Policies
retry:
  default_policy: exponential_backoff
  max_retries: 3
  base_delay: 1.0
  exponential_base: 2.0
  max_delay: 300.0
  jitter: true

# Scheduling
scheduling:
  enabled: true
  scheduler: cron  # cron, event, interval
  check_interval: 1  # seconds

# Monitoring
monitoring:
  enabled: true
  metrics_retention_hours: 24
  event_retention_count: 10000
  export_format: json  # json, prometheus

# Alerting
alerts:
  enabled: true
  channels:
    - type: email
      recipients: ["admin@resilienceai.org"]
    - type: webhook
      url: "https://alerts.resilienceai.org/webhook"
  rules:
    - name: workflow_failed
      condition: "workflow.status == 'failed'"
    - name: slow_task
      condition: "task.duration_ms > 60000"
    - name: high_retry_count
      condition: "task.retry_count > 2"

# DAG Defaults
dag_defaults:
  catchup: false
  max_active_runs: 1
  concurrency: 16
  tags: ["resilienceai"]

# Integration
integration:
  airflow:
    enabled: false
    dag_folder: "/opt/airflow/dags"
  prefect:
    enabled: false
    api_url: "http://localhost:4200"
```

### 13.2 Airflow Configuration

```python
# File: /mnt/okcomputer/output/resilience_ai_analysis/config/airflow.cfg

[core]
# The home folder for airflow
dags_folder = /opt/airflow/dags
base_log_folder = /opt/airflow/logs
remote_logging = False
executor = LocalExecutor
parallelism = 32
dag_concurrency = 16
max_active_runs_per_dag = 1

[scheduler]
# Task instance listen interval
job_heartbeat_sec = 5
scheduler_heartbeat_sec = 5
min_file_process_interval = 30
dag_dir_list_interval = 300

[webserver]
base_url = http://localhost:8080
web_server_host = 0.0.0.0
web_server_port = 8080

[database]
sql_alchemy_conn = sqlite:////opt/airflow/airflow.db

[logging]
base_log_folder = /opt/airflow/logs
logging_level = INFO
```

### 13.3 Prefect Configuration

```yaml
# File: /mnt/okcomputer/output/resilience_ai_analysis/config/prefect.yaml

# Prefect Configuration for ResilienceAI

name: resilienceai

prefect-version: 2.14.0

# Build configuration
build:
  - prefect_docker.deployments.steps.build_docker_image:
      id: build-image
      requires: prefect-docker>=0.3.0
      image_name: resilienceai
      tag: latest
      dockerfile: Dockerfile

# Push configuration
push:
  - prefect_docker.deployments.steps.push_docker_image:
      requires: prefect-docker>=0.3.0
      image_name: resilienceai
      tag: latest

# Pull configuration
pull:
  - prefect.deployments.steps.set_working_directory:
      directory: /opt/resilienceai

# Deployments
deployments:
  - name: data-pipeline
    version: 1.0.0
    tags: ["data", "pipeline"]
    description: "ResilienceAI data pipeline"
    entrypoint: flows/data_pipeline_flow.py:data_pipeline_flow
    parameters:
      force_download: false
    work_pool:
      name: default
      work_queue_name: default
    schedule:
      cron: "0 2 * * *"
      timezone: America/Chicago
    
  - name: agent-orchestration
    version: 1.0.0
    tags: ["agent", "orchestration"]
    description: "ResilienceAI agent orchestration"
    entrypoint: flows/agent_pipeline_flow.py:agent_orchestration_flow
    parameters:
      query: "Which counties are most vulnerable?"
    work_pool:
      name: default
      work_queue_name: agents
```

---

## 14. Summary and Recommendations

### 14.1 Key Improvements Over Current System

| Aspect | Current | Proposed | Benefit |
|--------|---------|----------|---------|
| Execution | Sequential | Parallel | 3-5x faster execution |
| Dependencies | None | Full DAG support | Correct execution order |
| State | In-memory | Persistent | Recovery, debugging |
| Retries | None | Configurable policies | Improved reliability |
| Scheduling | Manual | Cron/Event-driven | Automation |
| Monitoring | None | Full observability | Better visibility |
| Versioning | None | Semantic versioning | Change management |
| Integration | None | Airflow/Prefect | Enterprise deployment |

### 14.2 Architecture Decisions

1. **DAG-Based Design**: Provides clear dependency visualization and parallel execution opportunities
2. **Pluggable Executors**: Supports thread, process, and async execution models
3. **Multiple State Backends**: From in-memory (development) to Redis/Postgres (production)
4. **Retry Policies**: Configurable exponential backoff with jitter
5. **Integration Adapters**: Export to Airflow/Prefect without code changes

### 14.3 Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Backward compatibility | Maintain existing function signatures |
| Performance regression | Benchmark before/after, configurable parallelism |
| State corruption | Multiple backend options, backup/restore |
| Complexity increase | Incremental rollout, clear documentation |
| Integration issues | Adapters with fallback to local execution |

### 14.4 Success Metrics

- **Execution Time**: Reduce pipeline runtime by 50%
- **Reliability**: Achieve 99.5% success rate with retries
- **Observability**: Full visibility into workflow execution
- **Maintainability**: Clear DAG visualization and versioning
- **Scalability**: Support for 10x data volume increase

---

## 15. Generated Files Summary

| File Path | Description |
|-----------|-------------|
| `/mnt/okcomputer/output/resilience_ai_analysis/30_orchestration_workflow.md` | This comprehensive orchestration design document |
| `/mnt/okcomputer/output/resilience_ai_analysis/orchestration/core/dag.py` | Core DAG implementation |
| `/mnt/okcomputer/output/resilience_ai_analysis/orchestration/core/state.py` | State management system |
| `/mnt/okcomputer/output/resilience_ai_analysis/orchestration/core/executor.py` | Parallel execution engine |
| `/mnt/okcomputer/output/resilience_ai_analysis/orchestration/retry/policies.py` | Retry policies and circuit breaker |
| `/mnt/okcomputer/output/resilience_ai_analysis/orchestration/schedulers/cron_scheduler.py` | Cron-based scheduler |
| `/mnt/okcomputer/output/resilience_ai_analysis/orchestration/monitors/workflow_monitor.py` | Monitoring and observability |
| `/mnt/okcomputer/output/resilience_ai_analysis/orchestration/dags/data_pipeline_dag.py` | Data pipeline DAG definition |
| `/mnt/okcomputer/output/resilience_ai_analysis/orchestration/dags/agent_pipeline_dag.py` | Agent pipeline DAG definition |
| `/mnt/okcomputer/output/resilience_ai_analysis/orchestration/versioning/version_manager.py` | Workflow versioning |
| `/mnt/okcomputer/output/resilience_ai_analysis/orchestration/core/dynamic_builder.py` | Dynamic workflow generation |
| `/mnt/okcomputer/output/resilience_ai_analysis/orchestration/engines/airflow_engine.py` | Airflow integration adapter |
| `/mnt/okcomputer/output/resilience_ai_analysis/dags/data_pipeline.py` | Airflow DAG export |
| `/mnt/okcomputer/output/resilience_ai_analysis/flows/data_pipeline_flow.py` | Prefect flow export |
| `/mnt/okcomputer/output/resilience_ai_analysis/config/orchestration.yaml` | Orchestration configuration |
| `/mnt/okcomputer/output/resilience_ai_analysis/integration_example.py` | Integration examples |

---

*Document generated for ResilienceAI Orchestration Enhancement*
*Version: 1.0.0*
*Date: 2024*
