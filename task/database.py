from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHAMY_DATABASE_URL = 'sqlite:///./assetInfo.db'
connect_args = {"check_same_thread": False}

engine = create_engine(SQLALCHAMY_DATABASE_URL, connect_args = connect_args)
Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

