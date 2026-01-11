"""
User Role Model
"""
from sqlalchemy import Column, String, Boolean
from app.core.database import Base
from app.models.base import TimestampMixin, AuditMixin


class UserRole(Base, TimestampMixin, AuditMixin):
    """User Role model"""
    __tablename__ = "user_role"

    id = Column(String(50), primary_key=True, comment="组ID")
    name = Column(String(255), nullable=False, comment="组名称")
    description = Column(String(500), nullable=True, comment="描述")
    internal = Column(Boolean, default=False, nullable=False, comment="是否是内置用户组")
    type = Column(String(20), nullable=False, comment="所属类型 SYSTEM ORGANIZATION PROJECT")
    scope_id = Column("scope_id", String(50), nullable=False, comment="应用范围")

    def __repr__(self):
        return f"<UserRole(id={self.id}, name={self.name}, type={self.type})>"

