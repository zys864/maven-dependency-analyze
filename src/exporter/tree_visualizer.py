"""Tree visualizer using Rich library."""

from rich.tree import Tree
from rich.console import Console
from rich.text import Text
from typing import Optional
from ..models.dependency import DependencyTree, Dependency


class TreeVisualizer:
    """Visualize dependency trees using Rich for beautiful console output."""
    
    def __init__(self):
        self.console = Console()
    
    def print_tree(
        self, 
        tree: DependencyTree, 
        show_scope: bool = True, 
        max_depth: Optional[int] = None,
        filter_scope: Optional[str] = None,
        highlight_coordinates: Optional[list[str]] = None
    ) -> None:
        """
        Print the dependency tree to console.
        
        Args:
            tree: The dependency tree to visualize
            show_scope: Whether to show scope information
            max_depth: Maximum depth to display (None for no limit)
            filter_scope: Only show dependencies with this scope
            highlight_coordinates: List of coordinates to highlight
        """
        root = self._add_node_to_tree(
            tree.root, 
            show_scope=show_scope, 
            max_depth=max_depth, 
            current_depth=0,
            filter_scope=filter_scope,
            highlight_coordinates=highlight_coordinates
        )
        
        self.console.print(root)
    
    def _add_node_to_tree(
        self,
        dependency: Dependency,
        show_scope: bool,
        max_depth: Optional[int],
        current_depth: int,
        filter_scope: Optional[str],
        highlight_coordinates: Optional[list[str]]
    ) -> Tree:
        """
        Recursively add nodes to the Rich tree.
        
        Args:
            dependency: The dependency node to add
            show_scope: Whether to show scope information
            max_depth: Maximum depth to display
            current_depth: Current depth in the tree
            filter_scope: Only include nodes with this scope
            highlight_coordinates: Coordinates to highlight
            
        Returns:
            Rich Tree object
        """
        # Check if we should skip this node based on filters
        if max_depth is not None and current_depth > max_depth:
            return Tree("")  # Return empty tree to stop further expansion
        
        if filter_scope and dependency.scope != filter_scope:
            # If this node doesn't match the filter, still check its children
            tree_node = Tree("")
            for child in dependency.children:
                child_tree = self._add_node_to_tree(
                    child, show_scope, max_depth, current_depth + 1, 
                    filter_scope, highlight_coordinates
                )
                if child_tree.label != "":
                    tree_node.add(child_tree)
            return tree_node
        
        # Format the node label
        label_parts = [
            f"[bold]{dependency.group_id}[/bold]:",
            f"[bold]{dependency.artifact_id}[/bold]:",
            f"[bold]{dependency.version}[/bold]"
        ]
        
        if show_scope and dependency.scope:
            scope_style = self._get_scope_style(dependency.scope)
            label_parts.append(f" [yellow]\\[{dependency.scope}][/yellow]")
        
        if dependency.type and dependency.type != "jar":
            label_parts.insert(-1, f":{dependency.type}")
        
        label = "".join(label_parts)
        
        # Highlight if needed
        if highlight_coordinates and dependency.simple_coordinate in highlight_coordinates:
            label = f"[bright_magenta on red]{label}[/bright_magenta on red]"
        elif highlight_coordinates and dependency.coordinate in highlight_coordinates:
            label = f"[bright_magenta on red]{label}[/bright_magenta on red]"
        
        tree_node = Tree(label)
        
        # Add children
        for child in dependency.children:
            child_tree = self._add_node_to_tree(
                child, show_scope, max_depth, current_depth + 1, 
                filter_scope, highlight_coordinates
            )
            if child_tree.label != "":  # Only add non-empty trees
                tree_node.add(child_tree)
        
        return tree_node
    
    def _get_scope_style(self, scope: str) -> str:
        """
        Get appropriate style for dependency scope.
        
        Args:
            scope: The scope string (compile, test, runtime, etc.)
            
        Returns:
            Rich style string
        """
        scope_styles = {
            'compile': 'green',
            'runtime': 'blue',
            'test': 'red',
            'provided': 'yellow',
            'system': 'cyan',
            'import': 'magenta'
        }
        return scope_styles.get(scope.lower(), 'white')


def print_simple_tree(dependency: Dependency, indent: int = 0) -> None:
    """
    Simple tree printer without Rich formatting.
    
    Args:
        dependency: The dependency to print
        indent: Current indentation level
    """
    prefix = "  " * indent
    scope_part = f" ({dependency.scope})" if dependency.scope else ""
    print(f"{prefix}{dependency.group_id}:{dependency.artifact_id}:{dependency.version}{scope_part}")
    
    for child in dependency.children:
        print_simple_tree(child, indent + 1)