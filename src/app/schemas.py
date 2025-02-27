# schemas.py
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
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

class ImageRead(ImageBase):
    annotations: List[AnnotationRead] = []

    class Config:
        orm_mode = True

# Filter Schemas (optional if you want to handle queries)
class ImageFilter(BaseModel):
    user_ids: Optional[List[str]] = None
    location_ids: Optional[List[str]] = None
    instrument_ids: Optional[List[str]] = None
