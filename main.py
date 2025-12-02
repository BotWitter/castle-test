"""
X.com Login Flow - Main Entry Point

A professional, clean implementation of X.com authentication flow
with multi-step login, proxy support, and Castle token integration.

Usage:
    python main.py [username] [--proxy http://proxy:port]

Example:
    python main.py elonmuskcr
    python main.py user@example.com --proxy http://127.0.0.1:8080
"""

import argparse
import logging
import sys
from typing import Optional

from core.config import ProxyConfig
from core.http_client import HTTPClient
from core.login_flow import LoginFlowOrchestrator


def setup_logging(debug: bool = False) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        debug: Enable debug-level logging

    Returns:
        Configured logger instance
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="X.com Login Flow - Multi-step authentication with Castle token support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py elonmuskcr
  python main.py user@example.com --proxy http://127.0.0.1:8080
  python main.py user@example.com --debug
        """,
    )

    parser.add_argument(
        "username",
        help="Username or email address to authenticate with",
    )
    parser.add_argument(
        "--proxy",
        type=str,
        default=None,
        help="HTTP/HTTPS proxy URL (e.g., http://127.0.0.1:8080)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug-level logging",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Optional API key for Castle token generation",
    )

    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the application.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Parse arguments
    args = parse_arguments()
    logger = setup_logging(debug=args.debug)

    try:
        # Display banner
        logger.info("=" * 70)
        logger.info("X.com Login Flow - Multi-step Authentication")
        logger.info("=" * 70)

        # Configure proxy
        proxy_config = ProxyConfig()
        if args.proxy:
            proxy_parts = args.proxy.replace("://", "://").split("://")
            if len(proxy_parts) == 2:
                scheme, url = proxy_parts
                if scheme.lower() == "http":
                    proxy_config.http = args.proxy
                elif scheme.lower() == "https":
                    proxy_config.https = args.proxy
                else:
                    logger.warning(f"Unknown proxy scheme: {scheme}")
            logger.info(f"Using proxy: {args.proxy}")

        # Initialize HTTP client
        logger.info("Initializing HTTP client with TLS fingerprinting...")
        http_client = HTTPClient(
            client_identifier="chrome_120",
            proxy_config=proxy_config,
        )

        # Initialize login flow
        logger.info("Initializing login flow orchestrator...")
        login_flow = LoginFlowOrchestrator(http_client)

        # Override API key if provided
        if args.api_key:
            login_flow.castle_generator.api_key = args.api_key
            logger.info("Using custom API key for Castle token generation")
        else:
            logger.warning("No API key provided for Castle token generation, --api-key <api_key> required")
            return 1

        # Execute login flow
        success = login_flow.execute_login_flow(args.username)

        if success:
            logger.info("✓ Authentication flow completed successfully!")
            return 0
        else:
            logger.error("✗ Authentication flow failed")
            return 1

    except KeyboardInterrupt:
        logger.warning("\nOperation cancelled by user")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
