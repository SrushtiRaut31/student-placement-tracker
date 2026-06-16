# Student Placement Tracker - Authentication Module
# Handles JWT token generation, verification, and dependency injection

import jwt
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
import os

# ============================================================================
# JWT CONFIGURATION
# ============================================================================
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key_change_this_in_production')
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_HOURS = int(os.getenv('JWT_EXP_DELTA_HOURS', '24'))

# HTTPBearer security scheme for Swagger UI ("Authorize" button)
security_scheme = HTTPBearer(auto_error=False)


def generate_jwt_token(user_id: int) -> str:
    """
    Generate a JWT token for the given user ID.
    Token expires after JWT_EXP_DELTA_HOURS.
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXP_DELTA_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> Optional[int]:
    """
    Decode a JWT token and return the user_id.
    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user_from_session(request: Request):
    """
    Extract user info from session for HTML template routes.
    Returns (user_id, user_name) tuple. Both are None if not authenticated.
    """
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    if user_id is None:
        return None, None
    return user_id, user_name


def login_required_api(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """
    FastAPI dependency for protecting API routes.
    Extracts and verifies JWT from the HTTP Bearer token (via Swagger or direct header).
    Returns the authenticated user_id.
    Raises 401 HTTPException if authentication fails.
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail='Authentication token required')

    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail='Authentication token required')

    user_id = decode_jwt_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail='Invalid or expired token')

    return user_id
