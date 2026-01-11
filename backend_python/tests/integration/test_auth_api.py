"""
Integration tests for Auth API
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login"""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "test_password123",
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, test_user):
    """Test login with invalid credentials"""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "wrong_password",
        },
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(authenticated_client: AsyncClient, test_user):
    """Test getting current user"""
    response = await authenticated_client.get("/api/v1/auth/me")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test getting current user without authentication"""
    response = await client.get("/api/v1/auth/me")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(authenticated_client: AsyncClient):
    """Test logout"""
    response = await authenticated_client.post("/api/v1/auth/logout")
    
    assert response.status_code == 200

