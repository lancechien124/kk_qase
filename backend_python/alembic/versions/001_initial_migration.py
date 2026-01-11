"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', sa.String(50), primary_key=True, comment='ID'),
        sa.Column('name', sa.String(255), nullable=False, comment='用户名'),
        sa.Column('email', sa.String(64), nullable=False, comment='用户邮箱'),
        sa.Column('password', sa.String(255), nullable=True, comment='用户密码'),
        sa.Column('enable', sa.Boolean(), default=True, comment='是否启用'),
        sa.Column('language', sa.String(50), nullable=True, comment='语言'),
        sa.Column('last_organization_id', sa.String(50), nullable=True, comment='当前组织ID'),
        sa.Column('phone', sa.String(50), nullable=True, comment='手机号'),
        sa.Column('source', sa.String(50), nullable=False, default='LOCAL', comment='来源：LOCAL OIDC CAS OAUTH2'),
        sa.Column('last_project_id', sa.String(50), nullable=True, comment='当前项目ID'),
        sa.Column('cft_token', sa.String(255), nullable=True, comment='身份令牌'),
        sa.Column('create_time', sa.BigInteger(), comment='创建时间'),
        sa.Column('update_time', sa.BigInteger(), comment='更新时间'),
        sa.Column('deleted', sa.Boolean(), default=False, nullable=False, comment='是否删除'),
        sa.Column('delete_time', sa.BigInteger(), nullable=True, comment='删除时间'),
        sa.Column('delete_user', sa.String(50), nullable=True, comment='删除人'),
        sa.Column('create_user', sa.String(50), nullable=True, comment='创建人'),
        sa.Column('update_user', sa.String(50), nullable=True, comment='修改人'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_index('idx_user_email', 'user', ['email'], unique=True)
    op.create_index('idx_user_name', 'user', ['name'])
    op.create_index('idx_user_deleted', 'user', ['deleted'])

    # Create organization table
    op.create_table(
        'organization',
        sa.Column('id', sa.String(50), primary_key=True, comment='ID'),
        sa.Column('num', sa.Integer(), nullable=True, comment='组织编号'),
        sa.Column('name', sa.String(255), nullable=False, comment='组织名称'),
        sa.Column('description', sa.String(255), nullable=True, comment='描述'),
        sa.Column('enable', sa.Boolean(), default=True, comment='是否启用'),
        sa.Column('create_time', sa.BigInteger(), comment='创建时间'),
        sa.Column('update_time', sa.BigInteger(), comment='更新时间'),
        sa.Column('deleted', sa.Boolean(), default=False, nullable=False, comment='是否删除'),
        sa.Column('delete_time', sa.BigInteger(), nullable=True, comment='删除时间'),
        sa.Column('delete_user', sa.String(50), nullable=True, comment='删除人'),
        sa.Column('create_user', sa.String(50), nullable=True, comment='创建人'),
        sa.Column('update_user', sa.String(50), nullable=True, comment='修改人'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_index('idx_organization_name', 'organization', ['name'])
    op.create_index('idx_organization_deleted', 'organization', ['deleted'])

    # Create project table
    op.create_table(
        'project',
        sa.Column('id', sa.String(50), primary_key=True, comment='ID'),
        sa.Column('num', sa.Integer(), nullable=True, comment='项目编号'),
        sa.Column('organization_id', sa.String(50), nullable=False, comment='组织ID'),
        sa.Column('name', sa.String(255), nullable=False, comment='项目名称'),
        sa.Column('description', sa.String(255), nullable=True, comment='项目描述'),
        sa.Column('enable', sa.Boolean(), default=True, comment='是否启用'),
        sa.Column('module_setting', sa.String(255), nullable=True, comment='模块设置'),
        sa.Column('all_resource_pool', sa.Boolean(), default=True, comment='全部资源池'),
        sa.Column('create_time', sa.BigInteger(), comment='创建时间'),
        sa.Column('update_time', sa.BigInteger(), comment='更新时间'),
        sa.Column('deleted', sa.Boolean(), default=False, nullable=False, comment='是否删除'),
        sa.Column('delete_time', sa.BigInteger(), nullable=True, comment='删除时间'),
        sa.Column('delete_user', sa.String(50), nullable=True, comment='删除人'),
        sa.Column('create_user', sa.String(50), nullable=True, comment='创建人'),
        sa.Column('update_user', sa.String(50), nullable=True, comment='修改人'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_foreign_key('fk_project_organization', 'project', 'organization', ['organization_id'], ['id'])
    op.create_index('idx_project_organization_id', 'project', ['organization_id'])
    op.create_index('idx_project_name', 'project', ['name'])
    op.create_index('idx_project_deleted', 'project', ['deleted'])

    # Create user_role table
    op.create_table(
        'user_role',
        sa.Column('id', sa.String(50), primary_key=True, comment='ID'),
        sa.Column('name', sa.String(255), nullable=False, comment='组名称'),
        sa.Column('description', sa.String(255), nullable=True, comment='描述'),
        sa.Column('internal', sa.Boolean(), default=False, comment='是否是内置用户组'),
        sa.Column('type', sa.String(20), nullable=False, comment='所属类型 SYSTEM ORGANIZATION PROJECT'),
        sa.Column('scope_id', sa.String(50), nullable=False, comment='应用范围'),
        sa.Column('create_time', sa.BigInteger(), comment='创建时间'),
        sa.Column('update_time', sa.BigInteger(), comment='更新时间'),
        sa.Column('create_user', sa.String(50), nullable=True, comment='创建人'),
        sa.Column('update_user', sa.String(50), nullable=True, comment='修改人'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_index('idx_user_role_type', 'user_role', ['type'])
    op.create_index('idx_user_role_scope_id', 'user_role', ['scope_id'])

    # Create user_role_relation table
    op.create_table(
        'user_role_relation',
        sa.Column('id', sa.String(50), primary_key=True, comment='ID'),
        sa.Column('user_id', sa.String(50), nullable=False, comment='用户ID'),
        sa.Column('role_id', sa.String(50), nullable=False, comment='组ID'),
        sa.Column('source_id', sa.String(50), nullable=False, comment='组织或项目ID'),
        sa.Column('organization_id', sa.String(50), nullable=True, comment='记录所在的组织ID'),
        sa.Column('create_time', sa.BigInteger(), comment='创建时间'),
        sa.Column('update_time', sa.BigInteger(), comment='更新时间'),
        sa.Column('create_user', sa.String(50), nullable=True, comment='创建人'),
        sa.Column('update_user', sa.String(50), nullable=True, comment='修改人'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_foreign_key('fk_user_role_relation_user', 'user_role_relation', 'user', ['user_id'], ['id'])
    op.create_foreign_key('fk_user_role_relation_role', 'user_role_relation', 'user_role', ['role_id'], ['id'])
    op.create_index('idx_user_role_relation_user_id', 'user_role_relation', ['user_id'])
    op.create_index('idx_user_role_relation_role_id', 'user_role_relation', ['role_id'])
    op.create_index('idx_user_role_relation_source_id', 'user_role_relation', ['source_id'])

    # Create bug table
    op.create_table(
        'bug',
        sa.Column('id', sa.String(50), primary_key=True, comment='ID'),
        sa.Column('num', sa.Integer(), nullable=True, comment='业务ID'),
        sa.Column('title', sa.String(255), nullable=False, comment='缺陷标题'),
        sa.Column('handle_users', sa.String(500), nullable=True, comment='处理人集合'),
        sa.Column('handle_user', sa.String(50), nullable=False, comment='处理人'),
        sa.Column('project_id', sa.String(50), nullable=False, comment='项目ID'),
        sa.Column('template_id', sa.String(50), nullable=False, comment='模板ID'),
        sa.Column('platform', sa.String(50), nullable=False, comment='缺陷平台'),
        sa.Column('status', sa.String(50), nullable=False, comment='状态'),
        sa.Column('tags', sa.String(500), nullable=True, comment='标签'),
        sa.Column('platform_bug_id', sa.String(100), nullable=True, comment='第三方平台缺陷ID'),
        sa.Column('pos', sa.BigInteger(), nullable=False, default=0, comment='自定义排序，间隔5000'),
        sa.Column('create_time', sa.BigInteger(), comment='创建时间'),
        sa.Column('update_time', sa.BigInteger(), comment='更新时间'),
        sa.Column('deleted', sa.Boolean(), default=False, nullable=False, comment='是否删除'),
        sa.Column('delete_time', sa.BigInteger(), nullable=True, comment='删除时间'),
        sa.Column('delete_user', sa.String(50), nullable=True, comment='删除人'),
        sa.Column('create_user', sa.String(50), nullable=True, comment='创建人'),
        sa.Column('update_user', sa.String(50), nullable=True, comment='修改人'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_foreign_key('fk_bug_project', 'bug', 'project', ['project_id'], ['id'])
    op.create_index('idx_bug_project_id', 'bug', ['project_id'])
    op.create_index('idx_bug_status', 'bug', ['status'])
    op.create_index('idx_bug_deleted', 'bug', ['deleted'])

    # Create bug_comment table
    op.create_table(
        'bug_comment',
        sa.Column('id', sa.String(50), primary_key=True, comment='ID'),
        sa.Column('bug_id', sa.String(50), nullable=False, comment='缺陷ID'),
        sa.Column('reply_user', sa.String(50), nullable=True, comment='回复人'),
        sa.Column('notifier', sa.String(255), nullable=True, comment='通知人'),
        sa.Column('parent_id', sa.String(50), nullable=True, comment='父评论ID'),
        sa.Column('content', sa.Text(), nullable=False, comment='内容'),
        sa.Column('create_time', sa.BigInteger(), comment='创建时间'),
        sa.Column('update_time', sa.BigInteger(), comment='更新时间'),
        sa.Column('create_user', sa.String(50), nullable=True, comment='创建人'),
        sa.Column('update_user', sa.String(50), nullable=True, comment='修改人'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_foreign_key('fk_bug_comment_bug', 'bug_comment', 'bug', ['bug_id'], ['id'])
    op.create_index('idx_bug_comment_bug_id', 'bug_comment', ['bug_id'])

    # Create bug_local_attachment table
    op.create_table(
        'bug_local_attachment',
        sa.Column('id', sa.String(50), primary_key=True, comment='ID'),
        sa.Column('bug_id', sa.String(50), nullable=False, comment='缺陷ID'),
        sa.Column('file_id', sa.String(50), nullable=False, comment='文件ID'),
        sa.Column('file_name', sa.String(255), nullable=False, comment='文件名称'),
        sa.Column('size', sa.BigInteger(), nullable=False, comment='文件大小'),
        sa.Column('source', sa.String(255), nullable=False, comment='文件来源'),
        sa.Column('create_time', sa.BigInteger(), comment='创建时间'),
        sa.Column('update_time', sa.BigInteger(), comment='更新时间'),
        sa.Column('create_user', sa.String(50), nullable=True, comment='创建人'),
        sa.Column('update_user', sa.String(50), nullable=True, comment='修改人'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_foreign_key('fk_bug_attachment_bug', 'bug_local_attachment', 'bug', ['bug_id'], ['id'])
    op.create_index('idx_bug_attachment_bug_id', 'bug_local_attachment', ['bug_id'])

    # Create api_definition table
    op.create_table(
        'api_definition',
        sa.Column('id', sa.String(50), primary_key=True, comment='ID'),
        sa.Column('project_id', sa.String(50), nullable=False, comment='项目ID'),
        sa.Column('name', sa.String(255), nullable=False, comment='接口名称'),
        sa.Column('method', sa.String(20), nullable=False, comment='请求方法'),
        sa.Column('path', sa.String(500), nullable=False, comment='请求路径'),
        sa.Column('description', sa.Text(), nullable=True, comment='描述'),
        sa.Column('request_body', mysql.LONGTEXT(), nullable=True, comment='请求体'),
        sa.Column('response_body', mysql.LONGTEXT(), nullable=True, comment='响应体'),
        sa.Column('status', sa.String(50), nullable=True, comment='状态'),
        sa.Column('module_id', sa.String(50), nullable=True, comment='模块ID'),
        sa.Column('create_time', sa.BigInteger(), comment='创建时间'),
        sa.Column('update_time', sa.BigInteger(), comment='更新时间'),
        sa.Column('deleted', sa.Boolean(), default=False, nullable=False, comment='是否删除'),
        sa.Column('delete_time', sa.BigInteger(), nullable=True, comment='删除时间'),
        sa.Column('delete_user', sa.String(50), nullable=True, comment='删除人'),
        sa.Column('create_user', sa.String(50), nullable=True, comment='创建人'),
        sa.Column('update_user', sa.String(50), nullable=True, comment='修改人'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_foreign_key('fk_api_definition_project', 'api_definition', 'project', ['project_id'], ['id'])
    op.create_index('idx_api_definition_project_id', 'api_definition', ['project_id'])
    op.create_index('idx_api_definition_deleted', 'api_definition', ['deleted'])

    # Create api_test_case table
    op.create_table(
        'api_test_case',
        sa.Column('id', sa.String(50), primary_key=True, comment='ID'),
        sa.Column('project_id', sa.String(50), nullable=False, comment='项目ID'),
        sa.Column('api_definition_id', sa.String(50), nullable=False, comment='接口定义ID'),
        sa.Column('name', sa.String(255), nullable=False, comment='用例名称'),
        sa.Column('request', mysql.LONGTEXT(), nullable=False, comment='请求内容'),
        sa.Column('expected_response', mysql.LONGTEXT(), nullable=True, comment='预期响应'),
        sa.Column('status', sa.String(50), nullable=True, comment='状态'),
        sa.Column('priority', sa.String(50), nullable=True, comment='优先级'),
        sa.Column('create_time', sa.BigInteger(), comment='创建时间'),
        sa.Column('update_time', sa.BigInteger(), comment='更新时间'),
        sa.Column('deleted', sa.Boolean(), default=False, nullable=False, comment='是否删除'),
        sa.Column('delete_time', sa.BigInteger(), nullable=True, comment='删除时间'),
        sa.Column('delete_user', sa.String(50), nullable=True, comment='删除人'),
        sa.Column('create_user', sa.String(50), nullable=True, comment='创建人'),
        sa.Column('update_user', sa.String(50), nullable=True, comment='修改人'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_foreign_key('fk_api_test_case_project', 'api_test_case', 'project', ['project_id'], ['id'])
    op.create_foreign_key('fk_api_test_case_api_definition', 'api_test_case', 'api_definition', ['api_definition_id'], ['id'])
    op.create_index('idx_api_test_case_project_id', 'api_test_case', ['project_id'])
    op.create_index('idx_api_test_case_api_definition_id', 'api_test_case', ['api_definition_id'])
    op.create_index('idx_api_test_case_deleted', 'api_test_case', ['deleted'])

    # Create api_scenario table
    op.create_table(
        'api_scenario',
        sa.Column('id', sa.String(50), primary_key=True, comment='ID'),
        sa.Column('project_id', sa.String(50), nullable=False, comment='项目ID'),
        sa.Column('name', sa.String(255), nullable=False, comment='场景名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='描述'),
        sa.Column('status', sa.String(50), nullable=True, comment='状态'),
        sa.Column('module_id', sa.String(50), nullable=True, comment='模块ID'),
        sa.Column('create_time', sa.BigInteger(), comment='创建时间'),
        sa.Column('update_time', sa.BigInteger(), comment='更新时间'),
        sa.Column('deleted', sa.Boolean(), default=False, nullable=False, comment='是否删除'),
        sa.Column('delete_time', sa.BigInteger(), nullable=True, comment='删除时间'),
        sa.Column('delete_user', sa.String(50), nullable=True, comment='删除人'),
        sa.Column('create_user', sa.String(50), nullable=True, comment='创建人'),
        sa.Column('update_user', sa.String(50), nullable=True, comment='修改人'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_foreign_key('fk_api_scenario_project', 'api_scenario', 'project', ['project_id'], ['id'])
    op.create_index('idx_api_scenario_project_id', 'api_scenario', ['project_id'])
    op.create_index('idx_api_scenario_deleted', 'api_scenario', ['deleted'])

    # Create api_scenario_step table
    op.create_table(
        'api_scenario_step',
        sa.Column('id', sa.String(50), primary_key=True, comment='步骤id'),
        sa.Column('scenario_id', sa.String(50), nullable=False, comment='场景id'),
        sa.Column('name', sa.String(255), nullable=True, comment='步骤名称'),
        sa.Column('sort', sa.BigInteger(), nullable=False, default=0, comment='序号'),
        sa.Column('enable', sa.Boolean(), default=True, comment='启用/禁用'),
        sa.Column('resource_id', sa.String(50), nullable=True, comment='资源id'),
        sa.Column('resource_num', sa.String(255), nullable=True, comment='资源编号'),
        sa.Column('step_type', sa.String(50), nullable=True, comment='步骤类型/API/CASE等'),
        sa.Column('project_id', sa.String(50), nullable=True, comment='项目fk'),
        sa.Column('parent_id', sa.String(50), nullable=True, comment='父级fk'),
        sa.Column('version_id', sa.String(50), nullable=True, comment='版本号'),
        sa.Column('ref_type', sa.String(50), nullable=True, comment='引用/复制/自定义'),
        sa.Column('config', mysql.LONGTEXT(), nullable=True, comment='循环等组件基础数据'),
        sa.Column('origin_project_id', sa.String(50), nullable=True, comment='记录跨项目复制的步骤的原项目ID'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_foreign_key('fk_api_scenario_step_scenario', 'api_scenario_step', 'api_scenario', ['scenario_id'], ['id'])
    op.create_index('idx_api_scenario_step_scenario_id', 'api_scenario_step', ['scenario_id'])

    # Create api_report table
    op.create_table(
        'api_report',
        sa.Column('id', sa.String(50), primary_key=True, comment='ID'),
        sa.Column('name', sa.String(300), nullable=False, comment='接口报告名称'),
        sa.Column('test_plan_case_id', sa.String(50), nullable=False, comment='测试计划关联用例表ID'),
        sa.Column('start_time', sa.BigInteger(), nullable=False, comment='开始时间/同创建时间一致'),
        sa.Column('end_time', sa.BigInteger(), nullable=True, comment='结束时间/报告执行完成'),
        sa.Column('request_duration', sa.BigInteger(), nullable=False, comment='请求总耗时'),
        sa.Column('status', sa.String(20), nullable=False, comment='报告状态/SUCCESS/ERROR'),
        sa.Column('trigger_mode', sa.String(20), nullable=False, comment='触发方式'),
        sa.Column('run_mode', sa.String(20), nullable=False, comment='执行模式'),
        sa.Column('pool_id', sa.String(50), nullable=False, comment='资源池'),
        sa.Column('integrated', sa.Boolean(), default=False, comment='是否是集成报告'),
        sa.Column('project_id', sa.String(50), nullable=False, comment='项目fk'),
        sa.Column('environment_id', sa.String(50), nullable=True, comment='环境'),
        sa.Column('error_count', sa.BigInteger(), nullable=False, default=0, comment='失败数'),
        sa.Column('fake_error_count', sa.BigInteger(), nullable=False, default=0, comment='误报数'),
        sa.Column('pending_count', sa.BigInteger(), nullable=False, default=0, comment='未执行数'),
        sa.Column('success_count', sa.BigInteger(), nullable=False, default=0, comment='成功数'),
        sa.Column('assertion_count', sa.BigInteger(), nullable=False, default=0, comment='总断言数'),
        sa.Column('assertion_success_count', sa.BigInteger(), nullable=False, default=0, comment='成功断言数'),
        sa.Column('request_error_rate', sa.String(20), nullable=False, comment='请求失败率'),
        sa.Column('request_pending_rate', sa.String(20), nullable=False, comment='请求未执行率'),
        sa.Column('request_fake_error_rate', sa.String(20), nullable=False, comment='请求误报率'),
        sa.Column('request_pass_rate', sa.String(20), nullable=False, comment='请求通过率'),
        sa.Column('assertion_pass_rate', sa.String(20), nullable=False, comment='断言通过率'),
        sa.Column('script_identifier', sa.String(255), nullable=True, comment='脚本标识'),
        sa.Column('exec_status', sa.String(20), nullable=False, comment='执行状态'),
        sa.Column('plan', sa.Boolean(), default=False, comment='是否是测试计划整体执行'),
        sa.Column('create_time', sa.BigInteger(), comment='创建时间'),
        sa.Column('update_time', sa.BigInteger(), comment='更新时间'),
        sa.Column('deleted', sa.Boolean(), default=False, nullable=False, comment='是否删除'),
        sa.Column('delete_time', sa.BigInteger(), nullable=True, comment='删除时间'),
        sa.Column('delete_user', sa.String(50), nullable=True, comment='删除人'),
        sa.Column('create_user', sa.String(50), nullable=True, comment='创建人'),
        sa.Column('update_user', sa.String(50), nullable=True, comment='修改人'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_foreign_key('fk_api_report_project', 'api_report', 'project', ['project_id'], ['id'])
    op.create_index('idx_api_report_project_id', 'api_report', ['project_id'])
    op.create_index('idx_api_report_deleted', 'api_report', ['deleted'])

    # Create functional_case table
    op.create_table(
        'functional_case',
        sa.Column('id', sa.String(50), primary_key=True, comment='ID'),
        sa.Column('num', sa.BigInteger(), nullable=True, comment='业务ID'),
        sa.Column('module_id', sa.String(50), nullable=False, comment='模块ID'),
        sa.Column('project_id', sa.String(50), nullable=False, comment='项目ID'),
        sa.Column('template_id', sa.String(50), nullable=False, comment='模板ID'),
        sa.Column('name', sa.String(255), nullable=False, comment='名称'),
        sa.Column('review_status', sa.String(64), nullable=False, default='未评审', comment='评审结果：未评审/评审中/通过/不通过/重新提审'),
        sa.Column('tags', sa.String(500), nullable=True, comment='标签（JSON)'),
        sa.Column('case_edit_type', sa.String(50), nullable=False, default='STEP', comment='编辑模式：步骤模式/文本模式'),
        sa.Column('pos', sa.BigInteger(), nullable=False, default=0, comment='自定义排序，间隔5000'),
        sa.Column('version_id', sa.String(50), nullable=False, comment='版本ID'),
        sa.Column('ref_id', sa.String(50), nullable=False, comment='指向初始版本ID'),
        sa.Column('last_execute_result', sa.String(64), nullable=False, default='未执行', comment='最近的执行结果：未执行/通过/失败/阻塞/跳过'),
        sa.Column('ai_create', sa.Boolean(), default=False, comment='是否是ai自动生成的用例：0-否，1-是'),
        sa.Column('public_case', sa.Boolean(), default=False, comment='是否是公共用例：0-否，1-是'),
        sa.Column('latest', sa.Boolean(), default=True, comment='是否为最新版本：0-否，1-是'),
        sa.Column('create_time', sa.BigInteger(), comment='创建时间'),
        sa.Column('update_time', sa.BigInteger(), comment='更新时间'),
        sa.Column('deleted', sa.Boolean(), default=False, nullable=False, comment='是否删除'),
        sa.Column('delete_time', sa.BigInteger(), nullable=True, comment='删除时间'),
        sa.Column('delete_user', sa.String(50), nullable=True, comment='删除人'),
        sa.Column('create_user', sa.String(50), nullable=True, comment='创建人'),
        sa.Column('update_user', sa.String(50), nullable=True, comment='修改人'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_foreign_key('fk_functional_case_project', 'functional_case', 'project', ['project_id'], ['id'])
    op.create_index('idx_functional_case_project_id', 'functional_case', ['project_id'])
    op.create_index('idx_functional_case_deleted', 'functional_case', ['deleted'])

    # Create functional_case_blob table
    op.create_table(
        'functional_case_blob',
        sa.Column('id', sa.String(50), primary_key=True, comment='功能用例ID'),
        sa.Column('steps', mysql.LONGTEXT(), nullable=True, comment='用例步骤（JSON)，step_model 为 Step 时启用'),
        sa.Column('text_description', mysql.LONGTEXT(), nullable=True, comment='步骤描述，step_model 为 Text 时启用'),
        sa.Column('expected_result', mysql.LONGTEXT(), nullable=True, comment='预期结果，step_model 为 Text  时启用'),
        sa.Column('prerequisite', mysql.LONGTEXT(), nullable=True, comment='前置条件'),
        sa.Column('description', mysql.LONGTEXT(), nullable=True, comment='备注'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_foreign_key('fk_functional_case_blob_case', 'functional_case_blob', 'functional_case', ['id'], ['id'])

    # Create test_plan table
    op.create_table(
        'test_plan',
        sa.Column('id', sa.String(50), primary_key=True, comment='ID'),
        sa.Column('num', sa.BigInteger(), nullable=True, comment='num'),
        sa.Column('project_id', sa.String(50), nullable=False, comment='测试计划所属项目'),
        sa.Column('group_id', sa.String(50), nullable=False, default='none', comment='测试计划组ID;默认为none.只关联type为group的测试计划'),
        sa.Column('module_id', sa.String(50), nullable=False, comment='测试计划模块ID'),
        sa.Column('name', sa.String(255), nullable=False, comment='测试计划名称'),
        sa.Column('status', sa.String(20), nullable=False, default='未开始', comment='测试计划状态;未开始，进行中，已完成，已归档'),
        sa.Column('type', sa.String(30), nullable=False, default='testPlan', comment='数据类型;测试计划组（group）/测试计划（testPlan）'),
        sa.Column('tags', sa.String(500), nullable=True, comment='标签'),
        sa.Column('planned_start_time', sa.BigInteger(), nullable=True, comment='计划开始时间'),
        sa.Column('planned_end_time', sa.BigInteger(), nullable=True, comment='计划结束时间'),
        sa.Column('actual_start_time', sa.BigInteger(), nullable=True, comment='实际开始时间'),
        sa.Column('actual_end_time', sa.BigInteger(), nullable=True, comment='实际结束时间'),
        sa.Column('description', sa.Text(), nullable=True, comment='描述'),
        sa.Column('pos', sa.BigInteger(), nullable=False, default=0, comment='自定义排序'),
        sa.Column('create_time', sa.BigInteger(), comment='创建时间'),
        sa.Column('update_time', sa.BigInteger(), comment='更新时间'),
        sa.Column('create_user', sa.String(50), nullable=True, comment='创建人'),
        sa.Column('update_user', sa.String(50), nullable=True, comment='修改人'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_foreign_key('fk_test_plan_project', 'test_plan', 'project', ['project_id'], ['id'])
    op.create_index('idx_test_plan_project_id', 'test_plan', ['project_id'])
    op.create_index('idx_test_plan_status', 'test_plan', ['status'])

    # Create test_plan_report table
    op.create_table(
        'test_plan_report',
        sa.Column('id', sa.String(50), primary_key=True, comment='ID'),
        sa.Column('test_plan_id', sa.String(50), nullable=False, comment='测试计划ID'),
        sa.Column('name', sa.String(255), nullable=False, comment='报告名称'),
        sa.Column('start_time', sa.BigInteger(), nullable=True, comment='开始时间;计划开始执行的时间'),
        sa.Column('end_time', sa.BigInteger(), nullable=True, comment='结束时间;计划结束执行的时间'),
        sa.Column('exec_status', sa.String(50), nullable=False, comment='执行状态'),
        sa.Column('result_status', sa.String(50), nullable=False, comment='结果状态'),
        sa.Column('pass_rate', sa.Float(), nullable=True, comment='通过率'),
        sa.Column('trigger_mode', sa.String(50), nullable=False, comment='触发类型'),
        sa.Column('pass_threshold', sa.Float(), nullable=False, default=0.0, comment='通过阈值'),
        sa.Column('project_id', sa.String(50), nullable=False, comment='项目id'),
        sa.Column('integrated', sa.Boolean(), default=False, comment='是否是集成报告'),
        sa.Column('execute_rate', sa.Float(), nullable=True, comment='执行率'),
        sa.Column('parent_id', sa.String(50), nullable=True, comment='独立报告的父级ID'),
        sa.Column('test_plan_name', sa.String(255), nullable=False, comment='测试计划名称'),
        sa.Column('default_layout', sa.Boolean(), default=False, comment='是否默认布局'),
        sa.Column('create_time', sa.BigInteger(), comment='创建时间'),
        sa.Column('update_time', sa.BigInteger(), comment='更新时间'),
        sa.Column('deleted', sa.Boolean(), default=False, nullable=False, comment='是否删除'),
        sa.Column('delete_time', sa.BigInteger(), nullable=True, comment='删除时间'),
        sa.Column('delete_user', sa.String(50), nullable=True, comment='删除人'),
        sa.Column('create_user', sa.String(50), nullable=True, comment='创建人'),
        sa.Column('update_user', sa.String(50), nullable=True, comment='修改人'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
    )
    op.create_foreign_key('fk_test_plan_report_test_plan', 'test_plan_report', 'test_plan', ['test_plan_id'], ['id'])
    op.create_foreign_key('fk_test_plan_report_project', 'test_plan_report', 'project', ['project_id'], ['id'])
    op.create_index('idx_test_plan_report_test_plan_id', 'test_plan_report', ['test_plan_id'])
    op.create_index('idx_test_plan_report_project_id', 'test_plan_report', ['project_id'])
    op.create_index('idx_test_plan_report_deleted', 'test_plan_report', ['deleted'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('test_plan_report')
    op.drop_table('test_plan')
    op.drop_table('functional_case_blob')
    op.drop_table('functional_case')
    op.drop_table('api_report')
    op.drop_table('api_scenario_step')
    op.drop_table('api_scenario')
    op.drop_table('api_test_case')
    op.drop_table('api_definition')
    op.drop_table('bug_local_attachment')
    op.drop_table('bug_comment')
    op.drop_table('bug')
    op.drop_table('user_role_relation')
    op.drop_table('user_role')
    op.drop_table('project')
    op.drop_table('organization')
    op.drop_table('user')

