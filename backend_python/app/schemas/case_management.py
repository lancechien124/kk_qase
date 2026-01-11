"""
Case Management Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class FunctionalCaseBase(BaseModel):
    """Base Functional Case schema"""
    name: str = Field(..., min_length=1, max_length=255, description="名称")
    module_id: str = Field(..., min_length=1, max_length=50, description="模块ID")
    template_id: str = Field(..., min_length=1, max_length=50, description="模板ID")
    case_edit_type: str = Field(..., min_length=1, max_length=50, description="编辑模式：步骤模式/文本模式")
    review_status: Optional[str] = Field("UN_REVIEWED", max_length=64, description="评审结果：未评审/评审中/通过/不通过/重新提审")
    tags: Optional[List[str]] = Field(None, description="标签")
    last_execute_result: Optional[str] = Field("UN_EXECUTED", max_length=64, description="最近的执行结果：未执行/通过/失败/阻塞/跳过")


class FunctionalCaseCreate(FunctionalCaseBase):
    """Functional Case creation schema"""
    project_id: str = Field(..., min_length=1, max_length=50, description="项目ID")
    version_id: str = Field(..., min_length=1, max_length=50, description="版本ID")
    ref_id: str = Field(..., min_length=1, max_length=50, description="指向初始版本ID")
    create_user: Optional[str] = Field(None, max_length=50, description="创建人")
    steps: Optional[List[Dict[str, Any]]] = Field(None, description="用例步骤（JSON），step_model 为 Step 时启用")
    text_description: Optional[str] = Field(None, description="步骤描述，step_model 为 Text 时启用")
    expected_result: Optional[str] = Field(None, description="预期结果，step_model 为 Text 时启用")
    prerequisite: Optional[str] = Field(None, description="前置条件")
    description: Optional[str] = Field(None, description="备注")


class FunctionalCaseUpdate(BaseModel):
    """Functional Case update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="名称")
    module_id: Optional[str] = Field(None, min_length=1, max_length=50, description="模块ID")
    review_status: Optional[str] = Field(None, max_length=64, description="评审结果")
    tags: Optional[List[str]] = Field(None, description="标签")
    last_execute_result: Optional[str] = Field(None, max_length=64, description="最近的执行结果")
    steps: Optional[List[Dict[str, Any]]] = Field(None, description="用例步骤")
    text_description: Optional[str] = Field(None, description="步骤描述")
    expected_result: Optional[str] = Field(None, description="预期结果")
    prerequisite: Optional[str] = Field(None, description="前置条件")
    description: Optional[str] = Field(None, description="备注")
    update_user: Optional[str] = Field(None, max_length=50, description="修改人")


class FunctionalCase(FunctionalCaseBase):
    """Functional Case response schema"""
    id: str
    num: Optional[int] = None
    project_id: str
    version_id: str
    ref_id: str
    pos: int = 0
    ai_create: bool = False
    public_case: bool = False
    latest: bool = True
    create_time: Optional[int] = None
    update_time: Optional[int] = None
    deleted: bool = False

    class Config:
        from_attributes = True

