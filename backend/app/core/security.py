"""
Security authentication utilities
"""
from datetime import datetime, timedelta
from typing import Optional, Any
from jose import JWTError, jwt
import bcrypt
from app.core.config import settings

# JWT configuration
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token
    
    Args:
        data: Data to encode
        expires_delta: Expiration time delta
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode JWT access token
    
    Args:
        token: JWT token
        
    Returns:
        Optional[dict]: Decoded data or None on failure
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> Optional[Any]:
    """
    Verify and return data from token
    
    Args:
        token: JWT token
        
    Returns:
        Optional[Any]: User ID from token or None
    """
    payload = decode_access_token(token)
    if payload is None:
        return None
    return payload.get("sub")
