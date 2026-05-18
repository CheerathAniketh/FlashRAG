"""
Rate Limiting and Retry Logic for Groq API

Implements exponential backoff retry strategy for handling Groq rate limits (429).
Detects rate limit errors and retries with exponential backoff up to max attempts.
"""

import asyncio
import time
from typing import Callable, Any, Optional, TypeVar
from functools import wraps

T = TypeVar("T")


class RateLimitManager:
    """
    Manages rate limiting and retry logic for Groq API calls.
    
    Implements exponential backoff with configurable retry attempts.
    Detects 429 (rate limit) errors and gracefully handles retries.
    """
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 2.0) -> None:
        """
        Initialize the rate limit manager.
        
        Args:
            max_attempts: Maximum number of retry attempts (default: 3)
            base_delay: Base delay in seconds for exponential backoff (default: 2.0)
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
    
    def _get_retry_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay for given attempt number.
        
        Args:
            attempt: Attempt number (0-indexed)
            
        Returns:
            float: Delay in seconds (2^attempt * base_delay)
        """
        return (2 ** attempt) * self.base_delay
    
    def _is_rate_limit_error(self, error: Exception) -> bool:
        """
        Check if error is a rate limit error from Groq (429).
        
        Args:
            error: Exception to check
            
        Returns:
            bool: True if error is rate limit error, False otherwise
        """
        error_str = str(error).lower()
        
        # Check for 429 status code
        if "429" in error_str:
            return True
        
        # Check for rate limit keywords
        if any(keyword in error_str for keyword in ["rate limit", "too many requests", "quota"]):
            return True
        
        return False
    
    async def retry_with_backoff(
        self,
        async_func: Callable[..., Any],
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """
        Execute async function with exponential backoff retry on rate limit errors.
        
        Args:
            async_func: Async function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Any: Result from the async function
            
        Raises:
            RuntimeError: If all retry attempts fail
        """
        last_error = None
        
        for attempt in range(self.max_attempts):
            try:
                return await async_func(*args, **kwargs)
            
            except Exception as e:
                last_error = e
                
                # If not a rate limit error, fail immediately
                if not self._is_rate_limit_error(e):
                    raise
                
                # If this was the last attempt, raise the error
                if attempt == self.max_attempts - 1:
                    raise RuntimeError(
                        f"Groq API rate limit exceeded after {self.max_attempts} attempts. "
                        f"Please try again in a few minutes."
                    )
                
                # Calculate backoff delay and wait
                delay = self._get_retry_delay(attempt)
                await asyncio.sleep(delay)
        
        # Should not reach here, but handle just in case
        if last_error:
            raise last_error
    
    def retry_with_backoff_sync(
        self,
        sync_func: Callable[..., T],
        *args: Any,
        **kwargs: Any
    ) -> T:
        """
        Execute sync function with exponential backoff retry on rate limit errors.
        
        Args:
            sync_func: Sync function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Any: Result from the sync function
            
        Raises:
            RuntimeError: If all retry attempts fail
        """
        last_error = None
        
        for attempt in range(self.max_attempts):
            try:
                return sync_func(*args, **kwargs)
            
            except Exception as e:
                last_error = e
                
                # If not a rate limit error, fail immediately
                if not self._is_rate_limit_error(e):
                    raise
                
                # If this was the last attempt, raise the error
                if attempt == self.max_attempts - 1:
                    raise RuntimeError(
                        f"Groq API rate limit exceeded after {self.max_attempts} attempts. "
                        f"Please try again in a few minutes."
                    )
                
                # Calculate backoff delay and wait
                delay = self._get_retry_delay(attempt)
                time.sleep(delay)
        
        # Should not reach here, but handle just in case
        if last_error:
            raise last_error


# Global rate limiter instance
_rate_limiter: Optional[RateLimitManager] = None


def get_rate_limiter(max_attempts: int = 3) -> RateLimitManager:
    """
    Get or create the global rate limiter instance.
    
    Args:
        max_attempts: Maximum retry attempts (used only on first call)
        
    Returns:
        RateLimitManager: Global rate limiter instance
    """
    global _rate_limiter
    
    if _rate_limiter is None:
        _rate_limiter = RateLimitManager(max_attempts=max_attempts)
    
    return _rate_limiter
