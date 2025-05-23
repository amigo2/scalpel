from sqlalchemy import Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base

from pydantic import BaseModel
from typing import Optional, Dict, Any

Base = declarative_base()

class VendorTrayManufacturer(Base):
    __tablename__ = 'vendor_tray_manufacturers'

    # Primary key
    type = Column(String, primary_key=True, index=True)

    # Scalar attributes
    manufacturer = Column(String, nullable=True)
    name = Column(String, nullable=True)
    base_registration_path = Column(String, nullable=True)
    empty_tray_path = Column(String, nullable=True)

    # JSONB attributes
    aliases = Column(JSON, nullable=True)
    levels = Column(JSON, nullable=True)
    modifications = Column(JSON, nullable=True)
    additional_instruments = Column(JSON, nullable=True)
    notifications = Column(JSON, nullable=True)
    tray_notifications = Column(JSON, nullable=True)
    subgroups = Column(JSON, nullable=True)

# Pydantic schemas for FastAPI
class VendorTrayManufacturerBase(BaseModel):
    type: str
    manufacturer: Optional[str] = None
    name: Optional[str] = None
    base_registration_path: Optional[str] = None
    empty_tray_path: Optional[str] = None
    aliases: Optional[Dict[str, Any]] = None
    levels: Optional[Dict[str, Any]] = None
    modifications: Optional[Dict[str, Any]] = None
    additional_instruments: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, Any]] = None
    tray_notifications: Optional[Dict[str, Any]] = None
    subgroups: Optional[Dict[str, Any]] = None

class VendorTrayManufacturerCreate(VendorTrayManufacturerBase):
    pass

class VendorTrayManufacturerRead(VendorTrayManufacturerBase):
    class Config:
        orm_mode = True
