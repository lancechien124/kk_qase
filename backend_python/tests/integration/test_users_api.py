"""
Integration tests for Users API
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_users(authenticated_client: AsyncClient, test_user):
    """Test getting all users"""
    response = await authenticated_client.get("/api/v1/users")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_user_by_id(authenticated_client: AsyncClient, test_user):
    """Test getting user by ID"""
    response = await authenticated_client.get(f"/api/v1/users/{test_user.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["name"] == test_user.name


@pytest.mark.asyncio
async def test_create_user(authenticated_client: AsyncClient):
    """Test creating a user"""
    user_data = {
        "name": "new_user",
        "email": "new@example.com",
        "password": "password123",
    }
    
    response = await authenticated_client.post("/api/v1/users", json=user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_update_user(authenticated_client: AsyncClient, test_user):
    """Test updating a user"""
    update_data = {
        "name": "updated_user",
        "email": "updated@example.com",
    }
    
    response = await authenticated_client.put(
        f"/api/v1/users/{test_user.id}",
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["email"] == update_data["email"]


@pytest.mark.asyncio
async def test_delete_user(authenticated_client: AsyncClient, test_user):
    """Test deleting a user"""
    response = await authenticated_client.delete(f"/api/v1/users/{test_user.id}")
    
    assert response.status_code == 200
    
    # Verify user is deleted
    get_response = await authenticated_client.get(f"/api/v1/users/{test_user.id}")
    assert get_response.status_code == 404

