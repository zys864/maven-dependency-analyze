"""Parser for Maven dependency tree JSON files."""

import json
from pathlib import Path
from typing import Union, Dict, Any
from ..models.dependency import Dependency, DependencyTree


class TreeParser:
    """Parse Maven dependency tree from JSON format."""
    
    def parse(self, source: Union[str, Path, dict]) -> DependencyTree:
        """
        Parse dependency tree from various sources.
        
        Args:
            source: Either a file path, JSON string, or parsed dict
            
        Returns:
            DependencyTree object representing the parsed tree
        """
        if isinstance(source, (str, Path)):
            source_path = Path(source)
            if source_path.suffix.lower() == '.json':
                with open(source_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                # Assume it's a JSON string
                data = json.loads(str(source))
        else:
            # Already a dict
            data = source
        
        # Extract the root dependency from the tree structure
        root_node_data = data.get('root', data)
        
        # Build the dependency tree
        root_dependency = self._parse_node(root_node_data, None, 0)
        
        # Create the tree and build index
        tree = DependencyTree(root=root_dependency)
        tree.build_coordinate_index()
        
        return tree
    
    def _parse_node(self, node_dict: Dict[str, Any], parent: Dependency, depth: int) -> Dependency:
        """
        Recursively parse a node dictionary into a Dependency object.
        
        Args:
            node_dict: Dictionary representation of the dependency node
            parent: Parent dependency object
            depth: Current depth in the tree
            
        Returns:
            Parsed Dependency object
        """
        # Extract basic fields
        group_id = node_dict.get('groupId', '')
        artifact_id = node_dict.get('artifactId', '')
        version = node_dict.get('version', '')
        
        # Extract optional fields
        scope = node_dict.get('scope', 'compile')
        type_ = node_dict.get('type', 'jar')
        classifier = node_dict.get('classifier', '')
        
        # Handle optional field - it might be a string or boolean
        optional_raw = node_dict.get('optional', False)
        optional = optional_raw == "true" if isinstance(optional_raw, str) else bool(optional_raw)
        
        # Create dependency object
        dependency = Dependency(
            group_id=group_id,
            artifact_id=artifact_id,
            version=version,
            scope=scope,
            type=type_,
            classifier=classifier,
            optional=optional,
            parent=parent,
            depth=depth
        )
        
        # Process children - handle both 'dependencies' and 'children' keys
        children_data = node_dict.get('dependencies', []) or node_dict.get('children', [])
        for child_data in children_data:
            child_dependency = self._parse_node(child_data, dependency, depth + 1)
            dependency.children.append(child_dependency)
        
        return dependency