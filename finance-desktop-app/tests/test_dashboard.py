import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from unittest.mock import Mock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ui.dashboard import DashboardWindow
from api.client import APIClient

@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    app.quit()

@pytest.fixture
def mock_api_client():
    return Mock(spec=APIClient)

@pytest.fixture
def user_data():
    """Sample user data"""
    return {
        'id': 1,
        'name': 'Test User',
        'email': 'test@example.com'
    }

class TestDashboardWindow:
    
    def test_dashboard_creation(self, app, mock_api_client, user_data):
        dashboard = DashboardWindow(mock_api_client, user_data)
        assert dashboard is not None
        assert dashboard.windowTitle() == 'Finance Manager - Dashboard'
        assert dashboard.api_client == mock_api_client
        assert dashboard.user_data == user_data
        dashboard.close()
    
    def test_dashboard_ui_components(self, app, mock_api_client, user_data):
        dashboard = DashboardWindow(mock_api_client, user_data)
        
        # Check main components exist
        assert dashboard.sidebar is not None
        assert dashboard.content_area is not None
        assert dashboard.nav_list is not None
        
        # Check pages exist
        assert dashboard.overview_page is not None
        assert dashboard.transactions_page is not None
        assert dashboard.categories_page is not None
        assert dashboard.reports_page is not None
        assert dashboard.settings_page is not None
        
        dashboard.close()
    
    def test_navigation_items(self, app, mock_api_client, user_data):
        dashboard = DashboardWindow(mock_api_client, user_data)
        
        # Check navigation items count
        assert dashboard.nav_list.count() == 5
        
        # Check navigation item texts
        expected_items = ['Overview', 'Transactions', 'Categories', 'Reports', 'Settings']
        for i, expected_text in enumerate(expected_items):
            item = dashboard.nav_list.item(i)
            assert item.text() == expected_text
        
        dashboard.close()
    
    def test_summary_cards(self, app, mock_api_client, user_data):
        """Test summary cards creation"""
        dashboard = DashboardWindow(mock_api_client, user_data)
        
        # Check summary cards exist
        assert dashboard.balance_card is not None
        assert dashboard.income_card is not None
        assert dashboard.expenses_card is not None
        assert dashboard.savings_card is not None
        
        # Check cards have value labels
        assert hasattr(dashboard.balance_card, 'value_label')
        assert hasattr(dashboard.income_card, 'value_label')
        assert hasattr(dashboard.expenses_card, 'value_label')
        assert hasattr(dashboard.savings_card, 'value_label')
        
        dashboard.close()
    
    def test_update_summary_cards(self, app, mock_api_client, user_data):
        dashboard = DashboardWindow(mock_api_client, user_data)
        
        # Test data
        test_data = {
            'total_balance': 1500.25,
            'monthly_income': 2500.00,
            'monthly_expenses': 1800.75,
            'savings_rate': 28.5
        }
        
        # Update cards
        dashboard.update_summary_cards(test_data)
        
        # Check values were updated
        assert dashboard.balance_card.value_label.text() == "$1,500.25"
        assert dashboard.income_card.value_label.text() == "$2,500.00"
        assert dashboard.expenses_card.value_label.text() == "$1,800.75"
        assert dashboard.savings_card.value_label.text() == "28.5%"
        
        dashboard.close()
    
    def test_navigation_switching(self, app, mock_api_client, user_data):
        dashboard = DashboardWindow(mock_api_client, user_data)
        
        # Initially should show overview page
        assert dashboard.content_area.currentWidget() == dashboard.overview_page
        
        # Test switching to transactions page
        dashboard.nav_list.setCurrentRow(1)  # Transactions
        dashboard.show_transactions()
        assert dashboard.content_area.currentWidget() == dashboard.transactions_page
        
        # Test switching to categories page
        dashboard.nav_list.setCurrentRow(2)  # Categories
        dashboard.show_categories()
        assert dashboard.content_area.currentWidget() == dashboard.categories_page
        
        dashboard.close()
    
    def test_user_info_display(self, app, mock_api_client, user_data):
        dashboard = DashboardWindow(mock_api_client, user_data)
        dashboard.show()
        
        # Find user info labels in sidebar
        user_labels = dashboard.sidebar.findChildren(dashboard.sidebar.__class__.__bases__[0])
        
        # Should display user name and email somewhere
        sidebar_text = dashboard.sidebar.findChildren(dashboard.sidebar.__class__.__bases__[0])
        
        dashboard.close()
    
    def test_logout_functionality(self, app, mock_api_client, user_data):
        """Test logout functionality"""
        dashboard = DashboardWindow(mock_api_client, user_data)
        
        # Test logout button exists
        assert dashboard.logout_btn is not None
        
        # Mock logout signal
        logout_signal_emitted = False
        
        def on_logout():
            nonlocal logout_signal_emitted
            logout_signal_emitted = True
        
        dashboard.logout_requested.connect(on_logout)
        
        # Trigger logout
        dashboard.logout()
        
        # Check API client logout was called
        mock_api_client.logout.assert_called_once()
        
        # Check signal was emitted
        assert logout_signal_emitted == True
    
    def test_load_transactions(self, app, mock_api_client, user_data):
        """Test loading transactions"""
        dashboard = DashboardWindow(mock_api_client, user_data)
        
        # Load transactions
        dashboard.load_transactions()
        
        # Check transactions list is populated
        assert dashboard.transactions_list.count() > 0
        
        # Check first item is not the loading message
        first_item = dashboard.transactions_list.item(0)
        assert first_item.text() != 'Loading transactions...'
        
        dashboard.close()
    
    def test_recent_transactions_load(self, app, mock_api_client, user_data):
        dashboard = DashboardWindow(mock_api_client, user_data)
        
        # Load recent transactions
        dashboard.load_recent_transactions()
        
        # Check recent transactions list is populated
        assert dashboard.recent_transactions_list.count() > 0
        
        # Check first item is not the loading message
        first_item = dashboard.recent_transactions_list.item(0)
        assert first_item.text() != 'Loading transactions...'
        
        dashboard.close()