"""
Case Management Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import uuid
import time
import json

from app.models.functional_case import FunctionalCase, FunctionalCaseBlob
from app.schemas.case_management import FunctionalCase as FunctionalCaseSchema


class CaseManagementService:
    """Case Management service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_functional_cases(
        self,
        project_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        keyword: Optional[str] = None,
        module_id: Optional[str] = None
    ) -> List[FunctionalCase]:
        """Get functional cases"""
        query = select(FunctionalCase).where(FunctionalCase.deleted == False, FunctionalCase.latest == True)
        
        if project_id:
            query = query.where(FunctionalCase.project_id == project_id)
        
        if module_id:
            query = query.where(FunctionalCase.module_id == module_id)
        
        if keyword:
            query = query.where(FunctionalCase.name.like(f"%{keyword}%"))
        
        query = query.offset(skip).limit(limit).order_by(FunctionalCase.pos.desc(), FunctionalCase.create_time.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_functional_case_by_id(self, case_id: str) -> Optional[FunctionalCase]:
        """Get functional case by ID"""
        result = await self.db.execute(
            select(FunctionalCase).where(
                FunctionalCase.id == case_id,
                FunctionalCase.deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def create_functional_case(
        self,
        project_id: str,
        module_id: str,
        template_id: str,
        name: str,
        case_edit_type: str,
        version_id: str,
        ref_id: str,
        create_user: Optional[str] = None,
        **kwargs
    ) -> FunctionalCase:
        """Create functional case"""
        case_id = str(uuid.uuid4())
        
        # Get next num (case number) for the project
        result = await self.db.execute(
            select(func.max(FunctionalCase.num)).where(FunctionalCase.project_id == project_id)
        )
        max_num = result.scalar_one_or_none() or 0
        next_num = max_num + 1
        
        # Get next pos (position) for sorting
        result = await self.db.execute(
            select(func.max(FunctionalCase.pos)).where(FunctionalCase.project_id == project_id)
        )
        max_pos = result.scalar_one_or_none() or 0
        next_pos = max_pos + 5000  # Interval of 5000
        
        # Parse tags if provided as list
        tags = kwargs.get("tags")
        if isinstance(tags, list):
            tags = json.dumps(tags, ensure_ascii=False)
        
        functional_case = FunctionalCase(
            id=case_id,
            num=next_num,
            module_id=module_id,
            project_id=project_id,
            template_id=template_id,
            name=name,
            review_status=kwargs.get("review_status", "UN_REVIEWED"),
            tags=tags,
            case_edit_type=case_edit_type,
            pos=next_pos,
            version_id=version_id,
            ref_id=ref_id,
            last_execute_result=kwargs.get("last_execute_result", "UN_EXECUTED"),
            ai_create=kwargs.get("ai_create", False),
            public_case=kwargs.get("public_case", False),
            latest=True,
            create_user=create_user,
            deleted=False,
        )
        
        self.db.add(functional_case)
        
        # Create blob if steps or text data provided
        if kwargs.get("steps") or kwargs.get("text_description") or kwargs.get("expected_result"):
            blob = FunctionalCaseBlob(
                id=case_id,
                steps=json.dumps(kwargs.get("steps"), ensure_ascii=False) if kwargs.get("steps") else None,
                text_description=kwargs.get("text_description"),
                expected_result=kwargs.get("expected_result"),
                prerequisite=kwargs.get("prerequisite"),
                description=kwargs.get("description"),
            )
            self.db.add(blob)
        
        await self.db.commit()
        await self.db.refresh(functional_case)
        return functional_case
    
    async def update_functional_case(
        self,
        case_id: str,
        update_user: Optional[str] = None,
        **kwargs
    ) -> Optional[FunctionalCase]:
        """Update functional case"""
        functional_case = await self.get_functional_case_by_id(case_id)
        if not functional_case:
            return None
        
        # Handle tags if provided as list
        if "tags" in kwargs and isinstance(kwargs["tags"], list):
            kwargs["tags"] = json.dumps(kwargs["tags"], ensure_ascii=False)
        
        for key, value in kwargs.items():
            if hasattr(functional_case, key) and value is not None:
                setattr(functional_case, key, value)
        
        functional_case.update_user = update_user
        functional_case.update_time = int(time.time() * 1000)
        
        # Update blob if provided
        if any(k in kwargs for k in ["steps", "text_description", "expected_result", "prerequisite", "description"]):
            blob_result = await self.db.execute(
                select(FunctionalCaseBlob).where(FunctionalCaseBlob.id == case_id)
            )
            blob = blob_result.scalar_one_or_none()
            
            if not blob:
                blob = FunctionalCaseBlob(id=case_id)
                self.db.add(blob)
            
            if "steps" in kwargs:
                blob.steps = json.dumps(kwargs["steps"], ensure_ascii=False) if isinstance(kwargs["steps"], list) else kwargs["steps"]
            if "text_description" in kwargs:
                blob.text_description = kwargs["text_description"]
            if "expected_result" in kwargs:
                blob.expected_result = kwargs["expected_result"]
            if "prerequisite" in kwargs:
                blob.prerequisite = kwargs["prerequisite"]
            if "description" in kwargs:
                blob.description = kwargs["description"]
        
        await self.db.commit()
        await self.db.refresh(functional_case)
        return functional_case
    
    async def delete_functional_case(self, case_id: str, delete_user: Optional[str] = None) -> bool:
        """Delete functional case (soft delete)"""
        functional_case = await self.get_functional_case_by_id(case_id)
        if not functional_case:
            return False
        
        functional_case.deleted = True
        functional_case.delete_time = int(time.time() * 1000)
        functional_case.delete_user = delete_user
        
        await self.db.commit()
        return True
    
    async def import_cases_from_excel(
        self,
        file_content: bytes,
        file_name: str,
        project_id: str,
        module_id: Optional[str] = None,
    ) -> dict:
        """Import cases from Excel file"""
        # TODO: Implement Excel import logic using openpyxl or pandas
        return {
            "imported_count": 0,
            "errors": []
        }
    
    async def export_cases_to_excel(self, case_ids: List[str]) -> bytes:
        """Export cases to Excel file"""
        # TODO: Implement Excel export logic using openpyxl or pandas
        # For now, return empty bytes
        return b""
    
    async def import_cases_from_xmind(
        self,
        file_content: bytes,
        file_name: str,
        project_id: str,
        module_id: Optional[str] = None,
    ) -> dict:
        """Import cases from XMind file"""
        # TODO: Implement XMind import logic
        return {
            "imported_count": 0,
            "errors": []
        }
    
    async def execute_functional_case(
        self,
        case_id: str,
        environment_id: Optional[str] = None,
    ) -> Optional[dict]:
        """Execute functional case"""
        from app.tasks.test_execution import execute_functional_case_task
        
        case = await self.get_functional_case_by_id(case_id)
        if not case:
            return None
        
        # Execute asynchronously using Celery
        task = execute_functional_case_task.delay(case_id, environment_id)
        
        return {
            "case_id": case_id,
            "task_id": task.id,
            "status": "running",
            "environment_id": environment_id,
        }

