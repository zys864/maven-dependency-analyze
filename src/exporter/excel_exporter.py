"""Excel exporter for Maven dependency analysis results."""

import xlsxwriter
import polars as pl
from pathlib import Path
from typing import Union
from ..models.dependency import DependencyTree
from ..models.analysis_result import AnalysisResult, RedundancyCase
from ..analyzer.tree_analyzer import TreeAnalyzer
from ..analyzer.redundancy_analyzer import RedundancyAnalyzer


class ExcelExporter:
    """Export dependency analysis results to Excel format."""
    
    def export_analysis_report(
        self,
        tree: DependencyTree,
        analysis: AnalysisResult,
        output_path: Union[str, Path],
        redundancy_cases: list[RedundancyCase] = None
    ):
        """
        Export a comprehensive analysis report to Excel.
        
        Args:
            tree: The dependency tree
            analysis: The analysis result
            output_path: Path to save the Excel file
            redundancy_cases: Pre-computed redundancy cases (optional)
        """
        output_path = Path(output_path)
        
        # Initialize analyzers if needed
        if redundancy_cases is None:
            analyzer = RedundancyAnalyzer()
            redundancy_cases = analyzer.analyze(tree, analysis)
        
        tree_analyzer = TreeAnalyzer()
        stats = tree_analyzer.get_statistics(tree)
        
        # Create workbook
        with xlsxwriter.Workbook(output_path) as workbook:
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D7E4BC',
                'border': 1
            })
            
            # Sheet 1: Project Overview
            overview_worksheet = workbook.add_worksheet("Project Overview")
            overview_data = [
                ["Metric", "Value"],
                ["Project Coordinate", str(analysis.project_coordinate)],
                ["Total Dependencies", str(stats["total_dependencies"])],
                ["Direct Dependencies", str(stats["direct_dependencies"])],
                ["Transitive Dependencies", str(stats["transitive_dependencies"])],
                ["Max Depth", str(stats["max_depth"])],
                ["Unique Artifacts", str(stats["unique_artifacts"])],
                ["Used Undeclared Dependencies", str(len(analysis.used_undeclared))],
                ["Unused Declared Dependencies", str(len(analysis.unused_declared))],
                ["Redundancy Issues Found", str(len(redundancy_cases))]
            ]
            
            for row_num, row_data in enumerate(overview_data):
                for col_num, cell_data in enumerate(row_data):
                    if row_num == 0:  # Header row
                        overview_worksheet.write(row_num, col_num, cell_data, header_format)
                    else:
                        overview_worksheet.write(row_num, col_num, cell_data)
            
            # Adjust column widths
            overview_worksheet.set_column('A:A', 30)
            overview_worksheet.set_column('B:B', 50)
            
            # Sheet 2: Complete Dependency Tree
            tree_worksheet = workbook.add_worksheet("Complete Dependency Tree")
            tree_df = tree.to_polars_df()
            # Add indentation based on depth for better visualization
            # Add indentation based on depth for better visualization
            tree_data = tree_df.to_dicts()
            indented_dependencies = []
            for row in tree_data:
                indent = "  " * row["depth"]
                indented_dep = f"{indent}{row['group_id']}:{row['artifact_id']}:{row['version']}"
                indented_dependencies.append(indented_dep)
            
            tree_df_with_indent = tree_df.with_columns([
                pl.Series("indented_dependency", indented_dependencies)
            ])
            
            tree_export_data = tree_df_with_indent.select([
                "depth",
                "indented_dependency",
                "group_id",
                "artifact_id",
                "version",
                "scope",
                "type"
            ])
            
            # Write headers
            headers = tree_export_data.columns
            for col_num, header in enumerate(headers):
                tree_worksheet.write(0, col_num, header, header_format)
            
            # Write data rows
            for row_num, row in enumerate(tree_export_data.iter_rows(), start=1):
                for col_num, cell_data in enumerate(row):
                    tree_worksheet.write(row_num, col_num, str(cell_data) if cell_data is not None else "")
            
            # Adjust column widths
            tree_worksheet.set_column('A:A', 8)  # depth
            tree_worksheet.set_column('B:B', 50)  # indented_dependency
            tree_worksheet.set_column('C:C', 25)  # group_id
            tree_worksheet.set_column('D:D', 25)  # artifact_id
            tree_worksheet.set_column('E:E', 15)  # version
            tree_worksheet.set_column('F:F', 15)  # scope
            tree_worksheet.set_column('G:G', 10)  # type
            
            # Sheet 3: Used But Undeclared Dependencies
            if analysis.used_undeclared:
                used_worksheet = workbook.add_worksheet("Used But Undeclared")
                used_headers = ["Coordinate", "Group ID", "Artifact ID", "Version", "Scope"]
                used_data = []
                for coord in analysis.used_undeclared:
                    row = [
                        coord,
                        coord.split(':')[0] if ':' in coord else '',
                        self._extract_artifact_id(coord),
                        self._extract_version(coord),
                        self._extract_scope(coord)
                    ]
                    used_data.append(row)
                
                # Write headers
                for col_num, header in enumerate(used_headers):
                    used_worksheet.write(0, col_num, header, header_format)
                
                # Write data
                for row_num, row in enumerate(used_data, start=1):
                    for col_num, cell_data in enumerate(row):
                        used_worksheet.write(row_num, col_num, str(cell_data) if cell_data is not None else "")
                
                # Adjust column widths
                used_worksheet.set_column('A:A', 50)
                used_worksheet.set_column('B:B', 20)
                used_worksheet.set_column('C:C', 20)
                used_worksheet.set_column('D:D', 15)
                used_worksheet.set_column('E:E', 15)
            
            # Sheet 4: Declared But Unused Dependencies
            if analysis.unused_declared:
                unused_worksheet = workbook.add_worksheet("Declared But Unused")
                unused_headers = ["Coordinate", "Group ID", "Artifact ID", "Version", "Scope"]
                unused_data = []
                for coord in analysis.unused_declared:
                    row = [
                        coord,
                        coord.split(':')[0] if ':' in coord else '',
                        self._extract_artifact_id(coord),
                        self._extract_version(coord),
                        self._extract_scope(coord)
                    ]
                    unused_data.append(row)
                
                # Write headers
                for col_num, header in enumerate(unused_headers):
                    unused_worksheet.write(0, col_num, header, header_format)
                
                # Write data
                for row_num, row in enumerate(unused_data, start=1):
                    for col_num, cell_data in enumerate(row):
                        unused_worksheet.write(row_num, col_num, str(cell_data) if cell_data is not None else "")
                
                # Adjust column widths
                unused_worksheet.set_column('A:A', 50)
                unused_worksheet.set_column('B:B', 20)
                unused_worksheet.set_column('C:C', 20)
                unused_worksheet.set_column('D:D', 15)
                unused_worksheet.set_column('E:E', 15)
            
            # Sheet 5: Redundancy Analysis
            if redundancy_cases:
                redundancy_worksheet = workbook.add_worksheet("Redundancy Analysis")
                redundancy_headers = ["Declared Dependency", "Actually Used Dependencies", "Dependency Path", "Recommendation", "Severity"]
                redundancy_data = []
                for case in redundancy_cases:
                    row = [
                        case.declared_dependency,
                        ', '.join(case.actually_used),
                        ' -> '.join(case.dependency_path) if case.dependency_path else 'N/A',
                        case.recommendation,
                        case.severity
                    ]
                    redundancy_data.append(row)
                
                # Write headers
                for col_num, header in enumerate(redundancy_headers):
                    redundancy_worksheet.write(0, col_num, header, header_format)
                
                # Write data
                for row_num, row in enumerate(redundancy_data, start=1):
                    for col_num, cell_data in enumerate(row):
                        redundancy_worksheet.write(row_num, col_num, str(cell_data) if cell_data is not None else "")
                
                # Adjust column widths
                redundancy_worksheet.set_column('A:A', 30)
                redundancy_worksheet.set_column('B:B', 40)
                redundancy_worksheet.set_column('C:C', 50)
                redundancy_worksheet.set_column('D:D', 80)
                redundancy_worksheet.set_column('E:E', 10)
            
            # Sheet 6: Statistics by Scope
            scope_worksheet = workbook.add_worksheet("Statistics by Scope")
            scope_stats = tree.to_polars_df().group_by("scope").agg([
                pl.len().alias("Count")
            ]).sort("Count", descending=True)
            
            scope_headers = scope_stats.columns
            # Write headers
            for col_num, header in enumerate(scope_headers):
                scope_worksheet.write(0, col_num, header, header_format)
            
            # Write data
            for row_num, row in enumerate(scope_stats.iter_rows(), start=1):
                for col_num, cell_data in enumerate(row):
                    scope_worksheet.write(row_num, col_num, str(cell_data) if cell_data is not None else "")
            
            # Adjust column widths
            scope_worksheet.set_column('A:A', 20)
            scope_worksheet.set_column('B:B', 15)
            
            # Sheet 7: Statistics by Depth
            depth_worksheet = workbook.add_worksheet("Statistics by Depth")
            depth_stats = tree.to_polars_df().group_by("depth").agg([
                pl.len().alias("Count")
            ]).sort("depth")
            
            depth_headers = depth_stats.columns
            # Write headers
            for col_num, header in enumerate(depth_headers):
                depth_worksheet.write(0, col_num, header, header_format)
            
            # Write data
            for row_num, row in enumerate(depth_stats.iter_rows(), start=1):
                for col_num, cell_data in enumerate(row):
                    depth_worksheet.write(row_num, col_num, str(cell_data) if cell_data is not None else "")
            
            # Adjust column widths
            depth_worksheet.set_column('A:A', 15)
            depth_worksheet.set_column('B:B', 15)

    def _extract_artifact_id(self, coordinate: str) -> str:
        """Extract artifact ID from coordinate string."""
        parts = coordinate.split(':')
        return parts[1] if len(parts) >= 2 else ''
    
    def _extract_version(self, coordinate: str) -> str:
        """Extract version from coordinate string."""
        parts = coordinate.split(':')
        # Version is typically the 3rd or 4th element depending on format
        if len(parts) >= 3:
            # Handle formats like: group:artifact:type:version:scope or group:artifact:version
            if parts[2] in ['jar', 'war', 'pom', 'aar', 'so', 'dll', 'exe']:
                # Format is group:artifact:type:version:scope
                return parts[3] if len(parts) > 3 else ''
            else:
                # Format is group:artifact:version
                return parts[2]
        return ''
    
    def _extract_scope(self, coordinate: str) -> str:
        """Extract scope from coordinate string."""
        parts = coordinate.split(':')
        # Scope is typically the last element in the common format
        if len(parts) >= 5:
            # Format is group:artifact:type:version:scope
            return parts[4]
        elif len(parts) >= 3:
            # Format is group:artifact:version (no scope)
            return 'compile'  # Default scope
        return ''

    def _extract_artifact_id(self, coordinate: str) -> str:
        """Extract artifact ID from coordinate string."""
        parts = coordinate.split(':')
        return parts[1] if len(parts) >= 2 else ''
    
    def _extract_version(self, coordinate: str) -> str:
        """Extract version from coordinate string."""
        parts = coordinate.split(':')
        # Version is typically the 3rd or 4th element depending on format
        if len(parts) >= 3:
            # Handle formats like: group:artifact:type:version:scope or group:artifact:version
            if parts[2] in ['jar', 'war', 'pom', 'aar', 'so', 'dll', 'exe']:
                # Format is group:artifact:type:version:scope
                return parts[3] if len(parts) > 3 else ''
            else:
                # Format is group:artifact:version
                return parts[2]
        return ''
    
    def _extract_scope(self, coordinate: str) -> str:
        """Extract scope from coordinate string."""
        parts = coordinate.split(':')
        # Scope is typically the last element in the common format
        if len(parts) >= 5:
            # Format is group:artifact:type:version:scope
            return parts[4]
        elif len(parts) >= 3:
            # Format is group:artifact:version (no scope)
            return 'compile'  # Default scope
        return ''