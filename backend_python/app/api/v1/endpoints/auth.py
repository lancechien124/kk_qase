"""
Authentication Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.core.database import get_db
from app.core.config import settings
from app.core.redis import redis_client
from app.schemas.auth import Token, UserLogin
from app.services.auth_service import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    response: Response = None,
    db: AsyncSession = Depends(get_db),
):
    """User login"""
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create session
    session_id = await auth_service.create_session(user)
    
    # Create JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email, "user_id": user.id, "session_id": session_id},
        expires_delta=access_token_expires,
    )
    
    # Set session cookie (optional)
    if response:
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            max_age=settings.SESSION_TIMEOUT,
            samesite="lax"
        )
    
    return {"access_token": access_token, "token_type": "bearer", "session_id": session_id}


@router.get("/me")
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Get current user information"""
    auth_service = AuthService(db)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("user_id")
        session_id: str = payload.get("session_id")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Try to get user from session cache first
        if session_id:
            session_user = await auth_service.get_session_user(session_id)
            if session_user:
                return session_user
        
        # Fallback to database
        user = await auth_service.get_user_with_cache(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "language": user.language,
            "last_organization_id": user.last_organization_id,
            "last_project_id": user.last_project_id,
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    response: Response = None,
    db: AsyncSession = Depends(get_db),
):
    """User logout"""
    auth_service = AuthService(db)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        session_id: str = payload.get("session_id")
        
        if session_id:
            await auth_service.delete_session(session_id)
        
        # Clear session cookie
        if response:
            response.delete_cookie(key="session_id")
        
        return {"message": "Logged out successfully"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

