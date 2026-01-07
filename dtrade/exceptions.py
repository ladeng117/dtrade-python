"""
Custom exceptions for dtrade-python
"""

from typing import Optional


class DTraderError(Exception):
    """Base exception for all dtrade errors"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class AuthenticationError(DTraderError):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed", error_code: str = "AUTH_ERROR"):
        super().__init__(message, error_code)


class APIError(DTraderError):
    """API error with detailed error information"""
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        status_code: Optional[int] = None,
        api_code: Optional[int] = None
    ):
        super().__init__(message, error_code)
        self.status_code = status_code
        self.api_code = api_code
    
    def __str__(self) -> str:
        details = []
        if self.error_code:
            details.append(f"code={self.error_code}")
        if self.status_code:
            details.append(f"status={self.status_code}")
        if self.api_code:
            details.append(f"api_code={self.api_code}")
        
        detail_str = ", ".join(details)
        return f"APIError({detail_str}): {self.message}"


class ConnectionError(DTraderError):
    """Raised when connection to server fails"""
    def __init__(self, message: str = "Connection failed", error_code: str = "CONNECTION_ERROR"):
        super().__init__(message, error_code)


class TimeoutError(DTraderError):
    """Raised when request times out"""
    def __init__(self, message: str = "Request timeout", error_code: str = "TIMEOUT_ERROR"):
        super().__init__(message, error_code)


class ValidationError(DTraderError):
    """Raised when input validation fails"""
    def __init__(self, message: str, field: Optional[str] = None, error_code: str = "VALIDATION_ERROR"):
        super().__init__(message, error_code)
        self.field = field
    
    def __str__(self) -> str:
        if self.field:
            return f"ValidationError(field='{self.field}'): {self.message}"
        return f"ValidationError: {self.message}"


class TradingError(DTraderError):
    """Raised when trading operations fail"""
    def __init__(self, message: str, error_code: str = "TRADING_ERROR"):
        super().__init__(message, error_code)


class MarketDataError(DTraderError):
    """Raised when market data operations fail"""
    def __init__(self, message: str, error_code: str = "MARKET_DATA_ERROR"):
        super().__init__(message, error_code)


class RateLimitError(DTraderError):
    """Raised when API rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded", error_code: str = "RATE_LIMIT_ERROR"):
        super().__init__(message, error_code)


class InsufficientFundsError(TradingError):
    """Raised when account has insufficient funds"""
    def __init__(self, message: str = "Insufficient funds", error_code: str = "INSUFFICIENT_FUNDS"):
        super().__init__(message, error_code)


class OrderNotFoundError(TradingError):
    """Raised when order is not found"""
    def __init__(self, message: str = "Order not found", error_code: str = "ORDER_NOT_FOUND"):
        super().__init__(message, error_code)


class InvalidOrderError(TradingError):
    """Raised when order parameters are invalid"""
    def __init__(self, message: str, error_code: str = "INVALID_ORDER"):
        super().__init__(message, error_code)