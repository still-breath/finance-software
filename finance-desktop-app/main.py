#!/usr/bin/env python3
"""
Finance Desktop Application
Main entry point for the PyQt5-based personal finance management application.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api.client import APIClient
from ui.auth import LoginDialog, RegisterDialog
from ui.dashboard import DashboardWindow
from ui.simple_dashboard import UltraSimpleDashboard  
from utils.logger import log_user_action, log_app_event, log_window_event, log_validation_error

class MainWindow(QWidget):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        log_app_event("application_start", "MainWindow")
        self.api_client = APIClient()
        self.current_user = None
        self.initUI()
        log_window_event("MainWindow", "initialized")
    
    def initUI(self):
        self.setWindowTitle('Finance Manager')
        self.setGeometry(100, 100, 1000, 700)
        
        # Main container with card style
        main_container = QWidget()
        main_container.setObjectName('mainCard')
        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(80, 60, 80, 60)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(60, 80, 60, 80)
        layout.setSpacing(35)
        
        # Header with logo and title side by side
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)
        
        # Logo
        logo_label = QLabel('💰')
        logo_font = QFont('Open Sans', 56)
        logo_label.setFont(logo_font)
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Title section
        title_section = QVBoxLayout()
        title_section.setSpacing(5)
        
        title = QLabel('Finance Dashboard')
        title_font = QFont('Open Sans', 32, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50; background: transparent;")
        
        subtitle = QLabel('Simple and effective financial management')
        subtitle_font = QFont('Open Sans', 14)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #7f8c8d; background: transparent;")
        
        title_section.addWidget(title)
        title_section.addWidget(subtitle)
        
        header_layout.addWidget(logo_label)
        header_layout.addLayout(title_section)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addSpacing(40)
        
        # Button container with modern card-like buttons
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(20)
        button_layout.setContentsMargins(150, 0, 150, 0)
        
        # Primary button
        login_btn = QPushButton('Get Started')
        login_btn.setObjectName('primary_btn')
        login_btn.setFixedHeight(65)
        login_btn.setFont(QFont('Open Sans', 16, QFont.Bold))
        login_btn.clicked.connect(self.show_login)
        
        # Secondary button
        register_btn = QPushButton('Create New Account')
        register_btn.setObjectName('secondary_btn')
        register_btn.setFixedHeight(60)
        register_btn.setFont(QFont('Open Sans', 14, QFont.DemiBold))
        register_btn.clicked.connect(self.show_register)
        
        # Demo button
        demo_btn = QPushButton('Try Demo')
        demo_btn.setObjectName('demo_btn')
        demo_btn.setFixedHeight(55)
        demo_btn.setFont(QFont('Open Sans', 13))
        demo_btn.clicked.connect(self.show_demo)
        
        button_layout.addWidget(login_btn)
        button_layout.addWidget(register_btn)
        button_layout.addWidget(demo_btn)
        
        layout.addWidget(button_container)
        layout.addStretch()
        
        container_layout.addLayout(layout)
        
        # Main window layout
        window_layout = QVBoxLayout()
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(main_container)
        
        self.setLayout(window_layout)
        
        # Apply styling
        self.apply_modern_styling()
        
        # Center window on screen
        self.center()
    
    def apply_modern_styling(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                font-family: 'Open Sans', Arial, sans-serif;
            }
            
            QWidget#mainCard {
                background-color: white;
                border-radius: 15px;
                margin: 20px;
            }
            
            QLabel {
                color: #2c3e50;
                background: transparent;
            }
            
            QPushButton {
                border: none;
                border-radius: 12px;
                font-weight: 600;
                padding: 15px 30px;
                font-size: 14px;
                transition: all 0.3s;
            }
            
            QPushButton#primary_btn {
                background-color: #007bff;
                color: white;
                font-size: 16px;
                box-shadow: 0 4px 6px rgba(0, 123, 255, 0.3);
            }
            
            QPushButton#primary_btn:hover {
                background-color: #0056b3;
                box-shadow: 0 6px 12px rgba(0, 123, 255, 0.4);
                padding: 15px 35px;
            }
            
            QPushButton#primary_btn:pressed {
                background-color: #004085;
            }
            
            QPushButton#secondary_btn {
                background-color: white;
                color: #007bff;
                border: 2px solid #007bff;
                font-weight: 600;
            }
            
            QPushButton#secondary_btn:hover {
                background-color: #007bff;
                color: white;
                box-shadow: 0 4px 8px rgba(0, 123, 255, 0.2);
            }
            
            QPushButton#secondary_btn:pressed {
                background-color: #0056b3;
                color: white;
            }
            
            QPushButton#demo_btn {
                background-color: #f8f9fa;
                color: #6c757d;
                border: 2px solid #dee2e6;
                font-weight: 500;
            }
            
            QPushButton#demo_btn:hover {
                background-color: #e2e6ea;
                border-color: #adb5bd;
                color: #495057;
            }
            
            QPushButton#demo_btn:pressed {
                background-color: #dae0e5;
            }
        """)
    
    def center(self):
        from PyQt5.QtWidgets import QDesktopWidget
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def show_login(self):
        """Show login dialog"""
        log_user_action("show_login_dialog", "MainWindow")
        login_dialog = LoginDialog(self.api_client, self)
        login_dialog.login_successful.connect(self.on_login_success)
        login_dialog.exec_()
    
    def show_register(self):
        """Show register dialog"""
        log_user_action("show_register_dialog", "MainWindow")
        register_dialog = RegisterDialog(self.api_client, self)
        register_dialog.registration_successful.connect(self.on_registration_success)
        register_dialog.exec_()
    
    def show_demo(self):
        """Show demo mode (placeholder)"""
        log_user_action("show_demo_mode", "MainWindow")
        QMessageBox.information(
            self, 
            'Demo Mode', 
            'Demo mode will be implemented in the next iteration.\n\nFor now, please use Login or Register to access the application.'
        )
    
    def on_login_success(self, result):
        """Handle successful login"""
        try:
            self.current_user = result.get('user', {})
            log_app_event("login_successful", "MainWindow", {
                "user_id": self.current_user.get('id'),
                "user_name": self.current_user.get('name')
            })
            
            # Try simple dashboard first for debugging
            print(f"Attempting to create dashboard for user: {self.current_user}")
            
            self.dashboard = UltraSimpleDashboard(self.api_client, self.current_user, None)
            self.dashboard.logout_requested.connect(self.on_logout)
            
            print("Dashboard created, showing...")
            self.dashboard.show()
            self.dashboard.activateWindow()
            self.dashboard.raise_()
            
            # Don't hide main window immediately - let dashboard stabilize first
            print("Dashboard shown, keeping main window for stability...")
            
            log_window_event("UltraSimpleDashboard", "opened")
            print("Dashboard should be visible now")
            
        except Exception as e:
            log_validation_error("MainWindow", "dashboard_creation_failed", str(e))
            QMessageBox.critical(self, "Error", f"Failed to open dashboard: {str(e)}")
            # Keep main window visible if dashboard fails
            self.show()
    
    def on_registration_success(self, result):
        """Handle successful registration"""
        log_app_event("registration_successful", "MainWindow", {
            "user_data": result.get('user', {})
        })
        QMessageBox.information(
            self,
            'Registration Successful',
            'Account created successfully!\nYou can now login with your credentials.'
        )
    
    def on_logout(self):
        """Handle logout from dashboard"""
        log_app_event("user_logout", "MainWindow")
        self.current_user = None
        self.show()
        log_window_event("MainWindow", "shown_after_logout")

def main():
    """Main application function"""
    log_app_event("application_starting", "main")
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName('Finance Manager')
    app.setApplicationVersion('1.0.0')
    app.setOrganizationName('Finance App')
    log_app_event("qt_application_configured", "main")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    log_window_event("MainWindow", "shown")
    
    log_app_event("starting_event_loop", "main")
    # Start event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()