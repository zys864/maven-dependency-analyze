"""Analyzer for detecting redundant dependencies."""

from typing import List
from ..models.dependency import DependencyTree
from ..models.analysis_result import AnalysisResult, RedundancyCase


class RedundancyAnalyzer:
    """Detect redundant dependencies in Maven projects."""
    
    def analyze(self, tree: DependencyTree, analysis: AnalysisResult) -> List[RedundancyCase]:
        """
        Analyze the dependency tree and analysis result to detect redundancies.
        
        Args:
            tree: The dependency tree to analyze
            analysis: The analysis result with used/unused dependencies
            
        Returns:
            List of RedundancyCase objects describing detected redundancies
        """
        redundancy_cases = []
        
        # For each unused declared dependency, check if it has transitive dependencies
        # that are actually used
        for unused_dep in analysis.unused_declared:
            # Find this dependency in the tree
            matching_nodes = tree.find_dependency(unused_dep)
            
            for node in matching_nodes:
                # If this is a direct dependency (depth=1), check its children
                if node.depth == 1:
                    # Check if any of its children are in the used_undeclared list
                    for child in node.get_all_descendants():
                        if child.simple_coordinate in analysis.used_undeclared or child.coordinate in analysis.used_undeclared:
                            # We found a redundancy: declared A but only use its transitive dependency B
                            
                            # Find the path from the unused dependency to the actually used one
                            path = self._find_path_in_tree(node, child.simple_coordinate)
                            if path is None:
                                path = self._find_path_in_tree(node, child.coordinate)
                            
                            path_strs = [p.simple_coordinate for p in path] if path else []
                            
                            redundancy_case = RedundancyCase(
                                declared_dependency=node.simple_coordinate,
                                actually_used=[child.simple_coordinate],
                                dependency_path=path_strs,
                                recommendation=f"Remove '{node.simple_coordinate}' and directly declare '{child.simple_coordinate}' instead"
                            )
                            redundancy_cases.append(redundancy_case)
        
        # Additional analysis: Find dependencies that are declared but only their 
        # transitive dependencies are used
        for unused_dep in analysis.unused_declared:
            matching_nodes = tree.find_dependency(unused_dep)
            
            for node in matching_nodes:
                if node.depth == 1:  # Direct dependency
                    actually_used_transitives = []
                    
                    # Collect all transitive dependencies that are actually used
                    for descendant in node.get_all_descendants():
                        if (descendant.simple_coordinate in analysis.used_undeclared or 
                            descendant.coordinate in analysis.used_undeclared):
                            actually_used_transitives.append(descendant.simple_coordinate)
                    
                    if actually_used_transitives:
                        # Construct path from node to each actually used transitive dependency
                        paths = []
                        for used_transitive in actually_used_transitives:
                            path = self._find_path_in_tree(node, used_transitive)
                            if path:
                                paths.extend([p.simple_coordinate for p in path])
                        
                        # Remove duplicates in paths
                        unique_paths = list(dict.fromkeys(paths))  # Preserves order
                        
                        redundancy_case = RedundancyCase(
                            declared_dependency=node.simple_coordinate,
                            actually_used=actually_used_transitives,
                            dependency_path=unique_paths,
                            recommendation=f"Consider removing '{node.simple_coordinate}' and directly declaring its used transitive dependencies"
                        )
                        redundancy_cases.append(redundancy_case)
        
        # Detect version conflicts - same artifact with different versions
        version_conflicts = self._detect_version_conflicts(tree)
        for conflict in version_conflicts:
            redundancy_case = RedundancyCase(
                declared_dependency=conflict["artifact"],
                actually_used=conflict["versions"][1:],  # All but the first as "actually used"
                dependency_path=[],
                recommendation=f"Multiple versions of '{conflict['artifact']}' detected: {conflict['versions']}. Consider consolidating to a single version."
            )
            redundancy_cases.append(redundancy_case)
        
        return redundancy_cases
    
    def _find_path_in_tree(self, start_node: 'Dependency', target_coordinate: str) -> List['Dependency']:
        """
        Find path from start_node to target coordinate within the subtree.
        
        Args:
            start_node: Node to start searching from
            target_coordinate: Target dependency coordinate to find
            
        Returns:
            List of Dependency objects forming the path, or None if not found
        """
        if start_node.simple_coordinate == target_coordinate or start_node.coordinate == target_coordinate:
            return [start_node]
        
        # Search in children
        for child in start_node.children:
            path = self._find_path_in_tree(child, target_coordinate)
            if path:
                return [start_node] + path
        
        return None
    
    def _detect_version_conflicts(self, tree: DependencyTree) -> List[dict]:
        """
        Detect multiple versions of the same artifact in the dependency tree.
        
        Args:
            tree: The dependency tree to analyze
            
        Returns:
            List of conflict dictionaries
        """
        import polars as pl
        conflicts = []
        
        # Group dependencies by group:artifact
        df = tree.to_polars_df()
        grouped = df.group_by("group_id", "artifact_id").agg([
            pl.col("version").unique()
        ]).to_dicts()
        
        # Find artifacts with multiple versions
        for item in grouped:
            versions = item["version"]
            if len(versions) > 1:
                artifact = f"{item['group_id']}:{item['artifact_id']}"
                conflicts.append({
                    "artifact": artifact,
                    "versions": sorted(versions)
                })
        
        return conflicts