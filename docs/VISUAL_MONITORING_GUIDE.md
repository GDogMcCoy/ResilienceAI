# 📊 Dashboard Visual Monitoring Guide

## 🎯 How to Track Dashboard Activity Visually

### 1. Status Widget (Always Visible)
At the top of every page, you'll see 6 status indicators:

| Icon | Meaning | Status |
|------|---------|--------|
| 🗄️ Data | County database loaded | ✅ Green = Ready |
| 🤖 Agent | AI agent initialized | ✅ Green = Ready |
| 🌦️ Weather | NOAA API connected | ✅ Green = Connected |
| 🌾 Agriculture | USDA API connected | ✅ Green = Connected |
| 🚨 Alerts | Alert system active | ✅ Green = Active |
| ⏱️ Time | Current time | Updates every minute |

**Look for:** All green = system fully operational

---

### 2. Activity Monitor Tab (Tab 15)

**What it shows:**
- Real-time dashboard usage
- API calls being made
- Alerts being triggered
- User interactions

**How to use it:**
1. Click **"📈 Activity Monitor"** tab
2. Select time range (15 min to 24 hours)
3. Enable **"🔄 Auto-refresh"** for live updates

**Visual indicators:**
- 📊 Bar chart: Activity by type
- 📈 Line chart: Activity over time
- 📝 Log: Recent events with timestamps

---

### 3. Visual Activity Types

When activity happens, you'll see colored badges:

| Badge | Activity | Color |
|-------|----------|-------|
| 🔍 | User queries | Blue |
| 🚨 | Alerts triggered | Red |
| 🌦️ | Weather checks | Yellow |
| 🌾 | Agriculture analysis | Green |
| 📊 | General activity | Gray |

---

### 4. System Health Panel

In the Activity Monitor tab, check 4 health indicators:

| Component | Good | Bad |
|-----------|------|-----|
| Data Pipeline | ✅ Healthy | ❌ Error |
| API Connections | ✅ All Online | ❌ Disconnected |
| Alert System | ✅ Active | ❌ Inactive |
| Database | ✅ Connected | ❌ Error |

---

### 5. Quick Checks

**To verify everything is working:**

1. **Look at status widget** (top of page)
   - All should be green ✅

2. **Go to Activity Monitor tab**
   - Should see recent activity
   - Charts should show data

3. **Try a test query**
   - Go to Agent Query tab
   - Type: "Show me Missouri counties"
   - Should see response + activity logged

4. **Check Activity Monitor again**
   - Should see new "query" activity
   - Timestamp should be recent

---

### 6. Auto-Refresh Setup

For continuous monitoring:

1. Open **Activity Monitor** tab
2. Check **"🔄 Auto-refresh (30 seconds)"**
3. Page updates automatically
4. Watch activity in real-time

---

### 7. What to Watch For

**Good signs:**
- ✅ All status indicators green
- ✅ Activity charts showing data
- ✅ Recent timestamps (within minutes)
- ✅ No error messages

**Warning signs:**
- ⚠️ Red status indicators
- ⚠️ "No data" messages
- ⚠️ Old timestamps (>1 hour)
- ⚠️ Error messages in logs

**If something's wrong:**
1. Check status widget for red indicators
2. Refresh the page
3. Check Activity Monitor for errors
4. Message me with what you see

---

### 8. Mobile-Friendly Checking

On your phone:
1. Open dashboard
2. Status widget shows at top
3. Scroll to Activity Monitor tab
4. Same visual indicators work

---

## 🎬 Demo Day Monitoring

During your hackathon demo:

**Before demo:**
- Check all status indicators are green
- Verify Activity Monitor shows recent activity
- Test one query to ensure logging works

**During demo:**
- Activity Monitor shows live interactions
- Judges can see real-time system usage
- Visual proof of working system

**After demo:**
- Activity log shows all demo interactions
- Can review what was tested
- Proof of system functionality

---

## 📱 Quick Reference

| Want to check... | Go to... | Look for... |
|------------------|----------|-------------|
| System status | Top of any page | Status widget |
| Recent activity | Activity Monitor tab | Charts + logs |
| Errors | Activity Monitor tab | Red indicators |
| API health | Activity Monitor tab | System Health panel |
| Live updates | Activity Monitor tab | Auto-refresh checkbox |

---

*Visual monitoring makes it easy to see what's happening without reading logs!*
