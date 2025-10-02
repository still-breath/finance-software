"""
Dashboard UI components for Finance Desktop Application
Main dashboard with navigation and content areas
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QStackedWidget, QListWidget, QListWidgetItem,
                           QLabel, QPushButton, QFrame, QScrollArea,
                           QGridLayout, QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.client import APIClient
from utils.logger import log_user_action, log_app_event, log_window_event

class DashboardWindow(QMainWindow):
    """Main dashboard window"""
    
    logout_requested = pyqtSignal()
    
    def __init__(self, api_client: APIClient, user_data: dict, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.user_data = user_data
        log_window_event("DashboardWindow", "initializing", {
            "user_id": user_data.get('id'),
            "user_name": user_data.get('name')
        })
        self.initUI()
        self.load_dashboard_data()
        log_window_event("DashboardWindow", "initialization_complete")
    
    def initUI(self):
        """Initialize dashboard UI"""
        self.setWindowTitle('Finance Manager - Dashboard')
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create sidebar
        self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Create content area
        self.create_content_area()
        main_layout.addWidget(self.content_area, stretch=1)
        
        # Apply styling
        self.apply_styles()
        
        # Connect navigation after everything is created
        self.nav_list.currentItemChanged.connect(self.on_nav_changed)
        
        # Set initial page after everything is created
        self.nav_list.setCurrentRow(0)
        self.content_area.setCurrentWidget(self.overview_page)
    
    def create_sidebar(self):
        """Create navigation sidebar"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setFrameStyle(QFrame.StyledPanel)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # User info section
        user_frame = QFrame()
        user_frame.setFixedHeight(80)
        user_layout = QVBoxLayout(user_frame)
        
        user_name = QLabel(f"Welcome, {self.user_data.get('name', 'User')}")
        user_name_font = QFont()
        user_name_font.setPointSize(14)
        user_name_font.setBold(True)
        user_name.setFont(user_name_font)
        user_name.setAlignment(Qt.AlignCenter)
        
        user_email = QLabel(self.user_data.get('email', ''))
        user_email.setAlignment(Qt.AlignCenter)
        user_email.setStyleSheet("color: #666; font-size: 12px;")
        
        user_layout.addWidget(user_name)
        user_layout.addWidget(user_email)
        
        sidebar_layout.addWidget(user_frame)
        
        # Navigation list
        self.nav_list = QListWidget()
        self.nav_list.setFrameStyle(QFrame.NoFrame)
        
        # Navigation items
        nav_items = [
            ('Overview', 'overview'),
            ('Transactions', 'transactions'),
            ('Categories', 'categories'),
            ('Reports', 'reports'),
            ('Settings', 'settings')
        ]
        
        for text, data in nav_items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, data)
            self.nav_list.addItem(item)
        
        sidebar_layout.addWidget(self.nav_list)
        
        # Logout button
        self.logout_btn = QPushButton('Logout')
        self.logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(self.logout_btn)
    
    def create_content_area(self):
        """Create main content area"""
        self.content_area = QStackedWidget()
        
        # Create pages
        self.overview_page = self.create_overview_page()
        self.transactions_page = self.create_transactions_page()
        self.categories_page = self.create_categories_page()
        self.reports_page = self.create_reports_page()
        self.settings_page = self.create_settings_page()
        
        # Add pages to stack
        self.content_area.addWidget(self.overview_page)
        self.content_area.addWidget(self.transactions_page)
        self.content_area.addWidget(self.categories_page)
        self.content_area.addWidget(self.reports_page)
        self.content_area.addWidget(self.settings_page)
    
    def create_overview_page(self):
        """Create overview/dashboard page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Page title
        title = QLabel('Financial Overview')
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Summary cards
        cards_layout = QGridLayout()
        
        # Create summary cards
        self.balance_card = self.create_summary_card('Total Balance', '$0.00', '#28a745')
        self.income_card = self.create_summary_card('Monthly Income', '$0.00', '#17a2b8')
        self.expenses_card = self.create_summary_card('Monthly Expenses', '$0.00', '#dc3545')
        self.savings_card = self.create_summary_card('Savings Rate', '0%', '#6f42c1')
        
        cards_layout.addWidget(self.balance_card, 0, 0)
        cards_layout.addWidget(self.income_card, 0, 1)
        cards_layout.addWidget(self.expenses_card, 1, 0)
        cards_layout.addWidget(self.savings_card, 1, 1)
        
        layout.addLayout(cards_layout)
        
        # Recent transactions
        recent_frame = QFrame()
        recent_frame.setFrameStyle(QFrame.StyledPanel)
        recent_layout = QVBoxLayout(recent_frame)
        
        recent_title = QLabel('Recent Transactions')
        recent_title_font = QFont()
        recent_title_font.setPointSize(16)
        recent_title_font.setBold(True)
        recent_title.setFont(recent_title_font)
        recent_layout.addWidget(recent_title)
        
        self.recent_transactions_list = QListWidget()
        self.recent_transactions_list.addItem('Loading transactions...')
        recent_layout.addWidget(self.recent_transactions_list)
        
        layout.addWidget(recent_frame)
        
        return page
    
    def create_summary_card(self, title: str, value: str, color: str):
        """Create a summary card widget"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setFixedHeight(120)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 14px; color: #666;")
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_font = QFont()
        value_font.setPointSize(18)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
    
    def create_transactions_page(self):
        """Create transactions page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel('Transactions')
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Add transaction button
        add_btn = QPushButton('Add Transaction')
        add_btn.setMaximumWidth(150)
        add_btn.clicked.connect(self.add_transaction)
        layout.addWidget(add_btn)
        
        # Transactions list
        self.transactions_list = QListWidget()
        self.transactions_list.addItem('Loading transactions...')
        layout.addWidget(self.transactions_list)
        
        return page
    
    def create_categories_page(self):
        """Create categories page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel('Categories')
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        content = QLabel('Category management will be implemented here.')
        content.setAlignment(Qt.AlignCenter)
        layout.addWidget(content)
        
        return page
    
    def create_reports_page(self):
        """Create reports page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel('Reports')
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        content = QLabel('Financial reports and charts will be implemented here.')
        content.setAlignment(Qt.AlignCenter)
        layout.addWidget(content)
        
        return page
    
    def create_settings_page(self):
        """Create settings page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel('Settings')
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        content = QLabel('Application settings will be implemented here.')
        content.setAlignment(Qt.AlignCenter)
        layout.addWidget(content)
        
        return page
    
    def on_nav_changed(self, current, previous):
        """Handle navigation change"""
        if current is None:
            return
        
        page_name = current.data(Qt.UserRole)
        log_user_action("navigate_to_page", "DashboardWindow", {"page": page_name})
        
        if page_name == 'overview':
            self.show_overview()
        elif page_name == 'transactions':
            self.show_transactions()
        elif page_name == 'categories':
            self.show_categories()
        elif page_name == 'reports':
            self.show_reports()
        elif page_name == 'settings':
            self.show_settings()
    
    def show_overview(self):
        """Show overview page"""
        self.content_area.setCurrentWidget(self.overview_page)
    
    def show_transactions(self):
        """Show transactions page"""
        self.content_area.setCurrentWidget(self.transactions_page)
        self.load_transactions()
    
    def show_categories(self):
        """Show categories page"""
        self.content_area.setCurrentWidget(self.categories_page)
    
    def show_reports(self):
        """Show reports page"""
        self.content_area.setCurrentWidget(self.reports_page)
    
    def show_settings(self):
        """Show settings page"""
        self.content_area.setCurrentWidget(self.settings_page)
    
    def load_dashboard_data(self):
        """Load dashboard summary data"""
        log_app_event("loading_dashboard_data", "DashboardWindow")
        try:
            # dummy data for now
            dashboard_data = {
                'total_balance': 5250.75,
                'monthly_income': 3500.00,
                'monthly_expenses': 2100.50,
                'savings_rate': 40.0
            }
            self.update_summary_cards(dashboard_data)
            log_app_event("dashboard_data_loaded", "DashboardWindow", dashboard_data)
            
            # Load recent transactions
            self.load_recent_transactions()
            
        except Exception as e:
            log_app_event("dashboard_data_load_error", "DashboardWindow", {"error": str(e)})
            QMessageBox.warning(self, 'Error', f'Failed to load dashboard data: {str(e)}')
    
    def update_summary_cards(self, data):
        """Update summary card values"""
        self.balance_card.value_label.setText(f"${data['total_balance']:,.2f}")
        self.income_card.value_label.setText(f"${data['monthly_income']:,.2f}")
        self.expenses_card.value_label.setText(f"${data['monthly_expenses']:,.2f}")
        self.savings_card.value_label.setText(f"{data['savings_rate']:.1f}%")
    
    def load_recent_transactions(self):
        """Load recent transactions"""
        try:
            # dummy data for now
            self.recent_transactions_list.clear()
            
            recent_transactions = [
                "Grocery Store - $85.50",
                "Salary Deposit - $3500.00",
                "Gas Station - $45.00",
                "Restaurant - $28.75",
                "Online Shopping - $125.99"
            ]
            
            for transaction in recent_transactions:
                self.recent_transactions_list.addItem(transaction)
                
        except Exception as e:
            self.recent_transactions_list.clear()
            self.recent_transactions_list.addItem(f'Error loading transactions: {str(e)}')
    
    def load_transactions(self):
        """Load full transactions list"""
        try:
            # dummy data for now
            self.transactions_list.clear()
            
            transactions = [
                "2024-10-01 - Grocery Store - $85.50 - Food",
                "2024-10-01 - Salary Deposit - $3500.00 - Income",
                "2024-09-30 - Gas Station - $45.00 - Transportation",
                "2024-09-29 - Restaurant - $28.75 - Food",
                "2024-09-28 - Online Shopping - $125.99 - Shopping",
                "2024-09-27 - Electricity Bill - $120.00 - Utilities",
                "2024-09-26 - Coffee Shop - $12.50 - Food",
                "2024-09-25 - Gym Membership - $50.00 - Health"
            ]
            
            for transaction in transactions:
                self.transactions_list.addItem(transaction)
                
        except Exception as e:
            self.transactions_list.clear()
            self.transactions_list.addItem(f'Error loading transactions: {str(e)}')
    
    def add_transaction(self):
        """Add new transaction (placeholder)"""
        log_user_action("add_transaction_clicked", "DashboardWindow")
        QMessageBox.information(
            self,
            'Add Transaction',
            'Transaction form will be implemented in the next iteration.'
        )
    
    def logout(self):
        """Handle logout"""
        log_user_action("logout_clicked", "DashboardWindow")
        self.api_client.logout()
        self.logout_requested.emit()
        self.close()
        log_window_event("DashboardWindow", "closed_after_logout")
    
    def apply_styles(self):
        """Apply stylesheet to dashboard"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QFrame#sidebar {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
            
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            
            QListWidget::item {
                padding: 12px 16px;
                color: #ecf0f1;
                border-bottom: 1px solid #34495e;
            }
            
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            
            QListWidget::item:hover {
                background-color: #34495e;
            }
            
            QPushButton {
                padding: 10px 16px;
                font-size: 14px;
                border: none;
                border-radius: 4px;
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #21618c;
            }
            
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin: 4px;
            }
            
            QStackedWidget {
                background-color: white;
                padding: 20px;
            }
        """)
        
        # Set sidebar ID for styling
        self.sidebar.setObjectName('sidebar')