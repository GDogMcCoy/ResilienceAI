# 🛡️ ResilienceAI - Quick Start Guide

## 🚀 Run the Dashboard (Easiest Way)

### Option 1: Double-Click Launcher (Recommended)
```bash
# In VS Code terminal or command line:
python run_dashboard.py
```

This will:
- ✅ Check dependencies
- ✅ Launch Streamlit
- ✅ Open browser automatically
- ✅ Start at http://localhost:8501

### Option 2: Manual Streamlit Command
```bash
# From the project root folder:
streamlit run app/dashboard.py
```

### Option 3: Python Module
```bash
# From the project root folder:
python -m streamlit run app/dashboard.py
```

---

## 📁 Project Structure

```
ResilienceAI/
├── 🚀 run_dashboard.py          ← START HERE (launcher script)
├── 📊 app/
│   └── dashboard.py             ← Main dashboard (16 tabs)
├── 🔧 src/
│   ├── agent.py                 ← 38 MCP tools
│   ├── alert_manager.py         ← Real-time alerts
│   ├── weather_client.py        ← NOAA integration
│   ├── agriculture_client.py    ← USDA integration
│   ├── realtime_pipeline.py     ← Live streaming
│   ├── geo_visualizations.py    ← Maps & 3D
│   └── modern_ui.py             ← Visual styling
├── 📖 demo_materials/           ← Hackathon presentation
├── ⚙️  archia/                   ← Deployment config
└── 📋 docs/                     ← Documentation
```

---

## 🎯 What's Inside

| Feature | Description |
|---------|-------------|
| **38 MCP Tools** | AI-powered vulnerability analysis |
| **16 Dashboard Tabs** | Complete assessment platform |
| **Real-Time Streaming** | Live NOAA/USGS data |
| **Geospatial Maps** | Choropleth, hexbin, 3D |
| **Modern UI** | Gradient themes, animations |

---

## 🔧 Setup (If First Time)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the dashboard
python run_dashboard.py
```

---

## 🌐 Access the Dashboard

Once running, open your browser to:
**http://localhost:8501**

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "streamlit not found" | Run: `pip install streamlit` |
| "module not found" | Run: `pip install -r requirements.txt` |
| Port already in use | Change port: `streamlit run app/dashboard.py --server.port 8502` |
| Data not loading | Check that `data/processed/county_features.csv` exists |

---

## 📞 Need Help?

Check these files:
- `docs/VISUAL_MONITORING_GUIDE.md` - How to track activity
- `demo_materials/README.md` - Hackathon submission guide
- `BUG_REPORT.md` - Known issues and fixes

---

**Ready to launch? Run: `python run_dashboard.py`** 🚀
