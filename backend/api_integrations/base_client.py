"""
Base API Client

Abstract base class for all external API integrations.
Provides common functionality for authentication, rate limiting, error handling, and retries.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API errors"""
    pass


class AuthenticationError(APIError):
    """Raised when authentication fails"""
    pass


class RateLimitError(APIError):
    """Raised when rate limit is exceeded"""
    pass


class BaseAPIClient(ABC):
    """
    Abstract base class for external API clients.
    
    Provides:
    - HTTP session management with retry logic
    - Rate limiting
    - Error handling
    - Authentication framework
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the API client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for API endpoints
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = self._create_session()
        self.rate_limit_remaining = None
        self.rate_limit_reset = None
        
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry logic.
        
        Returns:
            Configured requests.Session
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the API.
        
        Returns:
            True if authentication successful
            
        Raises:
            AuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get the current connection status.
        
        Returns:
            Dictionary with connection status information
        """
        pass
    
    def _handle_rate_limit(self, response: requests.Response):
        """
        Handle rate limiting based on response headers.
        
        Args:
            response: HTTP response object
        """
        # Check for rate limit headers (common patterns)
        if "X-RateLimit-Remaining" in response.headers:
            self.rate_limit_remaining = int(response.headers["X-RateLimit-Remaining"])
            
        if "X-RateLimit-Reset" in response.headers:
            reset_timestamp = int(response.headers["X-RateLimit-Reset"])
            self.rate_limit_reset = datetime.fromtimestamp(reset_timestamp)
            
        # If rate limited, wait until reset
        if response.status_code == 429:
            if self.rate_limit_reset:
                wait_seconds = (self.rate_limit_reset - datetime.now()).total_seconds()
                if wait_seconds > 0:
                    logger.warning(f"Rate limited. Waiting {wait_seconds} seconds...")
                    time.sleep(wait_seconds + 1)
            else:
                # Default wait if no reset time provided
                logger.warning("Rate limited. Waiting 60 seconds...")
                time.sleep(60)
                
            raise RateLimitError("API rate limit exceeded")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            headers: Additional headers
            
        Returns:
            Response JSON data
            
        Raises:
            APIError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=30
            )
            
            # Handle rate limiting
            self._handle_rate_limit(response)
            
            # Raise for HTTP errors
            response.raise_for_status()
            
            return response.json() if response.content else {}
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError(f"Authentication failed: {e}")
            elif e.response.status_code == 429:
                raise RateLimitError(f"Rate limit exceeded: {e}")
            else:
                raise APIError(f"HTTP error: {e}")
                
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}")
    
    def close(self):
        """Close the HTTP session"""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
