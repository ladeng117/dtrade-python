"""
Main client class for DTrader API
"""

import requests
from typing import Optional, Dict, Any
from urllib.parse import urljoin

from .exceptions import (
    AuthenticationError, APIError, ConnectionError, TimeoutError, 
    ValidationError, RateLimitError
)


class DTraderClient:
    """Main client for interacting with DTrader API"""
    
    def __init__(self, host: str, port: int, api_key: str, timeout: int = 30):
        """
        Initialize DTrader client
        
        Args:
            host: Server hostname or IP address
            port: Server port
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.host = host
        self.port = port
        self.api_key = api_key
        self.timeout = timeout
        
        # Build base URL
        self.base_url = f"http://{host}:{port}"
        
        # Initialize session
        self.session = requests.Session()
        self.session.headers.update({
            "Auth": api_key,
            "Content-Type": "application/json",
            "User-Agent": "dtrade-python/0.1.0"
        })
        
        # Initialize sub-clients
        self._trading = None
        self._market = None
    
    @property
    def trading(self):
        """Access trading API"""
        if self._trading is None:
            from .trading import TradingAPI
            self._trading = TradingAPI(self)
        return self._trading
    
    @property
    def market(self):
        """Access market API"""
        if self._market is None:
            from .market import MarketAPI
            self._market = MarketAPI(self)
        return self._market
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
        
        Returns:
            Parsed JSON response
        
        Raises:
            ConnectionError: If connection fails
            AuthenticationError: If authentication fails
            APIError: If API returns an error
        """
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            # Handle HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            result = response.json()
            
            # Check for API-level errors
            if isinstance(result, dict) and result.get("code") != 0:
                error_msg = result.get("msg", "Unknown error")
                api_code = result.get("code")
                
                # Handle specific error codes
                if api_code == 401:
                    raise AuthenticationError(f"Authentication failed: {error_msg}")
                elif api_code == 429:
                    raise RateLimitError(f"Rate limit exceeded: {error_msg}")
                else:
                    raise APIError(
                        error_msg, 
                        status_code=response.status_code,
                        api_code=api_code
                    )
            
            return result
            
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to {url}: {str(e)}") from e
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Request to {url} timed out after {self.timeout} seconds") from e
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise AuthenticationError(f"Invalid API key: {response.text}") from e
            elif response.status_code == 429:
                raise RateLimitError(f"Rate limit exceeded: {response.text}") from e
            else:
                raise APIError(
                    f"HTTP Error {response.status_code}: {response.text}", 
                    status_code=response.status_code
                ) from e
        except ValueError as e:
            raise APIError(f"Invalid JSON response: {response.text if 'response' in locals() else 'No response'}") from e
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        return self._request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request"""
        return self._request("POST", endpoint, json=data)
    
    def close(self):
        """Close the client session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()