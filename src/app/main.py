# main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from .database import engine, get_session
from .models import Base, Image, Annotation
from .schemas import (
    ImageCreate, ImageRead, AnnotationCreate, AnnotationRead, ImageFilter
)

app = FastAPI(title="Scalpel Challenge FastAPI & Async SQLAlchemy")

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

    # Create Image ORM object
    new_image = Image(
        image_key=image_in.image_key,
        client_id=image_in.client_id,
        created_at=image_in.created_at,
        hardware_id=image_in.hardware_id,
        ml_tag=image_in.ml_tag.value if image_in.ml_tag else None,
        location_id=image_in.location_id,
        user_id=image_in.user_id,
    )

    # Add annotations if provided
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
    await db.refresh(new_image)
    return new_image

# 2. Create a new annotation for a given image
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
    """
    Example usage:
      GET /images?user_ids=123&user_ids=456&location_ids=LOC789&instrument_ids=INSTR987
    """
    from sqlalchemy import select, or_, and_

    query = select(Image).outerjoin(Annotation)

    # If user_ids filter
    if user_ids:
        query = query.where(Image.user_id.in_(user_ids))

    # If location_ids filter
    if location_ids:
        query = query.where(Image.location_id.in_(location_ids))

    # If instrument_ids filter
    if instrument_ids:
        query = query.where(Annotation.instrument.in_(instrument_ids))

    results = await db.execute(query.distinct())
    images = results.scalars().unique().all()
    return images

# 5. Return an image (optionally transform scale/quality)
@app.get("/images/{image_key}/file")
async def get_image_file(
    image_key: str,
    scale: float = 1.0,
    quality: int = 100,
    db: AsyncSession = Depends(get_session)
):
    """
    In a real scenario, you might store images on S3 or disk.
    Then retrieve, resize/compress (e.g., using Pillow),
    and return as a streaming response or file.
    """
    image = await db.get(Image, image_key)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found.")

    # Pseudocode for retrieving and transforming the image:
    # file_path = f"/some/local/path/{image.image_key}.png"
    # from PIL import Image as PILImage
    # pil_image = PILImage.open(file_path)
    # # scale the image
    # width, height = pil_image.size
    # new_size = (int(width * scale), int(height * scale))
    # pil_image = pil_image.resize(new_size)
    # # adjust quality -> typically done when saving to JPEG
    # response_bytes = io.BytesIO()
    # pil_image.save(response_bytes, format="JPEG", quality=quality)
    # response_bytes.seek(0)
    # return StreamingResponse(response_bytes, media_type="image/jpeg")

    return {
        "message": f"Image {image_key} would be returned here with scale={scale}, quality={quality}."
    }

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
