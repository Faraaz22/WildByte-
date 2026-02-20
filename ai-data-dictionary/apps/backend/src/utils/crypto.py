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
