"""
HTTP client with proxy support for X.com authentication.
Handles TLS sessions and request proxying.
"""

import re
from typing import Optional

import tls_client

from .config import ProxyConfig, RequestsHeaders


class HTTPClient:
    """
    Manages HTTP requests with TLS fingerprinting and proxy support.
    Uses tls_client for browser-like TLS handshakes.
    """

    def __init__(
        self,
        client_identifier: str = "chrome_120",
        proxy_config: Optional[ProxyConfig] = None,
    ):
        """
        Initialize the HTTP client.

        Args:
            client_identifier: TLS client identifier (default: chrome_120)
            proxy_config: Optional proxy configuration
        """
        self.session = tls_client.Session(
            client_identifier=client_identifier,
            random_tls_extension_order=True,
        )
        self.proxy_config = proxy_config or ProxyConfig.from_env()

        # Apply proxy settings if configured
        if self.proxy_config.get_proxies_dict():
            self.session.proxies = self.proxy_config.get_proxies_dict()

    def get_login_page(self, headers: Optional[dict] = None) -> str:
        """
        Fetch the X.com login page.

        Args:
            headers: Optional custom headers

        Returns:
            HTML content of the login page
        """
        default_headers = RequestsHeaders.get_initial_headers(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
        )
        headers = headers or default_headers

        response = self.session.get("https://x.com/i/flow/login", headers=headers)
        return response.text

    def extract_guest_token(self, html_content: str) -> Optional[str]:
        """
        Extract guest token from login page HTML.

        Args:
            html_content: HTML content of the login page

        Returns:
            Guest token string or None if not found
        """
        return self._extract_between(html_content, "gt=", ";")

    def extract_value(self, text: str, start_marker: str, end_marker: str) -> Optional[str]:
        """
        Extract a value between two markers in text.

        Args:
            text: Text to search
            start_marker: Starting marker
            end_marker: Ending marker

        Returns:
            Extracted value or empty string if not found
        """
        return self._extract_between(text, start_marker, end_marker)

    @staticmethod
    def _extract_between(
        text: str, start_text: str, end_text: str
    ) -> Optional[str]:
        """
        Extract text between two delimiters.

        Args:
            text: Source text
            start_text: Start delimiter
            end_text: End delimiter

        Returns:
            Extracted text or None
        """
        try:
            start_index = text.find(start_text)
            if start_index == -1:
                return None

            start_index += len(start_text)
            end_index = text.find(end_text, start_index)
            if end_index == -1:
                return None

            result = text[start_index:end_index]
            return result.replace(" ", "").replace("\n", "")
        except Exception:
            return None

    @property
    def cookies(self):
        """Access session cookies."""
        return self.session.cookies

    @property
    def client(self):
        """Access underlying TLS client session."""
        return self.session
