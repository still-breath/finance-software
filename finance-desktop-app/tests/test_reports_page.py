import sys, os
import pytest
from unittest.mock import Mock
from PyQt5.QtWidgets import QApplication

# Ensure src on path
BASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'src')
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui.reports import ReportsPage

@pytest.fixture(scope="module")
def app():
    qapp = QApplication.instance() or QApplication(sys.argv)
    yield qapp

@pytest.fixture
def mock_api():
    m = Mock()
    m.get_monthly_stats.return_value = {
        'monthly_stats': [
            {'month': '2025-10', 'income': 1000000, 'expense': -400000, 'balance': 600000},
            {'month': '2025-09', 'income': 900000, 'expense': -500000, 'balance': 400000},
            {'month': '2025-08', 'income': 800000, 'expense': -300000, 'balance': 500000},
        ]
    }
    m.get_category_stats.return_value = {
        'category_distribution': [
            {'category_name': 'Food', 'total_amount': -150000, 'transaction_count': 5, 'avg_amount': -30000},
            {'category_name': 'Salary', 'total_amount': 2000000, 'transaction_count': 1, 'avg_amount': 2000000},
            {'category_name': 'Transport', 'total_amount': -50000, 'transaction_count': 3, 'avg_amount': -16666},
        ],
        'prediction_methods': [
            {'method': 'ai_prediction', 'count': 10},
            {'method': 'manual', 'count': 5},
            {'method': 'default', 'count': 5},
        ]
    }
    m.get_transactions.return_value = {
        'transactions': [
            {'description': 'Lunch', 'amount': -45000, 'category_name': 'Food', 'transaction_date': '2025-10-04'},
            {'description': 'Salary October', 'amount': 2000000, 'category_name': 'Salary', 'transaction_date': '2025-10-01'},
            {'description': 'Bus', 'amount': -8000, 'category_name': 'Transport', 'transaction_date': '2025-10-03'},
        ]
    }
    m.get_transaction_summary.return_value = {'summary': {'transaction_count': 3}}
    return m

class TestReportsPage:
    def test_construction(self, app, mock_api):
        page = ReportsPage(mock_api)
        assert page is not None
        assert page.api_client == mock_api

    def test_load_all_populates(self, app, mock_api):
        page = ReportsPage(mock_api)
        page.load_all()
        # Check some labels updated
        assert 'Income:' in page.monthly_income_label.text()
        assert page.category_stats_layout.count() > 0
        assert page.ai_stats_layout.count() > 0
        assert page.top_categories_layout.count() > 0
        assert page.recent_summary_layout.count() > 0

    def test_update_monthly_trends(self, app, mock_api):
        page = ReportsPage(mock_api)
        data = mock_api.get_monthly_stats.return_value
        page.update_monthly_trends(data)
        # Expect chart or fallback created + table label
        assert page.trend_info_layout.count() >= 1
