# ResilienceAI Agent Swarm - Team Contribution Guide

## 🎯 Current Sprint: 8-Hour Hackathon Development

**Status:** Phase 2 of 4 - NOAA Weather API Integration  
**Branch:** `KIMI-2.5-Agent-Swarm`  
**Goal:** MUIDSI Hackathon 2026 Submission

---

## 📋 How to Contribute

### For Technical Teammates

#### 1. Code Contributions
- **Pick a feature** from the roadmap below
- **Create a branch** from `KIMI-2.5-Agent-Swarm`
- **Submit PR** with clear description
- **Tag me** for review

#### 2. Testing & QA
- Run dashboard locally: `streamlit run app/dashboard.py`
- Test MCP tools: `python src/agent.py`
- Report bugs with screenshots

#### 3. Data Research
- Find new federal datasets (CDC, USDA, USGS, NOAA)
- Document API endpoints and access methods
- Suggest novel data combinations

### For Non-Technical Teammates

#### 1. Prompt Engineering
- Test the Agent Query tab with natural language
- Suggest example queries for the demo
- Refine response quality

#### 2. Documentation
- Review README for clarity
- Suggest improvements to user guides
- Create demo scripts

#### 3. Domain Expertise
- Share insights from your field
- Suggest vulnerability factors we missed
- Validate risk scoring logic

#### 4. Presentation & Demo
- Create slide deck
- Record demo video
- Prepare judge Q&A

---

## 🗺️ Feature Roadmap

### ✅ Completed (Phase 1)
| Feature | Status | Files |
|---------|--------|-------|
| Real-Time Alert System | ✅ Done | `src/alert_manager.py` |
| 6 Alert MCP Tools | ✅ Done | `src/agent.py` |
| Alert Dashboard Tab | 🔄 In Progress | `app/dashboard.py` |

### 🔄 In Progress (Phase 2)
| Feature | Owner | Help Needed |
|---------|-------|-------------|
| NOAA Weather API Integration | MedGeo Claw | API key testing |
| Weather Alert Correlation | MedGeo Claw | Data validation |
| Real-Time Weather Feed | MedGeo Claw | UI/UX feedback |

### 📋 Up Next (Phase 3)
| Feature | Owner | Help Needed |
|---------|-------|-------------|
| USDA Crop Data Integration | **OPEN** | Agricultural expertise |
| Drought Monitor API | **OPEN** | Climate data research |
| Crop Vulnerability Scoring | **OPEN** | Plant science input |
| Food Security Risk Model | **OPEN** | Public health insight |

### 📋 Planned (Phase 4)
| Feature | Owner | Help Needed |
|---------|-------|-------------|
| Dashboard Alert Tab UI | **OPEN** | Streamlit expertise |
| 3D Risk Visualization | **OPEN** | PyDeck/Deck.gl skills |
| Demo Script | **OPEN** | Presentation skills |
| Video Recording | **OPEN** | Video editing |

---

## 🌟 Specific Contribution Opportunities

### Immediate Needs (Next 2 Hours)

#### 1. Weather API Testing
**What:** Test NOAA API endpoints  
**Skills:** Python, API testing  
**Time:** 30 min  
**How:** Run `python src/weather_client.py --test` (coming soon)

#### 2. Agricultural Data Research
**What:** Find USDA NASS Quick Stats API examples  
**Skills:** Research, documentation  
**Time:** 1 hour  
**Deliverable:** List of 5 useful crop data endpoints

#### 3. Alert UI Design
**What:** Design Alert Management dashboard tab  
**Skills:** Streamlit, UI/UX  
**Time:** 1-2 hours  
**Reference:** See `app/dashboard.py` Agent Query tab

#### 4. Demo Query Suggestions
**What:** Create 10 compelling natural language queries  
**Skills:** Writing, domain knowledge  
**Time:** 30 min  
**Examples:** 
- "Which Missouri counties face corn yield failure risk?"
- "Show me rural healthcare deserts during flood season"

### Medium-Term (Next 4 Hours)

#### 5. Soil Health Data Integration
**What:** Research USDA NRCS gSSURGO soil database  
**Skills:** GIS, soil science  
**Time:** 2 hours  
**Impact:** Unique differentiator for hackathon

#### 6. Pollinator Health Risk Map
**What:** Integrate bee colony data + pesticide use  
**Skills:** Ecology, data research  
**Time:** 2 hours  
**Impact:** Novel cross-disciplinary feature

#### 7. Intervention Cost Database
**What:** Research costs for hospital/EMS/fire station construction  
**Skills:** Healthcare economics, research  
**Time:** 1 hour  
**Impact:** Improves ROI calculations

#### 8. Climate Scenario Modeling
**What:** Find SSP climate projection data  
**Skills:** Climate science, GIS  
**Time:** 2 hours  
**Impact:** Forward-looking vulnerability assessment

---

## 📝 Contribution Workflow

### Step 1: Pick a Task
Comment below or message me with:
```
I'm taking: [Task Name]
ETA: [When you'll complete it]
Questions: [Any blockers]
```

### Step 2: Work on It
- Create feature branch: `git checkout -b feature/your-feature-name`
- Commit frequently with clear messages
- Test locally before pushing

### Step 3: Submit
- Push branch: `git push origin feature/your-feature-name`
- Create Pull Request to `KIMI-2.5-Agent-Swarm`
- Tag me: `@MedGeo Claw`

### Step 4: Review
- I'll review within 30 minutes
- Address feedback
- Merge when ready

---

## 💡 Idea Prompts for Brainstorming

### Climate + Agriculture
- How do heat waves affect livestock vulnerability?
- Can we predict crop insurance claims?
- What's the link between drought and rural mental health?

### Health + Infrastructure
- Which counties have "zero redundancy" for dialysis centers?
- How does hospital closure affect disaster mortality?
- Where do EMS response times exceed 30 minutes?

### Novel Combinations
- Food desert + flood risk = ?
- Pollinator decline + crop yield + economic impact = ?
- Soil erosion + water quality + health outcomes = ?

### Presentation Ideas
- What's our "wow" factor for judges?
- How do we demo this in 5 minutes?
- What makes us different from other teams?

---

## 📊 Current Stats

| Metric | Value |
|--------|-------|
| MCP Tools | 29 |
| Dashboard Tabs | 12 |
| Data Features | 66 |
| Lines of Code | ~15,000 |
| Documentation Pages | 8 |

---

## 🔗 Quick Links

- **GitHub Repo:** https://github.com/GDogMcCoy/ResilienceAI
- **Active Branch:** `KIMI-2.5-Agent-Swarm`
- **Actions/CI:** https://github.com/GDogMcCoy/ResilienceAI/actions
- **Data Dictionary:** `docs/DATA_DICTIONARY.md`
- **Setup Guide:** `docs/SETUP_GUIDE.md`

---

## 🙋 Questions?

- **Technical:** Comment on this file or message me
- **Domain:** Share your expertise - we need diverse perspectives
- **Urgent:** Tag me with `[URGENT]` for immediate attention

---

*Last Updated: 2026-02-17 00:35 GMT+8*  
*Next Update: After Phase 2 completion*
