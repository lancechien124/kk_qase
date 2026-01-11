"""
Integration tests for Project API
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_projects(authenticated_client: AsyncClient, test_project):
    """Test getting all projects"""
    response = await authenticated_client.get("/api/v1/project")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_project_by_id(authenticated_client: AsyncClient, test_project):
    """Test getting project by ID"""
    response = await authenticated_client.get(f"/api/v1/project/{test_project.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_project.id
    assert data["name"] == test_project.name


@pytest.mark.asyncio
async def test_create_project(authenticated_client: AsyncClient):
    """Test creating a project"""
    project_data = {
        "name": "New Project",
        "description": "New project description",
        "organization_id": "test_org_id",
    }
    
    response = await authenticated_client.post("/api/v1/project", json=project_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == project_data["name"]
    assert data["description"] == project_data["description"]


@pytest.mark.asyncio
async def test_update_project(authenticated_client: AsyncClient, test_project):
    """Test updating a project"""
    update_data = {
        "name": "Updated Project",
        "description": "Updated description",
    }
    
    response = await authenticated_client.put(
        f"/api/v1/project/{test_project.id}",
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]


@pytest.mark.asyncio
async def test_delete_project(authenticated_client: AsyncClient, test_project):
    """Test deleting a project"""
    response = await authenticated_client.delete(f"/api/v1/project/{test_project.id}")
    
    assert response.status_code == 200
    
    # Verify project is deleted
    get_response = await authenticated_client.get(f"/api/v1/project/{test_project.id}")
    assert get_response.status_code == 404

