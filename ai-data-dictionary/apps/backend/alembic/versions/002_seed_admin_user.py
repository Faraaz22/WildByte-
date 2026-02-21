"""Seed admin user (username: admin, password: admin 123).

Revision ID: 002
Revises: 001
Create Date: 2026-02-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # bcrypt hash for "admin 123" (cost 12)
    # Generated with: bcrypt.hashpw(b'admin 123', bcrypt.gensalt(rounds=12))
    password_hash = "$2b$12$24dPDcuRbv9VTUHJHb1Jx.SSCuyUMIjlQ6RN94jlWN4XLZqu8j6wi"
    op.execute(
        f"""
        INSERT INTO users (email, username, password_hash, role, is_active, is_verified, created_at, updated_at)
        VALUES (
            'admin@localhost',
            'admin',
            '{password_hash}',
            'admin',
            true,
            true,
            now(),
            now()
        )
        ON CONFLICT (username) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM users WHERE username = 'admin'"))
