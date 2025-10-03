"""
Ultra Simple Dashboard for debugging crash issues
Minimal implementation with just basic widgets
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.client import APIClient
from utils.logger import log_window_event

class UltraSimpleDashboard(QMainWindow):
    """Ultra simple dashboard for debugging"""
    
    logout_requested = pyqtSignal()
    
    def __init__(self, api_client: APIClient, user_data: dict, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.user_data = user_data
        
        print("UltraSimpleDashboard: Starting initialization...")
        
        try:
            self.init_ultra_simple_ui()
            
            # Make window persistent and prevent auto-close
            self.setAttribute(Qt.WA_QuitOnClose, False)  # Don't quit app when this window closes
            self.setWindowFlags(Qt.Window)  # Make it a proper independent window
            
            print("UltraSimpleDashboard: UI created successfully")
            
        except Exception as e:
            print(f"UltraSimpleDashboard: Error in init: {e}")
            raise
    
    def init_ultra_simple_ui(self):
        """Initialize ultra simple UI"""
        print("UltraSimpleDashboard: Setting window properties...")
        self.setWindowTitle('Ultra Simple Dashboard')
        self.setGeometry(300, 300, 600, 400)
        
        print("UltraSimpleDashboard: Creating central widget...")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        print("UltraSimpleDashboard: Creating layout...")
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        
        print("UltraSimpleDashboard: Adding title...")
        title = QLabel('🎉 Dashboard Works!')
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2d3748; padding: 20px; background: #f0f8f0; border-radius: 10px;")
        layout.addWidget(title)
        
        print("UltraSimpleDashboard: Adding user info...")
        user_info = QLabel(f"User: {self.user_data.get('username', 'Unknown')}")
        user_info.setFont(QFont('Arial', 14))
        user_info.setAlignment(Qt.AlignCenter)
        user_info.setStyleSheet("color: #4a5568; padding: 10px;")
        layout.addWidget(user_info)
        
        print("UltraSimpleDashboard: Adding logout button...")
        logout_btn = QPushButton('Logout')
        logout_btn.setFont(QFont('Arial', 12))
        logout_btn.setFixedHeight(40)
        logout_btn.setStyleSheet("""
            QPushButton {
                background: #e53e3e;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background: #c53030;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        print("UltraSimpleDashboard: UI setup complete")
    
    def logout(self):
        """Handle logout"""
        print("UltraSimpleDashboard: Logout clicked")
        self.logout_requested.emit()
        self.close()
    
    def show(self):
        """Override show to add debugging"""
        print("UltraSimpleDashboard: show() called")
        super().show()
        
        # Force window to stay visible
        self.setWindowState(Qt.WindowNoState)
        self.activateWindow()
        self.raise_()
        
        # Set a timer to check visibility
        QTimer.singleShot(1000, self.check_status)
        
        print("UltraSimpleDashboard: show() completed")
    
    def check_status(self):
        """Check dashboard status after 1 second"""
        print(f"UltraSimpleDashboard: Status check - Visible: {self.isVisible()}, Active: {self.isActiveWindow()}")
        if not self.isVisible():
            print("UltraSimpleDashboard: Window not visible, forcing show again...")
            self.show()
        
    def closeEvent(self, event):
        """Handle close event"""
        print("UltraSimpleDashboard: closeEvent triggered")
        event.accept()