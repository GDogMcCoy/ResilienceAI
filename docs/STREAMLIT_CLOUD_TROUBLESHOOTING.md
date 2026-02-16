# 🔧 Streamlit Cloud Access Troubleshooting

## Problem
You're seeing: "You do not have access to this app or it does not exist"

## Why This Happens
The Streamlit Cloud app is linked to a specific GitHub account/organization. Your current GitHub account (`gdogmccoy`) may not be the one that deployed the app.

## Solutions

### Option 1: Check Which Account Deployed the App
1. Go to [https://share.streamlit.io/](https://share.streamlit.io/)
2. Sign in with different GitHub accounts you have access to
3. Look for the ResilienceAI app in your dashboard

### Option 2: Redeploy Under Your Account
If you can't access the existing deployment:

```bash
# 1. Fork the repository to your GitHub account
# 2. Go to https://share.streamlit.io/
# 3. Click "New app"
# 4. Select your forked repository
# 5. Set main file path: app/dashboard.py
# 6. Deploy!
```

### Option 3: Run Locally (Guaranteed to Work)
```bash
# Clone the repo
git clone https://github.com/GDogMcCoy/ResilienceAI.git
cd ResilienceAI

# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app/dashboard.py
```

Then open: **http://localhost:8501**

### Option 4: Use GitHub Codespaces (Free Cloud IDE)
1. Go to: https://github.com/GDogMcCoy/ResilienceAI
2. Click the green "<> Code" button
3. Select "Codespaces" tab
4. Click "Create codespace on main"
5. Wait for it to load
6. In the terminal, run: `streamlit run app/dashboard.py`
7. Click "Open in Browser" when prompted

## Quick Fix for Teammates

**Share these options with your team:**

| Method | Difficulty | Link/Command |
|--------|------------|--------------|
| **Try existing deploy** | Easiest | [Current link](https://ask-resilienceai-dashboardagentquerytab-3f8fqqh5fqjpyhw.streamlit.app/) |
| **Run locally** | Easy | `streamlit run app/dashboard.py` |
| **GitHub Codespaces** | Medium | Use Codespaces button on repo |
| **Redeploy** | Harder | Follow Option 2 above |

## For the Developer (You)

To fix permissions:
1. Go to [Streamlit Cloud Dashboard](https://share.streamlit.io/)
2. Find the ResilienceAI app
3. Click "Settings" ⚙️
4. Under "Access", add teammates' GitHub usernames
5. Or make it "Public" so anyone can view

## Alternative: Share Screenshots/Video

If deployment issues persist, share:
- Screen recording of the working dashboard
- Screenshots of key features
- Direct teammates to run locally

## Need Immediate Access?

**Fastest solution:** Run locally with:
```bash
python run_dashboard.py
```

This works 100% of the time regardless of cloud permissions!
