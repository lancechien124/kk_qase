"""
API Test Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional, Dict
import uuid
import time
import json

from app.models.api_test import ApiDefinition, ApiTestCase, ApiScenario
from app.schemas.api_test import ApiDefinition as ApiDefinitionSchema, ApiTestCase as ApiTestCaseSchema, ApiScenario as ApiScenarioSchema


class ApiTestService:
    """API Test service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # API Definition methods
    async def get_api_definitions(
        self, project_id: Optional[str] = None, skip: int = 0, limit: int = 100, keyword: Optional[str] = None
    ) -> List[ApiDefinition]:
        """Get API definitions"""
        query = select(ApiDefinition).where(ApiDefinition.deleted == False)
        
        if project_id:
            query = query.where(ApiDefinition.project_id == project_id)
        
        if keyword:
            query = query.where(
                (ApiDefinition.name.like(f"%{keyword}%")) |
                (ApiDefinition.path.like(f"%{keyword}%"))
            )
        
        query = query.offset(skip).limit(limit).order_by(ApiDefinition.create_time.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_api_definition_by_id(self, definition_id: str) -> Optional[ApiDefinition]:
        """Get API definition by ID"""
        result = await self.db.execute(
            select(ApiDefinition).where(
                ApiDefinition.id == definition_id,
                ApiDefinition.deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def create_api_definition(
        self,
        project_id: str,
        name: str,
        method: str,
        path: str,
        create_user: Optional[str] = None,
        **kwargs
    ) -> ApiDefinition:
        """Create API definition"""
        definition_id = str(uuid.uuid4())
        
        # Serialize request_body and response_body if provided
        request_body = kwargs.get("request_body")
        response_body = kwargs.get("response_body")
        
        if isinstance(request_body, dict):
            request_body = json.dumps(request_body, ensure_ascii=False)
        if isinstance(response_body, dict):
            response_body = json.dumps(response_body, ensure_ascii=False)
        
        definition = ApiDefinition(
            id=definition_id,
            project_id=project_id,
            name=name,
            method=method,
            path=path,
            description=kwargs.get("description"),
            request_body=request_body,
            response_body=response_body,
            status=kwargs.get("status", "PROCESSING"),
            module_id=kwargs.get("module_id"),
            create_user=create_user,
            deleted=False,
        )
        
        self.db.add(definition)
        await self.db.commit()
        await self.db.refresh(definition)
        return definition
    
    async def update_api_definition(
        self,
        definition_id: str,
        update_user: Optional[str] = None,
        **kwargs
    ) -> Optional[ApiDefinition]:
        """Update API definition"""
        definition = await self.get_api_definition_by_id(definition_id)
        if not definition:
            return None
        
        # Handle request_body and response_body serialization
        if "request_body" in kwargs and isinstance(kwargs["request_body"], dict):
            kwargs["request_body"] = json.dumps(kwargs["request_body"], ensure_ascii=False)
        if "response_body" in kwargs and isinstance(kwargs["response_body"], dict):
            kwargs["response_body"] = json.dumps(kwargs["response_body"], ensure_ascii=False)
        
        for key, value in kwargs.items():
            if hasattr(definition, key) and value is not None:
                setattr(definition, key, value)
        
        definition.update_user = update_user
        definition.update_time = int(time.time() * 1000)
        
        await self.db.commit()
        await self.db.refresh(definition)
        return definition
    
    async def delete_api_definition(self, definition_id: str, delete_user: Optional[str] = None) -> bool:
        """Delete API definition (soft delete)"""
        definition = await self.get_api_definition_by_id(definition_id)
        if not definition:
            return False
        
        definition.deleted = True
        definition.delete_time = int(time.time() * 1000)
        definition.delete_user = delete_user
        
        await self.db.commit()
        return True
    
    # API Test Case methods
    async def get_api_test_cases(
        self, project_id: Optional[str] = None, api_definition_id: Optional[str] = None,
        skip: int = 0, limit: int = 100, keyword: Optional[str] = None
    ) -> List[ApiTestCase]:
        """Get API test cases"""
        query = select(ApiTestCase).where(ApiTestCase.deleted == False)
        
        if project_id:
            query = query.where(ApiTestCase.project_id == project_id)
        
        if api_definition_id:
            query = query.where(ApiTestCase.api_definition_id == api_definition_id)
        
        if keyword:
            query = query.where(ApiTestCase.name.like(f"%{keyword}%"))
        
        query = query.offset(skip).limit(limit).order_by(ApiTestCase.create_time.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_api_test_case_by_id(self, test_case_id: str) -> Optional[ApiTestCase]:
        """Get API test case by ID"""
        result = await self.db.execute(
            select(ApiTestCase).where(
                ApiTestCase.id == test_case_id,
                ApiTestCase.deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def create_api_test_case(
        self,
        project_id: str,
        api_definition_id: str,
        name: str,
        request: dict,
        create_user: Optional[str] = None,
        **kwargs
    ) -> ApiTestCase:
        """Create API test case"""
        test_case_id = str(uuid.uuid4())
        
        # Serialize request and expected_response
        request_str = json.dumps(request, ensure_ascii=False) if isinstance(request, dict) else str(request)
        expected_response = kwargs.get("expected_response")
        if isinstance(expected_response, dict):
            expected_response = json.dumps(expected_response, ensure_ascii=False)
        
        test_case = ApiTestCase(
            id=test_case_id,
            project_id=project_id,
            api_definition_id=api_definition_id,
            name=name,
            request=request_str,
            expected_response=expected_response,
            status=kwargs.get("status", "PROCESSING"),
            priority=kwargs.get("priority", "P0"),
            create_user=create_user,
            deleted=False,
        )
        
        self.db.add(test_case)
        await self.db.commit()
        await self.db.refresh(test_case)
        return test_case
    
    async def update_api_test_case(
        self,
        test_case_id: str,
        update_user: Optional[str] = None,
        **kwargs
    ) -> Optional[ApiTestCase]:
        """Update API test case"""
        test_case = await self.get_api_test_case_by_id(test_case_id)
        if not test_case:
            return None
        
        # Handle request and expected_response serialization
        if "request" in kwargs and isinstance(kwargs["request"], dict):
            kwargs["request"] = json.dumps(kwargs["request"], ensure_ascii=False)
        if "expected_response" in kwargs and isinstance(kwargs["expected_response"], dict):
            kwargs["expected_response"] = json.dumps(kwargs["expected_response"], ensure_ascii=False)
        
        for key, value in kwargs.items():
            if hasattr(test_case, key) and value is not None:
                setattr(test_case, key, value)
        
        test_case.update_user = update_user
        test_case.update_time = int(time.time() * 1000)
        
        await self.db.commit()
        await self.db.refresh(test_case)
        return test_case
    
    async def delete_api_test_case(self, test_case_id: str, delete_user: Optional[str] = None) -> bool:
        """Delete API test case (soft delete)"""
        test_case = await self.get_api_test_case_by_id(test_case_id)
        if not test_case:
            return False
        
        test_case.deleted = True
        test_case.delete_time = int(time.time() * 1000)
        test_case.delete_user = delete_user
        
        await self.db.commit()
        return True
    
    # API Scenario methods
    async def get_api_scenarios(
        self, project_id: Optional[str] = None, skip: int = 0, limit: int = 100, keyword: Optional[str] = None
    ) -> List[ApiScenario]:
        """Get API scenarios"""
        query = select(ApiScenario).where(ApiScenario.deleted == False)
        
        if project_id:
            query = query.where(ApiScenario.project_id == project_id)
        
        if keyword:
            query = query.where(ApiScenario.name.like(f"%{keyword}%"))
        
        query = query.offset(skip).limit(limit).order_by(ApiScenario.create_time.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_api_scenario_by_id(self, scenario_id: str) -> Optional[ApiScenario]:
        """Get API scenario by ID"""
        result = await self.db.execute(
            select(ApiScenario).where(
                ApiScenario.id == scenario_id,
                ApiScenario.deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def create_api_scenario(
        self,
        project_id: str,
        name: str,
        create_user: Optional[str] = None,
        **kwargs
    ) -> ApiScenario:
        """Create API scenario"""
        scenario_id = str(uuid.uuid4())
        
        scenario = ApiScenario(
            id=scenario_id,
            project_id=project_id,
            name=name,
            description=kwargs.get("description"),
            status=kwargs.get("status", "PROCESSING"),
            module_id=kwargs.get("module_id"),
            create_user=create_user,
            deleted=False,
        )
        
        self.db.add(scenario)
        await self.db.commit()
        await self.db.refresh(scenario)
        return scenario
    
    async def update_api_scenario(
        self,
        scenario_id: str,
        update_user: Optional[str] = None,
        **kwargs
    ) -> Optional[ApiScenario]:
        """Update API scenario"""
        scenario = await self.get_api_scenario_by_id(scenario_id)
        if not scenario:
            return None
        
        for key, value in kwargs.items():
            if hasattr(scenario, key) and value is not None:
                setattr(scenario, key, value)
        
        scenario.update_user = update_user
        scenario.update_time = int(time.time() * 1000)
        
        await self.db.commit()
        await self.db.refresh(scenario)
        return scenario
    
    async def delete_api_scenario(self, scenario_id: str, delete_user: Optional[str] = None) -> bool:
        """Delete API scenario (soft delete)"""
        scenario = await self.get_api_scenario_by_id(scenario_id)
        if not scenario:
            return False
        
        scenario.deleted = True
        scenario.delete_time = int(time.time() * 1000)
        scenario.delete_user = delete_user
        
        await self.db.commit()
        return True
    
    async def execute_api_test(self, test_case_id: str, environment_id: Optional[str] = None, is_scenario: bool = False) -> Dict:
        """Execute API test case"""
        from app.core.kafka import notify_test_execution_result
        from app.tasks.test_execution import execute_api_test_task
        from app.utils.task_running_cache import task_running_cache
        
        # Check if task is already running
        is_running = await task_running_cache.exists(test_case_id)
        if is_running:
            return {
                "test_case_id": test_case_id,
                "status": "already_running",
                "message": "Test is already running"
            }
        
        # Mark task as running
        await task_running_cache.set_if_absent(test_case_id)
        
        # Send notification that test execution started
        notify_test_execution_result(
            test_id=test_case_id,
            test_type="api_scenario" if is_scenario else "api_test",
            status="running",
            result={},
            project_id=None
        )
        
        # Execute asynchronously using Celery
        task = execute_api_test_task.delay(test_case_id, environment_id)
        
        return {
            "test_case_id": test_case_id,
            "task_id": task.id,
            "status": "running",
            "environment_id": environment_id,
            "is_scenario": is_scenario
        }
    
    async def import_api_definitions(
        self,
        file_content: bytes,
        file_name: str,
        project_id: str,
        module_id: Optional[str] = None,
        platform: str = "Swagger3",
        cover_data: bool = False,
        sync_case: bool = False,
    ) -> Dict:
        """Import API definitions from file"""
        # TODO: Implement actual import logic based on platform
        return {
            "imported_count": 0,
            "updated_count": 0,
            "errors": []
        }
    
    async def export_api_definitions(self, definition_ids: List[str], export_type: str = "json") -> Dict:
        """Export API definitions to file"""
        definitions = []
        for definition_id in definition_ids:
            definition = await self.get_api_definition_by_id(definition_id)
            if definition:
                definitions.append({
                    "id": definition.id,
                    "name": definition.name,
                    "method": definition.method,
                    "path": definition.path,
                    "request_body": json.loads(definition.request_body) if definition.request_body else None,
                    "response_body": json.loads(definition.response_body) if definition.response_body else None,
                })
        
        return {
            "definitions": definitions,
            "export_type": export_type
        }
    
    async def import_api_scenarios(
        self,
        file_content: bytes,
        file_name: str,
        project_id: str,
        module_id: Optional[str] = None,
        platform: str = "Metersphere",
        cover_data: bool = False,
    ) -> Dict:
        """Import API scenarios from file"""
        # TODO: Implement actual import logic
        return {
            "imported_count": 0,
            "errors": []
        }
    
    async def export_api_scenarios(self, scenario_ids: List[str], export_type: str = "json") -> Dict:
        """Export API scenarios to file"""
        scenarios = []
        for scenario_id in scenario_ids:
            scenario = await self.get_api_scenario_by_id(scenario_id)
            if scenario:
                scenarios.append({
                    "id": scenario.id,
                    "name": scenario.name,
                    "description": scenario.description,
                    "status": scenario.status,
                })
        
        return {
            "scenarios": scenarios,
            "export_type": export_type
        }

