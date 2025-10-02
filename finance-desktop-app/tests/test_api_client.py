import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api.client import APIClient

class TestAPIClient:
    """Test cases for APIClient"""
    
    def setup_method(self):
        self.client = APIClient("http://localhost:8080")
    
    def test_init(self):
        assert self.client.base_url == "http://localhost:8080"
        assert self.client.token is None
        assert self.client.session is not None
        assert self.client.session.headers['Content-Type'] == 'application/json'
        assert self.client.session.headers['Accept'] == 'application/json'
    
    def test_base_url_normalization(self):
        client = APIClient("http://localhost:8080/")
        assert client.base_url == "http://localhost:8080"
    
    @patch('requests.Session.post')
    def test_login_success(self, mock_post):
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'token': 'test_token_123',
            'user': {'id': 1, 'email': 'test@example.com'}
        }
        mock_response.content = True
        mock_post.return_value = mock_response
        
        # Test login
        result = self.client.login('test@example.com', 'password123')
        
        # Assertions
        assert result['token'] == 'test_token_123'
        assert self.client.token == 'test_token_123'
        mock_post.assert_called_once()
    
    @patch('requests.Session.post')
    def test_register_success(self, mock_post):
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'message': 'User created successfully',
            'user': {'id': 1, 'email': 'test@example.com', 'name': 'Test User'}
        }
        mock_response.content = True
        mock_post.return_value = mock_response
        
        # Test register
        result = self.client.register('test@example.com', 'password123', 'Test User')
        
        # Assertions
        assert result['message'] == 'User created successfully'
        mock_post.assert_called_once()
    
    @patch('requests.Session.post')
    def test_login_failure(self, mock_post):
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'error': 'Invalid credentials'}
        mock_response.content = True
        mock_post.return_value = mock_response
        
        # Test login failure
        with pytest.raises(Exception, match="Unauthorized"):
            self.client.login('test@example.com', 'wrongpassword')
    
    @patch('requests.Session.get')
    def test_connection_error(self, mock_get):
        """Test connection error handling"""
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError("Connection failed")
        
        result = self.client.test_connection()
        assert result == False
    
    def test_is_authenticated(self):
        assert self.client.is_authenticated() == False
        
        self.client.token = "test_token"
        assert self.client.is_authenticated() == True
    
    def test_logout(self):
        # Set token first
        self.client.token = "test_token"
        self.client.session.headers['Authorization'] = 'Bearer test_token'
        
        # Logout
        self.client.logout()
        
        # Check token is cleared
        assert self.client.token is None
        assert 'Authorization' not in self.client.session.headers
    
    @patch('requests.Session.get')
    def test_get_transactions(self, mock_get):
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'transactions': [
                {'id': 1, 'description': 'Test transaction', 'amount': 100.0}
            ]
        }
        mock_response.content = True
        mock_get.return_value = mock_response
        
        # Set token
        self.client.token = "test_token"
        
        # Test get transactions
        result = self.client.get_transactions()
        
        # Assertions
        assert 'transactions' in result
        assert len(result['transactions']) == 1
        mock_get.assert_called_once()