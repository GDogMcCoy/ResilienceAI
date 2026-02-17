# ResilienceAI Accessibility Enhancement Guide
## WCAG 2.1 AA Compliance & Inclusive Design

---

## Executive Summary

This document provides comprehensive accessibility guidelines for ResilienceAI to ensure WCAG 2.1 AA compliance, meeting legal requirements for government and public sector use. The guidelines cover all aspects of accessibility from design principles to implementation and testing.

### Legal Context
- **Section 508** (US Federal): Requires federal agencies to make ICT accessible
- **ADA Title II**: Requires state/local government digital services to be accessible
- **WCAG 2.1 AA**: International standard for web accessibility
- **EN 301 549**: European accessibility standard

---

## 1. Accessibility Audit Checklist

### 1.1 Perceivable (WCAG Principle 1)

#### 1.1.1 Text Alternatives
| Check | Requirement | Priority | Status |
|-------|-------------|----------|--------|
| [ ] | All images have meaningful alt text | P0 | ⬜ |
| [ ] | Decorative images have empty alt (alt="") | P0 | ⬜ |
| [ ] | Complex charts have detailed descriptions | P0 | ⬜ |
| [ ] | Form buttons have descriptive labels | P0 | ⬜ |
| [ ] | CAPTCHA has alternative access methods | P1 | ⬜ |
| [ ] | Audio content has transcripts | P1 | ⬜ |
| [ ] | Video content has captions | P1 | ⬜ |

#### 1.1.2 Time-based Media
| Check | Requirement | Priority | Status |
|-------|-------------|----------|--------|
| [ ] | Pre-recorded audio has text transcript | P1 | ⬜ |
| [ ] | Pre-recorded video has captions | P1 | ⬜ |
| [ ] | Video has audio description for visual info | P2 | ⬜ |
| [ ] | Live captions available for live broadcasts | P2 | ⬜ |

#### 1.1.3 Adaptable
| Check | Requirement | Priority | Status |
|-------|-------------|----------|--------|
| [ ] | Content readable without CSS | P0 | ⬜ |
| [ ] | Info structure preserved when zoomed to 200% | P0 | ⬜ |
| [ ] | Content doesn't require horizontal scroll at 320px | P0 | ⬜ |
| [ ] | Tables have proper headers | P0 | ⬜ |
| [ ] | Form labels programmatically associated | P0 | ⬜ |

#### 1.1.4 Distinguishable
| Check | Requirement | Priority | Status |
|-------|-------------|----------|--------|
| [ ] | Text contrast ratio ≥ 4.5:1 (normal) | P0 | ⬜ |
| [ ] | Large text contrast ratio ≥ 3:1 | P0 | ⬜ |
| [ ] | UI components contrast ratio ≥ 3:1 | P0 | ⬜ |
| [ ] | Text can be resized to 200% without loss | P0 | ⬜ |
| [ ] | Images of text avoided where possible | P1 | ⬜ |
| [ ] | No content flashes more than 3 times/second | P0 | ⬜ |

### 1.2 Operable (WCAG Principle 2)

#### 1.2.1 Keyboard Accessible
| Check | Requirement | Priority | Status |
|-------|-------------|----------|--------|
| [ ] | All functionality available via keyboard | P0 | ⬜ |
| [ ] | No keyboard traps | P0 | ⬜ |
| [ ] | Keyboard shortcuts documented | P1 | ⬜ |
| [ ] | Focus order is logical and meaningful | P0 | ⬜ |

#### 1.2.2 Enough Time
| Check | Requirement | Priority | Status |
|-------|-------------|----------|--------|
| [ ] | Users can turn off/adjust time limits | P1 | ⬜ |
| [ ] | Users can pause/stop moving content | P1 | ⬜ |
| [ ] | No auto-refresh without user control | P1 | ⬜ |

#### 1.2.3 Seizures and Physical Reactions
| Check | Requirement | Priority | Status |
|-------|-------------|----------|--------|
| [ ] | No flashing content >3Hz | P0 | ⬜ |
| [ ] | Animation can be disabled | P2 | ⬜ |

#### 1.2.4 Navigable
| Check | Requirement | Priority | Status |
|-------|-------------|----------|--------|
| [ ] | Page titles describe content | P0 | ⬜ |
| [ ] | Focus visible on all interactive elements | P0 | ⬜ |
| [ ] | Skip links provided for repeated content | P0 | ⬜ |
| [ ] | Page purpose clear from headings | P0 | ⬜ |
| [ ] | Focus order preserves meaning | P0 | ⬜ |

#### 1.2.5 Input Modalities
| Check | Requirement | Priority | Status |
|-------|-------------|----------|--------|
| [ ] | Touch targets minimum 44x44px | P1 | ⬜ |
| [ ] | Motion actions have alternatives | P2 | ⬜ |
| [ ] | Accidental activation prevented | P1 | ⬜ |

### 1.3 Understandable (WCAG Principle 3)

#### 1.3.1 Readable
| Check | Requirement | Priority | Status |
|-------|-------------|----------|--------|
| [ ] | Language of page identified | P0 | ⬜ |
| [ ] | Language of parts identified | P2 | ⬜ |
| [ ] | Unusual words defined | P2 | ⬜ |
| [ ] | Abbreviations expanded on first use | P2 | ⬜ |
| [ ] | Reading level appropriate (Grade 8-12) | P2 | ⬜ |

#### 1.3.2 Predictable
| Check | Requirement | Priority | Status |
|-------|-------------|----------|--------|
| [ ] | Navigation consistent across pages | P0 | ⬜ |
| [ ] | Components with same function look/operate same | P0 | ⬜ |
| [ ] | Context changes only on user request | P0 | ⬜ |

#### 1.3.3 Input Assistance
| Check | Requirement | Priority | Status |
|-------|-------------|----------|--------|
| [ ] | Input errors identified | P0 | ⬜ |
| [ ] | Labels/instructions provided | P0 | ⬜ |
| [ ] | Error suggestions provided | P0 | ⬜ |
| [ ] | Error prevention for important data | P1 | ⬜ |

### 1.4 Robust (WCAG Principle 4)

#### 1.4.1 Compatible
| Check | Requirement | Priority | Status |
|-------|-------------|----------|--------|
| [ ] | Valid HTML markup | P0 | ⬜ |
| [ ] | ARIA roles used correctly | P0 | ⬜ |
| [ ] | Name/role/value available to assistive tech | P0 | ⬜ |
| [ ] | Status messages announced to screen readers | P0 | ⬜ |

---

## 2. Implementation Guidelines

### 2.1 Color Contrast Requirements

#### Contrast Ratio Standards
```
┌─────────────────────────────────────────────────────────────┐
│ CONTRAST RATIO REQUIREMENTS (WCAG 2.1 AA)                   │
├─────────────────────────────────────────────────────────────┤
│ Normal Text (<18pt or <14pt bold):     4.5:1 minimum        │
│ Large Text (≥18pt or ≥14pt bold):      3:1 minimum          │
│ UI Components & Graphics:              3:1 minimum          │
│ Enhanced (AAA) Normal Text:            7:1 minimum          │
│ Enhanced (AAA) Large Text:             4.5:1 minimum        │
└─────────────────────────────────────────────────────────────┘
```

#### Approved Color Palette (WCAG AA Compliant)
```css
:root {
  /* Primary Colors - All 4.5:1+ on white */
  --color-primary-900: #1a365d;    /* 12.6:1 on white */
  --color-primary-800: #1e4e8c;    /* 7.8:1 on white */
  --color-primary-700: #2b6cb0;    /* 5.2:1 on white */
  --color-primary-600: #3182ce;    /* 4.5:1 on white */
  
  /* Secondary Colors */
  --color-secondary-900: #276749;  /* 7.2:1 on white */
  --color-secondary-800: #2f855a;  /* 4.8:1 on white */
  
  /* Semantic Colors */
  --color-error-700: #c53030;      /* 6.1:1 on white */
  --color-error-600: #e53e3e;      /* 4.6:1 on white */
  --color-warning-700: #c05621;    /* 5.4:1 on white */
  --color-success-700: #276749;    /* 7.2:1 on white */
  --color-info-700: #2b6cb0;       /* 5.2:1 on white */
  
  /* Neutral Colors */
  --color-gray-900: #1a202c;       /* 14.2:1 on white */
  --color-gray-800: #2d3748;       /* 10.1:1 on white */
  --color-gray-700: #4a5568;       /* 6.4:1 on white */
  --color-gray-600: #718096;       /* 4.6:1 on white */
  --color-gray-500: #a0aec0;       /* 3.0:1 on white - NOT for text */
  --color-gray-400: #cbd5e0;       /* 1.9:1 on white - backgrounds only */
  
  /* Background Colors */
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f7fafc;
  --color-bg-tertiary: #edf2f7;
}
```

#### Contrast Checking Utility
```javascript
// utils/contrast.js
/**
 * Calculate contrast ratio between two colors
 * @param {string} color1 - Hex color (e.g., '#ffffff')
 * @param {string} color2 - Hex color (e.g., '#000000')
 * @returns {number} Contrast ratio
 */
export function getContrastRatio(color1, color2) {
  const lum1 = getLuminance(color1);
  const lum2 = getLuminance(color2);
  const brightest = Math.max(lum1, lum2);
  const darkest = Math.min(lum1, lum2);
  return (brightest + 0.05) / (darkest + 0.05);
}

function getLuminance(hex) {
  const rgb = hexToRgb(hex);
  const [r, g, b] = rgb.map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? [
    parseInt(result[1], 16),
    parseInt(result[2], 16),
    parseInt(result[3], 16)
  ] : null;
}

// Usage in tests
export function isWCAGAACompliant(foreground, background, isLargeText = false) {
  const ratio = getContrastRatio(foreground, background);
  const minRatio = isLargeText ? 3 : 4.5;
  return ratio >= minRatio;
}
```

### 2.2 Screen Reader Compatibility

#### Semantic HTML Structure
```html
<!-- CORRECT: Semantic structure -->
<header>
  <nav aria-label="Main navigation">
    <ul>
      <li><a href="/dashboard" aria-current="page">Dashboard</a></li>
      <li><a href="/reports">Reports</a></li>
      <li><a href="/settings">Settings</a></li>
    </ul>
  </nav>
</header>

<main>
  <h1>Resilience Dashboard</h1>
  
  <section aria-labelledby="metrics-heading">
    <h2 id="metrics-heading">Key Metrics</h2>
    <!-- Content -->
  </section>
  
  <section aria-labelledby="charts-heading">
    <h2 id="charts-heading">Visual Analytics</h2>
    <!-- Content -->
  </section>
</main>

<footer>
  <p>&copy; 2024 ResilienceAI. All rights reserved.</p>
</footer>

<!-- INCORRECT: Non-semantic structure -->
<div class="header">
  <div class="nav">
    <div class="link">Dashboard</div>
    <div class="link">Reports</div>
  </div>
</div>
<div class="main">
  <div class="title">Resilience Dashboard</div>
</div>
```

#### ARIA Landmarks
```html
<body>
  <!-- Skip link for keyboard users -->
  <a href="#main-content" class="skip-link">
    Skip to main content
  </a>
  
  <header role="banner">
    <nav role="navigation" aria-label="Primary">
      <!-- Navigation items -->
    </nav>
  </header>
  
  <aside role="complementary" aria-label="Filters">
    <!-- Sidebar filters -->
  </aside>
  
  <main id="main-content" role="main" tabindex="-1">
    <!-- Main content -->
  </main>
  
  <footer role="contentinfo">
    <!-- Footer content -->
  </footer>
  
  <!-- Live region for dynamic updates -->
  <div role="status" aria-live="polite" aria-atomic="true" class="sr-only">
    <!-- Announcements will be read by screen readers -->
  </div>
</body>
```

#### Screen Reader Only Content
```css
/* styles/accessibility.css */

/**
 * Visually hidden but accessible to screen readers
 */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/**
 * Show element when focused (for skip links)
 */
.sr-only-focusable:focus {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: normal;
}

/**
 * Skip link styling
 */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-primary-900);
  color: white;
  padding: 8px 16px;
  z-index: 10000;
  text-decoration: none;
  border-radius: 0 0 4px 0;
}

.skip-link:focus {
  top: 0;
}
```

### 2.3 Keyboard Navigation

#### Focus Management
```css
/* styles/focus.css */

/**
 * Default focus indicator - visible and clear
 */
:focus {
  outline: 3px solid var(--color-primary-600);
  outline-offset: 2px;
}

/**
 * Focus visible (for keyboard only)
 */
:focus-visible {
  outline: 3px solid var(--color-primary-600);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(49, 130, 206, 0.3);
}

/**
 * Remove default outline for mouse users (keep for keyboard)
 */
:focus:not(:focus-visible) {
  outline: none;
}

/**
 * Custom focus styles for specific components
 */
.btn:focus-visible {
  outline: 3px solid var(--color-primary-600);
  outline-offset: 2px;
}

.card:focus-visible {
  outline: 3px solid var(--color-primary-600);
  outline-offset: 4px;
  box-shadow: 0 0 0 6px rgba(49, 130, 206, 0.2);
}

/**
 * Focus trap for modals
 */
.modal-open {
  overflow: hidden;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: auto;
}
```

#### Keyboard Navigation JavaScript
```javascript
// utils/keyboard-navigation.js

/**
 * Focus trap for modals and dialogs
 */
export class FocusTrap {
  constructor(element) {
    this.element = element;
    this.focusableSelectors = [
      'button:not([disabled])',
      'a[href]',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      '[tabindex]:not([tabindex="-1"])',
      '[contenteditable]'
    ].join(', ');
    
    this.handleKeyDown = this.handleKeyDown.bind(this);
  }
  
  activate() {
    this.previousFocus = document.activeElement;
    this.element.addEventListener('keydown', this.handleKeyDown);
    
    // Focus first focusable element
    const focusable = this.getFocusableElements();
    if (focusable.length > 0) {
      focusable[0].focus();
    }
  }
  
  deactivate() {
    this.element.removeEventListener('keydown', this.handleKeyDown);
    if (this.previousFocus) {
      this.previousFocus.focus();
    }
  }
  
  getFocusableElements() {
    return Array.from(
      this.element.querySelectorAll(this.focusableSelectors)
    ).filter(el => {
      return el.offsetParent !== null && !el.hasAttribute('disabled');
    });
  }
  
  handleKeyDown(event) {
    if (event.key !== 'Tab') return;
    
    const focusable = this.getFocusableElements();
    const firstFocusable = focusable[0];
    const lastFocusable = focusable[focusable.length - 1];
    
    if (event.shiftKey && document.activeElement === firstFocusable) {
      event.preventDefault();
      lastFocusable.focus();
    } else if (!event.shiftKey && document.activeElement === lastFocusable) {
      event.preventDefault();
      firstFocusable.focus();
    }
  }
}

/**
 * Keyboard shortcut manager
 */
export class KeyboardShortcuts {
  constructor() {
    this.shortcuts = new Map();
    this.handleKeyDown = this.handleKeyDown.bind(this);
  }
  
  register(shortcut, callback, description) {
    this.shortcuts.set(shortcut, { callback, description });
  }
  
  unregister(shortcut) {
    this.shortcuts.delete(shortcut);
  }
  
  start() {
    document.addEventListener('keydown', this.handleKeyDown);
  }
  
  stop() {
    document.removeEventListener('keydown', this.handleKeyDown);
  }
  
  handleKeyDown(event) {
    // Don't trigger shortcuts when user is typing in form fields
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)) {
      return;
    }
    
    const key = this.normalizeKey(event);
    const shortcut = this.shortcuts.get(key);
    
    if (shortcut) {
      event.preventDefault();
      shortcut.callback();
    }
  }
  
  normalizeKey(event) {
    const parts = [];
    if (event.ctrlKey) parts.push('Ctrl');
    if (event.altKey) parts.push('Alt');
    if (event.shiftKey) parts.push('Shift');
    if (event.metaKey) parts.push('Meta');
    parts.push(event.key);
    return parts.join('+');
  }
  
  getHelpText() {
    return Array.from(this.shortcuts.entries())
      .map(([key, { description }]) => `${key}: ${description}`)
      .join('\n');
  }
}

// Usage
const shortcuts = new KeyboardShortcuts();
shortcuts.register('Ctrl+/', () => openHelp(), 'Open help');
shortcuts.register('Ctrl+K', () => openSearch(), 'Open search');
shortcuts.register('Escape', () => closeModal(), 'Close modal');
shortcuts.start();
```

#### Tab Index Guidelines
```html
<!-- Tab index usage examples -->

<!-- Natural tab order (preferred) -->
<form>
  <label for="name">Name</label>
  <input type="text" id="name" />
  
  <label for="email">Email</label>
  <input type="email" id="email" />
  
  <button type="submit">Submit</button>
</form>

<!-- tabindex="0" - Add to tab order -->
<div role="button" tabindex="0" onclick="handleClick()">
  Custom button
</div>

<!-- tabindex="-1" - Programmatically focusable only -->
<div id="error-summary" tabindex="-1" role="alert">
  Please fix the errors below
</div>

<!-- tabindex="1+" - AVOID: Overrides natural tab order -->
<!-- This is an anti-pattern and should not be used -->
```

### 2.4 Alt Text for Visualizations

#### Chart Accessibility Components
```html
<!-- components/accessible-chart.html -->
<figure class="chart-container">
  <!-- Screen reader accessible summary -->
  <figcaption class="sr-only">
    <h3>Resilience Score Trend</h3>
    <p>
      Line chart showing resilience scores from January to December 2024.
      Scores range from 65 in January to 89 in December, 
      with a steady upward trend throughout the year.
      The average score is 78.
    </p>
  </figcaption>
  
  <!-- Visual chart for sighted users -->
  <div class="chart-visual" role="img" 
       aria-label="Resilience score trend chart">
    <canvas id="resilienceChart"></canvas>
  </div>
  
  <!-- Data table for screen readers -->
  <div class="chart-data">
    <table class="sr-only">
      <caption>Resilience Score Data</caption>
      <thead>
        <tr>
          <th scope="col">Month</th>
          <th scope="col">Score</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>January</td><td>65</td></tr>
        <tr><td>February</td><td>68</td></tr>
        <tr><td>March</td><td>72</td></tr>
        <!-- ... -->
        <tr><td>December</td><td>89</td></tr>
      </tbody>
    </table>
  </div>
  
  <!-- Toggle for data table visibility -->
  <button type="button" 
          class="btn btn-text"
          aria-expanded="false"
          aria-controls="chart-data-table"
          onclick="toggleDataTable()">
    Show data table
  </button>
</figure>
```

#### Chart Accessibility JavaScript
```javascript
// components/AccessibleChart.js

/**
 * Accessible chart wrapper component
 */
export class AccessibleChart {
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      title: '',
      description: '',
      dataTable: true,
      ...options
    };
    
    this.chartId = `chart-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  render() {
    this.container.innerHTML = `
      <figure class="accessible-chart" role="group" 
              aria-labelledby="${this.chartId}-title">
        
        <!-- Accessible title -->
        <figcaption id="${this.chartId}-title" class="chart-title">
          ${this.options.title}
        </figcaption>
        
        <!-- Screen reader description -->
        <div id="${this.chartId}-desc" class="sr-only">
          ${this.options.description}
        </div>
        
        <!-- Chart container -->
        <div class="chart-wrapper" 
             role="img"
             aria-labelledby="${this.chartId}-title ${this.chartId}-desc">
          <canvas id="${this.chartId}-canvas"></canvas>
        </div>
        
        <!-- Accessible data table -->
        ${this.options.dataTable ? this.renderDataTable() : ''}
        
        <!-- Controls -->
        <div class="chart-controls">
          <button type="button"
                  class="btn btn-sm"
                  aria-controls="${this.chartId}-table"
                  aria-expanded="false"
                  onclick="this.toggleDataTable()">
            <span class="btn-text">Show data table</span>
          </button>
          <button type="button"
                  class="btn btn-sm"
                  onclick="this.downloadCSV()">
            Download CSV
          </button>
        </div>
      </figure>
    `;
    
    this.initChart();
  }
  
  renderDataTable() {
    const data = this.options.data;
    return `
      <div id="${this.chartId}-table" 
           class="chart-data-table"
           hidden>
        <table>
          <caption>${this.options.title} - Data Table</caption>
          <thead>
            <tr>
              ${data.headers.map(h => `<th scope="col">${h}</th>`).join('')}
            </tr>
          </thead>
          <tbody>
            ${data.rows.map(row => `
              <tr>
                ${row.map((cell, i) => 
                  i === 0 ? `<th scope="row">${cell}</th>` : `<td>${cell}</td>`
                ).join('')}
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  }
  
  toggleDataTable() {
    const table = this.container.querySelector(`#${this.chartId}-table`);
    const button = this.container.querySelector('[aria-controls="${this.chartId}-table"]');
    const isExpanded = button.getAttribute('aria-expanded') === 'true';
    
    table.hidden = isExpanded;
    button.setAttribute('aria-expanded', !isExpanded);
    button.querySelector('.btn-text').textContent = 
      isExpanded ? 'Show data table' : 'Hide data table';
  }
  
  announceUpdate(message) {
    const announcer = document.getElementById('sr-announcer');
    if (announcer) {
      announcer.textContent = message;
    }
  }
}
```

### 2.5 Accessible Forms

#### Form Structure
```html
<!-- components/accessible-form.html -->
<form class="accessible-form" novalidate>
  
  <!-- Error summary (shown when validation fails) -->
  <div id="error-summary" 
       class="error-summary" 
       role="alert"
       aria-live="assertive"
       tabindex="-1"
       hidden>
    <h2>There is a problem</h2>
    <ul class="error-list">
      <!-- Errors populated dynamically -->
    </ul>
  </div>
  
  <!-- Text input with full labeling -->
  <div class="form-group">
    <label for="organization-name">
      Organization name
      <span class="required" aria-hidden="true">*</span>
      <span class="sr-only">(required)</span>
    </label>
    <input 
      type="text" 
      id="organization-name"
      name="organizationName"
      required
      aria-required="true"
      aria-describedby="org-name-hint org-name-error"
      autocomplete="organization"
    />
    <span id="org-name-hint" class="form-hint">
      Enter your organization's legal name
    </span>
    <span id="org-name-error" class="error-message" role="alert" hidden>
      Enter your organization name
    </span>
  </div>
  
  <!-- Email input -->
  <div class="form-group">
    <label for="contact-email">
      Contact email
      <span class="required" aria-hidden="true">*</span>
      <span class="sr-only">(required)</span>
    </label>
    <input 
      type="email" 
      id="contact-email"
      name="contactEmail"
      required
      aria-required="true"
      aria-describedby="email-error"
      autocomplete="email"
    />
    <span id="email-error" class="error-message" role="alert" hidden>
      Enter a valid email address
    </span>
  </div>
  
  <!-- Select dropdown -->
  <div class="form-group">
    <label for="industry-sector">
      Industry sector
      <span class="required" aria-hidden="true">*</span>
      <span class="sr-only">(required)</span>
    </label>
    <select 
      id="industry-sector"
      name="industrySector"
      required
      aria-required="true"
      aria-describedby="sector-error"
    >
      <option value="">Select an industry</option>
      <option value="healthcare">Healthcare</option>
      <option value="finance">Finance</option>
      <option value="manufacturing">Manufacturing</option>
      <option value="technology">Technology</option>
      <option value="government">Government</option>
    </select>
    <span id="sector-error" class="error-message" role="alert" hidden>
      Select an industry sector
    </span>
  </div>
  
  <!-- Radio button group -->
  <fieldset class="form-group">
    <legend>
      Organization size
      <span class="required" aria-hidden="true">*</span>
      <span class="sr-only">(required)</span>
    </legend>
    <div class="radio-group">
      <label class="radio-label">
        <input 
          type="radio" 
          name="orgSize"
          value="small"
          required
          aria-required="true"
        />
        <span>Small (1-50 employees)</span>
      </label>
      <label class="radio-label">
        <input 
          type="radio" 
          name="orgSize"
          value="medium"
        />
        <span>Medium (51-250 employees)</span>
      </label>
      <label class="radio-label">
        <input 
          type="radio" 
          name="orgSize"
          value="large"
        />
        <span>Large (251+ employees)</span>
      </label>
    </div>
  </fieldset>
  
  <!-- Checkbox group -->
  <fieldset class="form-group">
    <legend>
      Resilience domains to assess
      <span class="sr-only">(select all that apply)</span>
    </legend>
    <div class="checkbox-group">
      <label class="checkbox-label">
        <input type="checkbox" name="domains" value="operational" />
        <span>Operational Resilience</span>
      </label>
      <label class="checkbox-label">
        <input type="checkbox" name="domains" value="financial" />
        <span>Financial Resilience</span>
      </label>
      <label class="checkbox-label">
        <input type="checkbox" name="domains" value="cyber" />
        <span>Cyber Resilience</span>
      </label>
      <label class="checkbox-label">
        <input type="checkbox" name="domains" value="supply-chain" />
        <span>Supply Chain Resilience</span>
      </label>
    </div>
  </fieldset>
  
  <!-- Submit button -->
  <div class="form-actions">
    <button type="submit" class="btn btn-primary">
      Submit assessment
    </button>
    <button type="reset" class="btn btn-secondary">
      Clear form
    </button>
  </div>
  
</form>
```

#### Form Validation JavaScript
```javascript
// components/AccessibleForm.js

/**
 * Accessible form validation
 */
export class AccessibleForm {
  constructor(formElement) {
    this.form = formElement;
    this.errorSummary = formElement.querySelector('#error-summary');
    
    this.init();
  }
  
  init() {
    // Real-time validation on blur
    this.form.querySelectorAll('input, select, textarea').forEach(field => {
      field.addEventListener('blur', () => this.validateField(field));
      field.addEventListener('input', () => this.clearFieldError(field));
    });
    
    // Form submission
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));
  }
  
  validateField(field) {
    const errorElement = document.getElementById(
      field.getAttribute('aria-describedby')?.split(' ').find(id => id.includes('error'))
    );
    
    let errorMessage = '';
    
    if (field.validity.valueMissing) {
      errorMessage = this.getRequiredMessage(field);
    } else if (field.validity.typeMismatch) {
      errorMessage = this.getTypeMismatchMessage(field);
    } else if (field.validity.patternMismatch) {
      errorMessage = this.getPatternMessage(field);
    }
    
    if (errorMessage) {
      this.showFieldError(field, errorElement, errorMessage);
      return false;
    } else {
      this.clearFieldError(field);
      return true;
    }
  }
  
  showFieldError(field, errorElement, message) {
    field.setAttribute('aria-invalid', 'true');
    field.classList.add('error');
    
    if (errorElement) {
      errorElement.textContent = message;
      errorElement.hidden = false;
    }
  }
  
  clearFieldError(field) {
    field.removeAttribute('aria-invalid');
    field.classList.remove('error');
    
    const errorId = field.getAttribute('aria-describedby')
      ?.split(' ')
      .find(id => id.includes('error'));
    
    if (errorId) {
      const errorElement = document.getElementById(errorId);
      if (errorElement) {
        errorElement.hidden = true;
      }
    }
  }
  
  handleSubmit(event) {
    event.preventDefault();
    
    const fields = this.form.querySelectorAll('input, select, textarea');
    const errors = [];
    
    fields.forEach(field => {
      if (!this.validateField(field)) {
        errors.push({
          field,
          message: document.getElementById(
            field.getAttribute('aria-describedby')?.split(' ').find(id => id.includes('error'))
          )?.textContent
        });
      }
    });
    
    if (errors.length > 0) {
      this.showErrorSummary(errors);
    } else {
      this.submitForm();
    }
  }
  
  showErrorSummary(errors) {
    const errorList = this.errorSummary.querySelector('.error-list');
    errorList.innerHTML = errors.map(({ field, message }) => `
      <li>
        <a href="#${field.id}" onclick="document.getElementById('${field.id}').focus(); return false;">
          ${message}
        </a>
      </li>
    `).join('');
    
    this.errorSummary.hidden = false;
    this.errorSummary.focus();
  }
  
  getRequiredMessage(field) {
    const label = document.querySelector(`label[for="${field.id}"]`);
    const labelText = label?.textContent?.replace(/\*/g, '').trim() || 'This field';
    return `Enter ${labelText.toLowerCase()}`;
  }
  
  getTypeMismatchMessage(field) {
    if (field.type === 'email') {
      return 'Enter an email address in the correct format, like name@example.com';
    }
    return `Enter a valid ${field.type}`;
  }
  
  getPatternMessage(field) {
    return field.dataset.errorMessage || 'Enter the information in the correct format';
  }
}
```

### 2.6 ARIA Labels and Roles

#### Common ARIA Patterns
```html
<!-- Button with icon -->
<button type="button" aria-label="Close dialog">
  <svg aria-hidden="true" focusable="false">...</svg>
</button>

<!-- Status message -->
<div role="status" aria-live="polite" class="sr-only">
  Assessment saved successfully
</div>

<!-- Alert message -->
<div role="alert" aria-live="assertive" class="alert alert-error">
  <strong>Error:</strong> Unable to save assessment
</div>

<!-- Progress indicator -->
<div role="progressbar" 
     aria-valuenow="45" 
     aria-valuemin="0" 
     aria-valuemax="100"
     aria-label="Assessment progress">
  <div class="progress-bar" style="width: 45%"></div>
</div>

<!-- Tabs -->
<div class="tabs">
  <div role="tablist" aria-label="Assessment sections">
    <button role="tab" 
            aria-selected="true" 
            aria-controls="tab-panel-1"
            id="tab-1">
      Overview
    </button>
    <button role="tab" 
            aria-selected="false" 
            aria-controls="tab-panel-2"
            id="tab-2"
            tabindex="-1">
      Details
    </button>
  </div>
  
  <div role="tabpanel" 
       id="tab-panel-1" 
       aria-labelledby="tab-1">
    <!-- Panel content -->
  </div>
  
  <div role="tabpanel" 
       id="tab-panel-2" 
       aria-labelledby="tab-2"
       hidden>
    <!-- Panel content -->
  </div>
</div>

<!-- Accordion -->
<div class="accordion">
  <h3>
    <button aria-expanded="false" 
            aria-controls="accordion-section-1"
            id="accordion-header-1">
      Section 1
      <span aria-hidden="true">+</span>
    </button>
  </h3>
  <div id="accordion-section-1" 
       role="region" 
       aria-labelledby="accordion-header-1"
       hidden>
    <!-- Content -->
  </div>
</div>

<!-- Modal/Dialog -->
<div role="dialog" 
     aria-modal="true"
     aria-labelledby="dialog-title"
     aria-describedby="dialog-description">
  <h2 id="dialog-title">Confirm Action</h2>
  <p id="dialog-description">
    Are you sure you want to delete this assessment?
  </p>
  <button>Cancel</button>
  <button>Delete</button>
</div>

<!-- Breadcrumb -->
<nav aria-label="Breadcrumb">
  <ol>
    <li><a href="/">Home</a></li>
    <li><a href="/assessments">Assessments</a></li>
    <li aria-current="page">Current Assessment</li>
  </ol>
</nav>

<!-- Search results -->
<div role="search">
  <label for="search-input">Search assessments</label>
  <input type="search" id="search-input" />
  <button type="submit">Search</button>
</div>

<div role="region" aria-label="Search results">
  <p>Found 12 results</p>
  <ul>
    <li><a href="...">Result 1</a></li>
    <!-- ... -->
  </ul>
</div>
```

#### ARIA Best Practices
```javascript
// utils/aria-utils.js

/**
 * ARIA utility functions
 */

/**
 * Announce message to screen readers
 */
export function announce(message, priority = 'polite') {
  const announcer = document.getElementById('sr-announcer') || createAnnouncer();
  announcer.setAttribute('aria-live', priority);
  
  // Clear and set new message
  announcer.textContent = '';
  setTimeout(() => {
    announcer.textContent = message;
  }, 100);
}

function createAnnouncer() {
  const announcer = document.createElement('div');
  announcer.id = 'sr-announcer';
  announcer.className = 'sr-only';
  announcer.setAttribute('aria-live', 'polite');
  announcer.setAttribute('aria-atomic', 'true');
  document.body.appendChild(announcer);
  return announcer;
}

/**
 * Set loading state on element
 */
export function setLoadingState(element, isLoading) {
  if (isLoading) {
    element.setAttribute('aria-busy', 'true');
    element.setAttribute('aria-label', 'Loading...');
  } else {
    element.removeAttribute('aria-busy');
    element.removeAttribute('aria-label');
  }
}

/**
 * Update live region
 */
export function updateLiveRegion(regionId, message) {
  const region = document.getElementById(regionId);
  if (region) {
    region.textContent = message;
  }
}

/**
 * Set current page in navigation
 */
export function setCurrentPage(navItem) {
  // Remove current from all items
  navItem.closest('nav').querySelectorAll('[aria-current]').forEach(item => {
    item.removeAttribute('aria-current');
  });
  
  // Set current on active item
  navItem.setAttribute('aria-current', 'page');
}

/**
 * Manage expanded state
 */
export function toggleExpanded(button, target) {
  const isExpanded = button.getAttribute('aria-expanded') === 'true';
  button.setAttribute('aria-expanded', !isExpanded);
  target.hidden = isExpanded;
}
```

---

## 3. Testing Tools and Procedures

### 3.1 Automated Testing Tools

#### Recommended Tools
| Tool | Purpose | Usage |
|------|---------|-------|
| axe DevTools | Automated WCAG testing | Browser extension, CI/CD |
| Lighthouse | Accessibility audit | Chrome DevTools, CI/CD |
| WAVE | Visual accessibility check | Browser extension |
| Pa11y | Command-line testing | CI/CD integration |
| jest-axe | Unit testing | Jest test framework |
| Cypress-axe | E2E testing | Cypress framework |

#### Axe Core Implementation
```javascript
// tests/accessibility/axe.test.js
import { axe, toHaveNoViolations } from 'jest-axe';
import { render } from '@testing-library/react';
import Dashboard from '../../components/Dashboard';

expect.extend(toHaveNoViolations);

describe('Dashboard Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(<Dashboard />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

#### Pa11y CI Configuration
```json
// .pa11yci
{
  "defaults": {
    "timeout": 10000,
    "wait": 2000,
    "standard": "WCAG2AA",
    "runners": ["axe", "htmlcs"],
    "ignore": [
      "WCAG2AA.Principle1.Guideline1_4.1_4_3.G18.Fail"
    ]
  },
  "urls": [
    "http://localhost:3000/",
    "http://localhost:3000/dashboard",
    "http://localhost:3000/assessments",
    "http://localhost:3000/reports"
  ]
}
```

#### Cypress Accessibility Tests
```javascript
// cypress/e2e/accessibility.cy.js
describe('Accessibility Tests', () => {
  beforeEach(() => {
    cy.visit('/');
    cy.injectAxe();
  });

  it('Has no detectable a11y violations on load', () => {
    cy.checkA11y();
  });

  it('Has no violations on dashboard', () => {
    cy.visit('/dashboard');
    cy.checkA11y(null, {
      rules: {
        'color-contrast': { enabled: true }
      }
    });
  });

  it('Has no violations in modal', () => {
    cy.get('[data-testid="open-modal"]').click();
    cy.checkA11y('.modal', {
      rules: {
        'aria-hidden-focus': { enabled: true }
      }
    });
  });
});
```

### 3.2 Manual Testing Procedures

#### Keyboard Testing Checklist
```
┌────────────────────────────────────────────────────────────────┐
│ KEYBOARD TESTING CHECKLIST                                     │
├────────────────────────────────────────────────────────────────┤
│ [ ] All interactive elements reachable via Tab                 │
│ [ ] Tab order follows visual flow (left→right, top→bottom)    │
│ [ ] Shift+Tab navigates backwards                              │
│ [ ] Enter activates buttons and links                          │
│ [ ] Space activates buttons and checkboxes                     │
│ [ ] Arrow keys navigate within widgets (menus, tabs, etc.)     │
│ [ ] Escape closes modals and menus                             │
│ [ ] Focus visible on all interactive elements                  │
│ [ ] No keyboard traps (can Tab out of all elements)            │
│ [ ] Skip link works and is visible on focus                    │
│ [ ] Focus returns to trigger when modal closes                 │
└────────────────────────────────────────────────────────────────┘
```

#### Screen Reader Testing
```
┌────────────────────────────────────────────────────────────────┐
│ SCREEN READER TESTING CHECKLIST                                │
├────────────────────────────────────────────────────────────────┤
│ NVDA (Windows)                                                 │
│ [ ] All content readable in browse mode                        │
│ [ ] Form labels announced correctly                            │
│ [ ] Error messages announced when they appear                  │
│ [ ] Dynamic updates announced via live regions                 │
│ [ ] Tables announced with proper headers                       │
│ [ ] Images have meaningful alt text or marked decorative       │
│ [ ] Headings provide proper page structure                     │
│ [ ] Landmarks navigable via shortcuts                          │
│                                                                │
│ JAWS (Windows)                                                 │
│ [ ] Same tests as NVDA                                         │
│ [ ] Virtual cursor navigation works                            │
│ [ ] Forms mode activates correctly                             │
│                                                                │
│ VoiceOver (macOS/iOS)                                          │
│ [ ] Rotor shows proper heading/landmark structure              │
│ [ ] Touch gestures work on mobile                              │
│ [ ] All content accessible via swipe navigation                │
│                                                                │
│ TalkBack (Android)                                             │
│ [ ] All interactive elements accessible                        │
│ [ ] Focus indicator visible                                    │
└────────────────────────────────────────────────────────────────┘
```

#### Visual Testing
```
┌────────────────────────────────────────────────────────────────┐
│ VISUAL TESTING CHECKLIST                                       │
├────────────────────────────────────────────────────────────────┤
│ [ ] Text readable at 200% zoom                                 │
│ [ ] No horizontal scroll at 320px width                        │
│ [ ] Content readable without CSS                               │
│ [ ] Color not sole means of conveying information              │
│ [ ] Focus indicator visible on all elements                    │
│ [ ] Contrast ratios meet WCAG AA standards                     │
│ [ ] Text spacing can be adjusted without loss of content       │
│ [ ] Animations can be disabled                                 │
│ [ ] No content flashes more than 3 times per second            │
└────────────────────────────────────────────────────────────────┘
```

### 3.3 Testing Documentation Template
```markdown
# Accessibility Test Report

## Test Information
- **Date**: [Date]
- **Tester**: [Name]
- **Page/Feature**: [URL/Feature]
- **Browser**: [Browser + Version]
- **Screen Reader**: [NVDA/JAWS/VoiceOver/TalkBack + Version]

## Automated Testing Results
| Tool | Issues Found | Severity | Status |
|------|--------------|----------|--------|
| axe | 0 | - | Pass |
| Lighthouse | 2 warnings | Low | Review |
| WAVE | 1 error | High | Fix |

## Manual Testing Results

### Keyboard Navigation
| Test | Result | Notes |
|------|--------|-------|
| Tab order | Pass | Logical flow |
| Focus visibility | Pass | Clear outline |
| No keyboard traps | Pass | - |
| Skip link | Pass | Works correctly |

### Screen Reader
| Test | Result | Notes |
|------|--------|-------|
| Page title | Pass | Descriptive |
| Headings | Pass | Proper hierarchy |
| Landmarks | Pass | All present |
| Images | Fail | Missing alt on chart |
| Forms | Pass | Labels associated |
| Live regions | Pass | Updates announced |

### Visual
| Test | Result | Notes |
|------|--------|-------|
| 200% zoom | Pass | No content loss |
| 320px width | Pass | No horizontal scroll |
| Color contrast | Fail | Button contrast 3.8:1 |
| Focus indicator | Pass | Visible on all |

## Issues Found
1. [Issue description] - [Severity] - [Recommendation]

## Recommendations
- [Recommendation 1]
- [Recommendation 2]

## Sign-off
- [ ] Tester
- [ ] Reviewer
```

---

## 4. Compliance Documentation

### 4.1 VPAT (Voluntary Product Accessibility Template)

```markdown
# Voluntary Product Accessibility Template (VPAT)
## ResilienceAI Platform v2.0

### Report Date: [Date]
### Product Description: AI-powered organizational resilience assessment platform
### Contact Information: accessibility@resilienceai.com

---

## WCAG 2.1 Level A & AA Report

### Principle 1: Perceivable

#### 1.1 Text Alternatives
| Criteria | Level | Status | Remarks |
|----------|-------|--------|---------|
| 1.1.1 Non-text Content | A | Supports | All images have alt text |

#### 1.2 Time-based Media
| Criteria | Level | Status | Remarks |
|----------|-------|--------|---------|
| 1.2.1 Audio-only/Video-only | A | N/A | No audio/video content |
| 1.2.2 Captions (Prerecorded) | A | N/A | No video content |

#### 1.3 Adaptable
| Criteria | Level | Status | Remarks |
|----------|-------|--------|---------|
| 1.3.1 Info and Relationships | A | Supports | Semantic HTML used |
| 1.3.2 Meaningful Sequence | A | Supports | Logical reading order |
| 1.3.3 Sensory Characteristics | A | Supports | No sensory-only info |
| 1.3.4 Orientation | AA | Supports | Works in any orientation |
| 1.3.5 Identify Input Purpose | AA | Supports | Autocomplete attributes |

#### 1.4 Distinguishable
| Criteria | Level | Status | Remarks |
|----------|-------|--------|---------|
| 1.4.1 Use of Color | A | Supports | Color not sole indicator |
| 1.4.2 Audio Control | A | N/A | No auto-playing audio |
| 1.4.3 Contrast (Minimum) | AA | Supports | 4.5:1 minimum met |
| 1.4.4 Resize Text | AA | Supports | Works at 200% |
| 1.4.5 Images of Text | AA | Supports | Text used instead |
| 1.4.10 Reflow | AA | Supports | No horizontal scroll |
| 1.4.11 Non-text Contrast | AA | Supports | 3:1 for UI components |
| 1.4.12 Text Spacing | AA | Supports | Content preserved |
| 1.4.13 Content on Hover/Focus | AA | Supports | Hover content dismissible |

### Principle 2: Operable

#### 2.1 Keyboard Accessible
| Criteria | Level | Status | Remarks |
|----------|-------|--------|---------|
| 2.1.1 Keyboard | A | Supports | All functions keyboard accessible |
| 2.1.2 No Keyboard Trap | A | Supports | No traps found |
| 2.1.4 Character Key Shortcuts | A | Supports | No single-key shortcuts |

#### 2.2 Enough Time
| Criteria | Level | Status | Remarks |
|----------|-------|--------|---------|
| 2.2.1 Timing Adjustable | A | N/A | No time limits |
| 2.2.2 Pause, Stop, Hide | A | N/A | No auto-updating content |

#### 2.3 Seizures and Physical Reactions
| Criteria | Level | Status | Remarks |
|----------|-------|--------|---------|
| 2.3.1 Three Flashes or Below | A | Supports | No flashing content |
| 2.3.3 Animation from Interactions | AAA | N/A | - |

#### 2.4 Navigable
| Criteria | Level | Status | Remarks |
|----------|-------|--------|---------|
| 2.4.1 Bypass Blocks | A | Supports | Skip links provided |
| 2.4.2 Page Titled | A | Supports | Descriptive titles |
| 2.4.3 Focus Order | A | Supports | Logical focus order |
| 2.4.4 Link Purpose | A | Supports | Link text descriptive |
| 2.4.5 Multiple Ways | AA | Supports | Search + navigation |
| 2.4.6 Headings and Labels | AA | Supports | Descriptive headings |
| 2.4.7 Focus Visible | AA | Supports | Visible focus indicator |

#### 2.5 Input Modalities
| Criteria | Level | Status | Remarks |
|----------|-------|--------|---------|
| 2.5.1 Pointer Gestures | A | Supports | No complex gestures |
| 2.5.2 Pointer Cancellation | A | Supports | Up-event activation |
| 2.5.3 Label in Name | A | Supports | Visible label in accessible name |
| 2.5.4 Motion Actuation | A | N/A | No motion-based actions |

### Principle 3: Understandable

#### 3.1 Readable
| Criteria | Level | Status | Remarks |
|----------|-------|--------|---------|
| 3.1.1 Language of Page | A | Supports | Lang attribute set |
| 3.1.2 Language of Parts | AA | Supports | Language changes marked |

#### 3.2 Predictable
| Criteria | Level | Status | Remarks |
|----------|-------|--------|---------|
| 3.2.1 On Focus | A | Supports | No context change on focus |
| 3.2.2 On Input | A | Supports | No context change on input |
| 3.2.3 Consistent Navigation | AA | Supports | Navigation consistent |
| 3.2.4 Consistent Identification | AA | Supports | Icons consistent |

#### 3.3 Input Assistance
| Criteria | Level | Status | Remarks |
|----------|-------|--------|---------|
| 3.3.1 Error Identification | A | Supports | Errors clearly identified |
| 3.3.2 Labels/Instructions | A | Supports | Labels provided |
| 3.3.3 Error Suggestion | AA | Supports | Suggestions provided |
| 3.3.4 Error Prevention | AA | Supports | Confirmation for deletions |

### Principle 4: Robust

#### 4.1 Compatible
| Criteria | Level | Status | Remarks |
|----------|-------|--------|---------|
| 4.1.1 Parsing | A | Supports | Valid HTML |
| 4.1.2 Name, Role, Value | A | Supports | ARIA used correctly |
| 4.1.3 Status Messages | AA | Supports | Live regions used |

---

## Legal Disclaimer

This VPAT represents the accessibility status of ResilienceAI as of the report date. 
Accessibility is an ongoing commitment, and we continuously work to improve our platform.

For accessibility support or to report issues:
- Email: accessibility@resilienceai.com
- Phone: 1-800-ACCESS-1
```

### 4.2 Accessibility Statement

```markdown
# Accessibility Statement

## Our Commitment
ResilienceAI is committed to ensuring digital accessibility for people with disabilities. 
We are continually improving the user experience for everyone and applying the relevant 
accessibility standards.

## Conformance Status
The Web Content Accessibility Guidelines (WCAG) defines requirements for designers and 
developers to improve accessibility for people with disabilities. It defines three levels 
of conformance: Level A, Level AA, and Level AAA.

**ResilienceAI is partially conformant with WCAG 2.1 level AA.** 
Partially conformant means that some parts of the content do not fully conform to the 
accessibility standard.

## Accessibility Features
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode
- Text resizing up to 200%
- Skip links for navigation
- Descriptive alt text for images
- Accessible forms with error identification
- Focus indicators on all interactive elements

## Known Limitations
- Some legacy PDF reports may not be fully accessible
- Third-party embedded content may have accessibility issues
- Complex data visualizations may require additional assistance

## Feedback
We welcome your feedback on the accessibility of ResilienceAI. Please let us know if you 
encounter accessibility barriers:

- Email: accessibility@resilienceai.com
- Phone: 1-800-ACCESS-1
- Postal address: 123 Accessibility Way, Suite 100

We aim to respond to accessibility feedback within 2 business days.

## Assessment Approach
ResilienceAI assesses accessibility through:
- Self-evaluation using automated testing tools
- Manual testing with assistive technologies
- User testing with people with disabilities
- Third-party accessibility audits

## Formal Complaints
If you are not satisfied with our response to your accessibility concern, you may file 
a formal complaint by contacting our Accessibility Officer at accessibility-officer@resilienceai.com.

## Date
This statement was created on [Date] and last updated on [Date].
```

---

## 5. Training Materials

### 5.1 Developer Training

#### Module 1: Accessibility Fundamentals
```markdown
# Module 1: Accessibility Fundamentals

## Learning Objectives
- Understand why accessibility matters
- Learn about different types of disabilities
- Familiarize with assistive technologies
- Understand WCAG principles

## Key Concepts

### Why Accessibility Matters
1. **Legal Requirements**: Section 508, ADA, international laws
2. **Business Benefits**: Larger audience, better SEO, reduced legal risk
3. **Moral Imperative**: Equal access for all
4. **Technical Benefits**: Better code quality, improved usability

### Types of Disabilities
- **Visual**: Blindness, low vision, color blindness
- **Auditory**: Deafness, hard of hearing
- **Motor**: Limited movement, tremors, paralysis
- **Cognitive**: Learning disabilities, memory issues, attention disorders

### Assistive Technologies
- Screen readers (NVDA, JAWS, VoiceOver)
- Screen magnifiers
- Voice recognition software
- Switch devices
- Braille displays

### WCAG Principles (POUR)
1. **Perceivable**: Information must be presentable
2. **Operable**: Interface components must be operable
3. **Understandable**: Information and operation must be understandable
4. **Robust**: Content must work with assistive technologies

## Exercises
1. Install NVDA and navigate a webpage
2. Try using only keyboard for 30 minutes
3. Test color contrast on your current project
```

#### Module 2: Semantic HTML
```markdown
# Module 2: Semantic HTML

## Learning Objectives
- Understand the importance of semantic HTML
- Learn proper heading hierarchy
- Use ARIA landmarks correctly
- Create accessible tables and forms

## Best Practices

### Headings
```html
<!-- Correct -->
<h1>Page Title</h1>
  <h2>Section 1</h2>
    <h3>Subsection 1.1</h3>
  <h2>Section 2</h2>

<!-- Incorrect -->
<h1>Page Title</h1>
  <h4>Section 1</h4>  <!-- Skipped h2, h3 -->
  <h2>Section 2</h2>
```

### Landmarks
```html
<header role="banner">...</header>
<nav role="navigation">...</nav>
<main role="main">...</main>
<aside role="complementary">...</aside>
<footer role="contentinfo">...</footer>
```

### Tables
```html
<table>
  <caption>Quarterly Sales</caption>
  <thead>
    <tr>
      <th scope="col">Quarter</th>
      <th scope="col">Sales</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Q1</th>
      <td>$100,000</td>
    </tr>
  </tbody>
</table>
```

## Exercises
1. Convert a non-semantic page to semantic HTML
2. Fix heading hierarchy issues
3. Add proper landmarks to a template
```

### 5.2 Designer Training

#### Color and Contrast Guidelines
```markdown
# Color and Contrast for Designers

## Contrast Requirements
- Normal text: 4.5:1 minimum
- Large text: 3:1 minimum
- UI components: 3:1 minimum

## Tools
- WebAIM Contrast Checker
- Stark plugin for Figma/Sketch
- Colour Contrast Analyser (CCA)

## Best Practices
1. Never rely on color alone
2. Use patterns/textures in addition to color
3. Test with color blindness simulators
4. Provide dark mode option

## Color Palette Example
```
Primary: #2B6CB0 (5.2:1 on white)
Success: #276749 (7.2:1 on white)
Warning: #C05621 (5.4:1 on white)
Error: #C53030 (6.1:1 on white)
```

## Common Mistakes
- Using light gray on white
- Red/green combinations without additional indicators
- Insufficient contrast on buttons
```

### 5.3 Content Creator Training

#### Writing Accessible Content
```markdown
# Writing Accessible Content

## Guidelines

### Headings
- Use descriptive headings
- Maintain proper hierarchy
- Don't skip levels

### Links
- Use descriptive link text
- Avoid "click here" or "read more"
- Example: "Download the accessibility guide" not "Click here"

### Alt Text
- Describe the image's purpose, not just appearance
- Keep it concise (under 125 characters)
- Use empty alt for decorative images

### Examples
```
Good: "Chart showing 25% increase in resilience scores"
Bad: "Chart"
Bad: "Image of a chart with blue and green bars"
```

### Documents
- Use proper heading styles in Word/Google Docs
- Add alt text to images
- Use tables for data, not layout
- Export to accessible PDF
```

---

## 6. Integration with Existing UI

### 6.1 Component Library Updates

#### Accessible Button Component
```jsx
// components/Button/Button.jsx
import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import './Button.css';

/**
 * Accessible button component
 * 
 * @example
 * <Button variant="primary" onClick={handleClick}>
 *   Submit
 * </Button>
 */
export const Button = React.forwardRef(({
  children,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  icon = null,
  iconPosition = 'left',
  onClick,
  type = 'button',
  ariaLabel,
  ariaExpanded,
  ariaControls,
  ariaPressed,
  className,
  ...props
}, ref) => {
  const buttonClasses = classNames(
    'btn',
    `btn--${variant}`,
    `btn--${size}`,
    {
      'btn--disabled': disabled,
      'btn--loading': loading,
      'btn--with-icon': icon,
    },
    className
  );

  return (
    <button
      ref={ref}
      type={type}
      className={buttonClasses}
      onClick={onClick}
      disabled={disabled || loading}
      aria-label={ariaLabel}
      aria-expanded={ariaExpanded}
      aria-controls={ariaControls}
      aria-pressed={ariaPressed}
      aria-busy={loading}
      {...props}
    >
      {loading && (
        <span className="btn__spinner" aria-hidden="true">
          <LoadingIcon />
        </span>
      )}
      {icon && iconPosition === 'left' && (
        <span className="btn__icon btn__icon--left" aria-hidden="true">
          {icon}
        </span>
      )}
      <span className="btn__text">{children}</span>
      {icon && iconPosition === 'right' && (
        <span className="btn__icon btn__icon--right" aria-hidden="true">
          {icon}
        </span>
      )}
    </button>
  );
});

Button.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(['primary', 'secondary', 'tertiary', 'danger']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  disabled: PropTypes.bool,
  loading: PropTypes.bool,
  icon: PropTypes.node,
  iconPosition: PropTypes.oneOf(['left', 'right']),
  onClick: PropTypes.func,
  type: PropTypes.oneOf(['button', 'submit', 'reset']),
  ariaLabel: PropTypes.string,
  ariaExpanded: PropTypes.bool,
  ariaControls: PropTypes.string,
  ariaPressed: PropTypes.bool,
  className: PropTypes.string,
};

Button.displayName = 'Button';
```

#### Accessible Modal Component
```jsx
// components/Modal/Modal.jsx
import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { FocusTrap } from '../../utils/keyboard-navigation';
import './Modal.css';

/**
 * Accessible modal dialog
 * 
 * Features:
 * - Focus trap
 * - Escape key to close
 * - Return focus on close
 * - ARIA attributes
 */
export const Modal = ({
  isOpen,
  onClose,
  title,
  description,
  children,
  size = 'medium',
  closeOnOverlayClick = true,
  showCloseButton = true,
  footer = null,
}) => {
  const modalRef = useRef(null);
  const previousFocusRef = useRef(null);
  const focusTrapRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      // Store previous focus
      previousFocusRef.current = document.activeElement;
      
      // Prevent body scroll
      document.body.classList.add('modal-open');
      
      // Initialize focus trap
      if (modalRef.current) {
        focusTrapRef.current = new FocusTrap(modalRef.current);
        focusTrapRef.current.activate();
      }
      
      // Focus the modal
      modalRef.current?.focus();
    } else {
      document.body.classList.remove('modal-open');
      focusTrapRef.current?.deactivate();
      
      // Return focus
      previousFocusRef.current?.focus();
    }

    return () => {
      document.body.classList.remove('modal-open');
      focusTrapRef.current?.deactivate();
    };
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const handleOverlayClick = (event) => {
    if (closeOnOverlayClick && event.target === event.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return createPortal(
    <div 
      className="modal-overlay" 
      onClick={handleOverlayClick}
      role="presentation"
    >
      <div
        ref={modalRef}
        className={`modal modal--${size}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        aria-describedby={description ? 'modal-description' : undefined}
        tabIndex={-1}
      >
        <header className="modal__header">
          <h2 id="modal-title" className="modal__title">
            {title}
          </h2>
          {showCloseButton && (
            <button
              type="button"
              className="modal__close"
              onClick={onClose}
              aria-label="Close dialog"
            >
              <CloseIcon aria-hidden="true" />
            </button>
          )}
        </header>
        
        {description && (
          <p id="modal-description" className="modal__description">
            {description}
          </p>
        )}
        
        <div className="modal__content">
          {children}
        </div>
        
        {footer && (
          <footer className="modal__footer">
            {footer}
          </footer>
        )}
      </div>
    </div>,
    document.body
  );
};
```

### 6.2 CSS Framework Updates

#### Accessibility Utilities
```css
/* styles/utilities/accessibility.css */

/* Screen reader only */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.sr-only-focusable:focus {
  position: static;
  width: auto;
  height: auto;
  padding: inherit;
  margin: inherit;
  overflow: visible;
  clip: auto;
  white-space: normal;
}

/* Skip link */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-primary-900);
  color: white;
  padding: 8px 16px;
  z-index: 10000;
  text-decoration: none;
  border-radius: 0 0 4px 0;
  transition: top 0.2s;
}

.skip-link:focus {
  top: 0;
}

/* Focus styles */
.focus-ring:focus-visible {
  outline: 3px solid var(--color-primary-600);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(49, 130, 206, 0.3);
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .btn {
    border: 2px solid currentColor;
  }
  
  :focus-visible {
    outline: 4px solid CanvasText;
    outline-offset: 2px;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-primary: #1a202c;
    --color-bg-secondary: #2d3748;
    --color-text-primary: #f7fafc;
    --color-text-secondary: #e2e8f0;
  }
}

/* Print styles */
@media print {
  .no-print {
    display: none !important;
  }
  
  a[href]::after {
    content: " (" attr(href) ")";
  }
}
```

---

## 7. Implementation Priority Order

### Phase 1: Critical (Weeks 1-2)
| Priority | Item | Impact | Effort |
|----------|------|--------|--------|
| P0 | Fix color contrast issues | High | Low |
| P0 | Add missing alt text | High | Low |
| P0 | Implement focus indicators | High | Low |
| P0 | Add form labels | High | Medium |
| P0 | Fix keyboard navigation | High | Medium |

### Phase 2: High Priority (Weeks 3-4)
| Priority | Item | Impact | Effort |
|----------|------|--------|--------|
| P1 | Add ARIA landmarks | High | Medium |
| P1 | Implement skip links | High | Low |
| P1 | Add error messaging | High | Medium |
| P1 | Chart accessibility | High | High |
| P1 | Modal focus traps | High | Medium |

### Phase 3: Medium Priority (Weeks 5-6)
| Priority | Item | Impact | Effort |
|----------|------|--------|--------|
| P2 | Screen reader testing | High | Medium |
| P2 | Automated testing setup | Medium | Medium |
| P2 | Documentation | Medium | Medium |
| P2 | Training materials | Medium | High |

### Phase 4: Enhancement (Weeks 7-8)
| Priority | Item | Impact | Effort |
|----------|------|--------|--------|
| P3 | Advanced ARIA patterns | Medium | High |
| P3 | User testing | High | High |
| P3 | VPAT documentation | Medium | Medium |
| P3 | Accessibility statement | Low | Low |

---

## 8. Quick Reference

### Common Patterns
```html
<!-- Skip Link -->
<a href="#main" class="skip-link">Skip to main content</a>

<!-- Button with Icon -->
<button aria-label="Close">
  <svg aria-hidden="true">...</svg>
</button>

<!-- Form Input -->
<label for="email">Email <span aria-label="required">*</span></label>
<input id="email" type="email" required aria-describedby="email-error">
<span id="email-error" role="alert"></span>

<!-- Live Region -->
<div aria-live="polite" aria-atomic="true" class="sr-only"></div>

<!-- Status Message -->
<div role="status">Saved successfully</div>
```

### Contrast Quick Check
```
Minimum Ratios:
- Normal text: 4.5:1
- Large text: 3:1
- UI components: 3:1

Tools:
- WebAIM Contrast Checker
- Chrome DevTools (hover color in styles)
- axe DevTools
```

### Keyboard Shortcuts Reference
```
Tab         - Move to next focusable element
Shift+Tab   - Move to previous focusable element
Enter       - Activate button/link
Space       - Activate button/checkbox
Arrow keys  - Navigate within widgets
Escape      - Close modals/menus
Home/End    - Go to start/end of list
```

---

## Appendix A: Resources

### Tools
- [axe DevTools](https://www.deque.com/axe/)
- [WAVE](https://wave.webaim.org/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [NVDA Screen Reader](https://www.nvaccess.org/)

### Documentation
- [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

### Training
- [WebAIM Training](https://webaim.org/training/)
- [Deque University](https://dequeuniversity.com/)
- [W3C WAI Tutorials](https://www.w3.org/WAI/tutorials/)

---

*Document Version: 1.0*
*Last Updated: [Date]*
*Next Review: [Date + 6 months]*
