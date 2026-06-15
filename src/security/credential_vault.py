"""DPAPI-backed credential vault for secure API key storage.

Binds credentials to the local Windows user account via Windows Credential
Manager. Replaces plaintext file-based key storage with OS-level encryption.
"""

import os
import logging
from typing import Optional

import keyring

logger = logging.getLogger(__name__)

_SERVICE_NAME = "SuperDiagnosticTool"
_KEY_ALIAS = "gemini_api_key"


class CredentialVault:
    """Manages API credentials through Windows DPAPI-backed storage.

    The Windows Credential Manager encrypts secrets at rest using the
    logged-in user's master key. Keys are invisible to other user
    accounts on the same machine.
    """

    @staticmethod
    def store(api_key: str) -> bool:
        """Persist an API key into the OS credential store.

        Args:
            api_key: The Gemini API key to store.

        Returns:
            True on success, False on backend failure.
        """
        try:
            keyring.set_password(_SERVICE_NAME, _KEY_ALIAS, api_key)
            return True
        except keyring.errors.KeyringError as exc:
            logger.warning("Credential store write failed: %s", exc)
            return False

    @staticmethod
    def retrieve() -> Optional[str]:
        """Retrieve the stored API key from the OS credential store.

        Returns:
            The API key string, or None if no key is stored.
        """
        try:
            return keyring.get_password(_SERVICE_NAME, _KEY_ALIAS)
        except keyring.errors.KeyringError as exc:
            logger.warning("Credential store read failed: %s", exc)
            return None

    @staticmethod
    def delete() -> bool:
        """Remove the stored API key from the OS credential store.

        Returns:
            True on success, False if the key did not exist or on error.
        """
        try:
            keyring.delete_password(_SERVICE_NAME, _KEY_ALIAS)
            return True
        except keyring.errors.PasswordDeleteError:
            return False
        except keyring.errors.KeyringError as exc:
            logger.warning("Credential store delete failed: %s", exc)
            return False

    @staticmethod
    def migrate_from_file(key_file_path: str) -> bool:
        """One-time migration from legacy plaintext key file to DPAPI vault.

        Reads the key from the file, stores it in the credential manager,
        then securely removes the plaintext file.

        Args:
            key_file_path: Absolute path to the legacy ``gemini.key`` file.

        Returns:
            True if migration succeeded, False otherwise.
        """
        if not os.path.isfile(key_file_path):
            return False

        try:
            with open(key_file_path, "r", encoding="utf-8") as fh:
                legacy_key = fh.read().strip()
        except OSError as exc:
            logger.warning("Could not read legacy key file: %s", exc)
            return False

        if not legacy_key:
            return False

        if not CredentialVault.store(legacy_key):
            return False

        try:
            os.remove(key_file_path)
            logger.info("Legacy key file removed after migration.")
        except OSError as exc:
            logger.warning("Could not remove legacy key file: %s", exc)

        return True
