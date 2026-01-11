"""
Case Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.schemas.case_management import FunctionalCase, FunctionalCaseCreate, FunctionalCaseUpdate
from app.services.case_management_service import CaseManagementService

router = APIRouter()


@router.get("/cases", response_model=List[FunctionalCase])
async def get_functional_cases(
    project_id: Optional[str] = Query(None),
    module_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get functional cases"""
    service = CaseManagementService(db)
    return await service.get_functional_cases(project_id, skip, limit, keyword, module_id)


@router.get("/cases/{case_id}", response_model=FunctionalCase)
async def get_functional_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get functional case by ID"""
    service = CaseManagementService(db)
    case = await service.get_functional_case_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Functional case not found")
    return case


@router.post("/cases", response_model=FunctionalCase)
async def create_functional_case(
    case_data: FunctionalCaseCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create functional case"""
    service = CaseManagementService(db)
    case = await service.create_functional_case(
        project_id=case_data.project_id,
        module_id=case_data.module_id,
        template_id=case_data.template_id,
        name=case_data.name,
        case_edit_type=case_data.case_edit_type,
        version_id=case_data.version_id,
        ref_id=case_data.ref_id,
        create_user=case_data.create_user,
        review_status=case_data.review_status,
        tags=case_data.tags,
        last_execute_result=case_data.last_execute_result,
        steps=case_data.steps,
        text_description=case_data.text_description,
        expected_result=case_data.expected_result,
        prerequisite=case_data.prerequisite,
        description=case_data.description,
    )
    return case


@router.put("/cases/{case_id}", response_model=FunctionalCase)
async def update_functional_case(
    case_id: str,
    case_data: FunctionalCaseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update functional case"""
    service = CaseManagementService(db)
    update_dict = case_data.dict(exclude_unset=True)
    case = await service.update_functional_case(case_id, **update_dict)
    if not case:
        raise HTTPException(status_code=404, detail="Functional case not found")
    return case


@router.delete("/cases/{case_id}")
async def delete_functional_case(
    case_id: str,
    delete_user: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Delete functional case (soft delete)"""
    service = CaseManagementService(db)
    success = await service.delete_functional_case(case_id, delete_user)
    if not success:
        raise HTTPException(status_code=404, detail="Functional case not found")
    return {"message": "Functional case deleted successfully"}


@router.post("/cases/import/excel")
async def import_cases_from_excel(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    module_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Import functional cases from Excel file"""
    service = CaseManagementService(db)
    try:
        file_content = await file.read()
        result = await service.import_cases_from_excel(
            file_content=file_content,
            file_name=file.filename,
            project_id=project_id,
            module_id=module_id,
        )
        return {"message": "Import completed", "imported_count": result.get("imported_count", 0), "errors": result.get("errors", [])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


@router.post("/cases/export/excel")
async def export_cases_to_excel(
    case_ids: List[str],
    db: AsyncSession = Depends(get_db),
):
    """Export functional cases to Excel file"""
    from fastapi.responses import StreamingResponse
    import io
    
    service = CaseManagementService(db)
    try:
        excel_data = await service.export_cases_to_excel(case_ids)
        return StreamingResponse(
            io.BytesIO(excel_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=functional_cases.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Export failed: {str(e)}")


@router.post("/cases/import/xmind")
async def import_cases_from_xmind(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    module_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Import functional cases from XMind file"""
    service = CaseManagementService(db)
    try:
        file_content = await file.read()
        result = await service.import_cases_from_xmind(
            file_content=file_content,
            file_name=file.filename,
            project_id=project_id,
            module_id=module_id,
        )
        return {"message": "Import completed", "imported_count": result.get("imported_count", 0), "errors": result.get("errors", [])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


@router.post("/cases/{case_id}/execute")
async def execute_functional_case(
    case_id: str,
    environment_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Execute functional case"""
    service = CaseManagementService(db)
    result = await service.execute_functional_case(case_id, environment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Functional case not found")
    return result

