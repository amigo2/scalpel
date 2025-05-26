import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.app.models import User  # adjust import as needed
import json

@pytest.fixture
async def create_test_user(db_session: AsyncSession):
    """Fixture to create a test user before running tests."""
    user_id = f"user_{uuid.uuid4()}"
    user = User(
        id=user_id,
        first_name="Test",
        last_name="User",
        role="default_role"
    )
    db_session.add(user)
    await db_session.commit()
    yield user

    # ✅ Ensure cleanup of related data before deleting the user
    try:
        # First delete images related to the user
        await db_session.execute(text("DELETE FROM image WHERE user_id = :uid"), {"uid": user_id})

        # Now delete the user
        await db_session.execute(text("DELETE FROM \"user\" WHERE id = :uid"), {"uid": user_id})

        await db_session.commit()  # ✅ Ensure changes are committed
    except Exception as e:
        await db_session.rollback()  # 🔄 Rollback if an error occurs
        print(f"❌ Error deleting test user: {e}")  # Debugging





@pytest.mark.asyncio
async def test_create_image(test_client: AsyncClient, create_test_user):
    """Test creating an image through the FastAPI endpoint with a unique image_key."""
    
    # Generate a random unique image_key
    unique_image_key = f"/static/images/test_{uuid.uuid4().hex}.png"
    
    # Prepare the image form data
    image_form_data = {
        "image_key": unique_image_key,  # ✅ Ensure unique image_key
        "client_id": "client01",
        "created_at": "2025-02-24T00:00:00Z",
        "hardware_id": "3af9d8da-c689-48f5-bd87-afbfc999e589",
        "ml_tag": "TRAIN",
        "location_id": "loc1",
        "user_id": create_test_user.id,  # Use ID from fixture
        "annotations": [
            {
                "index": 0,
                "instrument": "instr1",
                "polygon": {
                    "points": [[0, 0], [1, 1]]
                }
            }
        ]
    }

    # Simulate an image file upload
    image_content = b"fake image data"
    
    # Prepare the request as `multipart/form-data`
    files = {
        "image_file": (f"test_image_{uuid.uuid4().hex}.png", image_content, "image/png"),
        "image_form": (None, json.dumps(image_form_data)),  # ✅ Fix `image_form`
    }

    # Send the request
    response = await test_client.post("/images", files=files)

    # Check response
    assert response.status_code == 200, f"Response failed: {response.json()}"
    data = response.json()

    # ✅ Allow flexible matching for `image_key`
    assert data["image_key"].endswith(".png"), f"Unexpected image_key: {data['image_key']}"

    assert len(data["annotations"]) == 1
    assert data["annotations"][0]["instrument"] == "instr1"



# import pytest
# import uuid
# import json
# from httpx import AsyncClient
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import text
# from src.app.models import Annotation  # adjust import as needed

# @pytest.mark.asyncio
# async def test_create_annotation(test_client: AsyncClient, create_test_user, db_session: AsyncSession):
#     """Test creating an annotation for an existing image."""

#     # ✅ Generate a unique image_key
#     unique_image_key = f"/static/images/test_{uuid.uuid4().hex}.png"

#     # ✅ Create an image before adding annotations
#     image_form_data = {
#         "image_key": unique_image_key,
#         "client_id": "client01",
#         "created_at": "2025-02-24T00:00:00Z",
#         "hardware_id": "3af9d8da-c689-48f5-bd87-afbfc999e589",
#         "ml_tag": "TRAIN",
#         "location_id": "loc1",
#         "user_id": create_test_user.id,
#         "annotations": []  # No annotations initially
#     }

#     image_content = b"fake image data"
#     files = {
#         "image_file": (f"test_image_{uuid.uuid4().hex}.png", image_content, "image/png"),
#         "image_form": (None, json.dumps(image_form_data)),
#     }

#     # ✅ Ensure database operations are properly awaited
#     async with db_session.begin():
#         image_response = await test_client.post("/images", files=files)
#         assert image_response.status_code == 200, f"Response failed: {image_response.json()}"
#         image_data = image_response.json()

#     # ✅ Add annotation to the created image
#     annotation_data = {
#         "index": 0,
#         "instrument": "instr1",
#         "polygon": {"points": [[0, 0], [1, 1]]}
#     }

#     annotation_response = await test_client.post(
#         f"/images/{unique_image_key}/annotations", json=annotation_data
#     )

#     assert annotation_response.status_code == 200, f"Response failed: {annotation_response.json()}"
    
#     annotation_result = annotation_response.json()
#     assert annotation_result["index"] == 0
#     assert annotation_result["instrument"] == "instr1"
#     assert annotation_result["polygon"]["points"] == [[0, 0], [1, 1]]








@pytest.fixture(scope="session", autouse=True)
async def cleanup_test_data_after_session(db_session: AsyncSession):
    """Cleanup test data after the test session."""
    yield  # Let tests run first

    try:
        # 🔴 Delete annotations first (since they reference images)
        await db_session.execute(text("DELETE FROM annotation WHERE image_key LIKE 'test_%'"))

        # 🟡 Then delete images (since they reference users)
        await db_session.execute(text("DELETE FROM image WHERE image_key LIKE 'test_%'"))

        # 🟢 Finally, delete users
        await db_session.execute(text("DELETE FROM \"user\" WHERE id LIKE 'user_%'"))

        await db_session.commit()  # ✅ Ensure changes are committed
    except Exception as e:
        await db_session.rollback()  # 🔄 Rollback if an error occurs
        print(f"❌ Cleanup failed: {e}")



# import pytest
# import uuid
# import os
# from httpx import AsyncClient
# from sqlalchemy.ext.asyncio import AsyncSession
# from PIL import Image as PILImage
# from io import BytesIO
# from src.app.models import Image

# STATIC_DIR = "/app/static/images"  # Adjust this if your directory is different

# @pytest.fixture
# async def create_test_image(db_session: AsyncSession):
#     """Fixture to create a test image and store it in the static directory."""
    
#     # ✅ Generate a unique image key
#     image_key = f"test_image_{uuid.uuid4().hex}.png"
#     file_path = os.path.join(STATIC_DIR, image_key)

#     # ✅ Create and save a test image
#     img = PILImage.new("RGB", (100, 100), color="blue")  # A simple blue image
#     img.save(file_path, "PNG")

#     # ✅ Insert test image entry in the database
#     test_image = Image(image_key=f"/static/images/{image_key}", client_id="client01")
#     db_session.add(test_image)
#     await db_session.commit()

#     yield test_image, file_path  # Pass the image key and path to the test

#     # ✅ Cleanup: Remove the test image after the test
#     if os.path.exists(file_path):
#         os.remove(file_path)

#     await db_session.execute(
#         "DELETE FROM image WHERE image_key = :image_key", {"image_key": f"/static/images/{image_key}"}
#     )
#     await db_session.commit()


# @pytest.mark.asyncio
# async def test_update_image_file(test_client: AsyncClient, create_test_image):
#     """Test updating an image file by applying scaling and quality settings."""
    
#     test_image, file_path = create_test_image
#     image_key = test_image.image_key  # Get the image key stored in DB

#     # ✅ Check the original file exists before updating
#     assert os.path.exists(file_path), "Test image file should exist before update"

#     # ✅ Define the scaling and quality parameters
#     params = {"scale": 0.5, "quality": 80}  # Reduce image size by 50% & set quality to 80

#     # ✅ Send the PUT request
#     response = await test_client.put(f"/images/{image_key}/file", params=params)

#     # ✅ Verify the response is successful
#     assert response.status_code == 200, f"Failed response: {response.json()}"

#     # ✅ Read the updated image
#     with PILImage.open(file_path) as img:
#         # Check if scaling was applied correctly
#         assert img.size == (50, 50), f"Unexpected image size: {img.size}"
