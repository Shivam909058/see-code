

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
from typing import Optional
import jwt
from datetime import datetime, timedelta
from urllib.parse import urlencode
from pydantic import BaseModel
from loguru import logger
from app.models.analysis import UserCreate, UserResponse, Token, GitHubAuthRequest
from app.auth.supabase_client import supabase_client
from app.auth.github_auth import github_auth
from app.utils.config import get_settings
router = APIRouter(tags=["authentication"])
security = HTTPBearer()
settings = get_settings()

class TokenVerificationRequest(BaseModel):
    token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

# Define get_current_user FIRST before it's used
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current user from token"""
    try:
        token = credentials.credentials
        user_data = await supabase_client.get_user(token)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Optional version for endpoints that don't require auth
async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))) -> Optional[dict]:
    """Get current user from token (optional)"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_data = await supabase_client.get_user(token)
        return user_data
    except Exception as e:
        logger.warning(f"Optional authentication failed: {str(e)}")
        return None

# Now define the routes
@router.get("/oauth/github")
async def github_oauth():
    """Initiate GitHub OAuth flow"""
    try:
        oauth_url = supabase_client.get_oauth_url("github", "http://localhost:3000/auth/callback")
        if not oauth_url:
            raise HTTPException(status_code=500, detail="Failed to generate OAuth URL")
        
        return RedirectResponse(url=oauth_url)
    except Exception as e:
        logger.error(f"GitHub OAuth error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"GitHub OAuth failed: {str(e)}")

@router.post("/callback")
async def auth_callback(request: Request):
    """Handle OAuth callback"""
    try:
        body = await request.json()
        code = body.get("code")
        
        if not code:
            raise HTTPException(status_code=400, detail="No authorization code provided")
        
        # Exchange code for session
        session_data = await supabase_client.exchange_code_for_session(code)
        
        if not session_data:
            raise HTTPException(status_code=400, detail="Failed to exchange code for session")
        
        return {
            "access_token": session_data["session"].access_token,
            "token_type": "bearer",
            "user": {
                "id": session_data["user"].id,
                "email": session_data["user"].email,
                "github_username": session_data["user"].user_metadata.get("user_name"),
                "full_name": session_data["user"].user_metadata.get("full_name"),
                "avatar_url": session_data["user"].user_metadata.get("avatar_url"),
                "created_at": session_data["user"].created_at.isoformat() if session_data["user"].created_at else None,
                "is_active": True
            }
        }
    except Exception as e:
        logger.error(f"Auth callback error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@router.post("/verify-token")
async def verify_supabase_token(request: TokenVerificationRequest):
    """Verify Supabase token and return user info"""
    try:
        logger.info(f"Verifying token: {request.token[:20]}...")
        
        # Get user data from Supabase
        user_data = await supabase_client.get_user(request.token)
        
        if not user_data:
            logger.error("Token verification failed - no user data returned")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        logger.info(f"Token verification successful for user: {user_data.get('email')}")
        
        return {
            "user": user_data,
            "token": request.token
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {"user": current_user}

@router.post("/github")
async def github_auth_endpoint(request: GitHubAuthRequest):
    """GitHub OAuth authentication"""
    try:
        # Exchange authorization code for access token
        token_data = await github_auth.exchange_code_for_token(request.code)
        
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code"
            )
        
        # Get user info from GitHub
        user_info = await github_auth.get_user_info(token_data["access_token"])
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user information from GitHub"
            )
        
        # Create or update user in our system
        user_data = {
            "email": user_info["email"],
            "github_username": user_info["login"],
            "full_name": user_info.get("name", ""),
            "avatar_url": user_info.get("avatar_url", ""),
            "github_id": user_info["id"]
        }
        
        # Generate JWT token for our system
        token_payload = {
            "sub": str(user_info["id"]),
            "email": user_info["email"],
            "github_username": user_info["login"],
            "exp": datetime.utcnow() + timedelta(days=30)
        }
        
        token = jwt.encode(token_payload, settings.secret_key, algorithm="HS256")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitHub authentication failed: {str(e)}"
        )

@router.post("/debug-token")
async def debug_token_verification(request: TokenVerificationRequest):
    """Debug endpoint to check token verification"""
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {request.token}",
                "apikey": settings.supabase_key,
                "Content-Type": "application/json"
            }
            
            response = await client.get(
                f"{settings.supabase_url}/auth/v1/user",
                headers=headers,
                timeout=10.0
            )
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text,
                "supabase_url": settings.supabase_url,
                "has_supabase_key": bool(settings.supabase_key)
            }
            
    except Exception as e:
        return {"error": str(e)}

