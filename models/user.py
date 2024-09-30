from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    firstname = Column(String(255))
    lastname = Column(String(255))
    account_created = Column(DateTime(timezone=True), server_default=func.now())
    account_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
