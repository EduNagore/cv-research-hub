"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('item_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    
    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('item_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_tags_id'), 'tags', ['id'], unique=False)
    
    # Create research_items table
    op.create_table(
        'research_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('slug', sa.String(length=600), nullable=False),
        sa.Column('source', sa.Enum('ARXIV', 'PAPERS_WITH_CODE', 'GITHUB', 'HUGGINGFACE', 'OPENREVIEW', 'JOURNAL', 'CONFERENCE', 'OTHER', name='sourcetype'), nullable=False),
        sa.Column('source_id', sa.String(length=255), nullable=True),
        sa.Column('source_url', sa.String(length=1000), nullable=True),
        sa.Column('published_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('authors', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('author_affiliations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('abstract', sa.Text(), nullable=True),
        sa.Column('short_summary', sa.Text(), nullable=True),
        sa.Column('full_summary', sa.Text(), nullable=True),
        sa.Column('why_it_matters', sa.Text(), nullable=True),
        sa.Column('problem_solved', sa.Text(), nullable=True),
        sa.Column('contribution_description', sa.Text(), nullable=True),
        sa.Column('use_cases', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('paper_url', sa.String(length=1000), nullable=True),
        sa.Column('abstract_url', sa.String(length=1000), nullable=True),
        sa.Column('code_url', sa.String(length=1000), nullable=True),
        sa.Column('github_url', sa.String(length=1000), nullable=True),
        sa.Column('project_page_url', sa.String(length=1000), nullable=True),
        sa.Column('demo_url', sa.String(length=1000), nullable=True),
        sa.Column('contribution_type', sa.Enum('PAPER', 'MODEL', 'BENCHMARK', 'DATASET', 'REPOSITORY', 'LIBRARY', 'SURVEY', name='contributiontype'), nullable=False),
        sa.Column('modality', sa.Enum('IMAGE', 'VIDEO', 'MULTIMODAL', 'THREE_D', 'MEDICAL', 'HISTOPATHOLOGY', 'DERMATOLOGY', 'NATURAL_IMAGES', name='modalitytype'), nullable=True),
        sa.Column('architecture_family', sa.Enum('CNN', 'TRANSFORMER', 'DIFFUSION', 'GAN', 'AUTOENCODER', 'RNN', 'MLP', 'HYBRID', 'OTHER', name='architecturefamily'), nullable=True),
        sa.Column('model_name', sa.String(length=255), nullable=True),
        sa.Column('status_label', sa.Enum('NEW', 'TRENDING', 'UPDATED', 'USEFUL_FOR_RESEARCH', 'USEFUL_FOR_PRODUCTION', name='statuslabel'), nullable=False, default='NEW'),
        sa.Column('is_official_code', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_unofficial_reimplementation', sa.Boolean(), nullable=False, default=False),
        sa.Column('github_stars', sa.Integer(), nullable=True),
        sa.Column('github_forks', sa.Integer(), nullable=True),
        sa.Column('github_last_updated', sa.DateTime(timezone=True), nullable=True),
        sa.Column('github_language', sa.String(length=50), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('recency_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('code_availability_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('source_quality_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('impact_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('clarity_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('venue', sa.String(length=255), nullable=True),
        sa.Column('venue_type', sa.String(length=50), nullable=True),
        sa.Column('canonical_id', sa.Integer(), nullable=True),
        sa.Column('is_canonical', sa.Boolean(), nullable=False, default=True),
        sa.Column('duplicate_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ingestion_batch_id', sa.String(length=100), nullable=True),
        sa.Column('last_ingested_at', sa.DateTime(timezone=True), nullable=False, default=sa.text('now()')),
        sa.Column('metadata_version', sa.Integer(), nullable=False, default=1),
        sa.Column('raw_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        sa.ForeignKeyConstraint(['canonical_id'], ['research_items.id'])
    )
    op.create_index(op.f('ix_research_items_id'), 'research_items', ['id'], unique=False)
    op.create_index(op.f('ix_research_items_slug'), 'research_items', ['slug'], unique=True)
    op.create_index(op.f('ix_research_items_source'), 'research_items', ['source'], unique=False)
    op.create_index(op.f('ix_research_items_source_id'), 'research_items', ['source_id'], unique=False)
    op.create_index(op.f('ix_research_items_published_date'), 'research_items', ['published_date'], unique=False)
    op.create_index(op.f('ix_research_items_contribution_type'), 'research_items', ['contribution_type'], unique=False)
    op.create_index(op.f('ix_research_items_status_label'), 'research_items', ['status_label'], unique=False)
    op.create_index(op.f('ix_research_items_modality'), 'research_items', ['modality'], unique=False)
    op.create_index(op.f('ix_research_items_model_name'), 'research_items', ['model_name'], unique=False)
    op.create_index(op.f('ix_research_items_relevance_score'), 'research_items', ['relevance_score'], unique=False)
    op.create_index(op.f('ix_research_items_ingestion_batch_id'), 'research_items', ['ingestion_batch_id'], unique=False)
    
    # Create research_item_categories association table
    op.create_table(
        'research_item_categories',
        sa.Column('research_item_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['research_item_id'], ['research_items.id']),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('research_item_id', 'category_id')
    )
    
    # Create research_item_tags association table
    op.create_table(
        'research_item_tags',
        sa.Column('research_item_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['research_item_id'], ['research_items.id']),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id']),
        sa.PrimaryKeyConstraint('research_item_id', 'tag_id')
    )
    
    # Create user_items table
    op.create_table(
        'user_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_identifier', sa.String(length=255), nullable=False),
        sa.Column('research_item_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('UNREAD', 'READING', 'READ', 'REVIEW_LATER', 'ARCHIVED', name='useritemstatus'), nullable=False, default='UNREAD'),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_bookmarked', sa.Boolean(), nullable=False, default=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('first_seen_at', sa.DateTime(timezone=True), nullable=False, default=sa.text('now()')),
        sa.Column('last_viewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['research_item_id'], ['research_items.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_items_id'), 'user_items', ['id'], unique=False)
    op.create_index(op.f('ix_user_items_user_identifier'), 'user_items', ['user_identifier'], unique=False)
    op.create_index(op.f('ix_user_items_research_item_id'), 'user_items', ['research_item_id'], unique=False)
    op.create_index(op.f('ix_user_items_status'), 'user_items', ['status'], unique=False)
    
    # Create trends table
    op.create_table(
        'trends',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('trend_type', sa.Enum('ARCHITECTURE', 'TOPIC', 'METHOD', 'DATASET', 'BENCHMARK', 'KEYWORD', 'AUTHOR', 'LAB', name='trendtype'), nullable=False),
        sa.Column('period', sa.Enum('DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', name='trendperiod'), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('frequency', sa.Integer(), nullable=False, default=0),
        sa.Column('growth_rate', sa.Float(), nullable=True),
        sa.Column('popularity_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('related_item_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('related_papers_count', sa.Integer(), nullable=False, default=0),
        sa.Column('related_models_count', sa.Integer(), nullable=False, default=0),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trends_id'), 'trends', ['id'], unique=False)
    op.create_index(op.f('ix_trends_name'), 'trends', ['name'], unique=False)
    op.create_index(op.f('ix_trends_slug'), 'trends', ['slug'], unique=False)
    op.create_index(op.f('ix_trends_trend_type'), 'trends', ['trend_type'], unique=False)
    op.create_index(op.f('ix_trends_period'), 'trends', ['period'], unique=False)
    
    # Create comparisons table
    op.create_table(
        'comparisons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False, unique=True),
        sa.Column('task', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('strengths', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('limitations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('architecture_family', sa.String(length=100), nullable=True),
        sa.Column('computational_cost', sa.Enum('VERY_LOW', 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH', name='computationalcost'), nullable=True),
        sa.Column('maturity_level', sa.Enum('EXPERIMENTAL', 'RESEARCH', 'BETA', 'PRODUCTION', 'MATURE', name='maturitylevel'), nullable=True),
        sa.Column('performance_metrics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('best_use_cases', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('not_recommended_for', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('dataset_size_requirements', sa.String(length=255), nullable=True),
        sa.Column('annotation_requirements', sa.String(length=255), nullable=True),
        sa.Column('hardware_requirements', sa.Text(), nullable=True),
        sa.Column('paper_url', sa.String(length=1000), nullable=True),
        sa.Column('code_url', sa.String(length=1000), nullable=True),
        sa.Column('documentation_url', sa.String(length=1000), nullable=True),
        sa.Column('related_research_item_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=False, default=True),
        sa.Column('view_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comparisons_id'), 'comparisons', ['id'], unique=False)
    op.create_index(op.f('ix_comparisons_slug'), 'comparisons', ['slug'], unique=True)
    op.create_index(op.f('ix_comparisons_task'), 'comparisons', ['task'], unique=False)


def downgrade() -> None:
    op.drop_table('comparisons')
    op.drop_table('trends')
    op.drop_table('user_items')
    op.drop_table('research_item_tags')
    op.drop_table('research_item_categories')
    op.drop_table('research_items')
    op.drop_table('tags')
    op.drop_table('categories')
