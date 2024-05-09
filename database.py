from sqlalchemy import create_engine
from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import settings


# SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

SQLALCHEMY_DATABASE_URL = f"postgresql://fastapi_database_owner:bhSd7GBerIO5@ep-twilight-leaf-a5jzjuwc.us-east-2.aws.neon.tech/Bezpieczni-app?sslmode=require"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]