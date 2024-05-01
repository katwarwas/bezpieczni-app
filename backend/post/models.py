from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP, text, DateTime
from sqlalchemy.orm import relationship
from database import Base
from ..general.soft_delete import SoftDeleteMixin


class Posts(Base, SoftDeleteMixin):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("Users", foreign_keys=[user_id])