"""
Dashboard Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Optional, List
from datetime import datetime, timedelta

from app.models.project import Project
from app.models.bug import Bug
from app.models.api_test import ApiDefinition, ApiTestCase, ApiScenario


class DashboardService:
    """Dashboard service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_statistics(
        self,
        project_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> Dict:
        """Get dashboard statistics"""
        stats = {}
        
        # Count projects
        project_query = select(func.count(Project.id)).where(Project.deleted == False)
        if organization_id:
            project_query = project_query.where(Project.organization_id == organization_id)
        if project_id:
            project_query = project_query.where(Project.id == project_id)
        result = await self.db.execute(project_query)
        stats["total_projects"] = result.scalar_one() or 0
        
        # Count bugs
        bug_query = select(func.count(Bug.id)).where(Bug.deleted == False)
        if project_id:
            bug_query = bug_query.where(Bug.project_id == project_id)
        result = await self.db.execute(bug_query)
        stats["total_bugs"] = result.scalar_one() or 0
        
        # Count API definitions
        api_def_query = select(func.count(ApiDefinition.id)).where(ApiDefinition.deleted == False)
        if project_id:
            api_def_query = api_def_query.where(ApiDefinition.project_id == project_id)
        result = await self.db.execute(api_def_query)
        stats["total_api_definitions"] = result.scalar_one() or 0
        
        # Count API test cases
        api_case_query = select(func.count(ApiTestCase.id)).where(ApiTestCase.deleted == False)
        if project_id:
            api_case_query = api_case_query.where(ApiTestCase.project_id == project_id)
        result = await self.db.execute(api_case_query)
        stats["total_api_test_cases"] = result.scalar_one() or 0
        
        # Count API scenarios
        api_scenario_query = select(func.count(ApiScenario.id)).where(ApiScenario.deleted == False)
        if project_id:
            api_scenario_query = api_scenario_query.where(ApiScenario.project_id == project_id)
        result = await self.db.execute(api_scenario_query)
        stats["total_api_scenarios"] = result.scalar_one() or 0
        
        # Count functional cases
        from app.models.functional_case import FunctionalCase
        func_case_query = select(func.count(FunctionalCase.id)).where(
            FunctionalCase.deleted == False,
            FunctionalCase.latest == True
        )
        if project_id:
            func_case_query = func_case_query.where(FunctionalCase.project_id == project_id)
        result = await self.db.execute(func_case_query)
        stats["total_functional_cases"] = result.scalar_one() or 0
        
        # Count test plans
        from app.models.test_plan import TestPlan
        test_plan_query = select(func.count(TestPlan.id)).where(TestPlan.deleted == False)
        if project_id:
            test_plan_query = test_plan_query.where(TestPlan.project_id == project_id)
        result = await self.db.execute(test_plan_query)
        stats["total_test_plans"] = result.scalar_one() or 0
        
        return stats
    
    async def get_project_statistics(self, project_id: str) -> Dict:
        """Get project-specific statistics"""
        return await self.get_statistics(project_id=project_id)
    
    async def get_test_coverage(self, project_id: str) -> Dict:
        """Get test coverage statistics"""
        # TODO: Implement test coverage calculation
        return {
            "project_id": project_id,
            "coverage": 0.0,
            "message": "Test coverage calculation not yet implemented"
        }
    
    async def get_recent_activities(self, project_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get recent activities"""
        # TODO: Implement activity log query
        # This would typically query an operation_log table
        return []

