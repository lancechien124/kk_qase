"""
API Report Model
"""
from sqlalchemy import Column, String, Boolean, BigInteger, ForeignKey, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin, AuditMixin


class ApiReport(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """API Report model"""
    __tablename__ = "api_report"

    id = Column(String(50), primary_key=True, comment="接口报告pk")
    name = Column(String(300), nullable=False, comment="接口报告名称")
    test_plan_case_id = Column("test_plan_case_id", String(50), nullable=False, comment="测试计划关联用例表ID")
    start_time = Column("start_time", BigInteger, nullable=False, comment="开始时间/同创建时间一致")
    end_time = Column("end_time", BigInteger, nullable=True, comment="结束时间/报告执行完成")
    request_duration = Column("request_duration", BigInteger, nullable=False, default=0, comment="请求总耗时")
    status = Column(String(20), nullable=False, comment="报告状态/SUCCESS/ERROR")
    trigger_mode = Column("trigger_mode", String(20), nullable=False, comment="触发方式")
    run_mode = Column("run_mode", String(20), nullable=False, comment="执行模式")
    pool_id = Column("pool_id", String(50), nullable=False, comment="资源池")
    integrated = Column(Boolean, default=False, nullable=False, comment="是否是集成报告")
    project_id = Column("project_id", String(50), ForeignKey("project.id"), nullable=False, comment="项目fk")
    environment_id = Column("environment_id", String(50), nullable=True, comment="环境")
    error_count = Column("error_count", BigInteger, nullable=False, default=0, comment="失败数")
    fake_error_count = Column("fake_error_count", BigInteger, nullable=False, default=0, comment="误报数")
    pending_count = Column("pending_count", BigInteger, nullable=False, default=0, comment="未执行数")
    success_count = Column("success_count", BigInteger, nullable=False, default=0, comment="成功数")
    assertion_count = Column("assertion_count", BigInteger, nullable=False, default=0, comment="总断言数")
    assertion_success_count = Column("assertion_success_count", BigInteger, nullable=False, default=0, comment="成功断言数")
    request_error_rate = Column("request_error_rate", String(20), nullable=False, default="0", comment="请求失败率")
    request_pending_rate = Column("request_pending_rate", String(20), nullable=False, default="0", comment="请求未执行率")
    request_fake_error_rate = Column("request_fake_error_rate", String(20), nullable=False, default="0", comment="请求误报率")
    request_pass_rate = Column("request_pass_rate", String(20), nullable=False, default="0", comment="请求通过率")
    assertion_pass_rate = Column("assertion_pass_rate", String(20), nullable=False, default="0", comment="断言通过率")
    script_identifier = Column("script_identifier", String(100), nullable=True, comment="脚本标识")
    exec_status = Column("exec_status", String(20), nullable=False, comment="执行状态")
    plan = Column(Boolean, default=False, nullable=False, comment="是否是测试计划整体执行")

    # Relationships
    # project = relationship("Project", back_populates="api_reports")

    def __repr__(self):
        return f"<ApiReport(id={self.id}, name={self.name}, project_id={self.project_id})>"

