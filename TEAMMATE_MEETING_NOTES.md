# Teammate Meeting Integration Requirements
**Date:** February 17, 2026  
**Attendees:** 6 team members  
**Status:** Requirements for implementation

---

## 1. LLM Integration for Local Inference

### Requirement
Differentiate the project by using LLMs (Hugging Face or other providers) for **local inference of data insights**.

### Implementation Approach

#### Option A: Hugging Face Transformers (Local)
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load model for local inference
model_name = "microsoft/DialoGPT-medium"  # or other open model
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Local inference function
def generate_insight(prompt, context_data):
    """Generate data insights using local LLM"""
    enriched_prompt = f"""Based on the following climate and vulnerability data:
{context_data}

User Question: {prompt}

Provide a concise, actionable insight:"""
    
    inputs = tokenizer(enriched_prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=512)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response
```

#### Option B: Ollama (Local Container)
```python
import ollama

# Local inference with Ollama
def generate_insight_ollama(prompt, context_data):
    response = ollama.generate(
        model='llama2:7b',  # or mistral, codellama, etc.
        prompt=f"""Analyze this disaster resilience data and answer:
{context_data}

Question: {prompt}"""
    )
    return response['response']
```

#### Option C: llama.cpp (Edge/Local)
- GGUF format models for CPU inference
- No GPU required
- Privacy-preserving (no data leaves machine)

### Recommended Models
| Model | Size | Use Case | Provider |
|-------|------|----------|----------|
| Llama 2 7B | 7B | General insights | Hugging Face |
| Mistral 7B | 7B | Fast inference | Hugging Face |
| CodeLlama 7B | 7B | Data analysis | Hugging Face |
| Phi-2 | 2.7B | Edge deployment | Microsoft |
| Orca 2 | 7B | Reasoning tasks | Microsoft |

### Differentiation Strategy
- **Privacy-first:** All inference happens locally, no data sent to cloud
- **Cost-effective:** No per-token API costs
- **Customizable:** Fine-tune on domain-specific disaster resilience data
- **Resilient:** Works offline during disasters when connectivity is limited

---

## 2. Archia Agent Orchestration

### Requirement
Deeply integrate Archia agents with **sophisticated orchestration** where:
1. User prompt is taken in
2. Crafted into a response to their question
3. **Hyperdimensional vector space relationships** highlighted where relevant

### Architecture Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ARCHIA AGENT ORCHESTRATION                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐     ┌──────────────────┐     ┌──────────────┐     │
│  │   User       │────▶│  Query           │────▶│  Intent      │     │
│  │   Prompt     │     │  Parser          │     │  Classifier  │     │
│  └──────────────┘     └──────────────────┘     └──────┬───────┘     │
│                                                        │              │
│                                                        ▼              │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                 AGENT ORCHESTRATION LAYER                     │    │
│  │                                                                │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │    │
│  │  │ Monitoring  │  │ Prediction  │  │ Response    │           │    │
│  │  │ Agent       │  │ Agent       │  │ Agent       │           │    │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘           │    │
│  │         │                │                │                   │    │
│  │         └────────────────┼────────────────┘                   │    │
│  │                          │                                    │    │
│  │                          ▼                                    │    │
│  │  ┌──────────────────────────────────────────────────────┐    │    │
│  │  │           LangGraph State Machine                     │    │    │
│  │  │  - Route to appropriate agent(s)                      │    │    │
│  │  │  - Parallel execution where possible                  │    │    │
│  │  │  - Sequential dependencies                            │    │    │
│  │  └──────────────────────┬───────────────────────────────┘    │    │
│  │                         │                                     │    │
│  │                         ▼                                     │    │
│  │  ┌──────────────────────────────────────────────────────┐    │    │
│  │  │      HYPERDIMENSIONAL VECTOR SPACE LAYER              │    │    │
│  │  │                                                        │    │    │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │    │    │
│  │  │  │ Climate     │  │ Health      │  │ Infrastructure│   │    │    │
│  │  │  │ Vectors     │  │ Vectors     │  │ Vectors       │   │    │    │
│  │  │  │ (768-dim)   │  │ (768-dim)   │  │ (768-dim)     │   │    │    │
│  │  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │    │    │
│  │  │         │                │                │           │    │    │
│  │  │         └────────────────┼────────────────┘           │    │    │
│  │  │                          │                            │    │    │
│  │  │                          ▼                            │    │    │
│  │  │  ┌─────────────────────────────────────────────────┐  │    │    │
│  │  │  │  Cross-Domain Similarity Search                  │  │    │    │
│  │  │  │  - Find similar patterns across domains          │  │    │    │
│  │  │  │  - Highlight unexpected relationships            │  │    │    │
│  │  │  │  - Surface hidden correlations                   │  │    │    │
│  │  │  └─────────────────────────────────────────────────┘  │    │    │
│  │  └──────────────────────────────────────────────────────┘    │    │
│  │                                                               │    │
│  └───────────────────────────────────────────────────────────────┘    │
│                                                                        │
│                          │                                             │
│                          ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                    RESPONSE CRAFTER                              │  │
│  │                                                                  │  │
│  │  1. Synthesize agent outputs                                    │  │
│  │  2. Inject hyperdimensional insights                            │  │
│  │  3. Format for user consumption                                 │  │
│  │  4. Highlight vector space relationships                        │  │
│  └──────────────────────┬──────────────────────────────────────────┘  │
│                         │                                              │
│                         ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                    USER RESPONSE                                 │  │
│  │  - Direct answer to question                                     │  │
│  │  - Relevant hyperdimensional relationships highlighted           │  │
│  │  - Suggested follow-up queries                                   │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Hyperdimensional Vector Space Implementation

```python
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

class HyperdimensionalVectorSpace:
    """
    Manages vector embeddings across multiple data domains
    and surfaces cross-domain relationships
    """
    
    def __init__(self):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.climate_index = None
        self.health_index = None
        self.infrastructure_index = None
        self.cross_domain_mappings = {}
    
    def encode_climate_data(self, climate_features):
        """Encode climate data into vector space"""
        descriptions = [
            f"County {row['county']} has {row['flood_risk']} flood risk, "
            f"{row['heat_index']} heat index, precipitation trend {row['precip_trend']}"
            for _, row in climate_features.iterrows()
        ]
        vectors = self.encoder.encode(descriptions)
        self.climate_index = faiss.IndexFlatIP(vectors.shape[1])
        self.climate_index.add(vectors)
        return vectors
    
    def encode_health_data(self, health_features):
        """Encode health data into vector space"""
        descriptions = [
            f"County {row['county']} has SVI {row['svi']}, "
            f"{row['elderly_pct']}% elderly, {row['chronic_disease_rate']} chronic disease rate"
            for _, row in health_features.iterrows()
        ]
        vectors = self.encoder.encode(descriptions)
        self.health_index = faiss.IndexFlatIP(vectors.shape[1])
        self.health_index.add(vectors)
        return vectors
    
    def find_cross_domain_similarities(self, query_vector, top_k=5):
        """Find similar patterns across different domains"""
        # Search climate index
        climate_scores, climate_ids = self.climate_index.search(
            np.array([query_vector]), top_k
        )
        
        # Search health index
        health_scores, health_ids = self.health_index.search(
            np.array([query_vector]), top_k
        )
        
        # Find unexpected correlations (high climate risk + high health vulnerability)
        cross_domain_matches = []
        for c_id, c_score in zip(climate_ids[0], climate_scores[0]):
            for h_id, h_score in zip(health_ids[0], health_scores[0]):
                if c_id == h_id:  # Same county
                    cross_domain_matches.append({
                        'county_id': c_id,
                        'climate_score': float(c_score),
                        'health_score': float(h_score),
                        'composite_risk': float(c_score * h_score)
                    })
        
        return sorted(cross_domain_matches, 
                     key=lambda x: x['composite_risk'], 
                     reverse=True)
    
    def highlight_relationships(self, query, response_context):
        """Highlight relevant hyperdimensional relationships"""
        query_vector = self.encoder.encode([query])[0]
        
        # Find similar patterns
        similarities = self.find_cross_domain_similarities(query_vector)
        
        # Generate insight about relationships
        if similarities:
            top_match = similarities[0]
            relationship_insight = (
                f"\n\n🔍 **Hyperdimensional Insight:** "
                f"This county shows unexpected correlation between "
                f"climate vulnerability (score: {top_match['climate_score']:.2f}) "
                f"and health vulnerability (score: {top_match['health_score']:.2f}). "
                f"Similar patterns found in {len(similarities)} other counties."
            )
            return response_context + relationship_insight
        
        return response_context

# Usage in Archia agent
vector_space = HyperdimensionalVectorSpace()
vector_space.encode_climate_data(climate_df)
vector_space.encode_health_data(health_df)
```

### Archia Agent Configuration

```toml
# ~/.archia/agents/resilience_orchestrator.toml
name = "resilience_orchestrator"
model_name = "claude-sonnet-4-5-20250929"
enabled = true
description = "Orchestrates multi-agent analysis with hyperdimensional insights"

system_prompt = """
You are the ResilienceAI Orchestrator Agent. Your role is to:

1. Parse user queries about disaster resilience, climate risk, and vulnerability
2. Route to appropriate specialized agents (Monitoring, Prediction, Response)
3. Synthesize multi-agent outputs into coherent responses
4. Highlight hyperdimensional vector space relationships when relevant

When responding:
- Provide direct, actionable answers
- Include specific data points and metrics
- Highlight unexpected correlations or patterns
- Suggest follow-up questions for deeper analysis

Always consider the intersection of:
- Climate trends (precipitation, temperature, extremes)
- Health vulnerability (SVI, demographics, disease burden)
- Infrastructure exposure (power grid, hospitals, transportation)
"""

[mcp_tools]
monitoring_agent = ["get_real_time_alerts", "check_weather_status"]
prediction_agent = ["predict_flood_risk", "forecast_heat_events"]
response_agent = ["generate_evacuation_plan", "allocate_resources"]
vector_space = ["query_similar_patterns", "find_correlations"]
llm_inference = ["generate_insight", "summarize_data"]
```

### LangGraph State Machine

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional

class ResilienceState(TypedDict):
    user_query: str
    parsed_intent: dict
    agent_outputs: dict
    vector_insights: Optional[list]
    crafted_response: Optional[str]

def parse_query(state: ResilienceState):
    """Parse user query into structured intent"""
    query = state["user_query"]
    # Use local LLM for intent classification
    intent = classify_intent_local(query)
    return {"parsed_intent": intent}

def route_to_agents(state: ResilienceState):
    """Route to appropriate agents based on intent"""
    intent = state["parsed_intent"]
    
    # Parallel agent execution
    outputs = {}
    if intent["needs_monitoring"]:
        outputs["monitoring"] = monitoring_agent.query(intent)
    if intent["needs_prediction"]:
        outputs["prediction"] = prediction_agent.query(intent)
    if intent["needs_response"]:
        outputs["response"] = response_agent.query(intent)
    
    return {"agent_outputs": outputs}

def query_vector_space(state: ResilienceState):
    """Query hyperdimensional vector space for insights"""
    query = state["user_query"]
    
    # Encode query
    query_vector = vector_space.encoder.encode([query])[0]
    
    # Find cross-domain similarities
    insights = vector_space.find_cross_domain_similarities(query_vector)
    
    return {"vector_insights": insights}

def craft_response(state: ResilienceState):
    """Craft final response with highlighted relationships"""
    agent_outputs = state["agent_outputs"]
    vector_insights = state.get("vector_insights", [])
    
    # Use local LLM to synthesize response
    context = format_agent_outputs(agent_outputs)
    
    # Inject vector space insights
    if vector_insights:
        context += format_vector_insights(vector_insights)
    
    # Generate response
    response = generate_insight_local(state["user_query"], context)
    
    return {"crafted_response": response}

# Build graph
workflow = StateGraph(ResilienceState)
workflow.add_node("parse", parse_query)
workflow.add_node("route", route_to_agents)
workflow.add_node("vector_query", query_vector_space)
workflow.add_node("craft", craft_response)

workflow.set_entry_point("parse")
workflow.add_edge("parse", "route")
workflow.add_edge("parse", "vector_query")
workflow.add_edge("route", "craft")
workflow.add_edge("vector_query", "craft")
workflow.add_edge("craft", END)

orchestrator = workflow.compile()

# Usage
result = orchestrator.invoke({
    "user_query": "Which counties in Missouri face the highest compound risk from flooding and health vulnerability?"
})
print(result["crafted_response"])
```

---

## 3. Integration Checklist

### Phase 1: Local LLM Setup
- [ ] Select and download model (Mistral 7B or Llama 2 7B)
- [ ] Set up inference pipeline (Transformers/Ollama/llama.cpp)
- [ ] Create insight generation functions
- [ ] Test with sample queries

### Phase 2: Vector Space Implementation
- [ ] Set up sentence transformer encoder
- [ ] Create FAISS indices for each data domain
- [ ] Implement cross-domain similarity search
- [ ] Build relationship highlighting logic

### Phase 3: Archia Integration
- [ ] Configure Archia agent with MCP tools
- [ ] Implement LangGraph state machine
- [ ] Connect vector space to agent orchestration
- [ ] Test end-to-end query flow

### Phase 4: Response Crafting
- [ ] Build response synthesis pipeline
- [ ] Add hyperdimensional insight injection
- [ ] Format for user consumption
- [ ] Add suggested follow-up queries

---

## 4. Technical Requirements

### Compute Requirements
| Component | CPU | RAM | GPU | Notes |
|-----------|-----|-----|-----|-------|
| Local LLM (7B) | 8+ cores | 16GB | Optional | Works on CPU |
| Vector Encoding | 4+ cores | 8GB | Optional | Batch processing |
| FAISS Index | 4+ cores | 16GB | Optional | For 3,000+ counties |
| Full System | 16+ cores | 32GB | Recommended | For concurrent users |

### Dependencies
```
transformers>=4.30.0
sentence-transformers>=2.2.0
faiss-cpu>=1.7.4  # or faiss-gpu
langgraph>=0.0.20
ollama>=0.1.0  # if using Ollama
```

### Model Downloads
```bash
# Hugging Face
huggingface-cli download microsoft/DialoGPT-medium

# Ollama
ollama pull mistral:7b
ollama pull llama2:7b

# llama.cpp (GGUF)
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

---

## 5. Demo Scenario

**User Query:** "Which Missouri counties have the highest compound climate-health risk that isn't obvious from looking at either factor alone?"

**System Response Flow:**
1. **Parse:** Intent = compound risk analysis, domains = climate + health
2. **Route:** 
   - Climate Agent: Calculate flood + heat trends
   - Health Agent: Retrieve SVI + disease burden
3. **Vector Query:** Find counties with high cross-domain similarity
4. **Craft Response:**
   ```
   Boone County, MO shows the highest compound risk with:
   - Climate: 23% increase in extreme precipitation (1990-2023)
   - Health: SVI 0.72 (high vulnerability)
   
   🔍 Hyperdimensional Insight: This county clusters with 12 others 
   showing similar "hidden risk" patterns where infrastructure age 
   (avg 47 years) compounds climate vulnerability.
   
   Suggested follow-ups:
   - Which infrastructure investments would reduce this risk?
   - How does Boone County compare to similar counties nationally?
   ```

---

## 6. Next Steps

1. **Immediate:** Select local LLM approach (Hugging Face vs Ollama vs llama.cpp)
2. **Day 1:** Set up vector space with current data
3. **Day 2:** Integrate with Archia agent configuration
4. **Day 3:** Test with demo queries and refine
5. **Day 4:** Polish response crafting and presentation

---

*Meeting Notes Compiled: February 17, 2026*
*Integration Status: Ready for implementation*
