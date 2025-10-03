"""
Authentication UI components for Finance Desktop Application
Login and Registration forms with modern design
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLineEdit, QPushButton, QLabel, QMessageBox, 
                           QProgressBar, QCheckBox, QWidget, QGraphicsDropShadowEffect,
                           QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QColor
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.client import APIClient
from utils.logger import log_user_action, log_validation_error, log_window_event

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
                    self.kwargs['username'], 
                    self.kwargs['password']
                )
                self.success.emit(result)
            elif self.operation == 'register':
                result = self.api_client.register(
                    self.kwargs['username'], 
                    self.kwargs['password']
                )
                self.success.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class LoginDialog(QDialog):
    """Modern login dialog with clean design"""
    
    login_successful = pyqtSignal(dict)
    
    def __init__(self, api_client: APIClient, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.auth_worker = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Finance Manager')
        self.setFixedSize(900, 600)
        self.setModal(True)
        
        # Main layout - horizontal split
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left side - Login form
        left_widget = QWidget()
        left_widget.setStyleSheet("background-color: white;")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(60, 50, 60, 50)
        left_layout.setSpacing(25)
        
        # Logo section
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(10)
        
        logo_label = QLabel('💰')
        logo_label.setFont(QFont('Open Sans', 28))
        
        logo_text = QLabel('Finance Manager')
        logo_text.setFont(QFont('Open Sans', 16, QFont.Bold))
        logo_text.setStyleSheet("color: #2c3e50;")
        
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()
        
        left_layout.addWidget(logo_container)
        left_layout.addSpacing(20)
        
        # Welcome text
        welcome_title = QLabel('Welcome Back!')
        welcome_title.setFont(QFont('Open Sans', 28, QFont.Bold))
        welcome_title.setStyleSheet("color: #2c3e50;")
        
        welcome_subtitle = QLabel('Please login to your account')
        welcome_subtitle.setFont(QFont('Open Sans', 12))
        welcome_subtitle.setStyleSheet("color: #7f8c8d;")
        
        left_layout.addWidget(welcome_title)
        left_layout.addWidget(welcome_subtitle)
        left_layout.addSpacing(15)
        
        # Form fields
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(20)
        
        # Username field
        username_label = QLabel('Username')
        username_label.setFont(QFont('Open Sans', 11, QFont.Medium))
        username_label.setStyleSheet("color: #2c3e50;")
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText('Enter your username')
        self.username_edit.setFont(QFont('Open Sans', 12))
        self.username_edit.setMinimumHeight(50)
        
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_edit)
        
        # Password field
        password_label = QLabel('Password')
        password_label.setFont(QFont('Open Sans', 11, QFont.Medium))
        password_label.setStyleSheet("color: #2c3e50;")
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText('Enter your password')
        self.password_edit.setFont(QFont('Open Sans', 12))
        self.password_edit.setMinimumHeight(50)
        
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_edit)
        
        # Remember me
        remember_layout = QHBoxLayout()
        self.remember_cb = QCheckBox('Remember me')
        self.remember_cb.setFont(QFont('Open Sans', 10))
        self.remember_cb.setStyleSheet("color: #7f8c8d;")
        
        forgot_btn = QPushButton('Forgot Password?')
        forgot_btn.setFlat(True)
        forgot_btn.setFont(QFont('Open Sans', 10))
        forgot_btn.setStyleSheet("color: #3498db; border: none; text-align: right;")
        forgot_btn.setCursor(Qt.PointingHandCursor)
        
        remember_layout.addWidget(self.remember_cb)
        remember_layout.addStretch()
        remember_layout.addWidget(forgot_btn)
        
        form_layout.addLayout(remember_layout)
        
        left_layout.addWidget(form_widget)
        left_layout.addSpacing(10)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        left_layout.addWidget(self.progress_bar)
        
        # Login button
        self.login_btn = QPushButton('LOGIN')
        self.login_btn.setDefault(True)
        self.login_btn.setFixedHeight(55)
        self.login_btn.setFont(QFont('Open Sans', 13, QFont.Bold))
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.login)
        
        left_layout.addWidget(self.login_btn)
        
        # Sign up link
        signup_widget = QWidget()
        signup_layout = QHBoxLayout(signup_widget)
        signup_layout.setContentsMargins(0, 0, 0, 0)
        
        signup_text = QLabel("Don't have an account?")
        signup_text.setFont(QFont('Open Sans', 11))
        signup_text.setStyleSheet("color: #7f8c8d;")
        
        self.register_btn = QPushButton('Sign Up')
        self.register_btn.setFlat(True)
        self.register_btn.setFont(QFont('Open Sans', 11, QFont.Bold))
        self.register_btn.setStyleSheet("color: #3498db; border: none;")
        self.register_btn.setCursor(Qt.PointingHandCursor)
        self.register_btn.clicked.connect(self.show_register)
        
        signup_layout.addStretch()
        signup_layout.addWidget(signup_text)
        signup_layout.addWidget(self.register_btn)
        signup_layout.addStretch()
        
        left_layout.addWidget(signup_widget)
        left_layout.addStretch()
        
        # Right side - Illustration panel
        right_widget = QWidget()
        right_widget.setFixedWidth(350)
        right_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3498db, stop:1 #2980b9);
        """)
        
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(40, 60, 40, 60)
        right_layout.setAlignment(Qt.AlignCenter)
        
        # Illustration
        illustration = QLabel('📊')
        illustration.setFont(QFont('Open Sans', 120))
        illustration.setAlignment(Qt.AlignCenter)
        
        # Text on right panel
        right_title = QLabel('Financial Management')
        right_title.setFont(QFont('Open Sans', 20, QFont.Bold))
        right_title.setStyleSheet("color: white;")
        right_title.setAlignment(Qt.AlignCenter)
        right_title.setWordWrap(True)
        
        right_subtitle = QLabel('Track, analyze, and manage your finances with ease')
        right_subtitle.setFont(QFont('Open Sans', 12))
        right_subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        right_subtitle.setAlignment(Qt.AlignCenter)
        right_subtitle.setWordWrap(True)
        
        right_layout.addStretch()
        right_layout.addWidget(illustration)
        right_layout.addSpacing(30)
        right_layout.addWidget(right_title)
        right_layout.addSpacing(15)
        right_layout.addWidget(right_subtitle)
        right_layout.addStretch()
        
        # Add both sides to main layout
        main_layout.addWidget(left_widget, stretch=1)
        main_layout.addWidget(right_widget)
        
        self.setLayout(main_layout)
        
        # Connect Enter key
        self.password_edit.returnPressed.connect(self.login)
        
        self.apply_modern_styling()
    
    def apply_modern_styling(self):
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: none;
            }
            
            QLineEdit {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 13px;
                color: #2c3e50;
            }
            
            QLineEdit:focus {
                border-color: #3498db;
                background-color: white;
            }
            
            QLineEdit:hover {
                border-color: #3498db;
            }
            
            QPushButton#login_btn {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                letter-spacing: 1px;
            }
            
            QPushButton#login_btn:hover {
                background-color: #2980b9;
            }
            
            QPushButton#login_btn:pressed {
                background-color: #21618c;
            }
            
            QPushButton#login_btn:disabled {
                background-color: #bdc3c7;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #bdc3c7;
                background-color: white;
            }
            
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
            
            QProgressBar {
                border: none;
                background-color: #ecf0f1;
                border-radius: 2px;
            }
            
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
        """)
        
        self.login_btn.setObjectName('login_btn')
    
    def login(self):
        """Handle login button click"""
        log_user_action("login_attempt", "LoginDialog")
        
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        # Validation
        if not username:
            log_validation_error("LoginDialog", "username", "empty username")
            QMessageBox.warning(self, 'Validation Error', 'Please enter your username')
            self.username_edit.setFocus()
            return
            
        if not password:
            log_validation_error("LoginDialog", "password", "empty password")
            QMessageBox.warning(self, 'Validation Error', 'Please enter your password')
            self.password_edit.setFocus()
            return

        if len(username) < 3:
            log_validation_error("LoginDialog", "username", "username too short")
            QMessageBox.warning(self, 'Validation Error', 'Username must be at least 3 characters long')
            self.username_edit.setFocus()
            return
        
        log_user_action("login_validation_passed", "LoginDialog", {"username": username})
        
        # Show progress
        self.set_loading(True)
        
        # Start authentication
        self.auth_worker = AuthWorker(self.api_client, 'login', username=username, password=password)
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
            self.progress_bar.setRange(0, 0)
        
        self.username_edit.setEnabled(not loading)
        self.password_edit.setEnabled(not loading)
        self.login_btn.setEnabled(not loading)
        self.register_btn.setEnabled(not loading)

class RegisterDialog(QDialog):
    """Modern registration dialog"""
    
    registration_successful = pyqtSignal(dict)
    
    def __init__(self, api_client: APIClient, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.auth_worker = None
        self.initUI()
    
    def initUI(self):
        """Initialize registration dialog UI"""
        self.setWindowTitle('Create Account')
        self.setFixedSize(900, 600)
        self.setModal(True)
        
        # Main layout - horizontal split
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left side - Illustration panel
        left_widget = QWidget()
        left_widget.setFixedWidth(350)
        left_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #27ae60, stop:1 #229954);
        """)
        
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(40, 60, 40, 60)
        left_layout.setAlignment(Qt.AlignCenter)
        
        # Illustration
        illustration = QLabel('🚀')
        illustration.setFont(QFont('Open Sans', 120))
        illustration.setAlignment(Qt.AlignCenter)
        
        # Text on left panel
        left_title = QLabel('Join Us Today')
        left_title.setFont(QFont('Open Sans', 20, QFont.Bold))
        left_title.setStyleSheet("color: white;")
        left_title.setAlignment(Qt.AlignCenter)
        left_title.setWordWrap(True)
        
        left_subtitle = QLabel('Start your financial journey with our comprehensive management tools')
        left_subtitle.setFont(QFont('Open Sans', 12))
        left_subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        left_subtitle.setAlignment(Qt.AlignCenter)
        left_subtitle.setWordWrap(True)
        
        left_layout.addStretch()
        left_layout.addWidget(illustration)
        left_layout.addSpacing(30)
        left_layout.addWidget(left_title)
        left_layout.addSpacing(15)
        left_layout.addWidget(left_subtitle)
        left_layout.addStretch()
        
        # Right side - Registration form
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(60, 50, 60, 50)
        right_layout.setSpacing(25)
        
        # Logo section
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(10)
        
        logo_label = QLabel('💰')
        logo_label.setFont(QFont('Open Sans', 28))
        
        logo_text = QLabel('Finance Manager')
        logo_text.setFont(QFont('Open Sans', 16, QFont.Bold))
        logo_text.setStyleSheet("color: #2c3e50;")
        
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()
        
        right_layout.addWidget(logo_container)
        right_layout.addSpacing(20)
        
        # Title
        title = QLabel('Create Account')
        title.setFont(QFont('Open Sans', 28, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        
        subtitle = QLabel('Sign up to get started')
        subtitle.setFont(QFont('Open Sans', 12))
        subtitle.setStyleSheet("color: #7f8c8d;")
        
        right_layout.addWidget(title)
        right_layout.addWidget(subtitle)
        right_layout.addSpacing(15)
        
        # Form fields
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(18)
        
        # Username field
        username_label = QLabel('Username')
        username_label.setFont(QFont('Open Sans', 11, QFont.Medium))
        username_label.setStyleSheet("color: #2c3e50;")
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText('Choose a username')
        self.username_edit.setFont(QFont('Open Sans', 12))
        self.username_edit.setMinimumHeight(50)
        
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_edit)
        
        # Password field
        password_label = QLabel('Password')
        password_label.setFont(QFont('Open Sans', 11, QFont.Medium))
        password_label.setStyleSheet("color: #2c3e50;")
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText('Create a strong password')
        self.password_edit.setFont(QFont('Open Sans', 12))
        self.password_edit.setMinimumHeight(50)
        
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_edit)
        
        # Confirm password field
        confirm_label = QLabel('Confirm Password')
        confirm_label.setFont(QFont('Open Sans', 11, QFont.Medium))
        confirm_label.setStyleSheet("color: #2c3e50;")
        
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setPlaceholderText('Confirm your password')
        self.confirm_password_edit.setFont(QFont('Open Sans', 12))
        self.confirm_password_edit.setMinimumHeight(50)
        
        form_layout.addWidget(confirm_label)
        form_layout.addWidget(self.confirm_password_edit)
        
        right_layout.addWidget(form_widget)
        right_layout.addSpacing(10)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        right_layout.addWidget(self.progress_bar)
        
        # Register button
        self.register_btn = QPushButton('CREATE ACCOUNT')
        self.register_btn.setDefault(True)
        self.register_btn.setFixedHeight(55)
        self.register_btn.setFont(QFont('Open Sans', 13, QFont.Bold))
        self.register_btn.setCursor(Qt.PointingHandCursor)
        self.register_btn.clicked.connect(self.register)
        
        right_layout.addWidget(self.register_btn)
        
        # Sign in link
        signin_widget = QWidget()
        signin_layout = QHBoxLayout(signin_widget)
        signin_layout.setContentsMargins(0, 0, 0, 0)
        
        signin_text = QLabel("Already have an account?")
        signin_text.setFont(QFont('Open Sans', 11))
        signin_text.setStyleSheet("color: #7f8c8d;")
        
        self.back_btn = QPushButton('Sign In')
        self.back_btn.setFlat(True)
        self.back_btn.setFont(QFont('Open Sans', 11, QFont.Bold))
        self.back_btn.setStyleSheet("color: #27ae60; border: none;")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self.reject)
        
        signin_layout.addStretch()
        signin_layout.addWidget(signin_text)
        signin_layout.addWidget(self.back_btn)
        signin_layout.addStretch()
        
        right_layout.addWidget(signin_widget)
        right_layout.addStretch()
        
        # Add both sides to main layout
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget, stretch=1)
        
        self.setLayout(main_layout)
        
        # Connect Enter key
        self.confirm_password_edit.returnPressed.connect(self.register)
        
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: none;
            }
            
            QLineEdit {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 13px;
                color: #2c3e50;
            }
            
            QLineEdit:focus {
                border-color: #27ae60;
                background-color: white;
            }
            
            QLineEdit:hover {
                border-color: #27ae60;
            }
            
            QPushButton#register_btn {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                letter-spacing: 1px;
            }
            
            QPushButton#register_btn:hover {
                background-color: #229954;
            }
            
            QPushButton#register_btn:pressed {
                background-color: #1e8449;
            }
            
            QPushButton#register_btn:disabled {
                background-color: #bdc3c7;
            }
            
            QProgressBar {
                border: none;
                background-color: #ecf0f1;
                border-radius: 2px;
            }
            
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 2px;
            }
        """)
        
        self.register_btn.setObjectName('register_btn')
    
    def register(self):
        """Handle registration button click"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        # Validation
        if not username:
            QMessageBox.warning(self, 'Validation Error', 'Please enter your username')
            self.username_edit.setFocus()
            return
        
        if len(username) < 3:
            QMessageBox.warning(self, 'Validation Error', 'Username must be at least 3 characters long')
            self.username_edit.setFocus()
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
        
        # Show progress
        self.set_loading(True)
        
        # Start registration
        self.auth_worker = AuthWorker(self.api_client, 'register', 
                                    username=username, password=password)
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
            self.progress_bar.setRange(0, 0)
        
        self.username_edit.setEnabled(not loading)
        self.password_edit.setEnabled(not loading)
        self.confirm_password_edit.setEnabled(not loading)
        self.register_btn.setEnabled(not loading)
        self.back_btn.setEnabled(not loading)