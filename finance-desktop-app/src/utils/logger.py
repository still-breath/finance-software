"""
Logging utilities for Finance Desktop Application
Provides comprehensive logging for user actions, API calls, and application events
"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import json

class ColorFormatter(logging.Formatter):
    """Custom formatter to add colors to log output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'API_REQUEST': '\033[34m', # Blue
        'API_RESPONSE': '\033[96m', # Light Cyan
        'USER_ACTION': '\033[92m', # Light Green
        'RESET': '\033[0m'        # Reset color
    }
    
    def format(self, record):
        if hasattr(record, 'log_type'):
            color = self.COLORS.get(record.log_type, self.COLORS['INFO'])
        else:
            color = self.COLORS.get(record.levelname, self.COLORS['INFO'])
        
        # Format the message
        formatted = super().format(record)
        return f"{color}{formatted}{self.COLORS['RESET']}"

class FinanceLogger:
    """Central logging system for the Finance application"""
    
    def __init__(self, name: str = "FinanceApp"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = ColorFormatter(
            '%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(self._format_message(message, **kwargs))
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(self._format_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(self._format_message(message, **kwargs))
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(self._format_message(message, **kwargs))
    
    def user_action(self, action: str, component: str, details: Optional[Dict] = None):
        """Log user action"""
        extra_info = {'log_type': 'USER_ACTION'}
        message = f"USER ACTION | {component} | {action}"
        
        if details:
            details_str = json.dumps(details, indent=2, default=str)
            message += f"\n   Details: {details_str}"
        
        self.logger.info(message, extra=extra_info)
    
    def api_request(self, method: str, endpoint: str, data: Optional[Dict] = None):
        """Log API request"""
        extra_info = {'log_type': 'API_REQUEST'}
        message = f"API REQUEST | {method} {endpoint}"
        
        if data:
            # Mask sensitive data
            safe_data = self._mask_sensitive_data(data)
            data_str = json.dumps(safe_data, indent=2, default=str)
            message += f"\n   Data: {data_str}"
        
        self.logger.info(message, extra=extra_info)
    
    def api_response(self, method: str, endpoint: str, status_code: int, 
                    response_data: Optional[Dict] = None, error: Optional[str] = None):
        """Log API response"""
        extra_info = {'log_type': 'API_RESPONSE'}
        
        if error:
            message = f"API RESPONSE | {method} {endpoint} | ERROR {status_code}"
            message += f"\n   Error: {error}"
            self.logger.error(message, extra=extra_info)
        else:
            message = f"API RESPONSE | {method} {endpoint} | SUCCESS {status_code}"
            
            if response_data:
                # Mask sensitive data in response
                safe_data = self._mask_sensitive_data(response_data)
                data_str = json.dumps(safe_data, indent=2, default=str)
                message += f"\n   Response: {data_str}"
            
            self.logger.info(message, extra=extra_info)
    
    def app_event(self, event: str, component: str, details: Optional[Dict] = None):
        """Log application event"""
        message = f"⚡ APP EVENT | {component} | {event}"
        
        if details:
            details_str = json.dumps(details, indent=2, default=str)
            message += f"\n   Details: {details_str}"
        
        self.logger.info(message)
    
    def window_event(self, window: str, event: str, details: Optional[Dict] = None):
        """Log window/UI event"""
        message = f"WINDOW EVENT | {window} | {event}"
        
        if details:
            details_str = json.dumps(details, indent=2, default=str)
            message += f"\n   Details: {details_str}"
        
        self.logger.info(message)
    
    def validation_error(self, component: str, field: str, error: str):
        """Log validation error"""
        message = f"VALIDATION ERROR | {component} | {field}: {error}"
        self.logger.warning(message)
    
    def performance_metric(self, operation: str, duration: float, component: str):
        """Log performance metric"""
        message = f"PERFORMANCE | {component} | {operation} took {duration:.3f}s"
        self.logger.info(message)
    
    def _format_message(self, message: str, **kwargs) -> str:
        """Format message with additional context"""
        if kwargs:
            context_str = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            return f"{message} | {context_str}"
        return message
    
    def _mask_sensitive_data(self, data: Dict) -> Dict:
        """Mask sensitive data in logs"""
        if not isinstance(data, dict):
            return data
        
        sensitive_keys = ['password', 'token', 'secret', 'key', 'auth', 'credential']
        masked_data = {}
        
        for key, value in data.items():
            if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                if isinstance(value, str) and len(value) > 0:
                    masked_data[key] = f"{value[:3]}***{value[-2:]}" if len(value) > 5 else "***"
                else:
                    masked_data[key] = "***"
            elif isinstance(value, dict):
                masked_data[key] = self._mask_sensitive_data(value)
            else:
                masked_data[key] = value
        
        return masked_data

# Global logger instance
logger = FinanceLogger()

# Convenience functions
def log_user_action(action: str, component: str, details: Optional[Dict] = None):
    logger.user_action(action, component, details)

def log_api_request(method: str, endpoint: str, data: Optional[Dict] = None):
    logger.api_request(method, endpoint, data)

def log_api_response(method: str, endpoint: str, status_code: int, 
                    response_data: Optional[Dict] = None, error: Optional[str] = None):
    logger.api_response(method, endpoint, status_code, response_data, error)

def log_app_event(event: str, component: str, details: Optional[Dict] = None):
    logger.app_event(event, component, details)

def log_window_event(window: str, event: str, details: Optional[Dict] = None):
    logger.window_event(window, event, details)

def log_validation_error(component: str, field: str, error: str):
    logger.validation_error(component, field, error)

def log_performance_metric(operation: str, duration: float, component: str):
    logger.performance_metric(operation, duration, component)