"""Cryptography utilities for credential encryption."""

from cryptography.fernet import Fernet


class CredentialManager:
    """
    Manages encryption and decryption of database credentials.
    
    Uses Fernet symmetric encryption for secure credential storage.
    """

    def __init__(self, encryption_key: str):
        """
        Initialize credential manager.
        
        Args:
            encryption_key: Base64-encoded Fernet encryption key
        """
        self.cipher = Fernet(encryption_key.encode())

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Encrypted string (base64-encoded)
        """
        encrypted_bytes = self.cipher.encrypt(plaintext.encode())
        return encrypted_bytes.decode()

    def decrypt(self, encrypted: str) -> str:
        """
        Decrypt an encrypted string.
        
        Args:
            encrypted: Encrypted string (base64-encoded)
            
        Returns:
            Decrypted plaintext string
        """
        decrypted_bytes = self.cipher.decrypt(encrypted.encode())
        return decrypted_bytes.decode()

    @staticmethod
    def generate_key() -> str:
        """
        Generate a new Fernet encryption key.
        
        Returns:
            Base64-encoded encryption key
        """
        return Fernet.generate_key().decode()


# Module-level functions for convenience
def encrypt_connection_string(plaintext: str, encryption_key: str | None = None) -> str:
    """
    Encrypt a database connection string.
    
    Args:
        plaintext: Connection string to encrypt
        encryption_key: Encryption key (uses ENCRYPTION_KEY from settings if not provided)
        
    Returns:
        Encrypted connection string
    """
    from src.config.settings import get_settings
    
    if encryption_key is None:
        settings = get_settings()
        encryption_key = settings.encryption_key
    
    manager = CredentialManager(encryption_key)
    return manager.encrypt(plaintext)


def decrypt_connection_string(encrypted: str, encryption_key: str | None = None) -> str:
    """
    Decrypt a database connection string.
    
    Args:
        encrypted: Encrypted connection string
        encryption_key: Encryption key (uses ENCRYPTION_KEY from settings if not provided)
        
    Returns:
        Decrypted connection string
    """
    from src.config.settings import get_settings
    
    if encryption_key is None:
        settings = get_settings()
        encryption_key = settings.encryption_key
    
    manager = CredentialManager(encryption_key)
    return manager.decrypt(encrypted)
