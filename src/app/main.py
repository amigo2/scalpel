# main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import selectinload
from PIL import Image as PILImage
from sqlalchemy import select
from io import BytesIO
import os

from .database import engine, get_session
from .models import Base, Image, Annotation, Location, User
from .schemas import (
    ImageCreate, ImageRead, AnnotationCreate, AnnotationRead, ImageFilter
)

app = FastAPI(title="Scalpel Challenge, FastAPI & Async SQLAlchemy")

@app.on_event("startup")
async def startup_event():
    """
    Create tables at startup (not recommended for production,
    but convenient for a coding challenge).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 1. Create an image (with optional annotations)
@app.post("/images", response_model=ImageRead)
async def create_image(
    image_in: ImageCreate,
    db: AsyncSession = Depends(get_session)
):
    # Check if image already exists
    existing_image = await db.get(Image, image_in.image_key)
    if existing_image:
        raise HTTPException(status_code=400, detail="Image key already exists.")

    # If a location_id is provided, ensure the location exists or create it
    if image_in.location_id:
        location = await db.get(Location, image_in.location_id)
        if not location:
            new_location = Location(
                id=image_in.location_id,
                address="Default Address",
                country="Default Country",
                town="Default Town"
            )
            db.add(new_location)
            await db.flush()
    
    # Check if user exists, if user_id is provided
    if image_in.user_id:
        user = await db.get(User, image_in.user_id)
        if not user:
            # Option 1: Create a default user (if appropriate)
            new_user = User(
                id=image_in.user_id,
                first_name="Default",
                last_name="User",
                role="default_role"
            )
            db.add(new_user)
            await db.flush()
            
            # Option 2: Raise an error to indicate the user must exist
            raise HTTPException(status_code=400, detail="User does not exist. Please create the user first.")

    new_image = Image(
        image_key=image_in.image_key,
        client_id=image_in.client_id,
        created_at=image_in.created_at.replace(tzinfo=None),
        hardware_id=image_in.hardware_id,
        ml_tag=image_in.ml_tag.value if image_in.ml_tag else None,
        location_id=image_in.location_id,
        user_id=image_in.user_id,
    )

    if image_in.annotations:
        for ann in image_in.annotations:
            annotation = Annotation(
                image_key=image_in.image_key,
                index=ann.index,
                instrument=ann.instrument,
                polygon=ann.polygon
            )
            new_image.annotations.append(annotation)

    db.add(new_image)
    await db.commit()
    # the refresh is giving issues, needs more work.
    # await db.refresh(new_image, options=[selectinload(Image.annotations)])
    return new_image




# 2. Create a new annotation for a given image

#   {
#     "index": 13,
#     "instrument": "inster1",
#     "polygon": {
#       "points": [
#         [
#           0,
#           0
#         ],
#         [
#           1,
#           1
#         ]
#       ]
#     }
#   }
@app.post("/images/{image_key}/annotations", response_model=AnnotationRead)
async def create_annotation(
    image_key: str,
    annotation_in: AnnotationCreate,
    db: AsyncSession = Depends(get_session)
):
    image = await db.get(Image, image_key)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found.")

    # Check if annotation with the same index exists
    existing_annotation = await db.get(Annotation, (image_key, annotation_in.index))
    if existing_annotation:
        raise HTTPException(status_code=400, detail="Annotation index already exists for this image.")

    new_annotation = Annotation(
        image_key=image_key,
        index=annotation_in.index,
        instrument=annotation_in.instrument,
        polygon=annotation_in.polygon
    )
    db.add(new_annotation)
    await db.commit()
    await db.refresh(new_annotation)
    return new_annotation


# 3. Update an existing annotation
@app.put("/images/{image_key}/annotations/{annotation_index}", response_model=AnnotationRead)
async def update_annotation(
    image_key: str,
    annotation_index: int,
    annotation_in: AnnotationCreate,
    db: AsyncSession = Depends(get_session)
):
    annotation = await db.get(Annotation, (image_key, annotation_index))
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found.")

    annotation.instrument = annotation_in.instrument
    annotation.polygon = annotation_in.polygon
    db.add(annotation)
    await db.commit()
    await db.refresh(annotation)
    return annotation

# 4. List all images, optionally filtering by user, location, or instrument
@app.get("/images", response_model=List[ImageRead])
async def list_images(
    user_ids: Optional[List[str]] = Query(None),
    location_ids: Optional[List[str]] = Query(None),
    instrument_ids: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_session)
):
    query = select(Image).options(selectinload(Image.annotations))
    
    if user_ids:
        query = query.where(Image.user_id.in_(user_ids))
    if location_ids:
        query = query.where(Image.location_id.in_(location_ids))
    if instrument_ids:
        # When filtering by instrument, join with the Annotation table.
        query = query.join(Image.annotations).where(Annotation.instrument.in_(instrument_ids))
    
    results = await db.execute(query.distinct())
    images = results.scalars().unique().all()
    return images




# 6. Return the annotations of an image
@app.get("/images/{image_key}/annotations", response_model=List[AnnotationRead])
async def get_image_annotations(
    image_key: str,
    db: AsyncSession = Depends(get_session)
):
    from sqlalchemy import select

    image = await db.get(Image, image_key)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found.")

    query = select(Annotation).where(Annotation.image_key == image_key)
    results = await db.execute(query)
    annotations = results.scalars().all()
    return annotations



# {
#   "image_key": "./images/scalpel.png",
#   "client_id": "client01",
#   "created_at": "2025-02-24T00:00:00Z",
#   "hardware_id": "3af9d8da-c689-48f5-bd87-afbfc999e589",
#   "ml_tag": "TRAIN",
#   "location_id": "loc1",
#   "user_id": "user1",
#   "annotations": [
#     {
#       "index": 0,
#       "instrument": "instr1",
#       "polygon": {
#         "points": [[0, 0], [1, 1]]
#       }
#     }
#   ]
# }



# New endpoint to return an image with adjustable scale and quality
@app.get("/images/{image_key}/file")
async def get_image_file(
    image_key: str,
    scale: float = Query(1.0, gt=0.0, description="Scaling factor for the image (e.g., 0.5 for half size)"),
    quality: int = Query(75, ge=1, le=100, description="Quality for JPEG images (1-100)"),
    db: AsyncSession = Depends(get_session)
):
    # Verify the image exists in the database
    image_obj = await db.get(Image, image_key)
    if not image_obj:
        raise HTTPException(status_code=404, detail="Image not found in database.")

    # For the purpose of this challenge, we assume image_key is the file path on local disk.
    file_path = image_key
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image file not found on disk.")

    # Open the image using Pillow
    with PILImage.open(file_path) as img:
        # Apply scaling if necessary
        if scale != 1.0:
            new_size = (int(img.width * scale), int(img.height * scale))
            # Using Resampling.LANCZOS for high-quality downsampling
            img = img.resize(new_size, PILImage.Resampling.LANCZOS)

        # Save the image to an in-memory buffer
        buf = BytesIO()
        # Determine the image format, defaulting to JPEG if not set
        image_format = img.format if img.format else "JPEG"
        # If the image is JPEG, apply the quality parameter
        if image_format.upper() == "JPEG":
            img.save(buf, format=image_format, quality=quality)
        else:
            img.save(buf, format=image_format)
        buf.seek(0)

        # Set the appropriate media type based on image format
        if image_format.upper() == "JPEG":
            media_type = "image/jpeg"
        elif image_format.upper() == "PNG":
            media_type = "image/png"
        else:
            media_type = "application/octet-stream"

    return StreamingResponse(buf, media_type=media_type)