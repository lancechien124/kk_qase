"""
Test Plan Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class TestPlanBase(BaseModel):
    """Base Test Plan schema"""
    name: str = Field(..., min_length=1, max_length=255, description="测试计划名称")
    module_id: str = Field(..., min_length=1, max_length=50, description="测试计划模块ID")
    status: str = Field(..., min_length=1, max_length=20, description="测试计划状态;未开始，进行中，已完成，已归档")
    type: str = Field(..., min_length=1, max_length=30, description="数据类型;测试计划组（group）/测试计划（testPlan）")
    description: Optional[str] = Field(None, description="描述")
    tags: Optional[List[str]] = Field(None, description="标签")


class TestPlanCreate(TestPlanBase):
    """Test Plan creation schema"""
    project_id: str = Field(..., min_length=1, max_length=50, description="测试计划所属项目")
    group_id: str = Field("none", min_length=1, max_length=50, description="测试计划组ID;默认为none")
    planned_start_time: Optional[int] = Field(None, description="计划开始时间")
    planned_end_time: Optional[int] = Field(None, description="计划结束时间")
    create_user: Optional[str] = Field(None, max_length=50, description="创建人")


class TestPlanUpdate(BaseModel):
    """Test Plan update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="测试计划名称")
    module_id: Optional[str] = Field(None, min_length=1, max_length=50, description="测试计划模块ID")
    status: Optional[str] = Field(None, min_length=1, max_length=20, description="测试计划状态")
    type: Optional[str] = Field(None, min_length=1, max_length=30, description="数据类型")
    description: Optional[str] = Field(None, description="描述")
    tags: Optional[List[str]] = Field(None, description="标签")
    planned_start_time: Optional[int] = Field(None, description="计划开始时间")
    planned_end_time: Optional[int] = Field(None, description="计划结束时间")
    actual_start_time: Optional[int] = Field(None, description="实际开始时间")
    actual_end_time: Optional[int] = Field(None, description="实际结束时间")
    update_user: Optional[str] = Field(None, max_length=50, description="修改人")


class TestPlan(TestPlanBase):
    """Test Plan response schema"""
    id: str
    num: Optional[int] = None
    project_id: str
    group_id: str
    pos: int = 0
    planned_start_time: Optional[int] = None
    planned_end_time: Optional[int] = None
    actual_start_time: Optional[int] = None
    actual_end_time: Optional[int] = None
    create_time: Optional[int] = None
    update_time: Optional[int] = None
    deleted: bool = False

    class Config:
        from_attributes = True


class TestPlanReport(BaseModel):
    """Test Plan Report schema"""
    id: str
    test_plan_id: str
    name: str
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    exec_status: str
    result_status: str
    pass_rate: Optional[str] = None
    trigger_mode: str
    pass_threshold: str
    project_id: str
    integrated: bool = False
    execute_rate: Optional[str] = None
    parent_id: Optional[str] = None
    test_plan_name: str
    default_layout: bool = False
    create_time: Optional[int] = None
    deleted: bool = False

    class Config:
        from_attributes = True

