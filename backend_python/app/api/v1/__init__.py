"""
API v1 Router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    api_test,
    bug_management,
    case_management,
    dashboard,
    project_management,
    system_setting,
    test_plan,
    auth,
    users,
    files,
    import_export,
    jmeter,
    jmeter_generate,
    ai,
    i18n,
    batch_operations,
    health,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="", tags=["用户管理"])
api_router.include_router(api_test.router, prefix="/api-test", tags=["API测试"])
api_router.include_router(bug_management.router, prefix="/bug", tags=["缺陷管理"])
api_router.include_router(case_management.router, prefix="/case", tags=["用例管理"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["仪表板"])
api_router.include_router(project_management.router, prefix="/project", tags=["项目管理"])
api_router.include_router(system_setting.router, prefix="/system", tags=["系统设置"])
api_router.include_router(test_plan.router, prefix="/test-plan", tags=["测试计划"])
api_router.include_router(files.router, prefix="/files", tags=["文件管理"])
api_router.include_router(import_export.router, prefix="/import-export", tags=["导入导出"])
api_router.include_router(jmeter.router, prefix="/jmeter", tags=["JMeter整合"])
api_router.include_router(jmeter_generate.router, prefix="/jmeter", tags=["JMeter整合"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI功能"])
api_router.include_router(i18n.router, prefix="/i18n", tags=["国际化"])
api_router.include_router(batch_operations.router, prefix="/batch", tags=["批量操作"])
api_router.include_router(health.router, prefix="", tags=["健康檢查"])

