# ResilienceAI: Comprehensive LLM & AI Integration Enhancement Design

## Executive Summary

This document provides a comprehensive analysis of the current LLM integration in ResilienceAI and designs extensive enhancements for AI-powered disaster vulnerability assessment. The architecture supports multi-modal AI (text, data, maps), RAG (Retrieval-Augmented Generation), vector embeddings, conversation memory, and multi-LLM provider orchestration.

---

## 1. Current State Analysis

### 1.1 Existing LLM Architecture

```
ResilienceAI LLM Stack (Current)
================================
┌─────────────────────────────────────────────────────────────────┐
│                        Application Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  modern_ui  │  │  Dashboard  │  │  Agent Orchestrator     │  │
│  │   (Streamlit)│  │  Monitor    │  │  (45 MCP Tools)         │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
└─────────┼────────────────┼─────────────────────┼────────────────┘
          │                │                     │
┌─────────┼────────────────┼─────────────────────┼────────────────┐
│         ▼                ▼                     ▼                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              LLM Interface (llm_interface.py)             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │   │
│  │  │ LLMManager  │  │ LLMConfig   │  │ LLMMessage      │   │   │
│  │  │ LLMResponse │  │ BaseProvider│  │ ProviderFactory │   │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌───────────────────────────┼───────────────────────────────┐   │
│  │         LLM Providers (llm_providers/)                     │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │   │
│  │  │  Ollama  │ │ LM Studio│ │HuggingFace│ │  llama.cpp   │  │   │
│  │  │ (Default)│ │          │ │          │ │              │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │   │
│  └───────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│              Vector Space (vector_space.py)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Sentence Transformers (384-dim) + FAISS Index           │   │
│  │  Multi-domain encoding: climate, health, infrastructure  │   │
│  │  Similarity search, anomaly detection                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Current Capabilities

| Component | Status | Description |
|-----------|--------|-------------|
| LLM Interface | ✅ Implemented | Abstract base with 4 providers |
| Vector Embeddings | ✅ Implemented | 384-dim sentence transformers |
| FAISS Index | ✅ Implemented | Similarity search for counties |
| Agent Orchestration | ✅ Implemented | LangGraph-based routing |
| MCP Tools | ✅ 45 Tools | Weather, geospatial, health, etc. |
| Streaming | ⚠️ Partial | Basic async support |
| Conversation Memory | ❌ Missing | No persistent chat history |
| RAG System | ⚠️ Basic | Vector search without LLM integration |
| Multi-modal | ⚠️ Partial | Text + data, limited image support |
| Fine-tuning | ❌ Missing | No domain adaptation |

### 1.3 File Structure (Current)

```
src/
├── llm_interface.py          # Abstract LLM interface
├── archia_client.py          # Archia Cloud API client
├── vector_space.py           # FAISS + embeddings
├── llm_providers/
│   ├── __init__.py           # Provider registration
│   ├── ollama.py             # Ollama provider
│   ├── lmstudio.py           # LM Studio provider
│   ├── huggingface.py        # HuggingFace provider
│   └── llamacpp.py           # llama.cpp provider
├── agents/
│   ├── base_agent.py         # Base agent class
│   ├── langgraph_flow.py     # LangGraph orchestration
│   ├── orchestrator.py       # Agent orchestrator
│   ├── climate_agent.py      # Climate analysis agent
│   ├── vulnerability_agent.py # Vulnerability assessment
│   ├── planning_agent.py     # Intervention planning
│   └── realtime_agent.py     # Real-time monitoring
└── agent_orchestrator.py     # MCP tool orchestration
```

---

## 2. Proposed RAG Architecture

### 2.1 Enhanced RAG System Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ResilienceAI RAG Architecture                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     Query Processing Layer                       │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │    │
│  │  │Query Router  │  │Intent Classifier│  │Query Expansion   │  │    │
│  │  │& Decomposer  │  │(LLM-based)     │  │& Reformulation   │  │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │    │
│  └─────────┼─────────────────┼─────────────────────┼──────────────┘    │
│            │                 │                     │                    │
│            ▼                 ▼                     ▼                    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Multi-Modal Retrieval Layer                   │    │
│  │                                                                  │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │    │
│  │  │  Dense Retrieval │  │  Sparse Retrieval │  │  Hybrid Search   │ │    │
│  │  │  (Vector DB)     │  │  (BM25/TF-IDF)   │  │  (RRF Fusion)    │ │    │
│  │  │                  │  │                  │  │                  │ │    │
│  │  │ • County vectors │  │ • County names   │  │ • Combined       │ │    │
│  │  │ • Disaster docs  │  │ • FEMA codes     │  │   ranking        │ │    │
│  │  │ • Health data    │  │ • State codes    │  │ • Re-ranking     │ │    │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬─────────┘ │    │
│  └───────────┼────────────────────┼────────────────────┼───────────┘    │
│              │                    │                    │                 │
│              ▼                    ▼                    ▼                 │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Context Assembly Layer                        │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │    │
│  │  │Re-ranker     │  │Context       │  │Multi-modal Context   │  │    │
│  │  │(Cross-encoder)│  │Compressor    │  │Assembler (text+data) │  │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │    │
│  └─────────┼─────────────────┼─────────────────────┼──────────────┘    │
│            │                 │                     │                    │
│            ▼                 ▼                     ▼                    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Generation Layer                              │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │    │
│  │  │Prompt        │  │LLM Engine    │  │Response              │  │    │
│  │  │Engineering   │  │(Multi-provider)│  │Post-processing     │  │    │
│  │  │(Templates)   │  │              │  │• Citation            │  │    │
│  │  │              │  │              │  │• Fact-checking       │  │    │
│  │  └─────────────┘  └──────────────┘  └──────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 RAG Implementation Components

```python
# src/rag/__init__.py
"""ResilienceAI RAG System - Retrieval-Augmented Generation"""

from .query_processor import QueryProcessor, QueryIntent
from .retriever import HybridRetriever, DenseRetriever, SparseRetriever
from .context_assembler import ContextAssembler, ContextCompression
from .citation_manager import CitationManager, SourceAttribution
from .response_generator import ResponseGenerator, ResponseValidator

__all__ = [
    'QueryProcessor', 'QueryIntent',
    'HybridRetriever', 'DenseRetriever', 'SparseRetriever',
    'ContextAssembler', 'ContextCompression',
    'CitationManager', 'SourceAttribution',
    'ResponseGenerator', 'ResponseValidator'
]
```


```python
# src/rag/query_processor.py
"""Query processing and intent classification for RAG."""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum
import re

class QueryIntent(Enum):
    """Classification of user query intents."""
    COUNTY_LOOKUP = "county_lookup"
    VULNERABILITY_ANALYSIS = "vulnerability_analysis"
    DISASTER_HISTORY = "disaster_history"
    INTERVENTION_PLANNING = "intervention_planning"
    COMPARISON = "comparison"
    TREND_ANALYSIS = "trend_analysis"
    REALTIME_ALERT = "realtime_alert"
    GENERAL_INFO = "general_info"

@dataclass
class ProcessedQuery:
    """Structured representation of processed query."""
    original_query: str
    intent: QueryIntent
    confidence: float
    entities: Dict[str, Any]
    expanded_queries: List[str]
    filters: Dict[str, Any]
    temporal_context: Optional[Dict[str, str]]

class QueryProcessor:
    """Process and enhance natural language queries."""
    
    INTENT_PATTERNS = {
        QueryIntent.COUNTY_LOOKUP: [
            r'\b(county|parish|borough)\s+in\s+(\w+)',
            r'\b(what|tell me about|show)\s+(.+?)\s+(county|parish)',
            r'\b(FIPS|fips)\s*[:\-]?\s*(\d{5})',
        ],
        QueryIntent.VULNERABILITY_ANALYSIS: [
            r'\b(vulnerable|vulnerability|risk|at risk|exposed)\b',
            r'\b(health|medical|hospital|facility)\s+(gap|shortage|access)\b',
            r'\b(resilience|preparedness|capacity)\b',
        ],
        QueryIntent.DISASTER_HISTORY: [
            r'\b(disaster|flood|hurricane|tornado|fire|storm)\s+(history|past|previous)\b',
            r'\b(FEMA|declaration|incident)\s+(\d{4}|number|id)\b',
            r'\b(how many|frequency|often)\s+disaster',
        ],
        QueryIntent.INTERVENTION_PLANNING: [
            r'\b(intervention|mitigation|preparedness|plan)\b',
            r'\b(what should|recommend|suggest|how to improve)\b',
            r'\b(ROI|cost|benefit|invest|funding)\b',
        ],
        QueryIntent.COMPARISON: [
            r'\b(compare|versus|vs|difference between|better than)\b',
            r'\b(ranking|rank|top|bottom|highest|lowest)\b',
        ],
        QueryIntent.TREND_ANALYSIS: [
            r'\b(trend|changing|over time|increasing|decreasing)\b',
            r'\b(historical|since|from \d{4} to \d{4})\b',
        ],
        QueryIntent.REALTIME_ALERT: [
            r'\b(current|now|today|active|ongoing|alert|warning)\b',
            r'\b(NOAA|weather|flood warning|tornado watch)\b',
        ],
    }
    
    def __init__(self, llm_manager=None):
        self.llm_manager = llm_manager
        self.entity_extractor = EntityExtractor()
        
    def process(self, query: str, conversation_context: Optional[List] = None) -> ProcessedQuery:
        intent, confidence = self._classify_intent(query)
        entities = self.entity_extractor.extract(query)
        expanded = self._expand_query(query, intent)
        filters = self._extract_filters(query)
        temporal = self._extract_temporal_context(query)
        
        return ProcessedQuery(
            original_query=query, intent=intent, confidence=confidence,
            entities=entities, expanded_queries=expanded,
            filters=filters, temporal_context=temporal
        )
    
    def _classify_intent(self, query: str) -> tuple:
        query_lower = query.lower()
        scores = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = sum(1 for p in patterns if re.search(p, query_lower, re.I))
            scores[intent] = score / len(patterns) if patterns else 0
        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent]
        if confidence < 0.3 and self.llm_manager:
            best_intent, confidence = self._llm_classify(query)
        return best_intent, confidence

class EntityExtractor:
    """Extract named entities from queries."""
    
    def extract(self, query: str) -> Dict[str, Any]:
        return {
            'counties': self._extract_counties(query),
            'states': self._extract_states(query),
            'fips_codes': self._extract_fips(query),
            'disaster_types': self._extract_disaster_types(query),
            'metrics': self._extract_metrics(query),
        }
    
    def _extract_counties(self, query: str) -> List[str]:
        patterns = [
            r'([A-Za-z\s]+?)\s+(County|Parish|Borough)',
            r'(?:County|Parish|Borough)\s+of\s+([A-Za-z\s]+)',
        ]
        counties = []
        for pattern in patterns:
            matches = re.findall(pattern, query, re.I)
            for match in matches:
                counties.append(match[0].strip() if isinstance(match, tuple) else match.strip())
        return list(set(counties))
    
    def _extract_states(self, query: str) -> List[str]:
        state_abbr = re.findall(r'\b([A-Z]{2})\b', query)
        state_names = re.findall(r'\b(in|for|of)\s+([A-Za-z\s]+?)(?:\s+County|\s+State|\s*$)', query, re.I)
        return list(set(state_abbr + [s[1].strip() for s in state_names]))
    
    def _extract_fips(self, query: str) -> List[str]:
        return re.findall(r'\b(\d{5})\b', query)
    
    def _extract_disaster_types(self, query: str) -> List[str]:
        types = ['flood', 'hurricane', 'tornado', 'fire', 'storm', 'earthquake', 'drought', 'winter storm']
        return [t for t in types if t in query.lower()]
    
    def _extract_metrics(self, query: str) -> List[str]:
        metrics = ['SVI', 'vulnerability', 'risk score', 'resilience', 'hospital beds', 'uninsured']
        return [m for m in metrics if m.lower() in query.lower()]
```

---

## 3. Vector Database Design

### 3.1 Enhanced Vector Store Architecture

```python
# src/vector_store/embeddings.py
"""Embedding models for different data types."""

import numpy as np
import torch
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class EmbeddingConfig:
    model_name: str = "all-MiniLM-L6-v2"
    dimension: int = 384
    batch_size: int = 32
    device: str = "auto"
    normalize: bool = True

class CountyEmbeddingModel:
    """Generate embeddings for county data with domain-specific encoding."""
    
    DOMAIN_WEIGHTS = {
        'climate': 1.0, 'health': 1.2, 'infrastructure': 1.0,
        'socioeconomic': 0.8, 'geographic': 0.6,
    }
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        self.config = config or EmbeddingConfig()
        self._model = None
        
    def _load_model(self):
        from sentence_transformers import SentenceTransformer
        device = "cuda" if torch.cuda.is_available() else "cpu" if self.config.device == "auto" else self.config.device
        self._model = SentenceTransformer(self.config.model_name, device=device)
    
    def encode(self, county_data: List[Dict[str, Any]]) -> np.ndarray:
        if self._model is None:
            self._load_model()
        texts = [self._county_to_text(c) for c in county_data]
        embeddings = self._model.encode(texts, batch_size=self.config.batch_size, convert_to_numpy=True)
        if self.config.normalize:
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings
    
    def encode_query(self, query: str) -> np.ndarray:
        if self._model is None:
            self._load_model()
        enhanced = self._enhance_query(query)
        embedding = self._model.encode([enhanced], convert_to_numpy=True)
        if self.config.normalize:
            embedding = embedding / np.linalg.norm(embedding)
        return embedding[0]
    
    def _county_to_text(self, county: Dict[str, Any]) -> str:
        parts = [f"{county.get('county_name', 'Unknown')} County, {county.get('state', 'Unknown')}"]
        parts.append(f"FIPS: {county.get('fips', 'Unknown')}")
        if 'disaster_count' in county:
            parts.append(f"Has experienced {county['disaster_count']} disasters")
        if 'disaster_flood' in county and county['disaster_flood'] > 0:
            parts.append(f"{county['disaster_flood']} flood events")
        if 'elderly_pct' in county:
            parts.append(f"{county['elderly_pct']:.1f}% elderly population")
        if 'uninsured_pct' in county:
            parts.append(f"{county['uninsured_pct']:.1f}% uninsured")
        if 'svi_overall' in county:
            parts.append(f"Social Vulnerability Index: {county['svi_overall']:.3f}")
        return ". ".join(parts)
    
    def _enhance_query(self, query: str) -> str:
        enhancements = []
        q = query.lower()
        if 'vulnerable' in q or 'at risk' in q:
            enhancements.append("high vulnerability low resilience")
        if 'hospital' in q or 'medical' in q:
            enhancements.append("healthcare access medical facilities")
        if 'flood' in q:
            enhancements.append("flood disaster water damage")
        return f"{query}. Context: {', '.join(enhancements)}" if enhancements else query
```

### 3.2 FAISS Vector Index

```python
# src/vector_store/vector_index.py
"""Vector index implementations for similarity search."""

import numpy as np
import faiss
from typing import List, Dict, Optional
from dataclasses import dataclass
import pickle

@dataclass
class SearchResult:
    id: str
    score: float
    metadata: Dict[str, Any]
    distance: float

class FAISSIndex:
    """FAISS-based vector index with metadata filtering."""
    
    def __init__(self, dimension: int, index_type: str = "flat"):
        self.dimension = dimension
        self.index_type = index_type
        self.metadata: Dict[str, Dict] = {}
        self.id_to_index: Dict[str, int] = {}
        self.index_to_id: Dict[int, str] = {}
        self._index = None
        self._build_index()
    
    def _build_index(self):
        if self.index_type == "flat":
            self._index = faiss.IndexFlatIP(self.dimension)
        elif self.index_type == "ivf":
            quantizer = faiss.IndexFlatIP(self.dimension)
            self._index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
        elif self.index_type == "hnsw":
            self._index = faiss.IndexHNSWFlat(self.dimension, 32)
            self._index.hnsw.efConstruction = 200
    
    def add(self, embeddings: np.ndarray, ids: List[str], metadata: List[Dict]):
        faiss.normalize_L2(embeddings)
        if self.index_type == "ivf" and not self._index.is_trained:
            self._index.train(embeddings)
        self._index.add(embeddings)
        start_idx = len(self.id_to_index)
        for i, (id_, meta) in enumerate(zip(ids, metadata)):
            idx = start_idx + i
            self.id_to_index[id_] = idx
            self.index_to_id[idx] = id_
            self.metadata[id_] = meta
    
    def search(self, query: np.ndarray, k: int = 10, filters: Optional[Dict] = None) -> List[SearchResult]:
        query = query.reshape(1, -1)
        faiss.normalize_L2(query)
        scores, indices = self._index.search(query, k * 2)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            id_ = self.index_to_id.get(int(idx))
            if not id_:
                continue
            meta = self.metadata.get(id_, {})
            if filters and not self._matches_filters(meta, filters):
                continue
            results.append(SearchResult(id=id_, score=float(score), metadata=meta, distance=1.0 - float(score)))
            if len(results) >= k:
                break
        return results
    
    def _matches_filters(self, metadata: Dict, filters: Dict) -> bool:
        for key, value in filters.items():
            if key not in metadata:
                return False
            if isinstance(value, (list, tuple)):
                if metadata[key] not in value:
                    return False
            elif metadata[key] != value:
                return False
        return True
    
    def save(self, path: str):
        faiss.write_index(self._index, f"{path}.faiss")
        with open(f"{path}.meta", 'wb') as f:
            pickle.dump({'metadata': self.metadata, 'id_to_index': self.id_to_index,
                        'index_to_id': self.index_to_id, 'dimension': self.dimension}, f)
```

---

## 4. Multi-Modal AI Architecture

### 4.1 Multi-Modal Encoders

```python
# src/multimodal/encoders.py
"""Multi-modal encoders for different data types."""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class EncoderOutput:
    embedding: torch.Tensor
    attention_weights: Optional[torch.Tensor] = None

class TextEncoder(nn.Module):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", output_dim: int = 384):
        super().__init__()
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self.output_dim = output_dim
        if self.model.get_sentence_embedding_dimension() != output_dim:
            self.projection = nn.Linear(self.model.get_sentence_embedding_dimension(), output_dim)
        else:
            self.projection = None
    
    def forward(self, texts: List[str]) -> EncoderOutput:
        embeddings = self.model.encode(texts, convert_to_tensor=True)
        if self.projection:
            embeddings = self.projection(embeddings)
        return EncoderOutput(embedding=embeddings)

class DataEncoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: List[int] = [256, 128], output_dim: int = 384, dropout: float = 0.2):
        super().__init__()
        layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            layers.extend([nn.Linear(prev_dim, hidden_dim), nn.ReLU(), nn.Dropout(dropout), nn.BatchNorm1d(hidden_dim)])
            prev_dim = hidden_dim
        layers.append(nn.Linear(prev_dim, output_dim))
        self.encoder = nn.Sequential(*layers)
        self.attention = nn.MultiheadAttention(output_dim, num_heads=4)
    
    def forward(self, data: torch.Tensor) -> EncoderOutput:
        embedding = self.encoder(data)
        embedding_attended, weights = self.attention(embedding.unsqueeze(0), embedding.unsqueeze(0), embedding.unsqueeze(0))
        return EncoderOutput(embedding=embedding_attended.squeeze(0), attention_weights=weights.squeeze(0))

class GeoEncoder(nn.Module):
    def __init__(self, output_dim: int = 384):
        super().__init__()
        self.coord_encoder = nn.Sequential(nn.Linear(2, 64), nn.ReLU(), nn.Linear(64, 128))
        self.shape_encoder = nn.LSTM(input_size=2, hidden_size=64, num_layers=2, batch_first=True, bidirectional=True)
        self.projection = nn.Linear(128 + 128, output_dim)
    
    def forward(self, coordinates: torch.Tensor, shapes: Optional[List[torch.Tensor]] = None) -> EncoderOutput:
        coord_emb = self.coord_encoder(coordinates)
        if shapes:
            shape_embs = []
            for shape in shapes:
                _, (hidden, _) = self.shape_encoder(shape.unsqueeze(0))
                shape_embs.append(hidden[-1].squeeze())
            shape_emb = torch.stack(shape_embs).mean(dim=0)
        else:
            shape_emb = torch.zeros(coordinates.size(0), 128, device=coordinates.device)
        combined = torch.cat([coord_emb, shape_emb], dim=-1)
        embedding = self.projection(combined)
        return EncoderOutput(embedding=embedding)

class TemporalEncoder(nn.Module):
    def __init__(self, input_dim: int, output_dim: int = 384, num_layers: int = 2, dropout: float = 0.2):
        super().__init__()
        self.tcn = nn.ModuleList()
        for i in range(num_layers):
            dilation = 2 ** i
            self.tcn.append(nn.Conv1d(input_dim if i == 0 else output_dim // 2, output_dim // 2, kernel_size=3, dilation=dilation, padding=dilation))
        self.lstm = nn.LSTM(output_dim // 2, output_dim // 2, num_layers=num_layers, batch_first=True, dropout=dropout, bidirectional=True)
        self.projection = nn.Linear(output_dim, output_dim)
    
    def forward(self, time_series: torch.Tensor) -> EncoderOutput:
        x = time_series.transpose(1, 2)
        for conv in self.tcn:
            x = torch.relu(conv(x))
        x = x.transpose(1, 2)
        lstm_out, (hidden, _) = self.lstm(x)
        embedding = torch.cat([hidden[-2], hidden[-1]], dim=-1)
        embedding = self.projection(embedding)
        return EncoderOutput(embedding=embedding)
```

---

## 5. Advanced Prompt Engineering

### 5.1 Prompt Templates

```python
# src/prompts/templates.py
"""Prompt templates for different use cases."""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from string import Template

@dataclass
class PromptTemplate:
    system_prompt: str
    user_template: str
    output_format: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    
    def render(self, **kwargs) -> Dict[str, str]:
        system = self.system_prompt
        if self.output_format:
            system += f"\n\nOutput Format:\n{self.output_format}"
        if self.constraints:
            system += "\n\nConstraints:\n" + "\n".join(f"- {c}" for c in self.constraints)
        user = Template(self.user_template).safe_substitute(**kwargs)
        return {"system": system, "user": user}

class CountyAnalysisTemplate(PromptTemplate):
    SYSTEM_PROMPT = """You are a disaster resilience analyst specializing in county-level vulnerability assessment.

Key metrics:
- Social Vulnerability Index (SVI): Higher values indicate greater vulnerability
- Health infrastructure: Hospital beds per capita, distance to facilities
- Disaster history: Frequency and types of past events
- Socioeconomic factors: Poverty rate, uninsured percentage, elderly population

Guidelines:
- Be specific and cite data points
- Identify the most critical vulnerabilities
- Prioritize recommendations by impact and feasibility"""
    
    OUTPUT_FORMAT = """{
    "executive_summary": "2-3 sentence overview",
    "key_vulnerabilities": [{"factor": "description", "severity": "high/medium/low", "data_point": "value"}],
    "risk_assessment": {"overall_risk": "high/medium/low", "confidence": "high/medium/low"},
    "recommendations": [{"action": "description", "priority": "immediate/short-term/long-term"}]
}"""
    
    USER_TEMPLATE = """Analyze the following county data:

County: $county_name, $state
FIPS: $fips
SVI: $svi_overall
Poverty: $poverty_pct%
Uninsured: $uninsured_pct%
Elderly: $elderly_pct%
Disasters: $disaster_count

Provide a comprehensive vulnerability analysis."""
    
    def __init__(self):
        super().__init__(
            system_prompt=self.SYSTEM_PROMPT,
            user_template=self.USER_TEMPLATE,
            output_format=self.OUTPUT_FORMAT,
            constraints=["Base all claims on the provided data", "Recommendations must be specific and actionable"]
        )

# Pre-defined templates
COUNTY_ANALYSIS = CountyAnalysisTemplate()
```

---

## 6. LLM Chaining and Composition

### 6.1 Chain Base Classes

```python
# src/chains/base.py
"""Base classes for LLM chains."""

from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio

@dataclass
class ChainContext:
    input_data: Dict[str, Any]
    intermediate_results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def get(self, key: str, default=None):
        return self.intermediate_results.get(key, self.input_data.get(key, default))
    
    def set(self, key: str, value: Any):
        self.intermediate_results[key] = value

@dataclass
class ChainStep:
    name: str
    processor: Callable[[ChainContext], Any]
    output_key: str
    condition: Optional[Callable[[ChainContext], bool]] = None
    fallback: Optional[Callable[[ChainContext], Any]] = None
    
    async def execute(self, context: ChainContext) -> bool:
        try:
            if self.condition and not self.condition(context):
                return True
            result = await self._run_processor(context) if asyncio.iscoroutinefunction(self.processor) else self.processor(context)
            context.set(self.output_key, result)
            return True
        except Exception as e:
            context.errors.append(f"{self.name}: {str(e)}")
            if self.fallback:
                try:
                    result = self.fallback(context)
                    context.set(self.output_key, result)
                    return True
                except Exception as fe:
                    context.errors.append(f"{self.name} fallback: {str(fe)}")
            return False
    
    async def _run_processor(self, context: ChainContext) -> Any:
        return await self.processor(context)

class Chain(ABC):
    def __init__(self, name: str, llm_manager=None):
        self.name = name
        self.llm_manager = llm_manager
        self.steps: List[ChainStep] = []
    
    def add_step(self, step: ChainStep):
        self.steps.append(step)
    
    async def execute(self, input_data: Dict[str, Any]) -> ChainContext:
        context = ChainContext(input_data=input_data)
        for step in self.steps:
            success = await step.execute(context)
            if not success:
                context.errors.append(f"Chain halted at step: {step.name}")
                break
        return context
    
    @abstractmethod
    def build(self):
        pass
```

---

## 7. Conversation Memory Management

### 7.1 Memory Base Classes

```python
# src/memory/base.py
"""Base classes for conversation memory."""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

@dataclass
class Message:
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_name: Optional[str] = None
    tool_result: Optional[Any] = None
    
    def to_dict(self) -> Dict:
        return {
            'role': self.role.value, 'content': self.content,
            'timestamp': self.timestamp.isoformat(), 'message_id': self.message_id,
            'metadata': self.metadata, 'tool_name': self.tool_name, 'tool_result': self.tool_result
        }

@dataclass
class Conversation:
    conversation_id: str
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    messages: List[Message] = field(default_factory=list)
    summary: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: Message):
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_recent(self, n: int = 10) -> List[Message]:
        return self.messages[-n:]
    
    def to_llm_format(self, n: Optional[int] = None) -> List[Dict]:
        messages = self.messages if n is None else self.get_recent(n)
        return [{'role': m.role.value, 'content': m.content} for m in messages]

class ConversationMemory:
    def __init__(self, store, summarizer=None, max_tokens: int = 4000):
        self.store = store
        self.summarizer = summarizer
        self.max_tokens = max_tokens
        self.conversations: Dict[str, Conversation] = {}
    
    async def create_conversation(self, user_id: Optional[str] = None) -> str:
        conversation_id = str(uuid.uuid4())
        conversation = Conversation(conversation_id=conversation_id, user_id=user_id)
        self.conversations[conversation_id] = conversation
        await self.store.save(conversation)
        return conversation_id
    
    async def add_message(self, conversation_id: str, role: MessageRole, content: str, metadata: Optional[Dict] = None) -> Message:
        conversation = await self.get_conversation(conversation_id)
        message = Message(role=role, content=content, metadata=metadata or {})
        conversation.add_message(message)
        if len(conversation.messages) > 20 and self.summarizer:
            conversation.summary = await self.summarizer.summarize(conversation)
        await self.store.save(conversation)
        return message
    
    async def get_conversation(self, conversation_id: str) -> Conversation:
        if conversation_id not in self.conversations:
            conversation = await self.store.load(conversation_id)
            self.conversations[conversation_id] = conversation
        return self.conversations[conversation_id]
    
    async def get_context_for_llm(self, conversation_id: str, max_messages: int = 10) -> List[Dict]:
        conversation = await self.get_conversation(conversation_id)
        messages = []
        if conversation.summary:
            messages.append({'role': 'system', 'content': f"Previous conversation summary: {conversation.summary}"})
        messages.extend(conversation.to_llm_format(max_messages))
        return messages
```

---

## 8. Multi-LLM Provider Support

### 8.1 Enhanced Provider Base

```python
# src/llm_providers/enhanced_base.py
"""Enhanced base classes for LLM providers."""

from typing import AsyncIterator, Dict, List, Optional, Union, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import asyncio
import time
import json
import hashlib

@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float = 0.0

@dataclass
class EnhancedLLMResponse:
    content: str
    model: str
    usage: TokenUsage
    finish_reason: str
    latency_ms: float
    metadata: Dict[str, Any]
    cached: bool = False

class EnhancedProvider(ABC):
    def __init__(self, config):
        self.config = config
        self._cache = {}
        self._rate_limiter = RateLimiter()
        self._metrics = MetricsCollector()
    
    @abstractmethod
    async def generate(self, messages: List[Dict], stream: bool = False, tools: Optional[List[Dict]] = None) -> EnhancedLLMResponse:
        pass
    
    async def generate_with_fallback(self, messages: List[Dict], fallback_providers: List['EnhancedProvider'], **kwargs) -> EnhancedLLMResponse:
        providers = [self] + fallback_providers
        for provider in providers:
            try:
                start = time.time()
                response = await provider.generate(messages, **kwargs)
                response.latency_ms = (time.time() - start) * 1000
                return response
            except Exception as e:
                self._metrics.record_error(provider.name, str(e))
                continue
        raise RuntimeError("All providers failed")
    
    def _check_cache(self, messages: List[Dict]) -> Optional[EnhancedLLMResponse]:
        cache_key = hashlib.md5(json.dumps(messages, sort_keys=True).encode()).hexdigest()
        return self._cache.get(cache_key)
    
    def _cache_response(self, messages: List[Dict], response: EnhancedLLMResponse):
        cache_key = hashlib.md5(json.dumps(messages, sort_keys=True).encode()).hexdigest()
        self._cache[cache_key] = response

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = []
    
    async def acquire(self):
        now = time.time()
        self.requests = [r for r in self.requests if now - r < 60]
        if len(self.requests) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.requests[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        self.requests.append(now)

class MetricsCollector:
    def __init__(self):
        self.metrics = {'requests': 0, 'errors': 0, 'total_latency_ms': 0, 'total_tokens': 0, 'cost_usd': 0}
    
    def record_request(self, latency_ms: float, tokens: int, cost: float):
        self.metrics['requests'] += 1
        self.metrics['total_latency_ms'] += latency_ms
        self.metrics['total_tokens'] += tokens
        self.metrics['cost_usd'] += cost
    
    def record_error(self, provider: str, error: str):
        self.metrics['errors'] += 1
```

---

## 9. Fine-Tuning for Disaster Domain

### 9.1 Data Preparation

```python
# src/finetuning/data_prep.py
"""Data preparation for fine-tuning."""

from typing import List, Dict, Any
from dataclasses import dataclass
import json

@dataclass
class TrainingExample:
    instruction: str
    input_data: str
    output: str
    context: Dict[str, Any]

class TrainingDataBuilder:
    def __init__(self, county_data, disaster_docs):
        self.county_data = county_data
        self.disaster_docs = disaster_docs
    
    def build_vulnerability_examples(self, n: int = 1000) -> List[TrainingExample]:
        examples = []
        for county in self.county_data.sample(n).to_dict('records'):
            if county.get('svi_overall', 0) > 0.7:
                example = TrainingExample(
                    instruction="Analyze the vulnerability of this county.",
                    input_data=self._county_to_text(county),
                    output=self._generate_vulnerability_output(county),
                    context={"type": "high_vulnerability", "fips": county.get('fips')}
                )
                examples.append(example)
        return examples
    
    def _county_to_text(self, county: Dict) -> str:
        parts = [f"{county.get('county_name')} County, {county.get('state')}"]
        parts.append(f"SVI: {county.get('svi_overall', 'N/A')}")
        parts.append(f"Poverty: {county.get('poverty_pct', 'N/A')}%")
        return ", ".join(parts)
    
    def _generate_vulnerability_output(self, county: Dict) -> str:
        vulnerabilities = []
        if county.get('svi_overall', 0) > 0.7:
            vulnerabilities.append("High social vulnerability")
        return json.dumps({"vulnerabilities": vulnerabilities, "risk_level": "high" if len(vulnerabilities) >= 2 else "medium"})
```

---

## 10. Token Optimization

### 10.1 Token Optimizer

```python
# src/tokens/optimizer.py
"""Token optimization strategies."""

from typing import List, Dict
from dataclasses import dataclass
from enum import Enum
import json

class CompressionStrategy(Enum):
    TRUNCATE = "truncate"
    SUMMARIZE = "summarize"
    SELECTIVE = "selective"
    STRUCTURED = "structured"

@dataclass
class OptimizationResult:
    original_tokens: int
    optimized_tokens: int
    compression_ratio: float
    strategy_used: CompressionStrategy
    content: str

class TokenOptimizer:
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        self.estimator = TokenEstimator()
    
    def optimize(self, content: str, target_tokens: int, strategy: CompressionStrategy = CompressionStrategy.SELECTIVE) -> OptimizationResult:
        original_tokens = self.estimator.estimate(content)
        if original_tokens <= target_tokens:
            return OptimizationResult(original_tokens, original_tokens, 1.0, strategy, content)
        
        if strategy == CompressionStrategy.TRUNCATE:
            optimized = self._truncate(content, target_tokens)
        elif strategy == CompressionStrategy.SELECTIVE:
            optimized = self._selective_compression(content, target_tokens)
        else:
            optimized = self._truncate(content, target_tokens)
        
        optimized_tokens = self.estimator.estimate(optimized)
        return OptimizationResult(original_tokens, optimized_tokens, optimized_tokens / original_tokens, strategy, optimized)
    
    def _truncate(self, content: str, target_tokens: int) -> str:
        return content[:target_tokens * 4] + "..." if len(content) > target_tokens * 4 else content
    
    def _selective_compression(self, content: str, target_tokens: int) -> str:
        try:
            data = json.loads(content)
            priority_fields = ['county_name', 'state', 'fips', 'svi_overall', 'disaster_count']
            compressed = {k: v for k, v in data.items() if k in priority_fields}
            return json.dumps(compressed)
        except json.JSONDecodeError:
            return self._truncate(content, target_tokens)

class TokenEstimator:
    def __init__(self, model: str = "gpt-4"):
        self.chars_per_token = 4
    
    def estimate(self, text: str) -> int:
        return len(text) // self.chars_per_token
    
    def estimate_messages(self, messages: List[Dict]) -> int:
        return sum(4 + self.estimate(m.get('content', '')) + self.estimate(m.get('role', '')) for m in messages)
```

---

## 11. Response Streaming

### 11.1 Streaming Handler

```python
# src/streaming/handler.py
"""Handle streaming responses from LLMs."""

from typing import AsyncIterator, Callable, List
from dataclasses import dataclass
import asyncio

@dataclass
class StreamChunk:
    content: str
    chunk_type: str = "content"
    is_complete: bool = False

class StreamBuffer:
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.buffer = ""
        self.chunks: List[str] = []
    
    def add(self, content: str):
        self.buffer += content
        self.chunks.append(content)
        if len(self.buffer) > self.max_size:
            self.buffer = self.buffer[-self.max_size:]

class StreamingHandler:
    def __init__(self, formatter=None, aggregator=None):
        self.formatter = formatter
        self.aggregator = aggregator
        self.buffer = StreamBuffer()
        self.callbacks: List[Callable] = []
    
    def on_chunk(self, callback: Callable):
        self.callbacks.append(callback)
    
    async def process_stream(self, stream: AsyncIterator[str]) -> AsyncIterator[StreamChunk]:
        async for chunk in stream:
            self.buffer.add(chunk)
            for callback in self.callbacks:
                if asyncio.iscoroutinefunction(callback):
                    await callback(chunk)
                else:
                    callback(chunk)
            content = self.formatter.format(chunk) if self.formatter else chunk
            yield StreamChunk(content=content, chunk_type="content")
        yield StreamChunk(content="", chunk_type="content", is_complete=True)
```

---

## 12. Integration Layer

```python
# src/integration.py
"""Integration points for new LLM components."""

from typing import Dict, Any, Optional

class ResilienceAIIntegration:
    def __init__(self, existing_llm_interface, vector_space, agent_orchestrator):
        self.llm_interface = existing_llm_interface
        self.vector_space = vector_space
        self.agent_orchestrator = agent_orchestrator
        self._init_components()
    
    def _init_components(self):
        from .rag import QueryProcessor
        from .vector_store import CountyEmbeddingModel, FAISSIndex
        from .memory import ConversationMemory, SQLiteStore
        
        self.query_processor = QueryProcessor(self.llm_interface)
        self.embedder = CountyEmbeddingModel()
        self.vector_index = FAISSIndex(dimension=384)
        self.memory = ConversationMemory(SQLiteStore("data/conversations.db"))
    
    async def process_query(self, query: str, conversation_id: Optional[str] = None, use_rag: bool = True, use_memory: bool = True) -> Dict[str, Any]:
        if use_memory:
            if not conversation_id:
                conversation_id = await self.memory.create_conversation()
            await self.memory.add_message(conversation_id, MessageRole.USER, query)
            conversation_context = await self.memory.get_context_for_llm(conversation_id)
        else:
            conversation_context = [{"role": "user", "content": query}]
        
        if use_rag:
            processed = self.query_processor.process(query)
            query_embedding = self.embedder.encode_query(query)
            # ... retrieval and response generation
            response = "Generated response"
        else:
            messages = conversation_context
            llm_response = await self.llm_interface.generate(messages)
            response = llm_response.content
        
        if use_memory:
            await self.memory.add_message(conversation_id, MessageRole.ASSISTANT, response)
        
        return {"response": response, "conversation_id": conversation_id}
```

---

## 13. Implementation Priority Order

### Phase 1: Foundation (Weeks 1-2)
1. **Enhanced Vector Store** - FAISSIndex with metadata filtering, CountyEmbeddingModel
2. **RAG Core** - QueryProcessor with intent classification, ContextAssembler
3. **Prompt Templates** - CountyAnalysisTemplate, VulnerabilityTemplate

### Phase 2: Intelligence (Weeks 3-4)
4. **LLM Chains** - VulnerabilityAnalysisChain, IntentRouterChain
5. **Conversation Memory** - SQLiteStore, ConversationSummarizer
6. **Streaming Support** - StreamingHandler, StreamFormatter

### Phase 3: Scale (Weeks 5-6)
7. **Multi-Provider Support** - OpenAIProvider, AnthropicProvider, Fallback
8. **Token Optimization** - TokenOptimizer with compression strategies
9. **Fine-Tuning Pipeline** - TrainingDataBuilder, LoRA setup

### Phase 4: Polish (Week 7)
10. **Multi-Modal AI** - GeoEncoder, TemporalEncoder
11. **Integration & Testing** - Full pipeline integration

---

## 14. Proposed File Structure

```
src/
├── llm_interface.py              # (existing) - Enhanced
├── llm_providers/                # (existing)
│   ├── openai_provider.py        # NEW
│   └── anthropic_provider.py     # NEW
├── vector_store/                 # NEW
│   ├── __init__.py
│   ├── embeddings.py
│   └── vector_index.py
├── rag/                          # NEW
│   ├── __init__.py
│   ├── query_processor.py
│   └── retriever.py
├── prompts/                      # NEW
│   ├── __init__.py
│   └── templates.py
├── chains/                       # NEW
│   ├── __init__.py
│   ├── base.py
│   └── analysis_chain.py
├── memory/                       # NEW
│   ├── __init__.py
│   ├── base.py
│   └── stores.py
├── streaming/                    # NEW
│   ├── __init__.py
│   └── handler.py
├── tokens/                       # NEW
│   ├── __init__.py
│   └── optimizer.py
├── multimodal/                   # NEW
│   ├── __init__.py
│   └── encoders.py
├── finetuning/                   # NEW
│   ├── __init__.py
│   └── data_prep.py
└── integration.py                # NEW
```

---

## 15. Summary

This comprehensive LLM and AI integration enhancement design provides:

1. **RAG System**: Full retrieval-augmented generation with hybrid search
2. **Vector Store**: Enhanced embeddings with domain-specific encoding
3. **Multi-Modal AI**: Support for text, tabular data, geospatial, temporal data
4. **Advanced Prompts**: Template system with chain-of-thought
5. **LLM Chains**: Composable chains for complex multi-step reasoning
6. **Conversation Memory**: Persistent storage with summarization
7. **Multi-Provider**: Support for Ollama, OpenAI, Anthropic
8. **Fine-Tuning**: LoRA-based domain adaptation pipeline
9. **Token Optimization**: Compression strategies and budget management
10. **Streaming**: Real-time response handling

The implementation follows a phased approach over 7 weeks, starting with foundational components and building up to advanced features.
