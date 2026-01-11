"""
Base Model Classes
"""
"""
Base Model Classes
"""
from sqlalchemy import Column, BigInteger, Boolean, String
import time

from app.core.database import Base


class TimestampMixin:
    """Mixin for timestamp fields"""
    create_time = Column(BigInteger, default=lambda: int(time.time() * 1000), comment="创建时间")
    update_time = Column(BigInteger, default=lambda: int(time.time() * 1000), onupdate=lambda: int(time.time() * 1000), comment="更新时间")


class SoftDeleteMixin:
    """Mixin for soft delete"""
    deleted = Column(Boolean, default=False, nullable=False, comment="是否删除")
    delete_time = Column(BigInteger, nullable=True, comment="删除时间")
    delete_user = Column(String(50), nullable=True, comment="删除人")


class AuditMixin:
    """Mixin for audit fields"""
    create_user = Column(String(50), nullable=True, comment="创建人")
    update_user = Column(String(50), nullable=True, comment="修改人")

