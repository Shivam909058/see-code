"""AI-powered code quality intelligence agent using LangChain and advanced analysis"""

import asyncio
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
from loguru import logger

from app.models.analysis import (
    AnalysisResponse, CodeIssue, QualityMetrics, LanguageStats,
    ArchitectureInsight, DependencyInfo, IssueSeverity, IssueCategory
)
from app.utils.code_parser import CodeParser
from app.analyzers.security_analyzer import SecurityAnalyzer
from app.analyzers.performance_analyzer import PerformanceAnalyzer
from app.analyzers.complexity_analyzer import ComplexityAnalyzer
from app.analyzers.duplication_analyzer import DuplicationAnalyzer
from app.analyzers.ast_analyzer import ASTAnalyzer
from app.utils.config import get_settings
import hashlib

class QualityIntelligenceAgent:
    """AI-powered code quality analysis agent"""
    
    def __init__(self):
        self.settings = get_settings()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key=self.settings.openai_api_key,
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=2000
        )
        
        # Initialize memory for conversations - FIXED: Use updated LangChain memory
        self.memory = ConversationBufferMemory(
            chat_memory=ChatMessageHistory(),
            return_messages=True
        )
        
        # Initialize vector store for RAG
        self.vector_store = None
        self.embeddings = None
        
        # Initialize code parser and analyzers
        self.code_parser = CodeParser()
        self.security_analyzer = SecurityAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.duplication_analyzer = DuplicationAnalyzer()
        self.ast_analyzer = ASTAnalyzer()
        
        logger.info("🤖 Quality Intelligence Agent initialized with LLM and analyzers")
    
    async def initialize(self):
        """Initialize the agent (async initialization if needed)"""
        try:
            # Check if OpenAI API key is available
            if not self.settings.openai_api_key:
                logger.warning("⚠️  OpenAI API key not set. Some features may not work.")
                return False
            
            # Test LLM connection
            logger.info("🔍 Testing LLM connection...")
            await self.llm.ainvoke("Hello")
            logger.info("✅ LLM connection successful")
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  LLM initialization warning: {str(e)}")
            return False

    async def analyze_codebase(self, codebase_path: str) -> AnalysisResponse:
        """
        Comprehensive codebase analysis using LLM, traditional analyzers, and RAG
        """
        start_time = time.time()
        
        try:
            logger.info(f"🔍 Starting comprehensive analysis of codebase: {codebase_path}")
            
            # Parse codebase structure
            parsed_files = await self.code_parser.parse_directory(codebase_path)
            
            if not parsed_files:
                raise ValueError("No supported files found in codebase")
            
            # Calculate total codebase size
            total_chars = sum(len(file_info.content) for file_info in parsed_files)
            total_lines = sum(file_info.line_count for file_info in parsed_files)
            
            # Determine analysis strategy based on size
            use_rag = total_chars > 50000  # Use RAG for large codebases
            analysis_strategy = "RAG" if use_rag else "Direct LLM"
            
            logger.info(f"📊 Codebase size: {total_chars} chars, Using RAG: {use_rag}")
            
            # Initialize vector store for RAG if needed
            if use_rag:
                await self._initialize_vector_store(parsed_files)
            
            logger.info("🤖 Running LLM-powered comprehensive analysis...")
            
            # Run traditional analyzers in parallel
            security_issues = await self.security_analyzer.analyze(parsed_files)
            performance_issues = await self.performance_analyzer.analyze(parsed_files)
            complexity_issues = await self.complexity_analyzer.analyze(parsed_files)
            duplication_issues = await self.duplication_analyzer.analyze(parsed_files)
            
            # Combine traditional analysis results
            traditional_issues = security_issues + performance_issues + complexity_issues + duplication_issues
            
            # Get AST insights
            ast_analysis_result = await self.ast_analyzer.analyze(parsed_files)
            
            # Generate LLM-powered analysis
            llm_analysis = await self._perform_llm_analysis(parsed_files, traditional_issues, use_rag)
            
            # Combine all issues
            llm_issues = llm_analysis.get("additional_issues", [])
            all_issues = traditional_issues + llm_issues
            
            # Ensure all issues have IDs
            all_issues = self._ensure_issue_ids(all_issues)
            
            # Calculate metrics
            quality_metrics = self._calculate_quality_metrics(all_issues, parsed_files)
            language_stats = self._calculate_language_stats(parsed_files)
            
            # Generate summary and recommendations
            summary = llm_analysis.get("summary", f"Analysis completed with {len(all_issues)} issues found")
            recommendations = llm_analysis.get("recommendations", [])
            
            # Process AST insights into proper format
            ast_insights_list = []
            if isinstance(ast_analysis_result, dict) and "issues" in ast_analysis_result:
                # Convert AST issues to ArchitectureInsight format
                for issue in ast_analysis_result.get("issues", []):
                    if isinstance(issue, dict):
                        ast_insights_list.append({
                            "type": issue.get("category", "architectural"),
                            "description": issue.get("description", issue.get("title", "AST Analysis Issue")),
                            "affected_files": [issue.get("file_path", "unknown")],
                            "severity": issue.get("severity", "medium"),
                            "suggestion": issue.get("suggestion", "Review and refactor as needed")
                        })
            
            # Add LLM insights as architectural insights
            if "insights" in llm_analysis and isinstance(llm_analysis["insights"], dict):
                for key, value in llm_analysis["insights"].items():
                    if key != "rag_response":  # Skip raw responses
                        ast_insights_list.append({
                            "type": "llm_insight",
                            "description": f"{key}: {str(value)[:200]}",
                            "affected_files": [],
                            "severity": "info",
                            "suggestion": "Consider this insight for code improvement"
                        })
            
            processing_time = time.time() - start_time
            
            logger.info(f"✅ Analysis completed in {processing_time:.2f}s with {len(all_issues)} issues found")
            
            return AnalysisResponse(
                analysis_id="temp_id",  # FIXED: Will be set by caller
                repository_info={
                    "path": codebase_path,
                    "file_count": len(parsed_files),
                    "total_lines": total_lines,
                    "total_size": total_chars,
                    "languages": list(set(f.language for f in parsed_files)),
                    "analysis_strategy": analysis_strategy
                },
                quality_metrics=quality_metrics,
                language_stats=language_stats,
                issues=all_issues,
                dependencies=[],  # Will be populated by dependency analyzer
                architecture_insights=ast_insights_list,  # FIXED: Now returns a list
                summary=summary,
                recommendations=recommendations,
                processing_time=processing_time,
                files_analyzed=len(parsed_files),
                lines_analyzed=total_lines,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {str(e)}")
            raise Exception(f"Analysis failed: {str(e)}")
    
    async def _perform_llm_analysis(
        self, 
        parsed_files, 
        traditional_issues: List[CodeIssue], 
        use_rag: bool
    ) -> Dict[str, Any]:
        """Perform LLM analysis using either direct context or RAG"""
        if use_rag:
            return await self._perform_rag_analysis(parsed_files, traditional_issues)
        else:
            return await self._perform_direct_llm_analysis(parsed_files, traditional_issues)
    
    async def _perform_direct_llm_analysis(self, parsed_files, traditional_issues: List[CodeIssue]) -> Dict[str, Any]:
        """Perform direct LLM analysis for smaller codebases"""
        try:
            logger.info("🧠 Performing direct LLM analysis...")
            
            # Prepare context for LLM
            context_parts = []
            
            for file_info in parsed_files[:10]:  # Limit to prevent token overflow
                context_parts.append(f"""
File: {file_info.relative_path}
Language: {file_info.language}
Lines: {file_info.line_count}
Content:
```{file_info.language}
{file_info.content[:2000]}  # Truncate very long files
```
""")
            
            context = "\n".join(context_parts)
            
            # Create comprehensive analysis prompt
            prompt = f"""
You are an expert code quality analyst. Analyze this codebase and provide insights beyond traditional static analysis.

CODEBASE CONTEXT:
{context}

EXISTING ISSUES FOUND BY STATIC ANALYSIS:
{len(traditional_issues)} issues found including security, performance, complexity, and duplication issues.

ANALYSIS REQUIREMENTS:
1. Identify architectural patterns and anti-patterns
2. Assess code maintainability and readability
3. Find potential bugs not caught by static analysis
4. Evaluate error handling and edge cases
5. Check for proper separation of concerns
6. Assess testing strategy and coverage gaps
7. Identify performance bottlenecks beyond obvious ones
8. Check for security vulnerabilities beyond static rules

Please provide your analysis in JSON format:
{{
    "summary": "Overall assessment of the codebase quality and main concerns",
    "recommendations": [
        "Specific actionable recommendations for improvement"
    ],
    "additional_issues": [
        {{
            "category": "security|performance|complexity|duplication|testing|documentation|maintainability",
            "severity": "critical|high|medium|low|info",
            "title": "Brief issue title",
            "description": "Detailed description of the issue",
            "file_path": "path/to/file.py",
            "line_number": 42,
            "suggestion": "How to fix this issue",
            "impact_score": 7.5,
            "confidence": 0.8
        }}
    ],
    "insights": {{
        "architecture_quality": "Assessment of overall architecture",
        "maintainability_score": "Subjective score 1-10",
        "technical_debt_areas": ["Areas needing attention"],
        "strengths": ["What the codebase does well"],
        "improvement_priorities": ["Top 3 areas to focus on"]
    }}
}}
"""
            
            # Get LLM response
            response = await self.llm.ainvoke(prompt)
            llm_response = response.content
            
            # Parse JSON response
            try:
                import json
                # Extract JSON from response
                if "```json" in llm_response:
                    json_start = llm_response.find("```json") + 7
                    json_end = llm_response.find("```", json_start)
                    json_str = llm_response[json_start:json_end].strip()
                elif "{" in llm_response and "}" in llm_response:
                    json_start = llm_response.find("{")
                    json_end = llm_response.rfind("}") + 1
                    json_str = llm_response[json_start:json_end]
                else:
                    raise ValueError("No JSON found")
                
                parsed_response = json.loads(json_str)
                
                # Convert additional_issues to CodeIssue objects
                additional_issues = []
                for issue_data in parsed_response.get("additional_issues", []):
                    try:
                        # FIXED: Map invalid categories to valid ones
                        category_mapping = {
                            "error handling": "maintainability",
                            "error_handling": "maintainability",
                            "testing": "testing",
                            "documentation": "documentation",
                            "architecture": "architecture",
                            "maintainability": "maintainability"
                        }
                        
                        raw_category = issue_data.get("category", "complexity")
                        mapped_category = category_mapping.get(raw_category.lower(), raw_category)
                        
                        issue = CodeIssue(
                            category=IssueCategory(mapped_category),
                            severity=IssueSeverity(issue_data.get("severity", "medium")),
                            title=issue_data.get("title", "LLM Identified Issue"),
                            description=issue_data.get("description", ""),
                            file_path=issue_data.get("file_path", ""),
                            line_number=issue_data.get("line_number"),
                            suggestion=issue_data.get("suggestion", ""),
                            impact_score=float(issue_data.get("impact_score", 5.0)),  # FIXED: Include impact_score
                            confidence=float(issue_data.get("confidence", 0.8))       # FIXED: Include confidence
                        )
                        additional_issues.append(issue)
                    except Exception as e:
                        logger.warning(f"Failed to parse issue: {e}")
                        continue
                
                return {
                    "summary": parsed_response.get("summary", "LLM analysis completed"),
                    "recommendations": parsed_response.get("recommendations", []),
                    "additional_issues": additional_issues,
                    "insights": parsed_response.get("insights", {})
                }
                
            except Exception as e:
                logger.warning(f"Failed to parse LLM JSON response: {e}")
                return {
                    "summary": llm_response[:500] if llm_response else "Direct analysis completed",
                    "recommendations": ["Review LLM analysis output for detailed insights"],
                    "additional_issues": [],
                    "insights": {"llm_response": llm_response[:200]}
                }
                
        except Exception as e:
            logger.error(f"❌ Direct LLM analysis failed: {str(e)}")
            return {
                "summary": f"Direct analysis completed with {len(traditional_issues)} traditional issues found",
                "recommendations": ["Review traditional analysis results"],
                "additional_issues": [],
                "insights": {}
            }
    
    async def _perform_rag_analysis(self, parsed_files, traditional_issues: List[CodeIssue]) -> Dict[str, Any]:
        """Perform RAG-based analysis for larger codebases"""
        try:
            logger.info("🔍 Performing RAG analysis...")
            
            if not self.vector_store:
                logger.warning("Vector store not available for RAG analysis")
                return {
                    "summary": f"Traditional analysis completed with {len(traditional_issues)} issues found",
                    "recommendations": [],
                    "additional_issues": [],
                    "insights": {}
                }
            
            # Query for common code quality issues
            quality_queries = [
                "security vulnerabilities and unsafe practices",
                "performance bottlenecks and inefficient code",
                "code complexity and maintainability issues",
                "error handling and exception management",
                "testing gaps and coverage issues"
            ]
            
            insights = {}
            additional_issues = []
            
            for query in quality_queries:
                try:
                    # Search relevant code sections
                    docs = self.vector_store.similarity_search(query, k=3)
                    
                    if docs:
                        # Analyze with LLM
                        context = "\n".join([doc.page_content for doc in docs])
                        
                        prompt = f"""
Analyze this code section for: {query}

CODE:
{context}

Provide specific issues found in JSON format:
{{
    "issues": [
        {{
            "category": "security|performance|complexity|testing|documentation|maintainability",
            "severity": "critical|high|medium|low",
            "title": "Issue title",
            "description": "Detailed description",
            "suggestion": "How to fix",
            "impact_score": 6.0,
            "confidence": 0.7
        }}
    ],
    "insight": "Overall assessment for this query"
}}
"""
                        
                        response = await self.llm.ainvoke(prompt)
                        
                        # Parse response and add issues
                        try:
                            import json
                            if "```json" in response.content:
                                json_start = response.content.find("```json") + 7
                                json_end = response.content.find("```", json_start)
                                json_str = response.content[json_start:json_end].strip()
                            else:
                                json_str = response.content
                            
                            parsed = json.loads(json_str)
                            insights[query] = parsed.get("insight", "")
                            
                            for issue_data in parsed.get("issues", []):
                                # Map categories properly
                                category_mapping = {
                                    "error handling": "maintainability",
                                    "testing": "testing",
                                    "documentation": "documentation",
                                    "maintainability": "maintainability"
                                }
                                
                                raw_category = issue_data.get("category", "complexity")
                                mapped_category = category_mapping.get(raw_category.lower(), raw_category)
                                
                                issue = CodeIssue(
                                    category=IssueCategory(mapped_category),
                                    severity=IssueSeverity(issue_data.get("severity", "medium")),
                                    title=f"RAG: {issue_data.get('title', 'Issue')}",
                                    description=issue_data.get("description", ""),
                                    file_path="",  # RAG doesn't have specific file context
                                    suggestion=issue_data.get("suggestion", ""),
                                    impact_score=float(issue_data.get("impact_score", 5.0)),
                                    confidence=float(issue_data.get("confidence", 0.7))
                                )
                                additional_issues.append(issue)
                                
                        except:
                            insights[query] = response.content[:100]
                            
                except Exception as e:
                    logger.warning(f"RAG query failed for '{query}': {e}")
                    continue
            
            return {
                "summary": f"RAG analysis completed with {len(additional_issues)} additional issues found",
                "recommendations": [
                    "Focus on high-severity issues identified by RAG analysis",
                    "Review code sections flagged by multiple quality queries",
                    "Consider architectural improvements suggested by LLM"
                ],
                "additional_issues": additional_issues,
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"❌ RAG analysis failed: {str(e)}")
            return {
                "summary": f"RAG analysis completed with {len(traditional_issues)} traditional issues found",
                "recommendations": [],
                "additional_issues": [],
                "insights": {}
            }
    
    async def _initialize_vector_store(self, parsed_files):
        """Initialize vector store for RAG"""
        try:
            logger.info("🔧 Initializing vector store for RAG...")
            
            # Initialize embeddings
            self.embeddings = OpenAIEmbeddings(
                api_key=self.settings.openai_api_key
            )
            
            # Create documents from code files
            documents = []
            for file_info in parsed_files:
                # Split large files into chunks
                content = file_info.content
                chunk_size = 1000
                
                if len(content) > chunk_size:
                    # Split into overlapping chunks
                    for i in range(0, len(content), chunk_size - 100):
                        chunk = content[i:i + chunk_size]
                        documents.append(Document(
                            page_content=chunk,
                            metadata={
                                "file_path": file_info.relative_path,
                                "language": file_info.language,
                                "chunk_index": i // (chunk_size - 100)
                            }
                        ))
                else:
                    documents.append(Document(
                        page_content=content,
                        metadata={
                            "file_path": file_info.relative_path,
                            "language": file_info.language,
                            "chunk_index": 0
                        }
                    ))
            
            # Create vector store
            #self.embeddings = OpenAIEmbeddings(api_key=self.settings.openai_api_key)
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=None  # In-memory for now
            )
            
            logger.info(f"✅ Vector store initialized with {len(documents)} document chunks")
            
        except Exception as e:
            logger.error(f"❌ Failed to create embeddings: {str(e)}")
    
    def _calculate_quality_metrics(self, issues: List[CodeIssue], parsed_files) -> Dict[str, Any]:
        try:
            total_issues = len(issues)
            critical_issues = len([i for i in issues if i.severity == IssueSeverity.CRITICAL])
            high_issues = len([i for i in issues if i.severity == IssueSeverity.HIGH])
            
            # Calculate scores (0-100)
            security_score = max(0, 100 - (len([i for i in issues if i.category == IssueCategory.SECURITY]) * 5))
            performance_score = max(0, 100 - (len([i for i in issues if i.category == IssueCategory.PERFORMANCE]) * 3))
            
            # Calculate complexity metrics from issues and parsed files
            complexity_issues = [i for i in issues if i.category == IssueCategory.COMPLEXITY]
            avg_cyclomatic = sum(f.complexity_score for f in parsed_files) / len(parsed_files) if parsed_files else 1.0
            
            # Calculate maintainability index (0-100, higher is better)
            maintainability_index = max(0, 100 - (len(complexity_issues) * 3) - (avg_cyclomatic * 2))
            
            # Calculate code duplication percentage
            duplication_issues = [i for i in issues if i.category == IssueCategory.DUPLICATION]
            code_duplication = min(100, len(duplication_issues) * 2.5)  # Convert to percentage
            
            # Calculate technical debt ratio (0-100, lower is better)
            tech_debt_factors = critical_issues * 8 + high_issues * 4 + len(complexity_issues) * 2
            total_lines = sum(f.line_count for f in parsed_files) if parsed_files else 1
            technical_debt_ratio = min(100, (tech_debt_factors / total_lines) * 1000)  # Normalized
            
            # Calculate documentation coverage (mock implementation)
            documentation_coverage = max(0, 80 - len([i for i in issues if i.category == IssueCategory.DOCUMENTATION]) * 10)
            
            # Calculate dependency health
            dependency_issues = [i for i in issues if 'dependency' in i.title.lower() or 'import' in i.title.lower()]
            dependency_health = max(0, 100 - len(dependency_issues) * 5)
            
            # Calculate test coverage (mock - would need actual test analysis)
            test_coverage = max(0, 70 - len([i for i in issues if 'test' in i.title.lower()]) * 15)
            
            overall_score = (
                security_score * 0.25 + 
                performance_score * 0.20 + 
                maintainability_index * 0.20 + 
                (100 - code_duplication) * 0.15 + 
                (100 - technical_debt_ratio) * 0.10 + 
                documentation_coverage * 0.05 + 
                dependency_health * 0.05
            )
            
            return {
                "overall_score": round(overall_score, 1),
                "maintainability_index": round(maintainability_index, 1),
                "cyclomatic_complexity": round(avg_cyclomatic, 1),
                "test_coverage": round(test_coverage, 1),
                "code_duplication": round(code_duplication, 1),
                "technical_debt_ratio": round(technical_debt_ratio, 1),
                "security_score": round(security_score, 1),
                "performance_score": round(performance_score, 1),
                "documentation_coverage": round(documentation_coverage, 1),
                "dependency_health": round(dependency_health, 1)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate quality metrics: {str(e)}")
            # Return all required fields with default values
            return {
                "overall_score": 50.0,
                "maintainability_index": 50.0,
                "cyclomatic_complexity": 5.0,
                "test_coverage": 0.0,
                "code_duplication": 20.0,
                "technical_debt_ratio": 30.0,
                "security_score": 50.0,
                "performance_score": 50.0,
                "documentation_coverage": 40.0,
                "dependency_health": 60.0
            }
    
    def _calculate_language_stats(self, parsed_files) -> List[Dict[str, Any]]:
        """Calculate language distribution statistics - Returns list of dicts"""
        try:
            lang_stats = {}
            total_lines = sum(f.line_count for f in parsed_files)
            
            for file_info in parsed_files:
                lang = file_info.language
                if lang not in lang_stats:
                    lang_stats[lang] = {"files": 0, "lines": 0, "complexity": 0.0}
                
                lang_stats[lang]["files"] += 1
                lang_stats[lang]["lines"] += file_info.line_count
                lang_stats[lang]["complexity"] += file_info.complexity_score
            
            result = []
            for lang, stats in lang_stats.items():
                percentage = (stats["lines"] / total_lines * 100) if total_lines > 0 else 0
                avg_complexity = stats["complexity"] / stats["files"] if stats["files"] > 0 else 0
                
                result.append({
                    "language": lang,
                    "files_count": stats["files"],
                    "lines_of_code": stats["lines"],
                    "percentage": round(percentage, 1),
                    "complexity_score": round(avg_complexity, 1)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate language stats: {str(e)}")
            return []
    
    async def answer_question(
        self,
        question: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Answer questions about code analysis using RAG and LLM"""
        try:
            # Search relevant context from vector store
            if self.vector_store:
                docs = self.vector_store.similarity_search(question, k=5)
                context_parts = [doc.page_content for doc in docs]
                search_context = "\n\n".join(context_parts)
            else:
                search_context = context or "No specific context available."
            
            # Prepare conversation history
            history_text = ""
            if conversation_history:
                history_text = "\n".join([
                    f"Q: {item.get('question', '')}\nA: {item.get('answer', '')}"
                    for item in conversation_history[-3:]  # Last 3 exchanges
                ])
            
            # Create comprehensive prompt
            prompt = f"""
You are an expert code quality analyst assistant. Answer the user's question about code analysis using the provided context.

CONVERSATION HISTORY:
{history_text}

RELEVANT CODE CONTEXT:
{search_context}

USER QUESTION: {question}

Provide a helpful, accurate answer based on the context. If the context doesn't contain enough information, say so and provide general guidance.
"""
            
            response = await self.llm.ainvoke(prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"❌ Q&A failed: {str(e)}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"

    def _ensure_issue_ids(self, issues: List[CodeIssue]) -> List[CodeIssue]:
        """Ensure all issues have unique IDs"""
        for i, issue in enumerate(issues):
            if not issue.id:
                # Generate ID from issue details
                id_source = f"{issue.category.value}_{issue.file_path}_{issue.line_number or 0}_{i}"
                issue.id = hashlib.md5(id_source.encode()).hexdigest()[:12]
        return issues
