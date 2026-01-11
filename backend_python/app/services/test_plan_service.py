"""
Test Plan Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict
import uuid
import time
import json

from app.models.test_plan import TestPlan, TestPlanReport
from app.schemas.test_plan import TestPlan as TestPlanSchema


class TestPlanService:
    """Test Plan service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_test_plans(
        self,
        project_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        type: Optional[str] = None
    ) -> List[TestPlan]:
        """Get test plans"""
        query = select(TestPlan).where(TestPlan.deleted == False)
        
        if project_id:
            query = query.where(TestPlan.project_id == project_id)
        
        if keyword:
            query = query.where(TestPlan.name.like(f"%{keyword}%"))
        
        if status:
            query = query.where(TestPlan.status == status)
        
        if type:
            query = query.where(TestPlan.type == type)
        
        query = query.offset(skip).limit(limit).order_by(TestPlan.pos.desc(), TestPlan.create_time.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_test_plan_by_id(self, plan_id: str) -> Optional[TestPlan]:
        """Get test plan by ID"""
        result = await self.db.execute(
            select(TestPlan).where(
                TestPlan.id == plan_id,
                TestPlan.deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def create_test_plan(
        self,
        project_id: str,
        group_id: str,
        module_id: str,
        name: str,
        status: str,
        type: str,
        create_user: Optional[str] = None,
        **kwargs
    ) -> TestPlan:
        """Create test plan"""
        plan_id = str(uuid.uuid4())
        
        # Get next num (plan number) for the project
        result = await self.db.execute(
            select(func.max(TestPlan.num)).where(TestPlan.project_id == project_id)
        )
        max_num = result.scalar_one_or_none() or 0
        next_num = max_num + 1
        
        # Get next pos (position) for sorting
        result = await self.db.execute(
            select(func.max(TestPlan.pos)).where(TestPlan.project_id == project_id)
        )
        max_pos = result.scalar_one_or_none() or 0
        next_pos = max_pos + 5000  # Interval of 5000
        
        # Parse tags if provided as list
        tags = kwargs.get("tags")
        if isinstance(tags, list):
            tags = json.dumps(tags, ensure_ascii=False)
        
        test_plan = TestPlan(
            id=plan_id,
            num=next_num,
            project_id=project_id,
            group_id=group_id,
            module_id=module_id,
            name=name,
            status=status,
            type=type,
            tags=tags,
            planned_start_time=kwargs.get("planned_start_time"),
            planned_end_time=kwargs.get("planned_end_time"),
            description=kwargs.get("description"),
            pos=next_pos,
            create_user=create_user,
            deleted=False,
        )
        
        self.db.add(test_plan)
        await self.db.commit()
        await self.db.refresh(test_plan)
        return test_plan
    
    async def update_test_plan(
        self,
        plan_id: str,
        update_user: Optional[str] = None,
        **kwargs
    ) -> Optional[TestPlan]:
        """Update test plan"""
        test_plan = await self.get_test_plan_by_id(plan_id)
        if not test_plan:
            return None
        
        # Handle tags if provided as list
        if "tags" in kwargs and isinstance(kwargs["tags"], list):
            kwargs["tags"] = json.dumps(kwargs["tags"], ensure_ascii=False)
        
        for key, value in kwargs.items():
            if hasattr(test_plan, key) and value is not None:
                setattr(test_plan, key, value)
        
        test_plan.update_user = update_user
        test_plan.update_time = int(time.time() * 1000)
        
        await self.db.commit()
        await self.db.refresh(test_plan)
        return test_plan
    
    async def delete_test_plan(self, plan_id: str, delete_user: Optional[str] = None) -> bool:
        """Delete test plan (soft delete)"""
        test_plan = await self.get_test_plan_by_id(plan_id)
        if not test_plan:
            return False
        
        test_plan.deleted = True
        test_plan.delete_time = int(time.time() * 1000)
        test_plan.delete_user = delete_user
        
        await self.db.commit()
        return True
    
    async def get_test_plan_report_by_id(self, report_id: str) -> Optional[TestPlanReport]:
        """Get test plan report by ID"""
        result = await self.db.execute(
            select(TestPlanReport).where(
                TestPlanReport.id == report_id,
                TestPlanReport.deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def get_test_plan_reports(
        self,
        test_plan_id: Optional[str] = None,
        project_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestPlanReport]:
        """Get test plan reports"""
        query = select(TestPlanReport).where(TestPlanReport.deleted == False)
        
        if test_plan_id:
            query = query.where(TestPlanReport.test_plan_id == test_plan_id)
        
        if project_id:
            query = query.where(TestPlanReport.project_id == project_id)
        
        query = query.offset(skip).limit(limit).order_by(TestPlanReport.create_time.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def execute_test_plan(self, plan_id: str, executor: str) -> dict:
        """Execute test plan"""
        # TODO: Implement test plan execution
        # This would typically:
        # 1. Get all test cases in the plan
        # 2. Execute each test case
        # 3. Collect results
        # 4. Generate report
        return {
            "plan_id": plan_id,
            "status": "running",
            "message": "Test plan execution not yet implemented"
        }
    
    async def execute_test_plan(
        self,
        plan_id: str,
        environment_id: Optional[str] = None,
        trigger_mode: str = "MANUAL",
    ) -> Optional[Dict]:
        """Execute test plan"""
        from app.tasks.test_execution import execute_test_plan_task
        
        test_plan = await self.get_test_plan_by_id(plan_id)
        if not test_plan:
            return None
        
        # Execute asynchronously using Celery
        task = execute_test_plan_task.delay(plan_id, environment_id)
        
        return {
            "plan_id": plan_id,
            "task_id": task.id,
            "status": "running",
            "trigger_mode": trigger_mode,
            "environment_id": environment_id,
            "message": "Test plan execution started"
        }
    
    async def get_test_plan_report(self, plan_id: str) -> Optional[Dict]:
        """Get test plan report"""
        # TODO: Implement report generation
        test_plan = await self.get_test_plan_by_id(plan_id)
        if not test_plan:
            return None
        
        return {
            "plan_id": plan_id,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "message": "Report generation not yet implemented"
        }

