"""Configuration settings for the application"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # API Settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    environment: str = "development"
    log_level: str = "INFO"
    
    # OpenAI Settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    
    # Supabase Settings
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_service_key: Optional[str] = None  # Added missing field
    supabase_jwt_secret: Optional[str] = None
    
    # GitHub OAuth Settings
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None
    github_redirect_uri: str = "http://localhost:3000/auth/callback"
    
    # JWT Settings - Added missing fields
    jwt_secret_key: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    
    # Database Settings
    database_url: Optional[str] = None
    
    # Redis Settings - Added missing field
    redis_url: Optional[str] = None
    
    # Security Settings
    secret_key: str = "scgbkwlhe8734569ytincldjkasb()(_*(&^&%^%%)_)__()&YY^GFYUGHBUTYR@$%^^R"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # File Upload Settings - Added missing fields
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: str = ".py,.js,.ts,.java,.go,.cpp,.cs,.zip,.tar,.gz"
    
    # Analysis Settings - Added missing fields
    max_files_per_analysis: int = 1000
    analysis_timeout: int = 300  # 5 minutes
    max_analysis_time: int = 300  # Added missing field
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # Allow extra fields to prevent validation errors
        extra = "ignore"  # This will ignore extra fields instead of raising errors

    def __post_init__(self):
        """Validate required settings"""
        if not self.openai_api_key:
            print("⚠️  Warning: OPENAI_API_KEY not set")
        if not self.supabase_url or not self.supabase_key:
            print("⚠️  Warning: Supabase credentials not set")
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get allowed extensions as a list"""
        return [ext.strip() for ext in self.allowed_extensions.split(',')]

_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.__post_init__()
    return _settings