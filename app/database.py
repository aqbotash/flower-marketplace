from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = 'sqlite:///./sql_app.db'
#postresql://user:password@postgresserver.db

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args = {'check_same_thread' : False}) # connect agrs only for sqlite
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # class for creating a session or connecting to db
Base = declarative_base() # class which connect python classes and tables in db, ORM classes