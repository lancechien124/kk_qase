"""
Unit tests for UserService
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate


@pytest.mark.asyncio
async def test_get_users(db_session: AsyncSession, test_user):
    """Test getting all users"""
    user_service = UserService(db_session)
    
    users = await user_service.get_users(skip=0, limit=10)
    
    assert len(users) >= 1
    assert any(user.id == test_user.id for user in users)


@pytest.mark.asyncio
async def test_get_user_by_id(db_session: AsyncSession, test_user):
    """Test getting user by ID"""
    user_service = UserService(db_session)
    
    user = await user_service.get_user_by_id(test_user.id)
    
    assert user is not None
    assert user.id == test_user.id
    assert user.name == test_user.name


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test creating a user"""
    user_service = UserService(db_session)
    
    user_data = UserCreate(
        name="new_user",
        email="new@example.com",
        password="password123",
    )
    
    user = await user_service.create_user(user_data)
    
    assert user is not None
    assert user.name == "new_user"
    assert user.email == "new@example.com"


@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession, test_user):
    """Test updating a user"""
    user_service = UserService(db_session)
    
    update_data = UserUpdate(
        name="updated_user",
        email="updated@example.com",
    )
    
    updated_user = await user_service.update_user(test_user.id, update_data)
    
    assert updated_user is not None
    assert updated_user.name == "updated_user"
    assert updated_user.email == "updated@example.com"


@pytest.mark.asyncio
async def test_delete_user(db_session: AsyncSession, test_user):
    """Test deleting a user"""
    user_service = UserService(db_session)
    
    await user_service.delete_user(test_user.id)
    
    # Try to get deleted user
    user = await user_service.get_user_by_id(test_user.id)
    assert user is None

