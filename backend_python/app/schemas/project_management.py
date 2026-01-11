"""
Project Management Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=255, description="项目名称")
    description: Optional[str] = Field(None, max_length=500, description="项目描述")


class ProjectCreate(ProjectBase):
    """Project creation schema"""
    organization_id: str = Field(..., min_length=1, max_length=50, description="组织ID")
    enable: Optional[bool] = Field(True, description="是否启用")
    all_resource_pool: Optional[bool] = Field(False, description="全部资源池")
    create_user: Optional[str] = Field(None, max_length=50, description="创建人")


class ProjectUpdate(BaseModel):
    """Project update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="项目名称")
    description: Optional[str] = Field(None, max_length=500, description="项目描述")
    enable: Optional[bool] = Field(None, description="是否启用")
    all_resource_pool: Optional[bool] = Field(None, description="全部资源池")
    module_setting: Optional[str] = Field(None, max_length=500, description="模块设置")
    update_user: Optional[str] = Field(None, max_length=50, description="修改人")


class Project(ProjectBase):
    """Project response schema"""
    id: str
    num: Optional[int] = None
    organization_id: str
    enable: bool
    all_resource_pool: bool
    module_setting: Optional[str] = None
    create_time: Optional[int] = None
    update_time: Optional[int] = None
    deleted: bool = False

    class Config:
        from_attributes = True

