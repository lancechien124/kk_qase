"""
Unit tests for AuthService
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import AuthService
from app.core.security import verify_password


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test user creation"""
    auth_service = AuthService(db_session)
    
    user = await auth_service.create_user(
        name="test_user",
        email="test@example.com",
        password="test_password123",
    )
    
    assert user is not None
    assert user.name == "test_user"
    assert user.email == "test@example.com"
    assert verify_password("test_password123", user.password)


@pytest.mark.asyncio
async def test_authenticate_user(db_session: AsyncSession):
    """Test user authentication"""
    auth_service = AuthService(db_session)
    
    # Create user
    await auth_service.create_user(
        name="test_user",
        email="test@example.com",
        password="test_password123",
    )
    
    # Authenticate with correct password
    user = await auth_service.authenticate_user("test@example.com", "test_password123")
    assert user is not None
    assert user.email == "test@example.com"
    
    # Authenticate with wrong password
    user = await auth_service.authenticate_user("test@example.com", "wrong_password")
    assert user is None


@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession):
    """Test getting user by email"""
    auth_service = AuthService(db_session)
    
    # Create user
    created_user = await auth_service.create_user(
        name="test_user",
        email="test@example.com",
        password="test_password123",
    )
    
    # Get user by email
    user = await auth_service.get_user_by_email("test@example.com")
    assert user is not None
    assert user.id == created_user.id
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_name(db_session: AsyncSession):
    """Test getting user by name"""
    auth_service = AuthService(db_session)
    
    # Create user
    created_user = await auth_service.create_user(
        name="test_user",
        email="test@example.com",
        password="test_password123",
    )
    
    # Get user by name
    user = await auth_service.get_user_by_name("test_user")
    assert user is not None
    assert user.id == created_user.id
    assert user.name == "test_user"


@pytest.mark.asyncio
async def test_password_hashing():
    """Test password hashing"""
    from app.services.auth_service import AuthService
    from app.core.security import verify_password
    
    auth_service = AuthService(None)  # No DB needed for hashing
    
    password = "test_password123"
    hashed = auth_service.get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)

