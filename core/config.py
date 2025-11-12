"""
Configuration module for Castle Token authentication system.
Centralized settings and constants.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProxyConfig:
    """Proxy configuration settings."""
    http: Optional[str] = None
    https: Optional[str] = None

    @classmethod
    def from_env(cls) -> "ProxyConfig":
        """Load proxy settings from environment variables."""
        return cls(
            http=os.getenv("HTTP_PROXY") or os.getenv("http_proxy"),
            https=os.getenv("HTTPS_PROXY") or os.getenv("https_proxy"),
        )

    def get_proxies_dict(self) -> Optional[dict]:
        """Get proxies as dictionary for requests library."""
        if not self.http and not self.https:
            return None
        return {
            "http": self.http,
            "https": self.https,
        }


@dataclass
class AuthConfig:
    """Authentication configuration."""
    bearer_token: str = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
    castle_api_key: str = ""  # Optional API key for Castle token generation
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"


@dataclass
class EncryptionConfig:
    """Encryption configuration for XPFF header."""
    base_key: str = "0e6be1f1e21ffc33590b888fd4dc81b19713e570e805d4e5df80a493c9571a05"


class RequestsHeaders:
    """Pre-configured request headers."""

    @staticmethod
    def get_initial_headers(user_agent: str) -> dict:
        """Headers for initial login page request."""
        return {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=0, i",
            "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": user_agent,
        }

    @staticmethod
    def get_api_headers(user_agent: str, bearer_token: str, guest_token: str,
                       xpff_header: str, transaction_id: str) -> dict:
        """Headers for API requests."""
        return {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {bearer_token}",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://x.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://x.com/",
            "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": user_agent,
            "x-client-transaction-id": transaction_id,
            "x-guest-token": guest_token,
            "x-twitter-active-user": "yes",
            "x-twitter-client-language": "en",
            "x-xp-forwarded-for": xpff_header,
        }


class APIEndpoints:
    """API endpoint URLs."""
    BASE_URL = "https://api.x.com/1.1"
    LOGIN_PAGE = "https://x.com/i/flow/login"
    ONBOARDING_TASK = f"{BASE_URL}/onboarding/task.json"
    CASTLE_TOKEN_GENERATE = "https://castle.botwitter.com/generate-token"


class FlowConfig:
    """Login flow configuration."""
    # Subtask versions - required for the initial flow request
    SUBTASK_VERSIONS = {
        "action_list": 2,
        "alert_dialog": 1,
        "app_download_cta": 1,
        "check_logged_in_account": 1,
        "choice_selection": 3,
        "contacts_live_sync_permission_prompt": 0,
        "cta": 7,
        "email_verification": 2,
        "end_flow": 1,
        "enter_date": 1,
        "enter_email": 2,
        "enter_password": 5,
        "enter_phone": 2,
        "enter_recaptcha": 1,
        "enter_text": 5,
        "enter_username": 2,
        "generic_urt": 3,
        "in_app_notification": 1,
        "interest_picker": 3,
        "js_instrumentation": 1,
        "menu_dialog": 1,
        "notifications_permission_prompt": 2,
        "open_account": 2,
        "open_home_timeline": 1,
        "open_link": 1,
        "phone_verification": 4,
        "privacy_options": 1,
        "security_key": 3,
        "select_avatar": 4,
        "select_banner": 2,
        "settings_list": 7,
        "show_code": 1,
        "sign_up": 2,
        "sign_up_review": 4,
        "tweet_selection_urt": 1,
        "update_users": 1,
        "upload_media": 1,
        "user_recommendations_list": 4,
        "user_recommendations_urt": 1,
        "wait_spinner": 3,
        "web_modal": 1,
    }
