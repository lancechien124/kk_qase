"""
User Role Relation Model
"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, AuditMixin


class UserRoleRelation(Base, TimestampMixin, AuditMixin):
    """User Role Relation model - Links users to roles in organizations/projects"""
    __tablename__ = "user_role_relation"

    id = Column(String(50), primary_key=True, comment="用户组关系ID")
    user_id = Column("user_id", String(50), ForeignKey("user.id"), nullable=False, comment="用户ID")
    role_id = Column("role_id", String(50), ForeignKey("user_role.id"), nullable=False, comment="组ID")
    source_id = Column("source_id", String(50), nullable=False, comment="组织或项目ID")
    organization_id = Column("organization_id", String(50), ForeignKey("organization.id"), nullable=True, comment="记录所在的组织ID")

    # Relationships
    role = relationship("UserRole", foreign_keys=[role_id])

    def __repr__(self):
        return f"<UserRoleRelation(id={self.id}, user_id={self.user_id}, role_id={self.role_id}, source_id={self.source_id})>"

