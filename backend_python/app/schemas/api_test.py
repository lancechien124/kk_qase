"""
API Test Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ApiDefinitionBase(BaseModel):
    """Base API Definition schema"""
    name: str = Field(..., min_length=1, max_length=255, description="接口名称")
    method: str = Field(..., description="请求方法")
    path: str = Field(..., max_length=500, description="请求路径")
    description: Optional[str] = Field(None, description="描述")
    request_body: Optional[Dict[str, Any]] = Field(None, description="请求体")
    response_body: Optional[Dict[str, Any]] = Field(None, description="响应体")
    status: Optional[str] = Field(None, description="状态")
    module_id: Optional[str] = Field(None, description="模块ID")


class ApiDefinitionCreate(ApiDefinitionBase):
    """API Definition creation schema"""
    project_id: str = Field(..., min_length=1, max_length=50, description="项目ID")
    create_user: Optional[str] = Field(None, max_length=50, description="创建人")


class ApiDefinitionUpdate(BaseModel):
    """API Definition update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="接口名称")
    method: Optional[str] = Field(None, description="请求方法")
    path: Optional[str] = Field(None, max_length=500, description="请求路径")
    description: Optional[str] = Field(None, description="描述")
    request_body: Optional[Dict[str, Any]] = Field(None, description="请求体")
    response_body: Optional[Dict[str, Any]] = Field(None, description="响应体")
    status: Optional[str] = Field(None, description="状态")
    module_id: Optional[str] = Field(None, description="模块ID")
    update_user: Optional[str] = Field(None, max_length=50, description="修改人")


class ApiDefinition(ApiDefinitionBase):
    """API Definition response schema"""
    id: str
    project_id: str
    create_time: Optional[int] = None
    update_time: Optional[int] = None
    deleted: bool = False

    class Config:
        from_attributes = True


class ApiTestCase(BaseModel):
    """API Test Case schema"""
    id: Optional[str] = None
    project_id: str
    api_definition_id: str
    name: str
    request: Dict[str, Any]
    expected_response: Optional[Dict[str, Any]] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApiScenario(BaseModel):
    """API Scenario schema"""
    id: Optional[str] = None
    project_id: str
    name: str
    steps: list[Dict[str, Any]]
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True

