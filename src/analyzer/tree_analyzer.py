"""Analyzer for dependency tree statistics and analysis."""

import polars as pl
from typing import Dict, List
from ..models.dependency import DependencyTree, Dependency


class TreeAnalyzer:
    """Analyze dependency trees for statistics and insights."""
    
    def get_statistics(self, tree: DependencyTree) -> Dict:
        """
        Get comprehensive statistics about the dependency tree.
        
        Args:
            tree: The dependency tree to analyze
            
        Returns:
            Dictionary containing various statistics
        """
        df = tree.to_polars_df()
        
        # Basic counts
        total_deps = len(df)
        direct_deps = len(df.filter(df["depth"] == 1))
        max_depth = df["depth"].max()
        
        # Scope distribution
        scope_counts = df.group_by("scope").len().to_dicts()
        scope_distribution = {item["scope"]: item["len"] for item in scope_counts}
        
        # Type distribution
        type_counts = df.group_by("type").len().to_dicts()
        type_distribution = {item["type"]: item["len"] for item in type_counts}
        
        # Depth distribution
        depth_counts = df.group_by("depth").len().to_dicts()
        depth_distribution = {item["depth"]: item["len"] for item in depth_counts}
        
        # Duplicate dependencies (same group:artifact, different versions)
        grouped_coords = df.group_by("group_id", "artifact_id").agg([
            "version"
        ]).to_dicts()
        duplicate_deps = []
        for item in grouped_coords:
            versions = item["version"]
            if len(set(versions)) > 1:  # Multiple versions of same artifact
                duplicate_deps.append({
                    "group_artifact": f"{item['group_id']}:{item['artifact_id']}",
                    "versions": list(set(versions)),
                    "count": len(set(versions))
                })
        
        stats = {
            "total_dependencies": total_deps,
            "direct_dependencies": direct_deps,
            "transitive_dependencies": total_deps - direct_deps,
            "max_depth": max_depth,
            "unique_artifacts": len(grouped_coords),
            "duplicate_dependencies": duplicate_deps,
            "scope_distribution": scope_distribution,
            "type_distribution": type_distribution,
            "depth_distribution": depth_distribution
        }
        
        return stats
    
    def get_dependency_paths(self, tree: DependencyTree, target: str) -> List[List[Dependency]]:
        """
        Find all paths to a specific dependency.
        
        Args:
            tree: The dependency tree to search in
            target: Target dependency coordinate to find paths to
            
        Returns:
            List of paths (each path is a list of Dependency objects)
        """
        all_paths = []
        
        def traverse(node: Dependency, current_path: List[Dependency]):
            # Check if current node matches target
            if node.simple_coordinate == target or node.coordinate == target:
                all_paths.append(current_path + [node])
            else:
                # Continue searching in children
                for child in node.children:
                    traverse(child, current_path + [node])
        
        traverse(tree.root, [])
        return all_paths
    
    def group_by_depth(self, tree: DependencyTree):
        """
        Group dependencies by depth and return a DataFrame.
        
        Args:
            tree: The dependency tree to analyze
            
        Returns:
            Polars DataFrame with dependencies grouped by depth
        """
        import polars as pl
        df = tree.to_polars_df()
        return df.group_by("depth").agg([
            pl.len().alias("count"),
            pl.col("group_id").unique().len().alias("unique_group_ids"),
            pl.col("artifact_id").unique().len().alias("unique_artifact_ids")
        ]).sort("depth")
    
    def find_most_transitive_deps(self, tree: DependencyTree, n: int = 5) -> List[Dict]:
        """
        Find dependencies that bring in the most transitive dependencies.
        
        Args:
            tree: The dependency tree to analyze
            n: Number of top dependencies to return
            
        Returns:
            List of dictionaries with top dependencies and their transitive count
        """
        def count_transitive_deps(dep: Dependency) -> int:
            return len(dep.get_all_descendants())
        
        # Calculate transitive dependency counts for direct dependencies
        direct_deps = [child for child in tree.root.children]
        dep_stats = []
        
        for dep in direct_deps:
            transitive_count = count_transitive_deps(dep)
            dep_stats.append({
                "dependency": dep.simple_coordinate,
                "transitive_count": transitive_count,
                "depth": dep.depth
            })
        
        # Sort by transitive count and return top N
        dep_stats.sort(key=lambda x: x["transitive_count"], reverse=True)
        return dep_stats[:n]
    
    def get_unused_direct_deps(self, tree: DependencyTree, analysis_result) -> List[Dict]:
        """
        Identify direct dependencies that are unused based on analysis.
        
        Args:
            tree: The dependency tree
            analysis_result: Analysis result with unused declared dependencies
            
        Returns:
            List of unused direct dependencies with details
        """
        unused_coords = set(analysis_result.unused_declared)
        direct_deps = [child for child in tree.root.children]
        
        unused_direct = []
        for dep in direct_deps:
            if dep.simple_coordinate in unused_coords or dep.coordinate in unused_coords:
                unused_direct.append({
                    "coordinate": dep.simple_coordinate,
                    "full_info": dep,
                    "transitive_deps_count": len(dep.get_all_descendants())
                })
        
        return unused_direct