# ResilienceAI Demo Materials - Index
## MUIDSI Hackathon 2026

---

## 📁 Demo Materials Package Contents

This package contains all materials needed for the ResilienceAI hackathon presentation:

### 1. Demo Script (5-Minute Presentation)
**File:** `DEMO_SCRIPT.md`

Complete script for live presentation including:
- Hook/attention grabber (30 sec)
- Problem statement (45 sec)
- Solution walkthrough (90 sec)
- Live demo flow (2 min)
- Impact statement (45 sec)
- Q&A preparation

**Use this for:** Live presentations to judges

---

### 2. Slide Deck (15 Slides)
**File:** `SLIDE_DECK.md`

Complete slide content for presentation:
- Title slide
- Team introduction
- Problem overview
- Solution architecture
- Key features showcase
- Technical highlights
- Demo screenshots
- Impact metrics
- Future roadmap
- Thank you/Q&A

**Use this for:** Creating PowerPoint/Google Slides presentation

---

### 3. Video Script (3-Minute Demo)
**File:** `VIDEO_SCRIPT.md`

Professional video production script including:
- Scene-by-scene breakdown
- Voiceover narration
- Screen recording cues
- Transition points
- Key moments to emphasize
- Production notes

**Use this for:** Creating demo video for submission

---

### 4. Judge FAQ Preparation
**File:** `JUDGE_FAQ.md`

Comprehensive Q&A preparation with 30+ anticipated questions:
- Technical questions (architecture, ML, data)
- Data source questions (provenance, licensing)
- Scalability questions (performance, deployment)
- Differentiation questions (competitive analysis)
- Impact questions (real-world applications)

**Use this for:** Preparing for judge Q&A session

---

### 5. One-Pager Summary
**File:** `ONE_PAGER.md`

Executive summary document including:
- Project overview
- Key stats (37 tools, 15 tabs, etc.)
- Unique selling points
- Technical highlights
- Contact information

**Use this for:** Handout to judges, project summary

---

## 🎯 Quick Reference: Key Statistics

| Metric | Value |
|--------|-------|
| Counties Analyzed | 3,222 |
| Facilities Mapped | 157,363 |
| MCP Tools | 29 |
| Engineered Features | 66 |
| Data Sources | 7 federal agencies |
| ML Model F1 Score | 98.3% |
| Dashboard Tabs | 12 |
| Query Response Time | < 2 seconds |

---

## 🚀 Quick Start for Demo

```bash
# 1. Start Archia server
archiad --config archia/archia.toml

# 2. Launch dashboard
streamlit run app/dashboard.py

# 3. Open browser to http://localhost:8501

# 4. Navigate to "Agent Query" tab

# 5. Try these demo queries:
#    - "Which Missouri counties are most vulnerable to flooding?"
#    - "Show me compound risk hotspots"
#    - "Compare St. Louis County to its peers"
```

---

## 📋 Demo Checklist

### Before Presentation
- [ ] Dashboard running on localhost:8501
- [ ] Archia server started
- [ ] Test queries working
- [ ] Backup screenshots ready
- [ ] Presentation slides loaded
- [ ] One-pagers printed (if in-person)

### Demo Flow
1. **Hook** — Show scale (3,222 counties)
2. **Problem** — Data silos, manual analysis
3. **Solution** — Three pillars (Data, AI, Action)
4. **Live Demo** — Agent Query + Compound Risk
5. **Impact** — Metrics and applications
6. **Q&A** — Use FAQ document

---

## 🎬 Video Production Checklist

### Recording Setup
- [ ] Close unnecessary applications
- [ ] Set resolution to 1920x1080
- [ ] Disable notifications
- [ ] Test audio levels
- [ ] Prepare query text

### Recording Software
- OBS Studio (recommended, free)
- ScreenFlow (Mac)
- Camtasia (Windows/Mac)
- Loom (quick option)

### Export Settings
- Format: MP4 (H.264)
- Resolution: 1920x1080
- Frame Rate: 30fps
- Audio: AAC, 192kbps
- Target Size: < 100MB

---

## 📊 Key Talking Points by Audience

### Technical Judges
- "29 MCP tools with dynamic tool selection"
- "Moran's I and Getis-Ord Gi* spatial statistics"
- "FHIR R4 compliant health data export"
- "Logistic Regression with 98.3% F1 score"

### Domain Judges
- "Zero redundancy hospital detection"
- "Compound risk clustering for resource prioritization"
- "Population-weighted vulnerability for equitable allocation"
- "Gap analysis for targeted interventions"

### Business Judges
- "157,363 records from 7 federal sources"
- "FHIR export enables EHR integration"
- "Kubernetes deployment for enterprise scale"
- "Open source with commercial support model"

---

## 🔗 Important Links

| Resource | Location |
|----------|----------|
| GitHub Repository | github.com/GDogMcCoy/ResilienceAI |
| Setup Guide | `docs/SETUP_GUIDE.md` |
| Data Dictionary | `docs/DATA_DICTIONARY.md` |
| Demo Script | `demo_materials/DEMO_SCRIPT.md` |
| Video Script | `demo_materials/VIDEO_SCRIPT.md` |
| Slide Deck | `demo_materials/SLIDE_DECK.md` |
| Judge FAQ | `demo_materials/JUDGE_FAQ.md` |
| One-Pager | `demo_materials/ONE_PAGER.md` |

---

## 💡 Pro Tips

1. **Practice the demo** — Run through the script at least 3 times
2. **Have backups** — Screenshots in case live demo fails
3. **Know the FAQ** — Review all 30 questions before Q&A
4. **Time yourself** — Stay within 5-minute limit
5. **Show enthusiasm** — Genuine excitement is contagious
6. **Handle errors gracefully** — If something breaks, pivot to screenshots

---

## 📞 Support

For questions about the demo materials:
- Review the full documentation in `docs/`
- Check the HACKATHON_SUBMISSION.md for technical details
- Refer to FEATURE_ROADMAP.md for future plans

---

## ✅ Submission Checklist

- [ ] Demo script reviewed
- [ ] Slides created from SLIDE_DECK.md
- [ ] Video recorded (if required)
- [ ] One-pager printed/available
- [ ] FAQ reviewed
- [ ] Live demo tested
- [ ] Backup screenshots prepared
- [ ] GitHub repository updated
- [ ] Documentation complete

---

**Good luck with the presentation! 🚀**

*ResilienceAI — Built for emergency planners. Powered by agentic AI.*
