# 🚀 Quantum Code Inspector

**An AI-Powered Code Quality Intelligence Agent**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> Transform your codebase analysis with AI-powered insights, intelligent Q&A, and actionable recommendations.

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [💻 Usage](#-usage)
- [🔧 Configuration](#-configuration)
- [🌐 Web Interface](#-web-interface)
- [🤖 AI Agent Capabilities](#-ai-agent-capabilities)
- [📊 Analysis Categories](#-analysis-categories)
- [🛠️ Development](#️-development)
- [🔌 API Reference](#-api-reference)
- [🎥 Demo Video](#-demo-video)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🎯 Overview

Quantum Code Inspector is an advanced AI-powered code quality analysis platform that goes beyond traditional linting tools. It combines multiple analysis techniques including AST parsing, security scanning, performance profiling, and LLM-powered insights to provide comprehensive, actionable feedback on your codebase.

### 🌟 What Makes It Special

- **🧠 AI-Powered Analysis**: Uses GPT-4 for intelligent code understanding and contextual recommendations
- **🔍 Multi-Language Support**: Analyzes Python, JavaScript, TypeScript, Java, Go, C++, and more
- **💬 Interactive Q&A**: Ask natural language questions about your codebase
- **🌐 Web & CLI Interface**: Use via command line or beautiful web interface
- **🔒 Security First**: Comprehensive security vulnerability detection
- **📊 Visual Reports**: Rich, interactive reports with charts and insights
- **🚀 RAG Implementation**: Handles large codebases with vector embeddings
- **🔧 Extensible**: Modular architecture for easy customization

## ✨ Key Features

### 🎯 Core Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| **Multi-Language Analysis** | Python, JS/TS, Java, Go, C++, C# | ✅ |
| **Security Scanning** | Bandit, Semgrep, custom patterns | ✅ |
| **Performance Analysis** | Bottleneck detection, optimization suggestions | ✅ |
| **Code Complexity** | Cyclomatic, cognitive complexity analysis | ✅ |
| **Duplication Detection** | Exact and similar code block identification | ✅ |
| **AST Parsing** | Deep structural analysis with Tree-sitter | ✅ |
| **AI-Powered Insights** | LLM-generated recommendations | ✅ |
| **Interactive Q&A** | Natural language codebase queries | ✅ |

### 🌐 Deployment Options

| Platform | Features | Status |
|----------|----------|--------|
| **CLI Tool** | `quantum-inspector analyze <path>` | ✅ |
| **Web Interface** | React-based dashboard | ✅ |
| **GitHub Integration** | Direct repository analysis | ✅ |
| **API Access** | RESTful API endpoints | ✅ |
| **Docker Support** | Containerized deployment | ✅ |

### 🔍 Advanced Features

- **RAG Implementation**: Vector embeddings for large codebase analysis
- **Severity Scoring**: Intelligent issue prioritization
- **Dependency Analysis**: Vulnerability scanning for packages
- **Architecture Insights**: Code structure and relationship mapping
- **Real-time Analysis**: Background processing with status updates
- **Export Capabilities**: JSON, Markdown, PDF reports

## 🏗️ Architecture

### 🎨 System Design

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   AI Services   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (OpenAI)      │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • Analysis API  │    │ • GPT-4 Agent   │
│ • File Upload   │    │ • Q&A System    │    │ • Embeddings    │
│ • GitHub Login  │    │ • Auth System   │    │ • RAG Pipeline  │
│ • Reports       │    │ • Background    │    │                 │
│ • Interactive   │    │   Tasks         │    │                 │
│   Q&A           │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   Data Layer    │              │
         └──────────────►│                 │◄─────────────┘
                        │ • Supabase DB   │
                        │ • ChromaDB      │
                        │ • File Storage  │
                        │ • Vector Store  │
                        └─────────────────┘
```

### 🧩 Component Architecture

#### Backend Services
- **Quality Agent**: AI-powered analysis orchestrator
- **Security Analyzer**: Multi-tool security scanning (Bandit, Semgrep)
- **Performance Analyzer**: Bottleneck and optimization detection
- **Complexity Analyzer**: Cyclomatic and cognitive complexity
- **Duplication Analyzer**: Code similarity detection
- **AST Analyzer**: Deep structural analysis
- **Code Parser**: Multi-language file parsing with Tree-sitter

#### Frontend Components
- **Analysis Dashboard**: Central control panel
- **Report Viewer**: Interactive analysis results
- **Q&A Interface**: Conversational code exploration
- **GitHub Integration**: Repository analysis
- **File Uploader**: Local file analysis
- **User Management**: Authentication and profiles

#### AI & ML Pipeline
- **LLM Integration**: GPT-4 for intelligent analysis
- **Vector Embeddings**: ChromaDB for RAG implementation
- **Context Management**: Conversation memory and state
- **Prompt Engineering**: Optimized prompts for code analysis

## 🚀 Quick Start

### ⚡ 1-Minute Setup

```bash
# Clone the repository
git clone https://github.com/your-repo/quantum-code-inspector.git
cd quantum-code-inspector

# Set up environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Install and run
docker-compose up -d

# Or run locally:
# Backend
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload

# Frontend  
cd frontend && npm install && npm run dev

# CLI Usage
quantum-inspector analyze your-code-directory
```

### 🎯 First Analysis

```bash
# Analyze a Python file
quantum-inspector analyze test.py

# Analyze entire project
quantum-inspector analyze /path/to/your/project

# GitHub repository analysis
quantum-inspector analyze-repo https://github.com/user/repo

# Interactive Q&A
quantum-inspector ask /path/to/code -q "What are the main security issues?"
```

## 📦 Installation

### 🐳 Docker Installation (Recommended)

```bash
# Clone repository
git clone https://github.com/your-repo/quantum-code-inspector.git
cd quantum-code-inspector

# Configure environment
cp backend/.env.example backend/.env
# Edit with your configuration

# Start services
docker-compose up -d

# Access web interface
open http://localhost:3000
```

### 🔧 Local Development Setup

#### Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- OpenAI API Key
- Supabase Account (optional)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install CLI tool
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run database setup (if using Supabase)
python create_tables.py

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit with your settings

# Start development server
npm run dev

# Build for production
npm run build
```

#### CLI Installation

```bash
# Install CLI globally
cd backend
pip install -e .

# Verify installation
quantum-inspector --help
qci --version  # Short alias
```

## 💻 Usage

### 🖥️ Command Line Interface

#### Basic Analysis

```bash
# Analyze single file
quantum-inspector analyze app.py

# Analyze directory
quantum-inspector analyze ./src

# With output options
quantum-inspector analyze ./src --output report.json --format detailed

# Filter by severity
quantum-inspector analyze ./src --severity high --category security
```

#### Advanced Options

```bash
# GitHub repository analysis
quantum-inspector analyze-repo https://github.com/user/repo --branch main

# Interactive Q&A session
quantum-inspector ask ./src --question "What are the performance bottlenecks?"

# Configuration check
quantum-inspector config

# Help and documentation
quantum-inspector --help
quantum-inspector analyze --help
```

#### Output Formats

```bash
# Table format (default)
quantum-inspector analyze ./src

# Detailed report
quantum-inspector analyze ./src --format detailed

# JSON export
quantum-inspector analyze ./src --format json --output analysis.json

# Save results
quantum-inspector analyze ./src --output results.json
```

### 🌐 Web Interface Usage

#### Dashboard Features

1. **📁 File Upload**: Drag & drop files or folders
2. **🔗 GitHub Integration**: Analyze repositories directly
3. **📊 Interactive Reports**: Visual analysis results
4. **💬 Q&A Chat**: Ask questions about your code
5. **📈 History Tracking**: View past analyses
6. **👤 User Profiles**: Manage your account

#### Analysis Workflow

```
Upload Code → Processing → Results → Q&A → Export
     ↓            ↓          ↓        ↓       ↓
  Files/Repo → Background → Report → Chat → Download
              Analysis    Display  Interface
```

### 🤖 Interactive Q&A Examples

```bash
# Security questions
"What are the main security vulnerabilities in this codebase?"
"Are there any SQL injection risks?"
"Which files have hardcoded secrets?"

# Performance questions  
"What are the performance bottlenecks?"
"Which functions are most complex?"
"Are there any inefficient algorithms?"

# Architecture questions
"What is the overall structure of this codebase?"
"Which files are most coupled?"
"What are the main dependencies?"

# Code quality questions
"What are the highest priority issues to fix?"
"Which files need the most attention?"
"What are the best practices violations?"
```

## 🔧 Configuration

### 🔑 Environment Variables

#### Backend Configuration (`backend/.env`)

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.1

# Supabase Configuration (Optional)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# GitHub OAuth (Optional)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760  # 10MB
MAX_FILES_PER_ANALYSIS=100
ANALYSIS_TIMEOUT=600    # 10 minutes

# Security
JWT_SECRET=your-jwt-secret-key
CORS_ORIGINS=["http://localhost:3000"]

# Analysis Tools
ENABLE_BANDIT=true
ENABLE_SEMGREP=true
ENABLE_SAFETY=true
ENABLE_RAG=true
```

#### Frontend Configuration (`frontend/.env`)

```env
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Supabase (if using)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Features
VITE_ENABLE_GITHUB_LOGIN=true
VITE_ENABLE_FILE_UPLOAD=true
VITE_ENABLE_REPO_ANALYSIS=true
```

### ⚙️ Advanced Configuration

#### Analysis Customization

```python
# backend/app/utils/config.py
class Settings(BaseSettings):
    # Analysis thresholds
    complexity_threshold: int = 10
    duplication_threshold: float = 0.8
    security_severity_min: str = "medium"
    
    # Performance settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    batch_size: int = 50
    timeout: int = 600
    
    # LLM settings
    llm_temperature: float = 0.1
    max_tokens: int = 4000
    context_window: int = 8000
```

#### Tool Configuration

```yaml
# analysis-config.yaml
analyzers:
  security:
    enabled: true
    tools: ["bandit", "semgrep", "safety"]
    severity_threshold: "medium"
    
  performance:
    enabled: true
    check_loops: true
    check_io: true
    check_algorithms: true
    
  complexity:
    enabled: true
    cyclomatic_threshold: 10
    cognitive_threshold: 15
    
  duplication:
    enabled: true
    similarity_threshold: 0.8
    min_lines: 5
```

## 🌐 Web Interface

### 🎨 Features Overview

#### Dashboard Components

1. **📊 Analysis Overview**
   - Quality score visualization
   - Issue distribution charts
   - Language statistics
   - Processing status

2. **🔍 Issue Explorer**
   - Filterable issue list
   - Severity-based sorting
   - Category grouping
   - Code snippet preview

3. **💬 AI Chat Interface**
   - Natural language queries
   - Context-aware responses
   - Follow-up questions
   - Conversation history

4. **📈 Metrics & Insights**
   - Complexity trends
   - Security score tracking
   - Performance metrics
   - Technical debt analysis

#### User Experience Features

- **🌓 Dark/Light Mode**: Adaptive theming
- **📱 Responsive Design**: Mobile-friendly interface
- **⚡ Real-time Updates**: Live analysis progress
- **🔄 Auto-refresh**: Dynamic content updates
- **💾 Export Options**: Multiple format support
- **🔍 Advanced Search**: Intelligent filtering

### 🎯 Navigation Guide

```
Home → Login → Dashboard → Analysis → Results → Q&A → Export
  ↓      ↓        ↓         ↓         ↓        ↓      ↓
Landing  Auth   File/Repo  Process   Report   Chat   Download
 Page   Flow    Upload     Monitor   View    Interface
```

## 🤖 AI Agent Capabilities

### 🧠 Intelligence Features

#### Core AI Capabilities

- **🔍 Code Understanding**: Deep semantic analysis of code structure
- **💡 Contextual Recommendations**: Actionable improvement suggestions
- **🎯 Issue Prioritization**: Intelligent severity scoring
- **📚 Knowledge Integration**: Best practices and pattern recognition
- **🔄 Continuous Learning**: Adaptive analysis based on feedback

#### LLM Integration

```python
# Quality Intelligence Agent Architecture
class QualityIntelligenceAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4-turbo-preview")
        self.memory = ConversationBufferMemory()
        self.tools = [
            SecurityAnalyzer(),
            PerformanceAnalyzer(),
            ComplexityAnalyzer(),
            DuplicationAnalyzer(),
            ASTAnalyzer()
        ]
        self.vector_store = ChromaDB()
```

#### Analysis Workflow

1. **📥 Input Processing**: File parsing and preprocessing
2. **🔍 Multi-tool Analysis**: Parallel analyzer execution
3. **🤖 AI Enhancement**: LLM-powered insight generation
4. **📊 Result Synthesis**: Comprehensive report compilation
5. **💬 Interactive Q&A**: Conversational exploration

### 🎯 Specialized Agents

#### Security Agent
- Vulnerability pattern recognition
- OWASP Top 10 compliance checking
- Dependency vulnerability scanning
- Custom security rule creation

#### Performance Agent
- Bottleneck identification
- Algorithm efficiency analysis
- Resource usage optimization
- Scalability assessment

#### Architecture Agent
- Design pattern recognition
- Code smell detection
- Dependency analysis
- Refactoring suggestions

## 📊 Analysis Categories

### 🔒 Security Analysis

#### Vulnerability Detection

| Category | Tools Used | Severity Levels |
|----------|------------|-----------------|
| **SQL Injection** | Bandit, Semgrep, Custom | Critical |
| **XSS Vulnerabilities** | Semgrep, Pattern Matching | High |
| **Hardcoded Secrets** | Regex Patterns, AI Analysis | Critical |
| **Path Traversal** | Static Analysis, Patterns | High |
| **Command Injection** | Bandit, Custom Rules | Critical |
| **Weak Cryptography** | Bandit, Best Practices | Medium |
| **Insecure Dependencies** | Safety, Audit Tools | Variable |

#### Security Metrics

```python
SecurityMetrics = {
    "vulnerability_count": int,
    "severity_distribution": Dict[str, int],
    "owasp_coverage": float,
    "dependency_vulnerabilities": int,
    "security_score": float  # 0-100
}
```

### ⚡ Performance Analysis

#### Performance Categories

| Issue Type | Detection Method | Impact |
|------------|------------------|--------|
| **Inefficient Loops** | AST Analysis | High |
| **N+1 Queries** | Pattern Recognition | Critical |
| **Memory Leaks** | Static Analysis | High |
| **Synchronous I/O** | Code Pattern Detection | Medium |
| **Algorithm Complexity** | Big-O Analysis | Variable |
| **Resource Usage** | Profiling Simulation | Medium |

#### Performance Metrics

```python
PerformanceMetrics = {
    "bottleneck_count": int,
    "complexity_score": float,
    "optimization_opportunities": int,
    "estimated_improvement": float,
    "performance_score": float  # 0-100
}
```

### 🧠 Complexity Analysis

#### Complexity Types

- **Cyclomatic Complexity**: Decision point counting
- **Cognitive Complexity**: Human comprehension difficulty
- **Halstead Complexity**: Program vocabulary analysis
- **Maintainability Index**: Overall code maintainability

#### Complexity Thresholds

```python
COMPLEXITY_THRESHOLDS = {
    "cyclomatic": {
        "low": 1-5,
        "medium": 6-10,
        "high": 11-20,
        "critical": 21+
    },
    "cognitive": {
        "low": 1-7,
        "medium": 8-15,
        "high": 16-25,
        "critical": 26+
    }
}
```

### 🔄 Code Duplication

#### Duplication Types

- **Exact Duplication**: Identical code blocks
- **Structural Duplication**: Similar code patterns
- **Functional Duplication**: Same behavior, different implementation
- **Type-1**: Identical code except for whitespace
- **Type-2**: Identical code except for identifiers
- **Type-3**: Copied code with minor modifications

#### Detection Algorithms

```python
class DuplicationAnalyzer:
    def analyze(self, files):
        return {
            "exact_matches": self._find_exact_duplicates(files),
            "similar_blocks": self._find_similar_code(files),
            "structural_clones": self._find_structural_duplicates(files)
        }
```

### 🌳 AST Analysis

#### Structural Analysis

- **Function Complexity**: Parameter count, nesting depth
- **Class Design**: Method count, inheritance depth
- **Import Analysis**: Dependency mapping
- **Call Graph**: Function relationship mapping
- **Dead Code**: Unused functions and variables

#### AST Metrics

```python
ASTMetrics = {
    "function_count": int,
    "class_count": int,
    "import_count": int,
    "max_nesting_depth": int,
    "average_function_length": float,
    "dependency_graph": Dict[str, List[str]]
}
```

## 🛠️ Development

### 🏗️ Project Structure

```
quantum-code-inspector/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── agents/            # AI Agent Implementation
│   │   │   └── quality_agent.py
│   │   ├── analyzers/         # Code Analysis Tools
│   │   │   ├── security_analyzer.py
│   │   │   ├── performance_analyzer.py
│   │   │   ├── complexity_analyzer.py
│   │   │   ├── duplication_analyzer.py
│   │   │   └── ast_analyzer.py
│   │   ├── api/              # API Routes
│   │   │   └── auth.py
│   │   ├── auth/             # Authentication
│   │   │   ├── supabase_client.py
│   │   │   └── github_auth.py
│   │   ├── models/           # Data Models
│   │   │   └── analysis.py
│   │   ├── utils/            # Utilities
│   │   │   ├── code_parser.py
│   │   │   ├── config.py
│   │   │   └── file_handler.py
│   │   └── main.py           # FastAPI Application
│   ├── cli/                  # Command Line Interface
│   │   └── main.py
│   ├── requirements.txt      # Python Dependencies
│   ├── pyproject.toml       # Project Configuration
│   └── Dockerfile           # Docker Configuration
├── frontend/                 # React Frontend
│   ├── src/
│   │   ├── components/       # React Components
│   │   │   ├── analysis/     # Analysis Components
│   │   │   ├── ui/          # UI Components
│   │   │   ├── FileUploader.tsx
│   │   │   ├── InteractiveQA.tsx
│   │   │   └── RepositoryAnalyzer.tsx
│   │   ├── pages/           # Page Components
│   │   │   ├── HomePage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   └── AnalysisPage.tsx
│   │   ├── stores/          # State Management
│   │   │   └── auth.ts
│   │   ├── lib/             # Utilities
│   │   │   ├── api.ts
│   │   │   └── utils.ts
│   │   └── App.tsx          # Main Application
│   ├── package.json         # Node.js Dependencies
│   ├── vite.config.ts      # Vite Configuration
│   └── Dockerfile          # Docker Configuration
├── docker-compose.yml       # Docker Compose
├── README.md               # This file
└── test.py                 # Test file for analysis
```

### 🧪 Testing

#### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/test_analyzers.py
pytest tests/test_api.py
pytest tests/test_agents.py
```

#### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run end-to-end tests
npm run test:e2e
```

#### Integration Tests

```bash
# Test CLI functionality
quantum-inspector analyze test.py --format json

# Test API endpoints
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"files": ["test.py"]}'

# Test full workflow
docker-compose up -d
npm run test:integration
```

### 🔧 Development Workflow

#### Setting Up Development Environment

```bash
# 1. Clone and setup
git clone <repository>
cd quantum-code-inspector

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# 3. Frontend setup
cd ../frontend
npm install

# 4. Environment configuration
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit environment files

# 5. Start development servers
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Test CLI
quantum-inspector analyze test.py
```

#### Code Quality Standards

```bash
# Python code formatting
cd backend
black app/ cli/
isort app/ cli/
flake8 app/ cli/

# TypeScript code formatting
cd frontend
npm run lint
npm run format
npm run type-check
```

#### Contributing Guidelines

1. **🌿 Branch Strategy**: Feature branches from `main`
2. **📝 Commit Messages**: Conventional commits format
3. **🧪 Testing**: All new features must have tests
4. **📚 Documentation**: Update docs for new features
5. **🔍 Code Review**: All PRs require review
6. **✅ CI/CD**: All checks must pass

## 🔌 API Reference

### 🌐 REST API Endpoints

#### Analysis Endpoints

```http
POST /analyze
Content-Type: multipart/form-data

# Upload files for analysis
{
  "files": [File],
  "name": "string",
  "options": {
    "severity_threshold": "medium",
    "categories": ["security", "performance"]
  }
}
```

```http
POST /analyze/github
Content-Type: application/json

# Analyze GitHub repository
{
  "repo_url": "https://github.com/user/repo",
  "branch": "main",
  "name": "Analysis Name"
}
```

```http
GET /analysis/{analysis_id}
# Get analysis results

Response:
{
  "id": "uuid",
  "status": "completed",
  "quality_metrics": {...},
  "issues": [...],
  "recommendations": [...]
}
```

#### Q&A Endpoints

```http
POST /chat/{analysis_id}
Content-Type: application/json

# Ask questions about analysis
{
  "question": "What are the main security issues?",
  "context": "Focus on authentication code"
}

Response:
{
  "answer": "string",
  "confidence": 0.95,
  "sources": [...],
  "follow_up_questions": [...]
}
```

#### Authentication Endpoints

```http
POST /auth/login
POST /auth/register
GET /auth/me
POST /auth/github/authorize
GET /auth/github/callback
```

#### User Endpoints

```http
GET /user/analyses
GET /user/profile
PUT /user/profile
DELETE /analysis/{analysis_id}
```

### 📊 WebSocket Events

```javascript
// Real-time analysis updates
const ws = new WebSocket('ws://localhost:8000/ws/analysis/{analysis_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  switch(data.type) {
    case 'status_update':
      // Handle progress updates
      break;
    case 'analysis_complete':
      // Handle completion
      break;
    case 'error':
      // Handle errors
      break;
  }
};
```

### 🔧 CLI API

```bash
# Analysis commands
quantum-inspector analyze <path> [OPTIONS]
quantum-inspector analyze-repo <repo_url> [OPTIONS]
quantum-inspector ask <path> --question <question>

# Configuration commands
quantum-inspector config
quantum-inspector --version
quantum-inspector --help

# Options
--output, -o          Output file path
--format, -f          Output format (table|json|detailed)
--severity, -s        Minimum severity level
--category, -c        Filter by categories
--no-progress        Disable progress indicators
```
