"""
User Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
import uuid
import time

from app.models.user import User
from app.services.auth_service import AuthService


class UserService:
    """User service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_service = AuthService(db)
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email, User.deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100,
        organization_id: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> List[User]:
        """Get users with pagination"""
        query = select(User).where(User.deleted == False)
        
        if organization_id:
            query = query.where(User.last_organization_id == organization_id)
        
        if keyword:
            query = query.where(
                (User.name.like(f"%{keyword}%")) | 
                (User.email.like(f"%{keyword}%"))
            )
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_users(
        self,
        organization_id: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> int:
        """Count users"""
        query = select(func.count(User.id)).where(User.deleted == False)
        
        if organization_id:
            query = query.where(User.last_organization_id == organization_id)
        
        if keyword:
            query = query.where(
                (User.name.like(f"%{keyword}%")) | 
                (User.email.like(f"%{keyword}%"))
            )
        
        result = await self.db.execute(query)
        return result.scalar_one()
    
    async def create_user(
        self,
        name: str,
        email: str,
        password: str,
        create_user: Optional[str] = None,
        **kwargs
    ) -> User:
        """Create new user"""
        # Check if email already exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")
        
        # Generate user ID
        user_id = str(uuid.uuid4())
        
        # Hash password
        hashed_password = self.auth_service.get_password_hash(password)
        
        # Generate CFT token (identity token)
        import secrets
        cft_token = secrets.token_urlsafe(32)
        
        # Create user
        user = User(
            id=user_id,
            name=name,
            email=email,
            password=hashed_password,
            enable=True,
            source=kwargs.get("source", "LOCAL"),
            create_user=create_user,
            cft_token=cft_token,
            **{k: v for k, v in kwargs.items() if k not in ["source"]}
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update_user(
        self,
        user_id: str,
        update_user: Optional[str] = None,
        **kwargs
    ) -> Optional[User]:
        """Update user"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update password if provided
        if "password" in kwargs:
            kwargs["password"] = self.auth_service.get_password_hash(kwargs["password"])
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        user.update_user = update_user
        user.update_time = int(time.time() * 1000)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete_user(self, user_id: str, delete_user: Optional[str] = None) -> bool:
        """Soft delete user"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.deleted = True
        user.delete_time = int(time.time() * 1000)
        user.delete_user = delete_user
        
        await self.db.commit()
        return True
    
    async def enable_user(self, user_id: str) -> bool:
        """Enable user"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.enable = True
        await self.db.commit()
        return True
    
    async def disable_user(self, user_id: str) -> bool:
        """Disable user"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.enable = False
        await self.db.commit()
        return True

