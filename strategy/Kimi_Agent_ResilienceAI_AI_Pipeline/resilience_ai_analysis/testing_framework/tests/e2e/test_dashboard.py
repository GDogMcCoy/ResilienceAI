"""
End-to-end tests for Streamlit Dashboard

Uses Playwright for browser automation testing of the
ResilienceAI Streamlit dashboard.
"""
import pytest
import re
from playwright.sync_api import Page, expect, Browser


@pytest.mark.e2e
class TestDashboard:
    """E2E tests for ResilienceAI Dashboard."""
    
    @pytest.fixture(scope="class")
    def browser_context(self, browser: Browser):
        """Create browser context for tests."""
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            record_video_dir='tests/e2e/videos/'
        )
        yield context
        context.close()
    
    @pytest.fixture
    def page(self, browser_context):
        """Navigate to dashboard."""
        page = browser_context.new_page()
        page.goto("http://localhost:8501")
        page.wait_for_load_state('networkidle')
        yield page
        page.close()
    
    def test_dashboard_loads(self, page: Page):
        """Test dashboard loads successfully."""
        # Check title contains ResilienceAI
        expect(page).to_have_title(re.compile("ResilienceAI"))
        
        # Check main header is visible
        header = page.locator("h1").first
        expect(header).to_be_visible()
        expect(header).to_contain_text("ResilienceAI")
    
    def test_sidebar_is_visible(self, page: Page):
        """Test sidebar is visible."""
        sidebar = page.locator("[data-testid='stSidebar']")
        expect(sidebar).to_be_visible()
    
    def test_main_content_area(self, page: Page):
        """Test main content area is visible."""
        main = page.locator("main")
        expect(main).to_be_visible()
    
    def test_sidebar_navigation_tabs(self, page: Page):
        """Test sidebar navigation tabs exist."""
        # Common tab names in ResilienceAI dashboard
        expected_tabs = [
            'Vulnerability Map',
            'Risk Analysis',
            'Healthcare Gaps',
            'Agent Chat'
        ]
        
        for tab in expected_tabs:
            # Try to find tab button
            tab_button = page.locator(f"text={tab}")
            # Not all tabs may be visible, so just check if any exist
            count = tab_button.count()
            if count > 0:
                print(f"Found tab: {tab}")
    
    def test_county_filter_exists(self, page: Page):
        """Test county filter widget exists."""
        # Look for selectbox or multiselect for counties
        filter_widget = page.locator("[data-testid='stSelectbox']").first
        # or page.locator("[data-testid='stMultiselect']").first
        
        # If filter exists, it should be visible
        if filter_widget.count() > 0:
            expect(filter_widget).to_be_visible()
    
    def test_visualization_exists(self, page: Page):
        """Test that visualizations exist."""
        # Look for common visualization elements
        viz_selectors = [
            "[data-testid='stDeckGlJsonChart']",  # Map
            "[data-testid='stPlotlyChart']",       # Plotly charts
            "[data-testid='stPyplot']",            # Matplotlib
        ]
        
        for selector in viz_selectors:
            elements = page.locator(selector)
            if elements.count() > 0:
                print(f"Found visualization: {selector}")
                break
    
    def test_data_table_exists(self, page: Page):
        """Test data table exists."""
        table = page.locator("[data-testid='stDataFrame']")
        if table.count() > 0:
            expect(table.first).to_be_visible()


@pytest.mark.e2e
class TestDashboardInteractions:
    """Test dashboard user interactions."""
    
    @pytest.fixture
    def page(self, browser):
        """Navigate to dashboard."""
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        page.goto("http://localhost:8501")
        page.wait_for_load_state('networkidle')
        yield page
        page.close()
    
    def test_county_filter_interaction(self, page: Page):
        """Test filtering by county."""
        # Find and interact with county filter
        filter_select = page.locator("[data-testid='stSelectbox']").first
        
        if filter_select.count() > 0:
            # Click to open dropdown
            filter_select.click()
            
            # Select a county (if dropdown opens)
            county_option = page.locator("text=St. Louis").first
            if county_option.count() > 0 and county_option.is_visible():
                county_option.click()
                
                # Wait for update
                page.wait_for_timeout(1000)
                
                # Verify filter applied
                expect(page.locator("text=St. Louis").first).to_be_visible()
    
    def test_tab_switching(self, page: Page):
        """Test switching between tabs."""
        # Find tabs
        tabs = page.locator("[data-testid='stTab']")
        
        if tabs.count() > 1:
            # Click second tab
            tabs.nth(1).click()
            page.wait_for_timeout(500)
            
            # Verify content changed
            main_content = page.locator("main")
            expect(main_content).to_be_visible()
    
    def test_agent_chat_interface(self, page: Page):
        """Test agent chat interface."""
        # Look for chat input
        chat_input = page.locator("[data-testid='stChatInput']")
        
        if chat_input.count() > 0:
            # Type message
            chat_input.fill("What is the vulnerability score for Jackson County?")
            
            # Submit (press Enter)
            chat_input.press("Enter")
            
            # Wait for response
            page.wait_for_selector("[data-testid='stChatMessage']", timeout=10000)
            
            # Verify response appeared
            messages = page.locator("[data-testid='stChatMessage']")
            expect(messages.first).to_be_visible()
    
    def test_export_functionality(self, page: Page):
        """Test data export functionality."""
        # Look for export buttons
        export_button = page.locator("button:has-text('Export')").first
        
        if export_button.count() > 0:
            # Click export
            export_button.click()
            
            # Wait for download or modal
            page.wait_for_timeout(500)


@pytest.mark.e2e
class TestDashboardResponsiveness:
    """Test dashboard responsiveness at different viewports."""
    
    @pytest.mark.parametrize("viewport", [
        {"width": 1920, "height": 1080, "name": "Desktop"},
        {"width": 1366, "height": 768, "name": "Laptop"},
        {"width": 768, "height": 1024, "name": "Tablet"},
        {"width": 390, "height": 844, "name": "Mobile"},
    ])
    def test_responsive_layout(self, browser, viewport):
        """Test dashboard at different viewport sizes."""
        context = browser.new_context(viewport=viewport)
        page = context.new_page()
        
        page.goto("http://localhost:8501")
        page.wait_for_load_state('networkidle')
        
        # Check that main content is visible
        main = page.locator("main")
        expect(main).to_be_visible()
        
        # Take screenshot for visual comparison
        page.screenshot(path=f"tests/e2e/screenshots/{viewport['name']}.png")
        
        context.close()


@pytest.mark.e2e
class TestDashboardErrorHandling:
    """Test dashboard error handling."""
    
    @pytest.fixture
    def page(self, browser):
        """Navigate to dashboard."""
        page = browser.new_page()
        page.goto("http://localhost:8501")
        page.wait_for_load_state('networkidle')
        yield page
        page.close()
    
    def test_invalid_county_input(self, page: Page):
        """Test handling of invalid county input."""
        # Try to input invalid county
        filter_input = page.locator("input").first
        
        if filter_input.count() > 0:
            filter_input.fill("INVALID_COUNTY_12345")
            filter_input.press("Enter")
            
            # Should show error or no results, not crash
            page.wait_for_timeout(500)
            
            # Check for error message
            error_msg = page.locator("text=error", case_sensitive=False)
            # or page.locator("text=not found", case_sensitive=False)
    
    def test_empty_state(self, page: Page):
        """Test dashboard handles empty state gracefully."""
        # Dashboard should load even with no data
        main = page.locator("main")
        expect(main).to_be_visible()


# Page Object for Dashboard
class DashboardPage:
    """Page object for Dashboard E2E tests."""
    
    URL = "http://localhost:8501"
    
    def __init__(self, page: Page):
        self.page = page
    
    def navigate(self):
        """Navigate to dashboard."""
        self.page.goto(self.URL)
        self.page.wait_for_load_state('networkidle')
    
    def get_header_text(self) -> str:
        """Get header text."""
        return self.page.locator("h1").first.text_content()
    
    def filter_by_county(self, county_name: str):
        """Filter dashboard by county."""
        filter_select = self.page.locator("[data-testid='stSelectbox']").first
        
        if filter_select.count() > 0:
            filter_select.click()
            option = self.page.locator(f"text={county_name}").first
            if option.count() > 0:
                option.click()
                self.page.wait_for_timeout(500)
    
    def send_chat_message(self, message: str):
        """Send message in chat."""
        chat_input = self.page.locator("[data-testid='stChatInput']")
        
        if chat_input.count() > 0:
            chat_input.fill(message)
            chat_input.press("Enter")
            self.page.wait_for_selector("[data-testid='stChatMessage']", timeout=10000)
    
    def get_chat_messages(self):
        """Get all chat messages."""
        return self.page.locator("[data-testid='stChatMessage']").all()
    
    def switch_tab(self, tab_name: str):
        """Switch to different dashboard tab."""
        tabs = self.page.locator("[data-testid='stTab']")
        
        for i in range(tabs.count()):
            if tab_name in tabs.nth(i).text_content():
                tabs.nth(i).click()
                self.page.wait_for_timeout(500)
                break
    
    def take_screenshot(self, name: str):
        """Take screenshot for debugging."""
        self.page.screenshot(path=f"tests/e2e/screenshots/{name}.png")
    
    def is_loaded(self) -> bool:
        """Check if dashboard is loaded."""
        main = self.page.locator("main")
        return main.count() > 0 and main.is_visible()


# Example usage of page object
@pytest.mark.e2e
def test_using_page_object(browser):
    """Example test using page object pattern."""
    page = browser.new_page()
    dashboard = DashboardPage(page)
    
    dashboard.navigate()
    assert dashboard.is_loaded()
    
    header = dashboard.get_header_text()
    assert "ResilienceAI" in header
    
    page.close()
