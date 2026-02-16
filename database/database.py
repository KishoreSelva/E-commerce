from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,scoped_session
from config import settings

username = settings.DB_USERNAME
password = settings.DB_PASSWORD
ip_address = settings.DB_HOST
port = settings.DB_PORT
database = settings.DB_NAME

db_string = f"postgresql://{username}:{password}@{ip_address}:{port}/{database}"

engine = create_engine(db_string, pool_pre_ping=True)

Base = declarative_base() 

session = scoped_session(sessionmaker(bind=engine))

def getdb():
    Session = sessionmaker(bind=engine)
    session = Session()
    session.autoflush = False
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()