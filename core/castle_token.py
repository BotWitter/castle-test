"""
Castle token generation for X.com authentication.
Castle tokens are security tokens required for specific API operations.
"""

import time
from typing import Optional

from .config import APIEndpoints, AuthConfig


class CastleTokenGenerator:
    """
    Generates and caches Castle tokens for X.com authentication.
    Tokens are cached for 60 seconds to avoid excessive API calls.

    Rate Limits:
    - Without API key: 3 requests/second, 100 requests/hour
    - With API key: Custom limits, higher quota, priority support

    Args:
        session: TLS client session for making requests
        api_key: Optional API key for higher rate limits
        user_agent: Browser user agent string
    """

    # Cache duration in seconds
    CACHE_DURATION = 60

    def __init__(
        self,
        session,
        api_key: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """Initialize the Castle token generator."""
        self.session = session
        self.api_key = api_key or AuthConfig.castle_api_key
        self.user_agent = user_agent or AuthConfig.user_agent

        # Cache storage
        self._cached_token: Optional[str] = None
        self._cached_cuid: Optional[str] = None
        self._token_timestamp: Optional[float] = None

    def _generate_cuid(self) -> str:
        """
        Generate a unique client identifier (CUID).

        Returns:
            32-character hexadecimal string (16 bytes)
            Example: 169c90ba59a6f01cc46e69d2669e080b
        """
        import secrets

        return secrets.token_hex(16)

    def generate_token(self) -> str:
        """
        Generate a new Castle token.

        Process:
        1. Generate a 32-character hexadecimal CUID
        2. Set __cuid cookie in the session
        3. Send POST request to castle.botwitter.com/generate-token
        4. Extract and cache the token

        Returns:
            The generated Castle token string

        Raises:
            Exception: If the API request fails or returns an error
        """
        # Generate new CUID
        self._cached_cuid = self._generate_cuid()

        # Set __cuid cookie for both domains
        self.session.cookies.set("__cuid", self._cached_cuid, domain=".x.com")
        self.session.cookies.set("__cuid", self._cached_cuid, domain=".twitter.com")

        # Prepare request payload
        payload = {
            "userAgent": self.user_agent,
            "cuid": self._cached_cuid,
        }

        # Prepare headers with optional API key authentication
        headers = {
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Send request to Castle token API
        response = self.session.post(
            APIEndpoints.CASTLE_TOKEN_GENERATE,
            json=payload,
            headers=headers,
        )

        # Extract token from response
        response_data = response.json()
        self._cached_token = response_data.get("token", "")
        self._token_timestamp = time.time()

        return self._cached_token

    def get_token(self) -> str:
        """
        Get cached token or generate a new one if expired.

        Cache expiration: 60 seconds

        Returns:
            Valid Castle token string
        """
        # Generate new token if not cached
        if self._cached_token is None or self._token_timestamp is None:
            return self.generate_token()

        # Check if token has expired (> 60 seconds old)
        if time.time() - self._token_timestamp > self.CACHE_DURATION:
            return self.generate_token()

        # Return cached valid token
        return self._cached_token

    @property
    def cuid(self) -> Optional[str]:
        """Get the current CUID."""
        return self._cached_cuid

    @property
    def token_timestamp(self) -> Optional[float]:
        """Get the timestamp of when the token was generated."""
        return self._token_timestamp
