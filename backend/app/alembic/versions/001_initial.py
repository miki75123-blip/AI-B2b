"""initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2026-04-27

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 用戶表
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(200), nullable=True),
        sa.Column('company_name', sa.String(200), nullable=True),
        sa.Column('company_description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 供應商表
    op.create_table(
        'suppliers',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('company_name', sa.String(255), nullable=False),
        sa.Column('contact_name', sa.String(200), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('website', sa.String(500), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('products', sa.JSON(), nullable=True),
        sa.Column('certifications', sa.JSON(), nullable=True),
        sa.Column('quality_score', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='new'),
        sa.Column('email_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_suppliers_email'), 'suppliers', ['email'], unique=False)
    op.create_index(op.f('ix_suppliers_status'), 'suppliers', ['status'], unique=False)
    op.create_index(op.f('ix_suppliers_source'), 'suppliers', ['source'], unique=False)

    # 活動表
    op.create_table(
        'campaigns',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='draft'),
        sa.Column('target_countries', sa.JSON(), nullable=True),
        sa.Column('target_categories', sa.JSON(), nullable=True),
        sa.Column('min_quality_score', sa.Integer(), nullable=True),
        sa.Column('template_id', sa.UUID(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_suppliers', sa.Integer(), nullable=False, default=0),
        sa.Column('emails_sent', sa.Integer(), nullable=False, default=0),
        sa.Column('emails_delivered', sa.Integer(), nullable=False, default=0),
        sa.Column('emails_opened', sa.Integer(), nullable=False, default=0),
        sa.Column('emails_clicked', sa.Integer(), nullable=False, default=0),
        sa.Column('emails_replied', sa.Integer(), nullable=False, default=0),
        sa.Column('emails_bounced', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['template_id'], ['email_templates.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaigns_status'), 'campaigns', ['status'], unique=False)

    # 郵件模板表
    op.create_table(
        'email_templates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('subject', sa.String(500), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('variables', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # 郵件記錄表
    op.create_table(
        'emails',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('supplier_id', sa.UUID(), nullable=False),
        sa.Column('campaign_id', sa.UUID(), nullable=True),
        sa.Column('template_id', sa.UUID(), nullable=True),
        sa.Column('to_email', sa.String(255), nullable=False),
        sa.Column('to_name', sa.String(200), nullable=True),
        sa.Column('subject', sa.String(500), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('sendgrid_message_id', sa.String(100), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('opened_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('clicked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('replied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('bounced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id']),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id']),
        sa.ForeignKeyConstraint(['template_id'], ['email_templates.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_emails_status'), 'emails', ['status'], unique=False)
    op.create_index(op.f('ix_emails_sent_at'), 'emails', ['sent_at'], unique=False)

    # 活動日誌表
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=True),
        sa.Column('entity_id', sa.UUID(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activity_logs_created_at'), 'activity_logs', ['created_at'], unique=False)

    # 學習模式表
    op.create_table(
        'learning_patterns',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('pattern_type', sa.String(50), nullable=False),
        sa.Column('trigger', sa.JSON(), nullable=False),
        sa.Column('action', sa.JSON(), nullable=False),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('sample_size', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_patterns_type'), 'learning_patterns', ['pattern_type'], unique=False)


def downgrade() -> None:
    op.drop_table('learning_patterns')
    op.drop_table('activity_logs')
    op.drop_table('emails')
    op.drop_table('email_templates')
    op.drop_table('campaigns')
    op.drop_table('suppliers')
    op.drop_table('users')
