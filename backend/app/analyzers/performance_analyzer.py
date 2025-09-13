"""
Performance Analyzer for detecting bottlenecks and optimization opportunities
- Algorithmic complexity analysis
- Database query optimization
- Memory usage patterns
- I/O operations analysis
"""

import re
import ast
import asyncio
from typing import List, Dict, Any, Optional, Set
from loguru import logger

from app.models.analysis import CodeIssue, IssueSeverity, IssueCategory
from app.utils.code_parser import FileInfo

class PerformanceAnalyzer:
    """Analyzer for performance bottlenecks and optimization opportunities"""
    
    def __init__(self):
        self.performance_patterns = {
            'n_plus_one_query': [
                r'for\s+\w+\s+in\s+.*:\s*\n\s*.*\.query\(',
                r'\.forEach\s*\(\s*.*\s*=>\s*.*\.find\(',
                r'for\s*\(\s*.*\s*;\s*.*\s*;\s*.*\)\s*\{[\s\S]*?\.query\('
            ],
            'inefficient_loops': [
                r'for\s+.*\s+in\s+range\(len\(',
                r'while\s+.*:\s*\n\s*.*\.append\(',
                r'for\s*\(\s*int\s+\w+\s*=\s*0\s*;\s*\w+\s*<\s*.*\.length\s*;\s*\w+\+\+\)'
            ],
            'expensive_operations_in_loops': [
                r'for\s+.*:\s*\n\s*.*re\.compile\(',
                r'for\s+.*:\s*\n\s*.*json\.loads\(',
                r'while\s+.*:\s*\n\s*.*\.split\('
            ],
            'synchronous_io': [
                r'requests\.get\(',
                r'urllib\.request\.',
                r'open\s*\(\s*["\'][^"\']*["\']\s*,\s*["\']r["\']',
                r'fs\.readFileSync\(',
                r'fs\.writeFileSync\('
            ]
        }
    
    async def analyze(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Perform comprehensive performance analysis"""
        logger.info("⚡ Starting performance analysis...")
        
        all_issues = []
        
        # Run different analysis methods
        tasks = [
            self._analyze_patterns(files),
            self._analyze_complexity(files),
            self._analyze_database_queries(files),
            self._analyze_memory_usage(files),
            self._analyze_async_opportunities(files)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_issues.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"Performance analysis failed: {str(result)}")
        
        logger.info(f"⚡ Found {len(all_issues)} performance issues")
        return all_issues
    
    async def _analyze_patterns(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Analyze using performance anti-patterns"""
        issues = []
        
        for file_info in files:
            for pattern_type, patterns in self.performance_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, file_info.content, re.IGNORECASE | re.MULTILINE)
                    
                    for match in matches:
                        line_number = file_info.content[:match.start()].count('\n') + 1
                        
                        issue = CodeIssue(
                            id=f"perf_{pattern_type}_{file_info.hash}_{line_number}",
                            category=IssueCategory.PERFORMANCE,
                            severity=self._get_performance_severity(pattern_type),
                            title=f"Performance Issue: {pattern_type.replace('_', ' ').title()}",
                            description=self._get_performance_description(pattern_type),
                            file_path=file_info.relative_path,
                            line_number=line_number,
                            code_snippet=self._get_code_snippet(file_info.content, line_number),
                            suggestion=self._get_performance_suggestion(pattern_type),
                            impact_score=self._calculate_performance_impact(pattern_type),
                            confidence=0.7,
                            rule_id=f"perf_{pattern_type}",
                            fix_complexity="medium",
                            estimated_fix_time=45
                        )
                        issues.append(issue)
        
        return issues
    
    async def _analyze_complexity(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Analyze algorithmic complexity"""
        issues = []
        
        for file_info in files:
            if file_info.language == 'python' and file_info.ast_tree:
                issues.extend(await self._analyze_python_complexity(file_info))
        
        return issues
    
    async def _analyze_python_complexity(self, file_info: FileInfo) -> List[CodeIssue]:
        """Analyze Python code complexity using AST"""
        issues = []
        
        try:
            for node in ast.walk(file_info.ast_tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    
                    if complexity > 10:  # High complexity threshold
                        issue = CodeIssue(
                            id=f"complexity_{file_info.hash}_{node.lineno}",
                            category=IssueCategory.COMPLEXITY,
                            severity=IssueSeverity.MEDIUM if complexity <= 15 else IssueSeverity.HIGH,
                            title=f"High Complexity Function: {node.name}",
                            description=f"Function has cyclomatic complexity of {complexity}",
                            file_path=file_info.relative_path,
                            line_number=node.lineno,
                            code_snippet=self._get_function_signature(file_info.content, node.lineno),
                            suggestion="Consider breaking this function into smaller, more focused functions",
                            impact_score=min(complexity / 2, 10.0),
                            confidence=0.9,
                            rule_id="high_complexity",
                            fix_complexity="hard",
                            estimated_fix_time=complexity * 5
                        )
                        issues.append(issue)
        
        except Exception as e:
            logger.warning(f"Python complexity analysis failed for {file_info.relative_path}: {str(e)}")
        
        return issues
    
    async def _analyze_database_queries(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Analyze database query patterns"""
        issues = []
        
        db_patterns = {
            'select_star': r'SELECT\s+\*\s+FROM',
            'missing_index': r'WHERE\s+\w+\s*=\s*["\'].*["\']',
            'no_limit': r'SELECT.*FROM.*WHERE.*(?!LIMIT)',
        }
        
        for file_info in files:
            for pattern_name, pattern in db_patterns.items():
                matches = re.finditer(pattern, file_info.content, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    line_number = file_info.content[:match.start()].count('\n') + 1
                    
                    issue = CodeIssue(
                        id=f"db_{pattern_name}_{file_info.hash}_{line_number}",
                        category=IssueCategory.PERFORMANCE,
                        severity=IssueSeverity.MEDIUM,
                        title=f"Database Query Issue: {pattern_name.replace('_', ' ').title()}",
                        description=self._get_db_issue_description(pattern_name),
                        file_path=file_info.relative_path,
                        line_number=line_number,
                        code_snippet=self._get_code_snippet(file_info.content, line_number),
                        suggestion=self._get_db_suggestion(pattern_name),
                        impact_score=6.0,
                        confidence=0.7,
                        rule_id=f"db_{pattern_name}",
                        fix_complexity="medium",
                        estimated_fix_time=30
                    )
                    issues.append(issue)
        
        return issues
    
    async def _analyze_memory_usage(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Analyze memory usage patterns"""
        issues = []
        
        memory_patterns = {
            'large_list_comprehension': r'\[.*for.*in.*range\(\s*\d{4,}\s*\)\]',
            'global_variables': r'^[A-Z_][A-Z0-9_]*\s*=',
        }
        
        for file_info in files:
            for pattern_name, pattern in memory_patterns.items():
                matches = re.finditer(pattern, file_info.content, re.MULTILINE)
                
                for match in matches:
                    line_number = file_info.content[:match.start()].count('\n') + 1
                    
                    issue = CodeIssue(
                        id=f"memory_{pattern_name}_{file_info.hash}_{line_number}",
                        category=IssueCategory.PERFORMANCE,
                        severity=IssueSeverity.LOW,
                        title=f"Memory Usage: {pattern_name.replace('_', ' ').title()}",
                        description=self._get_memory_description(pattern_name),
                        file_path=file_info.relative_path,
                        line_number=line_number,
                        code_snippet=self._get_code_snippet(file_info.content, line_number),
                        suggestion=self._get_memory_suggestion(pattern_name),
                        impact_score=4.0,
                        confidence=0.6,
                        rule_id=f"memory_{pattern_name}",
                        fix_complexity="medium",
                        estimated_fix_time=25
                    )
                    issues.append(issue)
        
        return issues
    
    async def _analyze_async_opportunities(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Identify opportunities for async/await optimization"""
        issues = []
        
        async_patterns = {
            'blocking_io': r'requests\.(get|post|put|delete)\(',
            'sync_file_operations': r'open\(.*\)\.read\(\)',
            'blocking_sleep': r'time\.sleep\(',
        }
        
        for file_info in files:
            if file_info.language not in ['python', 'javascript', 'typescript']:
                continue
                
            for pattern_name, pattern in async_patterns.items():
                matches = re.finditer(pattern, file_info.content, re.MULTILINE)
                
                for match in matches:
                    line_number = file_info.content[:match.start()].count('\n') + 1
                    
                    issue = CodeIssue(
                        id=f"async_{pattern_name}_{file_info.hash}_{line_number}",
                        category=IssueCategory.PERFORMANCE,
                        severity=IssueSeverity.MEDIUM,
                        title=f"Async Opportunity: {pattern_name.replace('_', ' ').title()}",
                        description=self._get_async_description(pattern_name),
                        file_path=file_info.relative_path,
                        line_number=line_number,
                        code_snippet=self._get_code_snippet(file_info.content, line_number),
                        suggestion=self._get_async_suggestion(pattern_name, file_info.language),
                        impact_score=5.0,
                        confidence=0.7,
                        rule_id=f"async_{pattern_name}",
                        fix_complexity="medium",
                        estimated_fix_time=40
                    )
                    issues.append(issue)
        
        return issues
    
    # Helper methods
    def _get_performance_severity(self, pattern_type: str) -> IssueSeverity:
        severity_map = {
            'n_plus_one_query': IssueSeverity.HIGH,
            'inefficient_loops': IssueSeverity.MEDIUM,
            'expensive_operations_in_loops': IssueSeverity.HIGH,
            'synchronous_io': IssueSeverity.MEDIUM,
        }
        return severity_map.get(pattern_type, IssueSeverity.MEDIUM)
    
    def _get_performance_description(self, pattern_type: str) -> str:
        descriptions = {
            'n_plus_one_query': "N+1 query problem detected - executing queries in a loop",
            'inefficient_loops': "Inefficient loop pattern that could be optimized",
            'expensive_operations_in_loops': "Expensive operations being performed inside loops",
            'synchronous_io': "Synchronous I/O operations that could block execution",
        }
        return descriptions.get(pattern_type, "Performance issue detected")
    
    def _get_performance_suggestion(self, pattern_type: str) -> str:
        suggestions = {
            'n_plus_one_query': "Use bulk queries, joins, or prefetch related data to avoid N+1 queries",
            'inefficient_loops': "Consider using list comprehensions, map(), or vectorized operations",
            'expensive_operations_in_loops': "Move expensive operations outside the loop or cache results",
            'synchronous_io': "Use async/await patterns or threading for I/O operations",
        }
        return suggestions.get(pattern_type, "Optimize this performance bottleneck")
    
    def _calculate_performance_impact(self, pattern_type: str) -> float:
        impact_scores = {
            'n_plus_one_query': 8.0,
            'inefficient_loops': 6.0,
            'expensive_operations_in_loops': 7.0,
            'synchronous_io': 5.0,
        }
        return impact_scores.get(pattern_type, 5.0)
    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _get_code_snippet(self, content: str, line_number: int, context_lines: int = 2) -> str:
        """Extract code snippet around the line"""
        lines = content.splitlines()
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        
        snippet_lines = []
        for i in range(start, end):
            prefix = ">>> " if i == line_number - 1 else "    "
            snippet_lines.append(f"{prefix}{lines[i]}")
        
        return "\n".join(snippet_lines)
    
    def _get_function_signature(self, content: str, line_number: int) -> str:
        """Get function signature from content"""
        lines = content.splitlines()
        if 0 <= line_number - 1 < len(lines):
            return lines[line_number - 1].strip()
        return ""
    
    def _get_db_issue_description(self, pattern_name: str) -> str:
        descriptions = {
            'select_star': "Using SELECT * can be inefficient and retrieve unnecessary data",
            'missing_index': "Query may benefit from database indexing",
            'no_limit': "Query without LIMIT clause may return excessive results",
        }
        return descriptions.get(pattern_name, "Database performance issue")
    
    def _get_db_suggestion(self, pattern_name: str) -> str:
        suggestions = {
            'select_star': "Select only the columns you need instead of using SELECT *",
            'missing_index': "Consider adding database indexes for frequently queried columns",
            'no_limit': "Add LIMIT clause to prevent retrieving excessive data",
        }
        return suggestions.get(pattern_name, "Optimize database query")
    
    def _get_memory_description(self, pattern_name: str) -> str:
        descriptions = {
            'large_list_comprehension': "Large list comprehension may consume excessive memory",
            'global_variables': "Global variables can lead to memory leaks",
        }
        return descriptions.get(pattern_name, "Memory usage issue")
    
    def _get_memory_suggestion(self, pattern_name: str) -> str:
        suggestions = {
            'large_list_comprehension': "Consider using generators for large datasets",
            'global_variables': "Use local variables or proper scoping instead of globals",
        }
        return suggestions.get(pattern_name, "Optimize memory usage")
    
    def _get_async_description(self, pattern_name: str) -> str:
        descriptions = {
            'blocking_io': "Synchronous HTTP requests can block execution",
            'sync_file_operations': "File operations could be made asynchronous",
            'blocking_sleep': "time.sleep() blocks the entire thread",
        }
        return descriptions.get(pattern_name, "Async optimization opportunity")
    
    def _get_async_suggestion(self, pattern_name: str, language: str) -> str:
        if language == 'python':
            suggestions = {
                'blocking_io': "Use aiohttp or httpx for async HTTP requests",
                'sync_file_operations': "Use aiofiles for async file operations",
                'blocking_sleep': "Use asyncio.sleep() instead of time.sleep()",
            }
        else:  # JavaScript/TypeScript
            suggestions = {
                'blocking_io': "Use fetch() with await or Promise.all() for concurrent requests",
                'sync_file_operations': "Use fs.promises for async file operations",
                'blocking_sleep': "Use setTimeout with Promise for non-blocking delays",
            }
        
        return suggestions.get(pattern_name, "Consider using async/await patterns")