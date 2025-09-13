"""
Command Line Interface for Quantum Code Inspector
Provides CLI access to code analysis functionality
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from typing import Optional, List
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.agents.quality_agent import QualityIntelligenceAgent
from app.utils.config import get_settings
from app.models.analysis import IssueSeverity

console = Console()

@click.group()
@click.version_option(version="1.0.0", prog_name="Quantum Code Inspector")
def cli():
    """🔍 Quantum Code Inspector - AI-powered Code Quality Analysis"""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for results (JSON)')
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'detailed']), default='table', help='Output format')
@click.option('--severity', '-s', type=click.Choice(['critical', 'high', 'medium', 'low', 'info']), default='medium', help='Minimum severity level')
@click.option('--category', '-c', multiple=True, help='Filter by issue categories')
@click.option('--no-progress', is_flag=True, help='Disable progress indicators')
def analyze(path: str, output: Optional[str], format: str, severity: str, category: List[str], no_progress: bool):
    """Analyze code repository for quality issues"""
    
    if not no_progress:
        console.print(Panel.fit("🚀 Quantum Code Inspector", style="bold blue"))
    
    async def run_analysis():
        try:
            # Initialize agent
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                disable=no_progress
            ) as progress:
                
                init_task = progress.add_task("Initializing AI agent...", total=None)
                agent = QualityIntelligenceAgent()
                
                # Try to initialize, but don't fail if it doesn't work
                try:
                    await agent.initialize()
                except Exception as e:
                    console.print(f"⚠️  Agent initialization warning: {e}", style="yellow")
                
                progress.update(init_task, completed=True)
                
                # Run analysis
                analysis_task = progress.add_task("Analyzing codebase...", total=None)
                result = await agent.analyze_codebase(path)
                progress.update(analysis_task, completed=True)
            
            # Filter results
            filtered_issues = _filter_issues(result.issues, severity, category)
            
            # Output results
            if output:
                _save_results(result, output, filtered_issues)
                console.print(f"✅ Results saved to {output}")
            else:
                _display_results(result, filtered_issues, format)
                
        except Exception as e:
            console.print(f"❌ Analysis failed: {str(e)}", style="bold red")
            sys.exit(1)
    
    asyncio.run(run_analysis())

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--question', '-q', prompt=True, help='Question to ask about the codebase')
@click.option('--context', '-c', help='Additional context for the question')
def ask(path: str, question: str, context: Optional[str]):
    """Ask questions about the analyzed codebase"""
    
    async def run_qa():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                init_task = progress.add_task("Initializing AI agent...", total=None)
                agent = QualityIntelligenceAgent()
                
                # Try to initialize, but don't fail if it doesn't work
                try:
                    await agent.initialize()
                except Exception as e:
                    console.print(f"⚠️  Agent initialization warning: {e}", style="yellow")
                
                progress.update(init_task, completed=True)
                
                # First analyze the codebase
                analysis_task = progress.add_task("Analyzing codebase...", total=None)
                await agent.analyze_codebase(path)
                progress.update(analysis_task, completed=True)
                
                # Ask question
                qa_task = progress.add_task("Processing question...", total=None)
                response = await agent.answer_question(question, context)
                progress.update(qa_task, completed=True)
            
            # Display response
            console.print(Panel(response.answer, title="🤖 AI Response", border_style="green"))
            
            if response.follow_up_questions:
                console.print("\n💡 Suggested follow-up questions:")
                for i, follow_up in enumerate(response.follow_up_questions, 1):
                    console.print(f"  {i}. {follow_up}")
                    
        except Exception as e:
            console.print(f"❌ Q&A failed: {str(e)}", style="bold red")
            sys.exit(1)
    
    asyncio.run(run_qa())

@cli.command()
@click.argument('repo_url')
@click.option('--branch', '-b', default='main', help='Git branch to analyze')
@click.option('--output', '-o', type=click.Path(), help='Output file for results (JSON)')
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'detailed']), default='table', help='Output format')
def analyze_repo(repo_url: str, branch: str, output: Optional[str], format: str):
    """Analyze GitHub repository"""
    
    async def run_repo_analysis():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                init_task = progress.add_task("Initializing AI agent...", total=None)
                agent = QualityIntelligenceAgent()
                await agent.initialize()
                progress.update(init_task, completed=True)
                
                # Clone and analyze repository
                clone_task = progress.add_task(f"Cloning repository from {repo_url}...", total=None)
                from app.utils.file_handler import FileHandler
                file_handler = FileHandler()
                temp_dir = await file_handler.clone_repository(repo_url, branch)
                progress.update(clone_task, completed=True)
                
                try:
                    analysis_task = progress.add_task("Analyzing repository...", total=None)
                    result = await agent.analyze_codebase(temp_dir)
                    progress.update(analysis_task, completed=True)
                    
                    # Output results
                    if output:
                        _save_results(result, output, result.issues)
                        console.print(f"✅ Results saved to {output}")
                    else:
                        _display_results(result, result.issues, format)
                        
                finally:
                    # Cleanup
                    await file_handler.cleanup_temp_dir(temp_dir)
                    
        except Exception as e:
            console.print(f"❌ Repository analysis failed: {str(e)}", style="bold red")
            sys.exit(1)
    
    asyncio.run(run_repo_analysis())

@cli.command()
def config():
    """Show current configuration"""
    settings = get_settings()
    
    config_table = Table(title="Configuration")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    
    config_table.add_row("OpenAI Model", settings.openai_model)
    config_table.add_row("Max File Size", f"{settings.max_file_size // (1024*1024)} MB")
    config_table.add_row("Max Files", str(settings.max_files_per_analysis))
    config_table.add_row("Analysis Timeout", f"{settings.analysis_timeout} seconds")
    
    console.print(config_table)

def _filter_issues(issues, min_severity: str, categories: List[str]):
    """Filter issues by severity and category"""
    severity_order = {
        'info': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4
    }
    
    min_level = severity_order.get(min_severity, 2)
    
    filtered = []
    for issue in issues:
        issue_level = severity_order.get(issue.severity.value, 0)
        
        if issue_level >= min_level:
            if not categories or issue.category.value in categories:
                filtered.append(issue)
    
    return filtered

def _display_results(result, issues, format: str):
    """Display analysis results"""
    
    # Summary
    summary_table = Table(title="📊 Analysis Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")
    
    summary_table.add_row("Overall Score", f"{result.quality_metrics.overall_score}/100")
    summary_table.add_row("Files Analyzed", str(result.files_analyzed))
    summary_table.add_row("Lines Analyzed", str(result.lines_analyzed))
    summary_table.add_row("Issues Found", str(len(issues)))
    summary_table.add_row("Processing Time", f"{result.processing_time:.2f}s")
    
    console.print(summary_table)
    console.print()
    
    if format == 'detailed':
        _display_detailed_results(result, issues)
    elif format == 'json':
        console.print(json.dumps(result.dict(), indent=2, default=str))
    else:
        _display_table_results(issues)

def _display_detailed_results(result, issues):
    """Display detailed analysis results"""
    
    # Quality Metrics
    metrics_table = Table(title="🎯 Quality Metrics")
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Score", style="green")
    
    metrics = result.quality_metrics
    metrics_table.add_row("Maintainability Index", f"{metrics.maintainability_index:.1f}")
    metrics_table.add_row("Security Score", f"{metrics.security_score:.1f}")
    metrics_table.add_row("Performance Score", f"{metrics.performance_score:.1f}")
    metrics_table.add_row("Documentation Coverage", f"{metrics.documentation_coverage:.1f}%")
    
    console.print(metrics_table)
    console.print()
    
    # Language Statistics
    lang_table = Table(title="📝 Language Statistics")
    lang_table.add_column("Language", style="cyan")
    lang_table.add_column("Files", style="green")
    lang_table.add_column("Lines", style="green")
    lang_table.add_column("Percentage", style="yellow")
    
    for lang_stat in result.language_stats:
        lang_table.add_row(
            lang_stat.language,
            str(lang_stat.files_count),
            str(lang_stat.lines_of_code),
            f"{lang_stat.percentage:.1f}%"
        )
    
    console.print(lang_table)
    console.print()
    
    # Issues by severity
    _display_issues_by_severity(issues)
    
    # Recommendations
    if result.recommendations:
        console.print("💡 Recommendations:")
        for i, rec in enumerate(result.recommendations, 1):
            console.print(f"  {i}. {rec}")

def _display_table_results(issues):
    """Display issues in table format"""
    
    if not issues:
        console.print("✅ No issues found!", style="bold green")
        return
    
    # Group issues by severity
    _display_issues_by_severity(issues)

def _display_issues_by_severity(issues):
    """Display issues grouped by severity"""
    
    from collections import defaultdict
    issues_by_severity = defaultdict(list)
    
    for issue in issues:
        issues_by_severity[issue.severity.value].append(issue)
    
    severity_colors = {
        'critical': 'bold red',
        'high': 'red',
        'medium': 'yellow',
        'low': 'blue',
        'info': 'green'
    }
    
    for severity in ['critical', 'high', 'medium', 'low', 'info']:
        severity_issues = issues_by_severity.get(severity, [])
        if not severity_issues:
            continue
        
        color = severity_colors.get(severity, 'white')
        console.print(f"\n{severity.upper()} Issues ({len(severity_issues)}):", style=f"bold {color}")
        
        issues_table = Table()
        issues_table.add_column("File", style="cyan", max_width=30)
        issues_table.add_column("Line", style="green", width=6)
        issues_table.add_column("Issue", style="white")
        issues_table.add_column("Category", style="magenta", width=12)
        
        for issue in severity_issues[:100]:  # Show top 10 per severity
            issues_table.add_row(
                issue.file_path,
                str(issue.line_number) if issue.line_number else "-",
                issue.title,
                issue.category.value
            )
        
        console.print(issues_table)
        
        if len(severity_issues) > 100:
            console.print(f"... and {len(severity_issues) - 100} more {severity} issues")

def _save_results(result, output_path: str, issues):
    """Save results to file"""
    output_data = {
        'summary': {
            'overall_score': result.quality_metrics.overall_score,
            'files_analyzed': result.files_analyzed,
            'lines_analyzed': result.lines_analyzed,
            'total_issues': len(issues),
            'processing_time': result.processing_time
        },
        'quality_metrics': result.quality_metrics.dict(),
        'language_stats': [ls.dict() for ls in result.language_stats],
        'issues': [issue.dict() for issue in issues],
        'recommendations': result.recommendations,
        'analysis_id': result.analysis_id,
        'timestamp': result.timestamp
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)

def main():
    """Main entry point for CLI"""
    cli()


if __name__ == '__main__':
    main()