"""Secure token storage using encryption."""

import base64
import json
import os
from pathlib import Path
from typing import Optional


class SecureStorage:
    """Secure storage for sensitive tokens."""

    def __init__(self, storage_dir: Path):
        """Initialize secure storage.

        Args:
            storage_dir: Directory for storing encrypted tokens.
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.token_file = self.storage_dir / "tokens.enc"
        self._cipher = None

    def _get_cipher(self):
        """Get or create cipher for encryption."""
        if self._cipher is None:
            try:
                from cryptography.fernet import Fernet
                from cryptography.hazmat.primitives import hashes
                from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

                # Use a key derived from machine-specific info
                machine_id = f"{os.environ.get('USERNAME', 'user')}{os.environ.get('COMPUTERNAME', 'host')}"

                # Use a fixed salt for simplicity
                salt = b'ai_scraper_salt_v1'

                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )

                key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
                self._cipher = Fernet(key)
            except ImportError:
                # Fallback to base64 encoding if cryptography not available
                self._cipher = None

        return self._cipher

    def store_token(self, name: str, token: str) -> None:
        """Store a token securely.

        Args:
            name: Token name/identifier.
            token: Token value to store.
        """
        cipher = self._get_cipher()

        # Load existing tokens
        tokens = self._load_tokens()

        # Add/update token
        tokens[name] = token

        # Encrypt and save
        data = json.dumps(tokens)
        if cipher:
            encrypted = cipher.encrypt(data.encode())
            self.token_file.write_bytes(encrypted)
        else:
            # Fallback: base64 encode
            encoded = base64.b64encode(data.encode())
            self.token_file.write_bytes(encoded)

    def get_token(self, name: str) -> Optional[str]:
        """Retrieve a stored token.

        Args:
            name: Token name/identifier.

        Returns:
            Token value or None if not found.
        """
        tokens = self._load_tokens()
        return tokens.get(name)

    def delete_token(self, name: str) -> None:
        """Delete a stored token.

        Args:
            name: Token name/identifier.
        """
        tokens = self._load_tokens()
        if name in tokens:
            del tokens[name]

            cipher = self._get_cipher()
            data = json.dumps(tokens)

            if cipher:
                encrypted = cipher.encrypt(data.encode())
                self.token_file.write_bytes(encrypted)
            else:
                encoded = base64.b64encode(data.encode())
                self.token_file.write_bytes(encoded)

    def _load_tokens(self) -> dict:
        """Load tokens from encrypted storage."""
        if not self.token_file.exists():
            return {}

        try:
            cipher = self._get_cipher()
            data = self.token_file.read_bytes()

            if cipher:
                decrypted = cipher.decrypt(data)
                return json.loads(decrypted.decode())
            else:
                # Fallback: base64 decode
                decoded = base64.b64decode(data)
                return json.loads(decoded.decode())
        except Exception:
            return {}
