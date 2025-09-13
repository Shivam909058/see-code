"""Enhanced analysis data models with advanced features"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class IssueSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class IssueCategory(str, Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    COMPLEXITY = "complexity"
    DUPLICATION = "duplication"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    MAINTAINABILITY = "maintainability"
    STYLE = "style"
    ARCHITECTURE = "architecture"
    DEPENDENCIES = "dependencies"

class CodeIssue(BaseModel):
    id: Optional[str] = None  # FIXED: Make id optional
    category: IssueCategory
    severity: IssueSeverity
    title: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    line_range: Optional[tuple[int, int]] = None
    code_snippet: Optional[str] = None
    suggestion: str
    impact_score: float = Field(ge=0.0, le=10.0)
    confidence: float = Field(ge=0.0, le=1.0)
    rule_id: Optional[str] = None
    references: List[str] = []
    fix_complexity: str = "easy"  # easy, medium, hard
    estimated_fix_time: Optional[int] = None  # minutes

class DependencyInfo(BaseModel):
    name: str
    version: Optional[str] = None
    file_path: str
    is_direct: bool = True
    vulnerabilities: List[Dict[str, Any]] = []
    license: Optional[str] = None
    outdated: bool = False

class ArchitectureInsight(BaseModel):
    type: str  # "circular_dependency", "tight_coupling", "god_class", etc.
    description: str
    affected_files: List[str]
    severity: IssueSeverity
    suggestion: str

class LanguageStats(BaseModel):
    language: str
    files_count: int
    lines_of_code: int
    percentage: float
    complexity_score: float
    test_coverage: Optional[float] = None

class QualityMetrics(BaseModel):
    overall_score: float = Field(ge=0.0, le=100.0)
    maintainability_index: float
    cyclomatic_complexity: float
    test_coverage: Optional[float] = None
    code_duplication: float
    technical_debt_ratio: float
    security_score: float
    performance_score: float
    documentation_coverage: float
    dependency_health: float

class AnalysisRequest(BaseModel):
    repo_url: Optional[str] = None
    branch: str = "main"
    include_tests: bool = True
    include_docs: bool = True
    severity_threshold: IssueSeverity = IssueSeverity.LOW
    analysis_types: List[str] = ["all"]  # security, performance, complexity, etc.
    max_depth: int = 10  # for directory traversal

class AnalysisResponse(BaseModel):
    analysis_id: str
    timestamp: str
    user_id: Optional[str] = None
    repository_info: Dict[str, Any]
    quality_metrics: QualityMetrics
    language_stats: List[LanguageStats]
    issues: List[CodeIssue]
    dependencies: List[DependencyInfo]
    architecture_insights: List[ArchitectureInsight]
    summary: str
    recommendations: List[str]
    processing_time: float
    files_analyzed: int
    lines_analyzed: int

class QARequest(BaseModel):
    question: str
    analysis_id: Optional[str] = None
    context: Optional[str] = None
    conversation_history: List[Dict[str, str]] = []
    include_code_examples: bool = True

class QAResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[str] = []
    code_examples: List[Dict[str, str]] = []
    follow_up_questions: List[str] = []
    reasoning_steps: List[str] = []

# Authentication Models
class UserCreate(BaseModel):
    email: str
    password: str
    github_username: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    github_username: Optional[str] = None
    created_at: datetime
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class GitHubAuthRequest(BaseModel):
    code: str
    state: Optional[str] = None