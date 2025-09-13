"""
File handling utilities for code analysis
- File upload processing
- GitHub repository cloning
- Temporary directory management
- File validation and sanitization
"""

import os
import tempfile
import shutil
import zipfile
import tarfile
import asyncio
import aiofiles
from pathlib import Path
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
import git
from git import Repo
from fastapi import UploadFile
from loguru import logger

from app.utils.config import get_settings

class FileHandler:
    """Handle file operations for code analysis"""
    
    def __init__(self):
        self.settings = get_settings()
        self.supported_archives = {'.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2'}
        self.max_file_size = self.settings.max_file_size
        self.max_files = self.settings.max_files_per_analysis
        
        # Directories to skip during extraction
        self.skip_dirs = {
            '.git', '.svn', '.hg', '.bzr',
            'node_modules', '__pycache__', '.pytest_cache',
            'venv', 'env', '.env', 'virtualenv',
            'build', 'dist', 'target', 'bin', 'obj',
            '.idea', '.vscode', '.vs',
            'coverage', '.coverage', '.nyc_output',
            'logs', 'log', 'tmp', 'temp'
        }
    
    async def handle_uploaded_files(self, files: List[UploadFile]) -> str:
        """Process uploaded files and return temporary directory path"""
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="code_analysis_")
            logger.info(f"Created temporary directory: {temp_dir}")
            
            total_files = 0
            
            for upload_file in files:
                if not upload_file.filename:
                    continue
                
                # Validate file size
                content = await upload_file.read()
                if len(content) > self.max_file_size:
                    logger.warning(f"File {upload_file.filename} too large: {len(content)} bytes")
                    continue
                
                # Reset file pointer
                await upload_file.seek(0)
                
                file_path = Path(temp_dir) / upload_file.filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Check if it's an archive
                if self._is_archive(upload_file.filename):
                    extracted_files = await self._extract_archive(upload_file, temp_dir)
                    total_files += extracted_files
                else:
                    # Save individual file
                    async with aiofiles.open(file_path, 'wb') as f:
                        content = await upload_file.read()
                        await f.write(content)
                    total_files += 1
                
                if total_files > self.max_files:
                    logger.warning(f"Too many files: {total_files}, limit: {self.max_files}")
                    break
            
            logger.info(f"Processed {total_files} files in {temp_dir}")
            return temp_dir
            
        except Exception as e:
            logger.error(f"Failed to handle uploaded files: {str(e)}")
            if 'temp_dir' in locals():
                await self.cleanup_temp_dir(temp_dir)
            raise
    
    async def clone_repository(self, repo_url: str, branch: str = "main") -> str:
        """Clone a GitHub repository to temporary directory"""
        try:
            # Validate repository URL
            if not self._is_valid_repo_url(repo_url):
                raise ValueError(f"Invalid repository URL: {repo_url}")
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="repo_analysis_")
            logger.info(f"Cloning repository {repo_url} to {temp_dir}")
            
            # Clone repository
            try:
                repo = Repo.clone_from(repo_url, temp_dir, branch=branch, depth=1)
                logger.info(f"Successfully cloned repository: {repo_url}")
            except git.exc.GitCommandError as e:
                # Try with default branch if specified branch fails
                if branch != "main":
                    logger.warning(f"Branch {branch} not found, trying default branch")
                    repo = Repo.clone_from(repo_url, temp_dir, depth=1)
                else:
                    raise ValueError(f"Failed to clone repository: {str(e)}")
            
            # Remove .git directory to save space
            git_dir = Path(temp_dir) / '.git'
            if git_dir.exists():
                shutil.rmtree(git_dir)
            
            # Validate repository size
            total_size = self._calculate_directory_size(temp_dir)
            if total_size > self.max_file_size * 10:  # 10x individual file limit
                raise ValueError(f"Repository too large: {total_size} bytes")
            
            return temp_dir
            
        except Exception as e:
            logger.error(f"Failed to clone repository: {str(e)}")
            if 'temp_dir' in locals():
                await self.cleanup_temp_dir(temp_dir)
            raise
    
    async def _extract_archive(self, upload_file: UploadFile, temp_dir: str) -> int:
        """Extract archive file to temporary directory"""
        try:
            # Save archive to temporary file
            archive_path = Path(temp_dir) / upload_file.filename
            
            async with aiofiles.open(archive_path, 'wb') as f:
                content = await upload_file.read()
                await f.write(content)
            
            extracted_files = 0
            
            # Extract based on file type
            if upload_file.filename.endswith('.zip'):
                extracted_files = await self._extract_zip(archive_path, temp_dir)
            elif any(upload_file.filename.endswith(ext) for ext in ['.tar', '.tar.gz', '.tgz', '.tar.bz2']):
                extracted_files = await self._extract_tar(archive_path, temp_dir)
            
            # Remove archive file
            os.unlink(archive_path)
            
            return extracted_files
            
        except Exception as e:
            logger.error(f"Failed to extract archive {upload_file.filename}: {str(e)}")
            return 0
    
    async def _extract_zip(self, archive_path: Path, temp_dir: str) -> int:
        """Extract ZIP archive"""
        extracted_files = 0
        
        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                for member in zip_ref.infolist():
                    # Skip directories and hidden files
                    if member.is_dir() or member.filename.startswith('.'):
                        continue
                    
                    # Skip files in ignored directories
                    if any(skip_dir in member.filename for skip_dir in self.skip_dirs):
                        continue
                    
                    # Validate file size
                    if member.file_size > self.max_file_size:
                        logger.warning(f"Skipping large file: {member.filename}")
                        continue
                    
                    # Extract file
                    try:
                        zip_ref.extract(member, temp_dir)
                        extracted_files += 1
                        
                        if extracted_files > self.max_files:
                            logger.warning(f"Reached maximum files limit: {self.max_files}")
                            break
                            
                    except Exception as e:
                        logger.warning(f"Failed to extract {member.filename}: {str(e)}")
                        continue
            
            return extracted_files
            
        except Exception as e:
            logger.error(f"Failed to extract ZIP archive: {str(e)}")
            return 0
    
    async def _extract_tar(self, archive_path: Path, temp_dir: str) -> int:
        """Extract TAR archive"""
        extracted_files = 0
        
        try:
            # Determine compression mode
            if archive_path.name.endswith('.tar.gz') or archive_path.name.endswith('.tgz'):
                mode = 'r:gz'
            elif archive_path.name.endswith('.tar.bz2'):
                mode = 'r:bz2'
            else:
                mode = 'r'
            
            with tarfile.open(archive_path, mode) as tar_ref:
                for member in tar_ref.getmembers():
                    # Skip directories and hidden files
                    if member.isdir() or member.name.startswith('.'):
                        continue
                    
                    # Skip files in ignored directories
                    if any(skip_dir in member.name for skip_dir in self.skip_dirs):
                        continue
                    
                    # Validate file size
                    if member.size > self.max_file_size:
                        logger.warning(f"Skipping large file: {member.name}")
                        continue
                    
                    # Extract file
                    try:
                        tar_ref.extract(member, temp_dir)
                        extracted_files += 1
                        
                        if extracted_files > self.max_files:
                            logger.warning(f"Reached maximum files limit: {self.max_files}")
                            break
                            
                    except Exception as e:
                        logger.warning(f"Failed to extract {member.name}: {str(e)}")
                        continue
            
            return extracted_files
            
        except Exception as e:
            logger.error(f"Failed to extract TAR archive: {str(e)}")
            return 0
    
    async def cleanup_temp_dir(self, temp_dir: str):
        """Clean up temporary directory"""
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.error(f"Failed to cleanup temporary directory {temp_dir}: {str(e)}")
    
    def _is_archive(self, filename: str) -> bool:
        """Check if file is a supported archive"""
        return any(filename.lower().endswith(ext) for ext in self.supported_archives)
    
    def _is_valid_repo_url(self, url: str) -> bool:
        """Validate GitHub repository URL"""
        try:
            parsed = urlparse(url)
            
            # Check if it's a GitHub URL
            if parsed.netloc not in ['github.com', 'www.github.com']:
                return False
            
            # Check path format
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) < 2:
                return False
            
            # Remove .git suffix if present
            if path_parts[-1].endswith('.git'):
                path_parts[-1] = path_parts[-1][:-4]
            
            return True
            
        except Exception:
            return False
    
    def _calculate_directory_size(self, directory: str) -> int:
        """Calculate total size of directory"""
        total_size = 0
        
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, IOError):
                    continue
        
        return total_size
    
    async def get_repository_info(self, repo_url: str) -> Dict[str, Any]:
        """Get repository information from GitHub API"""
        try:
            # Extract owner and repo name from URL
            parsed = urlparse(repo_url)
            path_parts = parsed.path.strip('/').split('/')
            
            if len(path_parts) < 2:
                return {}
            
            owner = path_parts[0]
            repo_name = path_parts[1]
            
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            
            # Make API request (would need GitHub token for higher rate limits)
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo_name}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    repo_data = response.json()
                    return {
                        'name': repo_data.get('name'),
                        'full_name': repo_data.get('full_name'),
                        'description': repo_data.get('description'),
                        'language': repo_data.get('language'),
                        'stars': repo_data.get('stargazers_count'),
                        'forks': repo_data.get('forks_count'),
                        'size': repo_data.get('size'),
                        'default_branch': repo_data.get('default_branch'),
                        'created_at': repo_data.get('created_at'),
                        'updated_at': repo_data.get('updated_at'),
                        'license': repo_data.get('license', {}).get('name') if repo_data.get('license') else None
                    }
                else:
                    logger.warning(f"GitHub API request failed: {response.status_code}")
                    return {}
                    
        except Exception as e:
            logger.warning(f"Failed to get repository info: {str(e)}")
            return {}


