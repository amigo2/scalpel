# tests/test_endpoints.py
import pytest
from httpx import AsyncClient, ASGITransport
from src.app.main import app

@pytest.mark.asyncio
async def test_create_image():
    payload = {
        "image_key": "test_image",
        "client_id": "client1",
        "created_at": "2025-02-24T00:00:00Z",
        "hardware_id": "hw_001",
        "ml_tag": "TRAIN",
        "location_id": "loc1",
        "user_id": "user1",
        "annotations": [
            {"index": 0, "instrument": "instr1", "polygon": {"points": [[0, 0], [1, 1]]}}
        ]
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/images", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["image_key"] == payload["image_key"]
        # Optionally, check that annotations were created
        assert len(data["annotations"]) == 1

@pytest.mark.asyncio
async def test_update_annotation():
    # First, create an image with an annotation
    create_payload = {
        "image_key": "test_image_update",
        "client_id": "client_update",
        "created_at": "2025-02-24T00:00:00Z",
        "hardware_id": "hw_002",
        "ml_tag": "TEST",
        "location_id": "loc_update",
        "user_id": "user_update",
        "annotations": [
            {"index": 0, "instrument": "instr_update", "polygon": {"points": [[0, 0], [2, 2]]}}
        ]
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create_resp = await client.post("/images", json=create_payload)
        assert create_resp.status_code == 200

        # Now update the annotation
        update_payload = {
            "index": 0,  # This is required by the schema for update
            "instrument": "instr_updated",
            "polygon": {"points": [[1, 1], [3, 3]]}
        }
        update_url = f"/images/{create_payload['image_key']}/annotations/0"
        update_resp = await client.put(update_url, json=update_payload)
        assert update_resp.status_code == 200
        updated_data = update_resp.json()
        assert updated_data["instrument"] == "instr_updated"

@pytest.mark.asyncio
async def test_list_images_and_annotations():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.get("/images")
        assert list_resp.status_code == 200
        images = list_resp.json()
        assert isinstance(images, list)
        
        # Optionally, if an image exists, test the annotations endpoint
        if images:
            image_key = images[0]["image_key"]
            ann_resp = await client.get(f"/images/{image_key}/annotations")
            assert ann_resp.status_code == 200
            annotations = ann_resp.json()
            assert isinstance(annotations, list)
