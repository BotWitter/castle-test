"""
X.com login flow orchestration.
Manages the multi-step authentication process.
"""

import json
import logging
import time
from typing import Optional, Dict, Any

from .castle_token import CastleTokenGenerator
from .config import (
    APIEndpoints,
    AuthConfig,
    EncryptionConfig,
    FlowConfig,
    RequestsHeaders,
)
from .crypto import XPFFHeaderGenerator
from .http_client import HTTPClient


class LoginFlowOrchestrator:
    """
    Orchestrates the complete X.com login flow.
    Handles multiple authentication steps with proper state management.
    """

    def __init__(
        self,
        http_client: HTTPClient,
        auth_config: Optional[AuthConfig] = None,
        encryption_config: Optional[EncryptionConfig] = None,
    ):
        """
        Initialize the login flow orchestrator.

        Args:
            http_client: HTTPClient instance for making requests
            auth_config: Authentication configuration
            encryption_config: Encryption configuration
        """
        self.http_client = http_client
        self.auth_config = auth_config or AuthConfig()
        self.encryption_config = encryption_config or EncryptionConfig()

        # State tracking
        self.guest_id: Optional[str] = None
        self.guest_token: Optional[str] = None
        self.flow_token: Optional[str] = None
        self.xpff_generator = XPFFHeaderGenerator(self.encryption_config.base_key)
        self.castle_generator = CastleTokenGenerator(
            http_client.client,
            api_key=self.auth_config.castle_api_key,
            user_agent=self.auth_config.user_agent,
        )

        # Logging
        self.logger = logging.getLogger(__name__)

    def step_1_fetch_login_page(self) -> bool:
        """
        Step 1: Fetch login page to get guest ID and token.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Step 1: Fetching login page...")
            html = self.http_client.get_login_page()

            # Extract guest ID from cookies
            self.guest_id = self.http_client.cookies.get("guest_id")
            if not self.guest_id:
                self.logger.error("Failed to extract guest_id from cookies")
                return False

            # Extract guest token from HTML
            self.guest_token = self.http_client.extract_guest_token(html)
            if not self.guest_token:
                self.logger.error("Failed to extract guest_token from HTML")
                return False

            self.logger.info(f"✓ Guest ID: {self.guest_id}")
            self.logger.info(f"✓ Guest Token: {self.guest_token[:20]}...")
            return True
        except Exception as e:
            self.logger.error(f"Step 1 failed: {e}")
            return False

    def step_2_initialize_flow(self) -> bool:
        """
        Step 2: Initialize login flow and get flow token.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Step 2: Initializing login flow...")

            if not self.guest_token:
                self.logger.error("Guest token not available")
                return False

            # Generate XPFF header
            xpff_plain = json.dumps({
                "navigator_properties": {
                    "hasBeenActive": "true",
                    "userAgent": self.auth_config.user_agent,
                    "webdriver": "false",
                },
                "created_at": int(time.time() * 1000),
            })

            xpff_encrypted = self.xpff_generator.generate_xpff(
                xpff_plain, self.guest_id
            )

            # Prepare headers
            headers = RequestsHeaders.get_api_headers(
                user_agent=self.auth_config.user_agent,
                bearer_token=self.auth_config.bearer_token,
                guest_token=self.guest_token,
                xpff_header=xpff_encrypted,
                transaction_id=self._generate_transaction_id(),
            )

            # Prepare payload
            payload = {
                "input_flow_data": {
                    "flow_context": {
                        "debug_overrides": {},
                        "start_location": {"location": "manual_link"},
                    }
                },
                "subtask_versions": FlowConfig.SUBTASK_VERSIONS,
            }

            # Send request
            response = self.http_client.client.post(
                APIEndpoints.ONBOARDING_TASK,
                headers=headers,
                params={"flow_name": "login"},
                data=json.dumps(payload, separators=(",", ":")),
            )

            response_data = response.json()
            self.flow_token = response_data.get("flow_token")

            if not self.flow_token:
                self.logger.error("Failed to get flow_token from response")
                self.logger.debug(f"Response: {response_data}")
                return False

            self.logger.info(f"✓ Flow Token: {self.flow_token[:20]}...")
            return True
        except Exception as e:
            self.logger.error(f"Step 2 failed: {e}")
            return False

    def step_3_submit_js_instrumentation(self) -> bool:
        """
        Step 3: Submit JavaScript instrumentation response.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Step 3: Submitting JS instrumentation...")

            if not self.flow_token:
                self.logger.error("Flow token not available")
                return False

            # Prepare instrumentation response
            payload = {
                "flow_token": self.flow_token,
                "subtask_inputs": [
                    {
                        "subtask_id": "LoginJsInstrumentationSubtask",
                        "js_instrumentation": {
                            "response": json.dumps({
                                "rf": {
                                    "a936fafa6cfd8202f09b567899c51612b7d30988859e748fe6c46b4673f145af": 7,
                                    "afa4f9b3f6903b6940c5b4c3686de73feb8ebcec5d39b7cd5f778397bdd8af02": 0,
                                    "a24857ae70f173a2c9aa83f2302c75957e38970b12c3d517edea6b766f0c8c57": 0,
                                    "d9cd75556906d90d377a7bd862adb0bb6c332902a7c65f83fa8a7734368d5185": -238,
                                },
                                "s": "559pFstyTd4CwueiAS_hrsdrXwumoF-s7m_QeYEam0oRTQL9p13Qn93er2rC4Fdm9fT4-AUfM8bQLm9A75DUkLPVzXYtP1iSkwFRwy0Q5U1YAabIfMdm6Zw9dvhF7_IClU10JgC7tqBjT_6iSgaPzdNWFoTO1gnYod1FiIfWHwQF4DI7lpsf90ZhyJg0fjN70sAf94DgiJYyQUxF3EYaXfM05DDsa80AsNmr945WZW0A5yfQB9SyyQW0m3HkYGA7ne85l1qtY9XFK40N9AVnNV6IV-zqrCNT3Q196wllYwr3wPeeVrE6WjuGYsjbnYJI8TA3Qd8frl29Vv91kYMrfgAAAZp3SiVN",
                            }),
                            "link": "next_link",
                        },
                    }
                ],
            }

            xpff_encrypted = self.xpff_generator.generate_xpff(
                json.dumps({"navigator_properties": {
                    "hasBeenActive": "true",
                    "userAgent": self.auth_config.user_agent,
                    "webdriver": "false",
                }}),
                self.guest_id,
            )

            headers = RequestsHeaders.get_api_headers(
                user_agent=self.auth_config.user_agent,
                bearer_token=self.auth_config.bearer_token,
                guest_token=self.guest_token,
                xpff_header=xpff_encrypted,
                transaction_id=self._generate_transaction_id(),
            )

            response = self.http_client.client.post(
                APIEndpoints.ONBOARDING_TASK,
                headers=headers,
                data=json.dumps(payload, separators=(",", ":")),
            )

            response_data = response.json()
            new_flow_token = response_data.get("flow_token")

            if new_flow_token:
                self.flow_token = new_flow_token
                self.logger.info("✓ JS instrumentation submitted")
                return True

            self.logger.error("Failed to get new flow_token after JS instrumentation")
            return False
        except Exception as e:
            self.logger.error(f"Step 3 failed: {e}")
            return False

    def step_4_submit_user_identifier(self, username: str) -> bool:
        """
        Step 4: Submit user identifier (username/email).

        Args:
            username: The username or email to submit

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Step 4: Submitting user identifier ({username})...")

            if not self.flow_token:
                self.logger.error("Flow token not available")
                return False

            # Retry loop for submitting user identifier
            max_retries = 3
            for attempt in range(max_retries):
                # Generate Castle token (force new token on retries)
                if attempt > 0:
                    self.logger.info(f"Retry attempt {attempt + 1}/{max_retries}: Generating new Castle token...")
                    # Force new token generation by bypassing cache check if possible, 
                    # or just calling generate_token directly if the method is exposed.
                    # Looking at CastleTokenGenerator, generate_token() is public.
                    castle_token = self.castle_generator.generate_token()
                else:
                    castle_token = self.castle_generator.get_token()

                if not castle_token:
                    self.logger.error("Failed to generate Castle token")
                    if attempt == max_retries - 1:
                        return False
                    continue

                # Prepare payload
                payload = {
                    "flow_token": self.flow_token,
                    "subtask_inputs": [
                        {
                            "subtask_id": "LoginEnterUserIdentifierSSO",
                            "settings_list": {
                                "setting_responses": [
                                    {
                                        "key": "user_identifier",
                                        "response_data": {
                                            "text_data": {
                                                "result": username,
                                            }
                                        },
                                    }
                                ],
                                "link": "next_link",
                                "castle_token": castle_token,
                            },
                        }
                    ],
                }

                xpff_encrypted = self.xpff_generator.generate_xpff(
                    json.dumps({"navigator_properties": {
                        "hasBeenActive": "true",
                        "userAgent": self.auth_config.user_agent,
                        "webdriver": "false",
                    }}),
                    self.guest_id,
                )

                headers = RequestsHeaders.get_api_headers(
                    user_agent=self.auth_config.user_agent,
                    bearer_token=self.auth_config.bearer_token,
                    guest_token=self.guest_token,
                    xpff_header=xpff_encrypted,
                    transaction_id=self._generate_transaction_id(),
                )

                response = self.http_client.client.post(
                    APIEndpoints.ONBOARDING_TASK,
                    headers=headers,
                    data=json.dumps(payload, separators=(",", ":")),
                )

                if response.status_code == 200:
                    self.logger.info(f"✓ User identifier submitted (Status: 200)")
                    return True
                else:
                    self.logger.warning(
                        f"Failed to submit user identifier (Status: {response.status_code}, Attempt: {attempt + 1}/{max_retries})"
                    )
                    self.logger.debug(f"Response: {response.text}")
            
            self.logger.error("Failed to submit user identifier after all retries")
            return False
        except Exception as e:
            self.logger.error(f"Step 4 failed: {e}")
            return False

    def execute_login_flow(self, username: str) -> bool:
        """
        Execute the complete login flow.

        Args:
            username: Username or email to authenticate with

        Returns:
            True if all steps completed successfully, False otherwise
        """
        self.logger.info("=" * 50)
        self.logger.info("Starting X.com Login Flow")
        self.logger.info("=" * 50)

        steps = [
            ("Fetch Login Page", self.step_1_fetch_login_page),
            ("Initialize Flow", self.step_2_initialize_flow),
            ("Submit JS Instrumentation", self.step_3_submit_js_instrumentation),
            ("Submit User Identifier", lambda: self.step_4_submit_user_identifier(username)),
        ]

        for step_name, step_func in steps:
            if not step_func():
                self.logger.error(f"Login flow failed at: {step_name}")
                return False

        self.logger.info("=" * 50)
        self.logger.info("✓ Login flow completed successfully!")
        self.logger.info("=" * 50)
        return True

    @staticmethod
    def _generate_transaction_id() -> str:
        """Generate a random transaction ID."""
        import secrets
        return secrets.token_urlsafe(32)
