from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,scoped_session


username = "postgres"
password = 123
ip_address = "localhost"
port = 5432
database = "postgres"

string = f"postgresql://{username}:{password}@{ip_address}:{port}/{database}"

engine = create_engine(string)

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