# ResilienceAI - MUIDSI Hackathon 2026 Submission

**Submission Time:** 2026-02-17 22:00 CST  
**Team:** ResilienceAI Development Team  
**Repository:** https://github.com/GDogMcCoy/ResilienceAI  
**Branch:** main  
**Version:** v3.2.0

---

## Quick Links

- **Live Demo:** Run locally with `python run_dashboard.py`
- **Presentation:** `Hackathon Presentation_v2.pdf` (root folder)
- **One-Pager:** `presentation/ONE_PAGER.md`
- **Demo Script:** `demo_materials/DEMO_SCRIPT.md`
- **Agent Guide:** `AGENTS.md`

---

## Submission Checklist

### Technical Requirements
- [x] GitHub repository accessible
- [x] README.md with setup instructions
- [x] requirements.txt with all dependencies
- [x] Working code (tested E2E)
- [x] Clean repository (no cache/build files)

### Demo Requirements
- [x] Demo script prepared (`demo_materials/DEMO_SCRIPT.md`)
- [x] Video script prepared (`demo_materials/VIDEO_SCRIPT.md`)
- [x] Screenshots available in `outputs/figures/`
- [ ] Demo video recorded (optional - live demo ready)

### Presentation Requirements
- [x] Presentation PDF (`Hackathon Presentation_v2.pdf`)
- [x] One-pager (`presentation/ONE_PAGER.md`)
- [x] Judge FAQ (`presentation/JUDGE_FAQ.md`)
- [x] Speaker notes prepared

### Documentation
- [x] README.md (updated v3.2.0)
- [x] AGENTS.md (comprehensive agent guide)
- [x] Architecture documented
- [x] Data sources cited

---

## Project Overview

**ResilienceAI** is an AI-powered disaster vulnerability intelligence platform for Missouri communities, built for the MUIDSI Hackathon 2026.

### Key Features (v3.2.0)
- **45+ MCP Tools** across 6 categories
- **Multi-Agent Orchestration** with recursive analysis (10 rounds)
- **Dual LLM Backends** (Gemini + Local)
- **Real-Time NOAA Alerts**
- **Climate Intelligence** (ACIS, FEMA NRI, USGS, NOAA)
- **3,222 County Coverage**

### Architecture
```
Data Sources → Feature Engineering (66 features) → ML Ensemble → 
Multi-Agent Orchestrator → Streamlit Dashboard
```

---

## Running the Demo

```bash
# Install dependencies
pip install -r requirements.txt

# Launch dashboard
python run_dashboard.py

# Dashboard opens at http://localhost:8501
```

---

## What Makes This Special

1. **Agentic Intelligence:** Not just data visualization - the AI reasons across multiple tools to provide insights
2. **Recursive Analysis:** Forces deeper investigation with mandatory 3+ tool usage
3. **Real-World Impact:** Addresses actual disaster preparedness gaps in Missouri
4. **Production Ready:** Clean code, comprehensive tests, deployment configs

---

## Repository Structure

```
resilienceai/
├── app/dashboard.py          # Streamlit UI (16 tabs)
├── src/                      # Source code (45+ tools)
├── data/processed/           # County features (3,222 x 66)
├── models/                   # Trained ML models
├── demo_materials/           # Demo scripts
├── presentation/             # Submission materials
├── docs/                     # Documentation
└── tests/                    # E2E test suite
```

---

## Known Issues

None critical. All 60 E2E tests passing.

---

## Time Invested

- Development: ~2 weeks
- Agents Involved: 100+ agent swarms
- Commits: 50+
- Lines of Code: ~15,000

---

**Ready for Judging! 🚀**
