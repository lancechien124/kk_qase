"""
Functional Case Model
"""
from sqlalchemy import Column, String, Boolean, BigInteger, ForeignKey, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin, AuditMixin


class FunctionalCase(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Functional Case model"""
    __tablename__ = "functional_case"

    id = Column(String(50), primary_key=True, comment="ID")
    num = Column(BigInteger, nullable=True, comment="业务ID")
    module_id = Column("module_id", String(50), nullable=False, comment="模块ID")
    project_id = Column("project_id", String(50), ForeignKey("project.id"), nullable=False, comment="项目ID")
    template_id = Column("template_id", String(50), nullable=False, comment="模板ID")
    name = Column(String(255), nullable=False, comment="名称")
    review_status = Column("review_status", String(64), nullable=False, comment="评审结果：未评审/评审中/通过/不通过/重新提审")
    tags = Column(String(500), nullable=True, comment="标签（JSON）")
    case_edit_type = Column("case_edit_type", String(50), nullable=False, comment="编辑模式：步骤模式/文本模式")
    pos = Column(BigInteger, nullable=False, default=0, comment="自定义排序，间隔5000")
    version_id = Column("version_id", String(50), nullable=False, comment="版本ID")
    ref_id = Column("ref_id", String(50), nullable=False, comment="指向初始版本ID")
    last_execute_result = Column("last_execute_result", String(64), nullable=False, comment="最近的执行结果：未执行/通过/失败/阻塞/跳过")
    ai_create = Column("ai_create", Boolean, default=False, nullable=False, comment="是否是ai自动生成的用例：0-否，1-是")
    public_case = Column("public_case", Boolean, default=False, nullable=False, comment="是否是公共用例：0-否，1-是")
    latest = Column(Boolean, default=True, nullable=False, comment="是否为最新版本：0-否，1-是")

    # Relationships
    # project = relationship("Project", back_populates="functional_cases")
    # blob = relationship("FunctionalCaseBlob", uselist=False, back_populates="functional_case", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FunctionalCase(id={self.id}, name={self.name}, project_id={self.project_id})>"


class FunctionalCaseBlob(Base):
    """Functional Case Blob model for storing large text data"""
    __tablename__ = "functional_case_blob"

    id = Column(String(50), ForeignKey("functional_case.id"), primary_key=True, comment="功能用例ID")
    steps = Column("steps", String(65535), nullable=True, comment="用例步骤（JSON)，step_model 为 Step 时启用")
    text_description = Column("text_description", String(65535), nullable=True, comment="步骤描述，step_model 为 Text 时启用")
    expected_result = Column("expected_result", String(65535), nullable=True, comment="预期结果，step_model 为 Text 时启用")
    prerequisite = Column(String(65535), nullable=True, comment="前置条件")
    description = Column(String(65535), nullable=True, comment="备注")

    # Relationships
    # functional_case = relationship("FunctionalCase", back_populates="blob")

    def __repr__(self):
        return f"<FunctionalCaseBlob(id={self.id})>"

