"""Initial schema migration.

Revision ID: 001
Revises: 
Create Date: 2026-02-20 10:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all initial tables."""
    
    # Enums (database_type, user_role) are created by sa.Enum in create_table below
    
    # Create databases table
    op.create_table(
        'databases',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('db_type', sa.Enum('postgresql', 'snowflake', 'sqlserver', 'mysql', name='database_type'), nullable=False),
        sa.Column('connection_string_encrypted', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('host', sa.String(length=255), nullable=True),
        sa.Column('port', sa.Integer(), nullable=True),
        sa.Column('database_name', sa.String(length=255), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sync_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('sync_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create schemas table
    op.create_table(
        'schemas',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('database_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['database_id'], ['databases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_schemas_database_id', 'schemas', ['database_id'])
    
    # Create tables table
    op.create_table(
        'tables',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('schema_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('table_type', sa.String(length=50), nullable=False, server_default='table'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ai_generated_description', sa.Text(), nullable=True),
        sa.Column('row_count', sa.BigInteger(), nullable=True),
        sa.Column('size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('metadata_json', JSONB, nullable=True, server_default='{}'),
        sa.Column('use_cases', JSONB, nullable=True),
        sa.Column('freshness_assessment', sa.String(length=50), nullable=True),
        sa.Column('considerations', JSONB, nullable=True),
        sa.Column('has_quality_issues', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('completeness_pct', sa.Float(), nullable=True),
        sa.Column('freshness_hours', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_analyzed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['schema_id'], ['schemas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tables_schema_id', 'tables', ['schema_id'])
    op.execute(
        "CREATE INDEX idx_tables_search ON tables USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')))"
    )
    
    # Create columns table
    op.create_table(
        'columns',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('table_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('data_type', sa.String(length=100), nullable=False),
        sa.Column('ordinal_position', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ai_generated_description', sa.Text(), nullable=True),
        sa.Column('is_nullable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_primary_key', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_foreign_key', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_unique', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('default_value', sa.Text(), nullable=True),
        sa.Column('max_length', sa.Integer(), nullable=True),
        sa.Column('numeric_precision', sa.Integer(), nullable=True),
        sa.Column('numeric_scale', sa.Integer(), nullable=True),
        sa.Column('null_count', sa.Integer(), nullable=True),
        sa.Column('null_percentage', sa.Float(), nullable=True),
        sa.Column('distinct_count', sa.Integer(), nullable=True),
        sa.Column('sample_values', JSONB, nullable=True),
        sa.Column('foreign_key_table', sa.String(length=255), nullable=True),
        sa.Column('foreign_key_column', sa.String(length=255), nullable=True),
        sa.Column('metadata_json', JSONB, nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['table_id'], ['tables.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_columns_table_id', 'columns', ['table_id'])
    
    # Create lineage_edges table
    op.create_table(
        'lineage_edges',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('upstream_table_id', sa.Integer(), nullable=False),
        sa.Column('downstream_table_id', sa.Integer(), nullable=False),
        sa.Column('relationship_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('column_mapping', JSONB, nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('metadata_json', JSONB, nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['upstream_table_id'], ['tables.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['downstream_table_id'], ['tables.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('upstream_table_id', 'downstream_table_id', 'relationship_type', name='uq_lineage_edge')
    )
    op.create_index('idx_lineage_upstream', 'lineage_edges', ['upstream_table_id'])
    op.create_index('idx_lineage_downstream', 'lineage_edges', ['downstream_table_id'])
    
    # Create quality_metrics table
    op.create_table(
        'quality_metrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('table_id', sa.Integer(), nullable=False),
        sa.Column('metric_type', sa.String(length=50), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('measured_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('column_name', sa.String(length=255), nullable=True),
        sa.Column('threshold_min', sa.Float(), nullable=True),
        sa.Column('threshold_max', sa.Float(), nullable=True),
        sa.Column('is_violation', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('violation_severity', sa.String(length=20), nullable=True),
        sa.Column('sample_size', sa.Integer(), nullable=True),
        sa.Column('details', JSONB, nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['table_id'], ['tables.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_quality_metrics_table_id', 'quality_metrics', ['table_id'])
    op.create_index('idx_quality_metrics_composite', 'quality_metrics', 
                    ['table_id', 'metric_type', 'measured_at'])
    op.create_index('idx_quality_metrics_violations', 'quality_metrics', 
                    ['is_violation', 'violation_severity'])
    
    # Create task_results table
    op.create_table(
        'task_results',
        sa.Column('task_id', sa.String(length=255), nullable=False),
        sa.Column('task_name', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('result', JSONB, nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_traceback', sa.Text(), nullable=True),
        sa.Column('args', JSONB, nullable=True),
        sa.Column('kwargs', JSONB, nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('task_id')
    )
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('viewer', 'editor', 'analyst', 'admin', name='user_role'), 
                  nullable=False, server_default='viewer'),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])
    
    # Create trigger for updated_at auto-update
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    for table in ['databases', 'schemas', 'tables', 'columns', 'lineage_edges', 'users']:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE PROCEDURE update_updated_at_column();
        """)


def downgrade() -> None:
    """Drop all tables and types."""
    
    # Drop triggers
    for table in ['databases', 'schemas', 'tables', 'columns', 'lineage_edges', 'users']:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}")
    
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    
    # Drop tables
    op.drop_table('users')
    op.drop_table('task_results')
    op.drop_table('quality_metrics')
    op.drop_table('lineage_edges')
    op.drop_table('columns')
    op.drop_table('tables')
    op.drop_table('schemas')
    op.drop_table('databases')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS user_role")
    op.execute("DROP TYPE IF EXISTS database_type")
