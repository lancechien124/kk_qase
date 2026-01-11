"""
API Test Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import json
import io

from app.core.database import get_db
from app.schemas.api_test import ApiDefinition, ApiTestCase, ApiScenario, ApiDefinitionCreate, ApiDefinitionUpdate
from app.services.api_test_service import ApiTestService

router = APIRouter()


@router.get("/definitions", response_model=List[ApiDefinition])
async def get_api_definitions(
    project_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get API definitions"""
    service = ApiTestService(db)
    return await service.get_api_definitions(project_id, skip, limit, keyword)


@router.get("/definitions/{definition_id}", response_model=ApiDefinition)
async def get_api_definition(
    definition_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get API definition by ID"""
    service = ApiTestService(db)
    definition = await service.get_api_definition_by_id(definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail="API definition not found")
    return definition


@router.post("/definitions", response_model=ApiDefinition)
async def create_api_definition(
    definition_data: ApiDefinitionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create API definition"""
    service = ApiTestService(db)
    definition = await service.create_api_definition(
        project_id=definition_data.project_id,
        name=definition_data.name,
        method=definition_data.method,
        path=definition_data.path,
        create_user=definition_data.create_user,
        description=definition_data.description,
        request_body=definition_data.request_body,
        response_body=definition_data.response_body,
        status=definition_data.status,
        module_id=definition_data.module_id,
    )
    return definition


@router.put("/definitions/{definition_id}", response_model=ApiDefinition)
async def update_api_definition(
    definition_id: str,
    definition_data: ApiDefinitionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update API definition"""
    service = ApiTestService(db)
    update_dict = definition_data.dict(exclude_unset=True)
    definition = await service.update_api_definition(definition_id, **update_dict)
    if not definition:
        raise HTTPException(status_code=404, detail="API definition not found")
    return definition


@router.delete("/definitions/{definition_id}")
async def delete_api_definition(
    definition_id: str,
    delete_user: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Delete API definition"""
    service = ApiTestService(db)
    success = await service.delete_api_definition(definition_id, delete_user)
    if not success:
        raise HTTPException(status_code=404, detail="API definition not found")
    return {"message": "API definition deleted successfully"}


@router.get("/test-cases", response_model=List[ApiTestCase])
async def get_api_test_cases(
    project_id: Optional[str] = Query(None),
    api_definition_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get API test cases"""
    service = ApiTestService(db)
    return await service.get_api_test_cases(project_id, api_definition_id, skip, limit, keyword)


@router.get("/test-cases/{test_case_id}", response_model=ApiTestCase)
async def get_api_test_case(
    test_case_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get API test case by ID"""
    service = ApiTestService(db)
    test_case = await service.get_api_test_case_by_id(test_case_id)
    if not test_case:
        raise HTTPException(status_code=404, detail="API test case not found")
    return test_case


@router.post("/test-cases", response_model=ApiTestCase)
async def create_api_test_case(
    test_case_data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Create API test case"""
    service = ApiTestService(db)
    test_case = await service.create_api_test_case(
        project_id=test_case_data["project_id"],
        api_definition_id=test_case_data["api_definition_id"],
        name=test_case_data["name"],
        request=test_case_data["request"],
        create_user=test_case_data.get("create_user"),
        expected_response=test_case_data.get("expected_response"),
        status=test_case_data.get("status"),
        priority=test_case_data.get("priority"),
    )
    return test_case


@router.put("/test-cases/{test_case_id}", response_model=ApiTestCase)
async def update_api_test_case(
    test_case_id: str,
    test_case_data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Update API test case"""
    service = ApiTestService(db)
    update_dict = {k: v for k, v in test_case_data.items() if v is not None}
    test_case = await service.update_api_test_case(test_case_id, **update_dict)
    if not test_case:
        raise HTTPException(status_code=404, detail="API test case not found")
    return test_case


@router.delete("/test-cases/{test_case_id}")
async def delete_api_test_case(
    test_case_id: str,
    delete_user: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Delete API test case"""
    service = ApiTestService(db)
    success = await service.delete_api_test_case(test_case_id, delete_user)
    if not success:
        raise HTTPException(status_code=404, detail="API test case not found")
    return {"message": "API test case deleted successfully"}


@router.get("/scenarios", response_model=List[ApiScenario])
async def get_api_scenarios(
    project_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get API scenarios"""
    service = ApiTestService(db)
    return await service.get_api_scenarios(project_id, skip, limit, keyword)


@router.get("/scenarios/{scenario_id}", response_model=ApiScenario)
async def get_api_scenario(
    scenario_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get API scenario by ID"""
    service = ApiTestService(db)
    scenario = await service.get_api_scenario_by_id(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="API scenario not found")
    return scenario


@router.post("/scenarios", response_model=ApiScenario)
async def create_api_scenario(
    scenario_data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Create API scenario"""
    service = ApiTestService(db)
    scenario = await service.create_api_scenario(
        project_id=scenario_data["project_id"],
        name=scenario_data["name"],
        create_user=scenario_data.get("create_user"),
        description=scenario_data.get("description"),
        status=scenario_data.get("status"),
        module_id=scenario_data.get("module_id"),
    )
    return scenario


@router.put("/scenarios/{scenario_id}", response_model=ApiScenario)
async def update_api_scenario(
    scenario_id: str,
    scenario_data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Update API scenario"""
    service = ApiTestService(db)
    update_dict = {k: v for k, v in scenario_data.items() if v is not None}
    scenario = await service.update_api_scenario(scenario_id, **update_dict)
    if not scenario:
        raise HTTPException(status_code=404, detail="API scenario not found")
    return scenario


@router.delete("/scenarios/{scenario_id}")
async def delete_api_scenario(
    scenario_id: str,
    delete_user: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Delete API scenario"""
    service = ApiTestService(db)
    success = await service.delete_api_scenario(scenario_id, delete_user)
    if not success:
        raise HTTPException(status_code=404, detail="API scenario not found")
    return {"message": "API scenario deleted successfully"}


@router.post("/test-cases/{test_case_id}/execute")
async def execute_api_test(
    test_case_id: str,
    environment_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Execute API test case"""
    service = ApiTestService(db)
    result = await service.execute_api_test(test_case_id, environment_id)
    return result


@router.post("/scenarios/{scenario_id}/execute")
async def execute_api_scenario(
    scenario_id: str,
    environment_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Execute API scenario"""
    service = ApiTestService(db)
    result = await service.execute_api_test(scenario_id, environment_id, is_scenario=True)
    return result


@router.post("/definitions/import")
async def import_api_definitions(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    module_id: Optional[str] = Form(None),
    platform: str = Form("Swagger3", description="Import platform: Swagger3, Postman, Har, Metersphere"),
    cover_data: bool = Form(False, description="Whether to cover existing data"),
    sync_case: bool = Form(False, description="Whether to sync test cases"),
    db: AsyncSession = Depends(get_db),
):
    """Import API definitions from file (Swagger, Postman, Har, etc.)"""
    service = ApiTestService(db)
    try:
        file_content = await file.read()
        result = await service.import_api_definitions(
            file_content=file_content,
            file_name=file.filename,
            project_id=project_id,
            module_id=module_id,
            platform=platform,
            cover_data=cover_data,
            sync_case=sync_case,
        )
        return {"message": "Import completed", "imported_count": result.get("imported_count", 0), "updated_count": result.get("updated_count", 0)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


@router.post("/definitions/export")
async def export_api_definitions(
    definition_ids: List[str],
    export_type: str = Query("json", description="Export type: json, swagger, postman"),
    db: AsyncSession = Depends(get_db),
):
    """Export API definitions to file"""
    service = ApiTestService(db)
    try:
        export_data = await service.export_api_definitions(definition_ids, export_type)
        
        if export_type == "json":
            return JSONResponse(content=export_data)
        else:
            # For Swagger/Postman, return as file download
            file_content = json.dumps(export_data, indent=2, ensure_ascii=False).encode('utf-8')
            return StreamingResponse(
                io.BytesIO(file_content),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=api_definitions.{export_type}"}
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Export failed: {str(e)}")


@router.post("/scenarios/import")
async def import_api_scenarios(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    module_id: Optional[str] = Form(None),
    platform: str = Form("Metersphere", description="Import platform: Metersphere, Postman"),
    cover_data: bool = Form(False, description="Whether to cover existing data"),
    db: AsyncSession = Depends(get_db),
):
    """Import API scenarios from file"""
    service = ApiTestService(db)
    try:
        file_content = await file.read()
        result = await service.import_api_scenarios(
            file_content=file_content,
            file_name=file.filename,
            project_id=project_id,
            module_id=module_id,
            platform=platform,
            cover_data=cover_data,
        )
        return {"message": "Import completed", "imported_count": result.get("imported_count", 0)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


@router.post("/scenarios/export")
async def export_api_scenarios(
    scenario_ids: List[str],
    export_type: str = Query("json", description="Export type: json, postman"),
    db: AsyncSession = Depends(get_db),
):
    """Export API scenarios to file"""
    service = ApiTestService(db)
    try:
        export_data = await service.export_api_scenarios(scenario_ids, export_type)
        
        if export_type == "json":
            return JSONResponse(content=export_data)
        else:
            file_content = json.dumps(export_data, indent=2, ensure_ascii=False).encode('utf-8')
            return StreamingResponse(
                io.BytesIO(file_content),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=api_scenarios.{export_type}"}
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Export failed: {str(e)}")


@router.post("/mock")
async def generate_mock_data(
    key: str = Form(..., description="Mock key pattern"),
):
    """Generate mock data based on key pattern"""
    # Simple mock data generator
    # In production, this should use a more sophisticated mock library
    mock_data = {
        "string": "mock_string",
        "number": 123,
        "boolean": True,
        "array": [1, 2, 3],
        "object": {"key": "value"}
    }
    
    # Simple pattern matching
    if "email" in key.lower():
        return "mock@example.com"
    elif "phone" in key.lower():
        return "13800138000"
    elif "name" in key.lower():
        return "Mock Name"
    elif "id" in key.lower():
        return "mock_id_123"
    else:
        return mock_data.get(key.lower(), f"mock_{key}")

