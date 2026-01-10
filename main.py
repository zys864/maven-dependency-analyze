#!/usr/bin/env python3
"""Main entry point for Maven dependency analysis tool."""

import click
from rich.console import Console
from rich.table import Table

from src.parser.tree_parser import TreeParser
from src.parser.analysis_parser import AnalysisParser
from src.exporter.tree_visualizer import TreeVisualizer
from src.analyzer.tree_analyzer import TreeAnalyzer
from src.analyzer.redundancy_analyzer import RedundancyAnalyzer
from src.exporter.excel_exporter import ExcelExporter


@click.group()
def cli():
    """Maven Dependency Analysis Tool."""
    pass


@cli.command()
@click.option('--tree', '-t', required=True, type=click.Path(exists=True),
              help='Path to dependency tree JSON file')
@click.option('--max-depth', '-d', default=None, type=int,
              help='Maximum depth to display in tree')
@click.option('--scope', '-s', default=None,
              help='Filter by scope (compile, test, runtime, etc.)')
def show_tree(tree, max_depth, scope):
    """Display the dependency tree."""
    console = Console()
    
    try:
        parser = TreeParser()
        tree_obj = parser.parse(tree)
        
        visualizer = TreeVisualizer()
        console.print(f"[bold blue]Dependency Tree for:[/bold blue] {tree_obj.root.group_id}:{tree_obj.root.artifact_id}")
        console.print(f"[bold]Total Dependencies:[/bold] {tree_obj.total_dependencies}")
        console.print(f"[bold]Max Depth:[/bold] {tree_obj.max_depth}")
        console.print()
        
        visualizer.print_tree(
            tree_obj,
            show_scope=True,
            max_depth=max_depth,
            filter_scope=scope
        )
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


@cli.command()
@click.option('--tree', '-t', required=True, type=click.Path(exists=True),
              help='Path to dependency tree JSON file')
@click.option('--analysis', '-a', required=True, type=click.Path(exists=True),
              help='Path to dependency analysis text file')
@click.option('--output', '-o', type=click.Path(),
              help='Output Excel file path (optional)')
def analyze(tree, analysis, output):
    """Analyze dependencies for issues."""
    console = Console()
    
    try:
        # Parse the tree
        tree_parser = TreeParser()
        tree_obj = tree_parser.parse(tree)
        
        # Parse the analysis
        analysis_parser = AnalysisParser()
        analysis_obj = analysis_parser.parse(analysis)
        
        # Initialize analyzers
        tree_analyzer = TreeAnalyzer()
        redundancy_analyzer = RedundancyAnalyzer()
        
        console.print(f"[bold blue]Project:[/bold blue] {analysis_obj.project_coordinate}")
        console.print()
        
        # Show tree statistics
        stats = tree_analyzer.get_statistics(tree_obj)
        console.print(f"[bold]Total Dependencies:[/bold] {stats['total_dependencies']}")
        console.print(f"[bold]Direct Dependencies:[/bold] {stats['direct_dependencies']}")
        console.print(f"[bold]Transitive Dependencies:[/bold] {stats['transitive_dependencies']}")
        console.print(f"[bold]Max Depth:[/bold] {stats['max_depth']}")
        console.print(f"[bold]Unique Artifacts:[/bold] {stats['unique_artifacts']}")
        console.print()
        
        # Show scope distribution using Rich table
        scope_table = Table(title="Scope Distribution")
        scope_table.add_column("Scope", style="cyan")
        scope_table.add_column("Count", style="magenta")
        
        for scope, count in stats['scope_distribution'].items():
            if scope:  # Skip empty scopes
                scope_table.add_row(scope, str(count))
        
        console.print(scope_table)
        console.print()
        
        # Show type distribution using Rich table
        type_table = Table(title="Type Distribution")
        type_table.add_column("Type", style="cyan")
        type_table.add_column("Count", style="magenta")
        
        for type_, count in stats['type_distribution'].items():
            if type_:  # Skip empty types
                type_table.add_row(type_, str(count))
        
        console.print(type_table)
        console.print()
        
        # Show used undeclared dependencies
        if analysis_obj.used_undeclared:
            console.print(f"[bold yellow]Used Undeclared Dependencies ({len(analysis_obj.used_undeclared)}):[/bold yellow]")
            for dep in analysis_obj.used_undeclared[:10]:  # Show first 10
                console.print(f"  • {dep}")
            if len(analysis_obj.used_undeclared) > 10:
                console.print(f"  ... and {len(analysis_obj.used_undeclared) - 10} more")
            console.print()
        
        # Show unused declared dependencies
        if analysis_obj.unused_declared:
            console.print(f"[bold yellow]Unused Declared Dependencies ({len(analysis_obj.unused_declared)}):[/bold yellow]")
            for dep in analysis_obj.unused_declared[:10]:  # Show first 10
                console.print(f"  • {dep}")
            if len(analysis_obj.unused_declared) > 10:
                console.print(f"  ... and {len(analysis_obj.unused_declared) - 10} more")
            console.print()
        
        # Show redundancy analysis
        console.print("[bold green]Redundancy Analysis:[/bold green]")
        redundancy_cases = redundancy_analyzer.analyze(tree_obj, analysis_obj)
        
        if redundancy_cases:
            for case in redundancy_cases[:10]:  # Show first 10 cases
                console.print(f"  [bold red]Issue:[/bold red] {case.declared_dependency}")
                console.print(f"  [bold yellow]Actually Used:[/bold yellow] {', '.join(case.actually_used)}")
                console.print(f"  [bold cyan]Recommendation:[/bold cyan] {case.recommendation}")
                console.print()
            if len(redundancy_cases) > 10:
                console.print(f"  ... and {len(redundancy_cases) - 10} more issues")
        else:
            console.print("  No redundancy issues detected.")
        
        # Export to Excel if requested
        if output:
            exporter = ExcelExporter()
            exporter.export_analysis_report(tree_obj, analysis_obj, output, redundancy_cases)
            console.print(f"\n[bold green]Report exported to:[/bold green] {output}")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


@cli.command()
@click.option('--tree', '-t', required=True, type=click.Path(exists=True),
              help='Path to dependency tree JSON file')
@click.option('--analysis', '-a', required=True, type=click.Path(exists=True),
              help='Path to dependency analysis text file')
def check_redundancy(tree, analysis):
    """Check for redundant dependencies specifically."""
    console = Console()
    
    try:
        # Parse the tree
        tree_parser = TreeParser()
        tree_obj = tree_parser.parse(tree)
        
        # Parse the analysis
        analysis_parser = AnalysisParser()
        analysis_obj = analysis_parser.parse(analysis)
        
        # Perform redundancy analysis
        redundancy_analyzer = RedundancyAnalyzer()
        redundancy_cases = redundancy_analyzer.analyze(tree_obj, analysis_obj)
        
        console.print(f"[bold blue]Redundancy Check for:[/bold blue] {analysis_obj.project_coordinate}")
        console.print(f"[bold]Found {len(redundancy_cases)} potential redundancy issues.[/bold]")
        console.print()
        
        if redundancy_cases:
            for i, case in enumerate(redundancy_cases, 1):
                console.print(f"[bold]{i}. Redundant Dependency:[/bold] {case.declared_dependency}")
                console.print(f"   Actually Used Transitive Deps: {', '.join(case.actually_used)}")
                console.print(f"   Recommendation: {case.recommendation}")
                
                if case.dependency_path:
                    console.print(f"   Dependency Path: {' -> '.join(case.dependency_path)}")
                console.print()
        else:
            console.print("[bold green]No redundancy issues detected.[/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


@cli.command()
@click.option('--tree', '-t', required=True, type=click.Path(exists=True),
              help='Path to dependency tree JSON file')
@click.option('--analysis', '-a', required=True, type=click.Path(exists=True),
              help='Path to dependency analysis text file')
@click.option('--output', '-o', required=True, type=click.Path(),
              help='Output Excel file path')
def export_report(tree, analysis, output):
    """Export a comprehensive analysis report to Excel."""
    console = Console()
    
    try:
        # Parse the tree
        tree_parser = TreeParser()
        tree_obj = tree_parser.parse(tree)
        
        # Parse the analysis
        analysis_parser = AnalysisParser()
        analysis_obj = analysis_parser.parse(analysis)
        
        # Export to Excel
        exporter = ExcelExporter()
        exporter.export_analysis_report(tree_obj, analysis_obj, output)
        
        console.print(f"[bold green]Analysis report exported to:[/bold green] {output}")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


if __name__ == '__main__':
    cli()