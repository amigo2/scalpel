import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

@pytest.mark.asyncio
async def test_create_image(test_client: AsyncClient):
    """Test creating an image through the FastAPI endpoint with a unique image_key."""
    unique_image_key = f"test_{uuid.uuid4()}"  # Generate a unique image_key starting with "test_"

    image_data = {
        "image_key": unique_image_key,
        "client_id": "client01",
        "created_at": "2025-02-24T00:00:00Z",
        "hardware_id": "3af9d8da-c689-48f5-bd87-afbfc999e589",
        "ml_tag": "TRAIN",
        "location_id": "loc1",
        "user_id": "user1",
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

    response = await test_client.post("/images", json=image_data)

    assert response.status_code == 200, f"Response failed: {response.json()}"

    data = response.json()
    assert data["image_key"] == unique_image_key
    assert "annotations" in data
    assert len(data["annotations"]) == 1
    assert data["annotations"][0]["instrument"] == "instr1"


@pytest.fixture(scope="session", autouse=True)
async def cleanup_test_data_after_session(db_session: AsyncSession):
    """Cleanup test data where image_key starts with 'test_' after the test session."""
    yield  # Allow all tests to run first

    await db_session.execute(text("DELETE FROM annotation WHERE image_key LIKE 'test_%'"))

    # Cleanup test images and annotations
    await db_session.execute(text("DELETE FROM image WHERE image_key LIKE 'test_%'"))


    await db_session.commit()  # Commit the deletions
