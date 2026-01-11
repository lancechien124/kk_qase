"""
AI Schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class AIChatRequest(BaseModel):
    """AI chat request"""
    prompt: str
    conversation_id: Optional[str] = None
    system_prompt: Optional[str] = None


class AIChatResponse(BaseModel):
    """AI chat response"""
    content: str
    conversation_id: Optional[str] = None


class GenerateTestCaseRequest(BaseModel):
    """Request to generate test case"""
    requirement: str
    project_id: str
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class GenerateTestCaseResponse(BaseModel):
    """Response with generated test case"""
    test_case: Dict[str, Any]
    success: bool


class GenerateTestDataRequest(BaseModel):
    """Request to generate test data"""
    data_type: str  # e.g., "user", "email", "phone", "address"
    count: int = 1
    constraints: Optional[Dict[str, Any]] = None


class GenerateTestDataResponse(BaseModel):
    """Response with generated test data"""
    data: List[Dict[str, Any]]
    count: int


class AIConfigResponse(BaseModel):
    """AI configuration response"""
    enabled: bool
    model_available: bool
    base_url: Optional[str] = None

