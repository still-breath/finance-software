import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from unittest.mock import Mock, patch
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ui.auth import LoginDialog, RegisterDialog
from api.client import APIClient

@pytest.fixture(scope="module")
def app():
    """Create QApplication for testing"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    app.quit()

@pytest.fixture
def mock_api_client():
    """Create mock API client"""
    return Mock(spec=APIClient)

class TestLoginDialog:
    
    def test_login_dialog_creation(self, app, mock_api_client):
        dialog = LoginDialog(mock_api_client)
        assert dialog is not None
        assert dialog.windowTitle() == 'Login'
        assert dialog.api_client == mock_api_client
    
    def test_login_dialog_ui_elements(self, app, mock_api_client):
        dialog = LoginDialog(mock_api_client)
        
        # Check that email and password fields exist
        assert dialog.email_edit is not None
        assert dialog.password_edit is not None
        assert dialog.login_btn is not None
        assert dialog.register_btn is not None
        assert dialog.cancel_btn is not None
        assert dialog.remember_cb is not None
    
    def test_login_validation_empty_email(self, app, mock_api_client):
        dialog = LoginDialog(mock_api_client)
        
        # Clear email and set password
        dialog.email_edit.setText('')
        dialog.password_edit.setText('password')
        
        # Mock QMessageBox.warning to capture validation
        with patch('ui.auth.QMessageBox.warning') as mock_warning:
            dialog.login()
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert 'email' in args[2].lower()
    
    def test_login_validation_empty_password(self, app, mock_api_client):
        dialog = LoginDialog(mock_api_client)
        
        # Set email and clear password
        dialog.email_edit.setText('test@example.com')
        dialog.password_edit.setText('')
        
        # Mock QMessageBox.warning to capture validation
        with patch('ui.auth.QMessageBox.warning') as mock_warning:
            dialog.login()
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert 'password' in args[2].lower()
    
    def test_login_validation_invalid_email(self, app, mock_api_client):
        dialog = LoginDialog(mock_api_client)
        
        # Set invalid email
        dialog.email_edit.setText('invalid-email')
        dialog.password_edit.setText('password')
        
        # Mock QMessageBox.warning to capture validation
        with patch('ui.auth.QMessageBox.warning') as mock_warning:
            dialog.login()
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert 'valid email' in args[2].lower()

class TestRegisterDialog:
    """Test cases for RegisterDialog"""
    
    def test_register_dialog_creation(self, app, mock_api_client):
        dialog = RegisterDialog(mock_api_client)
        assert dialog is not None
        assert dialog.windowTitle() == 'Create Account'
        assert dialog.api_client == mock_api_client
    
    def test_register_dialog_ui_elements(self, app, mock_api_client):
        dialog = RegisterDialog(mock_api_client)
        
        # Check that all fields exist
        assert dialog.name_edit is not None
        assert dialog.email_edit is not None
        assert dialog.password_edit is not None
        assert dialog.confirm_password_edit is not None
        assert dialog.register_btn is not None
        assert dialog.cancel_btn is not None
    
    def test_register_validation_empty_name(self, app, mock_api_client):
        dialog = RegisterDialog(mock_api_client)
        
        # Clear name and set other fields
        dialog.name_edit.setText('')
        dialog.email_edit.setText('test@example.com')
        dialog.password_edit.setText('password123')
        dialog.confirm_password_edit.setText('password123')
        
        # Mock QMessageBox.warning to capture validation
        with patch('ui.auth.QMessageBox.warning') as mock_warning:
            dialog.register()
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert 'name' in args[2].lower()
    
    def test_register_validation_password_mismatch(self, app, mock_api_client):
        dialog = RegisterDialog(mock_api_client)
        
        # Set fields with mismatched passwords
        dialog.name_edit.setText('Test User')
        dialog.email_edit.setText('test@example.com')
        dialog.password_edit.setText('password123')
        dialog.confirm_password_edit.setText('different')
        
        # Mock QMessageBox.warning to capture validation
        with patch('ui.auth.QMessageBox.warning') as mock_warning:
            dialog.register()
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert 'do not match' in args[2].lower()
    
    def test_register_validation_short_password(self, app, mock_api_client):
        dialog = RegisterDialog(mock_api_client)
        
        # Set fields with short password
        dialog.name_edit.setText('Test User')
        dialog.email_edit.setText('test@example.com')
        dialog.password_edit.setText('123')
        dialog.confirm_password_edit.setText('123')
        
        # Mock QMessageBox.warning to capture validation
        with patch('ui.auth.QMessageBox.warning') as mock_warning:
            dialog.register()
            mock_warning.assert_called_once()
            args = mock_warning.call_args[0]
            assert '6 characters' in args[2]
    
    def test_set_loading_state(self, app, mock_api_client):
        dialog = RegisterDialog(mock_api_client)
        
        # Show dialog for proper widget initialization
        dialog.show()
        
        # Test loading=True
        dialog.set_loading(True)
        assert dialog.progress_bar.isVisible() == True
        assert dialog.name_edit.isEnabled() == False
        assert dialog.register_btn.isEnabled() == False
        
        # Test loading=False
        dialog.set_loading(False)
        assert dialog.progress_bar.isVisible() == False
        assert dialog.name_edit.isEnabled() == True
        assert dialog.register_btn.isEnabled() == True
        
        dialog.hide()