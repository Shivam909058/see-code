"""Supabase client and authentication"""

from supabase import create_client, Client
from app.utils.config import get_settings
import asyncio
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode
import httpx
from loguru import logger

class SupabaseClient:
    def __init__(self):
        settings = get_settings()
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
        self.settings = settings
    
    async def create_user(self, email: str, password: str, metadata: Optional[Dict] = None) -> Dict:
        """Create a new user"""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": metadata or {}}
            })
            return response.user
        except Exception as e:
            logger.error(f"User creation error: {str(e)}")
            raise
    
    async def sign_in(self, email: str, password: str) -> Dict:
        """Sign in user"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {
                "user": response.user,
                "session": response.session
            }
        except Exception as e:
            logger.error(f"Sign in error: {str(e)}")
            raise
    
    async def sign_out(self) -> None:
        """Sign out user"""
        try:
            self.client.auth.sign_out()
        except Exception as e:
            logger.error(f"Sign out error: {str(e)}")
            raise
    
    async def get_user(self, access_token: str) -> Optional[Dict]:
        """Get user by access token"""
        try:
            logger.info(f"Attempting to get user with token: {access_token[:50]}...")
            
            # Set the token for the client
            self.client.postgrest.auth(access_token)
            
            # Get user from Supabase
            user_response = self.client.auth.get_user(access_token)
            
            logger.info(f"Supabase get_user response: {user_response}")
            
            if user_response and user_response.user:
                user = user_response.user
                return {
                    "id": str(user.id),
                    "email": user.email,
                    "github_username": user.user_metadata.get("user_name") or user.user_metadata.get("preferred_username"),
                    "created_at": str(user.created_at),
                    "is_active": True
                }
            return None
            
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return None
    
    async def save_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Save analysis results to database"""
        try:
            # Validate and clean the status value - FIXED: Use correct database values
            status = analysis_data.get("status", "pending")
            if status not in ["pending", "processing", "completed", "failed"]:
                status = "pending"
            
            # Map application status to database status if needed
            status_mapping = {
                "running": "processing",  # Map 'running' to 'processing'
                "pending": "pending",
                "processing": "processing", 
                "completed": "completed",
                "failed": "failed"
            }
            status = status_mapping.get(status, "pending")
            
            # Validate and clean the type value  
            analysis_type = analysis_data.get("type", "upload")
            if analysis_type not in ["github", "upload"]:  # Database only allows these two
                analysis_type = "upload"
            
            # Ensure all required fields are present with correct types
            analysis_record = {
                "user_id": str(analysis_data.get("user_id")),
                "name": str(analysis_data.get("name", "Untitled Analysis")),
                "type": analysis_type,
                "repository_url": analysis_data.get("repository_url"),
                "repository_info": analysis_data.get("repository_info", {}),
                "quality_metrics": analysis_data.get("quality_metrics", {}),
                "language_stats": analysis_data.get("language_stats", []),
                "issues": analysis_data.get("issues", []),
                "dependencies": analysis_data.get("dependencies", []),
                "architecture_insights": analysis_data.get("architecture_insights", []),
                "summary": str(analysis_data.get("summary", "")),
                "recommendations": analysis_data.get("recommendations", []),
                "processing_time": float(analysis_data.get("processing_time", 0.0)),
                "files_analyzed": int(analysis_data.get("files_analyzed", 0)),
                "lines_analyzed": int(analysis_data.get("lines_analyzed", 0)),
                "issues_count": int(analysis_data.get("issues_count", 0)),
                "status": status  # Use the validated status
            }
            
            logger.info(f"Saving analysis record with status: {status}, type: {analysis_type}")
            
            response = self.client.table('analyses').insert(analysis_record).execute()
            
            if response.data and len(response.data) > 0:
                analysis_id = response.data[0]['id']
                logger.info(f"Analysis saved successfully with ID: {analysis_id}")
                return analysis_id
            else:
                raise Exception("No data returned from insert")
                
        except Exception as e:
            logger.error(f"Failed to save analysis: {str(e)}")
            raise Exception(f"Failed to save analysis: {str(e)}")
    
    async def update_analysis(self, analysis_id: str, update_data: Dict[str, Any]) -> bool:
        """Update analysis record"""
        try:
            # Clean the status if it's being updated - FIXED: Use correct database values
            if "status" in update_data:
                status = update_data["status"]
                
                # Map application status to database status
                status_mapping = {
                    "running": "processing",  # Map 'running' to 'processing'
                    "pending": "pending",
                    "processing": "processing", 
                    "completed": "completed",
                    "failed": "failed"
                }
                
                if status in status_mapping:
                    update_data["status"] = status_mapping[status]
                else:
                    update_data["status"] = "completed"  # Default fallback
            
            # Ensure proper data types for numeric fields
            if "processing_time" in update_data:
                update_data["processing_time"] = float(update_data["processing_time"])
            if "files_analyzed" in update_data:
                update_data["files_analyzed"] = int(update_data["files_analyzed"])
            if "lines_analyzed" in update_data:
                update_data["lines_analyzed"] = int(update_data["lines_analyzed"])
            if "issues_count" in update_data:
                update_data["issues_count"] = int(update_data["issues_count"])
            
            # Add updated_at timestamp
            update_data["updated_at"] = "now()"
            
            logger.info(f"Updating analysis {analysis_id} with status: {update_data.get('status', 'no status change')}")
            
            response = self.client.table('analyses').update(update_data).eq('id', analysis_id).execute()
            
            if response.data:
                logger.info(f"Analysis {analysis_id} updated successfully")
                return True
            else:
                logger.warning(f"No data returned when updating analysis {analysis_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update analysis {analysis_id}: {str(e)}")
            return False
    
    async def get_analysis(self, analysis_id: str) -> Optional[Dict]:
        """Get analysis by ID"""
        try:
            response = self.client.table('analyses').select('*').eq('id', analysis_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Failed to get analysis {analysis_id}: {str(e)}")
            return None
    
    async def get_user_analyses(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Get user's analyses"""
        try:
            response = (self.client.table('analyses')
                       .select('*')
                       .eq('user_id', user_id)
                       .order('created_at', desc=True)
                       .range(offset, offset + limit - 1)
                       .execute())
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Failed to get user analyses: {str(e)}")
            return []
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """Delete analysis"""
        try:
            response = self.client.table('analyses').delete().eq('id', analysis_id).execute()
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete analysis {analysis_id}: {str(e)}")
            return False
    
    async def save_qa_session(self, session_data: Dict[str, Any]) -> str:
        """Save Q&A session"""
        try:
            session_record = {
                "analysis_id": session_data.get("analysis_id"),
                "user_id": str(session_data.get("user_id")),
                "question": str(session_data.get("question", "")),
                "answer": str(session_data.get("answer", "")),
                "confidence": float(session_data.get("confidence", 0.0)),
                "context": session_data.get("context")
            }
            
            response = self.client.table('analysis_sessions').insert(session_record).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]['id']
            else:
                raise Exception("No data returned from Q&A session insert")
                
        except Exception as e:
            logger.error(f"Failed to save Q&A session: {str(e)}")
            raise Exception(f"Failed to save Q&A session: {str(e)}")

# Create global instance
supabase_client = SupabaseClient()
