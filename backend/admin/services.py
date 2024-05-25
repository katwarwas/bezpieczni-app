from database import DbSession
from fastapi import Cookie
from .models import Users
import bcrypt
import string
import random
from jose import jwt, JWTError
from typing import Annotated
from config import settings
from .exception import get_invalid_token_exception, user_exception, get_admin_exception

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