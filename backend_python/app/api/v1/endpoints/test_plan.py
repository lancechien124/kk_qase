"""
Test Plan Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.schemas.test_plan import TestPlan, TestPlanCreate, TestPlanUpdate, TestPlanReport
from app.services.test_plan_service import TestPlanService

router = APIRouter()


@router.get("/plans", response_model=List[TestPlan])
async def get_test_plans(
    project_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    keyword: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get test plans"""
    service = TestPlanService(db)
    return await service.get_test_plans(project_id, skip, limit, keyword, status, type)


@router.get("/plans/{plan_id}", response_model=TestPlan)
async def get_test_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get test plan by ID"""
    service = TestPlanService(db)
    plan = await service.get_test_plan_by_id(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Test plan not found")
    return plan


@router.post("/plans", response_model=TestPlan)
async def create_test_plan(
    plan_data: TestPlanCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create test plan"""
    service = TestPlanService(db)
    plan = await service.create_test_plan(
        project_id=plan_data.project_id,
        group_id=plan_data.group_id,
        module_id=plan_data.module_id,
        name=plan_data.name,
        status=plan_data.status,
        type=plan_data.type,
        create_user=plan_data.create_user,
        tags=plan_data.tags,
        planned_start_time=plan_data.planned_start_time,
        planned_end_time=plan_data.planned_end_time,
        description=plan_data.description,
    )
    return plan


@router.put("/plans/{plan_id}", response_model=TestPlan)
async def update_test_plan(
    plan_id: str,
    plan_data: TestPlanUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update test plan"""
    service = TestPlanService(db)
    update_dict = plan_data.dict(exclude_unset=True)
    plan = await service.update_test_plan(plan_id, **update_dict)
    if not plan:
        raise HTTPException(status_code=404, detail="Test plan not found")
    return plan


@router.delete("/plans/{plan_id}")
async def delete_test_plan(
    plan_id: str,
    delete_user: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Delete test plan (soft delete)"""
    service = TestPlanService(db)
    success = await service.delete_test_plan(plan_id, delete_user)
    if not success:
        raise HTTPException(status_code=404, detail="Test plan not found")
    return {"message": "Test plan deleted successfully"}


@router.get("/plans/{plan_id}/reports", response_model=List[TestPlanReport])
async def get_test_plan_reports(
    plan_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """Get test plan reports"""
    service = TestPlanService(db)
    return await service.get_test_plan_reports(test_plan_id=plan_id, skip=skip, limit=limit)


@router.post("/plans/{plan_id}/execute")
async def execute_test_plan(
    plan_id: str,
    environment_id: Optional[str] = Query(None),
    trigger_mode: str = Query("MANUAL", description="Trigger mode: MANUAL, SCHEDULE, API"),
    db: AsyncSession = Depends(get_db),
):
    """Execute test plan"""
    service = TestPlanService(db)
    result = await service.execute_test_plan(plan_id, environment_id, trigger_mode)
    if not result:
        raise HTTPException(status_code=404, detail="Test plan not found")
    return result


@router.get("/plans/{plan_id}/reports/{report_id}", response_model=TestPlanReport)
async def get_test_plan_report(
    plan_id: str,
    report_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get test plan report by ID"""
    service = TestPlanService(db)
    report = await service.get_test_plan_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Test plan report not found")
    return report


@router.post("/plans/{plan_id}/reports/generate")
async def generate_test_plan_report(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Generate test plan report"""
    service = TestPlanService(db)
    report = await service.get_test_plan_report(plan_id)
    if not report:
        raise HTTPException(status_code=404, detail="Test plan not found or no execution data")
    return report

