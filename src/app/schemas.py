# schemas.py
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

class MLTagEnum(str, Enum):
    TRAIN = "TRAIN"
    TEST = "TEST"
    LIVE = "LIVE"

# Annotation Schemas
class AnnotationBase(BaseModel):
    index: int
    instrument: str
    polygon: Optional[Dict] = None

class AnnotationCreate(AnnotationBase):
    pass

class AnnotationRead(AnnotationBase):
    class Config:
        orm_mode = True

# Image Schemas
class ImageBase(BaseModel):
    image_key: str
    client_id: str
    created_at: datetime
    hardware_id: Optional[str] = None
    ml_tag: Optional[MLTagEnum] = None
    location_id: Optional[str] = None
    user_id: Optional[str] = None

class ImageCreate(ImageBase):
    annotations: Optional[List[AnnotationCreate]] = []

class ImageRead(BaseModel):
    image_key: str
    client_id: str
    created_at: datetime
    hardware_id: str
    ml_tag: Optional[str]
    location_id: Optional[str]
    user_id: Optional[str]
    annotations: List[AnnotationRead] = []  # ✅ Ensure a default value to prevent issues

    model_config = ConfigDict(from_attributes=True)  # ✅ New Pydantic v2 synta


# Filter Schemas (optional if you want to handle queries)
class ImageFilter(BaseModel):
    user_ids: Optional[List[str]] = None
    location_ids: Optional[List[str]] = None
    instrument_ids: Optional[List[str]] = None
