"""
Functional Case AI Service
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai_service import AIService
from app.core.logging import logger


class FunctionalCaseAIService:
    """AI service for functional case generation"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIService()
    
    async def chat(
        self,
        prompt: str,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """
        AI chat for functional case generation
        
        Args:
            prompt: User prompt
            conversation_id: Conversation ID
            user_id: User ID
        
        Returns:
            AI response
        """
        # Check if user wants to generate test case
        is_generate_case = await self.ai_service.check_if_generate_case(prompt)
        
        if is_generate_case:
            # Generate test case
            logger.info("User wants to generate functional test case")
            system_prompt = self._get_functional_case_system_prompt(user_id)
            response = await self.ai_service.chat(
                prompt=prompt,
                conversation_id=conversation_id,
                system_prompt=system_prompt,
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
    
    async def generate_functional_case(
        self,
        requirement: str,
        project_id: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate functional test case
        
        Args:
            requirement: Requirement description
            project_id: Project ID
            user_id: User ID
            context: Optional context
        
        Returns:
            Generated test case data
        """
        return await self.ai_service.generate_test_case(
            requirement=requirement,
            project_id=project_id,
            case_type="functional",
            context=context,
        )
    
    def _get_functional_case_system_prompt(self, user_id: Optional[str] = None) -> str:
        """Get system prompt for functional case generation"""
        # TODO: Load user-specific prompt configuration from database
        base_prompt = """You are a functional test case generation assistant.
Generate comprehensive functional test cases based on requirements.

Format your response in Markdown with:
- Test case name
- Preconditions
- Test steps (numbered)
- Expected results
- Priority (High/Medium/Low)
"""
        return base_prompt
    
    async def transform_to_case_dto(
        self,
        ai_response: str,
    ) -> Dict[str, Any]:
        """
        Transform AI response to functional case DTO
        
        Args:
            ai_response: AI generated response
        
        Returns:
            Functional case DTO
        """
        # TODO: Implement intelligent parsing of AI response
        # This should extract structured data and create FunctionalCase object
        return {
            "name": "AI Generated Case",
            "description": ai_response,
            "steps": [],
            "expected_result": "",
        }

