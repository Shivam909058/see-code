"""
Advanced AST (Abstract Syntax Tree) Analyzer
- Deep structural analysis
- Code pattern detection
- Dependency graph construction
- Advanced metrics calculation
"""

import ast
import asyncio
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import defaultdict, Counter
from loguru import logger

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    logger.warning("NetworkX not available. Some graph analysis features will be disabled.")

from app.models.analysis import CodeIssue, IssueSeverity, IssueCategory, ArchitectureInsight
from app.utils.code_parser import FileInfo

class ASTAnalyzer:
    """Advanced AST-based code analysis"""
    
    def __init__(self):
        if NETWORKX_AVAILABLE:
            self.dependency_graph = nx.DiGraph()
            self.class_hierarchy = nx.DiGraph()
            self.call_graph = nx.DiGraph()
        else:
            self.dependency_graph = None
            self.class_hierarchy = None
            self.call_graph = None
        
    async def analyze(self, files: List[FileInfo]) -> Dict[str, Any]:
        """Perform comprehensive AST analysis"""
        logger.info("🌳 Starting AST analysis...")
        
        analysis_results = {
            'issues': [],
            'architecture_insights': [],
            'dependency_graph': None,
            'metrics': {},
            'patterns': []
        }
        
        # Filter Python files for AST analysis
        python_files = [f for f in files if f.language == 'python' and f.ast_tree]
        
        if not python_files:
            logger.info("No Python files found for AST analysis")
            return analysis_results
        
        try:
            # Run different AST analysis methods
            tasks = [
                self._analyze_code_patterns(python_files),
                self._detect_code_smells(python_files),
                self._analyze_design_patterns(python_files)
            ]
            
            # Add graph analysis tasks only if networkx is available
            if NETWORKX_AVAILABLE:
                tasks.extend([
                    self._build_dependency_graph(python_files),
                    self._analyze_class_hierarchy(python_files),
                    self._analyze_function_calls(python_files)
                ])
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect results
            result_index = 0
            
            # Code patterns
            if isinstance(results[result_index], list):
                analysis_results['issues'].extend(results[result_index])
            result_index += 1
            
            # Code smells
            if isinstance(results[result_index], list):
                analysis_results['issues'].extend(results[result_index])
            result_index += 1
            
            # Design patterns
            if isinstance(results[result_index], list):
                analysis_results['patterns'] = results[result_index]
            result_index += 1
            
            # Graph analysis results (only if networkx available)
            if NETWORKX_AVAILABLE:
                # Dependency graph
                if not isinstance(results[result_index], Exception):
                    analysis_results['dependency_graph'] = results[result_index]
                result_index += 1
                
                # Class hierarchy
                if isinstance(results[result_index], list):
                    analysis_results['architecture_insights'].extend(results[result_index])
                result_index += 1
                
                # Function calls
                if not isinstance(results[result_index], Exception):
                    analysis_results['call_graph'] = results[result_index]
            
            # Calculate advanced metrics
            analysis_results['metrics'] = self._calculate_ast_metrics(python_files)
            
            logger.info(f"🌳 AST analysis completed with {len(analysis_results['issues'])} issues")
            
        except Exception as e:
            logger.error(f"AST analysis failed: {str(e)}")
        
        return analysis_results
    
    async def analyze_structure(self, files: List[FileInfo]) -> Dict[str, Any]:
        """Analyze code structure - alias for analyze method"""
        return await self.analyze(files)
    
    async def _analyze_code_patterns(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Analyze code patterns using AST"""
        issues = []
        
        for file_info in files:
            try:
                if not file_info.ast_tree:
                    continue
                    
                visitor = CodePatternVisitor(file_info)
                visitor.visit(file_info.ast_tree)
                issues.extend(visitor.issues)
                
            except Exception as e:
                logger.warning(f"Pattern analysis failed for {file_info.relative_path}: {str(e)}")
        
        return issues
    
    async def _build_dependency_graph(self, files: List[FileInfo]):
        """Build dependency graph from imports"""
        if not NETWORKX_AVAILABLE:
            return None
            
        graph = nx.DiGraph()
        
        for file_info in files:
            try:
                module_name = self._get_module_name(file_info.relative_path)
                graph.add_node(module_name, file_path=file_info.relative_path)
                
                # Add import dependencies
                if file_info.imports:
                    for import_name in file_info.imports:
                        # Clean import name
                        clean_import = import_name.split('.')[0]
                        graph.add_edge(module_name, clean_import)
                
            except Exception as e:
                logger.warning(f"Dependency graph building failed for {file_info.relative_path}: {str(e)}")
        
        self.dependency_graph = graph
        return graph
    
    async def _analyze_class_hierarchy(self, files: List[FileInfo]) -> List[ArchitectureInsight]:
        """Analyze class inheritance hierarchy"""
        insights = []
        
        if not NETWORKX_AVAILABLE:
            return insights
        
        try:
            hierarchy = nx.DiGraph()
            
            # Build class hierarchy graph
            for file_info in files:
                if file_info.classes:
                    for cls in file_info.classes:
                        class_name = cls.get('name', 'unknown')
                        hierarchy.add_node(class_name, file_path=file_info.relative_path)
                        
                        # Add inheritance relationships
                        for base in cls.get('bases', []):
                            hierarchy.add_edge(base, class_name)
            
            self.class_hierarchy = hierarchy
            
            # Detect hierarchy issues
            # Deep inheritance chains
            for node in hierarchy.nodes():
                try:
                    # Find longest path to this node
                    paths = []
                    for root in [n for n in hierarchy.nodes() if hierarchy.in_degree(n) == 0]:
                        if nx.has_path(hierarchy, root, node):
                            path_length = nx.shortest_path_length(hierarchy, root, node)
                            paths.append(path_length)
                    
                    max_depth = max(paths) if paths else 0
                    
                    if max_depth > 5:  # Deep inheritance threshold
                        insight = ArchitectureInsight(
                            type="deep_inheritance",
                            description=f"Class '{node}' has inheritance depth of {max_depth}",
                            affected_files=[hierarchy.nodes[node]['file_path']],
                            severity=IssueSeverity.MEDIUM,
                            suggestion="Consider using composition over inheritance or flattening the hierarchy"
                        )
                        insights.append(insight)
                        
                except Exception:
                    continue
            
            # Detect circular dependencies in class hierarchy
            try:
                cycles = list(nx.simple_cycles(hierarchy))
                for cycle in cycles:
                    if len(cycle) > 1:
                        affected_files = [hierarchy.nodes[node].get('file_path', 'unknown') for node in cycle]
                        insight = ArchitectureInsight(
                            type="circular_inheritance",
                            description=f"Circular inheritance detected: {' -> '.join(cycle)}",
                            affected_files=list(set(affected_files)),
                            severity=IssueSeverity.HIGH,
                            suggestion="Remove circular inheritance by restructuring class relationships"
                        )
                        insights.append(insight)
            except Exception:
                pass
            
        except Exception as e:
            logger.warning(f"Class hierarchy analysis failed: {str(e)}")
        
        return insights
    
    async def _analyze_function_calls(self, files: List[FileInfo]):
        """Build function call graph"""
        if not NETWORKX_AVAILABLE:
            return None
            
        call_graph = nx.DiGraph()
        
        for file_info in files:
            try:
                if not file_info.ast_tree:
                    continue
                    
                visitor = FunctionCallVisitor(file_info)
                visitor.visit(file_info.ast_tree)
                
                # Add nodes and edges to call graph
                for caller, callees in visitor.call_relationships.items():
                    call_graph.add_node(caller, file_path=file_info.relative_path)
                    for callee in callees:
                        call_graph.add_edge(caller, callee)
                
            except Exception as e:
                logger.warning(f"Function call analysis failed for {file_info.relative_path}: {str(e)}")
        
        self.call_graph = call_graph
        return call_graph
    
    async def _detect_code_smells(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Detect code smells using AST analysis"""
        issues = []
        
        for file_info in files:
            try:
                if not file_info.ast_tree:
                    continue
                    
                visitor = CodeSmellVisitor(file_info)
                visitor.visit(file_info.ast_tree)
                issues.extend(visitor.issues)
                
            except Exception as e:
                logger.warning(f"Code smell detection failed for {file_info.relative_path}: {str(e)}")
        
        return issues
    
    async def _analyze_design_patterns(self, files: List[FileInfo]) -> List[Dict[str, Any]]:
        """Detect common design patterns"""
        patterns = []
        
        for file_info in files:
            try:
                if not file_info.ast_tree:
                    continue
                    
                visitor = DesignPatternVisitor(file_info)
                visitor.visit(file_info.ast_tree)
                patterns.extend(visitor.patterns)
                
            except Exception as e:
                logger.warning(f"Design pattern analysis failed for {file_info.relative_path}: {str(e)}")
        
        return patterns
    
    def _calculate_ast_metrics(self, files: List[FileInfo]) -> Dict[str, Any]:
        """Calculate advanced metrics from AST analysis"""
        metrics = {
            'total_classes': 0,
            'total_functions': 0,
            'total_imports': 0,
            'average_methods_per_class': 0,
            'inheritance_depth_distribution': Counter(),
            'cyclomatic_complexity_distribution': Counter(),
            'dependency_coupling': 0,
            'cohesion_metrics': {}
        }
        
        try:
            all_classes = []
            all_functions = []
            all_imports = []
            
            for file_info in files:
                if file_info.classes:
                    all_classes.extend(file_info.classes)
                if file_info.functions:
                    all_functions.extend(file_info.functions)
                if file_info.imports:
                    all_imports.extend(file_info.imports)
            
            metrics['total_classes'] = len(all_classes)
            metrics['total_functions'] = len(all_functions)
            metrics['total_imports'] = len(all_imports)
            
            if all_classes:
                total_methods = sum(len(cls.get('methods', [])) for cls in all_classes)
                metrics['average_methods_per_class'] = total_methods / len(all_classes)
            
            # Dependency coupling (only if networkx available)
            if NETWORKX_AVAILABLE and self.dependency_graph and self.dependency_graph.number_of_nodes() > 0:
                metrics['dependency_coupling'] = self.dependency_graph.number_of_edges() / self.dependency_graph.number_of_nodes()
            
        except Exception as e:
            logger.warning(f"Metrics calculation failed: {str(e)}")
        
        return metrics
    
    def _get_module_name(self, file_path: str) -> str:
        """Extract module name from file path"""
        return file_path.replace('/', '.').replace('\\', '.').replace('.py', '')


class CodePatternVisitor(ast.NodeVisitor):
    """AST visitor for detecting code patterns and anti-patterns"""
    
    def __init__(self, file_info: FileInfo):
        self.file_info = file_info
        self.issues = []
        self.current_function = None
        self.current_class = None
    
    def visit_FunctionDef(self, node):
        old_function = self.current_function
        self.current_function = node
        
        # Check for long parameter lists
        if len(node.args.args) > 7:
            self.issues.append(CodeIssue(
                id=f"long_param_list_{self.file_info.hash}_{node.lineno}",
                category=IssueCategory.COMPLEXITY,
                severity=IssueSeverity.MEDIUM,
                title=f"Long Parameter List: {node.name}",
                description=f"Function '{node.name}' has {len(node.args.args)} parameters",
                file_path=self.file_info.relative_path,
                line_number=node.lineno,
                suggestion="Consider using parameter objects or reducing parameter count",
                impact_score=min(len(node.args.args), 10.0),  # FIXED: Ensure <= 10
                confidence=0.9,
                rule_id="long_parameter_list"
            ))
        
        # Check for functions without docstrings
        if not ast.get_docstring(node):
            self.issues.append(CodeIssue(
                id=f"missing_docstring_{self.file_info.hash}_{node.lineno}",
                category=IssueCategory.DOCUMENTATION,
                severity=IssueSeverity.LOW,
                title=f"Missing Docstring: {node.name}",
                description=f"Function '{node.name}' lacks documentation",
                file_path=self.file_info.relative_path,
                line_number=node.lineno,
                suggestion="Add docstring to document function purpose and parameters",
                impact_score=2.0,
                confidence=0.8,
                rule_id="missing_docstring"
            ))
        
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node
        
        # Check for classes without docstrings
        if not ast.get_docstring(node):
            self.issues.append(CodeIssue(
                id=f"class_missing_docstring_{self.file_info.hash}_{node.lineno}",
                category=IssueCategory.DOCUMENTATION,
                severity=IssueSeverity.LOW,
                title=f"Missing Class Docstring: {node.name}",
                description=f"Class '{node.name}' lacks documentation",
                file_path=self.file_info.relative_path,
                line_number=node.lineno,
                suggestion="Add docstring to document class purpose and usage",
                impact_score=3.0,
                confidence=0.8,
                rule_id="missing_class_docstring"
            ))
        
        self.generic_visit(node)
        self.current_class = old_class
    
    def visit_Try(self, node):
        # Check for bare except clauses
        for handler in node.handlers:
            if handler.type is None:
                self.issues.append(CodeIssue(
                    id=f"bare_except_{self.file_info.hash}_{handler.lineno}",
                    category=IssueCategory.STYLE,
                    severity=IssueSeverity.MEDIUM,
                    title="Bare Except Clause",
                    description="Using bare 'except:' clause can hide errors",
                    file_path=self.file_info.relative_path,
                    line_number=handler.lineno,
                    suggestion="Specify exception types or use 'except Exception:'",
                    impact_score=5.0,
                    confidence=0.9,
                    rule_id="bare_except"
                ))
        
        self.generic_visit(node)


class FunctionCallVisitor(ast.NodeVisitor):
    """AST visitor for building function call relationships"""
    
    def __init__(self, file_info: FileInfo):
        self.file_info = file_info
        self.call_relationships = defaultdict(set)
        self.current_function = None
    
    def visit_FunctionDef(self, node):
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_Call(self, node):
        if self.current_function:
            if isinstance(node.func, ast.Name):
                self.call_relationships[self.current_function].add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                attr_name = self._get_attribute_name(node.func)
                if attr_name:
                    self.call_relationships[self.current_function].add(attr_name)
        
        self.generic_visit(node)
    
    def _get_attribute_name(self, node):
        """Extract attribute name from ast.Attribute node"""
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                return f"{node.value.id}.{node.attr}"
            elif isinstance(node.value, ast.Attribute):
                parent = self._get_attribute_name(node.value)
                return f"{parent}.{node.attr}" if parent else node.attr
        return None


class CodeSmellVisitor(ast.NodeVisitor):
    """AST visitor for detecting code smells"""
    
    def __init__(self, file_info: FileInfo):
        self.file_info = file_info
        self.issues = []
        self.current_function = None
    
    def visit_FunctionDef(self, node):
        old_function = self.current_function
        self.current_function = node
        
        # Detect god functions (too many statements)
        statement_count = len([n for n in ast.walk(node) if isinstance(n, ast.stmt)])
        if statement_count > 50:
            self.issues.append(CodeIssue(
                id=f"god_function_{self.file_info.hash}_{node.lineno}",
                category=IssueCategory.COMPLEXITY,
                severity=IssueSeverity.HIGH,
                title=f"God Function: {node.name}",
                description=f"Function '{node.name}' has {statement_count} statements",
                file_path=self.file_info.relative_path,
                line_number=node.lineno,
                suggestion="Break down this function into smaller, focused functions",
                impact_score=min(statement_count / 10, 10.0),
                confidence=0.8,
                rule_id="god_function"
            ))
        
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_If(self, node):
        # Detect long if-elif chains
        elif_count = 0
        current = node
        
        while hasattr(current, 'orelse') and current.orelse:
            if len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                elif_count += 1
                current = current.orelse[0]
            else:
                break
        
        if elif_count > 5:
            self.issues.append(CodeIssue(
                id=f"long_elif_chain_{self.file_info.hash}_{node.lineno}",
                category=IssueCategory.COMPLEXITY,
                severity=IssueSeverity.MEDIUM,
                title="Long If-Elif Chain",
                description=f"If-elif chain with {elif_count + 1} branches",
                file_path=self.file_info.relative_path,
                line_number=node.lineno,
                suggestion="Consider using dictionary mapping or polymorphism",
                impact_score=elif_count,
                confidence=0.8,
                rule_id="long_elif_chain"
            ))
        
        self.generic_visit(node)


class DesignPatternVisitor(ast.NodeVisitor):
    """AST visitor for detecting design patterns"""
    
    def __init__(self, file_info: FileInfo):
        self.file_info = file_info
        self.patterns = []
        self.classes = {}
    
    def visit_ClassDef(self, node):
        # Collect class information
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        self.classes[node.name] = {
            'methods': methods,
            'bases': [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases],
            'node': node
        }
        
        # Detect Singleton pattern
        if self._is_singleton_pattern(node):
            self.patterns.append({
                'pattern': 'Singleton',
                'class': node.name,
                'file_path': self.file_info.relative_path,
                'line_number': node.lineno,
                'confidence': 0.8
            })
        
        # Detect Factory pattern
        if self._is_factory_pattern(node):
            self.patterns.append({
                'pattern': 'Factory',
                'class': node.name,
                'file_path': self.file_info.relative_path,
                'line_number': node.lineno,
                'confidence': 0.7
            })
        
        self.generic_visit(node)
    
    def _is_singleton_pattern(self, node):
        """Detect Singleton pattern"""
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        return '__new__' in methods and any('instance' in method or 'Instance' in method for method in methods)
    
    def _is_factory_pattern(self, node):
        """Detect Factory pattern"""
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
        factory_indicators = ['create', 'make', 'build', 'factory']
        return any(any(indicator in method.lower() for indicator in factory_indicators) for method in methods)


