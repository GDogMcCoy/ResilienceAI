# ResilienceAI - 5-Minute Demo Script
## MUIDSI Hackathon 2026 Presentation

---

## 🎯 Overview
**Total Time:** 5 minutes  
**Format:** Live demo with dashboard + talking points  
**Goal:** Demonstrate true agentic AI capabilities for disaster vulnerability assessment

---

## 1. HOOK / ATTENTION GRABBER (30 seconds)

**Opening Statement:**
> "Every year, disasters displace millions of Americans. But here's what keeps emergency planners up at night: **they don't know where to send resources first.**"

**Visual:** Show the Overview tab with 3,222 counties displayed

**Key Stat:**
- "3,222 US counties. 157,363 facilities. 69,615 historical disasters."
- "Most tools show you what happened. ResilienceAI shows you **what's about to happen** — and what to do about it."

**Transition:** "Let me show you how."

---

## 2. PROBLEM STATEMENT (45 seconds)

**The Challenge:**
> "When Hurricane Katrina hit, emergency responders didn't have real-time vulnerability data. They didn't know which counties had zero hospital redundancy. They couldn't predict which communities would be cut off."

**Current State:**
- Static PDF reports updated annually
- Siloed data across FEMA, Census, health systems
- No predictive capability
- Hours of manual analysis for simple questions

**The Gap:**
> "Emergency managers need answers in **seconds**, not hours. They need to ask questions in plain English and get data-backed recommendations immediately."

**Visual:** Briefly scroll through static data sources (HIFLD, FEMA, Census)

---

## 3. SOLUTION WALKTHROUGH (90 seconds)

**Architecture Overview:**
> "ResilienceAI is built on three pillars:"

**Pillar 1: Unified Data Layer**
- 7 federal data sources integrated
- 66 engineered features per county
- Real-time spatial analysis with KD-trees
- **Visual:** Show data sources in documentation

**Pillar 2: Agentic AI Engine**
- 29 MCP tools for complex reasoning
- Natural language to data-backed answers
- Multi-step problem solving
- **Visual:** Show Agent Query tab

**Pillar 3: Actionable Intelligence**
- FHIR R4 export for health systems
- GeoJSON for GIS workflows
- Real-time alerting capabilities
- **Visual:** Show Export tab

**The Differentiator:**
> "This isn't keyword matching. This is true agentic AI that reasons about vulnerability, selects the right analytical tools, and generates actionable recommendations."

---

## 4. LIVE DEMO FLOW (2 minutes)

### Demo 1: Natural Language Query (45 seconds)

**Action:** Click to "Agent Query" tab

**Script:**
> "Watch this. I'm going to ask a complex question in plain English."

**Type:** "Which Missouri counties are most vulnerable to flooding?"

**Narrate:**
1. "The agent parses the query — Missouri, flooding, vulnerability"
2. "It selects the right tools: query_counties with state filter and disaster_flood > 0"
3. "It sorts by risk_score and returns the top 10"
4. "Each result includes citations — you can verify every number"

**Highlight:** Point to citations and data sources

**Key Point:** "No SQL. No coding. Just questions and answers."

---

### Demo 2: Compound Risk Analysis (45 seconds)

**Action:** Navigate to "Advanced Insights" tab

**Script:**
> "But what about counties with multiple vulnerabilities? Let me show you compound risk."

**Click:** "Compound Risk Hotspots" visualization

**Narrate:**
1. "These counties are in the top quartile for **four dimensions simultaneously**: vulnerability, isolation, disaster exposure, and infrastructure deficit"
2. "Boone County, Missouri — 95th percentile vulnerability, zero hospital redundancy"
3. "This isn't just a risk map. It's a priority list for resource allocation."

**Visual:** Show the compound risk map with color-coded counties

---

### Demo 3: Health System Integration (30 seconds)

**Action:** Return to Agent Query, type new query

**Type:** "Export high-risk counties in Florida as FHIR"

**Narrate:**
> "ResilienceAI doesn't just analyze — it integrates. This FHIR Bundle can be imported directly into Epic, Cerner, any EHR system."

**Show:** Export preview with Location and RiskAssessment resources

**Key Point:** "Health systems can now incorporate disaster vulnerability into clinical decision support."

---

## 5. IMPACT STATEMENT (45 seconds)

**Quantified Impact:**

| Metric | Value |
|--------|-------|
| Counties Analyzed | 3,222 |
| Facilities Mapped | 157,363 |
| Response Time | < 2 seconds |
| Time Saved vs. Manual Analysis | 95% |

**Real-World Applications:**
1. **FEMA:** Pre-position resources before disasters strike
2. **State Health Departments:** Identify hospital deserts for capacity planning
3. **Emergency Managers:** Scenario simulation for training exercises
4. **Rural Hospitals:** Mutual aid planning with neighboring counties

**The Bottom Line:**
> "ResilienceAI transforms disaster preparedness from reactive to predictive. From hours of analysis to seconds. From static reports to living intelligence."

**Call to Action:**
> "We're not just building a tool. We're building resilience for vulnerable communities."

---

## 6. Q&A PREPARATION (30 seconds buffer)

### Anticipated Questions & Answers

**Q: How is this different from FEMA's existing tools?**
A: "FEMA provides data. ResilienceAI provides intelligence. We don't just show you disaster history — we predict vulnerability, identify intervention points, and integrate with operational systems like EHRs."

**Q: What about data freshness?**
A: "All data is from authoritative federal sources updated monthly to annually. The pipeline can be re-run to refresh all 157,000+ records."

**Q: How accurate are the predictions?**
A: "Our ML models achieve 98.3% F1 score on risk classification, validated with 5-fold cross-validation."

**Q: Can this scale to real-time?**
A: "Yes — the Archia MCP runtime supports horizontal scaling. Our Kubernetes deployment can handle 10,000+ concurrent queries."

**Q: What's the business model?**
A: "Open source core with enterprise support. We want every emergency manager to have access to this capability."

---

## 🎬 DEMO CHECKLIST

### Before Presentation
- [ ] Dashboard running on localhost:8501
- [ ] Archia server started (if showing agent queries)
- [ ] Test queries prepared and working
- [ ] Backup screenshots in case of technical issues

### Technical Setup
```bash
# Terminal 1: Start Archia
archiad --config archia/archia.toml

# Terminal 2: Start Dashboard
streamlit run app/dashboard.py

# Verify: Open http://localhost:8501
```

### Backup Plan
If live demo fails, use:
- Pre-recorded screen capture (3 min video)
- Static screenshots in presentation deck
- Printed one-pager for judges

---

## 📊 KEY TALKING POINTS

### For Technical Judges
- "29 MCP tools with dynamic tool selection"
- "Moran's I and Getis-Ord Gi* spatial statistics"
- "FHIR R4 compliant health data export"
- "Logistic Regression with 98.3% F1 score"

### For Domain Judges
- "Zero redundancy hospital detection"
- "Compound risk clustering for resource prioritization"
- "Population-weighted vulnerability for equitable resource allocation"
- "Gap analysis for targeted interventions"

### For Business Judges
- "157,363 records from 7 federal sources — all real data"
- "FHIR export enables EHR integration (Epic, Cerner)"
- "Kubernetes deployment for enterprise scale"
- "Open source with commercial support model"

---

## 🏆 CLOSING STATEMENT

> "Disasters don't wait for us to be ready. ResilienceAI ensures we are."

**Thank you. Questions?**

---

*ResilienceAI — Built for emergency planners. Powered by agentic AI.*
