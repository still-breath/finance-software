"""
Authentication UI components for Finance Desktop Application
Login and Registration forms with validation
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLineEdit, QPushButton, QLabel, QMessageBox, 
                           QProgressBar, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.client import APIClient

class AuthWorker(QThread):
    """Worker thread for authentication operations"""
    
    success = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, api_client, operation, **kwargs):
        super().__init__()
        self.api_client = api_client
        self.operation = operation
        self.kwargs = kwargs
    
    def run(self):
        """Run authentication operation in background"""
        try:
            if self.operation == 'login':
                result = self.api_client.login(
                    self.kwargs['email'], 
                    self.kwargs['password']
                )
                self.success.emit(result)
            elif self.operation == 'register':
                result = self.api_client.register(
                    self.kwargs['email'], 
                    self.kwargs['password'],
                    self.kwargs['name']
                )
                self.success.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class LoginDialog(QDialog):
    """Login dialog window"""
    
    login_successful = pyqtSignal(dict)
    
    def __init__(self, api_client: APIClient, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.auth_worker = None
        self.initUI()
    
    def initUI(self):
        """Initialize login dialog UI"""
        self.setWindowTitle('Login')
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Title
        title = QLabel('Login to Finance Manager')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Email field
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText('Enter your email')
        form_layout.addRow('Email:', self.email_edit)
        
        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText('Enter your password')
        form_layout.addRow('Password:', self.password_edit)
        
        # Remember me checkbox
        self.remember_cb = QCheckBox('Remember me')
        form_layout.addRow('', self.remember_cb)
        
        layout.addLayout(form_layout)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_btn = QPushButton('Login')
        self.login_btn.setDefault(True)
        self.login_btn.clicked.connect(self.login)
        
        self.register_btn = QPushButton('Create Account')
        self.register_btn.clicked.connect(self.show_register)
        
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.register_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Set layout
        self.setLayout(layout)
        
        # Connect Enter key to login
        self.password_edit.returnPressed.connect(self.login)
        
        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #0066cc;
            }
            QPushButton {
                padding: 8px 16px;
                font-size: 12px;
                border: none;
                border-radius: 4px;
                background-color: #0066cc;
                color: white;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
            QPushButton#register_btn {
                background-color: #28a745;
            }
            QPushButton#register_btn:hover {
                background-color: #218838;
            }
            QPushButton#cancel_btn {
                background-color: #6c757d;
            }
            QPushButton#cancel_btn:hover {
                background-color: #545b62;
            }
        """)
        
        # Set button names for styling
        self.register_btn.setObjectName('register_btn')
        self.cancel_btn.setObjectName('cancel_btn')
    
    def login(self):
        """Handle login button click"""
        email = self.email_edit.text().strip()
        password = self.password_edit.text()
        
        # Validation
        if not email:
            QMessageBox.warning(self, 'Validation Error', 'Please enter your email')
            self.email_edit.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, 'Validation Error', 'Please enter your password')
            self.password_edit.setFocus()
            return
        
        # Validate email format
        if '@' not in email:
            QMessageBox.warning(self, 'Validation Error', 'Please enter a valid email address')
            self.email_edit.setFocus()
            return
        
        # Show progress and disable buttons
        self.set_loading(True)
        
        # Start authentication in background thread
        self.auth_worker = AuthWorker(self.api_client, 'login', email=email, password=password)
        self.auth_worker.success.connect(self.on_login_success)
        self.auth_worker.error.connect(self.on_login_error)
        self.auth_worker.start()
    
    def on_login_success(self, result):
        """Handle successful login"""
        self.set_loading(False)
        self.login_successful.emit(result)
        self.accept()
    
    def on_login_error(self, error_message):
        """Handle login error"""
        self.set_loading(False)
        QMessageBox.critical(self, 'Login Failed', error_message)
    
    def show_register(self):
        """Show registration dialog"""
        register_dialog = RegisterDialog(self.api_client, self)
        register_dialog.registration_successful.connect(self.on_registration_success)
        register_dialog.exec_()
    
    def on_registration_success(self, result):
        """Handle successful registration"""
        QMessageBox.information(
            self, 
            'Registration Successful', 
            'Account created successfully! You can now login with your credentials.'
        )
    
    def set_loading(self, loading: bool):
        """Set loading state"""
        self.progress_bar.setVisible(loading)
        if loading:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Disable/enable form elements
        self.email_edit.setEnabled(not loading)
        self.password_edit.setEnabled(not loading)
        self.login_btn.setEnabled(not loading)
        self.register_btn.setEnabled(not loading)
        self.cancel_btn.setEnabled(not loading)

class RegisterDialog(QDialog):
    """Registration dialog window"""
    
    registration_successful = pyqtSignal(dict)
    
    def __init__(self, api_client: APIClient, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.auth_worker = None
        self.initUI()
    
    def initUI(self):
        """Initialize registration dialog UI"""
        self.setWindowTitle('Create Account')
        self.setFixedSize(400, 350)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Title
        title = QLabel('Create Your Account')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('Enter your full name')
        form_layout.addRow('Full Name:', self.name_edit)
        
        # Email field
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText('Enter your email')
        form_layout.addRow('Email:', self.email_edit)
        
        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText('Enter your password')
        form_layout.addRow('Password:', self.password_edit)
        
        # Confirm password field
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setPlaceholderText('Confirm your password')
        form_layout.addRow('Confirm Password:', self.confirm_password_edit)
        
        layout.addLayout(form_layout)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.register_btn = QPushButton('Create Account')
        self.register_btn.setDefault(True)
        self.register_btn.clicked.connect(self.register)
        
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.register_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Set layout
        self.setLayout(layout)
        
        # Connect Enter key to register
        self.confirm_password_edit.returnPressed.connect(self.register)
        
        # Apply same styling as login dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #0066cc;
            }
            QPushButton {
                padding: 8px 16px;
                font-size: 12px;
                border: none;
                border-radius: 4px;
                background-color: #28a745;
                color: white;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton#cancel_btn {
                background-color: #6c757d;
            }
            QPushButton#cancel_btn:hover {
                background-color: #545b62;
            }
        """)
        
        self.cancel_btn.setObjectName('cancel_btn')
    
    def register(self):
        """Handle registration button click"""
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        # Validation
        if not name:
            QMessageBox.warning(self, 'Validation Error', 'Please enter your full name')
            self.name_edit.setFocus()
            return
        
        if not email:
            QMessageBox.warning(self, 'Validation Error', 'Please enter your email')
            self.email_edit.setFocus()
            return
        
        if '@' not in email:
            QMessageBox.warning(self, 'Validation Error', 'Please enter a valid email address')
            self.email_edit.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, 'Validation Error', 'Please enter a password')
            self.password_edit.setFocus()
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, 'Validation Error', 'Password must be at least 6 characters long')
            self.password_edit.setFocus()
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, 'Validation Error', 'Passwords do not match')
            self.confirm_password_edit.setFocus()
            return
        
        # Show progress and disable buttons
        self.set_loading(True)
        
        # Start registration in background thread
        self.auth_worker = AuthWorker(self.api_client, 'register', 
                                    name=name, email=email, password=password)
        self.auth_worker.success.connect(self.on_register_success)
        self.auth_worker.error.connect(self.on_register_error)
        self.auth_worker.start()
    
    def on_register_success(self, result):
        """Handle successful registration"""
        self.set_loading(False)
        self.registration_successful.emit(result)
        self.accept()
    
    def on_register_error(self, error_message):
        """Handle registration error"""
        self.set_loading(False)
        QMessageBox.critical(self, 'Registration Failed', error_message)
    
    def set_loading(self, loading: bool):
        """Set loading state"""
        self.progress_bar.setVisible(loading)
        if loading:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Disable/enable form elements
        self.name_edit.setEnabled(not loading)
        self.email_edit.setEnabled(not loading)
        self.password_edit.setEnabled(not loading)
        self.confirm_password_edit.setEnabled(not loading)
        self.register_btn.setEnabled(not loading)
        self.cancel_btn.setEnabled(not loading)