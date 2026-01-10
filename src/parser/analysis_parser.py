"""Parser for Maven dependency analysis text files."""

import re
from pathlib import Path
from typing import Union
from ..models.analysis_result import AnalysisResult


class AnalysisParser:
    """Parse Maven dependency analysis from text format."""
    
    def parse(self, source: Union[str, Path]) -> AnalysisResult:
        """
        Parse dependency analysis from a text file.
        
        Args:
            source: File path to the analysis text file
            
        Returns:
            AnalysisResult object representing the parsed analysis
        """
        source_path = Path(source)
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self._parse_content(content)
    
    def _parse_content(self, content: str) -> AnalysisResult:
        """
        Parse the content of a dependency analysis file.
        
        Args:
            content: Content of the analysis file
            
        Returns:
            AnalysisResult object
        """
        # Find project coordinate from the beginning of the file
        # Pattern: Building <groupId>:<artifactId>:<version>
        project_coord_match = re.search(r'Building\s+([^\s]+:[^\s]+:[^\s]+)', content)
        project_coordinate = project_coord_match.group(1) if project_coord_match else "unknown:unknown:unknown"
        
        # Find "Used undeclared dependencies" section
        used_undeclared = self._extract_section_from_warnings(content, 'Used undeclared dependencies found:')
        
        # Find "Unused declared dependencies" section
        unused_declared = self._extract_section_from_warnings(content, 'Unused declared dependencies found:')
        
        return AnalysisResult(
            project_coordinate=project_coordinate,
            used_undeclared=used_undeclared,
            unused_declared=unused_declared
        )
    
    def _extract_section_from_warnings(self, content: str, section_header: str) -> list[str]:
        """
        Extract dependencies from warning sections in Maven output.
        
        Args:
            content: Full content of the analysis file
            section_header: Header text to look for
            
        Returns:
            List of dependency coordinates found in the section
        """
        dependencies = []
        
        # Look for the section header and extract lines that follow
        lines = content.split('\n')
        in_section = False
        
        for line in lines:
            if section_header in line:
                in_section = True
                continue
            
            if in_section:
                # Look for dependency coordinates in format like:
                # [WARNING]    org.junit.jupiter:junit-jupiter-api:jar:6.0.1:test
                # Pattern: [WARNING] <groupId>:<artifactId>:<type>:<version>:<scope>
                coord_match = re.search(r'\[WARNING\]\s+([a-zA-Z0-9_\-.]+:[a-zA-Z0-9_\-.]+(?::[a-zA-Z0-9_\-.]+){0,3})', line)
                if coord_match:
                    coord = coord_match.group(1).strip()
                    if coord and not coord.startswith('BUILD') and not coord.startswith('Total'):
                        dependencies.append(coord)
                elif '[INFO]' in line and '[WARNING]' not in line:
                    # End of section reached when we hit next info section
                    break
        
        return dependencies
    
    def _extract_section(self, content: str, start_marker: str, end_marker: str) -> list[str]:
        """
        Extract dependencies from a specific section of the analysis.
        
        Args:
            content: Full content of the analysis file
            start_marker: Marker indicating the start of the section
            end_marker: Marker indicating the end of the section
            
        Returns:
            List of dependency coordinates found in the section
        """
        # Look for the section between start and end markers
        pattern = rf'{re.escape(start_marker)}.*?((?:\n.*?)*?)(?:{re.escape(end_marker)}|\n\[)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            # Try alternative approach: look for dependencies after marker until we hit empty line or next section
            alt_pattern = rf'{re.escape(start_marker)}.*?(\n\s+.*)*'
            match = re.search(alt_pattern, content, re.DOTALL)
        
        dependencies = []
        if match:
            section_content = match.group(0)
            # Extract dependency coordinates in format groupId:artifactId:type:version:scope
            # Example formats: org.springframework:spring-core:jar:5.3.21:compile
            coord_pattern = r'([a-zA-Z0-9_\-.]+:[a-zA-Z0-9_\-.]+(?::[a-zA-Z0-9_\-.]+){0,3})'
            deps = re.findall(coord_pattern, section_content)
            dependencies = [dep.strip() for dep in deps if dep.strip()]
        else:
            # Alternative parsing: find all potential dependency coordinates in the entire content
            # after the specific marker
            start_pos = content.find(start_marker)
            if start_pos != -1:
                remaining_content = content[start_pos + len(start_marker):]
                # Look for lines that contain dependency coordinates
                lines = remaining_content.split('\n')
                for line in lines:
                    # Stop at the end marker or if we reach another section
                    if end_marker in line or '[INFO]' in line or 'Used undeclared' in line or 'Unused declared' in line:
                        break
                    coord_matches = re.findall(r'([a-zA-Z0-9_\-.]+:[a-zA-Z0-9_\-.]+(?::[a-zA-Z0-9_\-.]+){0,3})', line)
                    for coord in coord_matches:
                        if coord.strip():
                            dependencies.append(coord.strip())
        
        # Remove duplicates while preserving order
        unique_deps = []
        for dep in dependencies:
            if dep not in unique_deps:
                unique_deps.append(dep)
        
        return unique_deps