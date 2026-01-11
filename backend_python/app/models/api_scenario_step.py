"""
API Scenario Step Model
"""
from sqlalchemy import Column, String, Boolean, BigInteger, Text, ForeignKey, relationship
from app.core.database import Base


class ApiScenarioStep(Base):
    """API Scenario Step model"""
    __tablename__ = "api_scenario_step"

    id = Column(String(50), primary_key=True, comment="步骤id")
    scenario_id = Column("scenario_id", String(50), ForeignKey("api_scenario.id"), nullable=False, comment="场景id")
    name = Column(String(255), nullable=True, comment="步骤名称")
    sort = Column(BigInteger, nullable=False, default=0, comment="序号")
    enable = Column(Boolean, default=True, nullable=True, comment="启用/禁用")
    resource_id = Column("resource_id", String(50), nullable=True, comment="资源id")
    resource_num = Column("resource_num", String(50), nullable=True, comment="资源编号")
    step_type = Column("step_type", String(50), nullable=True, comment="步骤类型/API/CASE等")
    project_id = Column("project_id", String(50), ForeignKey("project.id"), nullable=True, comment="项目fk")
    parent_id = Column("parent_id", String(50), ForeignKey("api_scenario_step.id"), nullable=True, comment="父级fk")
    version_id = Column("version_id", String(50), nullable=True, comment="版本号")
    ref_type = Column("ref_type", String(50), nullable=True, comment="引用/复制/自定义")
    config = Column(Text, nullable=True, comment="循环等组件基础数据")
    origin_project_id = Column("origin_project_id", String(50), nullable=True, comment="记录跨项目复制的步骤的原项目ID")

    # Relationships
    # scenario = relationship("ApiScenario", back_populates="steps")
    # parent = relationship("ApiScenarioStep", remote_side=[id], backref="children")

    def __repr__(self):
        return f"<ApiScenarioStep(id={self.id}, scenario_id={self.scenario_id}, step_type={self.step_type})>"

