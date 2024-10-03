from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import logging

# Parse a .env file and then load all the variables found as environment variables.
load_dotenv()

# setting up the logger 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database credentials
USER = os.getenv("MYSQL_USER")
PASSWORD = os.getenv("MYSQL_PASSWORD")
HOST = os.getenv("MYSQL_HOST")
PORT = os.getenv("MYSQL_PORT")
DATABASE = os.getenv("MYSQL_DATABASE")

DB_CONNECTION_STRING = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}"


def get_engine():
    try:
        engine = create_engine(DB_CONNECTION_STRING)
        return engine
    except Exception as e:
        logger.error(f"SQLAlchemy engine error... {e}")
    

'''
Function: get_database_connection()
Desc.: Checks the database connection
Params: None
Return: bool
'''
def get_database_connection() -> bool:
    engine = get_engine()
    try:
        with engine.connect() as conn:
            logger.info("Connection successful!")
            return True
    except Exception as e:
        logger.info(f"Error in database connection!  {e}")
        return False

"""
Function: get_database_session()
Desc.: Returns the database session
Params: None
Return: .Session
"""  
def get_database_session():
    try:
        engine = get_engine()
        SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
        db_session = SessionLocal()
        return db_session
    except Exception as e:
        logger.error(f"Exception occurred... {e}")
    finally:
        if db_session: db_session.close()
