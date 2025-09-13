"""GitHub OAuth authentication - Simplified for Supabase integration"""

import httpx
from typing import Dict, Any, Optional, List
from app.utils.config import get_settings

class GitHubAuth:
    def __init__(self):
        self.settings = get_settings()
        self.client_id = self.settings.github_client_id
        self.client_secret = self.settings.github_client_secret
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Get GitHub OAuth authorization URL"""
        if not self.client_id:
            raise Exception("GitHub client ID not configured")
            
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.settings.github_redirect_uri,
            "scope": "user:email,repo",
            "state": state or ""
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://github.com/login/oauth/authorize?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        if not self.client_id or not self.client_secret:
            raise Exception("GitHub OAuth credentials not configured")
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                },
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to exchange code for token: {response.text}")
            
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from GitHub"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get user info: {response.text}")
            
            return response.json()
    
    async def get_user_repos(self, access_token: str, per_page: int = 30) -> List[Dict[str, Any]]:
        """Get user's repositories"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/user/repos",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                params={"per_page": per_page, "sort": "updated"}
            )
            
            if response.status_code != 200:
                return []
            
            return response.json()

github_auth = GitHubAuth()