"""
API Test Models
"""
from sqlalchemy import Column, String, Boolean, BigInteger, Text, ForeignKey, relationship
from sqlalchemy.dialects.mysql import LONGTEXT
from app.core.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin, AuditMixin


class ApiDefinition(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """API Definition model"""
    __tablename__ = "api_definition"

    id = Column(String(50), primary_key=True, comment="ID")
    project_id = Column("project_id", String(50), ForeignKey("project.id"), nullable=False, comment="项目ID")
    name = Column(String(255), nullable=False, comment="接口名称")
    method = Column(String(20), nullable=False, comment="请求方法")
    path = Column(String(500), nullable=False, comment="请求路径")
    description = Column(Text, nullable=True, comment="描述")
    request_body = Column("request_body", LONGTEXT, nullable=True, comment="请求体")
    response_body = Column("response_body", LONGTEXT, nullable=True, comment="响应体")
    status = Column(String(50), nullable=True, comment="状态")
    module_id = Column("module_id", String(50), nullable=True, comment="模块ID")

    # Relationships
    # project = relationship("Project", back_populates="api_definitions")
    # test_cases = relationship("ApiTestCase", back_populates="api_definition", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ApiDefinition(id={self.id}, name={self.name}, method={self.method})>"


class ApiTestCase(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """API Test Case model"""
    __tablename__ = "api_test_case"

    id = Column(String(50), primary_key=True, comment="ID")
    project_id = Column("project_id", String(50), ForeignKey("project.id"), nullable=False, comment="项目ID")
    api_definition_id = Column("api_definition_id", String(50), ForeignKey("api_definition.id"), nullable=False, comment="接口定义ID")
    name = Column(String(255), nullable=False, comment="用例名称")
    request = Column(LONGTEXT, nullable=False, comment="请求内容")
    expected_response = Column("expected_response", LONGTEXT, nullable=True, comment="预期响应")
    status = Column(String(50), nullable=True, comment="状态")
    priority = Column(String(50), nullable=True, comment="优先级")

    # Relationships
    # project = relationship("Project", back_populates="api_test_cases")
    # api_definition = relationship("ApiDefinition", back_populates="test_cases")

    def __repr__(self):
        return f"<ApiTestCase(id={self.id}, name={self.name})>"


class ApiScenario(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """API Scenario model"""
    __tablename__ = "api_scenario"

    id = Column(String(50), primary_key=True, comment="ID")
    project_id = Column("project_id", String(50), ForeignKey("project.id"), nullable=False, comment="项目ID")
    name = Column(String(255), nullable=False, comment="场景名称")
    description = Column(Text, nullable=True, comment="描述")
    status = Column(String(50), nullable=True, comment="状态")
    module_id = Column("module_id", String(50), nullable=True, comment="模块ID")

    # Relationships
    # project = relationship("Project", back_populates="api_scenarios")
    # steps = relationship("ApiScenarioStep", back_populates="scenario", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ApiScenario(id={self.id}, name={self.name})>"

