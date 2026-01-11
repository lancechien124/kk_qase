"""
Bug Management Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class BugBase(BaseModel):
    """Base Bug schema"""
    title: str = Field(..., min_length=1, max_length=255, description="缺陷标题")
    handle_user: str = Field(..., min_length=1, max_length=50, description="处理人")
    template_id: str = Field(..., min_length=1, max_length=50, description="模板ID")
    platform: str = Field(..., min_length=1, max_length=50, description="缺陷平台")
    status: str = Field(..., min_length=1, max_length=50, description="状态")


class BugCreate(BugBase):
    """Bug creation schema"""
    project_id: str = Field(..., min_length=1, max_length=50, description="项目ID")
    handle_users: Optional[str] = Field(None, max_length=500, description="处理人集合")
    tags: Optional[List[str]] = Field(None, description="标签")
    platform_bug_id: Optional[str] = Field(None, max_length=100, description="第三方平台缺陷ID")
    create_user: Optional[str] = Field(None, max_length=50, description="创建人")


class BugUpdate(BaseModel):
    """Bug update schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="缺陷标题")
    handle_user: Optional[str] = Field(None, min_length=1, max_length=50, description="处理人")
    handle_users: Optional[str] = Field(None, max_length=500, description="处理人集合")
    status: Optional[str] = Field(None, min_length=1, max_length=50, description="状态")
    tags: Optional[List[str]] = Field(None, description="标签")
    platform_bug_id: Optional[str] = Field(None, max_length=100, description="第三方平台缺陷ID")
    update_user: Optional[str] = Field(None, max_length=50, description="修改人")


class Bug(BugBase):
    """Bug response schema"""
    id: str
    num: Optional[int] = None
    project_id: str
    handle_users: Optional[str] = None
    tags: Optional[str] = None
    platform_bug_id: Optional[str] = None
    pos: int = 0
    create_time: Optional[int] = None
    update_time: Optional[int] = None
    deleted: bool = False

    class Config:
        from_attributes = True

