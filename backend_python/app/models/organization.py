"""
Organization Model
"""
from sqlalchemy import Column, String, Boolean, BigInteger, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin, AuditMixin


class Organization(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Organization model"""
    __tablename__ = "organization"

    id = Column(String(50), primary_key=True, comment="组织ID")
    num = Column(BigInteger, nullable=True, comment="组织编号")
    name = Column(String(255), nullable=False, comment="组织名称")
    description = Column(String(500), nullable=True, comment="描述")
    enable = Column(Boolean, default=True, nullable=True, comment="是否启用")

    # Relationships
    # projects = relationship("Project", back_populates="organization")
    # members = relationship("UserRoleRelation", foreign_keys="UserRoleRelation.source_id", primaryjoin="Organization.id == UserRoleRelation.source_id")

    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name})>"

