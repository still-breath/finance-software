import pytest
import sys
import os
from unittest.mock import patch, Mock
from io import StringIO

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.logger import FinanceLogger, log_user_action, log_api_request, log_api_response

class TestFinanceLogger:
    
    def setup_method(self):
        self.logger = FinanceLogger("TestLogger")
    
    def test_logger_initialization(self):
        assert self.logger.logger.name == "TestLogger"
        assert len(self.logger.logger.handlers) == 1
        assert self.logger.logger.level == 10  # DEBUG level
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_basic_logging(self, mock_stdout):
        self.logger.info("Test message")
        output = mock_stdout.getvalue()
        assert "Test message" in output
        assert "INFO" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_user_action_logging(self, mock_stdout):
        self.logger.user_action("button_click", "TestComponent", {"button": "login"})
        output = mock_stdout.getvalue()
        assert "USER ACTION" in output
        assert "TestComponent" in output
        assert "button_click" in output
        assert "button" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_api_request_logging(self, mock_stdout):
        self.logger.api_request("POST", "/api/auth/login", {"email": "test@example.com", "password": "secret123"})
        output = mock_stdout.getvalue()
        assert "API REQUEST" in output
        assert "POST /api/auth/login" in output
        assert "test@example.com" in output
        # Password should be masked
        assert "secret123" not in output
        assert "***" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_api_response_success_logging(self, mock_stdout):
        response_data = {"token": "abc123token", "user": {"id": 1, "name": "Test User"}}
        self.logger.api_response("POST", "/api/auth/login", 200, response_data)
        output = mock_stdout.getvalue()
        assert "API RESPONSE" in output
        assert "SUCCESS 200" in output
        assert "Test User" in output
        # Token should be masked
        assert "abc123token" not in output
        assert "abc***en" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_api_response_error_logging(self, mock_stdout):
        """Test API response error logging"""
        self.logger.api_response("POST", "/api/auth/login", 401, error="Invalid credentials")
        output = mock_stdout.getvalue()
        assert "API RESPONSE" in output
        assert "ERROR 401" in output
        assert "Invalid credentials" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_sensitive_data_masking(self, mock_stdout):
        """Test sensitive data masking"""
        sensitive_data = {
            "email": "test@example.com",
            "password": "mypassword123",
            "token": "secret_token_here",
            "api_key": "apikey12345",
            "normal_field": "normal_value"
        }
        
        masked_data = self.logger._mask_sensitive_data(sensitive_data)
        
        # Check that sensitive fields are masked
        assert masked_data["password"] == "myp***23"
        assert masked_data["token"] == "sec***re"
        assert masked_data["api_key"] == "api***45"
        # Normal field should remain unchanged
        assert masked_data["normal_field"] == "normal_value"
        assert masked_data["email"] == "test@example.com"
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_validation_error_logging(self, mock_stdout):
        """Test validation error logging"""
        self.logger.validation_error("LoginForm", "email", "Invalid email format")
        output = mock_stdout.getvalue()
        assert "VALIDATION ERROR" in output
        assert "LoginForm" in output
        assert "email" in output
        assert "Invalid email format" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_performance_metric_logging(self, mock_stdout):
        """Test performance metric logging"""
        self.logger.performance_metric("database_query", 0.345, "APIClient")
        output = mock_stdout.getvalue()
        assert "PERFORMANCE" in output
        assert "database_query" in output
        assert "0.345s" in output
        assert "APIClient" in output
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_window_event_logging(self, mock_stdout):
        """Test window event logging"""
        self.logger.window_event("MainWindow", "opened", {"size": "800x600"})
        output = mock_stdout.getvalue()
        assert "WINDOW EVENT" in output
        assert "MainWindow" in output
        assert "opened" in output
        assert "800x600" in output
    
    def test_nested_sensitive_data_masking(self):
        """Test masking of nested sensitive data"""
        nested_data = {
            "user": {
                "name": "Test User",
                "credentials": {
                    "password": "secret123",
                    "token": "bearer_token"
                }
            },
            "api_key": "topSecret"
        }
        
        masked_data = self.logger._mask_sensitive_data(nested_data)
        
        assert masked_data["user"]["name"] == "Test User"
        assert masked_data["user"]["credentials"]["password"] == "sec***23"
        assert masked_data["user"]["credentials"]["token"] == "bea***en"
        assert masked_data["api_key"] == "top***et"

class TestConvenienceFunctions:
    
    @patch('utils.logger.logger')
    def test_log_user_action(self, mock_logger):
        log_user_action("test_action", "TestComponent", {"key": "value"})
        mock_logger.user_action.assert_called_once_with("test_action", "TestComponent", {"key": "value"})
    
    @patch('utils.logger.logger')
    def test_log_api_request(self, mock_logger):
        log_api_request("GET", "/api/test", {"param": "value"})
        mock_logger.api_request.assert_called_once_with("GET", "/api/test", {"param": "value"})
    
    @patch('utils.logger.logger')
    def test_log_api_response(self, mock_logger):
        log_api_response("GET", "/api/test", 200, {"result": "success"})
        mock_logger.api_response.assert_called_once_with("GET", "/api/test", 200, {"result": "success"}, None)