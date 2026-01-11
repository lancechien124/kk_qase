"""Add performance indexes

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Add performance indexes"""
    
    # User table indexes
    op.create_index('idx_user_email', 'user', ['email'], unique=True)
    op.create_index('idx_user_name', 'user', ['name'])
    op.create_index('idx_user_status', 'user', ['status'])
    op.create_index('idx_user_deleted', 'user', ['deleted'])
    
    # Project table indexes
    op.create_index('idx_project_org_id', 'project', ['organization_id'])
    op.create_index('idx_project_deleted', 'project', ['deleted'])
    op.create_index('idx_project_enable', 'project', ['enable'])
    op.create_index('idx_project_create_time', 'project', ['create_time'])
    
    # Organization table indexes
    op.create_index('idx_organization_name', 'organization', ['name'])
    op.create_index('idx_organization_deleted', 'organization', ['deleted'])
    
    # API Definition indexes
    op.create_index('idx_api_def_project_id', 'api_definition', ['project_id'])
    op.create_index('idx_api_def_method', 'api_definition', ['method'])
    op.create_index('idx_api_def_deleted', 'api_definition', ['deleted'])
    op.create_index('idx_api_def_create_time', 'api_definition', ['create_time'])
    
    # API Test Case indexes
    op.create_index('idx_api_case_def_id', 'api_test_case', ['api_definition_id'])
    op.create_index('idx_api_case_project_id', 'api_test_case', ['project_id'])
    op.create_index('idx_api_case_deleted', 'api_test_case', ['deleted'])
    
    # API Scenario indexes
    op.create_index('idx_api_scenario_project_id', 'api_scenario', ['project_id'])
    op.create_index('idx_api_scenario_deleted', 'api_scenario', ['deleted'])
    op.create_index('idx_api_scenario_create_time', 'api_scenario', ['create_time'])
    
    # Functional Case indexes
    op.create_index('idx_func_case_project_id', 'functional_case', ['project_id'])
    op.create_index('idx_func_case_deleted', 'functional_case', ['deleted'])
    op.create_index('idx_func_case_create_time', 'functional_case', ['create_time'])
    
    # Test Plan indexes
    op.create_index('idx_test_plan_project_id', 'test_plan', ['project_id'])
    op.create_index('idx_test_plan_deleted', 'test_plan', ['deleted'])
    op.create_index('idx_test_plan_status', 'test_plan', ['status'])
    op.create_index('idx_test_plan_create_time', 'test_plan', ['create_time'])
    
    # Bug indexes
    op.create_index('idx_bug_project_id', 'bug', ['project_id'])
    op.create_index('idx_bug_status', 'bug', ['status'])
    op.create_index('idx_bug_priority', 'bug', ['priority'])
    op.create_index('idx_bug_deleted', 'bug', ['deleted'])
    op.create_index('idx_bug_create_time', 'bug', ['create_time'])
    
    # User Role Relation indexes
    op.create_index('idx_user_role_user_id', 'user_role_relation', ['user_id'])
    op.create_index('idx_user_role_role_id', 'user_role_relation', ['role_id'])
    op.create_index('idx_user_role_source_id', 'user_role_relation', ['source_id'])
    op.create_index('idx_user_role_org_id', 'user_role_relation', ['organization_id'])
    
    # Composite indexes for common queries
    op.create_index('idx_project_org_deleted', 'project', ['organization_id', 'deleted'])
    op.create_index('idx_api_def_project_deleted', 'api_definition', ['project_id', 'deleted'])
    op.create_index('idx_func_case_project_deleted', 'functional_case', ['project_id', 'deleted'])
    op.create_index('idx_test_plan_project_deleted', 'test_plan', ['project_id', 'deleted'])
    op.create_index('idx_bug_project_deleted', 'bug', ['project_id', 'deleted'])


def downgrade():
    """Remove performance indexes"""
    
    # Remove composite indexes
    op.drop_index('idx_bug_project_deleted', table_name='bug')
    op.drop_index('idx_test_plan_project_deleted', table_name='test_plan')
    op.drop_index('idx_func_case_project_deleted', table_name='functional_case')
    op.drop_index('idx_api_def_project_deleted', table_name='api_definition')
    op.drop_index('idx_project_org_deleted', table_name='project')
    
    # Remove User Role Relation indexes
    op.drop_index('idx_user_role_org_id', table_name='user_role_relation')
    op.drop_index('idx_user_role_source_id', table_name='user_role_relation')
    op.drop_index('idx_user_role_role_id', table_name='user_role_relation')
    op.drop_index('idx_user_role_user_id', table_name='user_role_relation')
    
    # Remove Bug indexes
    op.drop_index('idx_bug_create_time', table_name='bug')
    op.drop_index('idx_bug_deleted', table_name='bug')
    op.drop_index('idx_bug_priority', table_name='bug')
    op.drop_index('idx_bug_status', table_name='bug')
    op.drop_index('idx_bug_project_id', table_name='bug')
    
    # Remove Test Plan indexes
    op.drop_index('idx_test_plan_create_time', table_name='test_plan')
    op.drop_index('idx_test_plan_status', table_name='test_plan')
    op.drop_index('idx_test_plan_deleted', table_name='test_plan')
    op.drop_index('idx_test_plan_project_id', table_name='test_plan')
    
    # Remove Functional Case indexes
    op.drop_index('idx_func_case_create_time', table_name='functional_case')
    op.drop_index('idx_func_case_deleted', table_name='functional_case')
    op.drop_index('idx_func_case_project_id', table_name='functional_case')
    
    # Remove API Scenario indexes
    op.drop_index('idx_api_scenario_create_time', table_name='api_scenario')
    op.drop_index('idx_api_scenario_deleted', table_name='api_scenario')
    op.drop_index('idx_api_scenario_project_id', table_name='api_scenario')
    
    # Remove API Test Case indexes
    op.drop_index('idx_api_case_deleted', table_name='api_test_case')
    op.drop_index('idx_api_case_project_id', table_name='api_test_case')
    op.drop_index('idx_api_case_def_id', table_name='api_test_case')
    
    # Remove API Definition indexes
    op.drop_index('idx_api_def_create_time', table_name='api_definition')
    op.drop_index('idx_api_def_deleted', table_name='api_definition')
    op.drop_index('idx_api_def_method', table_name='api_definition')
    op.drop_index('idx_api_def_project_id', table_name='api_definition')
    
    # Remove Organization indexes
    op.drop_index('idx_organization_deleted', table_name='organization')
    op.drop_index('idx_organization_name', table_name='organization')
    
    # Remove Project indexes
    op.drop_index('idx_project_create_time', table_name='project')
    op.drop_index('idx_project_enable', table_name='project')
    op.drop_index('idx_project_deleted', table_name='project')
    op.drop_index('idx_project_org_id', table_name='project')
    
    # Remove User indexes
    op.drop_index('idx_user_deleted', table_name='user')
    op.drop_index('idx_user_status', table_name='user')
    op.drop_index('idx_user_name', table_name='user')
    op.drop_index('idx_user_email', table_name='user')

