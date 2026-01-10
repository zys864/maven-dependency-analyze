# Project Coding Rules (Non-Obvious Only)

## Dependency Model Patterns
- Dependency objects maintain parent references for path finding but exclude from serialization (exclude=True) to prevent circular reference issues
- Use `simple_coordinate` (groupId:artifactId:version) for general matching, `coordinate` (with type and scope) for precise identification
- Always call `build_coordinate_index()` after creating/parsing a DependencyTree to populate the all_dependencies lookup table

## Data Processing
- Use computed properties in Pydantic models (like total_dependencies, max_depth) rather than recalculating values
- When flattening dependency trees, use the built-in `flatten()` method instead of manual recursion
- Use `to_polars_df()` method for advanced analysis and data manipulation tasks

## Tree Visualization
- TreeVisualizer handles Rich console output formatting - use the provided methods rather than direct Rich calls
- When filtering dependencies by scope or depth, use the built-in filtering parameters in print_tree() method
- The parent reference in Dependency is excluded from serialization to prevent infinite recursion during JSON output

## CLI Implementation
- Use Click decorators for command-line interface consistency
- Console output should use Rich styling for better user experience
- Error handling should use click.Abort() for proper command-line error reporting