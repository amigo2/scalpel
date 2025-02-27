# models.py
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, ForeignKey, Integer, Enum, JSON
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs

Base = declarative_base()

class MLTagEnum(str, enum.Enum):
    TRAIN = "TRAIN"
    TEST = "TEST"
    LIVE = "LIVE"

class Location(Base):
    __tablename__ = "location"

    id = Column(String, primary_key=True, index=True)
    address = Column(String, nullable=False)
    country = Column(String, nullable=False)
    town = Column(String, nullable=False)

    # Relationship to images (one location can have many images).
    images = relationship("Image", back_populates="location")

class User(Base):
    __tablename__ = "user"

    id = Column(String, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(String, nullable=False)

    # Relationship to images (one user can own many images).
    images = relationship("Image", back_populates="user")

class Image(Base):
    __tablename__ = "image"

    image_key = Column(String, primary_key=True, index=True)
    client_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

    hardware_id = Column(String, nullable=True)
    ml_tag = Column(Enum(MLTagEnum), nullable=True)
    
    location_id = Column(String, ForeignKey("location.id"), nullable=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=True)

    # Relationships
    location = relationship("Location", back_populates="images")
    user = relationship("User", back_populates="images")
    annotations = relationship("Annotation", back_populates="image",
                               cascade="all, delete-orphan")

class Annotation(Base):
    __tablename__ = "annotation"

    # Composite primary key
    image_key = Column(String, ForeignKey("image.image_key"), primary_key=True)
    index = Column(Integer, primary_key=True)

    instrument = Column(String, nullable=False)
    # For storing polygon data as JSON. In Postgres, you could also use JSONB type.
    polygon = Column(JSON, nullable=True)

    # Relationship back to Image
    image = relationship("Image", back_populates="annotations")
