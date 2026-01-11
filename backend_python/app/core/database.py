"""
Database Configuration and Session Management
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator

from app.core.config import settings

# Create async engine
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("mysql+pymysql://", "mysql+aiomysql://"),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_POOL_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    echo=settings.DEBUG,
    future=True,
)

# Create sync engine for migrations
sync_engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_POOL_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    echo=settings.DEBUG,
)

# Session makers
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database (create tables if not exist)"""
    # Import all models here to ensure they are registered
    # This must be at module level, so we import them before calling this function
    # Models are imported in app/models/__init__.py
    
    async with async_engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


def get_sync_db():
    """Get synchronous database session (for migrations)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

