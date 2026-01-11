"""
Bug Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import io

from app.core.database import get_db
from app.schemas.bug_management import Bug, BugCreate, BugUpdate
from app.services.bug_management_service import BugManagementService

router = APIRouter()


@router.get("/bugs", response_model=List[Bug])
async def get_bugs(
    project_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    keyword: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    handle_user: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get bugs with pagination and filters"""
    service = BugManagementService(db)
    return await service.get_bugs(project_id, skip, limit, keyword, status, handle_user)


@router.get("/bugs/{bug_id}", response_model=Bug)
async def get_bug(
    bug_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get bug by ID"""
    service = BugManagementService(db)
    bug = await service.get_bug_by_id(bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return bug


@router.post("/bugs", response_model=Bug)
async def create_bug(
    bug_data: BugCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create bug"""
    service = BugManagementService(db)
    bug = await service.create_bug(
        project_id=bug_data.project_id,
        title=bug_data.title,
        handle_user=bug_data.handle_user,
        template_id=bug_data.template_id,
        platform=bug_data.platform,
        status=bug_data.status,
        create_user=bug_data.create_user,
        handle_users=bug_data.handle_users,
        tags=bug_data.tags,
        platform_bug_id=bug_data.platform_bug_id,
    )
    return bug


@router.put("/bugs/{bug_id}", response_model=Bug)
async def update_bug(
    bug_id: str,
    bug_data: BugUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update bug"""
    service = BugManagementService(db)
    update_dict = bug_data.dict(exclude_unset=True)
    bug = await service.update_bug(bug_id, **update_dict)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return bug


@router.delete("/bugs/{bug_id}")
async def delete_bug(
    bug_id: str,
    delete_user: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Delete bug (soft delete)"""
    service = BugManagementService(db)
    success = await service.delete_bug(bug_id, delete_user)
    if not success:
        raise HTTPException(status_code=404, detail="Bug not found")
    return {"message": "Bug deleted successfully"}


@router.post("/bugs/{bug_id}/sync")
async def sync_bug_to_platform(
    bug_id: str,
    platform: str = Query(..., description="Platform to sync to"),
    db: AsyncSession = Depends(get_db),
):
    """Sync bug to third-party platform"""
    service = BugManagementService(db)
    success = await service.sync_bug_to_platform(bug_id, platform)
    if not success:
        raise HTTPException(status_code=404, detail="Bug not found or sync failed")
    return {"message": "Bug synced successfully"}


# Bug Comment Endpoints
@router.get("/bugs/{bug_id}/comments", response_model=List[dict])
async def get_bug_comments(
    bug_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get bug comments"""
    service = BugManagementService(db)
    comments = await service.get_bug_comments(bug_id)
    return comments


@router.post("/bugs/{bug_id}/comments")
async def create_bug_comment(
    bug_id: str,
    content: str = Form(...),
    parent_id: Optional[str] = Form(None),
    reply_user: Optional[str] = Form(None),
    notifier: Optional[str] = Form(None),
    create_user: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Create bug comment"""
    service = BugManagementService(db)
    comment = await service.create_bug_comment(
        bug_id=bug_id,
        content=content,
        parent_id=parent_id,
        reply_user=reply_user,
        notifier=notifier,
        create_user=create_user,
    )
    return comment


@router.put("/comments/{comment_id}")
async def update_bug_comment(
    comment_id: str,
    content: str = Form(...),
    update_user: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Update bug comment"""
    service = BugManagementService(db)
    comment = await service.update_bug_comment(comment_id, content, update_user)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.delete("/comments/{comment_id}")
async def delete_bug_comment(
    comment_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete bug comment"""
    service = BugManagementService(db)
    success = await service.delete_bug_comment(comment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Comment deleted successfully"}


# Bug Attachment Endpoints
@router.get("/bugs/{bug_id}/attachments", response_model=List[dict])
async def get_bug_attachments(
    bug_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get bug attachments"""
    service = BugManagementService(db)
    attachments = await service.get_bug_attachments(bug_id)
    return attachments


@router.post("/bugs/{bug_id}/attachments")
async def upload_bug_attachment(
    bug_id: str,
    file: UploadFile = File(...),
    source: str = Form("LOCAL", description="Attachment source: LOCAL, MINIO"),
    create_user: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Upload bug attachment"""
    service = BugManagementService(db)
    file_content = await file.read()
    attachment = await service.upload_bug_attachment(
        bug_id=bug_id,
        file_name=file.filename,
        file_content=file_content,
        file_size=len(file_content),
        source=source,
        create_user=create_user,
    )
    return attachment


@router.get("/attachments/{attachment_id}/download")
async def download_bug_attachment(
    attachment_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Download bug attachment"""
    service = BugManagementService(db)
    attachment_data = await service.download_bug_attachment(attachment_id)
    if not attachment_data:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    file_content, file_name = attachment_data
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )


@router.delete("/attachments/{attachment_id}")
async def delete_bug_attachment(
    attachment_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete bug attachment"""
    service = BugManagementService(db)
    success = await service.delete_bug_attachment(attachment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return {"message": "Attachment deleted successfully"}

