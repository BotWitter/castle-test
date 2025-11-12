"""
Cryptographic utilities for X.com authentication.
Handles XPFF header encryption and decryption.
"""

import binascii
import hashlib
from typing import Optional

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


class XPFFHeaderGenerator:
    """
    Generates and decrypts XPFF headers for X.com authentication.
    XPFF is an encrypted header containing device/browser fingerprint information.
    """

    def __init__(self, base_key: str):
        """
        Initialize the XPFF generator.

        Args:
            base_key: The base encryption key (hex string)
        """
        self.base_key = base_key

    def _derive_xpff_key(self, guest_id: str) -> bytes:
        """
        Derive the AES key from base key and guest ID.

        Args:
            guest_id: The guest ID from X.com session

        Returns:
            32-byte AES key derived from the combination
        """
        combined = self.base_key + guest_id
        return hashlib.sha256(combined.encode()).digest()

    def generate_xpff(self, plaintext: str, guest_id: str) -> str:
        """
        Generate encrypted XPFF header.

        Args:
            plaintext: JSON string containing device fingerprint data
            guest_id: The guest ID from X.com session

        Returns:
            Hex-encoded XPFF header (nonce + ciphertext + tag)
        """
        key = self._derive_xpff_key(guest_id)
        nonce = get_random_bytes(12)  # 96-bit nonce for GCM

        # AES-256-GCM encryption
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())

        # Concatenate: nonce (12 bytes) + ciphertext + tag (16 bytes)
        encrypted_data = nonce + ciphertext + tag
        return binascii.hexlify(encrypted_data).decode()

    def decode_xpff(self, hex_string: str, guest_id: str) -> str:
        """
        Decrypt XPFF header.

        Args:
            hex_string: Hex-encoded XPFF header
            guest_id: The guest ID from X.com session

        Returns:
            Decrypted plaintext JSON
        """
        key = self._derive_xpff_key(guest_id)
        raw = binascii.unhexlify(hex_string)

        # Extract components: nonce (12 bytes) + ciphertext + tag (16 bytes)
        nonce = raw[:12]
        ciphertext = raw[12:-16]
        tag = raw[-16:]

        # AES-256-GCM decryption
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)

        return plaintext.decode()


def get_device_fingerprint_json(user_agent: str, timestamp: int) -> str:
    """
    Generate device fingerprint JSON for XPFF header.

    Args:
        user_agent: Browser user agent string
        timestamp: Current timestamp in milliseconds

    Returns:
        JSON string with device fingerprint data
    """
    # Note: This is a simplified version. The actual fingerprint
    # may require additional fields depending on X.com's requirements
    return (
        '{"navigator_properties":{'
        '"hasBeenActive":"true",'
        f'"userAgent":"{user_agent}",'
        '"webdriver":"false"'
        f'}}'
        f'"created_at":{timestamp}'
        '}'
    )
