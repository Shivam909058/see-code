#!/usr/bin/env python3
"""Test the analysis system to identify any remaining issues"""

import asyncio
import tempfile
import os
from pathlib import Path

# Test if we can import all modules without errors
def test_imports():
    try:
        from app.agents.quality_agent import QualityIntelligenceAgent
        from app.models.analysis import CodeIssue, IssueSeverity, IssueCategory
        from app.utils.code_parser import CodeParser
        from app.analyzers.security_analyzer import SecurityAnalyzer
        from app.analyzers.performance_analyzer import PerformanceAnalyzer
        from app.analyzers.complexity_analyzer import ComplexityAnalyzer
        from app.analyzers.duplication_analyzer import DuplicationAnalyzer
        from app.analyzers.ast_analyzer import ASTAnalyzer
        
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_code_issue_creation():
    try:
        from app.models.analysis import CodeIssue, IssueSeverity, IssueCategory
        
        # Test creating a CodeIssue with all required fields
        issue = CodeIssue(
            category=IssueCategory.SECURITY,
            severity=IssueSeverity.HIGH,
            title="Test Issue",
            description="Test description",
            file_path="test.py",
            line_number=10,
            suggestion="Fix this issue",
            impact_score=7.5,
            confidence=0.8
        )
        
        print(f"✅ CodeIssue created successfully: {issue.title}")
        return True
    except Exception as e:
        print(f"❌ CodeIssue creation error: {e}")
        return False

async def test_analyzers():
    try:
        from app.utils.code_parser import CodeParser
        from app.analyzers.security_analyzer import SecurityAnalyzer
        
        # Create a simple test file
        test_code = '''
def test_function():
    password = "hardcoded_password_123"
    return password
'''
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Test code parser
            parser = CodeParser()
            file_info = await parser.parse_file(temp_file)
            
            print(f"✅ Code parser successful: {file_info.language}, {file_info.line_count} lines")
            
            # Test security analyzer
            security_analyzer = SecurityAnalyzer()
            issues = await security_analyzer.analyze([file_info])
            
            print(f"✅ Security analyzer successful: {len(issues)} issues found")
            
            return True
            
        finally:
            # Clean up
            os.unlink(temp_file)
            
    except Exception as e:
        print(f"❌ Analyzer test error: {e}")
        return False

async def main():
    print("🧪 Testing system components...")
    
    # Test imports
    if not test_imports():
        return
    
    # Test CodeIssue creation
    if not test_code_issue_creation():
        return
    
    # Test analyzers
    if not await test_analyzers():
        return
    
    print("✅ All tests passed! System should be working correctly.")

if __name__ == "__main__":
    asyncio.run(main())
