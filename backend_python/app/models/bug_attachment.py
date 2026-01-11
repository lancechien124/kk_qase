"""
Bug Attachment Model
"""
from sqlalchemy import Column, String, BigInteger, ForeignKey, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, AuditMixin


class BugLocalAttachment(Base, TimestampMixin, AuditMixin):
    """Bug Local Attachment model"""
    __tablename__ = "bug_local_attachment"

    id = Column(String(255), primary_key=True, comment="ID")
    bug_id = Column("bug_id", String(50), ForeignKey("bug.id"), nullable=False, comment="缺陷ID")
    file_id = Column("file_id", String(50), nullable=False, comment="文件ID")
    file_name = Column("file_name", String(255), nullable=False, comment="文件名称")
    size = Column(BigInteger, nullable=False, default=0, comment="文件大小")
    source = Column(String(255), nullable=False, comment="文件来源")

    # Relationships
    # bug = relationship("Bug", back_populates="attachments")

    def __repr__(self):
        return f"<BugLocalAttachment(id={self.id}, bug_id={self.bug_id}, file_name={self.file_name})>"

