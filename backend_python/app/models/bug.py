"""
Bug Model
"""
from sqlalchemy import Column, String, Boolean, BigInteger, Integer, ForeignKey, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin, AuditMixin


class Bug(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Bug model"""
    __tablename__ = "bug"

    id = Column(String(50), primary_key=True, comment="ID")
    num = Column(Integer, nullable=True, comment="业务ID")
    title = Column(String(255), nullable=False, comment="缺陷标题")
    handle_users = Column("handle_users", String(500), nullable=True, comment="处理人集合")
    handle_user = Column("handle_user", String(50), ForeignKey("user.id"), nullable=False, comment="处理人")
    project_id = Column("project_id", String(50), ForeignKey("project.id"), nullable=False, comment="项目ID")
    template_id = Column("template_id", String(50), nullable=False, comment="模板ID")
    platform = Column(String(50), nullable=False, comment="缺陷平台")
    status = Column(String(50), nullable=False, comment="状态")
    tags = Column(String(500), nullable=True, comment="标签")
    platform_bug_id = Column("platform_bug_id", String(100), nullable=True, comment="第三方平台缺陷ID")
    pos = Column(BigInteger, nullable=False, default=0, comment="自定义排序，间隔5000")

    # Relationships
    # project = relationship("Project", back_populates="bugs")
    # comments = relationship("BugComment", back_populates="bug", cascade="all, delete-orphan")
    # attachments = relationship("BugLocalAttachment", back_populates="bug", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Bug(id={self.id}, title={self.title}, project_id={self.project_id})>"

