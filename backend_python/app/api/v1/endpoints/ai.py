"""
AI Integration Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.ai_service import AIService
from app.services.functional_case_ai_service import FunctionalCaseAIService
from app.services.api_test_case_ai_service import ApiTestCaseAIService
from app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    GenerateTestCaseRequest,
    GenerateTestCaseResponse,
    GenerateTestDataRequest,
    GenerateTestDataResponse,
)

router = APIRouter()


@router.post("/chat", response_model=AIChatResponse)
async def ai_chat(
    request: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """General AI chat"""
    ai_service = AIService()
    
    if not ai_service.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not enabled or configured"
        )
    
    try:
        response = await ai_service.chat(
            prompt=request.prompt,
            conversation_id=request.conversation_id,
            system_prompt=request.system_prompt,
        )
        
        return AIChatResponse(
            content=response,
            conversation_id=request.conversation_id,
        )
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI chat failed: {str(e)}"
        )


@router.post("/functional-case/chat", response_model=AIChatResponse)
async def functional_case_ai_chat(
    request: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI chat for functional case generation"""
    service = FunctionalCaseAIService(db)
    
    try:
        response = await service.chat(
            prompt=request.prompt,
            conversation_id=request.conversation_id,
            user_id=current_user.id,
        )
        
        return AIChatResponse(
            content=response,
            conversation_id=request.conversation_id,
        )
    except Exception as e:
        logger.error(f"Error in functional case AI chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Functional case AI chat failed: {str(e)}"
        )


@router.post("/functional-case/generate", response_model=GenerateTestCaseResponse)
async def generate_functional_case(
    request: GenerateTestCaseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate functional test case using AI"""
    service = FunctionalCaseAIService(db)
    
    try:
        result = await service.generate_functional_case(
            requirement=request.requirement,
            project_id=request.project_id,
            user_id=current_user.id,
            context=request.context,
        )
        
        return GenerateTestCaseResponse(
            test_case=result,
            success=True,
        )
    except Exception as e:
        logger.error(f"Error generating functional case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate functional case: {str(e)}"
        )


@router.post("/api-case/chat", response_model=AIChatResponse)
async def api_case_ai_chat(
    api_definition_id: str,
    request: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI chat for API test case generation"""
    service = ApiTestCaseAIService(db)
    
    try:
        response = await service.chat(
            api_definition_id=api_definition_id,
            prompt=request.prompt,
            conversation_id=request.conversation_id,
            user_id=current_user.id,
        )
        
        return AIChatResponse(
            content=response,
            conversation_id=request.conversation_id,
        )
    except Exception as e:
        logger.error(f"Error in API case AI chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"API case AI chat failed: {str(e)}"
        )


@router.post("/api-case/generate", response_model=GenerateTestCaseResponse)
async def generate_api_test_case(
    api_definition_id: str,
    request: GenerateTestCaseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate API test case using AI"""
    service = ApiTestCaseAIService(db)
    
    try:
        response = await service.generate_api_test_case(
            api_definition_id=api_definition_id,
            user_prompt=request.requirement,
            conversation_id=request.conversation_id,
            user_id=current_user.id,
        )
        
        return GenerateTestCaseResponse(
            test_case={"content": response},
            success=True,
        )
    except Exception as e:
        logger.error(f"Error generating API test case: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate API test case: {str(e)}"
        )


@router.post("/test-data/generate", response_model=GenerateTestDataResponse)
async def generate_test_data(
    request: GenerateTestDataRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate test data using AI"""
    ai_service = AIService()
    
    if not ai_service.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not enabled or configured"
        )
    
    try:
        data = await ai_service.generate_test_data(
            data_type=request.data_type,
            count=request.count,
            constraints=request.constraints,
        )
        
        return GenerateTestDataResponse(
            data=data,
            count=len(data),
        )
    except Exception as e:
        logger.error(f"Error generating test data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate test data: {str(e)}"
        )


@router.get("/config")
async def get_ai_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get AI configuration"""
    from app.core.config import settings
    
    return {
        "enabled": settings.AI_ENABLED,
        "model_available": settings.OPENAI_API_KEY is not None,
        "base_url": settings.OPENAI_BASE_URL,
    }

