"""
Project Model
"""
from sqlalchemy import Column, String, Boolean, BigInteger, ForeignKey, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin, AuditMixin


class Project(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Project model"""
    __tablename__ = "project"

    id = Column(String(50), primary_key=True, comment="项目ID")
    num = Column(BigInteger, nullable=True, comment="项目编号")
    organization_id = Column("organization_id", String(50), ForeignKey("organization.id"), nullable=False, comment="组织ID")
    name = Column(String(255), nullable=False, comment="项目名称")
    description = Column(String(500), nullable=True, comment="项目描述")
    enable = Column(Boolean, default=True, nullable=True, comment="是否启用")
    module_setting = Column("module_setting", String(500), nullable=True, comment="模块设置")
    all_resource_pool = Column("all_resource_pool", Boolean, default=False, nullable=False, comment="全部资源池")

    # Relationships
    # organization = relationship("Organization", back_populates="projects")
    # members = relationship("UserRoleRelation", foreign_keys="UserRoleRelation.source_id", primaryjoin="Project.id == UserRoleRelation.source_id")

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, organization_id={self.organization_id})>"

