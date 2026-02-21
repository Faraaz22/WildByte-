"""Generate secure keys for .env configuration."""

from cryptography.fernet import Fernet
import secrets


def generate_keys():
    """Generate encryption and JWT secret keys."""
    print("🔑 Generating secure keys for your .env file\n")

    # Generate Fernet encryption key
    encryption_key = Fernet.generate_key().decode()
    print(f"ENCRYPTION_KEY={encryption_key}")

    # Generate JWT secret key
    jwt_secret = secrets.token_hex(32)
    print(f"JWT_SECRET_KEY={jwt_secret}")

    print("\n✅ Copy these values to your .env file")
    print("⚠️  Keep these keys secret and never commit them to version control!")


if __name__ == "__main__":
    generate_keys()
