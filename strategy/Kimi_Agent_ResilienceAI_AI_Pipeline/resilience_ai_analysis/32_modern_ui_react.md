# ResilienceAI Modern React UI Design

## Executive Summary

This document provides a comprehensive design for a modern React-based UI for ResilienceAI, offering a flexible and feature-rich alternative to the existing Streamlit dashboard. The design emphasizes enterprise-grade architecture, real-time capabilities, and exceptional user experience.

---

## 1. Project Architecture Overview

### 1.1 Technology Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    RESILIENCEAI REACT UI                        │
├─────────────────────────────────────────────────────────────────┤
│  Frontend Layer                                                 │
│  ├── React 18+ with TypeScript                                  │
│  ├── Vite (Build Tool)                                          │
│  ├── Material-UI v5 (MUI) + Tailwind CSS                        │
│  ├── React Query (Server State)                                 │
│  ├── Zustand (Client State)                                     │
│  ├── React Router v6 (Navigation)                               │
│  ├── Recharts + D3.js (Charts)                                  │
│  ├── React Hook Form + Zod (Forms)                              │
│  └── Socket.io-client (Real-time)                               │
├─────────────────────────────────────────────────────────────────┤
│  API Integration Layer                                          │
│  ├── Axios (HTTP Client)                                        │
│  ├── React Query (Caching/Refetching)                           │
│  └── WebSocket Manager                                          │
├─────────────────────────────────────────────────────────────────┤
│  Backend Integration                                            │
│  └── Existing FastAPI/Streamlit Backend                         │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Project Structure

```
resilience-ai-ui/
├── public/
│   ├── favicon.ico
│   ├── logo.svg
│   └── manifest.json
├── src/
│   ├── api/                          # API clients and configurations
│   │   ├── axios.config.ts
│   │   ├── auth.api.ts
│   │   ├── dashboard.api.ts
│   │   ├── incidents.api.ts
│   │   ├── analytics.api.ts
│   │   └── websocket.ts
│   │
│   ├── components/                   # Reusable UI components
│   │   ├── common/                   # Shared components
│   │   │   ├── Button/
│   │   │   ├── Card/
│   │   │   ├── DataTable/
│   │   │   ├── Modal/
│   │   │   ├── Loading/
│   │   │   ├── ErrorBoundary/
│   │   │   └── index.ts
│   │   │
│   │   ├── layout/                   # Layout components
│   │   │   ├── MainLayout/
│   │   │   ├── Sidebar/
│   │   │   ├── Header/
│   │   │   ├── Footer/
│   │   │   └── index.ts
│   │   │
│   │   ├── charts/                   # Chart components
│   │   │   ├── LineChart/
│   │   │   ├── BarChart/
│   │   │   ├── PieChart/
│   │   │   ├── Heatmap/
│   │   │   ├── Gauge/
│   │   │   └── index.ts
│   │   │
│   │   └── forms/                    # Form components
│   │       ├── FormInput/
│   │       ├── FormSelect/
│   │       ├── FormDatePicker/
│   │       └── index.ts
│   │
│   ├── features/                     # Feature-based modules
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── stores/
│   │   │   └── types.ts
│   │   │
│   │   ├── dashboard/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── stores/
│   │   │   └── types.ts
│   │   │
│   │   ├── incidents/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── stores/
│   │   │   └── types.ts
│   │   │
│   │   ├── analytics/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── stores/
│   │   │   └── types.ts
│   │   │
│   │   └── settings/
│   │       ├── components/
│   │       ├── hooks/
│   │       ├── stores/
│   │       └── types.ts
│   │
│   ├── hooks/                        # Global custom hooks
│   │   ├── useAuth.ts
│   │   ├── useWebSocket.ts
│   │   ├── useTheme.ts
│   │   └── useLocalStorage.ts
│   │
│   ├── stores/                       # Global state stores
│   │   ├── auth.store.ts
│   │   ├── theme.store.ts
│   │   └── notification.store.ts
│   │
│   ├── types/                        # Global TypeScript types
│   │   ├── api.types.ts
│   │   ├── auth.types.ts
│   │   ├── dashboard.types.ts
│   │   ├── incident.types.ts
│   │   └── index.ts
│   │
│   ├── utils/                        # Utility functions
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── constants.ts
│   │   └── helpers.ts
│   │
│   ├── theme/                        # MUI theme configuration
│   │   ├── palette.ts
│   │   ├── typography.ts
│   │   ├── components.ts
│   │   └── index.ts
│   │
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── .env
├── .env.example
├── .eslintrc.js
├── .prettierrc
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── package.json
```

---

## 2. TypeScript Type Definitions

### 2.1 Core Types (`src/types/index.ts`)

```typescript
// ============================================
// BASE TYPES
// ============================================

export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, string[]>;
  timestamp: string;
}

// ============================================
// AUTHENTICATION TYPES
// ============================================

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  avatar?: string;
  department?: string;
  lastLoginAt?: string;
  createdAt: string;
  updatedAt: string;
}

export type UserRole = 'admin' | 'analyst' | 'viewer' | 'operator';

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  department?: string;
}

// ============================================
// DASHBOARD TYPES
// ============================================

export interface DashboardMetrics {
  totalIncidents: number;
  activeIncidents: number;
  resolvedIncidents: number;
  avgResolutionTime: number;
  systemHealth: SystemHealth;
  alerts: Alert[];
  recentActivity: Activity[];
}

export interface SystemHealth {
  status: 'healthy' | 'warning' | 'critical';
  score: number;
  components: HealthComponent[];
  lastChecked: string;
}

export interface HealthComponent {
  name: string;
  status: 'healthy' | 'warning' | 'critical';
  uptime: number;
  latency: number;
}

export interface Alert {
  id: string;
  severity: AlertSeverity;
  title: string;
  message: string;
  source: string;
  timestamp: string;
  acknowledged: boolean;
  acknowledgedBy?: string;
}

export type AlertSeverity = 'info' | 'warning' | 'critical' | 'emergency';

export interface Activity {
  id: string;
  type: ActivityType;
  description: string;
  user?: User;
  metadata?: Record<string, unknown>;
  timestamp: string;
}

export type ActivityType = 
  | 'incident_created'
  | 'incident_updated'
  | 'incident_resolved'
  | 'alert_triggered'
  | 'user_login'
  | 'system_event';

// ============================================
// INCIDENT TYPES
// ============================================

export interface Incident {
  id: string;
  title: string;
  description: string;
  status: IncidentStatus;
  severity: IncidentSeverity;
  category: IncidentCategory;
  priority: IncidentPriority;
  assignee?: User;
  reporter: User;
  tags: string[];
  affectedSystems: string[];
  timeline: IncidentEvent[];
  comments: Comment[];
  attachments: Attachment[];
  createdAt: string;
  updatedAt: string;
  resolvedAt?: string;
  slaDeadline?: string;
}

export type IncidentStatus = 
  | 'open'
  | 'in_progress'
  | 'pending'
  | 'resolved'
  | 'closed'
  | 'reopened';

export type IncidentSeverity = 'low' | 'medium' | 'high' | 'critical';
export type IncidentPriority = 'p1' | 'p2' | 'p3' | 'p4';
export type IncidentCategory = 
  | 'security'
  | 'performance'
  | 'availability'
  | 'data'
  | 'infrastructure'
  | 'other';

export interface IncidentEvent {
  id: string;
  type: string;
  description: string;
  user?: User;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

export interface Comment {
  id: string;
  content: string;
  author: User;
  isInternal: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Attachment {
  id: string;
  filename: string;
  url: string;
  size: number;
  mimeType: string;
  uploadedBy: User;
  uploadedAt: string;
}

export interface IncidentFilter {
  status?: IncidentStatus[];
  severity?: IncidentSeverity[];
  category?: IncidentCategory[];
  assignee?: string;
  dateRange?: DateRange;
  search?: string;
  tags?: string[];
}

export interface DateRange {
  start: string;
  end: string;
}

// ============================================
// ANALYTICS TYPES
// ============================================

export interface TimeSeriesData {
  timestamp: string;
  value: number;
  label?: string;
}

export interface MetricSeries {
  name: string;
  data: TimeSeriesData[];
  color?: string;
  unit?: string;
}

export interface ChartData {
  labels: string[];
  datasets: MetricSeries[];
}

export interface AnalyticsDashboard {
  incidentTrends: MetricSeries[];
  resolutionMetrics: ResolutionMetrics;
  teamPerformance: TeamPerformance[];
  systemMetrics: SystemMetric[];
  customReports: CustomReport[];
}

export interface ResolutionMetrics {
  avgResolutionTime: number;
  medianResolutionTime: number;
  slaComplianceRate: number;
  firstResponseTime: number;
  timeBySeverity: Record<IncidentSeverity, number>;
  timeByCategory: Record<IncidentCategory, number>;
}

export interface TeamPerformance {
  userId: string;
  userName: string;
  incidentsResolved: number;
  avgResolutionTime: number;
  satisfactionScore: number;
}

export interface SystemMetric {
  name: string;
  current: number;
  target: number;
  trend: 'up' | 'down' | 'stable';
  changePercent: number;
}

export interface CustomReport {
  id: string;
  name: string;
  description: string;
  filters: ReportFilter;
  schedule?: ReportSchedule;
  lastRun?: string;
  createdBy: User;
  createdAt: string;
}

export interface ReportFilter {
  dateRange: DateRange;
  metrics: string[];
  groupBy?: string;
  filters?: Record<string, unknown>;
}

export interface ReportSchedule {
  frequency: 'daily' | 'weekly' | 'monthly';
  dayOfWeek?: number;
  dayOfMonth?: number;
  time: string;
  recipients: string[];
}

// ============================================
// NOTIFICATION TYPES
// ============================================

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  data?: Record<string, unknown>;
  read: boolean;
  createdAt: string;
}

export type NotificationType = 
  | 'incident_assigned'
  | 'incident_updated'
  | 'alert_triggered'
  | 'mention'
  | 'system'
  | 'report_ready';

// ============================================
// WEBSOCKET TYPES
// ============================================

export interface WebSocketMessage<T = unknown> {
  type: WebSocketEventType;
  payload: T;
  timestamp: string;
}

export type WebSocketEventType =
  | 'incident.created'
  | 'incident.updated'
  | 'incident.resolved'
  | 'alert.new'
  | 'alert.acknowledged'
  | 'system.health'
  | 'user.activity'
  | 'notification.new';

export interface WebSocketConfig {
  url: string;
  reconnectInterval: number;
  maxReconnectAttempts: number;
  heartbeatInterval: number;
}
```

---

## 3. Component Architecture

### 3.1 Component Hierarchy Diagram

```
App
├── AuthProvider
│   └── Routes
│       ├── PublicRoutes
│       │   ├── LoginPage
│       │   ├── RegisterPage
│       │   └── ForgotPasswordPage
│       │
│       └── ProtectedRoutes
│           └── MainLayout
│               ├── Header
│               │   ├── Logo
│               │   ├── GlobalSearch
│               │   ├── NotificationBell
│               │   └── UserMenu
│               │
│               ├── Sidebar
│               │   ├── Navigation
│               │   └── QuickActions
│               │
│               └── MainContent
│                   ├── DashboardPage
│                   │   ├── KPIStats
│                   │   ├── IncidentOverview
│                   │   ├── SystemHealth
│                   │   ├── RecentAlerts
│                   │   └── ActivityFeed
│                   │
│                   ├── IncidentsPage
│                   │   ├── FilterPanel
│                   │   ├── IncidentTable
│                   │   ├── IncidentDetail
│                   │   └── IncidentForm
│                   │
│                   ├── AnalyticsPage
│                   │   ├── DateRangePicker
│                   │   ├── MetricCards
│                   │   ├── TrendCharts
│                   │   └── CustomReports
│                   │
│                   └── SettingsPage
│                       ├── ProfileSettings
│                       ├── NotificationSettings
│                       └── SystemSettings
```

### 3.2 Key Component Implementations

#### MainLayout Component (`src/components/layout/MainLayout/MainLayout.tsx`)

```typescript
import React, { useState } from 'react';
import { Box, CssBaseline, useMediaQuery, useTheme } from '@mui/material';
import { Outlet } from 'react-router-dom';
import { Header } from '../Header';
import { Sidebar } from '../Sidebar';
import { useAuthStore } from '@/stores/auth.store';

const SIDEBAR_WIDTH = 280;
const SIDEBAR_COLLAPSED_WIDTH = 72;

export const MainLayout: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { user } = useAuthStore();
  
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleSidebarToggle = () => {
    if (isMobile) {
      setSidebarOpen(!sidebarOpen);
    } else {
      setSidebarCollapsed(!sidebarCollapsed);
    }
  };

  const currentSidebarWidth = sidebarCollapsed 
    ? SIDEBAR_COLLAPSED_WIDTH 
    : SIDEBAR_WIDTH;

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <CssBaseline />
      
      {/* Header */}
      <Header 
        onMenuToggle={handleSidebarToggle}
        sidebarWidth={currentSidebarWidth}
        user={user}
      />
      
      {/* Sidebar */}
      <Sidebar
        open={sidebarOpen}
        collapsed={sidebarCollapsed}
        width={SIDEBAR_WIDTH}
        collapsedWidth={SIDEBAR_COLLAPSED_WIDTH}
        onClose={() => setSidebarOpen(false)}
        userRole={user?.role}
      />
      
      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          ml: isMobile ? 0 : `${currentSidebarWidth}px`,
          transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          minHeight: 'calc(100vh - 64px)',
          backgroundColor: theme.palette.background.default,
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
};
```

#### Sidebar Component (`src/components/layout/Sidebar/Sidebar.tsx`)

```typescript
import React from 'react';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Divider,
  Typography,
  IconButton,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Warning as IncidentIcon,
  Assessment as AnalyticsIcon,
  Settings as SettingsIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { UserRole } from '@/types';

interface SidebarProps {
  open: boolean;
  collapsed: boolean;
  width: number;
  collapsedWidth: number;
  onClose: () => void;
  userRole?: UserRole;
}

interface NavItem {
  label: string;
  icon: React.ReactNode;
  path: string;
  roles: UserRole[];
  badge?: number;
}

const navItems: NavItem[] = [
  {
    label: 'Dashboard',
    icon: <DashboardIcon />,
    path: '/dashboard',
    roles: ['admin', 'analyst', 'viewer', 'operator'],
  },
  {
    label: 'Incidents',
    icon: <IncidentIcon />,
    path: '/incidents',
    roles: ['admin', 'analyst', 'operator'],
    badge: 0,
  },
  {
    label: 'Analytics',
    icon: <AnalyticsIcon />,
    path: '/analytics',
    roles: ['admin', 'analyst'],
  },
  {
    label: 'Settings',
    icon: <SettingsIcon />,
    path: '/settings',
    roles: ['admin', 'analyst', 'viewer', 'operator'],
  },
];

export const Sidebar: React.FC<SidebarProps> = ({
  open,
  collapsed,
  width,
  collapsedWidth,
  onClose,
  userRole = 'viewer',
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const filteredNavItems = navItems.filter(item =>
    item.roles.includes(userRole)
  );

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      onClose();
    }
  };

  const isActive = (path: string) => location.pathname.startsWith(path);

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo Area */}
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'space-between',
          height: 64,
        }}
      >
        {!collapsed && (
          <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main' }}>
            ResilienceAI
          </Typography>
        )}
        {collapsed && (
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: 1,
              bgcolor: 'primary.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontWeight: 700,
            }}
          >
            R
          </Box>
        )}
      </Box>

      <Divider />

      {/* Navigation */}
      <List sx={{ flexGrow: 1, py: 1 }}>
        {filteredNavItems.map((item) => (
          <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
            {collapsed ? (
              <Tooltip title={item.label} placement="right">
                <ListItemButton
                  onClick={() => handleNavigation(item.path)}
                  selected={isActive(item.path)}
                  sx={{
                    minHeight: 48,
                    justifyContent: 'center',
                    px: 2.5,
                    borderRadius: 1,
                    mx: 1,
                    '&.Mui-selected': {
                      bgcolor: 'primary.light',
                      color: 'primary.main',
                      '&:hover': { bgcolor: 'primary.light' },
                    },
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: 0,
                      justifyContent: 'center',
                      color: isActive(item.path) ? 'primary.main' : 'inherit',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                </ListItemButton>
              </Tooltip>
            ) : (
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                selected={isActive(item.path)}
                sx={{
                  minHeight: 48,
                  px: 2.5,
                  borderRadius: 1,
                  mx: 1,
                  '&.Mui-selected': {
                    bgcolor: 'primary.light',
                    color: 'primary.main',
                    '&:hover': { bgcolor: 'primary.light' },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: isActive(item.path) ? 'primary.main' : 'inherit',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{
                    fontSize: 14,
                    fontWeight: isActive(item.path) ? 600 : 400,
                  }}
                />
              </ListItemButton>
            )}
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Drawer
      variant={isMobile ? 'temporary' : 'permanent'}
      open={isMobile ? open : true}
      onClose={onClose}
      ModalProps={{ keepMounted: true }}
      sx={{
        width: collapsed ? collapsedWidth : width,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: collapsed ? collapsedWidth : width,
          boxSizing: 'border-box',
          borderRight: '1px solid',
          borderColor: 'divider',
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};
```

---

## 4. State Management with Zustand

### 4.1 Auth Store (`src/stores/auth.store.ts`)

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, AuthTokens, LoginCredentials } from '@/types';
import { authApi } from '@/api/auth.api';

interface AuthState {
  // State
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  updateUser: (user: Partial<User>) => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial State
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.login(credentials);
          set({
            user: response.data.user,
            tokens: response.data.tokens,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Login failed',
            isLoading: false,
            isAuthenticated: false,
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          await authApi.logout();
        } finally {
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
            error: null,
          });
        }
      },

      refreshToken: async () => {
        const { tokens } = get();
        if (!tokens?.refreshToken) return;

        try {
          const response = await authApi.refreshToken(tokens.refreshToken);
          set({
            tokens: response.data,
          });
        } catch (error) {
          // Token refresh failed, logout user
          get().logout();
        }
      },

      updateUser: (userData) => {
        const { user } = get();
        if (user) {
          set({ user: { ...user, ...userData } });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

### 4.2 Dashboard Store (`src/features/dashboard/stores/dashboard.store.ts`)

```typescript
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { DashboardMetrics, Alert, Activity } from '@/types';
import { dashboardApi } from '@/api/dashboard.api';

interface DashboardState {
  // State
  metrics: DashboardMetrics | null;
  alerts: Alert[];
  activities: Activity[];
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
  autoRefresh: boolean;
  refreshInterval: number;

  // Actions
  fetchDashboardData: () => Promise<void>;
  fetchAlerts: () => Promise<void>;
  acknowledgeAlert: (alertId: string) => Promise<void>;
  setAutoRefresh: (enabled: boolean) => void;
  setRefreshInterval: (interval: number) => void;
  clearError: () => void;
}

export const useDashboardStore = create<DashboardState>()(
  devtools(
    (set, get) => ({
      // Initial State
      metrics: null,
      alerts: [],
      activities: [],
      isLoading: false,
      error: null,
      lastUpdated: null,
      autoRefresh: true,
      refreshInterval: 30000, // 30 seconds

      // Actions
      fetchDashboardData: async () => {
        set({ isLoading: true, error: null });
        try {
          const [metricsRes, alertsRes, activitiesRes] = await Promise.all([
            dashboardApi.getMetrics(),
            dashboardApi.getAlerts(),
            dashboardApi.getRecentActivity(),
          ]);

          set({
            metrics: metricsRes.data,
            alerts: alertsRes.data,
            activities: activitiesRes.data,
            lastUpdated: new Date().toISOString(),
            isLoading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to fetch dashboard data',
            isLoading: false,
          });
        }
      },

      fetchAlerts: async () => {
        try {
          const response = await dashboardApi.getAlerts();
          set({ alerts: response.data });
        } catch (error) {
          console.error('Failed to fetch alerts:', error);
        }
      },

      acknowledgeAlert: async (alertId) => {
        try {
          await dashboardApi.acknowledgeAlert(alertId);
          const { alerts } = get();
          set({
            alerts: alerts.map((alert) =>
              alert.id === alertId ? { ...alert, acknowledged: true } : alert
            ),
          });
        } catch (error) {
          console.error('Failed to acknowledge alert:', error);
        }
      },

      setAutoRefresh: (enabled) => set({ autoRefresh: enabled }),
      setRefreshInterval: (interval) => set({ refreshInterval: interval }),
      clearError: () => set({ error: null }),
    }),
    { name: 'dashboard-store' }
  )
);
```

### 4.3 Notification Store (`src/stores/notification.store.ts`)

```typescript
import { create } from 'zustand';
import { Notification } from '@/types';

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  
  addNotification: (notification: Notification) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string) => void;
  clearAll: () => void;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  unreadCount: 0,

  addNotification: (notification) => {
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadCount: state.unreadCount + 1,
    }));
  },

  markAsRead: (id) => {
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    }));
  },

  markAllAsRead: () => {
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true })),
      unreadCount: 0,
    }));
  },

  removeNotification: (id) => {
    const { notifications } = get();
    const notification = notifications.find((n) => n.id === id);
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
      unreadCount: notification?.read
        ? state.unreadCount
        : Math.max(0, state.unreadCount - 1),
    }));
  },

  clearAll: () => set({ notifications: [], unreadCount: 0 }),
}));
```

---

## 5. API Client Integration

### 5.1 Axios Configuration (`src/api/axios.config.ts`)

```typescript
import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/stores/auth.store';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { tokens } = useAuthStore.getState();
    
    if (tokens?.accessToken) {
      config.headers.Authorization = `Bearer ${tokens.accessToken}`;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const { refreshToken } = useAuthStore.getState();
        await refreshToken();
        
        const { tokens } = useAuthStore.getState();
        if (tokens?.accessToken) {
          originalRequest.headers.Authorization = `Bearer ${tokens.accessToken}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        const { logout } = useAuthStore.getState();
        await logout();
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Error handler
export const handleApiError = (error: unknown): Error => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ message: string; details?: Record<string, string[]> }>;
    const message = axiosError.response?.data?.message || axiosError.message;
    return new Error(message);
  }
  return error instanceof Error ? error : new Error('Unknown error occurred');
};
```

### 5.2 React Query Hooks (`src/features/dashboard/hooks/useDashboard.ts`)

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { dashboardApi } from '@/api/dashboard.api';
import { DashboardMetrics, Alert } from '@/types';

const DASHBOARD_KEYS = {
  all: ['dashboard'] as const,
  metrics: () => [...DASHBOARD_KEYS.all, 'metrics'] as const,
  alerts: () => [...DASHBOARD_KEYS.all, 'alerts'] as const,
  activities: () => [...DASHBOARD_KEYS.all, 'activities'] as const,
};

// Hook for fetching dashboard metrics
export const useDashboardMetrics = (options?: { refetchInterval?: number }) => {
  return useQuery<DashboardMetrics, Error>({
    queryKey: DASHBOARD_KEYS.metrics(),
    queryFn: async () => {
      const response = await dashboardApi.getMetrics();
      return response.data;
    },
    refetchInterval: options?.refetchInterval || 30000,
    staleTime: 10000,
  });
};

// Hook for fetching alerts
export const useAlerts = () => {
  return useQuery<Alert[], Error>({
    queryKey: DASHBOARD_KEYS.alerts(),
    queryFn: async () => {
      const response = await dashboardApi.getAlerts();
      return response.data;
    },
    refetchInterval: 15000,
  });
};

// Hook for acknowledging alerts
export const useAcknowledgeAlert = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: dashboardApi.acknowledgeAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: DASHBOARD_KEYS.alerts() });
    },
  });
};
```

### 5.3 Dashboard API (`src/api/dashboard.api.ts`)

```typescript
import { apiClient } from './axios.config';
import { ApiResponse, DashboardMetrics, Alert, Activity } from '@/types';

export const dashboardApi = {
  // Metrics
  getMetrics: async (): Promise<ApiResponse<DashboardMetrics>> => {
    const response = await apiClient.get<ApiResponse<DashboardMetrics>>('/dashboard/metrics');
    return response.data;
  },

  // Alerts
  getAlerts: async (params?: { acknowledged?: boolean }): Promise<ApiResponse<Alert[]>> => {
    const response = await apiClient.get<ApiResponse<Alert[]>>('/dashboard/alerts', { params });
    return response.data;
  },

  acknowledgeAlert: async (alertId: string): Promise<ApiResponse<void>> => {
    const response = await apiClient.post<ApiResponse<void>>(`/dashboard/alerts/${alertId}/acknowledge`);
    return response.data;
  },

  // Activity
  getRecentActivity: async (limit = 20): Promise<ApiResponse<Activity[]>> => {
    const response = await apiClient.get<ApiResponse<Activity[]>>('/dashboard/activity', {
      params: { limit },
    });
    return response.data;
  },

  // System Health
  getSystemHealth: async (): Promise<ApiResponse<SystemHealth>> => {
    const response = await apiClient.get<ApiResponse<SystemHealth>>('/dashboard/health');
    return response.data;
  },
};
```

---

## 6. Real-Time Updates with WebSockets

### 6.1 WebSocket Manager (`src/api/websocket.ts`)

```typescript
import { io, Socket } from 'socket.io-client';
import { useAuthStore } from '@/stores/auth.store';
import { useNotificationStore } from '@/stores/notification.store';
import { useDashboardStore } from '@/features/dashboard/stores/dashboard.store';
import { WebSocketMessage, WebSocketEventType, Incident, Alert } from '@/types';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

class WebSocketManager {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 5000;
  private heartbeatInterval: NodeJS.Timeout | null = null;

  connect(): void {
    const { tokens } = useAuthStore.getState();
    
    if (!tokens?.accessToken) {
      console.warn('No access token available for WebSocket connection');
      return;
    }

    this.socket = io(WS_URL, {
      auth: { token: tokens.accessToken },
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectInterval,
    });

    this.setupEventHandlers();
    this.startHeartbeat();
  }

  private setupEventHandlers(): void {
    if (!this.socket) return;

    // Connection events
    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      this.stopHeartbeat();
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.reconnectAttempts++;
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached');
        this.disconnect();
      }
    });

    // Business events
    this.socket.on('incident.created', this.handleIncidentCreated.bind(this));
    this.socket.on('incident.updated', this.handleIncidentUpdated.bind(this));
    this.socket.on('incident.resolved', this.handleIncidentResolved.bind(this));
    this.socket.on('alert.new', this.handleNewAlert.bind(this));
    this.socket.on('system.health', this.handleSystemHealth.bind(this));
    this.socket.on('notification.new', this.handleNotification.bind(this));
  }

  private handleIncidentCreated(data: WebSocketMessage<Incident>): void {
    const { addNotification } = useNotificationStore.getState();
    
    addNotification({
      id: `incident-${data.payload.id}`,
      type: 'incident_created',
      title: 'New Incident',
      message: `Incident "${data.payload.title}" has been created`,
      data: { incidentId: data.payload.id },
      read: false,
      createdAt: data.timestamp,
    });

    // Refresh dashboard data
    const { fetchDashboardData } = useDashboardStore.getState();
    fetchDashboardData();
  }

  private handleIncidentUpdated(data: WebSocketMessage<Incident>): void {
    const { addNotification } = useNotificationStore.getState();
    
    addNotification({
      id: `incident-update-${Date.now()}`,
      type: 'incident_updated',
      title: 'Incident Updated',
      message: `Incident "${data.payload.title}" has been updated`,
      data: { incidentId: data.payload.id },
      read: false,
      createdAt: data.timestamp,
    });
  }

  private handleIncidentResolved(data: WebSocketMessage<Incident>): void {
    const { addNotification } = useNotificationStore.getState();
    
    addNotification({
      id: `incident-resolved-${data.payload.id}`,
      type: 'incident_updated',
      title: 'Incident Resolved',
      message: `Incident "${data.payload.title}" has been resolved`,
      data: { incidentId: data.payload.id },
      read: false,
      createdAt: data.timestamp,
    });
  }

  private handleNewAlert(data: WebSocketMessage<Alert>): void {
    const { addNotification } = useNotificationStore.getState();
    const { fetchAlerts } = useDashboardStore.getState();
    
    addNotification({
      id: `alert-${data.payload.id}`,
      type: 'alert_triggered',
      title: `Alert: ${data.payload.severity.toUpperCase()}`,
      message: data.payload.message,
      data: { alertId: data.payload.id },
      read: false,
      createdAt: data.timestamp,
    });

    fetchAlerts();
  }

  private handleSystemHealth(data: WebSocketMessage): void {
    const { metrics } = useDashboardStore.getState();
    if (metrics) {
      useDashboardStore.setState({
        metrics: {
          ...metrics,
          systemHealth: data.payload,
        },
      });
    }
  }

  private handleNotification(data: WebSocketMessage): void {
    const { addNotification } = useNotificationStore.getState();
    addNotification(data.payload);
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      this.socket?.emit('ping');
    }, 30000);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  disconnect(): void {
    this.stopHeartbeat();
    this.socket?.disconnect();
    this.socket = null;
  }

  // Subscribe to specific channels
  subscribe(channel: string, callback: (data: unknown) => void): void {
    this.socket?.on(channel, callback);
  }

  unsubscribe(channel: string, callback?: (data: unknown) => void): void {
    if (callback) {
      this.socket?.off(channel, callback);
    } else {
      this.socket?.off(channel);
    }
  }

  // Emit events
  emit(event: string, data?: unknown): void {
    this.socket?.emit(event, data);
  }
}

export const wsManager = new WebSocketManager();

// React hook for WebSocket
export const useWebSocket = () => {
  return {
    connect: () => wsManager.connect(),
    disconnect: () => wsManager.disconnect(),
    subscribe: wsManager.subscribe.bind(wsManager),
    unsubscribe: wsManager.unsubscribe.bind(wsManager),
    emit: wsManager.emit.bind(wsManager),
  };
};
```

---

## 7. Chart Component Integration

### 7.1 Chart Components with Recharts

```typescript
// src/components/charts/LineChart/LineChart.tsx
import React from 'react';
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';
import { Box, Typography, useTheme } from '@mui/material';
import { MetricSeries } from '@/types';

interface LineChartProps {
  title: string;
  data: MetricSeries[];
  height?: number;
  showArea?: boolean;
  yAxisUnit?: string;
}

export const LineChart: React.FC<LineChartProps> = ({
  title,
  data,
  height = 300,
  showArea = false,
  yAxisUnit = '',
}) => {
  const theme = useTheme();

  // Transform data for Recharts
  const chartData = React.useMemo(() => {
    if (!data.length) return [];
    
    const timestamps = data[0].data.map((d) => d.timestamp);
    return timestamps.map((timestamp, index) => {
      const point: Record<string, string | number> = {
        timestamp: new Date(timestamp).toLocaleDateString(),
      };
      
      data.forEach((series) => {
        point[series.name] = series.data[index]?.value || 0;
      });
      
      return point;
    });
  }, [data]);

  const colors = [
    theme.palette.primary.main,
    theme.palette.secondary.main,
    theme.palette.success.main,
    theme.palette.warning.main,
    theme.palette.error.main,
  ];

  const ChartComponent = showArea ? AreaChart : RechartsLineChart;

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        {title}
      </Typography>
      <ResponsiveContainer width="100%" height={height}>
        <ChartComponent data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
          <XAxis
            dataKey="timestamp"
            tick={{ fontSize: 12 }}
            stroke={theme.palette.text.secondary}
          />
          <YAxis
            tick={{ fontSize: 12 }}
            stroke={theme.palette.text.secondary}
            tickFormatter={(value) => `${value}${yAxisUnit}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: theme.palette.background.paper,
              border: `1px solid ${theme.palette.divider}`,
              borderRadius: 8,
            }}
            formatter={(value: number) => [`${value}${yAxisUnit}`, '']}
          />
          <Legend />
          {data.map((series, index) =>
            showArea ? (
              <Area
                key={series.name}
                type="monotone"
                dataKey={series.name}
                stroke={colors[index % colors.length]}
                fill={colors[index % colors.length]}
                fillOpacity={0.3}
                strokeWidth={2}
              />
            ) : (
              <Line
                key={series.name}
                type="monotone"
                dataKey={series.name}
                stroke={colors[index % colors.length]}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 6 }}
              />
            )
          )}
        </ChartComponent>
      </ResponsiveContainer>
    </Box>
  );
};
```

```typescript
// src/components/charts/Gauge/Gauge.tsx
import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';

interface GaugeProps {
  value: number;
  max: number;
  title: string;
  size?: number;
  thresholds?: { value: number; color: string }[];
}

export const Gauge: React.FC<GaugeProps> = ({
  value,
  max,
  title,
  size = 200,
  thresholds = [
    { value: 0.3, color: '#4caf50' },
    { value: 0.7, color: '#ff9800' },
    { value: 1, color: '#f44336' },
  ],
}) => {
  const theme = useTheme();
  const percentage = Math.min((value / max) * 100, 100);
  
  const getColor = () => {
    const ratio = value / max;
    for (const threshold of thresholds) {
      if (ratio <= threshold.value) return threshold.color;
    }
    return thresholds[thresholds.length - 1].color;
  };

  const strokeWidth = size * 0.1;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (percentage / 100) * circumference * 0.75;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        {title}
      </Typography>
      <Box sx={{ position: 'relative', width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          {/* Background arc */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={theme.palette.divider}
            strokeWidth={strokeWidth}
            strokeDasharray={`${circumference * 0.75} ${circumference}`}
            strokeLinecap="round"
            transform={`rotate(135 ${size / 2} ${size / 2})`}
          />
          {/* Value arc */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={getColor()}
            strokeWidth={strokeWidth}
            strokeDasharray={`${circumference * 0.75} ${circumference}`}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            transform={`rotate(135 ${size / 2} ${size / 2})`}
            style={{
              transition: 'stroke-dashoffset 0.5s ease-in-out',
            }}
          />
        </svg>
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            textAlign: 'center',
          }}
        >
          <Typography variant="h4" sx={{ fontWeight: 700, color: getColor() }}>
            {Math.round(percentage)}%
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {value} / {max}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};
```

---

## 8. Authentication Flows

### 8.1 Login Page (`src/features/auth/components/LoginPage/LoginPage.tsx`)

```typescript
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, Link } from 'react-router-dom';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Checkbox,
  FormControlLabel,
  Alert,
  InputAdornment,
  IconButton,
  useTheme,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email as EmailIcon,
  Lock as LockIcon,
} from '@mui/icons-material';
import { useAuthStore } from '@/stores/auth.store';
import { LoginCredentials } from '@/types';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  rememberMe: z.boolean().default(false),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const { login, isLoading, error, clearError } = useAuthStore();
  const [showPassword, setShowPassword] = React.useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      rememberMe: false,
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      clearError();
      await login(data);
      navigate('/dashboard');
    } catch {
      // Error is handled by the store
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        p: 2,
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          width: '100%',
          maxWidth: 420,
          borderRadius: 2,
        }}
      >
        {/* Logo */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Box
            sx={{
              width: 64,
              height: 64,
              bgcolor: 'primary.main',
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mx: 'auto',
              mb: 2,
            }}
          >
            <Typography variant="h4" sx={{ color: 'white', fontWeight: 700 }}>
              R
            </Typography>
          </Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
            Welcome Back
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Sign in to access your ResilienceAI dashboard
          </Typography>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={clearError}>
            {error}
          </Alert>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit(onSubmit)}>
          <TextField
            fullWidth
            label="Email"
            margin="normal"
            {...register('email')}
            error={!!errors.email}
            helperText={errors.email?.message}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <EmailIcon color="action" />
                </InputAdornment>
              ),
            }}
          />

          <TextField
            fullWidth
            label="Password"
            type={showPassword ? 'text' : 'password'}
            margin="normal"
            {...register('password')}
            error={!!errors.password}
            helperText={errors.password?.message}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <LockIcon color="action" />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowPassword(!showPassword)}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              mt: 1,
              mb: 2,
            }}
          >
            <FormControlLabel
              control={<Checkbox {...register('rememberMe')} />}
              label="Remember me"
            />
            <Link to="/forgot-password" style={{ textDecoration: 'none' }}>
              <Typography variant="body2" color="primary">
                Forgot password?
              </Typography>
            </Link>
          </Box>

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={isLoading}
            sx={{ mb: 2 }}
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </Button>
        </form>

        {/* Register Link */}
        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Don't have an account?{' '}
            <Link to="/register" style={{ textDecoration: 'none' }}>
              <Typography component="span" variant="body2" color="primary">
                Sign up
              </Typography>
            </Link>
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};
```

### 8.2 Protected Route Component (`src/components/common/ProtectedRoute/ProtectedRoute.tsx`)

```typescript
import React, { useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { CircularProgress, Box } from '@mui/material';
import { useAuthStore } from '@/stores/auth.store';
import { UserRole } from '@/types';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: UserRole[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRoles,
}) => {
  const { isAuthenticated, user, isLoading } = useAuthStore();
  const location = useLocation();

  if (isLoading) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredRoles && user && !requiredRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};
```

---

## 9. Material-UI Theme Configuration

### 9.1 Theme Definition (`src/theme/index.ts`)

```typescript
import { createTheme, ThemeOptions } from '@mui/material/styles';
import { palette } from './palette';
import { typography } from './typography';
import { components } from './components';

export const theme = createTheme({
  palette,
  typography,
  components,
  shape: {
    borderRadius: 8,
  },
  spacing: 8,
} as ThemeOptions);

// Dark theme variant
export const darkTheme = createTheme({
  ...theme,
  palette: {
    mode: 'dark',
    primary: palette.primary,
    secondary: palette.secondary,
    background: {
      default: '#0a0a0a',
      paper: '#1a1a1a',
    },
  },
});
```

### 9.2 Palette (`src/theme/palette.ts`)

```typescript
import { PaletteOptions } from '@mui/material/styles';

export const palette: PaletteOptions = {
  mode: 'light',
  primary: {
    main: '#1976d2',
    light: '#42a5f5',
    dark: '#1565c0',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#9c27b0',
    light: '#ba68c8',
    dark: '#7b1fa2',
    contrastText: '#ffffff',
  },
  error: {
    main: '#d32f2f',
    light: '#ef5350',
    dark: '#c62828',
  },
  warning: {
    main: '#ed6c02',
    light: '#ff9800',
    dark: '#e65100',
  },
  info: {
    main: '#0288d1',
    light: '#03a9f4',
    dark: '#01579b',
  },
  success: {
    main: '#2e7d32',
    light: '#4caf50',
    dark: '#1b5e20',
  },
  grey: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#eeeeee',
    300: '#e0e0e0',
    400: '#bdbdbd',
    500: '#9e9e9e',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
  },
  background: {
    default: '#f5f7fa',
    paper: '#ffffff',
  },
  text: {
    primary: '#1a1a2e',
    secondary: '#6b7280',
    disabled: '#9ca3af',
  },
  divider: '#e5e7eb',
};
```

### 9.3 Component Overrides (`src/theme/components.ts`)

```typescript
import { Components } from '@mui/material/styles';

export const components: Components = {
  MuiButton: {
    styleOverrides: {
      root: {
        textTransform: 'none',
        fontWeight: 600,
        borderRadius: 8,
        padding: '10px 24px',
      },
      contained: {
        boxShadow: 'none',
        '&:hover': {
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        },
      },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: 12,
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      },
    },
  },
  MuiTextField: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          borderRadius: 8,
        },
      },
    },
  },
  MuiChip: {
    styleOverrides: {
      root: {
        borderRadius: 6,
        fontWeight: 500,
      },
    },
  },
  MuiDataGrid: {
    styleOverrides: {
      root: {
        border: 'none',
        '& .MuiDataGrid-cell': {
          borderBottom: '1px solid #e5e7eb',
        },
        '& .MuiDataGrid-columnHeaders': {
          backgroundColor: '#f9fafb',
          borderBottom: '2px solid #e5e7eb',
        },
      },
    },
  },
};
```

---

## 10. Mobile Responsiveness

### 10.1 Responsive Breakpoints

```typescript
// src/theme/breakpoints.ts
import { BreakpointsOptions } from '@mui/material/styles';

export const breakpoints: BreakpointsOptions = {
  values: {
    xs: 0,      // Mobile
    sm: 600,    // Tablet
    md: 960,    // Small desktop
    lg: 1280,   // Desktop
    xl: 1920,   // Large desktop
  },
};
```

### 10.2 Responsive Dashboard Grid

```typescript
// src/features/dashboard/components/DashboardGrid/DashboardGrid.tsx
import React from 'react';
import { Grid, useMediaQuery, useTheme } from '@mui/material';
import { KPICards } from '../KPICards';
import { IncidentOverview } from '../IncidentOverview';
import { SystemHealth } from '../SystemHealth';
import { RecentAlerts } from '../RecentAlerts';
import { ActivityFeed } from '../ActivityFeed';

export const DashboardGrid: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'md'));

  return (
    <Grid container spacing={isMobile ? 2 : 3}>
      {/* KPI Cards - Full width on mobile, 4 columns on desktop */}
      <Grid item xs={12}>
        <KPICards />
      </Grid>

      {/* Incident Overview - Full width on mobile, 8 columns on desktop */}
      <Grid item xs={12} lg={8}>
        <IncidentOverview />
      </Grid>

      {/* System Health - Full width on mobile, 4 columns on desktop */}
      <Grid item xs={12} md={6} lg={4}>
        <SystemHealth />
      </Grid>

      {/* Recent Alerts - Half width on tablet, full on mobile */}
      <Grid item xs={12} md={6}>
        <RecentAlerts />
      </Grid>

      {/* Activity Feed - Half width on tablet, full on mobile */}
      <Grid item xs={12} md={6}>
        <ActivityFeed />
      </Grid>
    </Grid>
  );
};
```

### 10.3 Mobile-First Data Table

```typescript
// src/components/common/DataTable/DataTable.tsx
import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  useMediaQuery,
  useTheme,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
} from '@mui/material';

interface Column<T> {
  key: keyof T | string;
  header: string;
  width?: string | number;
  render?: (row: T) => React.ReactNode;
  hideOnMobile?: boolean;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (row: T) => string;
  onRowClick?: (row: T) => void;
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  onRowClick,
}: DataTableProps<T>) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  // Mobile card view
  if (isMobile) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {data.map((row) => (
          <Card
            key={keyExtractor(row)}
            onClick={() => onRowClick?.(row)}
            sx={{
              cursor: onRowClick ? 'pointer' : 'default',
              '&:hover': onRowClick ? { boxShadow: 4 } : {},
            }}
          >
            <CardContent>
              {columns
                .filter((col) => !col.hideOnMobile)
                .map((column) => (
                  <Box
                    key={String(column.key)}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      py: 0.5,
                      borderBottom: '1px solid',
                      borderColor: 'divider',
                      '&:last-child': { borderBottom: 'none' },
                    }}
                  >
                    <Typography variant="caption" color="text.secondary">
                      {column.header}
                    </Typography>
                    <Box>
                      {column.render
                        ? column.render(row)
                        : String((row as Record<string, unknown>)[column.key as string] ?? '-')}
                    </Box>
                  </Box>
                ))}
            </CardContent>
          </Card>
        ))}
      </Box>
    );
  }

  // Desktop table view
  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            {columns.map((column) => (
              <TableCell
                key={String(column.key)}
                style={{ width: column.width }}
              >
                {column.header}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row) => (
            <TableRow
              key={keyExtractor(row)}
              onClick={() => onRowClick?.(row)}
              sx={{
                cursor: onRowClick ? 'pointer' : 'default',
                '&:hover': onRowClick ? { bgcolor: 'action.hover' } : {},
              }}
            >
              {columns.map((column) => (
                <TableCell key={String(column.key)}>
                  {column.render
                    ? column.render(row)
                    : String((row as Record<string, unknown>)[column.key as string] ?? '-')}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
```

---

## 11. Package.json Configuration

```json
{
  "name": "resilience-ai-ui",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint . --ext ts,tsx --fix",
    "format": "prettier --write \"src/**/*.{ts,tsx}\"",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "@hookform/resolvers": "^3.3.2",
    "@mui/icons-material": "^5.14.19",
    "@mui/material": "^5.14.20",
    "@mui/x-data-grid": "^6.18.4",
    "@mui/x-date-pickers": "^6.18.4",
    "@tanstack/react-query": "^5.13.4",
    "axios": "^1.6.2",
    "date-fns": "^2.30.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-hook-form": "^7.49.2",
    "react-router-dom": "^6.21.0",
    "recharts": "^2.10.3",
    "socket.io-client": "^4.7.2",
    "zod": "^3.22.4",
    "zustand": "^4.4.7"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.1.5",
    "@testing-library/react": "^14.1.2",
    "@testing-library/user-event": "^14.5.1",
    "@types/node": "^20.10.5",
    "@types/react": "^18.2.45",
    "@types/react-dom": "^18.2.18",
    "@typescript-eslint/eslint-plugin": "^6.15.0",
    "@typescript-eslint/parser": "^6.15.0",
    "@vitejs/plugin-react": "^4.2.1",
    "@vitest/ui": "^1.1.0",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.56.0",
    "eslint-config-prettier": "^9.1.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "jsdom": "^23.0.2",
    "postcss": "^8.4.32",
    "prettier": "^3.1.1",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.3.3",
    "vite": "^5.0.10",
    "vitest": "^1.1.0"
  }
}
```

---

## 12. Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          mui: ['@mui/material', '@mui/icons-material'],
          charts: ['recharts'],
          query: ['@tanstack/react-query'],
        },
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
  },
});
```

---

## 13. Implementation Priority Order

### Phase 1: Foundation (Week 1-2)
1. **Project Setup**
   - Initialize Vite + React + TypeScript project
   - Configure ESLint, Prettier, Tailwind
   - Set up folder structure

2. **Core Infrastructure**
   - Axios configuration with interceptors
   - TypeScript type definitions
   - MUI theme configuration
   - Routing setup with React Router

3. **Authentication**
   - Login/Logout functionality
   - Protected routes
   - Auth store with Zustand
   - Token refresh mechanism

### Phase 2: Core Features (Week 3-4)
4. **Layout Components**
   - MainLayout with responsive sidebar
   - Header with user menu and notifications
   - Navigation system

5. **Dashboard**
   - KPI cards component
   - System health widget
   - Recent alerts list
   - Activity feed
   - React Query integration

6. **Incidents Module**
   - Incident list with filtering
   - Incident detail view
   - Incident creation form
   - Data table component

### Phase 3: Advanced Features (Week 5-6)
7. **Analytics**
   - Chart components (Recharts)
   - Time series data visualization
   - Custom reports
   - Export functionality

8. **Real-time Updates**
   - WebSocket integration
   - Live notifications
   - Real-time dashboard updates

9. **Settings & Profile**
   - User profile management
   - Notification preferences
   - System settings

### Phase 4: Polish & Optimization (Week 7-8)
10. **Mobile Responsiveness**
    - Mobile-first design refinements
    - Touch-friendly interactions
    - Responsive data tables

11. **Performance**
    - Code splitting
    - Lazy loading
    - Caching optimization

12. **Testing & Documentation**
    - Unit tests
    - Integration tests
    - Component documentation

---

## 14. Backend Integration Notes

### API Compatibility

The React UI is designed to work with the existing FastAPI backend:

```
┌─────────────────┐     REST/WebSocket     ┌─────────────────┐
│   React UI      │ ◄────────────────────► │  FastAPI        │
│   (New)         │                        │  Backend        │
│                 │                        │  (Existing)     │
└─────────────────┘                        └─────────────────┘
                                                  │
                                                  ▼
                                           ┌─────────────────┐
                                           │  Streamlit      │
                                           │  (Legacy)       │
                                           └─────────────────┘
```

### Required Backend Endpoints

1. **Authentication**
   - `POST /api/v1/auth/login`
   - `POST /api/v1/auth/logout`
   - `POST /api/v1/auth/refresh`
   - `GET /api/v1/auth/me`

2. **Dashboard**
   - `GET /api/v1/dashboard/metrics`
   - `GET /api/v1/dashboard/alerts`
   - `POST /api/v1/dashboard/alerts/{id}/acknowledge`
   - `GET /api/v1/dashboard/activity`
   - `GET /api/v1/dashboard/health`

3. **Incidents**
   - `GET /api/v1/incidents`
   - `GET /api/v1/incidents/{id}`
   - `POST /api/v1/incidents`
   - `PUT /api/v1/incidents/{id}`
   - `DELETE /api/v1/incidents/{id}`

4. **Analytics**
   - `GET /api/v1/analytics/trends`
   - `GET /api/v1/analytics/metrics`
   - `GET /api/v1/analytics/reports`

5. **WebSocket**
   - `ws://localhost:8000/ws`

---

## 15. Summary

This React-based UI design for ResilienceAI provides:

1. **Modern Architecture**: Component-based design with clear separation of concerns
2. **Type Safety**: Comprehensive TypeScript types for all data structures
3. **State Management**: Zustand for client state, React Query for server state
4. **Real-time Capabilities**: WebSocket integration for live updates
5. **Responsive Design**: Mobile-first approach with MUI + Tailwind
6. **Authentication**: Secure JWT-based auth with token refresh
7. **Performance**: Optimized with code splitting and caching
8. **Developer Experience**: Full TypeScript support, ESLint, Prettier

The implementation follows industry best practices and provides a scalable foundation for the ResilienceAI platform.
