# 🛡️ ResilienceAI - Quick Start Guide

## 🚀 Run the Dashboard (Recommended)

### Option 1: One-Click Launcher ⭐ EASIEST
```bash
python run_dashboard.py
```
Auto-opens browser at http://localhost:8501

### Option 2: VS Code (F5)
Press **F5** and select "🚀 Launch ResilienceAI Dashboard"

### Option 3: Manual
```bash
streamlit run app/dashboard.py
```

---

## ⚠️ Streamlit Cloud Status

The cloud deployment has access restrictions. **Run locally for best experience.**

If you need cloud access:
1. Fork this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Deploy your fork

---

## 📁 Project Structure

```
ResilienceAI/
├── 🚀 run_dashboard.py          ← START HERE
├── 📊 app/dashboard.py          ← Main dashboard (16 tabs)
├── 🔧 src/                      ← All modules
├── 📖 demo_materials/           ← Hackathon presentation
├── ⚙️  archia/                   ← Deployment config
└── 📋 docs/                     ← Documentation
```

---

## 🎯 What's Inside

| Feature | Description |
|---------|-------------|
| **45 MCP Tools** | AI-powered vulnerability analysis |
| **16 Dashboard Tabs** | Complete assessment platform |
| **Real-Time Streaming** | Live NOAA/USGS data |
| **Geospatial Maps** | Choropleth, hexbin, 3D |
| **Predictive Modeling** | Prophet/ARIMA forecasting |
| **Modern UI** | Gradient themes, animations |

---

## 🔧 First Time Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
python run_dashboard.py
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "streamlit not found" | `pip install streamlit` |
| "module not found" | `pip install -r requirements.txt` |
| Port 8501 in use | Use `--server.port 8502` |
| Data not loading | Check `data/processed/county_features.csv` |
| Cloud access denied | Run locally instead |

---

## 📞 Need Help?

- `docs/STREAMLIT_CLOUD_TROUBLESHOOTING.md` - Cloud access help
- `demo_materials/README.md` - Hackathon guide
- `BUG_REPORT.md` - Known issues

---

**Ready? Run: `python run_dashboard.py`** 🚀
