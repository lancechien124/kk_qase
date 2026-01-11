"""
Test Plan Models
"""
from sqlalchemy import Column, String, Boolean, BigInteger, Text, ForeignKey, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin, AuditMixin


class TestPlan(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Test Plan model"""
    __tablename__ = "test_plan"

    id = Column(String(50), primary_key=True, comment="ID")
    num = Column(BigInteger, nullable=True, comment="num")
    project_id = Column("project_id", String(50), ForeignKey("project.id"), nullable=False, comment="测试计划所属项目")
    group_id = Column("group_id", String(50), nullable=False, default="none", comment="测试计划组ID;默认为none.只关联type为group的测试计划")
    module_id = Column("module_id", String(50), nullable=False, comment="测试计划模块ID")
    name = Column(String(255), nullable=False, comment="测试计划名称")
    status = Column(String(20), nullable=False, comment="测试计划状态;未开始，进行中，已完成，已归档")
    type = Column(String(30), nullable=False, comment="数据类型;测试计划组（group）/测试计划（testPlan）")
    tags = Column(String(500), nullable=True, comment="标签")
    planned_start_time = Column("planned_start_time", BigInteger, nullable=True, comment="计划开始时间")
    planned_end_time = Column("planned_end_time", BigInteger, nullable=True, comment="计划结束时间")
    actual_start_time = Column("actual_start_time", BigInteger, nullable=True, comment="实际开始时间")
    actual_end_time = Column("actual_end_time", BigInteger, nullable=True, comment="实际结束时间")
    description = Column(Text, nullable=True, comment="描述")
    pos = Column(BigInteger, nullable=False, default=0, comment="自定义排序")

    # Relationships
    # project = relationship("Project", back_populates="test_plans")
    # reports = relationship("TestPlanReport", back_populates="test_plan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestPlan(id={self.id}, name={self.name}, project_id={self.project_id})>"


class TestPlanReport(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Test Plan Report model"""
    __tablename__ = "test_plan_report"

    id = Column(String(50), primary_key=True, comment="ID")
    test_plan_id = Column("test_plan_id", String(50), ForeignKey("test_plan.id"), nullable=False, comment="测试计划ID")
    name = Column(String(255), nullable=False, comment="报告名称")
    start_time = Column("start_time", BigInteger, nullable=True, comment="开始时间;计划开始执行的时间")
    end_time = Column("end_time", BigInteger, nullable=True, comment="结束时间;计划结束执行的时间")
    exec_status = Column("exec_status", String(50), nullable=False, comment="执行状态")
    result_status = Column("result_status", String(50), nullable=False, comment="结果状态")
    pass_rate = Column("pass_rate", String(20), nullable=True, comment="通过率")
    trigger_mode = Column("trigger_mode", String(50), nullable=False, comment="触发类型")
    pass_threshold = Column("pass_threshold", String(20), nullable=False, comment="通过阈值")
    project_id = Column("project_id", String(50), ForeignKey("project.id"), nullable=False, comment="项目id")
    integrated = Column(Boolean, default=False, nullable=False, comment="是否是集成报告")
    execute_rate = Column("execute_rate", String(20), nullable=True, comment="执行率")
    parent_id = Column("parent_id", String(50), ForeignKey("test_plan_report.id"), nullable=True, comment="独立报告的父级ID")
    test_plan_name = Column("test_plan_name", String(255), nullable=False, comment="测试计划名称")
    default_layout = Column("default_layout", Boolean, default=False, nullable=False, comment="是否默认布局")

    # Relationships
    # test_plan = relationship("TestPlan", back_populates="reports")
    # project = relationship("Project", back_populates="test_plan_reports")
    # parent = relationship("TestPlanReport", remote_side=[id], backref="children")

    def __repr__(self):
        return f"<TestPlanReport(id={self.id}, test_plan_id={self.test_plan_id}, name={self.name})>"

