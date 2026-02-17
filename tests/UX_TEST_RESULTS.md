# ResilienceAI Dashboard - User Experience Test Results

**Test Date:** February 17, 2026  
**Test Environment:** Linux Ubuntu 22.04, Python 3.12.3  
**Dashboard Version:** v2.0 (MUIDSI Hackathon 2026)  
**Tester Role:** New User (First-Time Experience)

---

## Executive Summary

ResilienceAI is a sophisticated disaster vulnerability intelligence platform with strong data foundations and comprehensive analytics. However, **new users face significant friction** during initial setup and feature discovery. The platform delivers powerful insights once operational, but the onboarding experience requires substantial improvement.

### Overall UX Score: 6.5/10
- **First-Time Setup:** 5/10 ⚠️
- **Feature Discovery:** 7/10 ✅
- **Real-World Use Cases:** 8/10 ✅
- **Accessibility:** 4/10 ❌
- **Documentation:** 7/10 ✅

---

## 1. First-Time User Experience

### 1.1 Setup Process Assessment

#### ✅ What Works
- **Virtual environment creation** is straightforward
- **Data pre-loading** is excellent - 3,222 counties with 66 features already processed
- **Auto-port detection** in run_dashboard.py prevents port conflicts
- **Dependency management** via requirements.txt is standard and expected

#### ❌ Pain Points

| Issue | Severity | Description |
|-------|----------|-------------|
| No `python` command | 🔴 High | `python` not available, must use `python3` - README assumes `python` |
| System package restrictions | 🔴 High | PEP 668 prevents direct pip install, requires venv |
| Streamlit email prompt | 🟡 Medium | First launch blocks on email input (can be skipped, but confusing) |
| Missing .env.example | 🟡 Medium | SETUP_GUIDE mentions `.env.example` but file doesn't exist |
| No setup validation | 🟡 Medium | No way to verify installation before launching dashboard |

#### 📋 Setup Journey Map

```
[Clone Repository] → [Check Python Version] → [Create Virtual Env] → [Activate] → [Install Dependencies]
      ↓                    ↓                      ↓                  ↓              ↓
   ✅ Easy            ⚠️ Must use python3   ✅ Standard      ✅ Standard    ⏱️ Slow (5+ min)
                                                                                ↓
[Launch Dashboard] → [Email Prompt] → [Browser Opens] → [Dashboard Loads]
        ↓                  ↓                ↓                  ↓
   ⚠️ python3 only    ⚠️ Confusing     ✅ Auto-open      ✅ Data ready
```

#### 💡 Recommendations
1. **Update README** to use `python3` explicitly for Linux/macOS
2. **Add setup validation script** that checks dependencies before launching
3. **Create .env.example** file or remove reference from documentation
4. **Add `--no-email` flag** documentation for Streamlit launch
5. **Consider Docker** setup for one-command deployment

### 1.2 First Dashboard Load Experience

#### ✅ What Works
- **Fast data loading** - 3,222 counties load instantly from cache
- **Clear system status** in sidebar shows "3,222 counties indexed"
- **Agent status indicators** show 4 specialist agents, 52 MCP tools
- **Auto-browser open** works correctly

#### ❌ Pain Points

| Issue | Severity | Description |
|-------|----------|-------------|
| No loading progress | 🟡 Medium | Large data loads without progress indication |
| Missing module warnings | 🟡 Medium | Climate, orchestrator modules show "not available" warnings |
| No guided tour | 🟡 Medium | New users don't know where to start |
| Sidebar collapsed | 🟢 Low | Default sidebar state hides key navigation |

---

## 2. Feature Discovery

### 2.1 Navigation Assessment

The dashboard uses **6 main tabs** with clear labeling:
1. Missouri Command Center
2. National Vulnerability Map
3. Climate Intelligence
4. Agent Console
5. Resilience Planner
6. Live Operations

#### ✅ What Works
- **Tab names are descriptive** - users can predict content
- **Logical grouping** - geographic → analytical → operational
- **Missouri focus prominent** - aligns with hackathon scope
- **KPI metrics** visible immediately in Missouri tab

#### ❌ Pain Points

| Issue | Severity | Description |
|-------|----------|-------------|
| No search functionality | 🟡 Medium | Can't search for specific counties across tabs |
| Tab overflow on mobile | 🔴 High | 6 tabs don't fit on small screens |
| No favorites/bookmarks | 🟢 Low | Can't save frequently viewed counties |
| Inconsistent county selection | 🟡 Medium | Each tab has different county picker implementation |

### 2.2 Tooltips & Help Text

#### ✅ What Works
- **Metric cards** show clear labels ("Missouri Risk Index", "High-Risk Counties")
- **Chart titles** are descriptive ("Vulnerability vs Isolation")
- **Agent Console** shows tool descriptions when selected

#### ❌ Pain Points

| Issue | Severity | Description |
|-------|----------|-------------|
| No feature explanations | 🔴 High | Terms like "isolation_index" not explained in UI |
| Missing methodology links | 🟡 Medium | No way to learn how risk scores are calculated |
| No contextual help | 🟡 Medium | No ? icons or help tooltips on metrics |
| Abbreviations undefined | 🟡 Medium | FIPS, EMS, SSP, NRI not explained for non-experts |

### 2.3 User Journey Maps

#### Emergency Manager Journey
```
[Dashboard Opens] → [See Missouri Command Center] → [View Risk Map] → [Identify High-Risk Counties]
        ↓                      ↓                           ↓                    ↓
   ✅ Default tab         ✅ MO pre-selected        ✅ Scatter plot      ✅ Table shows top 15
                                                                                ↓
[Click County] → [View Details] → [Get Recommendations]
        ↓              ↓                  ↓
   ⚠️ Can't click   ❌ No drill-down  ❌ Not actionable
```

**Friction Points:**
- Cannot click on map points to view county details
- No drill-down from summary to detailed view
- Recommendations not immediately actionable

#### Researcher Journey
```
[Dashboard Opens] → [Navigate to National Map] → [Filter by State] → [Select Metrics] → [Export Data]
        ↓                      ↓                      ↓                 ↓              ↓
   ✅ Default tab         ⚠️ Must switch      ✅ Dropdown      ✅ Color options   ❌ No export
```

**Friction Points:**
- No direct comparison tool for urban vs rural
- No export functionality visible
- Limited statistical analysis tools

---

## 3. Real-World Use Case Testing

### 3.1 Emergency Manager: "Show me highest risk counties in Missouri"

**Test Result:** ✅ **SUCCESSFUL**

**Path:** Missouri Command Center → View "Highest Risk Counties" table

**Findings:**
| County | Risk Score | Risk Level | Vulnerability Index |
|--------|------------|------------|---------------------|
| Ozark County | 0.4807 | High | 0.439 |
| Wayne County | 0.4706 | High | 0.431 |
| Hickory County | 0.4510 | High | 0.434 |
| Morgan County | 0.4438 | High | 0.410 |
| Reynolds County | 0.4408 | High | 0.407 |

**What Worked:**
- Table immediately visible on main tab
- Risk scores and levels clearly displayed
- 15 counties shown (good balance)

**What Didn't:**
- No explanation of what "risk score" means
- Cannot click to see county details
- No action buttons (export, alert, share)

### 3.2 Researcher: "Compare urban vs rural vulnerability"

**Test Result:** ⚠️ **PARTIAL - Requires Workaround**

**Path:** National Vulnerability Map → Filter by State → Manual Analysis

**Findings:**
```
Urban counties (pop >50k): 22
Rural counties (pop <20k): 61

Urban avg risk score: 0.237
Rural avg risk score: 0.321  (+35% higher)

Urban avg uninsured %: 9.5%
Rural avg uninsured %: 12.3%  (+30% higher)
```

**What Worked:**
- Data supports the analysis
- State filtering available
- Population data available

**What Didn't:**
- No built-in urban/rural classification
- No comparison tool - must export and analyze externally
- No statistical significance testing

### 3.3 Policymaker: "Which interventions have best ROI?"

**Test Result:** ⚠️ **PARTIAL - Limited Data**

**Path:** Resilience Planner → Intervention ROI → Select County

**Findings for Ozark County (highest risk):**
| Metric | Value |
|--------|-------|
| Intervention | Build New Hospital (50-bed) |
| Investment | $50,000,000 |
| Risk Reduction | 7.3% |
| Cost per person helped | $162,866 |
| Implementation | 5 years |

**What Worked:**
- ROI calculator available
- Shows cost per person helped
- Implementation timeline included

**What Didn't:**
- Only 1 intervention type tested (hospital)
- No comparison between intervention types
- ROI ratio field empty in output
- No visualization of ROI data

### 3.4 Public Health Official: "Find counties with health disparities"

**Test Result:** ✅ **SUCCESSFUL**

**Path:** Missouri Command Center → Health Disparity Matrix

**Findings:**
| County | Disparity Index |
|--------|-----------------|
| Scotland County | 1.92 |
| Morgan County | 1.76 |
| Knox County | 1.70 |
| Oregon County | 1.56 |
| Ozark County | 1.50 |

**What Worked:**
- Disparity analysis available on main tab
- Clear ranking with index scores
- Bar chart visualization

**What Didn't:**
- No explanation of how disparity index is calculated
- No breakdown by specific health metrics
- Cannot drill down to see contributing factors

---

## 4. Accessibility Testing

### 4.1 Keyboard Navigation

**Test Result:** ❌ **POOR**

| Test | Result | Notes |
|------|--------|-------|
| Tab navigation | ⚠️ Partial | Can tab between tabs, but no focus indicators |
| Enter to select | ✅ Yes | Works for tabs and buttons |
| Arrow key navigation | ❌ No | Cannot navigate map with keyboard |
| Skip links | ❌ No | No skip-to-content links |
| Focus trapping | ❌ No | Focus can leave modal contexts |

### 4.2 Screen Reader Compatibility

**Test Result:** ❌ **NOT TESTED - Structural Issues Identified**

Based on code review:
- Plotly charts lack alt text
- No ARIA labels on interactive elements
- Dynamic content updates not announced
- Table headers present but complex tables may be hard to navigate

### 4.3 Color Contrast

**Test Result:** ⚠️ **MODERATE ISSUES**

| Element | Issue | WCAG Level |
|---------|-------|------------|
| Risk level colors | Red/green may be indistinguishable for colorblind users | AA Fail |
| Scatter plot points | Color-only differentiation | AA Fail |
| Sidebar text | Dark on dark in some themes | AAA Fail |

### 4.4 Mobile Responsiveness

**Test Result:** ❌ **POOR**

| Test | Result | Notes |
|------|--------|-------|
| 375px width (iPhone) | ❌ Broken | Tabs overflow, charts cut off |
| 768px width (iPad) | ⚠️ Usable | Side-by-side columns stack awkwardly |
| 1024px width | ✅ Good | Most features accessible |
| Touch targets | ⚠️ Small | Some buttons < 44px |
| Pinch zoom | ✅ Works | But breaks layout |

---

## 5. Documentation Review

### 5.1 README.md Assessment

**Overall Score:** 7/10

| Aspect | Rating | Notes |
|--------|--------|-------|
| Quick start | ✅ Good | Clear 2-step process |
| Architecture diagram | ✅ Good | Clear pipeline description |
| Project structure | ✅ Good | Tree view helpful |
| MCP tools table | ✅ Good | 45 tools documented |
| Prerequisites | ⚠️ Incomplete | Missing Python 3.10+ requirement |
| Installation | ⚠️ Incomplete | Assumes `python` command exists |
| Troubleshooting | ❌ Missing | No common issues section |

### 5.2 SETUP_GUIDE.md Assessment

**Overall Score:** 8/10

| Aspect | Rating | Notes |
|--------|--------|-------|
| Prerequisites | ✅ Comprehensive | System requirements table |
| Installation options | ✅ Good | pip and conda covered |
| Environment variables | ✅ Detailed | Table with descriptions |
| Troubleshooting | ✅ Good | Common issues with solutions |
| Census API instructions | ✅ Clear | Step-by-step guide |
| Development workflow | ✅ Good | Pre-commit, testing covered |

**Issues Found:**
- References `.env.example` that doesn't exist
- Some commands assume macOS (brew)
- No Windows-specific instructions

### 5.3 API_REFERENCE.md Assessment

**Overall Score:** 9/10

| Aspect | Rating | Notes |
|--------|--------|-------|
| Endpoint verification | ✅ Excellent | "Verified Feb 15, 2026" |
| Working endpoints | ✅ Comprehensive | HIFLD, CMS, FEMA, Census |
| Dead endpoints | ✅ Helpful | Lists broken URLs to avoid |
| Pagination info | ✅ Good | Max records documented |
| Query parameters | ✅ Good | Examples provided |

### 5.4 DATA_DICTIONARY.md Assessment

**Overall Score:** 9/10

| Aspect | Rating | Notes |
|--------|--------|-------|
| Column definitions | ✅ Comprehensive | 66 columns documented |
| Data types | ✅ Good | Type, range, description |
| Calculation logic | ✅ Excellent | Shows how indices are computed |
| Example values | ✅ Helpful | Real examples provided |
| Advanced features | ✅ Good | Compound risk, contagion explained |

---

## 6. Critical Issues Summary

### 🔴 High Priority (Fix Immediately)

1. **Python command inconsistency**
   - README uses `python`, system requires `python3`
   - Fix: Update README with OS-specific commands

2. **No .env.example file**
   - Documentation references file that doesn't exist
   - Fix: Create .env.example or remove references

3. **Mobile responsiveness broken**
   - Dashboard unusable on phones
   - Fix: Add responsive breakpoints, mobile navigation

4. **Missing accessibility features**
   - No keyboard navigation, screen reader support
   - Fix: Add ARIA labels, focus management, alt text

### 🟡 Medium Priority (Fix Soon)

5. **No county drill-down**
   - Cannot click map/table to see details
   - Fix: Add click handlers linking to detail view

6. **Limited ROI comparison**
   - Only shows one intervention type
   - Fix: Add intervention type selector, comparison table

7. **No data export**
   - Cannot download analysis results
   - Fix: Add CSV/Excel export buttons

8. **Missing contextual help**
   - Technical terms not explained
   - Fix: Add tooltips, ? icons, glossary

### 🟢 Low Priority (Nice to Have)

9. **No guided tour**
   - New users don't know where to start
   - Fix: Add onboarding walkthrough

10. **No favorites/bookmarks**
    - Cannot save frequently viewed counties
    - Fix: Add star/favorite functionality

---

## 7. Recommendations by User Persona

### For Emergency Managers
- Add "Alert Me" button for high-risk counties
- Show real-time weather alerts on main dashboard
- Add evacuation planning tools
- Include contact information for county emergency offices

### For Researchers
- Add data export functionality (CSV, Excel, JSON)
- Provide statistical analysis tools (correlation, regression)
- Enable custom metric creation
- Add citation information for academic use

### For Policymakers
- Add intervention comparison matrix
- Include cost-benefit visualization
- Provide printable executive summaries
- Show funding opportunity links

### For Public Health Officials
- Add health-specific dashboard view
- Include disease surveillance integration
- Show healthcare facility capacity
- Provide health disparity breakdowns

---

## 8. Conclusion

ResilienceAI demonstrates **strong technical capabilities** with comprehensive data integration, sophisticated analytics, and a solid MCP tool architecture. The platform successfully answers complex vulnerability questions and provides valuable insights for disaster preparedness.

However, **new user experience requires significant attention**. The setup process has friction points, mobile users are excluded, and accessibility standards are not met. The documentation is generally excellent but has gaps between written instructions and actual file availability.

### Key Strengths
- ✅ Rich, pre-processed dataset (3,222 counties × 66 features)
- ✅ 56 MCP tools for comprehensive analysis
- ✅ Clear visualizations with Plotly
- ✅ Well-documented data dictionary
- ✅ Real-world use cases are supported

### Key Weaknesses
- ❌ Setup friction for new users
- ❌ Poor mobile experience
- ❌ Limited accessibility support
- ❌ No guided onboarding
- ❌ Missing drill-down capabilities

### Priority Actions
1. Fix Python command documentation
2. Create .env.example file
3. Add responsive design for mobile
4. Implement keyboard navigation
5. Add data export functionality

---

*Test completed by: UX Testing Subagent*  
*Test environment: Linux, Python 3.12, Chrome browser*  
*Dashboard version: v2.0 (MUIDSI Hackathon 2026)*
