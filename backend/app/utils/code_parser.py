"""Advanced code parser with AST support for multiple languages"""

import ast
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import hashlib
from loguru import logger

# Try to import tree-sitter, but make it optional since it's causing issues
try:
    import tree_sitter
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    logger.warning("Tree-sitter not available, falling back to basic parsing")

@dataclass
class FileInfo:
    absolute_path: str
    relative_path: str
    language: str
    content: str
    line_count: int
    size_bytes: int
    encoding: str = "utf-8"
    ast_tree: Optional[Any] = None
    imports: List[str] = None
    functions: List[Dict[str, Any]] = None
    classes: List[Dict[str, Any]] = None
    complexity_score: float = 0.0
    hash: str = ""

class CodeParser:
    """Advanced code parser with multi-language AST support"""
    
    def __init__(self):
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.rs': 'rust'
        }
        
        self.parsers = {}
        if TREE_SITTER_AVAILABLE:
            self._init_tree_sitter_parsers()
        else:
            logger.info("🔧 Using basic AST parsing (Tree-sitter not available)")
    
    def _init_tree_sitter_parsers(self):
        """Initialize Tree-sitter parsers for supported languages"""
        try:
            # For now, disable tree-sitter to avoid API issues
            # We'll use Python's built-in AST for Python and generic parsing for others
            logger.info("🔧 Tree-sitter parsers disabled due to API compatibility issues")
            logger.info("🔧 Using Python AST for Python files and generic parsing for others")
            return
            
            # This code is commented out until tree-sitter API is stable
            """
            languages_with_parsers = ['python', 'javascript', 'typescript', 'java', 'go']
            
            for lang in languages_with_parsers:
                try:
                    # Try the new tree-sitter API (v0.21+)
                    if lang == 'python':
                        import tree_sitter_python
                        language = tree_sitter_python.language()
                        parser = tree_sitter.Parser(language)
                    elif lang == 'javascript':
                        import tree_sitter_javascript
                        language = tree_sitter_javascript.language()
                        parser = tree_sitter.Parser(language)
                    elif lang == 'typescript':
                        import tree_sitter_typescript
                        language = tree_sitter_typescript.language_typescript()
                        parser = tree_sitter.Parser(language)
                    elif lang == 'java':
                        import tree_sitter_java
                        language = tree_sitter_java.language()
                        parser = tree_sitter.Parser(language)
                    elif lang == 'go':
                        import tree_sitter_go
                        language = tree_sitter_go.language()
                        parser = tree_sitter.Parser(language)
                    else:
                        continue
                    
                    self.parsers[lang] = parser
                    logger.info(f"✅ Initialized Tree-sitter parser for {lang}")
                    
                except ImportError:
                    logger.warning(f"⚠️ Tree-sitter parser for {lang} not available")
                except Exception as lang_error:
                    logger.warning(f"Failed to initialize {lang} parser: {str(lang_error)}")
            """
                    
        except Exception as e:
            logger.warning(f"Failed to initialize Tree-sitter parsers: {str(e)}")
    
    async def parse_directory(self, directory_path: str, max_depth: int = 10) -> List[FileInfo]:
        """Parse all supported files in a directory or a single file"""
        files = []
        path = Path(directory_path)
        
        if not path.exists():
            raise ValueError(f"Path does not exist: {directory_path}")
        
        # Handle single file case
        if path.is_file():
            if self._is_supported_file(path):
                try:
                    file_info = await self.parse_file(str(path), str(path.parent))
                    if file_info:
                        files.append(file_info)
                        logger.info(f"Found 1 supported file")
                    else:
                        logger.info(f"Found 0 supported files")
                except Exception as e:
                    logger.warning(f"Failed to parse file {path}: {str(e)}")
                    logger.info(f"Found 0 supported files")
            else:
                logger.info(f"Found 0 supported files - file type not supported: {path.suffix}")
            return files
        
        # Handle directory case
        directory = path
        supported_files = []
        for root, dirs, filenames in os.walk(directory):
            # Skip common directories that shouldn't be analyzed
            dirs[:] = [d for d in dirs if not self._should_skip_directory(d)]
            
            current_depth = len(Path(root).relative_to(directory).parts)
            if current_depth >= max_depth:
                dirs.clear()
                continue
            
            for filename in filenames:
                file_path = Path(root) / filename
                if self._is_supported_file(file_path):
                    supported_files.append(file_path)
        
        logger.info(f"Found {len(supported_files)} supported files")
        
        # Parse files in batches to avoid overwhelming the system
        batch_size = 50
        for i in range(0, len(supported_files), batch_size):
            batch = supported_files[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.parse_file(str(file_path), str(directory)) for file_path in batch],
                return_exceptions=True
            )
            
            for result in batch_results:
                if isinstance(result, FileInfo):
                    files.append(result)
                elif isinstance(result, Exception):
                    logger.warning(f"Failed to parse file: {str(result)}")
        
        return files
    
    async def parse_file(self, file_path: str, base_path: str = "") -> FileInfo:
        """Parse a single file with AST analysis"""
        try:
            path = Path(file_path)
            
            # Read file content
            content = await self._read_file_safely(file_path)
            if content is None:
                raise ValueError(f"Could not read file: {file_path}")
            
            # Determine language
            language = self.supported_extensions.get(path.suffix.lower(), 'unknown')
            
            # Calculate basic metrics
            line_count = len(content.splitlines())
            size_bytes = len(content.encode('utf-8'))
            file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            # Create relative path
            if base_path:
                try:
                    relative_path = str(path.relative_to(Path(base_path)))
                except ValueError:
                    relative_path = str(path)
            else:
                relative_path = str(path)
            
            file_info = FileInfo(
                absolute_path=str(path.absolute()),
                relative_path=relative_path,
                language=language,
                content=content,
                line_count=line_count,
                size_bytes=size_bytes,
                hash=file_hash
            )
            
            # Perform AST analysis
            await self._analyze_ast(file_info)
            
            return file_info
            
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {str(e)}")
            raise
    
    async def _analyze_ast(self, file_info: FileInfo):
        """Perform AST analysis on the file"""
        try:
            if file_info.language == 'python':
                await self._analyze_python_ast(file_info)
            elif file_info.language in ['javascript', 'typescript']:
                await self._analyze_js_ts_ast(file_info)
            elif file_info.language in self.parsers:
                await self._analyze_tree_sitter_ast(file_info)
            else:
                await self._analyze_generic(file_info)
                
        except Exception as e:
            logger.warning(f"AST analysis failed for {file_info.relative_path}: {str(e)}")
    
    async def _analyze_python_ast(self, file_info: FileInfo):
        """Analyze Python AST using built-in ast module"""
        try:
            tree = ast.parse(file_info.content)
            file_info.ast_tree = tree
            
            # Extract imports
            imports = []
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    else:  # ImportFrom
                        module = node.module or ''
                        for alias in node.names:
                            imports.append(f"{module}.{alias.name}")
                
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append({
                        'name': node.name,
                        'line_start': node.lineno,
                        'line_end': getattr(node, 'end_lineno', node.lineno),
                        'args': [arg.arg for arg in node.args.args],
                        'is_async': isinstance(node, ast.AsyncFunctionDef),
                        'decorators': [ast.unparse(d) if hasattr(ast, 'unparse') else str(d) for d in node.decorator_list]
                    })
                
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line_start': node.lineno,
                        'line_end': getattr(node, 'end_lineno', node.lineno),
                        'bases': [ast.unparse(base) if hasattr(ast, 'unparse') else str(base) for base in node.bases],
                        'methods': [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    })
            
            file_info.imports = imports
            file_info.functions = functions
            file_info.classes = classes
            
            # Calculate complexity score
            file_info.complexity_score = self._calculate_python_complexity(tree)
            
        except SyntaxError as e:
            logger.warning(f"Python syntax error in {file_info.relative_path}: {str(e)}")
            # Still set basic info even if AST parsing fails
            file_info.imports = []
            file_info.functions = []
            file_info.classes = []
            file_info.complexity_score = 1.0
        except Exception as e:
            logger.warning(f"Python AST analysis failed for {file_info.relative_path}: {str(e)}")
            # Fallback to generic analysis
            await self._analyze_generic(file_info)
    
    async def _analyze_js_ts_ast(self, file_info: FileInfo):
        """Analyze JavaScript/TypeScript using generic parsing (Tree-sitter disabled)"""
        # Since Tree-sitter is having issues, use generic parsing for JS/TS
        await self._analyze_generic(file_info)
    
    async def _analyze_tree_sitter_ast(self, file_info: FileInfo):
        """Analyze using Tree-sitter parser (currently disabled)"""
        # Tree-sitter is disabled due to API issues, fallback to generic
        await self._analyze_generic(file_info)
    
    async def _analyze_generic(self, file_info: FileInfo):
        """Generic analysis for all languages"""
        # Enhanced pattern-based extraction
        lines = file_info.content.splitlines()
        imports = []
        functions = []
        classes = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Language-specific import detection
            if file_info.language == 'python':
                if line_stripped.startswith(('import ', 'from ')):
                    imports.append(line_stripped)
            elif file_info.language in ['javascript', 'typescript']:
                if line_stripped.startswith(('import ', 'const ', 'let ', 'var ')) and ('require(' in line_stripped or 'from ' in line_stripped):
                    imports.append(line_stripped)
            elif file_info.language == 'java':
                if line_stripped.startswith('import '):
                    imports.append(line_stripped)
            elif file_info.language == 'go':
                if line_stripped.startswith('import ') or (line_stripped.startswith('"') and line_stripped.endswith('"')):
                    imports.append(line_stripped)
            else:
                # Generic import detection
                if any(line_stripped.startswith(keyword) for keyword in ['import ', 'from ', '#include', 'using ', 'require(']):
                    imports.append(line_stripped)
            
            # Enhanced function detection
            if file_info.language == 'python':
                if line_stripped.startswith(('def ', 'async def ')):
                    func_name = self._extract_function_name(line_stripped)
                    functions.append({
                        'name': func_name,
                        'line_start': i + 1,
                        'line_end': i + 1,
                        'args': self._extract_python_args(line_stripped),
                        'is_async': line_stripped.startswith('async def')
                    })
            elif file_info.language in ['javascript', 'typescript']:
                if any(keyword in line_stripped for keyword in ['function ', 'const ', 'let ', 'var ', '=>']):
                    if '(' in line_stripped and ')' in line_stripped:
                        func_name = self._extract_function_name(line_stripped)
                        functions.append({
                            'name': func_name,
                            'line_start': i + 1,
                            'line_end': i + 1
                        })
            else:
                # Generic function detection
                if any(keyword in line_stripped for keyword in ['function ', 'def ', 'func ', 'public ', 'private ', 'protected ']):
                    if '(' in line_stripped and ')' in line_stripped:
                        functions.append({
                            'name': self._extract_function_name(line_stripped),
                            'line_start': i + 1,
                            'line_end': i + 1
                        })
            
            # Enhanced class detection
            if file_info.language == 'python':
                if line_stripped.startswith('class '):
                    class_name = self._extract_class_name(line_stripped)
                    classes.append({
                        'name': class_name,
                        'line_start': i + 1,
                        'line_end': i + 1,
                        'bases': self._extract_python_bases(line_stripped)
                    })
            elif file_info.language == 'java':
                if line_stripped.startswith(('public class ', 'private class ', 'protected class ', 'class ')):
                    classes.append({
                        'name': self._extract_class_name(line_stripped),
                        'line_start': i + 1,
                        'line_end': i + 1
                    })
            else:
                # Generic class detection
                if any(line_stripped.startswith(keyword) for keyword in ['class ', 'struct ', 'interface ', 'type ']):
                    classes.append({
                        'name': self._extract_class_name(line_stripped),
                        'line_start': i + 1,
                        'line_end': i + 1
                    })
        
        file_info.imports = imports
        file_info.functions = functions
        file_info.classes = classes
        
        # Calculate complexity based on control structures
        file_info.complexity_score = self._calculate_generic_complexity(file_info.content)
    
    def _calculate_python_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity for Python code"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += len(node.handlers)
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(node, ast.comprehension):
                complexity += 1
        
        return float(complexity)
    
    def _calculate_generic_complexity(self, content: str) -> float:
        """Calculate approximate complexity for any language"""
        complexity = 1.0
        lines = content.splitlines()
        
        for line in lines:
            line_stripped = line.strip().lower()
            # Count control flow statements
            if any(keyword in line_stripped for keyword in ['if ', 'while ', 'for ', 'switch ', 'case ', 'catch ', 'except ']):
                complexity += 1
            elif any(keyword in line_stripped for keyword in ['&&', '||', 'and ', 'or ']):
                complexity += 0.5
        
        return complexity
    
    def _extract_python_args(self, line: str) -> List[str]:
        """Extract function arguments from Python function definition"""
        try:
            import re
            match = re.search(r'def\s+\w+\s*\((.*?)\)', line)
            if match:
                args_str = match.group(1)
                if not args_str.strip():
                    return []
                return [arg.strip().split('=')[0].strip() for arg in args_str.split(',')]
        except:
            pass
        return []
    
    def _extract_python_bases(self, line: str) -> List[str]:
        """Extract base classes from Python class definition"""
        try:
            import re
            match = re.search(r'class\s+\w+\s*\((.*?)\)', line)
            if match:
                bases_str = match.group(1)
                if not bases_str.strip():
                    return []
                return [base.strip() for base in bases_str.split(',')]
        except:
            pass
        return []
    
    def _extract_name_from_node(self, node) -> Optional[str]:
        """Extract name from Tree-sitter node (currently unused)"""
        return None
    
    def _extract_function_name(self, line: str) -> str:
        """Extract function name from line"""
        import re
        patterns = [
            r'def\s+(\w+)',           # Python
            r'async\s+def\s+(\w+)',   # Python async
            r'function\s+(\w+)',      # JavaScript
            r'(\w+)\s*:\s*\(',        # TypeScript
            r'const\s+(\w+)\s*=',     # JavaScript const
            r'let\s+(\w+)\s*=',       # JavaScript let
            r'var\s+(\w+)\s*=',       # JavaScript var
            r'func\s+(\w+)',          # Go
            r'public\s+\w+\s+(\w+)',  # Java
            r'private\s+\w+\s+(\w+)', # Java
            r'(\w+)\s*\(',            # Generic
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1)
        
        return "unknown"
    
    def _extract_class_name(self, line: str) -> str:
        """Extract class name from line"""
        import re
        patterns = [
            r'class\s+(\w+)',
            r'struct\s+(\w+)',
            r'interface\s+(\w+)',
            r'type\s+(\w+)',
            r'public\s+class\s+(\w+)',
            r'private\s+class\s+(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1)
        
        return "unknown"
    
    async def _read_file_safely(self, file_path: str) -> Optional[str]:
        """Safely read file with encoding detection"""
        encodings = ['utf-8', 'utf-16', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.warning(f"Failed to read {file_path}: {str(e)}")
                return None
        
        logger.warning(f"Could not decode file {file_path} with any encoding")
        return None
    
    def _is_supported_file(self, file_path: Path) -> bool:
        """Check if file is supported for analysis"""
        if file_path.suffix.lower() not in self.supported_extensions:
            return False
        
        # Skip files that are too large
        try:
            if file_path.stat().st_size > 1024 * 1024:  # 1MB limit
                return False
        except:
            return False
        
        # Skip binary files
        if self._is_binary_file(file_path):
            return False
        
        return True
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if file is binary"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except:
            return True
    
    def _should_skip_directory(self, dir_name: str) -> bool:
        """Check if directory should be skipped"""
        skip_dirs = {
            '.git', '.svn', '.hg', '.bzr',
            'node_modules', '__pycache__', '.pytest_cache',
            'venv', 'env', '.env', 'virtualenv',
            'build', 'dist', 'target', 'bin', 'obj',
            '.idea', '.vscode', '.vs',
            'coverage', '.coverage', '.nyc_output',
            'logs', 'log', 'tmp', 'temp'
        }
        
        return dir_name.lower() in skip_dirs or dir_name.startswith('.')


