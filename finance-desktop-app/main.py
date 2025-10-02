#!/usr/bin/env python3
"""
Finance Desktop Application
Main entry point for the PyQt5-based personal finance management application.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api.client import APIClient
from ui.auth import LoginDialog, RegisterDialog
from ui.dashboard import DashboardWindow

class MainWindow(QWidget):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.current_user = None
        self.initUI()
    
    def initUI(self):
        """Initialize the user interface"""
        self.setWindowTitle('Finance Manager')
        self.setGeometry(100, 100, 800, 600)
        
        # Create main layout
        layout = QVBoxLayout()
        
        # Add title
        title = QLabel('Personal Finance Manager')
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Add subtitle
        subtitle = QLabel('Manage your finances with ease')
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Add buttons
        login_btn = QPushButton('Login')
        register_btn = QPushButton('Register')
        demo_btn = QPushButton('Demo Mode')
        
        # Style buttons
        button_style = """
            QPushButton {
                padding: 10px 20px;
                font-size: 14px;
                margin: 5px;
                border: 2px solid #0066cc;
                border-radius: 5px;
                background-color: #0066cc;
                color: white;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
        """
        
        login_btn.setStyleSheet(button_style)
        register_btn.setStyleSheet(button_style)
        demo_btn.setStyleSheet(button_style.replace('#0066cc', '#28a745').replace('#0052a3', '#218838').replace('#003d7a', '#1e7e34'))
        
        # Connect buttons to placeholder functions
        login_btn.clicked.connect(self.show_login)
        register_btn.clicked.connect(self.show_register)
        demo_btn.clicked.connect(self.show_demo)
        
        layout.addWidget(login_btn)
        layout.addWidget(register_btn)
        layout.addWidget(demo_btn)
        
        # Set layout
        self.setLayout(layout)
        
        # Center window on screen
        self.center()
    
    def center(self):
        """Center the window on the screen"""
        from PyQt5.QtWidgets import QDesktopWidget
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def show_login(self):
        """Show login dialog"""
        login_dialog = LoginDialog(self.api_client, self)
        login_dialog.login_successful.connect(self.on_login_success)
        login_dialog.exec_()
    
    def show_register(self):
        """Show register dialog"""
        register_dialog = RegisterDialog(self.api_client, self)
        register_dialog.registration_successful.connect(self.on_registration_success)
        register_dialog.exec_()
    
    def show_demo(self):
        """Show demo mode (placeholder)"""
        QMessageBox.information(
            self, 
            'Demo Mode', 
            'Demo mode will be implemented in the next iteration.\n\nFor now, please use Login or Register to access the application.'
        )
    
    def on_login_success(self, result):
        """Handle successful login"""
        self.current_user = result.get('user', {})
        
        # Open dashboard window
        self.dashboard = DashboardWindow(self.api_client, self.current_user, self)
        self.dashboard.logout_requested.connect(self.on_logout)
        self.dashboard.show()
        
        self.hide()
    
    def on_registration_success(self, result):
        """Handle successful registration"""
        QMessageBox.information(
            self,
            'Registration Successful',
            'Account created successfully!\nYou can now login with your credentials.'
        )
    
    def on_logout(self):
        """Handle logout from dashboard"""
        self.current_user = None
        self.show()

def main():
    """Main application function"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName('Finance Manager')
    app.setApplicationVersion('1.0.0')
    app.setOrganizationName('Finance App')
    
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()