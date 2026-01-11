"""
User Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    name: str = Field(..., min_length=1, max_length=255, description="用户名")
    email: EmailStr = Field(..., description="用户邮箱")
    language: Optional[str] = Field(None, max_length=50, description="语言")
    phone: Optional[str] = Field(None, max_length=50, description="手机号")


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=6, description="用户密码")
    source: Optional[str] = Field("LOCAL", max_length=50, description="来源")
    create_user: Optional[str] = Field(None, max_length=50, description="创建人")


class UserUpdate(BaseModel):
    """User update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="用户名")
    email: Optional[EmailStr] = Field(None, description="用户邮箱")
    password: Optional[str] = Field(None, min_length=6, description="用户密码")
    language: Optional[str] = Field(None, max_length=50, description="语言")
    phone: Optional[str] = Field(None, max_length=50, description="手机号")
    enable: Optional[bool] = Field(None, description="是否启用")
    last_organization_id: Optional[str] = Field(None, max_length=50, description="当前组织ID")
    last_project_id: Optional[str] = Field(None, max_length=50, description="当前项目ID")
    update_user: Optional[str] = Field(None, max_length=50, description="修改人")


class User(UserBase):
    """User response schema"""
    id: str
    enable: bool
    source: str
    last_organization_id: Optional[str] = None
    last_project_id: Optional[str] = None
    create_time: Optional[int] = None
    update_time: Optional[int] = None
    deleted: bool = False

    class Config:
        from_attributes = True

