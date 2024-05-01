from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType
from enum import Enum
from database import Base
import bcrypt
from config import settings
from jose import jwt
from datetime import datetime, timedelta
from ..general.soft_delete import SoftDeleteMixin

class RoleEnum(Enum):
    admin = "Admin"
    moderator = "Moderator"

class Users(Base, SoftDeleteMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(LargeBinary, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    role = relationship("Roles", foreign_keys=[role_id])

    def check_password(self, password: str):
        return bcrypt.checkpw(password.encode(), self.password)
    
    @property
    def token(self):
        exp = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        data = {
            "exp": exp,
            "email": self.email,
        }
        return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)
    
    @property
    def refresh_token(self):
        exp = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_hours)
        data = {
            "exp": exp,
            "email": self.email,
        }
        return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)
    

class Roles(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(ChoiceType(RoleEnum), nullable=False)