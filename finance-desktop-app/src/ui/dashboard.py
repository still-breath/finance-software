"""
Dashboard UI components for Finance Desktop Application
Main dashboard with navigation and content areas
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QStackedWidget, QListWidget, QListWidgetItem,
                           QLabel, QPushButton, QFrame, QScrollArea,
                           QGridLayout, QSizePolicy, QMessageBox, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPainter, QBrush, QPen
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.client import APIClient
from utils.logger import log_user_action, log_app_event, log_window_event
from .transactions import TransactionListWidget

class MetricCard(QFrame):
    """Custom metric card widget"""
    
    def __init__(self, title, value, icon, color="#007bff", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setFixedHeight(120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Apply shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(8)
        
        # Title with icon
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont('Open Sans', 20))
        icon_label.setStyleSheet(f"color: {color};")
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Open Sans', 11))
        title_label.setStyleSheet("color: #8b95a7; font-weight: 500;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont('Open Sans', 24, QFont.Bold))
        self.value_label.setStyleSheet(f"color: #2c3e50;")
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            MetricCard {
                background-color: white;
                border-radius: 12px;
            }
        """)


class DashboardWindow(QMainWindow):
    """Main dashboard window"""
    
    logout_requested = pyqtSignal()
    
    def __init__(self, api_client: APIClient, user_data: dict, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.user_data = user_data
        
        print("DashboardWindow: Starting initialization...")
        
        try:
            log_window_event("DashboardWindow", "initializing", {
                "user_id": user_data.get('id'),
                "user_name": user_data.get('name')
            })
            self.setAttribute(Qt.WA_QuitOnClose, False)
            self.setWindowFlags(Qt.Window)
            
            print("DashboardWindow: Calling initUI...")
            self.initUI()
            
            print("DashboardWindow: Loading dashboard data...")
            self.load_dashboard_data()
            
            log_window_event("DashboardWindow", "initialization_complete")
            print("DashboardWindow: Initialization complete")
            
        except Exception as e:
            print(f"DashboardWindow: Error in init: {e}")
            log_window_event("DashboardWindow", "initialization_error", {"error": str(e)})
            raise
    
    def initUI(self):
        """Initialize dashboard UI"""
        print("DashboardWindow: Setting window properties...")
        self.setWindowTitle('Dashboard - Finance Manager')
        self.setGeometry(100, 100, 1300, 750)

        self.setMinimumSize(1200, 700)
        self.setMaximumSize(1500, 900)
        
        # Ensure window is visible and on top
        self.setWindowState(Qt.WindowNoState)
        self.activateWindow()
        self.raise_()
        
        print("DashboardWindow: Creating central widget...")
        # Create central widget with background
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #f0f2f5;")
        self.setCentralWidget(central_widget)
        
        print("DashboardWindow: Creating main layout...")
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        print("DashboardWindow: Creating sidebar...")
        # Create sidebar
        self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        print("DashboardWindow: Creating content wrapper...")
        # Create content area with padding
        content_wrapper = QWidget()
        content_wrapper.setStyleSheet("background-color: #f0f2f5;")
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        # Create header
        self.create_header()
        content_layout.addWidget(self.header_widget)
        
        # Create scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setStyleSheet("background-color: transparent;")
        
        # Create content area
        self.create_content_area()
        scroll_area.setWidget(self.content_area)
        content_layout.addWidget(scroll_area, stretch=1)
        
        main_layout.addWidget(content_wrapper, stretch=1)
        
        # Apply styling
        self.apply_styles()
        
        # Connect navigation
        self.nav_list.currentItemChanged.connect(self.on_nav_changed)
        
        # Set initial page
        self.nav_list.setCurrentRow(0)
        self.content_area.setCurrentWidget(self.overview_page)
    
    def create_sidebar(self):
        """Create navigation sidebar"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setFrameStyle(QFrame.NoFrame)
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: none;
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # User profile section
        user_container = QWidget()
        user_container.setStyleSheet("background-color: #34495e; border-bottom: 1px solid #1a252f;")
        user_layout = QVBoxLayout(user_container)
        user_layout.setSpacing(5)
        user_layout.setContentsMargins(15, 15, 15, 15)
        
        # Avatar
        avatar_label = QLabel('👤')
        avatar_label.setFont(QFont('Open Sans', 32))
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setStyleSheet("color: white;")
        
        user_layout.addWidget(avatar_label)
        
        # User name
        user_name = QLabel(self.user_data.get('name', 'User').upper())
        user_name.setFont(QFont('Open Sans', 14, QFont.Bold))
        user_name.setStyleSheet("color: white;")
        user_name.setAlignment(Qt.AlignCenter)
        
        # User email
        user_email = QLabel(self.user_data.get('email', 'user@example.com'))
        user_email.setFont(QFont('Open Sans', 10))
        user_email.setStyleSheet("color: #95a5a6;")
        user_email.setAlignment(Qt.AlignCenter)
        
        user_layout.addWidget(user_name)
        user_layout.addWidget(user_email)
        
        sidebar_layout.addWidget(user_container)
        
        # Navigation items
        self.nav_list = QListWidget()
        self.nav_list.setFrameStyle(QFrame.NoFrame)
        self.nav_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                color: #bdc3c7;
                padding: 18px 25px;
                border: none;
                font-family: 'Open Sans';
                font-size: 13px;
            }
            QListWidget::item:selected {
                background-color: #1a252f;
                color: white;
                border-left: 4px solid #3498db;
            }
            QListWidget::item:hover {
                background-color: #34495e;
                color: white;
            }
        """)
        
        nav_items = [
            ('🏠  Dashboard', 'overview'),
            ('�  Transactions', 'transactions'),
            ('✉️  Messages', 'messages'),
            ('🔔  Notifications', 'notifications'),
            ('📍  Location', 'location'),
            ('📊  Reports', 'reports')
        ]
        
        for text, data in nav_items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, data)
            item.setFont(QFont('Open Sans', 13))
            self.nav_list.addItem(item)
        
        sidebar_layout.addWidget(self.nav_list)
        
        # Logout button
        self.logout_btn = QPushButton('🚪  Logout')
        self.logout_btn.setFont(QFont('Open Sans', 12))
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #95a5a6;
                border: none;
                padding: 18px 25px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #34495e;
                color: white;
            }
        """)
        self.logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(self.logout_btn)
    
    def create_header(self):
        """Create header with title"""
        self.header_widget = QWidget()
        self.header_widget.setFixedHeight(70)
        self.header_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 14px;
            }
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.header_widget.setGraphicsEffect(shadow)
        
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(24, 12, 24, 12)
        
        # Title
        self.page_title = QLabel('Dashboard')
        self.page_title.setFont(QFont('Open Sans', 22, QFont.Bold))
        self.page_title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(self.page_title)
        header_layout.addStretch()
    
    def create_content_area(self):
        """Create main content area"""
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background-color: transparent;")
        
        # Create pages
        self.overview_page = self.create_overview_page()
        self.transactions_page = self.create_transactions_page()
        self.messages_page = self.create_placeholder_page('✉️ Messages', 'Messaging features coming soon')
        self.notifications_page = self.create_placeholder_page('🔔 Notifications', 'Notifications coming soon')
        self.location_page = self.create_placeholder_page('📍 Location', 'Location features coming soon')
        self.reports_page = self.create_reports_page()
        
        # Add pages
        self.content_area.addWidget(self.overview_page)
        self.content_area.addWidget(self.transactions_page)
        self.content_area.addWidget(self.messages_page)
        self.content_area.addWidget(self.notifications_page)
        self.content_area.addWidget(self.location_page)
        self.content_area.addWidget(self.reports_page)
    
    def create_overview_page(self):
        """Create overview page with metrics"""
        page = QWidget()
        page.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(25)
        
        # Metrics cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        self.earning_card = MetricCard('Total Income', 'IDR 0', '💵', '#27ae60')
        self.share_card = MetricCard('Transactions', '0', '�', '#3498db')
        self.likes_card = MetricCard('Categories', '0', '�', '#e74c3c')
        self.rating_card = MetricCard('Avg. Amount', 'IDR 0', '📊', '#f39c12')
        
        cards_layout.addWidget(self.earning_card)
        cards_layout.addWidget(self.share_card)
        cards_layout.addWidget(self.likes_card)
        cards_layout.addWidget(self.rating_card)
        
        layout.addLayout(cards_layout)
        
        # Charts row
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        # Result chart
        result_widget = self.create_result_chart()
        charts_layout.addWidget(result_widget, 2)
        
        # Stats widget
        stats_widget = self.create_stats_widget()
        charts_layout.addWidget(stats_widget, 1)
        
        layout.addLayout(charts_layout)
        
        # Bottom row
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        
        wave_chart = self.create_wave_chart()
        bottom_layout.addWidget(wave_chart, 2)
        
        calendar_widget = self.create_calendar_widget()
        bottom_layout.addWidget(calendar_widget, 1)
        
        layout.addLayout(bottom_layout)
        
        return page
    
    def create_result_chart(self):
        """Create bar chart widget"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.NoFrame)
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        widget.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel('Result')
        title.setFont(QFont('Open Sans', 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        
        check_btn = QPushButton('Check Now')
        check_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-family: 'Open Sans';
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(check_btn)
        
        layout.addLayout(header_layout)
        
        # Chart placeholder
        chart_label = QLabel('📊 Monthly Performance Chart')
        chart_label.setAlignment(Qt.AlignCenter)
        chart_label.setMinimumHeight(200)
        chart_label.setStyleSheet("""
            background-color: #f8f9fa;
            border-radius: 8px;
            color: #6c757d;
            font-size: 14px;
            font-family: 'Open Sans';
        """)
        
        layout.addWidget(chart_label)
        
        return widget
    
    def create_stats_widget(self):
        """Create stats widget"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.NoFrame)
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        widget.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Percentage
        percent_label = QLabel('45%')
        percent_label.setAlignment(Qt.AlignCenter)
        percent_label.setFont(QFont('Open Sans', 36, QFont.Bold))
        percent_label.setStyleSheet("color: #2c3e50;")
        
        layout.addWidget(percent_label)
        
        # Legend items
        for i in range(4):
            item = QLabel(f'• Item {i+1}')
            item.setFont(QFont('Open Sans', 11))
            item.setStyleSheet("color: #6c757d; padding: 5px 0;")
            layout.addWidget(item)
        
        # Check button
        check_btn = QPushButton('Check Now')
        check_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-family: 'Open Sans';
                font-size: 12px;
                font-weight: 600;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        
        layout.addWidget(check_btn)
        
        return widget
    
    def create_wave_chart(self):
        """Create wave chart widget"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.NoFrame)
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        widget.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 12, 20, 20)  # Top margin lebih kecil
        layout.setSpacing(8)  # Spacing antara legend dan chart
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(30)
        
        for color, text in [('#f39c12', 'Lorem ipsum'), ('#2c3e50', 'Dolor Amet')]:
            item_layout = QHBoxLayout()
            item_layout.setSpacing(8)
            
            dot = QLabel('●')
            dot.setStyleSheet(f"color: {color}; font-size: 16px;")
            
            label = QLabel(text)
            label.setFont(QFont('Open Sans', 11))
            label.setStyleSheet("color: #6c757d;")
            
            item_layout.addWidget(dot)
            item_layout.addWidget(label)
            
            legend_layout.addLayout(item_layout)
        
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        # Wave placeholder
        wave_label = QLabel('🌊 Wave Chart')
        wave_label.setAlignment(Qt.AlignCenter)
        wave_label.setMinimumHeight(180)
        wave_label.setStyleSheet("""
            background-color: #f8f9fa;
            border-radius: 8px;
            color: #6c757d;
            font-size: 14px;
            font-family: 'Open Sans';
        """)
        
        layout.addWidget(wave_label)
        
        return widget
    
    def create_calendar_widget(self):
        """Create calendar widget"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.NoFrame)
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        widget.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Calendar icon
        calendar_label = QLabel('📅')
        calendar_label.setAlignment(Qt.AlignCenter)
        calendar_label.setFont(QFont('Open Sans', 48))
        
        layout.addWidget(calendar_label)
        
        # Month
        month_label = QLabel('October 2025')
        month_label.setAlignment(Qt.AlignCenter)
        month_label.setFont(QFont('Open Sans', 14, QFont.Bold))
        month_label.setStyleSheet("color: #2c3e50;")
        
        layout.addWidget(month_label)
        
        # Calendar grid
        grid = QGridLayout()
        grid.setSpacing(5)
        
        # Days header
        days = ['S', 'M', 'T', 'W', 'T', 'F', 'S']
        for i, day in enumerate(days):
            label = QLabel(day)
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont('Open Sans', 10))
            label.setStyleSheet("color: #95a5a6;")
            grid.addWidget(label, 0, i)
        
        # Sample dates
        dates = [
            ['', '', '1', '2', '3', '4', '5'],
            ['6', '7', '8', '9', '10', '11', '12'],
            ['13', '14', '15', '16', '17', '18', '19'],
            ['20', '21', '22', '23', '24', '25', '26'],
            ['27', '28', '29', '30', '31', '', '']
        ]
        
        for row, week in enumerate(dates, 1):
            for col, date in enumerate(week):
                if date:
                    label = QLabel(date)
                    label.setAlignment(Qt.AlignCenter)
                    label.setFont(QFont('Open Sans', 10))
                    label.setFixedSize(30, 30)
                    
                    if date in ['3', '11', '18', '24']:
                        label.setStyleSheet("""
                            background-color: #2c3e50;
                            color: white;
                            border-radius: 15px;
                        """)
                    else:
                        label.setStyleSheet("color: #2c3e50;")
                    
                    grid.addWidget(label, row, col)
        
        layout.addLayout(grid)
        
        return widget
    
    def create_transactions_page(self):
        try:
            # Create TransactionListWidget which handles all transaction CRUD operations
            transaction_widget = TransactionListWidget(self.api_client)
            
            # Wrap in a container for consistent styling
            page = QWidget()
            page.setStyleSheet("background-color: transparent;")
            layout = QVBoxLayout(page)
            layout.setContentsMargins(0, 20, 0, 0)
            layout.addWidget(transaction_widget)
            
            return page
            
        except Exception as e:
            log_app_event("transactions_page_error", "DashboardWindow", {"error": str(e)})
            # Fallback to placeholder if there's an error
            return self.create_placeholder_page('💳 Transactions', f'Error loading transactions: {str(e)}')
    
    def create_reports_page(self):
        """Create comprehensive reports and analytics page"""
        try:
            page = QWidget()
            page.setStyleSheet("background-color: transparent;")
            main_layout = QVBoxLayout(page)
            main_layout.setContentsMargins(0, 20, 0, 0)
            main_layout.setSpacing(20)
            
            # Page title
            title = QLabel("📊 Financial Reports & Analytics")
            title.setFont(QFont('Segoe UI', 24, QFont.Bold))
            title.setStyleSheet("color: #1a202c; margin-bottom: 10px;")
            main_layout.addWidget(title)
            
            # Create scroll area for all reports
            scroll = QScrollArea()
            scroll.setStyleSheet("""
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                QScrollBar:vertical {
                    background-color: #f1f5f9;
                    width: 8px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background-color: #cbd5e1;
                    min-height: 20px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #94a3b8;
                }
            """)
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            # Content widget for scroll area
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setSpacing(20)
            
            # Top row - Summary cards
            summary_layout = QHBoxLayout()
            summary_layout.setSpacing(20)
            
            # Monthly Overview Card
            monthly_card = self.create_monthly_overview_card()
            summary_layout.addWidget(monthly_card)
            
            # Category Distribution Card
            category_card = self.create_category_distribution_card()
            summary_layout.addWidget(category_card)
            
            content_layout.addLayout(summary_layout)
            
            # Second row - Charts
            charts_layout = QHBoxLayout()
            charts_layout.setSpacing(20)
            
            # Monthly Trend Chart
            trend_card = self.create_monthly_trend_card()
            charts_layout.addWidget(trend_card)
            
            # AI Prediction Stats Card
            ai_stats_card = self.create_ai_stats_card()
            charts_layout.addWidget(ai_stats_card)
            
            content_layout.addLayout(charts_layout)
            
            # Third row - Detailed Analytics
            details_layout = QHBoxLayout()
            details_layout.setSpacing(20)
            
            # Top Categories Table
            top_categories_card = self.create_top_categories_card()
            details_layout.addWidget(top_categories_card)
            
            # Recent Transactions Summary
            recent_summary_card = self.create_recent_summary_card()
            details_layout.addWidget(recent_summary_card)
            
            content_layout.addLayout(details_layout)
            
            # Add stretch at the end
            content_layout.addStretch()
            
            scroll.setWidget(content_widget)
            main_layout.addWidget(scroll)
            
            # Load data for all cards
            self.load_reports_data()
            
            return page
            
        except Exception as e:
            log_app_event("reports_page_error", "DashboardWindow", {"error": str(e)})
            return self.create_placeholder_page('📊 Reports', f'Error loading reports: {str(e)}')
    
    def create_placeholder_page(self, title: str, subtitle: str):
        """Create placeholder page"""
        page = QWidget()
        page.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 20, 0, 0)
        
        card = QFrame()
        card.setFrameStyle(QFrame.NoFrame)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Open Sans', 20, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont('Open Sans', 13))
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-top: 10px;")
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(subtitle_label)
        card_layout.addStretch()
        
        layout.addWidget(card)
        
        return page
    
    def on_nav_changed(self, current, previous):
        """Handle navigation change"""
        if current:
            page_name = current.data(Qt.UserRole)
            log_user_action("navigation_changed", "DashboardWindow", {"page": page_name})
            
            # Update page title
            page_titles = {
                'overview': 'Dashboard',
                'transactions': 'Transactions',
                'messages': 'Messages',
                'notifications': 'Notifications',
                'location': 'Location',
                'reports': 'Reports'
            }
            self.page_title.setText(page_titles.get(page_name, 'Dashboard'))
            
            # Switch page
            page_map = {
                'overview': 0,
                'transactions': 1,
                'messages': 2,
                'notifications': 3,
                'location': 4,
                'reports': 5
            }
            
            if page_name in page_map:
                self.content_area.setCurrentIndex(page_map[page_name])
                
                # Load reports data when navigating to reports page
                if page_name == 'reports':
                    self.load_reports_data()
    
    def apply_styles(self):
        """Apply global styles"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
        """)
    
    def load_dashboard_data(self):
        log_app_event("dashboard_data_load_started", "DashboardWindow")
        
        # Load transaction summary for metrics cards
        try:
            summary_data = self.api_client.get_transaction_summary()
            self.update_metrics_cards(summary_data)
        except Exception as e:
            log_app_event("dashboard_summary_error", "DashboardWindow", {"error": str(e)})
            print(f"Failed to load transaction summary: {e}")
        
        # Load monthly stats for charts
        try:
            monthly_data = self.api_client.get_monthly_stats()
            self.update_charts_data(monthly_data)
        except Exception as e:
            log_app_event("dashboard_monthly_error", "DashboardWindow", {"error": str(e)})
            print(f"Failed to load monthly stats: {e}")
    
    def update_metrics_cards(self, summary_data):
        """Update metrics cards with real data"""
        try:
            if not summary_data:
                return
            
            # Update earnings card
            total_income = summary_data.get('total_income', 0)
            self.earning_card.value_label.setText(f"IDR {total_income:,.0f}")
            
            # Update transaction count
            total_transactions = summary_data.get('total_transactions', 0)
            self.share_card.value_label.setText(str(total_transactions))
            
            # Update categories count
            categories_count = summary_data.get('categories_count', 0)
            self.likes_card.value_label.setText(str(categories_count))
            
            # Update average transaction amount
            avg_amount = summary_data.get('average_amount', 0)
            self.rating_card.value_label.setText(f"IDR {avg_amount:,.0f}")
            
            log_app_event("metrics_updated", "DashboardWindow", summary_data)
            
        except Exception as e:
            log_app_event("metrics_update_error", "DashboardWindow", {"error": str(e)})
    
    def update_charts_data(self, monthly_data):
        """Update charts with monthly data"""
        try:
            raw = []
            if not monthly_data:
                return
            if 'monthly_stats' in monthly_data:
                raw = monthly_data.get('monthly_stats', [])
            elif 'months' in monthly_data:
                raw = monthly_data.get('months', [])
            else:
                if isinstance(monthly_data, list):
                    raw = monthly_data

            cleaned = []
            for item in raw:
                month_key = item.get('month') or item.get('period') or item.get('date')
                if not month_key:
                    continue
                # Accept formats YYYY-MM or YYYY-MM-DD
                month_id = month_key[:7]
                income = item.get('income') or item.get('total_income') or 0
                expense = item.get('expense') or item.get('total_expense') or 0
                balance = item.get('balance') or (income - abs(expense))
                cleaned.append({
                    'month': month_id,
                    'income': float(income),
                    'expense': float(expense),
                    'balance': float(balance)
                })

            cleaned.sort(key=lambda x: x['month'])

            for i, row in enumerate(cleaned):
                if i == 0:
                    row['income_delta'] = 0
                    row['expense_delta'] = 0
                    row['balance_delta'] = 0
                else:
                    prev = cleaned[i-1]
                    row['income_delta'] = row['income'] - prev['income']
                    row['expense_delta'] = row['expense'] - prev['expense']
                    row['balance_delta'] = row['balance'] - prev['balance']

            if cleaned:
                highest_income = max(cleaned, key=lambda r: r['income'])
                highest_expense = max(cleaned, key=lambda r: r['expense'])
                latest = cleaned[-1]
                trend_dir = 'up' if latest['balance_delta'] > 0 else ('flat' if latest['balance_delta'] == 0 else 'down')

                while self.trend_info_layout.count():
                    item = self.trend_info_layout.takeAt(0)
                    w = item.widget()
                    if w:
                        w.deleteLater()
                def fmt_month(m):
                    try:
                        year, month = m.split('-')
                        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                        return f"{month_names[int(month)-1]} {year}"
                    except Exception:
                        return m
                def colorize(val):
                    if val > 0:
                        return f"<span style='color:#059669'>+{val:,.0f}</span>"
                    if val < 0:
                        return f"<span style='color:#dc2626'>{val:,.0f}</span>"
                    return f"<span style='color:#64748b'>0</span>"
                # Build labels
                summary_label = QLabel(f"Latest Month: <b>{fmt_month(latest['month'])}</b> Balance <b>IDR {latest['balance']:,.0f}</b> (Δ {colorize(latest['balance_delta'])})")
                summary_label.setFont(QFont('Segoe UI', 11))
                summary_label.setStyleSheet("color:#374151; margin-bottom:4px;")
                self.trend_info_layout.addWidget(summary_label)

                income_label = QLabel(f"Income: IDR {latest['income']:,.0f} (Δ {colorize(latest['income_delta'])}) – Highest: {fmt_month(highest_income['month'])} (IDR {highest_income['income']:,.0f})")
                income_label.setFont(QFont('Segoe UI', 10))
                income_label.setStyleSheet("color:#1d4ed8; margin:2px 0;")
                self.trend_info_layout.addWidget(income_label)

                expense_label = QLabel(f"Expenses: IDR {latest['expense']:,.0f} (Δ {colorize(latest['expense_delta'])}) – Peak: {fmt_month(highest_expense['month'])} (IDR {highest_expense['expense']:,.0f})")
                expense_label.setFont(QFont('Segoe UI', 10))
                expense_label.setStyleSheet("color:#dc2626; margin:2px 0;")
                self.trend_info_layout.addWidget(expense_label)

                direction_map = {'up': ('📈 Improving balance', '#059669'), 'down': ('📉 Declining balance', '#dc2626'), 'flat': ('➖ Stable balance', '#64748b')}
                dir_text, dir_color = direction_map[trend_dir]
                dir_label = QLabel(dir_text)
                dir_label.setFont(QFont('Segoe UI', 10, QFont.Bold))
                dir_label.setStyleSheet(f"color:{dir_color}; margin-top:6px;")
                self.trend_info_layout.addWidget(dir_label)

                # Optional compact table style summary (raw rows)
                html_rows = []
                for r in cleaned[-6:]:
                    html_rows.append(
                        f"<tr><td style='padding:2px 8px'>{fmt_month(r['month'])}</td>"
                        f"<td style='padding:2px 8px;text-align:right'>{r['income']:,.0f}</td>"
                        f"<td style='padding:2px 8px;text-align:right'>{r['expense']:,.0f}</td>"
                        f"<td style='padding:2px 8px;text-align:right'>{r['balance']:,.0f}</td>" 
                        f"<td style='padding:2px 8px;text-align:right'>{'+' if r['balance_delta']>0 else ''}{r['balance_delta']:,.0f}</td></tr>"
                    )
                table_label = QLabel(
                    "<div style='margin-top:8px'><b>Recent 6 Months</b><br><table style='border-collapse:collapse;font-size:11px;color:#374151'>"
                    "<tr style='background:#f1f5f9'><th style='padding:2px 8px;text-align:left'>Month</th><th style='padding:2px 8px'>Income</th><th style='padding:2px 8px'>Expense</th><th style='padding:2px 8px'>Balance</th><th style='padding:2px 8px'>Δ Bal</th></tr>"
                    + "".join(html_rows) + "</table></div>"
                )
                table_label.setTextFormat(Qt.RichText)
                self.trend_info_layout.addWidget(table_label)

            log_app_event("charts_data_loaded", "DashboardWindow", {"months": len(cleaned)})
        except Exception as e:
            log_app_event("charts_update_error", "DashboardWindow", {"error": str(e)})
    
    def create_monthly_overview_card(self):
        """Create monthly overview summary card"""
        card = QFrame()
        card.setFrameStyle(QFrame.NoFrame)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📅 This Month Overview")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setStyleSheet("color: #1f2937; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # Create labels for data
        self.monthly_income_label = QLabel("Income: Loading...")
        self.monthly_expense_label = QLabel("Expenses: Loading...")
        self.monthly_balance_label = QLabel("Balance: Loading...")
        self.monthly_transactions_label = QLabel("Transactions: Loading...")
        
        for label in [self.monthly_income_label, self.monthly_expense_label, 
                     self.monthly_balance_label, self.monthly_transactions_label]:
            label.setFont(QFont('Segoe UI', 12))
            label.setStyleSheet("color: #4b5563; margin: 3px 0;")
            layout.addWidget(label)
        
        layout.addStretch()
        return card
    
    def create_category_distribution_card(self):
        """Create category distribution card"""
        card = QFrame()
        card.setFrameStyle(QFrame.NoFrame)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🎯 Category Distribution")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setStyleSheet("color: #1f2937; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # Container for category stats
        self.category_stats_layout = QVBoxLayout()
        layout.addLayout(self.category_stats_layout)
        
        # Loading placeholder
        loading_label = QLabel("Loading category data...")
        loading_label.setFont(QFont('Segoe UI', 11))
        loading_label.setStyleSheet("color: #6b7280;")
        self.category_stats_layout.addWidget(loading_label)
        
        layout.addStretch()
        return card
    
    def create_monthly_trend_card(self):
        """Create monthly trend chart card"""
        card = QFrame()
        card.setFrameStyle(QFrame.NoFrame)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📈 Monthly Trends")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setStyleSheet("color: #1f2937; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # Container for trend info
        self.trend_info_layout = QVBoxLayout()
        layout.addLayout(self.trend_info_layout)
        
        # Loading placeholder
        loading_label = QLabel("Loading trend data...")
        loading_label.setFont(QFont('Segoe UI', 11))
        loading_label.setStyleSheet("color: #6b7280;")
        self.trend_info_layout.addWidget(loading_label)
        
        layout.addStretch()
        return card
    
    def create_ai_stats_card(self):
        """Create AI prediction statistics card"""
        card = QFrame()
        card.setFrameStyle(QFrame.NoFrame)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🤖 AI Categorization Stats")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setStyleSheet("color: #1f2937; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # Container for AI stats
        self.ai_stats_layout = QVBoxLayout()
        layout.addLayout(self.ai_stats_layout)
        
        # Loading placeholder
        loading_label = QLabel("Loading AI statistics...")
        loading_label.setFont(QFont('Segoe UI', 11))
        loading_label.setStyleSheet("color: #6b7280;")
        self.ai_stats_layout.addWidget(loading_label)
        
        layout.addStretch()
        return card
    
    def create_top_categories_card(self):
        """Create top spending categories card"""
        card = QFrame()
        card.setFrameStyle(QFrame.NoFrame)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🏆 Top Spending Categories")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setStyleSheet("color: #1f2937; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # Container for top categories
        self.top_categories_layout = QVBoxLayout()
        layout.addLayout(self.top_categories_layout)
        
        # Loading placeholder
        loading_label = QLabel("Loading top categories...")
        loading_label.setFont(QFont('Segoe UI', 11))
        loading_label.setStyleSheet("color: #6b7280;")
        self.top_categories_layout.addWidget(loading_label)
        
        layout.addStretch()
        return card
    
    def create_recent_summary_card(self):
        """Create recent transactions summary card"""
        card = QFrame()
        card.setFrameStyle(QFrame.NoFrame)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("⏰ Recent Activity")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setStyleSheet("color: #1f2937; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # Container for recent summary
        self.recent_summary_layout = QVBoxLayout()
        layout.addLayout(self.recent_summary_layout)
        
        # Loading placeholder
        loading_label = QLabel("Loading recent activity...")
        loading_label.setFont(QFont('Segoe UI', 11))
        loading_label.setStyleSheet("color: #6b7280;")
        self.recent_summary_layout.addWidget(loading_label)
        
        layout.addStretch()
        return card
    
    def load_reports_data(self):
        """Load all data for reports page"""
        try:
            # Load monthly stats
            monthly_data = self.api_client.get_monthly_stats()
            self.update_monthly_overview(monthly_data)
            
            # Load category stats
            category_data = self.api_client.get_category_stats()
            self.update_category_distribution(category_data)
            self.update_ai_stats(category_data)
            self.update_top_categories(category_data)
            
            # Load recent transactions for summary
            transactions_data = self.api_client.get_transactions()
            self.update_recent_summary(transactions_data)
            
        except Exception as e:
            log_app_event("load_reports_data_error", "DashboardWindow", {"error": str(e)})
    
    def update_monthly_overview(self, data):
        """Update monthly overview card with data"""
        try:
            monthly_stats = data.get('monthly_stats', [])
            if monthly_stats:
                current_month = monthly_stats[0]  # Latest month
                income = current_month.get('income', 0)
                expense = current_month.get('expense', 0)
                balance = current_month.get('balance', 0)
                
                # Get transaction count from summary
                summary_data = self.api_client.get_transaction_summary()
                transaction_count = summary_data.get('summary', {}).get('transaction_count', 0)
                
                self.monthly_income_label.setText(f"💰 Income: Rp {income:,.0f}")
                self.monthly_income_label.setStyleSheet("color: #059669; font-weight: 600; margin: 3px 0;")
                
                self.monthly_expense_label.setText(f"💸 Expenses: Rp {expense:,.0f}")
                self.monthly_expense_label.setStyleSheet("color: #dc2626; font-weight: 600; margin: 3px 0;")
                
                balance_color = "#059669" if balance >= 0 else "#dc2626"
                self.monthly_balance_label.setText(f"📊 Balance: Rp {balance:,.0f}")
                self.monthly_balance_label.setStyleSheet(f"color: {balance_color}; font-weight: 600; margin: 3px 0;")
                
                self.monthly_transactions_label.setText(f"🧾 Transactions: {transaction_count}")
                self.monthly_transactions_label.setStyleSheet("color: #4b5563; font-weight: 600; margin: 3px 0;")
            else:
                self.monthly_income_label.setText("💰 Income: Rp 0")
                self.monthly_expense_label.setText("💸 Expenses: Rp 0")
                self.monthly_balance_label.setText("📊 Balance: Rp 0")
                self.monthly_transactions_label.setText("🧾 Transactions: 0")
                
        except Exception as e:
            log_app_event("update_monthly_overview_error", "DashboardWindow", {"error": str(e)})
    
    def update_category_distribution(self, data):
        """Update category distribution card"""
        try:
            # Clear existing widgets
            while self.category_stats_layout.count():
                child = self.category_stats_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            categories = data.get('category_distribution', [])
            if categories:
                for i, category in enumerate(categories[:5]):  # Top 5 categories
                    name = category.get('category_name', 'Unknown')
                    amount = abs(category.get('total_amount', 0))
                    count = category.get('transaction_count', 0)
                    
                    # Create category item
                    item_widget = QWidget()
                    item_layout = QHBoxLayout(item_widget)
                    item_layout.setContentsMargins(0, 5, 0, 5)
                    
                    # Category info
                    info_label = QLabel(f"{name}")
                    info_label.setFont(QFont('Segoe UI', 11, QFont.Medium))
                    info_label.setStyleSheet("color: #374151;")
                    
                    # Amount and count
                    stats_label = QLabel(f"Rp {amount:,.0f} ({count} txn)")
                    stats_label.setFont(QFont('Segoe UI', 10))
                    stats_label.setStyleSheet("color: #6b7280;")
                    stats_label.setAlignment(Qt.AlignRight)
                    
                    item_layout.addWidget(info_label)
                    item_layout.addStretch()
                    item_layout.addWidget(stats_label)
                    
                    self.category_stats_layout.addWidget(item_widget)
            else:
                no_data_label = QLabel("No category data available")
                no_data_label.setFont(QFont('Segoe UI', 11))
                no_data_label.setStyleSheet("color: #9ca3af;")
                self.category_stats_layout.addWidget(no_data_label)
                
        except Exception as e:
            log_app_event("update_category_distribution_error", "DashboardWindow", {"error": str(e)})
    
    def update_ai_stats(self, data):
        """Update AI statistics card"""
        try:
            # Clear existing widgets
            while self.ai_stats_layout.count():
                child = self.ai_stats_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            prediction_methods = data.get('prediction_methods', [])
            total_predictions = sum(method.get('count', 0) for method in prediction_methods)
            
            if prediction_methods and total_predictions > 0:
                for method in prediction_methods:
                    method_name = method.get('method', 'unknown')
                    count = method.get('count', 0)
                    percentage = (count / total_predictions) * 100 if total_predictions > 0 else 0
                    
                    # Method display names
                    display_names = {
                        'ai_prediction': '🤖 AI Prediction',
                        'manual': '👤 Manual',
                        'default': '⚡ Default'
                    }
                    display_name = display_names.get(method_name, method_name.title())
                    
                    # Create method item
                    item_widget = QWidget()
                    item_layout = QHBoxLayout(item_widget)
                    item_layout.setContentsMargins(0, 3, 0, 3)
                    
                    method_label = QLabel(display_name)
                    method_label.setFont(QFont('Segoe UI', 11))
                    method_label.setStyleSheet("color: #374151;")
                    
                    stats_label = QLabel(f"{percentage:.1f}% ({count})")
                    stats_label.setFont(QFont('Segoe UI', 10, QFont.Medium))
                    stats_label.setStyleSheet("color: #6366f1;")
                    stats_label.setAlignment(Qt.AlignRight)
                    
                    item_layout.addWidget(method_label)
                    item_layout.addStretch()
                    item_layout.addWidget(stats_label)
                    
                    self.ai_stats_layout.addWidget(item_widget)
            else:
                no_data_label = QLabel("No prediction data available")
                no_data_label.setFont(QFont('Segoe UI', 11))
                no_data_label.setStyleSheet("color: #9ca3af;")
                self.ai_stats_layout.addWidget(no_data_label)
                
        except Exception as e:
            log_app_event("update_ai_stats_error", "DashboardWindow", {"error": str(e)})
    
    def update_top_categories(self, data):
        """Update top categories card"""
        try:
            # Clear existing widgets
            while self.top_categories_layout.count():
                child = self.top_categories_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            categories = data.get('category_distribution', [])
            if categories:
                # Sort by total amount (descending)
                sorted_categories = sorted(categories, key=lambda x: abs(x.get('total_amount', 0)), reverse=True)
                
                for i, category in enumerate(sorted_categories[:3]):  # Top 3
                    name = category.get('category_name', 'Unknown')
                    amount = abs(category.get('total_amount', 0))
                    avg_amount = abs(category.get('avg_amount', 0))
                    
                    # Rank emoji
                    rank_emojis = ['🥇', '🥈', '🥉']
                    rank_emoji = rank_emojis[i] if i < 3 else '🏅'
                    
                    # Create ranking item
                    item_widget = QWidget()
                    item_layout = QVBoxLayout(item_widget)
                    item_layout.setContentsMargins(0, 8, 0, 8)
                    
                    # Rank and category
                    rank_layout = QHBoxLayout()
                    rank_label = QLabel(f"{rank_emoji} {name}")
                    rank_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
                    rank_label.setStyleSheet("color: #1f2937;")
                    
                    amount_label = QLabel(f"Rp {amount:,.0f}")
                    amount_label.setFont(QFont('Segoe UI', 11, QFont.Medium))
                    amount_label.setStyleSheet("color: #dc2626;")
                    amount_label.setAlignment(Qt.AlignRight)
                    
                    rank_layout.addWidget(rank_label)
                    rank_layout.addStretch()
                    rank_layout.addWidget(amount_label)
                    
                    # Average info
                    avg_label = QLabel(f"Avg: Rp {avg_amount:,.0f} per transaction")
                    avg_label.setFont(QFont('Segoe UI', 9))
                    avg_label.setStyleSheet("color: #6b7280; margin-left: 24px;")
                    
                    item_layout.addLayout(rank_layout)
                    item_layout.addWidget(avg_label)
                    
                    self.top_categories_layout.addWidget(item_widget)
                    
                    # Add separator line except for last item
                    if i < min(len(sorted_categories) - 1, 2):
                        separator = QFrame()
                        separator.setFrameShape(QFrame.HLine)
                        separator.setStyleSheet("color: #e5e7eb; margin: 5px 0;")
                        self.top_categories_layout.addWidget(separator)
            else:
                no_data_label = QLabel("No spending data available")
                no_data_label.setFont(QFont('Segoe UI', 11))
                no_data_label.setStyleSheet("color: #9ca3af;")
                self.top_categories_layout.addWidget(no_data_label)
                
        except Exception as e:
            log_app_event("update_top_categories_error", "DashboardWindow", {"error": str(e)})
    
    def update_recent_summary(self, data):
        """Update recent activity summary"""
        try:
            # Clear existing widgets
            while self.recent_summary_layout.count():
                child = self.recent_summary_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            transactions = data.get('transactions', [])
            if transactions:
                # Show recent 5 transactions
                recent_transactions = transactions[:5]
                
                for transaction in recent_transactions:
                    description = transaction.get('description', 'Unknown')
                    amount = transaction.get('amount', 0)
                    category = transaction.get('category_name', 'No Category')
                    date = transaction.get('transaction_date', '')[:10]  # Just date part
                    
                    # Create transaction item
                    item_widget = QWidget()
                    item_layout = QVBoxLayout(item_widget)
                    item_layout.setContentsMargins(0, 5, 0, 5)
                    
                    # Main info layout
                    main_layout = QHBoxLayout()
                    
                    # Transaction info
                    desc_label = QLabel(description[:30] + "..." if len(description) > 30 else description)
                    desc_label.setFont(QFont('Segoe UI', 11, QFont.Medium))
                    desc_label.setStyleSheet("color: #374151;")
                    
                    # Amount
                    amount_color = "#059669" if amount > 0 else "#dc2626"
                    amount_text = f"+Rp {amount:,.0f}" if amount > 0 else f"Rp {abs(amount):,.0f}"
                    amount_label = QLabel(amount_text)
                    amount_label.setFont(QFont('Segoe UI', 10, QFont.Bold))
                    amount_label.setStyleSheet(f"color: {amount_color};")
                    amount_label.setAlignment(Qt.AlignRight)
                    
                    main_layout.addWidget(desc_label)
                    main_layout.addStretch()
                    main_layout.addWidget(amount_label)
                    
                    # Category and date info
                    details_label = QLabel(f"{category} • {date}")
                    details_label.setFont(QFont('Segoe UI', 9))
                    details_label.setStyleSheet("color: #6b7280;")
                    
                    item_layout.addLayout(main_layout)
                    item_layout.addWidget(details_label)
                    
                    self.recent_summary_layout.addWidget(item_widget)
            else:
                no_data_label = QLabel("No recent transactions")
                no_data_label.setFont(QFont('Segoe UI', 11))
                no_data_label.setStyleSheet("color: #9ca3af;")
                self.recent_summary_layout.addWidget(no_data_label)
                
        except Exception as e:
            log_app_event("update_recent_summary_error", "DashboardWindow", {"error": str(e)})

    def ensure_visible(self):
        self.show()
        self.setWindowState(Qt.WindowNoState)
        self.activateWindow()
        self.raise_()
        print(f"Dashboard visibility: {self.isVisible()}")
        print(f"Dashboard window state: {self.windowState()}")
        log_window_event("DashboardWindow", "forced_visible")
    
    def logout(self):
        """Handle logout"""
        log_user_action("logout_clicked", "DashboardWindow")
        
        reply = QMessageBox.question(
            self,
            'Confirm Logout',
            'Are you sure you want to logout?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            log_user_action("logout_confirmed", "DashboardWindow")
            self.logout_requested.emit()
            self.close()