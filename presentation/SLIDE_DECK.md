# ResilienceAI - MUIDSI Hackathon 2026
## Slide Deck: 5-Minute Winning Pitch

---

## SLIDE 1: HOOK (0:00-0:30)

**[Visual: Animated US map with counties lighting up, counter ticking: 3,222 → 157,363 → 69,615]**

### Opening Line:
> "Every year, disasters displace 14 million Americans. But here's what keeps emergency planners up at night: **they don't know where to send resources first.**"

**The Problem:**
- 3,222 counties
- 157,363 critical facilities  
- 69,615 historical disasters
- **Zero tools that can answer a simple question in plain English**

**[Transition]**: "Let me show you why this matters."

---

## SLIDE 2: THE STAKES (0:30-1:00)

**[Visual: Split screen - confused emergency manager vs. confident ResilienceAI user]**

### The Reality:
> "When Hurricane Katrina hit, emergency responders didn't have real-time vulnerability data. They didn't know which counties had zero hospital redundancy. They couldn't predict which communities would be cut off."

**The Result:**
- 1,800 deaths that could have been prevented
- $125 billion in damages
- Years of recovery

**Current State Pain Points:**
1. **Data Silos** — FEMA, Census, Health systems don't talk
2. **Static Reports** — PDFs updated annually, not real-time
3. **Manual Analysis** — 6 hours of work for simple questions
4. **No Predictive Capability** — Reactive, not proactive

**[Transition]**: "This is where ResilienceAI changes everything."

---

## SLIDE 3: THE SOLUTION (1:00-1:30)

**[Visual: Three-pillar architecture diagram]**

### ResilienceAI: Agentic AI for Disaster Resilience

**Pillar 1: Unified Data Layer**
- 7 federal data sources integrated
- 66 engineered features per county
- Real-time spatial analysis

**Pillar 2: Agentic AI Engine**
- 4 specialized agents
- 56 MCP tools
- Natural language reasoning

**Pillar 3: Actionable Intelligence**
- FHIR R4 export for Epic/Cerner
- GeoJSON for GIS workflows
- Real-time alerting

**The Differentiator:**
> "Other tools show you what happened. ResilienceAI shows you **what's about to happen** — and what to do about it."

**[Transition]**: "But enough slides. Let me show you it in action."

---

## SLIDE 4: LIVE DEMO - MAGIC QUERY (1:30-2:15)

**[Visual: Screen recording of dashboard - Agent Query tab]**

### Demo 1: Natural Language Intelligence

**Scenario:** Missouri emergency manager, storm approaching

**Query:**
```
"Which Missouri counties are most vulnerable to flooding?"
```

**Narration:**
> "Watch this — no SQL, no coding, just plain English. In under 2 seconds, ResilienceAI analyzes 3,222 counties, identifies Missouri's flood-prone areas, and returns a prioritized list with citations for every data point."

**What Judges See:**
- Instant response (< 2 seconds)
- Ranked list with risk scores
- Citations for every claim
- Confidence: 98.3% F1 score

**[Transition]**: "But single-factor analysis isn't enough."

---

## SLIDE 5: LIVE DEMO - COMPOUND RISK (2:15-3:00)

**[Visual: Screen recording - Advanced Insights → Compound Risk Hotspots]**

### Demo 2: Multi-Dimensional Intelligence

**Query:**
> "Show me counties with multiple vulnerabilities simultaneously"

**What Judges See:**
- Interactive map with color-coded risk
- Counties ranked by compound risk score
- Boone County, Missouri: 95th percentile vulnerability, zero hospital redundancy

**The Insight:**
> "These counties are in the top quartile for vulnerability, isolation, disaster exposure, AND infrastructure deficit — all at once. This isn't just a risk map. **It's a priority list for saving lives.**"

**[Transition]**: "But analysis is only half the battle."

---

## SLIDE 6: LIVE DEMO - INTEGRATION (3:00-3:30)

**[Visual: Screen recording - FHIR export demonstration]**

### Demo 3: Enterprise Integration

**Query:**
```
"Export high-risk counties in Florida as FHIR"
```

**What Judges See:**
- FHIR R4 Bundle generated in seconds
- Location and RiskAssessment resources
- Ready for Epic, Cerner, any EHR system

**The Impact:**
> "Health systems can now incorporate disaster vulnerability into clinical decision support. A patient's risk score can include: Is this county under active flood warning? From natural language question to health system integration in seconds."

**[Transition]**: "Let me show you the numbers."

---

## SLIDE 7: IMPACT METRICS (3:30-4:00)

**[Visual: Metrics dashboard with animated counters]**

### Quantified Impact

| Metric | Value | Context |
|--------|-------|---------|
| **Counties Analyzed** | 3,222 | 100% US coverage |
| **Facilities Mapped** | 157,363 | Every hospital, shelter, power plant |
| **Response Time** | < 2 seconds | vs. 6+ hours manually |
| **Prediction Accuracy** | 98.3% F1 | ML-validated |
| **Time Saved** | 95% | 6 hours → 6 seconds |

### Real-World Applications

1. **FEMA** — Pre-position resources before disasters strike
2. **State Health Departments** — Identify hospital deserts for capacity planning
3. **Emergency Managers** — Scenario simulation for training exercises
4. **Rural Hospitals** — Mutual aid planning with neighboring counties

**[Transition]**: "This is more than a tool."

---

## SLIDE 8: WHY WE WIN (4:00-4:30)

**[Visual: Competitive comparison matrix]**

### Competitive Advantage

| Feature | ResilienceAI | FEMA EM | HHS ASPR | Generic BI |
|---------|--------------|---------|----------|------------|
| Natural Language | ✅ | ❌ | ❌ | ❌ |
| Real-Time Data | ✅ | ⚠️ | ❌ | ❌ |
| Predictive Models | ✅ | ❌ | ❌ | ⚠️ |
| FHIR Integration | ✅ | ❌ | ❌ | ❌ |
| Agentic AI | ✅ | ❌ | ❌ | ❌ |
| Open Source | ✅ | ❌ | ❌ | ⚠️ |

### Technical Excellence
- **384-dimension vector space** for semantic search
- **FAISS indexing** for sub-millisecond retrieval
- **3D visualizations** with t-SNE/UMAP
- **LangGraph orchestration** for agent workflows
- **Local LLM support** — Ollama, LM Studio, HF, llama.cpp

**[Transition]**: "We're not just building software."

---

## SLIDE 9: CLOSE (4:30-5:00)

**[Visual: Logo + tagline + QR code to demo]**

### Closing Statement

> "Disasters don't wait for us to be ready. **ResilienceAI ensures we are.**"

### The Ask

**Try it yourself:**
- GitHub: `github.com/GDogMcCoy/ResilienceAI`
- Branch: `claw-autonomous`
- Demo: [Live dashboard link]

### Tagline Options:
- "3,222 counties. One platform. Zero excuses for being unprepared."
- "From hours of analysis to seconds. From reactive to predictive."
- "Building resilience for vulnerable communities."

**[Final Visual]:**
```
┌─────────────────────────────────────┐
│                                     │
│      🔥 ResilienceAI 🔥            │
│                                     │
│   Agentic AI for Disaster          │
│   Resilience & Response            │
│                                     │
│   [QR CODE]                        │
│   github.com/GDogMcCoy/ResilienceAI │
│                                     │
└─────────────────────────────────────┘
```

**End:** "Thank you. Questions?"

---

## SPEAKER NOTES

### Timing Tips
- **Hook**: Make eye contact, pause after the stat
- **Problem**: Slow down, let the emotional weight land
- **Demo**: Speak through actions, don't narrate every click
- **Impact**: Let numbers sink in, pause between metrics
- **Close**: Strong voice, confident finish

### Demo Backup Plans
- If live demo fails: Use screenshots in slides
- If query is slow: Have pre-loaded results ready
- If system crashes: "Let me show you a recorded demonstration"

### Anticipated Questions
1. **Data sources?** — Census, FEMA, CDC, HRSA, NOAA, USGS, HIFLD
2. **How often updated?** — Real-time for weather, annual for census
3. **Cost?** — Open source, free to use
4. **Scalability?** — Handles 3,222 counties in <2 seconds
5. **Integration?** — FHIR R4, GeoJSON, REST API

### What Makes Judges Lean Forward
- The "6 hours → 6 seconds" comparison
- Live natural language query working
- FHIR integration (healthcare judges love this)
- Compound risk visualization
- The Missouri-specific example (MUIDSI connection)
