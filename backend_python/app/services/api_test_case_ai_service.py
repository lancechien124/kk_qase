"""
API Test Case AI Service
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai_service import AIService
from app.core.logging import logger


class ApiTestCaseAIService:
    """AI service for API test case generation"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIService()
    
    async def chat(
        self,
        api_definition_id: str,
        prompt: str,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """
        AI chat for API test case generation
        
        Args:
            api_definition_id: API definition ID
            prompt: User prompt
            conversation_id: Conversation ID
            user_id: User ID
        
        Returns:
            AI response
        """
        # Get API definition
        from app.services.api_test_service import ApiTestService
        api_test_service = ApiTestService(self.db)
        api_definition = await api_test_service.get_api_definition_by_id(api_definition_id)
        
        if not api_definition:
            raise ValueError(f"API definition not found: {api_definition_id}")
        
        # Check if user wants to generate test case
        is_generate_case = await self.ai_service.check_if_generate_case(prompt)
        
        if is_generate_case:
            # Generate test case
            logger.info("User wants to generate API test case")
            api_def_dict = {
                "id": api_definition.id,
                "name": api_definition.name,
                "method": api_definition.method,
                "path": api_definition.path,
                "description": api_definition.description,
                "request_body": api_definition.request_body,
                "response_body": api_definition.response_body,
            }
            
            response = await self.ai_service.generate_api_test_case(
                api_definition=api_def_dict,
                user_prompt=prompt,
                conversation_id=conversation_id,
            )
        else:
            # Normal chat
            logger.info("Normal AI chat")
            response = await self.ai_service.chat(
                prompt=prompt,
                conversation_id=conversation_id,
            )
        
        # Save conversation
        if conversation_id:
            await self.ai_service.save_conversation(conversation_id, "user", prompt)
            await self.ai_service.save_conversation(conversation_id, "assistant", response)
        
        return response
    
    async def generate_api_test_case(
        self,
        api_definition_id: str,
        user_prompt: Optional[str] = None,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Generate API test case from API definition
        
        Args:
            api_definition_id: API definition ID
            user_prompt: Optional user prompt
            conversation_id: Conversation ID
            user_id: User ID
        
        Returns:
            Generated test case content
        """
        # Get API definition
        from app.services.api_test_service import ApiTestService
        api_test_service = ApiTestService(self.db)
        api_definition = await api_test_service.get_api_definition_by_id(api_definition_id)
        
        if not api_definition:
            raise ValueError(f"API definition not found: {api_definition_id}")
        
        api_def_dict = {
            "id": api_definition.id,
            "name": api_definition.name,
            "method": api_definition.method,
            "path": api_definition.path,
            "description": api_definition.description,
            "request_body": api_definition.request_body,
            "response_body": api_definition.response_body,
        }
        
        return await self.ai_service.generate_api_test_case(
            api_definition=api_def_dict,
            user_prompt=user_prompt,
            conversation_id=conversation_id,
        )
    
    async def transform_to_case_dto(
        self,
        ai_response: str,
        api_definition_id: str,
    ) -> Dict[str, Any]:
        """
        Transform AI response to API test case DTO
        
        Args:
            ai_response: AI generated response
            api_definition_id: API definition ID
        
        Returns:
            API test case DTO
        """
        # TODO: Implement intelligent parsing of AI response
        # This should extract structured data and create ApiTestCase object
        return {
            "name": "AI Generated Test Case",
            "api_definition_id": api_definition_id,
            "request": "",
            "expected_response": ai_response,
        }
    
    async def get_user_prompt_config(self, user_id: str) -> Dict[str, Any]:
        """Get user's AI prompt configuration"""
        # TODO: Load from database
        return {
            "prompt": "",
            "enabled": True,
        }
    
    async def save_user_prompt_config(
        self,
        user_id: str,
        config: Dict[str, Any],
    ):
        """Save user's AI prompt configuration"""
        # TODO: Save to database
        pass

