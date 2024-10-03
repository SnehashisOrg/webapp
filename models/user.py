from sqlalchemy import Column, Integer, String, DateTime, func
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

# User schema to save the object in database
class User(Base):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    account_created = Column(DateTime(timezone=True), server_default=func.now())
    account_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
