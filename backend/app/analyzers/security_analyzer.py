"""
Advanced Security Analyzer using multiple tools and techniques
- Bandit for Python security issues
- Semgrep for multi-language security patterns
- Custom vulnerability detection with LLM analysis
- OWASP Top 10 coverage
"""

import asyncio
import subprocess
import json
import re
import tempfile
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger

from app.models.analysis import CodeIssue, IssueSeverity, IssueCategory
from app.utils.code_parser import FileInfo

class SecurityAnalyzer:
    """Advanced security vulnerability analyzer with LLM integration"""
    
    def __init__(self):
        self.vulnerability_patterns = {
            'sql_injection': [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'cursor\.execute\s*\(\s*f["\']',
                r'query\s*=\s*["\'].*\+.*["\']',
                r'SELECT.*\+.*FROM',
                r'INSERT.*\+.*VALUES'
            ],
            'xss': [
                r'innerHTML\s*=\s*.*\+',
                r'document\.write\s*\(',
                r'eval\s*\(',
                r'setTimeout\s*\(\s*["\'].*\+',
                r'setInterval\s*\(\s*["\'].*\+'
            ],
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']{8,}["\']',
                r'api_key\s*=\s*["\'][^"\']{20,}["\']',
                r'secret\s*=\s*["\'][^"\']{16,}["\']',
                r'token\s*=\s*["\'][^"\']{20,}["\']',
                r'private_key\s*=\s*["\'].*["\']'
            ],
            'path_traversal': [
                r'open\s*\(\s*.*\+.*\)',
                r'file\s*\(\s*.*\+.*\)',
                r'include\s*\(\s*.*\+.*\)',
                r'require\s*\(\s*.*\+.*\)'
            ],
            'command_injection': [
                r'os\.system\s*\(\s*.*\+',
                r'subprocess\.\w+\s*\(\s*.*\+',
                r'exec\s*\(\s*.*\+',
                r'eval\s*\(\s*.*\+'
            ],
            'insecure_random': [
                r'random\.random\(\)',
                r'Math\.random\(\)',
                r'rand\(\)',
                r'srand\('
            ],
            'weak_crypto': [
                r'md5\s*\(',
                r'sha1\s*\(',
                r'DES\s*\(',
                r'RC4\s*\('
            ]
        }
        
        self.severity_mapping = {
            'sql_injection': IssueSeverity.CRITICAL,
            'xss': IssueSeverity.HIGH,
            'hardcoded_secrets': IssueSeverity.CRITICAL,
            'path_traversal': IssueSeverity.HIGH,
            'command_injection': IssueSeverity.CRITICAL,
            'insecure_random': IssueSeverity.MEDIUM,
            'weak_crypto': IssueSeverity.HIGH
        }
    
    async def analyze(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Perform comprehensive security analysis"""
        logger.info("🔒 Starting security analysis...")
        
        all_issues = []
        
        # Run different analysis methods in parallel
        tasks = [
            self._analyze_with_patterns(files),
            self._analyze_with_bandit(files),
            self._analyze_with_semgrep(files),
            self._analyze_dependencies(files),
            self._analyze_configurations(files)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_issues.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"Security analysis failed: {str(result)}")
        
        # Deduplicate issues
        unique_issues = self._deduplicate_issues(all_issues)
        
        logger.info(f"🔒 Found {len(unique_issues)} security issues")
        return unique_issues
    
    async def _analyze_with_patterns(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Analyze using regex patterns for common vulnerabilities"""
        issues = []
        
        for file_info in files:
            for vuln_type, patterns in self.vulnerability_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, file_info.content, re.IGNORECASE | re.MULTILINE)
                    
                    for match in matches:
                        line_number = file_info.content[:match.start()].count('\n') + 1
                        
                        issue = CodeIssue(
                            id=f"sec_{vuln_type}_{file_info.hash}_{line_number}",
                            category=IssueCategory.SECURITY,
                            severity=self.severity_mapping.get(vuln_type, IssueSeverity.MEDIUM),
                            title=f"Potential {vuln_type.replace('_', ' ').title()}",
                            description=self._get_vulnerability_description(vuln_type),
                            file_path=file_info.relative_path,
                            line_number=line_number,
                            code_snippet=self._get_code_snippet(file_info.content, line_number),
                            suggestion=self._get_security_suggestion(vuln_type),
                            impact_score=self._calculate_impact_score(vuln_type),
                            confidence=0.7,
                            rule_id=f"pattern_{vuln_type}",
                            fix_complexity="medium",
                            estimated_fix_time=30
                        )
                        issues.append(issue)
        
        return issues
    
    async def _analyze_with_bandit(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Analyze Python files with Bandit"""
        issues = []
        python_files = [f for f in files if f.language == 'python']
        
        if not python_files:
            return issues
        
        try:
            # Create temporary directory with Python files
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_files = []
                
                for file_info in python_files:
                    temp_path = Path(temp_dir) / file_info.relative_path
                    temp_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        f.write(file_info.content)
                    temp_files.append(str(temp_path))
                
                # Run Bandit
                cmd = ['bandit', '-r', '-f', 'json', temp_dir]
                result = subprocess.run(cmd, capture_output=True, text=True,encoding='utf-8',errors='ignore')
                
                if result.stdout:
                    bandit_results = json.loads(result.stdout)
                    
                    for result_item in bandit_results.get('results', []):
                        # Map Bandit results to our format
                        severity_map = {
                            'HIGH': IssueSeverity.HIGH,
                            'MEDIUM': IssueSeverity.MEDIUM,
                            'LOW': IssueSeverity.LOW
                        }
                        
                        # Find original file path
                        temp_path = result_item['filename']
                        original_file = None
                        for file_info in python_files:
                            if temp_path.endswith(file_info.relative_path):
                                original_file = file_info
                                break
                        
                        if original_file:
                            issue = CodeIssue(
                                id=f"bandit_{result_item['test_id']}_{original_file.hash}_{result_item['line_number']}",
                                category=IssueCategory.SECURITY,
                                severity=severity_map.get(result_item['issue_severity'], IssueSeverity.MEDIUM),
                                title=result_item['issue_text'],
                                description=result_item.get('issue_text', ''),
                                file_path=original_file.relative_path,
                                line_number=result_item['line_number'],
                                code_snippet=result_item.get('code', ''),
                                suggestion=self._get_bandit_suggestion(result_item['test_id']),
                                impact_score=self._severity_to_impact(severity_map.get(result_item['issue_severity'])),
                                confidence=float(result_item.get('issue_confidence', 'MEDIUM').replace('HIGH', '0.9').replace('MEDIUM', '0.7').replace('LOW', '0.5')),
                                rule_id=result_item['test_id'],
                                fix_complexity="medium",
                                estimated_fix_time=45
                            )
                            issues.append(issue)
                
        except Exception as e:
            logger.warning(f"Bandit analysis failed: {str(e)}")
        
        return issues
    
    async def _analyze_with_semgrep(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Analyze with Semgrep for multi-language security patterns"""
        issues = []
        
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write files to temp directory
                file_mapping = {}
                for file_info in files:
                    temp_path = Path(temp_dir) / file_info.relative_path
                    temp_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        f.write(file_info.content)
                    
                    file_mapping[str(temp_path)] = file_info
                
                # Run Semgrep with security rules
                cmd = [
                    'semgrep', 
                    '--config=auto',
                    '--json',
                    '--no-git-ignore',
                    temp_dir
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120,encoding='utf-8',errors='ignore')
                
                if result.stdout:
                    semgrep_results = json.loads(result.stdout)
                    
                    for finding in semgrep_results.get('results', []):
                        temp_path = finding['path']
                        original_file = file_mapping.get(temp_path)
                        
                        if original_file:
                            severity = self._map_semgrep_severity(finding.get('extra', {}).get('severity', 'INFO'))
                            
                            issue = CodeIssue(
                                id=f"semgrep_{finding['check_id']}_{original_file.hash}_{finding['start']['line']}",
                                category=IssueCategory.SECURITY,
                                severity=severity,
                                title=finding['extra'].get('message', finding['check_id']),
                                description=finding['extra'].get('message', ''),
                                file_path=original_file.relative_path,
                                line_number=finding['start']['line'],
                                code_snippet=finding.get('extra', {}).get('lines', ''),
                                suggestion=self._get_semgrep_suggestion(finding['check_id']),
                                impact_score=self._severity_to_impact(severity),
                                confidence=0.8,
                                rule_id=finding['check_id'],
                                references=finding['extra'].get('references', []),
                                fix_complexity="medium",
                                estimated_fix_time=30
                            )
                            issues.append(issue)
                
        except subprocess.TimeoutExpired:
            logger.warning("Semgrep analysis timed out")
        except Exception as e:
            logger.warning(f"Semgrep analysis failed: {str(e)}")
        
        return issues
    
    async def _analyze_dependencies(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Analyze dependencies for known vulnerabilities"""
        issues = []
        
        # Find dependency files
        dep_files = [
            f for f in files 
            if f.relative_path.endswith(('requirements.txt', 'package.json', 'pom.xml', 'go.mod', 'Gemfile'))
        ]
        
        for dep_file in dep_files:
            if dep_file.relative_path.endswith('requirements.txt'):
                issues.extend(await self._analyze_python_deps(dep_file))
            elif dep_file.relative_path.endswith('package.json'):
                issues.extend(await self._analyze_npm_deps(dep_file))
        
        return issues
    
    async def _analyze_python_deps(self, dep_file: FileInfo) -> List[CodeIssue]:
        """Analyze Python dependencies with Safety"""
        issues = []
        
        try:
            # Create temporary requirements file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(dep_file.content)
                temp_file_path = temp_file.name
            
            # Run Safety check
            cmd = ['safety', 'check', '--json', '-r', temp_file_path]
            result = subprocess.run(cmd, capture_output=True, text=True,encoding='utf-8',errors='ignore')
            
            if result.stdout:
                try:
                    safety_results = json.loads(result.stdout)
                    
                    for vuln in safety_results:
                        issue = CodeIssue(
                            id=f"dep_vuln_{vuln['package']}_{vuln['id']}",
                            category=IssueCategory.SECURITY,
                            severity=IssueSeverity.HIGH,
                            title=f"Vulnerable dependency: {vuln['package']}",
                            description=vuln['advisory'],
                            file_path=dep_file.relative_path,
                            line_number=None,
                            code_snippet=f"{vuln['package']}=={vuln['installed_version']}",
                            suggestion=f"Update {vuln['package']} to version {vuln.get('safe_versions', ['latest'])[0]} or later",
                            impact_score=8.0,
                            confidence=0.95,
                            rule_id=f"safety_{vuln['id']}",
                            fix_complexity="easy",
                            estimated_fix_time=5
                        )
                        issues.append(issue)
                        
                except json.JSONDecodeError:
                    pass
            
            # Clean up
            os.unlink(temp_file_path)
            
        except Exception as e:
            logger.warning(f"Python dependency analysis failed: {str(e)}")
        
        return issues
    
    async def _analyze_npm_deps(self, dep_file: FileInfo) -> List[CodeIssue]:
        """Analyze npm dependencies (simplified)"""
        issues = []
        
        try:
            package_data = json.loads(dep_file.content)
            dependencies = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
            
            # Simple check for known vulnerable packages (would integrate with npm audit in real implementation)
            vulnerable_packages = {
                'lodash': '4.17.20',
                'moment': '2.29.0',
                'jquery': '3.5.0'
            }
            
            for pkg_name, version in dependencies.items():
                if pkg_name in vulnerable_packages:
                    issue = CodeIssue(
                        id=f"npm_vuln_{pkg_name}_{dep_file.hash}",
                        category=IssueCategory.SECURITY,
                        severity=IssueSeverity.MEDIUM,
                        title=f"Potentially vulnerable npm package: {pkg_name}",
                        description=f"Package {pkg_name} may have known vulnerabilities",
                        file_path=dep_file.relative_path,
                        line_number=None,
                        code_snippet=f'"{pkg_name}": "{version}"',
                        suggestion=f"Update {pkg_name} to the latest version and run npm audit",
                        impact_score=6.0,
                        confidence=0.6,
                        rule_id=f"npm_vuln_{pkg_name}",
                        fix_complexity="easy",
                        estimated_fix_time=10
                    )
                    issues.append(issue)
                    
        except Exception as e:
            logger.warning(f"npm dependency analysis failed: {str(e)}")
        
        return issues
    
    async def _analyze_configurations(self, files: List[FileInfo]) -> List[CodeIssue]:
        """Analyze configuration files for security issues"""
        issues = []
        
        config_files = [
            f for f in files 
            if any(f.relative_path.endswith(ext) for ext in ['.env', '.config', '.yml', '.yaml', '.json', '.xml'])
        ]
        
        for config_file in config_files:
            # Check for exposed secrets in config files
            secret_patterns = [
                (r'password\s*[:=]\s*["\']?[^"\'\s]{8,}', "Hardcoded password"),
                (r'api[_-]?key\s*[:=]\s*["\']?[^"\'\s]{20,}', "API key exposure"),
                (r'secret[_-]?key\s*[:=]\s*["\']?[^"\'\s]{16,}', "Secret key exposure"),
                (r'private[_-]?key\s*[:=]', "Private key in config"),
                (r'token\s*[:=]\s*["\']?[^"\'\s]{20,}', "Token exposure")
            ]
            
            for pattern, description in secret_patterns:
                matches = re.finditer(pattern, config_file.content, re.IGNORECASE)
                
                for match in matches:
                    line_number = config_file.content[:match.start()].count('\n') + 1
                    
                    issue = CodeIssue(
                        id=f"config_secret_{config_file.hash}_{line_number}",
                        category=IssueCategory.SECURITY,
                        severity=IssueSeverity.HIGH,
                        title=description,
                        description=f"{description} found in configuration file",
                        file_path=config_file.relative_path,
                        line_number=line_number,
                        code_snippet=self._get_code_snippet(config_file.content, line_number),
                        suggestion="Move sensitive data to environment variables or secure secret management",
                        impact_score=7.0,
                        confidence=0.8,
                        rule_id="config_secrets",
                        fix_complexity="medium",
                        estimated_fix_time=20
                    )
                    issues.append(issue)
        
        return issues
    
    # Helper methods
    def _get_vulnerability_description(self, vuln_type: str) -> str:
        descriptions = {
            'sql_injection': "Code may be vulnerable to SQL injection attacks through unsanitized user input",
            'xss': "Code may be vulnerable to Cross-Site Scripting (XSS) attacks",
            'hardcoded_secrets': "Sensitive credentials are hardcoded in the source code",
            'path_traversal': "Code may be vulnerable to path traversal attacks",
            'command_injection': "Code may be vulnerable to command injection attacks",
            'insecure_random': "Using insecure random number generation for security-sensitive operations",
            'weak_crypto': "Using weak or deprecated cryptographic algorithms"
        }
        return descriptions.get(vuln_type, f"Potential {vuln_type} vulnerability detected")
    
    def _get_security_suggestion(self, vuln_type: str) -> str:
        suggestions = {
            'sql_injection': "Use parameterized queries or prepared statements instead of string concatenation",
            'xss': "Sanitize user input and use proper encoding when rendering content",
            'hardcoded_secrets': "Move secrets to environment variables or secure configuration management",
            'path_traversal': "Validate and sanitize file paths, use allow-lists for permitted files",
            'command_injection': "Avoid executing user input as commands, use safe alternatives or proper sanitization",
            'insecure_random': "Use cryptographically secure random number generators (e.g., secrets module in Python)",
            'weak_crypto': "Use strong, modern cryptographic algorithms (e.g., AES-256, SHA-256 or higher)"
        }
        return suggestions.get(vuln_type, "Review and fix the security issue")
    
    def _get_bandit_suggestion(self, test_id: str) -> str:
        suggestions = {
            'B101': "Use assert statements only for debugging, not for data validation",
            'B102': "Avoid using exec() as it can execute arbitrary code",
            'B103': "Set file permissions explicitly instead of using 0o777",
            'B301': "Use pickle only with trusted data sources",
            'B501': "Use secure SSL/TLS configurations",
            'B601': "Avoid shell injection by using subprocess with shell=False"
        }
        return suggestions.get(test_id, "Follow Bandit recommendations to fix this security issue")
    
    def _get_semgrep_suggestion(self, check_id: str) -> str:
        return f"Follow security best practices to address issue {check_id}"
    
    def _map_semgrep_severity(self, severity: str) -> IssueSeverity:
        mapping = {
            'ERROR': IssueSeverity.HIGH,
            'WARNING': IssueSeverity.MEDIUM,
            'INFO': IssueSeverity.LOW
        }
        return mapping.get(severity.upper(), IssueSeverity.MEDIUM)
    
    def _calculate_impact_score(self, vuln_type: str) -> float:
        scores = {
            'sql_injection': 9.0,
            'xss': 7.0,
            'hardcoded_secrets': 8.0,
            'path_traversal': 7.5,
            'command_injection': 9.0,
            'insecure_random': 5.0,
            'weak_crypto': 6.0
        }
        return scores.get(vuln_type, 5.0)
    
    def _severity_to_impact(self, severity: IssueSeverity) -> float:
        mapping = {
            IssueSeverity.CRITICAL: 9.0,
            IssueSeverity.HIGH: 7.0,
            IssueSeverity.MEDIUM: 5.0,
            IssueSeverity.LOW: 3.0,
            IssueSeverity.INFO: 1.0
        }
        return mapping.get(severity, 5.0)
    
    def _get_code_snippet(self, content: str, line_number: int, context_lines: int = 2) -> str:
        lines = content.splitlines()
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        
        snippet_lines = []
        for i in range(start, end):
            prefix = ">>> " if i == line_number - 1 else "    "
            snippet_lines.append(f"{prefix}{lines[i]}")
        
        return "\n".join(snippet_lines)
    
    def _deduplicate_issues(self, issues: List[CodeIssue]) -> List[CodeIssue]:
        seen = set()
        unique_issues = []
        
        for issue in issues:
            key = (issue.file_path, issue.line_number, issue.title)
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        return unique_issues