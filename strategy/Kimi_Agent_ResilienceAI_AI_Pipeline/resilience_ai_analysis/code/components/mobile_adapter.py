"""
Mobile-Responsive Adapter for ResilienceAI Dashboard
Automatically adapts layout and interactions for mobile devices
"""
import streamlit as st
from typing import Dict, List, Callable, Optional, Any
import re


class MobileAdapter:
    """
    Detects mobile devices and adapts dashboard layout accordingly.
    Provides touch-optimized controls and simplified navigation.
    """
    
    MOBILE_BREAKPOINT = 768  # pixels
    TABLET_BREAKPOINT = 1024  # pixels
    
    # Simplified tab structure for mobile
    MOBILE_TABS = {
        '📊 Overview': {
            'icon': '📊',
            'tabs': ['metrics', 'alerts', 'quick_stats'],
            'description': 'Key metrics and alerts'
        },
        '🗺️ Map': {
            'icon': '🗺️',
            'tabs': ['choropleth', 'drill_down'],
            'description': 'Interactive maps'
        },
        '🔍 Search': {
            'icon': '🔍',
            'tabs': ['ai_chat', 'county_finder'],
            'description': 'Search and query'
        },
        '⚙️ More': {
            'icon': '⚙️',
            'tabs': ['preferences', 'filters', 'settings'],
            'description': 'Settings and filters'
        }
    }
    
    # Touch-optimized chart configurations
    MOBILE_CHART_CONFIG = {
        'height': 350,
        'margin': dict(l=30, r=30, t=40, b=30),
        'dragmode': False,
        'hovermode': 'closest',
        'showlegend': False
    }
    
    def __init__(self):
        self.is_mobile = self._detect_mobile()
        self.is_tablet = self._detect_tablet()
        self.screen_width = self._get_screen_width()
        self.device_type = self._determine_device_type()
        
    def _detect_mobile(self) -> bool:
        """Detect if user is on a mobile device."""
        # Check via JavaScript injection or user agent
        user_agent = st.session_state.get('user_agent', '').lower()
        
        mobile_patterns = [
            'android', 'iphone', 'ipad', 'ipod', 'windows phone',
            'blackberry', 'mobile', 'webos', 'opera mini'
        ]
        
        return any(pattern in user_agent for pattern in mobile_patterns)
    
    def _detect_tablet(self) -> bool:
        """Detect if user is on a tablet device."""
        user_agent = st.session_state.get('user_agent', '').lower()
        return 'ipad' in user_agent or ('android' in user_agent and 'mobile' not in user_agent)
    
    def _get_screen_width(self) -> int:
        """Get screen width via JavaScript."""
        # Use session state or default
        return st.session_state.get('screen_width', 1200)
    
    def _determine_device_type(self) -> str:
        """Determine device type based on detection."""
        if self.is_mobile:
            return 'mobile'
        elif self.is_tablet:
            return 'tablet'
        elif self.screen_width < self.TABLET_BREAKPOINT:
            return 'small_desktop'
        else:
            return 'desktop'
    
    def adapt_layout(self, content_renderer: Callable[[bool], None]):
        """
        Wrap content with mobile adaptations.
        
        Args:
            content_renderer: Function that renders dashboard content.
                            Receives `is_mobile` parameter.
        """
        # Inject responsive styles
        self._inject_responsive_styles()
        
        # Inject JavaScript for screen detection
        self._inject_screen_detection_js()
        
        # Render appropriate layout
        if self.device_type in ['mobile', 'tablet']:
            self._render_mobile_layout(content_renderer)
        else:
            self._render_desktop_layout(content_renderer)
    
    def _inject_responsive_styles(self):
        """Inject responsive CSS styles."""
        st.markdown("""
        <style>
        /* Mobile-first responsive design */
        @media (max-width: 768px) {
            .stApp {
                font-size: 14px !important;
            }
            
            /* Tab styling */
            .stTabs [data-baseweb="tab-list"] {
                flex-wrap: wrap !important;
                gap: 4px !important;
            }
            
            .stTabs [data-baseweb="tab"] {
                padding: 6px 10px !important;
                font-size: 11px !important;
                min-height: 36px !important;
            }
            
            /* Metric cards */
            .stMetric {
                padding: 8px !important;
            }
            
            .stMetric label {
                font-size: 11px !important;
            }
            
            .stMetric .css-1xarl3l {
                font-size: 18px !important;
            }
            
            /* Buttons */
            .stButton > button {
                width: 100% !important;
                padding: 12px !important;
                font-size: 14px !important;
                min-height: 44px !important;
            }
            
            /* Form inputs */
            .stSelectbox > div > div,
            .stTextInput > div > div {
                min-height: 44px !important;
            }
            
            /* Dataframes */
            .stDataFrame {
                font-size: 12px !important;
            }
            
            /* Sidebar */
            .css-1d391kg {
                width: 100% !important;
            }
        }
        
        /* Tablet adjustments */
        @media (min-width: 769px) and (max-width: 1024px) {
            .stTabs [data-baseweb="tab"] {
                padding: 8px 14px !important;
                font-size: 13px !important;
            }
        }
        
        /* Touch-friendly elements */
        .touch-target {
            min-height: 44px;
            min-width: 44px;
        }
        
        /* Bottom navigation for mobile */
        .mobile-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
            display: flex;
            justify-content: space-around;
            padding: 8px 0 calc(8px + env(safe-area-inset-bottom));
            border-top: 1px solid rgba(192, 132, 252, 0.3);
            z-index: 1000;
            backdrop-filter: blur(10px);
        }
        
        .mobile-nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            color: #94a3b8;
            font-size: 10px;
            padding: 4px 12px;
            cursor: pointer;
            transition: all 0.2s ease;
            min-width: 60px;
        }
        
        .mobile-nav-item.active {
            color: #c084fc;
        }
        
        .mobile-nav-item:active {
            transform: scale(0.95);
        }
        
        .mobile-nav-item .icon {
            font-size: 22px;
            margin-bottom: 2px;
        }
        
        /* Main content padding for bottom nav */
        .main-content-mobile {
            padding-bottom: 80px !important;
        }
        
        /* Touch cards */
        .touch-card {
            min-height: 60px;
            padding: 16px;
            margin: 8px 0;
            border-radius: 12px;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(30, 41, 59, 0.7) 100%);
            border: 1px solid rgba(192, 132, 252, 0.2);
            touch-action: manipulation;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .touch-card:active {
            transform: scale(0.98);
            background: rgba(192, 132, 252, 0.1);
        }
        
        /* Swipe indicators */
        .swipe-hint {
            text-align: center;
            color: #64748b;
            font-size: 12px;
            padding: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        /* Pull-to-refresh indicator */
        .pull-refresh {
            text-align: center;
            padding: 20px;
            color: #94a3b8;
        }
        
        /* Floating action button */
        .fab {
            position: fixed;
            bottom: 90px;
            right: 16px;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, #c084fc 0%, #818cf8 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(192, 132, 252, 0.4);
            z-index: 999;
            cursor: pointer;
        }
        
        /* Hide scrollbar but allow scrolling */
        .hide-scrollbar {
            -ms-overflow-style: none;
            scrollbar-width: none;
        }
        
        .hide-scrollbar::-webkit-scrollbar {
            display: none;
        }
        </style>
        
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="theme-color" content="#0f172a">
        """, unsafe_allow_html=True)
    
    def _inject_screen_detection_js(self):
        """Inject JavaScript for screen size detection."""
        js_code = """
        <script>
        // Detect screen size and user agent
        const screenWidth = window.innerWidth;
        const screenHeight = window.innerHeight;
        const userAgent = navigator.userAgent;
        const isTouch = 'ontouchstart' in window;
        
        // Send to Streamlit
        const data = {
            screen_width: screenWidth,
            screen_height: screenHeight,
            user_agent: userAgent,
            is_touch: isTouch,
            device_pixel_ratio: window.devicePixelRatio
        };
        
        // Store in session storage for persistence
        sessionStorage.setItem('device_info', JSON.stringify(data));
        
        // Send message to Streamlit
        if (window.parent && window.parent.postMessage) {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: JSON.stringify(data)
            }, '*');
        }
        
        // Listen for resize events
        window.addEventListener('resize', function() {
            const newData = {
                ...data,
                screen_width: window.innerWidth,
                screen_height: window.innerHeight
            };
            sessionStorage.setItem('device_info', JSON.stringify(newData));
        });
        </script>
        """
        st.components.v1.html(js_code, height=0)
    
    def _render_mobile_layout(self, content_renderer: Callable[[bool], None]):
        """Render mobile-optimized layout."""
        # Get current tab
        current_tab = st.session_state.get('mobile_tab', '📊 Overview')
        
        # Render simplified header
        st.markdown("""
        <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid rgba(192, 132, 252, 0.2);
            margin-bottom: 16px;
        ">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 24px;">🛡️</span>
                <span style="font-weight: 600; color: #f8fafc;">ResilienceAI</span>
            </div>
            <div style="color: #94a3b8; font-size: 12px;">Mobile</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Main content with padding for bottom nav
        st.markdown('<div class="main-content-mobile">', unsafe_allow_html=True)
        content_renderer(mobile=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Bottom navigation
        self._render_bottom_navigation()
    
    def _render_bottom_navigation(self):
        """Render bottom navigation bar for mobile."""
        current_tab = st.session_state.get('mobile_tab', '📊 Overview')
        
        nav_items = []
        for tab_name, tab_config in self.MOBILE_TABS.items():
            is_active = tab_name == current_tab
            active_class = 'active' if is_active else ''
            nav_items.append(f'''
                <div class="mobile-nav-item {active_class}" 
                     onclick="handleNavClick('{tab_name}')">
                    <span class="icon">{tab_config['icon']}</span>
                    <span>{tab_name[2:]}</span>
                </div>
            ''')
        
        nav_html = f'''
        <div class="mobile-nav">
            {''.join(nav_items)}
        </div>
        <script>
        function handleNavClick(tabName) {{
            // Send to Streamlit
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                key: 'mobile_tab',
                value: tabName
            }}, '*');
        }}
        </script>
        '''
        
        st.markdown(nav_html, unsafe_allow_html=True)
    
    def _render_desktop_layout(self, content_renderer: Callable[[bool], None]):
        """Render standard desktop layout."""
        content_renderer(mobile=False)
    
    def adapt_chart_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt chart configuration for mobile screens."""
        if self.device_type not in ['mobile', 'tablet']:
            return config
        
        mobile_config = config.copy()
        
        # Reduce chart height
        if 'height' in mobile_config:
            mobile_config['height'] = min(mobile_config['height'], self.MOBILE_CHART_CONFIG['height'])
        else:
            mobile_config['height'] = self.MOBILE_CHART_CONFIG['height']
        
        # Adjust margins
        mobile_config['margin'] = self.MOBILE_CHART_CONFIG['margin']
        
        # Simplify interactions
        mobile_config['dragmode'] = self.MOBILE_CHART_CONFIG['dragmode']
        mobile_config['hovermode'] = self.MOBILE_CHART_CONFIG['hovermode']
        
        # Reduce legend for mobile
        if self.device_type == 'mobile':
            mobile_config['showlegend'] = False
        
        return mobile_config
    
    def render_touch_card(
        self,
        title: str,
        value: str,
        subtitle: Optional[str] = None,
        on_tap: Optional[Callable] = None,
        icon: Optional[str] = None,
        badge: Optional[str] = None,
        key: Optional[str] = None
    ):
        """Render a touch-friendly metric card."""
        card_key = key or f"touch_card_{title}"
        
        badge_html = f'''
            <span style="
                background: rgba(192, 132, 252, 0.2);
                color: #c084fc;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 10px;
                margin-left: 8px;
            ">{badge}</span>
        ''' if badge else ''
        
        card_html = f'''
        <div class="touch-card" id="{card_key}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div style="color: #94a3b8; font-size: 12px; margin-bottom: 4px;">
                        {title} {badge_html}
                    </div>
                    <div style="color: #f8fafc; font-size: 28px; font-weight: 600;">
                        {icon + ' ' if icon else ''}{value}
                    </div>
                    {f'<div style="color: #64748b; font-size: 11px; margin-top: 4px;">{subtitle}</div>' if subtitle else ''}
                </div>
                <div style="color: #c084fc; font-size: 20px;">›</div>
            </div>
        </div>
        '''
        
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Handle tap via invisible button
        if on_tap:
            if st.button(f"Tap {title}", key=f"{card_key}_tap", visible=False):
                on_tap()
    
    def render_mobile_metrics(self, metrics: List[Dict[str, Any]]):
        """Render metrics in mobile-optimized grid."""
        # Use 2-column grid for mobile
        cols = st.columns(2)
        
        for idx, metric in enumerate(metrics):
            with cols[idx % 2]:
                self.render_touch_card(
                    title=metric.get('label', 'Metric'),
                    value=metric.get('value', 'N/A'),
                    subtitle=metric.get('delta'),
                    icon=metric.get('icon'),
                    badge=metric.get('badge'),
                    key=f"metric_{idx}"
                )
    
    def render_mobile_list(
        self,
        items: List[Dict[str, Any]],
        on_item_click: Optional[Callable] = None,
        key_prefix: str = "list"
    ):
        """Render a mobile-optimized list."""
        for idx, item in enumerate(items):
            with st.container():
                st.markdown(f'''
                <div style="
                    background: rgba(30, 41, 59, 0.6);
                    border-radius: 12px;
                    padding: 14px 16px;
                    margin: 8px 0;
                    border: 1px solid rgba(192, 132, 252, 0.1);
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                ">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 24px;">{item.get('icon', '📍')}</span>
                        <div>
                            <div style="color: #f8fafc; font-weight: 500;">{item.get('title', '')}</div>
                            <div style="color: #94a3b8; font-size: 12px;">{item.get('subtitle', '')}</div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #f8fafc; font-weight: 600;">{item.get('value', '')}</div>
                        {f'<div style="color: {item.get("delta_color", "#94a3b8")}; font-size: 11px;">{item.get("delta", "")}</div>' if item.get('delta') else ''}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                if on_item_click:
                    if st.button(f"Select", key=f"{key_prefix}_item_{idx}", visible=False):
                        on_item_click(item)
    
    def get_column_count(self) -> int:
        """Get recommended column count based on device type."""
        if self.device_type == 'mobile':
            return 1
        elif self.device_type == 'tablet':
            return 2
        elif self.device_type == 'small_desktop':
            return 2
        else:
            return 3
    
    def should_show_feature(self, feature: str) -> bool:
        """Determine if a feature should be shown on current device."""
        mobile_excluded = [
            '3d_visualization',
            'network_graph',
            'ar_mode',
            'advanced_filters'
        ]
        
        if self.device_type == 'mobile' and feature in mobile_excluded:
            return False
        
        return True


# Convenience functions for dashboard integration
def detect_device() -> MobileAdapter:
    """Detect device and return adapter."""
    return MobileAdapter()


def render_mobile_optimized(
    content_renderer: Callable[[bool], None],
    adapter: Optional[MobileAdapter] = None
):
    """Render content with mobile optimization."""
    if adapter is None:
        adapter = detect_device()
    
    adapter.adapt_layout(content_renderer)
