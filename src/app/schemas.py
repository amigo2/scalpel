from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

# Reuse the MLTagEnum defined in models
class MLTagEnum(str, Enum):
    TRAIN = "TRAIN"
    TEST = "TEST"
    LIVE = "LIVE"

class Polygon(BaseModel):
    points: List[List[float]]

class AnnotationCreate(BaseModel):
    index: int
    instrument: str
    polygon: Polygon

class AnnotationRead(AnnotationCreate):
    image_key: str

class AnnotationUpdateRequest(BaseModel):
    image_key: str
    annotation_index: int
    instrument: str
    polygon: Polygon

class ImageFilter(BaseModel):
    client_id: Optional[str] = None
    hardware_id: Optional[str] = None
    ml_tag: Optional[MLTagEnum] = None
    location_id: Optional[str] = None
    user_id: Optional[str] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None

class ImageBase(BaseModel):
    client_id: str
    created_at: datetime
    hardware_id: Optional[str]
    ml_tag: Optional[MLTagEnum]
    location_id: Optional[str]
    user_id: Optional[str]

class ImageCreate(ImageBase):
    # image_key is provided by file upload, not by client
    annotations: Optional[List[AnnotationCreate]] = None

class ImageRead(ImageBase):
    image_key: str
    annotations: List[AnnotationRead] = Field(default_factory=list)

    model_config = {
        "from_attributes": True
    }
