# main.py
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import selectinload
from PIL import Image as PILImage
from sqlalchemy import select
from io import BytesIO
import os
import logging
import json
from .database import engine, get_session
from .models import Base, Image, Annotation, Location, User
from .schemas import (
    ImageCreate, ImageRead, AnnotationCreate, AnnotationRead, ImageFilter
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level (INFO, DEBUG, etc.)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create a logger instance for this module
logger = logging.getLogger(__name__)


# Define directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
# We'll store uploads in a subfolder of the static directory (e.g., "uploads")
UPLOAD_DIR = os.path.join(STATIC_DIR, "images")
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure upload directory exists

app = FastAPI(title="Scalpel Challenge, FastAPI & Async SQLAlchemy")


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))



@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application and creating tables...")
    """
    Create tables at startup (not recommended for production,
    but convenient for a coding challenge).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

print("Starting up the application and creating tables...")

async def save_upload_file(upload_file: UploadFile) -> str:
    # Save file in the UPLOAD_DIR (i.e., static/images)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_location = os.path.join(UPLOAD_DIR, upload_file.filename)
    with open(file_location, "wb") as file_object:
        file_object.write(await upload_file.read())
    # Return the URL path for the file so clients can access it via /static
    return f"/static/images/{upload_file.filename}"

# {
#     "image_key": "",
#     "client_id": "client01",
#     "created_at": "2025-02-24T00:00:00Z",
#     "hardware_id": "3af9d8da-c689-48f5-bd87-afbfc999e589",
#     "ml_tag": "TRAIN",
#     "location_id": "loc1",
#     "user_id": "user1",
#     "annotations": [
#         {
#             "index": 0,
#             "instrument": "instr1",
#             "polygon": {
#                 "points": [[0, 0], [1, 1]]
#             }
#         }
#     ]
# }


@app.post("/images", response_model=ImageRead)
async def create_image(
    image_file: UploadFile = File(...),
    image_form: str = Form(...),
    db: AsyncSession = Depends(get_session)
):
    # Parse the JSON string from the form field
    try:
        image_form_data = json.loads(image_form)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in image_form: {str(e)}")
    
    # Build the Pydantic model from the parsed data
    try:
        image_in = ImageCreate(**image_form_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing image form data: {str(e)}")
    
    # Save the uploaded file and get the file location to use as image_key
    try:
        image_key = await save_upload_file(image_file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error saving image file: {str(e)}")
    
    # Update the image data with the new image_key.
    # Using .copy(update={...}) ensures immutability is preserved.
    image_in = image_in.copy(update={"image_key": image_key})
    
    # Optional: Check if an image with the same key already exists.
    existing_image = await db.get(Image, image_in.image_key)
    if existing_image:
        raise HTTPException(status_code=400, detail="Image key already exists.")
    
    # If a location_id is provided, ensure the location exists or create it.
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
    
    # If a user_id is provided, check if the user exists.
    if image_in.user_id:
        user = await db.get(User, image_in.user_id)
        if not user:
            # Optionally, create a default user or raise an error.
            new_user = User(
                id=image_in.user_id,
                first_name="Default",
                last_name="User",
                role="default_role"
            )
            db.add(new_user)
            await db.flush()
            # Alternatively, uncomment the following line to raise an error instead:
            # raise HTTPException(status_code=400, detail="User does not exist. Please create the user first.")
    
    # Create the new Image ORM instance using the data from the Pydantic model.
    new_image = Image(
        image_key=image_in.image_key,
        client_id=image_in.client_id,
        created_at=image_in.created_at.replace(tzinfo=None),
        hardware_id=image_in.hardware_id,
        ml_tag=image_in.ml_tag.value if image_in.ml_tag else None,
        location_id=image_in.location_id,
        user_id=image_in.user_id,
    )
    
    # If there are annotations provided, add them to the image.
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
    # Optionally refresh if needed: await db.refresh(new_image)
    return new_image






# 1. Create an image (with optional annotations)
# @app.post("/images", response_model=ImageRead)
# async def create_image(
#     image_file: UploadFile = File(...),
#     image_form: str = Form(...),

#     # Include additional fields if necessary.
#     db: AsyncSession = Depends(get_session)
# ):
#     image_form = json.loads(image_form)
#     image_in = ImageCreate(**image_form)

#     try: 
#         image_key = await save_upload_file(image_file)
#         image_in["image_key"] = image_key
#         new_image = Image(


#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error saving image file: {str(e)}")
    

    # Save the uploaded file and get its storage path as image_key
    # image_key = await save_upload_file(image_file)


    # # Check if image already exists
    # existing_image = await db.get(Image, image_in.image_key)
    # if existing_image:
    #     raise HTTPException(status_code=400, detail="Image key already exists.")

    # # If a location_id is provided, ensure the location exists or create it
    # if image_in.location_id:
    #     location = await db.get(Location, image_in.location_id)
    #     if not location:
    #         new_location = Location(
    #             id=image_in.location_id,
    #             address="Default Address",
    #             country="Default Country",
    #             town="Default Town"
    #         )
    #         db.add(new_location)
    #         await db.flush()
    
    # # Check if user exists, if user_id is provided
    # if image_in.user_id:
    #     user = await db.get(User, image_in.user_id)
    #     if not user:
    #         # Option 1: Create a default user (if appropriate)
    #         new_user = User(
    #             id=image_in.user_id,
    #             first_name="Default",
    #             last_name="User",
    #             role="default_role"
    #         )
    #         db.add(new_user)
    #         await db.flush()
            
    #         # Option 2: Raise an error to indicate the user must exist
    #         raise HTTPException(status_code=400, detail="User does not exist. Please create the user first.")

    # new_image = Image(
    #     image_key=image_in.image_key,
    #     client_id=image_in.client_id,
    #     created_at=image_in.created_at.replace(tzinfo=None),
    #     hardware_id=image_in.hardware_id,
    #     ml_tag=image_in.ml_tag.value if image_in.ml_tag else None,
    #     location_id=image_in.location_id,
    #     user_id=image_in.user_id,
    # )

    # if image_in.annotations:
    #     for ann in image_in.annotations:
    #         annotation = Annotation(
    #             image_key=image_in.image_key,
    #             index=ann.index,
    #             instrument=ann.instrument,
    #             polygon=ann.polygon
    #         )
    #         new_image.annotations.append(annotation)

    # db.add(new_image)
    # await db.commit()
    # # the refresh is giving issues, needs more work.
    # # await db.refresh(new_image, options=[selectinload(Image.annotations)])
    # return new_image




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

@app.post("/images/{image_key:path}/annotations", response_model=AnnotationRead)
async def create_annotation(
    image_key: str,
    annotation_in: AnnotationCreate,
    db: AsyncSession = Depends(get_session)
):
    image = await db.get(Image, image_key)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found.")

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
@app.put("/images/{image_key:path}/annotations/{annotation_index}", response_model=AnnotationRead)
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
# @app.get("/images", response_model=List[ImageRead])
# async def list_images(
#     user_ids: Optional[List[str]] = Query(None),
#     location_ids: Optional[List[str]] = Query(None),
#     instrument_ids: Optional[List[str]] = Query(None),
#     db: AsyncSession = Depends(get_session)
# ):
#     logger.info("popitsso GET /images")
#     query = select(Image).options(selectinload(Image.annotations))
    
#     if user_ids:
#         query = query.where(Image.user_id.in_(user_ids))
#     if location_ids:
#         query = query.where(Image.location_id.in_(location_ids))
#     if instrument_ids:
#         # When filtering by instrument, join with the Annotation table.
#         query = query.join(Image.annotations).where(Annotation.instrument.in_(instrument_ids))
    
#     results = await db.execute(query.distinct())
#     images = results.scalars().unique().all()
#     return images


@app.get("/images")
async def list_images( db: AsyncSession = Depends(get_session)):
    # result = await db.execute(select(Image))
    # images = result.scalars().all()

    # return images
    query = select(Image).options(selectinload(Image.annotations))

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
# @app.get("/images/{image_key}/file")
# async def get_image_file(
#     image_key: str,
#     scale: float = Query(1.0, gt=0.0, description="Scaling factor for the image (e.g., 0.5 for half size)"),
#     quality: int = Query(75, ge=1, le=100, description="Quality for JPEG images (1-100)"),
#     db: AsyncSession = Depends(get_session)
# ):
#     # Verify the image exists in the database
#     image_obj = await db.get(Image, image_key)
#     if not image_obj:
#         raise HTTPException(status_code=404, detail="Image not found in database.")

#     # For the purpose of this challenge, we assume image_key is the file path on local disk.
#     file_path = image_key
#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="Image file not found on disk.")

#     # Open the image using Pillow
#     with PILImage.open(file_path) as img:
#         # Apply scaling if necessary
#         if scale != 1.0:
#             new_size = (int(img.width * scale), int(img.height * scale))
#             # Using Resampling.LANCZOS for high-quality downsampling
#             img = img.resize(new_size, PILImage.Resampling.LANCZOS)

#         # Save the image to an in-memory buffer
#         buf = BytesIO()
#         # Determine the image format, defaulting to JPEG if not set
#         image_format = img.format if img.format else "JPEG"
#         # If the image is JPEG, apply the quality parameter
#         if image_format.upper() == "JPEG":
#             img.save(buf, format=image_format, quality=quality)
#         else:
#             img.save(buf, format=image_format)
#         buf.seek(0)

#         # Set the appropriate media type based on image format
#         if image_format.upper() == "JPEG":
#             media_type = "image/jpeg"
#         elif image_format.upper() == "PNG":
#             media_type = "image/png"
#         else:
#             media_type = "application/octet-stream"

#     return StreamingResponse(buf, media_type=media_type)

# new converted endpoint
# @app.get("/images/{image_key}/file")
# async def get_image_file(
#     image_key: str,
#     scale: float = Query(1.0, gt=0.0, description="Scaling factor for the image (e.g., 0.5 for half size)"),
#     quality: int = Query(75, ge=1, le=100, description="Quality for JPEG images (1-100)"),
#     db: AsyncSession = Depends(get_session)
# ):
#     # Verify the image exists in the database
#     image_obj = await db.get(Image, image_key)
#     if not image_obj:
#         raise HTTPException(status_code=404, detail="Image not found in database.")

#     # Convert the URL image key to an actual file path.
#     # For example, if image_key is "/static/images/filename.png", remove "/static" and prepend STATIC_DIR.
#     if image_key.startswith("/static"):
#         file_path = os.path.join(STATIC_DIR, image_key[len("/static/"):])
#     else:
#         file_path = image_key

#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="Image file not found on disk.")

#     with PILImage.open(file_path) as img:
#         if scale != 1.0:
#             new_size = (int(img.width * scale), int(img.height * scale))
#             img = img.resize(new_size, PILImage.Resampling.LANCZOS)

#         buf = BytesIO()
#         image_format = img.format if img.format else "JPEG"
#         if image_format.upper() == "JPEG":
#             img.save(buf, format=image_format, quality=quality)
#         else:
#             img.save(buf, format=image_format)
#         buf.seek(0)

#         if image_format.upper() == "JPEG":
#             media_type = "image/jpeg"
#         elif image_format.upper() == "PNG":
#             media_type = "image/png"
#         else:
#             media_type = "application/octet-stream"

#     return StreamingResponse(buf, media_type=media_type)



@app.delete("/images/{image_key:path}")
async def delete_image(image_key: str, db: AsyncSession = Depends(get_session)):
    logger.info(f"Image key: {image_key}")
    print("Image delete", image_key)

    # Retrieve the image record from the database using the provided key.
    result = await db.execute(select(Image).filter(Image.image_key == image_key))
    image = result.scalars().first()  # get the first matching image

    print("Image retrieved:", image)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found in database.")
    
    # Delete the image record from the database.
    await db.delete(image)
    await db.commit()

    return {"detail": "Image deleted successfully."}


@app.get("/test")
async def delete_image( db: AsyncSession = Depends(get_session)):
    # logger.info(f"Image key: {image_key}")
    # print("Image delete", image_key)

    # result = await db.execute(select(Image).filter(Image.image_key == image_key))
    result = await db.execute(select(Image))
    images = result.scalars().all()

    for image in images:
        image_data = {column.name: getattr(image, column.name) for column in image.__table__.columns}
        print(image_data)
    # Retrieve the image record from the database using the provided key.
    # image = await db.get(Image, image_key)
    print("Image retrieved:", images[0].image_key)
    if not images:
        raise HTTPException(status_code=404, detail="Image not found in database.")
    
    image = images[0]

    # Delete the image record from the database.
    # await db.delete(image)
    # await db.commit()

    return {"detail": "Image deleted successfully."}





@app.put("/images/{image_key:path}/file")
async def update_image_file(
    image_key: str,
    scale: float = Query(1.0, gt=0.0, description="Scaling factor for the image (e.g., 0.5 for half size)"),
    quality: int = Query(75, ge=1, le=100, description="Quality for JPEG images (1-100)"),
    db: AsyncSession = Depends(get_session)
):
    print("Image update", image_key)
    # Verify the image exists in the database
    image_obj = await db.get(Image, image_key)
    if not image_obj:
        raise HTTPException(status_code=404, detail="Image not found in database.")

    # Convert the URL-based image key to a file system path.
    if image_key.startswith("/static"):
        file_path = os.path.join(STATIC_DIR, image_key[len("/static/"):])
    else:
        file_path = image_key

    print("File path:", file_path)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image file not found on disk.")

    # Open the image, apply scaling and quality changes
    with PILImage.open(file_path) as img:
        if scale != 1.0:
            new_size = (int(img.width * scale), int(img.height * scale))
            img = img.resize(new_size, PILImage.Resampling.LANCZOS)

        buf = BytesIO()
        image_format = img.format if img.format else "JPEG"
        if image_format.upper() == "JPEG":
            img.save(buf, format=image_format, quality=quality)
        else:
            # For PNG, quality is not used but you could add optimize/compression options
            img.save(buf, format=image_format)
        buf.seek(0)

        # Optionally, overwrite the file on disk with the updated version
        with open(file_path, "wb") as f:
            f.write(buf.getbuffer())
        buf.seek(0)

    return StreamingResponse(buf, media_type=f"image/{image_format.lower()}")
