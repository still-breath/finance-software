"""
API Client for Finance Desktop Application
Handles communication with the Go backend server
"""

import requests
import json
import time
from typing import Dict, Any, Optional
from requests.exceptions import RequestException, ConnectionError, Timeout
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.logger import log_api_request, log_api_response, log_app_event

class APIClient:
    """API client for communicating with finance backend"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                      headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to backend"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        # Log the request
        log_api_request(method.upper(), endpoint, data)
        
        # Add auth token if available
        if self.token:
            self.session.headers['Authorization'] = f'Bearer {self.token}'
        
        # Add additional headers if provided
        if headers:
            self.session.headers.update(headers)
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=10)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, timeout=10)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Calculate request duration
            duration = time.time() - start_time
            
            # Handle response
            if response.status_code in [200, 201]:
                response_data = response.json() if response.content else {}
                log_api_response(method.upper(), endpoint, response.status_code, response_data)
                return response_data
            elif response.status_code == 401:
                error_msg = "Unauthorized - please login again"
                log_api_response(method.upper(), endpoint, response.status_code, error=error_msg)
                raise Exception(error_msg)
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                error_msg = f"Bad request: {error_data.get('error', 'Unknown error')}"
                log_api_response(method.upper(), endpoint, response.status_code, error=error_msg)
                raise Exception(error_msg)
            elif response.status_code == 500:
                error_msg = "Server error - please try again later"
                log_api_response(method.upper(), endpoint, response.status_code, error=error_msg)
                raise Exception(error_msg)
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                log_api_response(method.upper(), endpoint, response.status_code, error=error_msg)
                raise Exception(error_msg)
                
        except ConnectionError as e:
            error_msg = "Cannot connect to server - please check if backend is running"
            log_api_response(method.upper(), endpoint, 0, error=error_msg)
            raise Exception(error_msg)
        except Timeout as e:
            error_msg = "Request timeout - server is not responding"
            log_api_response(method.upper(), endpoint, 0, error=error_msg)
            raise Exception(error_msg)
        except RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            log_api_response(method.upper(), endpoint, 0, error=error_msg)
            raise Exception(error_msg)
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user and store auth token"""
        log_app_event("login_attempt", "APIClient", {"email": email})
        
        data = {
            "email": email,
            "password": password
        }
        
        result = self._make_request('POST', '/api/auth/login', data)
        
        # Store token for future requests
        if 'token' in result:
            self.token = result['token']
            log_app_event("login_success", "APIClient", {"email": email})
        else:
            log_app_event("login_failed", "APIClient", {"email": email, "reason": "no_token_in_response"})
            
        return result
    
    def register(self, email: str, password: str, name: str) -> Dict[str, Any]:
        """Register new user"""
        data = {
            "email": email,
            "password": password,
            "name": name
        }
        
        return self._make_request('POST', '/api/auth/register', data)
    
    def logout(self):
        """Logout user and clear token"""
        log_app_event("logout_attempt", "APIClient")
        
        if self.token:
            try:
                self._make_request('POST', '/api/auth/logout')
            except Exception as e:
                log_app_event("logout_api_error", "APIClient", {"error": str(e)})
            finally:
                self.token = None
                if 'Authorization' in self.session.headers:
                    del self.session.headers['Authorization']
                log_app_event("logout_success", "APIClient")
    
    def get_transactions(self) -> Dict[str, Any]:
        return self._make_request('GET', '/api/transactions')
    
    def create_transaction(self, transaction_data: Dict) -> Dict[str, Any]:
        return self._make_request('POST', '/api/transactions', transaction_data)
    
    def update_transaction(self, transaction_id: int, transaction_data: Dict) -> Dict[str, Any]:
        return self._make_request('PUT', f'/api/transactions/{transaction_id}', transaction_data)
    
    def delete_transaction(self, transaction_id: int) -> Dict[str, Any]:
        return self._make_request('DELETE', f'/api/transactions/{transaction_id}')
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        return self._make_request('GET', '/api/dashboard')
    
    def is_authenticated(self) -> bool:
        return self.token is not None
    
    def test_connection(self) -> bool:
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False