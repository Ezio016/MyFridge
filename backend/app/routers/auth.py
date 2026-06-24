"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import UserRegister, UserLogin, Token, UserResponse
from ..services.auth_service import (
    create_user, authenticate_user, create_token_for_user,
    decode_token, get_user_by_id
)
from ..models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User | None:
    """Get current authenticated user from JWT token."""
    if not token:
        return None
    
    token_data = decode_token(token)
    if not token_data or not token_data.user_id:
        return None
    
    user = get_user_by_id(db, token_data.user_id)
    if not user or not user.is_active:
        return None
    
    return user


async def get_current_user_required(
    user: User | None = Depends(get_current_user)
) -> User:
    """Require authenticated user."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        user = create_user(db, user_data)
        access_token = create_token_for_user(user)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                created_at=user.created_at,
                is_active=user.is_active
            )
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login with email and password."""
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_token_for_user(user)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            is_active=user.is_active
        )
    )


@router.post("/login/json", response_model=Token)
async def login_json(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login with JSON body (alternative to form)."""
    user = authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_token_for_user(user)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            is_active=user.is_active
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user_required)):
    """Get current user's profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at,
        is_active=current_user.is_active
    )


@router.get("/verify")
async def verify_token(current_user: User = Depends(get_current_user)):
    """Verify if token is valid."""
    if current_user:
        return {"valid": True, "user_id": current_user.id}
    return {"valid": False}
