"""
User Model
"""
from sqlalchemy import Column, String, Boolean
from app.core.database import Base
from app.models.base import TimestampMixin, SoftDeleteMixin, AuditMixin


class User(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """User model"""
    __tablename__ = "user"

    id = Column(String(50), primary_key=True, comment="用户ID")
    name = Column(String(255), nullable=False, comment="用户名")
    email = Column(String(64), nullable=False, unique=True, comment="用户邮箱")
    password = Column(String(255), nullable=True, comment="用户密码")
    enable = Column(Boolean, default=True, nullable=True, comment="是否启用")
    language = Column(String(50), nullable=True, comment="语言")
    last_organization_id = Column("last_organization_id", String(50), nullable=True, comment="当前组织ID")
    phone = Column(String(50), nullable=True, comment="手机号")
    source = Column(String(50), nullable=False, default="LOCAL", comment="来源：LOCAL OIDC CAS OAUTH2")
    last_project_id = Column("last_project_id", String(50), nullable=True, comment="当前项目ID")
    cft_token = Column("cft_token", String(255), nullable=False, comment="身份令牌")

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"

