"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from main import app


# Test database URL (use in-memory SQLite for testing)
# Note: aiosqlite is required for async SQLite support
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user"""
    from app.services.auth_service import AuthService
    
    auth_service = AuthService(db_session)
    
    user_data = {
        "name": "test_user",
        "email": "test@example.com",
        "password": "test_password123",
    }
    
    user = await auth_service.create_user(
        name=user_data["name"],
        email=user_data["email"],
        password=user_data["password"],
    )
    
    return user


@pytest.fixture
async def authenticated_client(client: AsyncClient, test_user: User) -> AsyncClient:
    """Create an authenticated test client"""
    token = create_access_token(data={"sub": test_user.id})
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin test user"""
    from app.services.auth_service import AuthService
    from app.models.user_role import UserRole
    from app.models.user_role_relation import UserRoleRelation
    from app.core.security import InternalUserRole
    
    auth_service = AuthService(db_session)
    
    user_data = {
        "name": "admin_user",
        "email": "admin@example.com",
        "password": "admin_password123",
    }
    
    user = await auth_service.create_user(
        name=user_data["name"],
        email=user_data["email"],
        password=user_data["password"],
    )
    
    # TODO: Assign admin role to user
    # This would require creating a role and relation
    
    return user


@pytest.fixture
async def test_project(db_session: AsyncSession, test_user: User):
    """Create a test project"""
    from app.models.project import Project
    
    project = Project(
        name="Test Project",
        description="Test project description",
        organization_id="test_org_id",
        create_user=test_user.id,
    )
    
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    
    return project

