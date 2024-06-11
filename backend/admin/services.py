from database import DbSession
from fastapi import Cookie
from .models import Users
from sqlalchemy.orm import Session
from database import engine
import bcrypt
import string
import random
from jose import jwt, JWTError
from typing import Annotated
from config import settings
from .exception import get_invalid_token_exception, user_exception, get_admin_exception
from ..general.send_email import simple_send
from .models import Roles, RoleEnum

def hash_password(password: str):
    pw = bytes(password, "utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt)


def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def get_by_email(db: DbSession, email: str, include_deleted: bool = False):
    return db.query(Users).filter(Users.email == email).execution_options(include_deleted=include_deleted).one_or_none()


def get_current_user(db: DbSession, token: Annotated[str | None, Cookie(alias="jwt")] = None):

    if token is None:
        raise get_invalid_token_exception()

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        email = payload.get("email")

        if email is None:
            raise get_invalid_token_exception()
        
    
    except JWTError:
        raise get_invalid_token_exception()
    
    user = get_by_email(db, email=email)

    if user is None:
        raise user_exception()
    
    return user


def get_current_admin(db: DbSession, token: Annotated[str | None, Cookie(alias="jwt")] = None):

    if token is None:
        raise get_invalid_token_exception()

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        email = payload.get("email")

        if email is None:
            raise get_invalid_token_exception()
        
    
    except JWTError:
        raise get_invalid_token_exception()
    
    user = get_by_email(db, email=email)

    if user is None:
        raise user_exception()
    
    if user.role_id != 1:
        raise get_admin_exception()
    
    return user

async def create_first_user():
    session = Session(bind=engine)
    if session.query(Users).all() is None:
        random_password = generate_random_password()
        password = hash_password(random_password)
        user_in = Users()
        user_in.name = "Admin"
        user_in.surname = "Admin"
        user_in.email = "testbezpieczni@gmail.com"
        user_in.role_id = 1
        user_in.password = password

        session.add(user_in)
        session.commit()
        session.refresh(user_in)
        session.close()

        await simple_send([user_in.email], random_password)
    else:
        session.commit()
        session.close()

def init_roles():
    session = Session(bind=engine)
    if not session.query(Roles).filter_by(name=RoleEnum.admin).first():
        admin_role = Roles(name=RoleEnum.admin)
        admin_role.id = 1
        session.add(admin_role)
    if not session.query(Roles).filter_by(name=RoleEnum.moderator).first():
        moderator_role = Roles(name=RoleEnum.moderator)
        moderator_role.id = 2
        session.add(moderator_role)
    session.commit()
    session.close()