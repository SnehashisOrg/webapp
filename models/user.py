from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
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
    is_verified = Column(Boolean, default=False, nullable=False)

    images = relationship("Image", back_populates="user")
    verification = relationship("Verification", back_populates="user", uselist=False)


class Image(Base):
    __tablename__ = "images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    file_name = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="images")


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    email = Column(String(255), ForeignKey('users.email'), unique=True, nullable=False)
    verification_link = Column(String(255), nullable=False)
    token = Column(String(36), unique=True, nullable=False)
    expiration_time = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    link_verified = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="verification")