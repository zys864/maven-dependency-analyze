# Project Architecture Rules (Non-Obvious Only)

## Data Flow Architecture
- Dependency tree parsing flows from TreeParser → DependencyTree → TreeVisualizer
- Analysis parsing flows from AnalysisParser → AnalysisResult for dependency issue detection
- Both flows can be combined to detect redundant dependencies where package A is used only for transitive dependency B

## Component Coupling
- Dependency model maintains parent references for path finding but excludes them from serialization to prevent circular references
- The all_dependencies index in DependencyTree must be rebuilt after tree modification with build_coordinate_index()
- TreeVisualizer depends on DependencyTree models but should not modify them

## Performance Considerations
- Large dependency trees should use computed properties instead of recalculating values repeatedly
- Use flatten() method for tree traversal instead of manual recursion to avoid stack overflow
- Polars DataFrames (via to_polars_df()) provide efficient analysis for large datasets

## Extensibility Points
- New export formats should extend from the base models without modifying core parsing logic
- Analysis algorithms should work with the existing Dependency/DependencyTree model structure
- CLI commands are implemented with Click decorators for consistent interface