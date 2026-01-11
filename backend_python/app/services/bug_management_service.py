"""
Bug Management Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Tuple
import uuid
import time

from app.models.bug import Bug
from app.models.bug_comment import BugComment
from app.models.bug_attachment import BugLocalAttachment
from app.schemas.bug_management import Bug as BugSchema


class BugManagementService:
    """Bug Management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_bugs(
        self,
        project_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        handle_user: Optional[str] = None
    ) -> List[Bug]:
        """Get bugs with pagination and filters"""
        query = select(Bug).where(Bug.deleted == False)
        
        if project_id:
            query = query.where(Bug.project_id == project_id)
        
        if keyword:
            query = query.where(Bug.title.like(f"%{keyword}%"))
        
        if status:
            query = query.where(Bug.status == status)
        
        if handle_user:
            query = query.where(Bug.handle_user == handle_user)
        
        query = query.offset(skip).limit(limit).order_by(Bug.pos.desc(), Bug.create_time.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_bug_by_id(self, bug_id: str) -> Optional[Bug]:
        """Get bug by ID"""
        result = await self.db.execute(
            select(Bug).where(Bug.id == bug_id, Bug.deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def count_bugs(
        self,
        project_id: Optional[str] = None,
        keyword: Optional[str] = None,
        status: Optional[str] = None
    ) -> int:
        """Count bugs"""
        query = select(func.count(Bug.id)).where(Bug.deleted == False)
        
        if project_id:
            query = query.where(Bug.project_id == project_id)
        
        if keyword:
            query = query.where(Bug.title.like(f"%{keyword}%"))
        
        if status:
            query = query.where(Bug.status == status)
        
        result = await self.db.execute(query)
        return result.scalar_one()
    
    async def create_bug(
        self,
        project_id: str,
        title: str,
        handle_user: str,
        template_id: str,
        platform: str,
        status: str,
        create_user: Optional[str] = None,
        **kwargs
    ) -> Bug:
        """Create bug"""
        bug_id = str(uuid.uuid4())
        
        # Get next num (bug number) for the project
        result = await self.db.execute(
            select(func.max(Bug.num)).where(Bug.project_id == project_id)
        )
        max_num = result.scalar_one_or_none() or 0
        next_num = max_num + 1
        
        # Get next pos (position) for sorting
        result = await self.db.execute(
            select(func.max(Bug.pos)).where(Bug.project_id == project_id)
        )
        max_pos = result.scalar_one_or_none() or 0
        next_pos = max_pos + 5000  # Interval of 5000
        
        # Parse tags if provided as list
        tags = kwargs.get("tags")
        if isinstance(tags, list):
            tags = ",".join(tags)
        
        bug = Bug(
            id=bug_id,
            num=next_num,
            title=title,
            handle_user=handle_user,
            handle_users=kwargs.get("handle_users"),
            project_id=project_id,
            template_id=template_id,
            platform=platform,
            status=status,
            tags=tags,
            platform_bug_id=kwargs.get("platform_bug_id"),
            pos=next_pos,
            create_user=create_user,
            deleted=False,
        )
        
        self.db.add(bug)
        await self.db.commit()
        await self.db.refresh(bug)
        return bug
    
    async def update_bug(
        self,
        bug_id: str,
        update_user: Optional[str] = None,
        **kwargs
    ) -> Optional[Bug]:
        """Update bug"""
        bug = await self.get_bug_by_id(bug_id)
        if not bug:
            return None
        
        # Handle tags if provided as list
        if "tags" in kwargs and isinstance(kwargs["tags"], list):
            kwargs["tags"] = ",".join(kwargs["tags"])
        
        for key, value in kwargs.items():
            if hasattr(bug, key) and value is not None:
                setattr(bug, key, value)
        
        bug.update_user = update_user
        bug.update_time = int(time.time() * 1000)
        
        await self.db.commit()
        await self.db.refresh(bug)
        return bug
    
    async def delete_bug(self, bug_id: str, delete_user: Optional[str] = None) -> bool:
        """Delete bug (soft delete)"""
        bug = await self.get_bug_by_id(bug_id)
        if not bug:
            return False
        
        bug.deleted = True
        bug.delete_time = int(time.time() * 1000)
        bug.delete_user = delete_user
        
        await self.db.commit()
        return True
    
    async def sync_bug_to_platform(self, bug_id: str, platform: str) -> bool:
        """Sync bug to third-party platform"""
        # TODO: Implement platform sync logic
        # This would typically call a plugin service to sync the bug
        return True
    
    # Bug Comment methods
    async def get_bug_comments(self, bug_id: str) -> List[dict]:
        """Get bug comments"""
        result = await self.db.execute(
            select(BugComment).where(BugComment.bug_id == bug_id).order_by(BugComment.create_time.asc())
        )
        comments = result.scalars().all()
        return [{
            "id": comment.id,
            "bug_id": comment.bug_id,
            "content": comment.content,
            "reply_user": comment.reply_user,
            "notifier": comment.notifier,
            "parent_id": comment.parent_id,
            "create_user": comment.create_user,
            "create_time": comment.create_time,
            "update_time": comment.update_time,
        } for comment in comments]
    
    async def create_bug_comment(
        self,
        bug_id: str,
        content: str,
        parent_id: Optional[str] = None,
        reply_user: Optional[str] = None,
        notifier: Optional[str] = None,
        create_user: Optional[str] = None,
    ) -> BugComment:
        """Create bug comment"""
        comment_id = str(uuid.uuid4())
        comment = BugComment(
            id=comment_id,
            bug_id=bug_id,
            content=content,
            parent_id=parent_id,
            reply_user=reply_user,
            notifier=notifier,
            create_user=create_user,
        )
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment
    
    async def update_bug_comment(
        self,
        comment_id: str,
        content: str,
        update_user: Optional[str] = None,
    ) -> Optional[BugComment]:
        """Update bug comment"""
        result = await self.db.execute(
            select(BugComment).where(BugComment.id == comment_id)
        )
        comment = result.scalar_one_or_none()
        if not comment:
            return None
        
        comment.content = content
        comment.update_user = update_user
        comment.update_time = int(time.time() * 1000)
        
        await self.db.commit()
        await self.db.refresh(comment)
        return comment
    
    async def delete_bug_comment(self, comment_id: str) -> bool:
        """Delete bug comment"""
        result = await self.db.execute(
            select(BugComment).where(BugComment.id == comment_id)
        )
        comment = result.scalar_one_or_none()
        if not comment:
            return False
        
        await self.db.delete(comment)
        await self.db.commit()
        return True
    
    # Bug Attachment methods
    async def get_bug_attachments(self, bug_id: str) -> List[dict]:
        """Get bug attachments"""
        result = await self.db.execute(
            select(BugLocalAttachment).where(BugLocalAttachment.bug_id == bug_id).order_by(BugLocalAttachment.create_time.desc())
        )
        attachments = result.scalars().all()
        return [{
            "id": att.id,
            "bug_id": att.bug_id,
            "file_id": att.file_id,
            "file_name": att.file_name,
            "size": att.size,
            "source": att.source,
            "create_user": att.create_user,
            "create_time": att.create_time,
        } for att in attachments]
    
    async def upload_bug_attachment(
        self,
        bug_id: str,
        file_name: str,
        file_content: bytes,
        file_size: int,
        source: str = "LOCAL",
        create_user: Optional[str] = None,
    ) -> BugLocalAttachment:
        """Upload bug attachment"""
        from app.core.minio import minio_client
        
        attachment_id = str(uuid.uuid4())
        
        # Save file to MinIO
        file_path = f"bug/{bug_id}/{attachment_id}/{file_name}"
        try:
            minio_client.upload_file(
                file_path=file_path,
                file_data=file_content,
                content_type=None,  # Auto-detect or pass from request
            )
            file_id = file_path  # Use file path as file_id
        except Exception as e:
            # Fallback: use attachment_id as file_id if MinIO fails
            file_id = attachment_id
        
        attachment = BugLocalAttachment(
            id=attachment_id,
            bug_id=bug_id,
            file_id=file_id,
            file_name=file_name,
            size=file_size,
            source=source,
            create_user=create_user,
        )
        self.db.add(attachment)
        await self.db.commit()
        await self.db.refresh(attachment)
        return attachment
    
    async def download_bug_attachment(self, attachment_id: str) -> Optional[Tuple[bytes, str]]:
        """Download bug attachment"""
        from app.core.minio import minio_client
        
        result = await self.db.execute(
            select(BugLocalAttachment).where(BugLocalAttachment.id == attachment_id)
        )
        attachment = result.scalar_one_or_none()
        if not attachment:
            return None
        
        # Retrieve file content from MinIO
        try:
            file_content = minio_client.download_file(attachment.file_id)
            return (file_content, attachment.file_name)
        except Exception as e:
            # Return None if file not found
            return None
    
    async def delete_bug_attachment(self, attachment_id: str) -> bool:
        """Delete bug attachment"""
        from app.core.minio import minio_client
        
        result = await self.db.execute(
            select(BugLocalAttachment).where(BugLocalAttachment.id == attachment_id)
        )
        attachment = result.scalar_one_or_none()
        if not attachment:
            return False
        
        # Delete file from MinIO
        try:
            minio_client.delete_file(attachment.file_id)
        except Exception as e:
            # Continue with database deletion even if MinIO deletion fails
            pass
        
        await self.db.delete(attachment)
        await self.db.commit()
        return True

