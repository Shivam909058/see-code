"""
Advanced Code Duplication Analyzer
- Exact duplicate detection
- Similar code block identification
- Cross-file duplication analysis
- Semantic similarity detection
"""

import hashlib
import re
import asyncio
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import defaultdict
from loguru import logger

try:
    import difflib
    DIFFLIB_AVAILABLE = True
except ImportError:
    DIFFLIB_AVAILABLE = False
    logger.warning("difflib not available. Using alternative similarity calculation.")

from app.models.analysis import CodeIssue, IssueSeverity, IssueCategory
from app.utils.code_parser import FileInfo

class DuplicationAnalyzer:
    """Advanced code duplication and similarity analyzer"""
    
    def __init__(self):
        self.min_duplicate_lines = 5  # Minimum lines to consider duplication
        self.similarity_threshold = 0.8  # Similarity threshold for near-duplicates
        self.min_tokens = 50  # Minimum tokens for duplicate detection
    
    async def analyze(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Perform comprehensive duplication analysis"""
        logger.info("🔄 Starting duplication analysis...")
        
        all_issues = []
        
        # Run different duplication analysis methods
        tasks = [
            self._analyze_exact_duplicates(files),
            self._analyze_similar_blocks(files),
            self._analyze_function_duplicates(files),
            self._analyze_class_duplicates(files),
            self._analyze_copy_paste_patterns(files)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_issues.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"Duplication analysis failed: {str(result)}")
        
        # Deduplicate issues
        unique_issues = self._deduplicate_issues(all_issues)
        
        logger.info(f"🔄 Found {len(unique_issues)} duplication issues")
        return unique_issues
    
    async def _analyze_exact_duplicates(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Find exact duplicate code blocks"""
        issues = []
        
        try:
            # Extract code blocks from all files
            code_blocks = []
            
            for file_info in files:
                blocks = self._extract_code_blocks(file_info)
                code_blocks.extend(blocks)
            
            # Group blocks by hash
            hash_groups = defaultdict(list)
            for block in code_blocks:
                hash_groups[block['hash']].append(block)
            
            # Find duplicates
            for block_hash, blocks in hash_groups.items():
                if len(blocks) > 1 and blocks[0]['line_count'] >= self.min_duplicate_lines:
                    # Create issues for duplicates
                    for i, block in enumerate(blocks):
                        other_locations = [
                            f"{b['file_path']}:{b['start_line']}-{b['end_line']}"
                            for j, b in enumerate(blocks) if j != i
                        ]
                        
                        severity = IssueSeverity.HIGH if block['line_count'] > 20 else IssueSeverity.MEDIUM
                        
                        issue = CodeIssue(
                            id=f"exact_dup_{block['file_hash']}_{block['start_line']}",
                            category=IssueCategory.DUPLICATION,
                            severity=severity,
                            title=f"Exact Code Duplication ({block['line_count']} lines)",
                            description=f"Code block duplicated in {len(blocks)} locations: {', '.join(other_locations)}",
                            file_path=block['file_path'],
                            line_number=block['start_line'],
                            line_range=(block['start_line'], block['end_line']),
                            code_snippet=block['content'][:500] + "..." if len(block['content']) > 500 else block['content'],
                            suggestion="Extract common code into a shared function or module",
                            impact_score=min(block['line_count'] / 5, 10.0),
                            confidence=1.0,
                            rule_id="exact_duplication",
                            fix_complexity="medium",
                            estimated_fix_time=block['line_count'] * 3
                        )
                        issues.append(issue)
        
        except Exception as e:
            logger.warning(f"Exact duplication analysis failed: {str(e)}")
        
        return issues
    
    async def _analyze_similar_blocks(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Find similar (but not identical) code blocks"""
        issues = []
        
        try:
            # Extract normalized code blocks
            normalized_blocks = []
            
            for file_info in files:
                blocks = self._extract_normalized_blocks(file_info)
                normalized_blocks.extend(blocks)
            
            # Compare blocks for similarity
            for i, block1 in enumerate(normalized_blocks):
                for j, block2 in enumerate(normalized_blocks[i+1:], i+1):
                    if block1['file_path'] == block2['file_path']:
                        continue  # Skip same file comparisons
                    
                    similarity = self._calculate_similarity(block1['normalized'], block2['normalized'])
                    
                    if similarity >= self.similarity_threshold and block1['line_count'] >= self.min_duplicate_lines:
                        severity = IssueSeverity.MEDIUM if similarity < 0.9 else IssueSeverity.HIGH
                        
                        issue = CodeIssue(
                            id=f"similar_dup_{block1['file_hash']}_{block1['start_line']}_{j}",
                            category=IssueCategory.DUPLICATION,
                            severity=severity,
                            title=f"Similar Code Block ({similarity:.1%} similar)",
                            description=f"Code block similar to {block2['file_path']}:{block2['start_line']}-{block2['end_line']}",
                            file_path=block1['file_path'],
                            line_number=block1['start_line'],
                            line_range=(block1['start_line'], block1['end_line']),
                            code_snippet=block1['content'][:500] + "..." if len(block1['content']) > 500 else block1['content'],
                            suggestion="Consider extracting common logic or creating a shared utility function",
                            impact_score=min(similarity * block1['line_count'] / 5, 10.0),
                            confidence=similarity,
                            rule_id="similar_duplication",
                            fix_complexity="medium",
                            estimated_fix_time=int(block1['line_count'] * 2.5)
                        )
                        issues.append(issue)
        
        except Exception as e:
            logger.warning(f"Similar blocks analysis failed: {str(e)}")
        
        return issues
    
    async def _analyze_function_duplicates(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Find duplicate or similar functions"""
        issues = []
        
        try:
            # Collect all functions
            all_functions = []
            
            for file_info in files:
                if file_info.functions:
                    for func in file_info.functions:
                        func_info = {
                            'name': func.get('name', 'unknown'),
                            'file_path': file_info.relative_path,
                            'file_hash': file_info.hash,
                            'start_line': func.get('line_start', 0),
                            'end_line': func.get('line_end', func.get('line_start', 0)),
                            'args': func.get('args', []),
                            'content': self._extract_function_content(file_info.content, func),
                        }
                        func_info['normalized'] = self._normalize_code(func_info['content'])
                        func_info['signature_hash'] = self._hash_function_signature(func_info)
                        all_functions.append(func_info)
            
            # Group functions by signature hash
            signature_groups = defaultdict(list)
            for func in all_functions:
                signature_groups[func['signature_hash']].append(func)
            
            # Find duplicate function signatures
            for sig_hash, functions in signature_groups.items():
                if len(functions) > 1:
                    for i, func in enumerate(functions):
                        other_locations = [
                            f"{f['file_path']}:{f['start_line']}"
                            for j, f in enumerate(functions) if j != i
                        ]
                        
                        issue = CodeIssue(
                            id=f"func_dup_{func['file_hash']}_{func['start_line']}",
                            category=IssueCategory.DUPLICATION,
                            severity=IssueSeverity.MEDIUM,
                            title=f"Duplicate Function: {func['name']}",
                            description=f"Function '{func['name']}' has similar signatures in: {', '.join(other_locations)}",
                            file_path=func['file_path'],
                            line_number=func['start_line'],
                            line_range=(func['start_line'], func['end_line']),
                            code_snippet=func['content'][:500] + "..." if len(func['content']) > 500 else func['content'],
                            suggestion="Consider consolidating similar functions or using inheritance/composition",
                            impact_score=6.0,
                            confidence=0.8,
                            rule_id="duplicate_function",
                            fix_complexity="medium",
                            estimated_fix_time=45
                        )
                        issues.append(issue)
            
            # Find similar function implementations
            for i, func1 in enumerate(all_functions):
                for j, func2 in enumerate(all_functions[i+1:], i+1):
                    if func1['file_path'] == func2['file_path']:
                        continue
                    
                    if func1['name'] == func2['name'] and func1['signature_hash'] != func2['signature_hash']:
                        similarity = self._calculate_similarity(func1['normalized'], func2['normalized'])
                        
                        if similarity >= 0.7:  # Lower threshold for functions
                            issue = CodeIssue(
                                id=f"func_similar_{func1['file_hash']}_{func1['start_line']}_{j}",
                                category=IssueCategory.DUPLICATION,
                                severity=IssueSeverity.LOW,
                                title=f"Similar Function Implementation: {func1['name']}",
                                description=f"Function similar to {func2['file_path']}:{func2['start_line']} ({similarity:.1%} similar)",
                                file_path=func1['file_path'],
                                line_number=func1['start_line'],
                                line_range=(func1['start_line'], func1['end_line']),
                                code_snippet=func1['content'][:300] + "..." if len(func1['content']) > 300 else func1['content'],
                                suggestion="Review function implementations for potential consolidation",
                                impact_score=similarity * 5,
                                confidence=similarity,
                                rule_id="similar_function",
                                fix_complexity="medium",
                                estimated_fix_time=30
                            )
                            issues.append(issue)
        
        except Exception as e:
            logger.warning(f"Function duplication analysis failed: {str(e)}")
        
        return issues
    
    async def _analyze_class_duplicates(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Find duplicate or similar classes"""
        issues = []
        
        try:
            # Collect all classes
            all_classes = []
            
            for file_info in files:
                if file_info.classes:
                    for cls in file_info.classes:
                        class_info = {
                            'name': cls.get('name', 'unknown'),
                            'file_path': file_info.relative_path,
                            'file_hash': file_info.hash,
                            'start_line': cls.get('line_start', 0),
                            'end_line': cls.get('line_end', cls.get('line_start', 0)),
                            'methods': cls.get('methods', []),
                            'bases': cls.get('bases', []),
                        }
                        class_info['method_signature'] = self._hash_class_methods(class_info)
                        all_classes.append(class_info)
            
            # Find classes with similar method signatures
            method_groups = defaultdict(list)
            for cls in all_classes:
                method_groups[cls['method_signature']].append(cls)
            
            for method_sig, classes in method_groups.items():
                if len(classes) > 1:
                    for i, cls in enumerate(classes):
                        other_locations = [
                            f"{c['file_path']}:{c['start_line']}"
                            for j, c in enumerate(classes) if j != i
                        ]
                        
                        issue = CodeIssue(
                            id=f"class_dup_{cls['file_hash']}_{cls['start_line']}",
                            category=IssueCategory.DUPLICATION,
                            severity=IssueSeverity.MEDIUM,
                            title=f"Similar Class Structure: {cls['name']}",
                            description=f"Class '{cls['name']}' has similar method structure to: {', '.join(other_locations)}",
                            file_path=cls['file_path'],
                            line_number=cls['start_line'],
                            code_snippet=f"class {cls['name']}({', '.join(cls['bases'])}): # {len(cls['methods'])} methods",
                            suggestion="Consider using inheritance, composition, or extracting common interface",
                            impact_score=5.0,
                            confidence=0.7,
                            rule_id="similar_class_structure",
                            fix_complexity="hard",
                            estimated_fix_time=60
                        )
                        issues.append(issue)
        
        except Exception as e:
            logger.warning(f"Class duplication analysis failed: {str(e)}")
        
        return issues
    
    async def _analyze_copy_paste_patterns(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Detect copy-paste programming patterns"""
        issues = []
        
        try:
            # Look for common copy-paste patterns
            for file_info in files:
                lines = file_info.content.splitlines()
                
                # Find repeated variable name patterns (common copy-paste indicator)
                variable_patterns = self._find_variable_patterns(lines)
                
                for pattern, occurrences in variable_patterns.items():
                    if len(occurrences) > 3:  # Pattern repeated more than 3 times
                        # Check if these are likely copy-paste instances
                        similar_blocks = []
                        for line_num, line_content in occurrences:
                            # Get surrounding context
                            start = max(0, line_num - 2)
                            end = min(len(lines), line_num + 3)
                            context = '\n'.join(lines[start:end])
                            similar_blocks.append((line_num, context))
                        
                        # Calculate similarity between blocks
                        high_similarity_count = 0
                        for i in range(len(similar_blocks)):
                            for j in range(i + 1, len(similar_blocks)):
                                similarity = self._calculate_similarity(similar_blocks[i][1], similar_blocks[j][1])
                                if similarity > 0.8:
                                    high_similarity_count += 1
                        
                        if high_similarity_count > 0:
                            first_occurrence = occurrences[0]
                            
                            issue = CodeIssue(
                                id=f"copy_paste_{file_info.hash}_{first_occurrence[0]}",
                                category=IssueCategory.DUPLICATION,
                                severity=IssueSeverity.LOW,
                                title=f"Potential Copy-Paste Pattern: {pattern}",
                                description=f"Variable pattern '{pattern}' repeated {len(occurrences)} times, suggesting copy-paste programming",
                                file_path=file_info.relative_path,
                                line_number=first_occurrence[0],
                                code_snippet=first_occurrence[1],
                                suggestion="Consider extracting repeated logic into functions or using loops/data structures",
                                impact_score=min(len(occurrences), 8.0),
                                confidence=0.6,
                                rule_id="copy_paste_pattern",
                                fix_complexity="medium",
                                estimated_fix_time=len(occurrences) * 5
                            )
                            issues.append(issue)
        
        except Exception as e:
            logger.warning(f"Copy-paste pattern analysis failed: {str(e)}")
        
        return issues
    
    def _extract_code_blocks(self, file_info: FileInfo) -> List[Dict[str, Any]]:
        """Extract meaningful code blocks from a file"""
        blocks = []
        lines = file_info.content.splitlines()
        
        # Simple block extraction based on indentation and blank lines
        current_block = []
        current_start = 0
        base_indent = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                if current_block and len(current_block) >= self.min_duplicate_lines:
                    block_content = '\n'.join(current_block)
                    blocks.append({
                        'content': block_content,
                        'hash': hashlib.md5(block_content.encode()).hexdigest(),
                        'start_line': current_start + 1,
                        'end_line': i,
                        'line_count': len(current_block),
                        'file_path': file_info.relative_path,
                        'file_hash': file_info.hash
                    })
                current_block = []
                base_indent = None
                continue
            
            # Determine block boundaries based on indentation
            indent = len(line) - len(line.lstrip())
            
            if base_indent is None:
                base_indent = indent
                current_start = i
                current_block = [line]
            elif indent >= base_indent:
                current_block.append(line)
            else:
                # End of block
                if current_block and len(current_block) >= self.min_duplicate_lines:
                    block_content = '\n'.join(current_block)
                    blocks.append({
                        'content': block_content,
                        'hash': hashlib.md5(block_content.encode()).hexdigest(),
                        'start_line': current_start + 1,
                        'end_line': i,
                        'line_count': len(current_block),
                        'file_path': file_info.relative_path,
                        'file_hash': file_info.hash
                    })
                
                # Start new block
                base_indent = indent
                current_start = i
                current_block = [line]
        
        # Handle last block
        if current_block and len(current_block) >= self.min_duplicate_lines:
            block_content = '\n'.join(current_block)
            blocks.append({
                'content': block_content,
                'hash': hashlib.md5(block_content.encode()).hexdigest(),
                'start_line': current_start + 1,
                'end_line': len(lines),
                'line_count': len(current_block),
                'file_path': file_info.relative_path,
                'file_hash': file_info.hash
            })
        
        return blocks
    
    def _extract_normalized_blocks(self, file_info: FileInfo) -> List[Dict[str, Any]]:
        """Extract and normalize code blocks for similarity comparison"""
        blocks = self._extract_code_blocks(file_info)
        
        for block in blocks:
            block['normalized'] = self._normalize_code(block['content'])
        
        return blocks
    
    def _normalize_code(self, code: str) -> str:
        """Normalize code for similarity comparison"""
        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Normalize whitespace
        code = re.sub(r'\s+', ' ', code)
        
        # Normalize variable names (replace with placeholders)
        code = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', 'VAR', code)
        
        # Normalize string literals
        code = re.sub(r'"[^"]*"', '"STRING"', code)
        code = re.sub(r"'[^']*'", "'STRING'", code)
        
        # Normalize numbers
        code = re.sub(r'\b\d+\b', 'NUM', code)
        
        return code.strip()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text blocks"""
        if DIFFLIB_AVAILABLE:
            return difflib.SequenceMatcher(None, text1, text2).ratio()
        else:
            # Alternative similarity calculation using Jaccard similarity
            set1 = set(text1.split())
            set2 = set(text2.split())
            
            if not set1 and not set2:
                return 1.0
            if not set1 or not set2:
                return 0.0
                
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            
            return intersection / union if union > 0 else 0.0
    
    def _extract_function_content(self, file_content: str, func_info: Dict[str, Any]) -> str:
        """Extract function content from file"""
        lines = file_content.splitlines()
        start = max(0, func_info.get('line_start', 1) - 1)
        end = min(len(lines), func_info.get('line_end', start + 1))
        
        return '\n'.join(lines[start:end])
    
    def _hash_function_signature(self, func_info: Dict[str, Any]) -> str:
        """Create hash of function signature"""
        signature = f"{func_info['name']}({','.join(func_info['args'])})"
        return hashlib.md5(signature.encode()).hexdigest()
    
    def _hash_class_methods(self, class_info: Dict[str, Any]) -> str:
        """Create hash of class method signatures"""
        methods_sig = ','.join(sorted(class_info['methods']))
        return hashlib.md5(methods_sig.encode()).hexdigest()
    
    def _find_variable_patterns(self, lines: List[str]) -> Dict[str, List[Tuple[int, str]]]:
        """Find repeated variable naming patterns"""
        patterns = defaultdict(list)
        
        for i, line in enumerate(lines):
            # Look for variable assignments
            matches = re.findall(r'(\w+)\s*=\s*', line)
            for var_name in matches:
                # Create pattern (e.g., "data1", "data2" -> "data*")
                base_pattern = re.sub(r'\d+$', '*', var_name)
                if base_pattern != var_name:  # Only if pattern was found
                    patterns[base_pattern].append((i + 1, line.strip()))
        
        return {k: v for k, v in patterns.items() if len(v) > 2}
    
    def _deduplicate_issues(self, issues: List[CodeIssue]) -> List[CodeIssue]:
        """Remove duplicate issues"""
        seen = set()
        unique_issues = []
        
        for issue in issues:
            key = (issue.file_path, issue.line_number, issue.title)
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        return unique_issues
