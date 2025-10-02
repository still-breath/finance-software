"""
API Client for Finance Desktop Application
Handles communication with the Go backend server
"""

import requests
import json
from typing import Dict, Any, Optional
from requests.exceptions import RequestException, ConnectionError, Timeout

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
            
            # Handle response
            if response.status_code == 200:
                return response.json() if response.content else {}
            elif response.status_code == 201:
                return response.json() if response.content else {}
            elif response.status_code == 401:
                raise Exception("Unauthorized - please login again")
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                raise Exception(f"Bad request: {error_data.get('error', 'Unknown error')}")
            elif response.status_code == 500:
                raise Exception("Server error - please try again later")
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except ConnectionError:
            raise Exception("Cannot connect to server - please check if backend is running")
        except Timeout:
            raise Exception("Request timeout - server is not responding")
        except RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user and store auth token"""
        data = {
            "email": email,
            "password": password
        }
        
        result = self._make_request('POST', '/api/auth/login', data)
        
        # Store token for future requests
        if 'token' in result:
            self.token = result['token']
            
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
        if self.token:
            try:
                self._make_request('POST', '/api/auth/logout')
            except:
                pass  # Ignore errors during logout
            finally:
                self.token = None
                if 'Authorization' in self.session.headers:
                    del self.session.headers['Authorization']
    
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