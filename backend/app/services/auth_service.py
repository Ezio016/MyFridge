"""Authentication service with JWT and password hashing."""
import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..models import User, UserFlavorProfile
from ..schemas import UserRegister, TokenData

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # The JWT "sub" claim must be a string per RFC 7519 (python-jose
        # enforces this), so it is stored as a string and cast back to int here.
        sub = payload.get("sub")
        email: str = payload.get("email")
        
        if sub is None:
            return None
        
        try:
            user_id = int(sub)
        except (TypeError, ValueError):
            return None
        
        return TokenData(user_id=user_id, email=email)
    except JWTError:
        return None


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password."""
    user = get_user_by_email(db, email)
    
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    
    return user


def create_user(db: Session, user_data: UserRegister) -> User:
    """Create a new user."""
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise ValueError("User with this email already exists")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        name=user_data.name,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create initial flavor profile
    flavor_profile = UserFlavorProfile(user_id=db_user.id)
    db.add(flavor_profile)
    db.commit()
    
    return db_user


def create_token_for_user(user: User) -> str:
    """Create access token for a user."""
    access_token = create_access_token(
        # "sub" must be a string per RFC 7519 / python-jose validation.
        data={"sub": str(user.id), "email": user.email}
    )
    return access_token
