"""
Authentication Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from typing import Optional
import uuid

from app.core.config import settings
from app.core.redis import redis_client
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user by email or name"""
        # Try to find user by email first, then by name
        user = await self.get_user_by_email(username)
        if not user:
            user = await self.get_user_by_name(username)
        
        if not user:
            return None
        
        if not user.enable:
            return None
        
        if not user.password:
            return None
        
        if not self.verify_password(password, user.password):
            return None
        
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email, User.deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_name(self, name: str) -> Optional[User]:
        """Get user by name"""
        result = await self.db.execute(
            select(User).where(User.name == name, User.deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username (email or name)"""
        user = await self.get_user_by_email(username)
        if not user:
            user = await self.get_user_by_name(username)
        return user
    
    async def create_session(self, user: User) -> str:
        """Create session for user"""
        session_id = str(uuid.uuid4())
        await redis_client.set_session(
            session_id=session_id,
            user_id=user.id,
            data={
                "email": user.email,
                "name": user.name,
                "last_organization_id": user.last_organization_id,
                "last_project_id": user.last_project_id,
            }
        )
        return session_id
    
    async def get_session_user(self, session_id: str) -> Optional[dict]:
        """Get user from session"""
        session = await redis_client.get_session(session_id)
        if session:
            user_id = session.get("user_id")
            if user_id:
                # Get user from database
                user = await self.get_user_by_id(user_id)
                if user:
                    return {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "last_organization_id": user.last_organization_id,
                        "last_project_id": user.last_project_id,
                    }
        return None
    
    async def delete_session(self, session_id: str):
        """Delete session"""
        await redis_client.delete_session(session_id)
    
    async def get_user_with_cache(self, user_id: str) -> Optional[User]:
        """Get user with Redis cache"""
        cache_key = f"user:{user_id}"
        
        # Try to get from cache
        cached_user = await redis_client.get_cache(cache_key)
        if cached_user:
            # Reconstruct User object from cache (simplified)
            # In production, you might want to store more fields
            user = User(
                id=cached_user.get("id"),
                name=cached_user.get("name"),
                email=cached_user.get("email"),
            )
            return user
        
        # Get from database
        user = await self.get_user_by_id(user_id)
        if user:
            # Cache user data
            await redis_client.set_cache(
                cache_key,
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "enable": user.enable,
                },
                expire=3600  # 1 hour
            )
        
        return user

