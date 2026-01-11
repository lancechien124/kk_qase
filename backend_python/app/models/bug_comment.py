"""
Bug Comment Model
"""
from sqlalchemy import Column, String, BigInteger, Text, ForeignKey, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, AuditMixin


class BugComment(Base, TimestampMixin, AuditMixin):
    """Bug Comment model"""
    __tablename__ = "bug_comment"

    id = Column(String(50), primary_key=True, comment="ID")
    bug_id = Column("bug_id", String(50), ForeignKey("bug.id"), nullable=False, comment="缺陷ID")
    reply_user = Column("reply_user", String(50), ForeignKey("user.id"), nullable=True, comment="回复人")
    notifier = Column(String(50), nullable=True, comment="通知人")
    parent_id = Column("parent_id", String(50), ForeignKey("bug_comment.id"), nullable=True, comment="父评论ID")
    content = Column(Text, nullable=False, comment="内容")

    # Relationships
    # bug = relationship("Bug", back_populates="comments")
    # parent = relationship("BugComment", remote_side=[id], backref="replies")

    def __repr__(self):
        return f"<BugComment(id={self.id}, bug_id={self.bug_id})>"

