"""
Import/Export Endpoints
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.import_export_service import ImportExportService

router = APIRouter()


@router.post("/excel/import")
async def import_excel(
    file: UploadFile = File(...),
    project_id: str = None,
    import_type: str = "functional_case",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Import data from Excel file"""
    service = ImportExportService()
    
    result = await service.import_excel(
        file=file,
        project_id=project_id,
        import_type=import_type,
    )
    
    return result


@router.post("/excel/export")
async def export_excel(
    data: List[Dict[str, Any]],
    filename: str = "export.xlsx",
    project_id: str = None,
    export_type: str = "functional_case",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export data to Excel file"""
    service = ImportExportService()
    
    excel_bytes = await service.export_excel(
        data=data,
        filename=filename,
        project_id=project_id,
        export_type=export_type,
    )
    
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        }
    )


@router.post("/xmind/import")
async def import_xmind(
    file: UploadFile = File(...),
    project_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Import data from XMind file"""
    service = ImportExportService()
    
    result = await service.import_xmind(
        file=file,
        project_id=project_id,
    )
    
    return result


@router.post("/postman/import")
async def import_postman(
    file: UploadFile = File(...),
    project_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Import Postman collection"""
    service = ImportExportService()
    
    result = await service.import_postman(
        file=file,
        project_id=project_id,
    )
    
    return result


@router.post("/swagger/import")
async def import_swagger(
    file: UploadFile = File(...),
    project_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Import Swagger/OpenAPI specification"""
    service = ImportExportService()
    
    result = await service.import_swagger(
        file=file,
        project_id=project_id,
    )
    
    return result


@router.post("/jmeter/import")
async def import_jmeter(
    file: UploadFile = File(...),
    project_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Import JMeter script"""
    service = ImportExportService()
    
    result = await service.import_jmeter(
        file=file,
        project_id=project_id,
    )
    
    return result

