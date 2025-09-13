"""
Advanced Complexity Analyzer for code maintainability assessment
- Cyclomatic complexity analysis
- Cognitive complexity measurement
- Function/class size analysis
- Nesting depth detection
- Code maintainability scoring
"""

import ast
import re
import asyncio
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
from loguru import logger

from app.models.analysis import CodeIssue, IssueSeverity, IssueCategory
from app.utils.code_parser import FileInfo

class ComplexityAnalyzer:
    """Advanced code complexity and maintainability analyzer"""
    
    def __init__(self):
        self.complexity_thresholds = {
            'function_length': {'low': 20, 'medium': 50, 'high': 100},
            'class_length': {'low': 200, 'medium': 500, 'high': 1000},
            'cyclomatic': {'low': 5, 'medium': 10, 'high': 15},
            'cognitive': {'low': 10, 'medium': 20, 'high': 30},
            'nesting_depth': {'low': 3, 'medium': 5, 'high': 7},
            'parameter_count': {'low': 4, 'medium': 7, 'high': 10}
        }
    
    async def analyze(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Perform comprehensive complexity analysis"""
        logger.info("🧠 Starting complexity analysis...")
        
        all_issues = []
        
        # Run different complexity analysis methods
        tasks = [
            self._analyze_cyclomatic_complexity(files),
            self._analyze_cognitive_complexity(files),
            self._analyze_function_complexity(files),
            self._analyze_class_complexity(files),
            self._analyze_nesting_depth(files),
            self._analyze_maintainability_index(files)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_issues.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"Complexity analysis failed: {str(result)}")
        
        logger.info(f"🧠 Found {len(all_issues)} complexity issues")
        return all_issues
    
    async def _analyze_cyclomatic_complexity(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Analyze cyclomatic complexity of functions"""
        issues = []
        
        for file_info in files:
            if file_info.language == 'python' and file_info.ast_tree:
                issues.extend(await self._analyze_python_cyclomatic(file_info))
            elif file_info.language in ['javascript', 'typescript']:
                issues.extend(await self._analyze_js_cyclomatic(file_info))
            elif file_info.language == 'java':
                issues.extend(await self._analyze_java_cyclomatic(file_info))
        
        return issues
    
    async def _analyze_python_cyclomatic(self, file_info: FileInfo) -> List[CodeIssue]:
        """Analyze Python cyclomatic complexity using AST"""
        issues = []
        
        try:
            class ComplexityVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.functions = []
                    self.current_function = None
                    self.complexity = 1
                
                def visit_FunctionDef(self, node):
                    # Save current state
                    old_function = self.current_function
                    old_complexity = self.complexity
                    
                    # Start new function analysis
                    self.current_function = node
                    self.complexity = 1  # Base complexity
                    
                    # Visit function body
                    self.generic_visit(node)
                    
                    # Store function complexity
                    self.functions.append({
                        'node': node,
                        'complexity': self.complexity,
                        'name': node.name
                    })
                    
                    # Restore previous state
                    self.current_function = old_function
                    self.complexity = old_complexity
                
                def visit_If(self, node):
                    if self.current_function:
                        self.complexity += 1
                    self.generic_visit(node)
                
                def visit_While(self, node):
                    if self.current_function:
                        self.complexity += 1
                    self.generic_visit(node)
                
                def visit_For(self, node):
                    if self.current_function:
                        self.complexity += 1
                    self.generic_visit(node)
                
                def visit_AsyncFor(self, node):
                    if self.current_function:
                        self.complexity += 1
                    self.generic_visit(node)
                
                def visit_ExceptHandler(self, node):
                    if self.current_function:
                        self.complexity += 1
                    self.generic_visit(node)
                
                def visit_With(self, node):
                    if self.current_function:
                        self.complexity += 1
                    self.generic_visit(node)
                
                def visit_Assert(self, node):
                    if self.current_function:
                        self.complexity += 1
                    self.generic_visit(node)
                
                def visit_BoolOp(self, node):
                    if self.current_function and isinstance(node.op, (ast.And, ast.Or)):
                        self.complexity += len(node.values) - 1
                    self.generic_visit(node)
            
            visitor = ComplexityVisitor()
            visitor.visit(file_info.ast_tree)
            
            for func_info in visitor.functions:
                complexity = func_info['complexity']
                node = func_info['node']
                
                if complexity > self.complexity_thresholds['cyclomatic']['medium']:
                    severity = IssueSeverity.HIGH if complexity > self.complexity_thresholds['cyclomatic']['high'] else IssueSeverity.MEDIUM
                    
                    issue = CodeIssue(
                        id=f"cyclomatic_{file_info.hash}_{node.lineno}",
                        category=IssueCategory.COMPLEXITY,
                        severity=severity,
                        title=f"High Cyclomatic Complexity: {func_info['name']}",
                        description=f"Function '{func_info['name']}' has cyclomatic complexity of {complexity}",
                        file_path=file_info.relative_path,
                        line_number=node.lineno,
                        code_snippet=self._get_function_snippet(file_info.content, node.lineno),
                        suggestion=f"Consider breaking this function into smaller functions. Target complexity: < {self.complexity_thresholds['cyclomatic']['medium']}",
                        impact_score=min(complexity / 2, 10.0),
                        confidence=0.9,
                        rule_id="high_cyclomatic_complexity",
                        fix_complexity="hard",
                        estimated_fix_time=complexity * 10
                    )
                    issues.append(issue)
        
        except Exception as e:
            logger.warning(f"Python cyclomatic complexity analysis failed for {file_info.relative_path}: {str(e)}")
        
        return issues
    
    async def _analyze_js_cyclomatic(self, file_info: FileInfo) -> List[CodeIssue]:
        """Analyze JavaScript/TypeScript cyclomatic complexity using regex patterns"""
        issues = []
        
        try:
            # Simple regex-based complexity analysis for JS/TS
            complexity_patterns = [
                r'\bif\s*\(',
                r'\belse\s+if\s*\(',
                r'\bwhile\s*\(',
                r'\bfor\s*\(',
                r'\bswitch\s*\(',
                r'\bcase\s+',
                r'\bcatch\s*\(',
                r'\b\?\s*.*\s*:',  # ternary operator
                r'\b&&\b',
                r'\b\|\|\b'
            ]
            
            lines = file_info.content.splitlines()
            current_function = None
            function_complexity = 0
            function_start_line = 0
            
            for i, line in enumerate(lines):
                line_num = i + 1
                
                # Detect function start
                if re.search(r'\bfunction\s+\w+|=>\s*{|\w+\s*:\s*function', line):
                    if current_function and function_complexity > self.complexity_thresholds['cyclomatic']['medium']:
                        severity = IssueSeverity.HIGH if function_complexity > self.complexity_thresholds['cyclomatic']['high'] else IssueSeverity.MEDIUM
                        
                        issue = CodeIssue(
                            id=f"js_cyclomatic_{file_info.hash}_{function_start_line}",
                            category=IssueCategory.COMPLEXITY,
                            severity=severity,
                            title=f"High Cyclomatic Complexity: {current_function}",
                            description=f"Function has estimated cyclomatic complexity of {function_complexity}",
                            file_path=file_info.relative_path,
                            line_number=function_start_line,
                            code_snippet=self._get_code_snippet(file_info.content, function_start_line),
                            suggestion="Consider breaking this function into smaller functions",
                            impact_score=min(function_complexity / 2, 10.0),
                            confidence=0.7,
                            rule_id="js_high_cyclomatic_complexity",
                            fix_complexity="hard",
                            estimated_fix_time=function_complexity * 10
                        )
                        issues.append(issue)
                    
                    # Start new function
                    func_match = re.search(r'function\s+(\w+)|(\w+)\s*=|(\w+)\s*:', line)
                    current_function = func_match.group(1) if func_match else "anonymous"
                    function_complexity = 1  # Base complexity
                    function_start_line = line_num
                
                # Count complexity patterns
                if current_function:
                    for pattern in complexity_patterns:
                        matches = re.findall(pattern, line)
                        function_complexity += len(matches)
            
            # Handle last function
            if current_function and function_complexity > self.complexity_thresholds['cyclomatic']['medium']:
                severity = IssueSeverity.HIGH if function_complexity > self.complexity_thresholds['cyclomatic']['high'] else IssueSeverity.MEDIUM
                
                issue = CodeIssue(
                    id=f"js_cyclomatic_{file_info.hash}_{function_start_line}",
                    category=IssueCategory.COMPLEXITY,
                    severity=severity,
                    title=f"High Cyclomatic Complexity: {current_function}",
                    description=f"Function has estimated cyclomatic complexity of {function_complexity}",
                    file_path=file_info.relative_path,
                    line_number=function_start_line,
                    code_snippet=self._get_code_snippet(file_info.content, function_start_line),
                    suggestion="Consider breaking this function into smaller functions",
                    impact_score=min(function_complexity / 2, 10.0),
                    confidence=0.7,
                    rule_id="js_high_cyclomatic_complexity",
                    fix_complexity="hard",
                    estimated_fix_time=function_complexity * 10
                )
                issues.append(issue)
        
        except Exception as e:
            logger.warning(f"JS/TS cyclomatic complexity analysis failed for {file_info.relative_path}: {str(e)}")
        
        return issues
    
    async def _analyze_java_cyclomatic(self, file_info: FileInfo) -> List[CodeIssue]:
        """Analyze Java cyclomatic complexity using regex patterns"""
        issues = []
        
        try:
            # Java complexity patterns
            complexity_patterns = [
                r'\bif\s*\(',
                r'\belse\s+if\s*\(',
                r'\bwhile\s*\(',
                r'\bfor\s*\(',
                r'\bdo\s+',
                r'\bswitch\s*\(',
                r'\bcase\s+',
                r'\bcatch\s*\(',
                r'\b\?\s*.*\s*:',  # ternary operator
                r'\b&&\b',
                r'\b\|\|\b'
            ]
            
            lines = file_info.content.splitlines()
            current_method = None
            method_complexity = 0
            method_start_line = 0
            
            for i, line in enumerate(lines):
                line_num = i + 1
                
                # Detect method start
                method_match = re.search(r'(public|private|protected|static).*\s+(\w+)\s*\(', line)
                if method_match:
                    if current_method and method_complexity > self.complexity_thresholds['cyclomatic']['medium']:
                        severity = IssueSeverity.HIGH if method_complexity > self.complexity_thresholds['cyclomatic']['high'] else IssueSeverity.MEDIUM
                        
                        issue = CodeIssue(
                            id=f"java_cyclomatic_{file_info.hash}_{method_start_line}",
                            category=IssueCategory.COMPLEXITY,
                            severity=severity,
                            title=f"High Cyclomatic Complexity: {current_method}",
                            description=f"Method has estimated cyclomatic complexity of {method_complexity}",
                            file_path=file_info.relative_path,
                            line_number=method_start_line,
                            code_snippet=self._get_code_snippet(file_info.content, method_start_line),
                            suggestion="Consider breaking this method into smaller methods",
                            impact_score=min(method_complexity / 2, 10.0),
                            confidence=0.7,
                            rule_id="java_high_cyclomatic_complexity",
                            fix_complexity="hard",
                            estimated_fix_time=method_complexity * 10
                        )
                        issues.append(issue)
                    
                    # Start new method
                    current_method = method_match.group(2)
                    method_complexity = 1  # Base complexity
                    method_start_line = line_num
                
                # Count complexity patterns
                if current_method:
                    for pattern in complexity_patterns:
                        matches = re.findall(pattern, line)
                        method_complexity += len(matches)
        
        except Exception as e:
            logger.warning(f"Java cyclomatic complexity analysis failed for {file_info.relative_path}: {str(e)}")
        
        return issues
    
    async def _analyze_cognitive_complexity(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Analyze cognitive complexity (readability and understandability)"""
        issues = []
        
        for file_info in files:
            if file_info.language == 'python' and file_info.ast_tree:
                issues.extend(await self._analyze_python_cognitive(file_info))
        
        return issues
    
    async def _analyze_python_cognitive(self, file_info: FileInfo) -> List[CodeIssue]:
        """Analyze Python cognitive complexity"""
        issues = []
        
        try:
            class CognitiveComplexityVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.functions = []
                    self.current_function = None
                    self.cognitive_score = 0
                    self.nesting_level = 0
                
                def visit_FunctionDef(self, node):
                    old_function = self.current_function
                    old_score = self.cognitive_score
                    old_nesting = self.nesting_level
                    
                    self.current_function = node
                    self.cognitive_score = 0
                    self.nesting_level = 0
                    
                    self.generic_visit(node)
                    
                    self.functions.append({
                        'node': node,
                        'cognitive_score': self.cognitive_score,
                        'name': node.name
                    })
                    
                    self.current_function = old_function
                    self.cognitive_score = old_score
                    self.nesting_level = old_nesting
                
                def visit_If(self, node):
                    if self.current_function:
                        self.cognitive_score += 1 + self.nesting_level
                        self.nesting_level += 1
                        self.generic_visit(node)
                        self.nesting_level -= 1
                    else:
                        self.generic_visit(node)
                
                def visit_While(self, node):
                    if self.current_function:
                        self.cognitive_score += 1 + self.nesting_level
                        self.nesting_level += 1
                        self.generic_visit(node)
                        self.nesting_level -= 1
                    else:
                        self.generic_visit(node)
                
                def visit_For(self, node):
                    if self.current_function:
                        self.cognitive_score += 1 + self.nesting_level
                        self.nesting_level += 1
                        self.generic_visit(node)
                        self.nesting_level -= 1
                    else:
                        self.generic_visit(node)
                
                def visit_Try(self, node):
                    if self.current_function:
                        self.cognitive_score += 1
                        self.generic_visit(node)
                    else:
                        self.generic_visit(node)
                
                def visit_ExceptHandler(self, node):
                    if self.current_function:
                        self.cognitive_score += 1 + self.nesting_level
                    self.generic_visit(node)
                
                def visit_BoolOp(self, node):
                    if self.current_function and isinstance(node.op, (ast.And, ast.Or)):
                        self.cognitive_score += 1
                    self.generic_visit(node)
            
            visitor = CognitiveComplexityVisitor()
            visitor.visit(file_info.ast_tree)
            
            for func_info in visitor.functions:
                cognitive_score = func_info['cognitive_score']
                node = func_info['node']
                
                if cognitive_score > self.complexity_thresholds['cognitive']['medium']:
                    severity = IssueSeverity.HIGH if cognitive_score > self.complexity_thresholds['cognitive']['high'] else IssueSeverity.MEDIUM
                    
                    issue = CodeIssue(
                        id=f"cognitive_{file_info.hash}_{node.lineno}",
                        category=IssueCategory.COMPLEXITY,
                        severity=severity,
                        title=f"High Cognitive Complexity: {func_info['name']}",
                        description=f"Function '{func_info['name']}' has cognitive complexity of {cognitive_score}",
                        file_path=file_info.relative_path,
                        line_number=node.lineno,
                        code_snippet=self._get_function_snippet(file_info.content, node.lineno),
                        suggestion=f"Reduce nesting and complex logic. Target cognitive complexity: < {self.complexity_thresholds['cognitive']['medium']}",
                        impact_score=min(cognitive_score / 3, 10.0),
                        confidence=0.8,
                        rule_id="high_cognitive_complexity",
                        fix_complexity="hard",
                        estimated_fix_time=cognitive_score * 8
                    )
                    issues.append(issue)
        
        except Exception as e:
            logger.warning(f"Python cognitive complexity analysis failed for {file_info.relative_path}: {str(e)}")
        
        return issues
    
    async def _analyze_function_complexity(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Analyze function length and parameter complexity"""
        issues = []
        
        for file_info in files:
            if file_info.functions:
                for func in file_info.functions:
                    func_name = func.get('name', 'unknown')
                    line_start = func.get('line_start', 0)
                    line_end = func.get('line_end', line_start)
                    func_length = line_end - line_start + 1
                    
                    # Check function length
                    if func_length > self.complexity_thresholds['function_length']['medium']:
                        severity = IssueSeverity.HIGH if func_length > self.complexity_thresholds['function_length']['high'] else IssueSeverity.MEDIUM
                        
                        issue = CodeIssue(
                            id=f"func_length_{file_info.hash}_{line_start}",
                            category=IssueCategory.COMPLEXITY,
                            severity=severity,
                            title=f"Long Function: {func_name}",
                            description=f"Function '{func_name}' is {func_length} lines long",
                            file_path=file_info.relative_path,
                            line_number=line_start,
                            code_snippet=self._get_function_snippet(file_info.content, line_start),
                            suggestion=f"Consider breaking this function into smaller functions. Target length: < {self.complexity_thresholds['function_length']['medium']} lines",
                            impact_score=min(func_length / 20, 10.0),
                            confidence=0.9,
                            rule_id="long_function",
                            fix_complexity="medium",
                            estimated_fix_time=func_length * 2
                        )
                        issues.append(issue)
                    
                    # Check parameter count
                    args = func.get('args', [])
                    param_count = len(args)
                    
                    if param_count > self.complexity_thresholds['parameter_count']['medium']:
                        severity = IssueSeverity.MEDIUM if param_count <= self.complexity_thresholds['parameter_count']['high'] else IssueSeverity.HIGH
                        
                        issue = CodeIssue(
                            id=f"param_count_{file_info.hash}_{line_start}",
                            category=IssueCategory.COMPLEXITY,
                            severity=severity,
                            title=f"Too Many Parameters: {func_name}",
                            description=f"Function '{func_name}' has {param_count} parameters",
                            file_path=file_info.relative_path,
                            line_number=line_start,
                            code_snippet=self._get_function_snippet(file_info.content, line_start),
                            suggestion=f"Consider using parameter objects or reducing parameter count. Target: < {self.complexity_thresholds['parameter_count']['medium']} parameters",
                            impact_score=min(param_count, 10.0),
                            confidence=0.8,
                            rule_id="too_many_parameters",
                            fix_complexity="medium",
                            estimated_fix_time=param_count * 5
                        )
                        issues.append(issue)
        
        return issues
    
    async def _analyze_class_complexity(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Analyze class complexity and size"""
        issues = []
        
        for file_info in files:
            if file_info.classes:
                for cls in file_info.classes:
                    class_name = cls.get('name', 'unknown')
                    line_start = cls.get('line_start', 0)
                    line_end = cls.get('line_end', line_start)
                    class_length = line_end - line_start + 1
                    
                    # Check class length
                    if class_length > self.complexity_thresholds['class_length']['medium']:
                        severity = IssueSeverity.HIGH if class_length > self.complexity_thresholds['class_length']['high'] else IssueSeverity.MEDIUM
                        
                        issue = CodeIssue(
                            id=f"class_length_{file_info.hash}_{line_start}",
                            category=IssueCategory.COMPLEXITY,
                            severity=severity,
                            title=f"Large Class: {class_name}",
                            description=f"Class '{class_name}' is {class_length} lines long",
                            file_path=file_info.relative_path,
                            line_number=line_start,
                            code_snippet=self._get_code_snippet(file_info.content, line_start),
                            suggestion=f"Consider breaking this class into smaller, more focused classes. Target length: < {self.complexity_thresholds['class_length']['medium']} lines",
                            impact_score=min(class_length / 100, 10.0),
                            confidence=0.8,
                            rule_id="large_class",
                            fix_complexity="hard",
                            estimated_fix_time=class_length * 3
                        )
                        issues.append(issue)
                    
                    # Check method count
                    methods = cls.get('methods', [])
                    method_count = len(methods)
                    
                    if method_count > 20:  # Arbitrary threshold for too many methods
                        issue = CodeIssue(
                            id=f"method_count_{file_info.hash}_{line_start}",
                            category=IssueCategory.COMPLEXITY,
                            severity=IssueSeverity.MEDIUM,
                            title=f"Too Many Methods: {class_name}",
                            description=f"Class '{class_name}' has {method_count} methods",
                            file_path=file_info.relative_path,
                            line_number=line_start,
                            code_snippet=self._get_code_snippet(file_info.content, line_start),
                            suggestion="Consider using composition or breaking the class into smaller classes",
                            impact_score=min(method_count / 5, 10.0),
                            confidence=0.7,
                            rule_id="too_many_methods",
                            fix_complexity="hard",
                            estimated_fix_time=method_count * 10
                        )
                        issues.append(issue)
        
        return issues
    
    async def _analyze_nesting_depth(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Analyze nesting depth in code"""
        issues = []
        
        for file_info in files:
            if file_info.language == 'python' and file_info.ast_tree:
                issues.extend(await self._analyze_python_nesting(file_info))
            else:
                issues.extend(await self._analyze_generic_nesting(file_info))
        
        return issues
    
    async def _analyze_python_nesting(self, file_info: FileInfo) -> List[CodeIssue]:
        """Analyze Python nesting depth using AST"""
        issues = []
        
        try:
            class NestingVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.max_depth = 0
                    self.current_depth = 0
                    self.depth_locations = []
                
                def visit_If(self, node):
                    self.current_depth += 1
                    if self.current_depth > self.max_depth:
                        self.max_depth = self.current_depth
                        if self.current_depth > 5:  # Deep nesting threshold
                            self.depth_locations.append((node.lineno, self.current_depth, 'if'))
                    self.generic_visit(node)
                    self.current_depth -= 1
                
                def visit_While(self, node):
                    self.current_depth += 1
                    if self.current_depth > self.max_depth:
                        self.max_depth = self.current_depth
                        if self.current_depth > 5:
                            self.depth_locations.append((node.lineno, self.current_depth, 'while'))
                    self.generic_visit(node)
                    self.current_depth -= 1
                
                def visit_For(self, node):
                    self.current_depth += 1
                    if self.current_depth > self.max_depth:
                        self.max_depth = self.current_depth
                        if self.current_depth > 5:
                            self.depth_locations.append((node.lineno, self.current_depth, 'for'))
                    self.generic_visit(node)
                    self.current_depth -= 1
                
                def visit_Try(self, node):
                    self.current_depth += 1
                    if self.current_depth > self.max_depth:
                        self.max_depth = self.current_depth
                        if self.current_depth > 5:
                            self.depth_locations.append((node.lineno, self.current_depth, 'try'))
                    self.generic_visit(node)
                    self.current_depth -= 1
                
                def visit_With(self, node):
                    self.current_depth += 1
                    if self.current_depth > self.max_depth:
                        self.max_depth = self.current_depth
                        if self.current_depth > 5:
                            self.depth_locations.append((node.lineno, self.current_depth, 'with'))
                    self.generic_visit(node)
                    self.current_depth -= 1
            
            visitor = NestingVisitor()
            visitor.visit(file_info.ast_tree)
            
            for line_no, depth, construct in visitor.depth_locations:
                severity = IssueSeverity.HIGH if depth > self.complexity_thresholds['nesting_depth']['high'] else IssueSeverity.MEDIUM
                
                issue = CodeIssue(
                    id=f"nesting_{file_info.hash}_{line_no}",
                    category=IssueCategory.COMPLEXITY,
                    severity=severity,
                    title=f"Deep Nesting: {construct} at depth {depth}",
                    description=f"Code has nesting depth of {depth} levels",
                    file_path=file_info.relative_path,
                    line_number=line_no,
                    code_snippet=self._get_code_snippet(file_info.content, line_no),
                    suggestion=f"Reduce nesting by using early returns, guard clauses, or extracting methods. Target depth: < {self.complexity_thresholds['nesting_depth']['medium']}",
                    impact_score=min(depth, 10.0),
                    confidence=0.9,
                    rule_id="deep_nesting",
                    fix_complexity="medium",
                    estimated_fix_time=depth * 15
                )
                issues.append(issue)
        
        except Exception as e:
            logger.warning(f"Python nesting analysis failed for {file_info.relative_path}: {str(e)}")
        
        return issues
    
    async def _analyze_generic_nesting(self, file_info: FileInfo) -> List[CodeIssue]:
        """Analyze nesting depth using simple indentation counting"""
        issues = []
        
        try:
            lines = file_info.content.splitlines()
            max_depth = 0
            
            for i, line in enumerate(lines):
                # Count leading whitespace
                stripped = line.lstrip()
                if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                    continue
                
                indent_level = len(line) - len(stripped)
                
                # Estimate nesting depth (assuming 4 spaces or 1 tab per level)
                if '\t' in line[:indent_level]:
                    depth = line[:indent_level].count('\t')
                else:
                    depth = indent_level // 4
                
                if depth > max_depth:
                    max_depth = depth
                
                if depth > self.complexity_thresholds['nesting_depth']['medium']:
                    severity = IssueSeverity.HIGH if depth > self.complexity_thresholds['nesting_depth']['high'] else IssueSeverity.MEDIUM
                    
                    issue = CodeIssue(
                        id=f"indent_nesting_{file_info.hash}_{i+1}",
                        category=IssueCategory.COMPLEXITY,
                        severity=severity,
                        title=f"Deep Nesting: {depth} levels",
                        description=f"Code has indentation depth of {depth} levels",
                        file_path=file_info.relative_path,
                        line_number=i + 1,
                        code_snippet=self._get_code_snippet(file_info.content, i + 1),
                        suggestion="Reduce nesting by using early returns or extracting functions",
                        impact_score=min(depth, 10.0),
                        confidence=0.6,
                        rule_id="deep_indentation",
                        fix_complexity="medium",
                        estimated_fix_time=depth * 10
                    )
                    issues.append(issue)
                    break  # Only report first occurrence per file
        
        except Exception as e:
            logger.warning(f"Generic nesting analysis failed for {file_info.relative_path}: {str(e)}")
        
        return issues
    
    async def _analyze_maintainability_index(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Calculate maintainability index for files"""
        issues = []
        
        for file_info in files:
            try:
                # Simplified maintainability index calculation
                lines_of_code = file_info.line_count
                
                # Count operators and operands (simplified)
                operators = len(re.findall(r'[+\-*/=<>!&|]', file_info.content))
                operands = len(re.findall(r'\b\w+\b', file_info.content))
                
                # Halstead metrics (simplified)
                program_length = operators + operands
                vocabulary = len(set(re.findall(r'\b\w+\b', file_info.content))) + len(set(re.findall(r'[+\-*/=<>!&|]', file_info.content)))
                
                if program_length > 0 and vocabulary > 0:
                    # Simplified maintainability index
                    complexity_score = file_info.complexity_score if file_info.complexity_score > 0 else 1
                    maintainability_index = max(0, 171 - 5.2 * complexity_score - 0.23 * lines_of_code / 10 - 16.2 * (program_length / vocabulary))
                    
                    if maintainability_index < 50:  # Low maintainability threshold
                        severity = IssueSeverity.HIGH if maintainability_index < 25 else IssueSeverity.MEDIUM
                        
                        issue = CodeIssue(
                            id=f"maintainability_{file_info.hash}",
                            category=IssueCategory.MAINTAINABILITY,
                            severity=severity,
                            title=f"Low Maintainability Index: {maintainability_index:.1f}",
                            description=f"File has low maintainability index of {maintainability_index:.1f}",
                            file_path=file_info.relative_path,
                            line_number=1,
                            code_snippet=file_info.content[:200] + "..." if len(file_info.content) > 200 else file_info.content,
                            suggestion="Improve code structure, reduce complexity, and enhance readability",
                            impact_score=max(0, 10 - maintainability_index / 10),
                            confidence=0.7,
                            rule_id="low_maintainability",
                            fix_complexity="hard",
                            estimated_fix_time=int((50 - maintainability_index) * 5)
                        )
                        issues.append(issue)
            
            except Exception as e:
                logger.warning(f"Maintainability analysis failed for {file_info.relative_path}: {str(e)}")
        
        return issues
    
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
    
    def _get_function_snippet(self, content: str, line_number: int) -> str:
        """Get function signature and first few lines"""
        lines = content.splitlines()
        start = max(0, line_number - 1)
        end = min(len(lines), line_number + 5)
        
        snippet_lines = []
        for i in range(start, end):
            prefix = ">>> " if i == line_number - 1 else "    "
            snippet_lines.append(f"{prefix}{lines[i]}")
        
        return "\n".join(snippet_lines)
