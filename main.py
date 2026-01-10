#!/usr/bin/env python3
"""Maven 依赖分析工具 CLI 入口"""

import click
from pathlib import Path
from rich.console import Console

from src.parser.tree_parser import TreeParser
from src.parser.analysis_parser import AnalysisParser
from src.exporter.tree_visualizer import TreeVisualizer

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Maven 依赖树分析工具

    分析 Java Maven 项目的依赖树，检测冗余依赖和依赖问题。
    """
    pass


@cli.command(name="show-tree")
@click.option(
    "--tree",
    "-t",
    "tree_file",
    required=True,
    type=click.Path(exists=True),
    help="依赖树 JSON 文件路径",
)
@click.option(
    "--max-depth",
    "-d",
    type=int,
    default=None,
    help="最大显示深度",
)
@click.option(
    "--scope",
    "-s",
    type=str,
    default=None,
    help="过滤特定 scope (compile, test, runtime 等)",
)
@click.option(
    "--no-scope",
    is_flag=True,
    help="不显示 scope 信息",
)
@click.option(
    "--stats",
    is_flag=True,
    help="显示统计信息",
)
def show_tree(tree_file, max_depth, scope, no_scope, stats):
    """显示依赖树结构"""
    try:
        # 解析依赖树
        console.print("[cyan]正在解析依赖树...[/cyan]")
        parser = TreeParser()
        tree = parser.parse(tree_file)

        console.print(f"[green]✓[/green] 成功解析 {tree.total_dependencies} 个依赖\n")

        # 显示统计信息
        if stats:
            visualizer = TreeVisualizer(console)
            visualizer.print_statistics(tree)
            console.print()

        # 显示依赖树
        console.print("[bold]依赖树结构:[/bold]\n")
        visualizer = TreeVisualizer(console)
        visualizer.print_tree(
            tree,
            show_scope=not no_scope,
            max_depth=max_depth,
            filter_scope=scope,
        )

    except Exception as e:
        console.print(f"[red]错误:[/red] {e}")
        raise click.Abort()


@cli.command(name="analyze")
@click.option(
    "--tree",
    "-t",
    "tree_file",
    required=True,
    type=click.Path(exists=True),
    help="依赖树 JSON 文件路径",
)
@click.option(
    "--analysis",
    "-a",
    "analysis_file",
    required=True,
    type=click.Path(exists=True),
    help="依赖分析文本文件路径",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="输出文件路径 (Excel)",
)
def analyze(tree_file, analysis_file, output):
    """分析依赖问题和冗余依赖"""
    try:
        # 解析依赖树
        console.print("[cyan]正在解析依赖树...[/cyan]")
        tree_parser = TreeParser()
        tree = tree_parser.parse(tree_file)
        console.print(f"[green]✓[/green] 依赖树: {tree.total_dependencies} 个依赖")

        # 解析依赖分析结果
        console.print("[cyan]正在解析依赖分析结果...[/cyan]")
        analysis_parser = AnalysisParser()
        analysis = analysis_parser.parse(analysis_file)
        console.print(
            f"[green]✓[/green] 分析结果: {analysis.total_issues} 个问题\n"
        )

        # 显示问题汇总
        from rich.table import Table

        table = Table(title="依赖问题汇总", show_header=True, header_style="bold yellow")
        table.add_column("问题类型", style="cyan")
        table.add_column("数量", style="magenta", justify="right")

        table.add_row(
            "使用但未声明", f"[red]{len(analysis.used_undeclared)}[/red]"
        )
        table.add_row(
            "声明但未使用", f"[yellow]{len(analysis.unused_declared)}[/yellow]"
        )

        console.print(table)
        console.print()

        # 显示详细问题列表
        if analysis.used_undeclared:
            console.print("[bold red]使用但未声明的依赖:[/bold red]")
            for dep in analysis.used_undeclared:
                console.print(f"  • {dep}")
            console.print()

        if analysis.unused_declared:
            console.print("[bold yellow]声明但未使用的依赖:[/bold yellow]")
            for dep in analysis.unused_declared:
                console.print(f"  • {dep}")
            console.print()

        # TODO: 冗余依赖检测将在 Phase 2 实现

        if output:
            console.print(f"[dim]Excel 导出功能将在 Phase 3 实现[/dim]")

    except Exception as e:
        console.print(f"[red]错误:[/red] {e}")
        raise click.Abort()


if __name__ == "__main__":
    cli()
