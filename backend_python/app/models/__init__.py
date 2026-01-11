"""
Database Models
"""
# Import all models here to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.organization import Organization
from app.models.project import Project
from app.models.user_role import UserRole
from app.models.user_role_relation import UserRoleRelation
from app.models.bug import Bug
from app.models.bug_comment import BugComment
from app.models.bug_attachment import BugLocalAttachment
from app.models.api_test import ApiDefinition, ApiTestCase, ApiScenario
from app.models.api_scenario_step import ApiScenarioStep
from app.models.api_report import ApiReport
from app.models.functional_case import FunctionalCase, FunctionalCaseBlob
from app.models.test_plan import TestPlan, TestPlanReport

__all__ = [
    "User",
    "Organization",
    "Project",
    "UserRole",
    "UserRoleRelation",
    "Bug",
    "BugComment",
    "BugLocalAttachment",
    "ApiDefinition",
    "ApiTestCase",
    "ApiScenario",
    "ApiScenarioStep",
    "ApiReport",
    "FunctionalCase",
    "FunctionalCaseBlob",
    "TestPlan",
    "TestPlanReport",
]

