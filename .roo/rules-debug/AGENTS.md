# Project Debug Rules (Non-Obvious Only)

## Dependency Analysis
- When debugging dependency parsing issues, check both the raw JSON structure and the parsed Dependency objects
- Use the `simple_coordinate` vs `coordinate` formats appropriately for different matching scenarios
- The `parent` attribute is excluded from serialization, so it won't appear in JSON dumps but still exists in memory

## Tree Structure Issues
- Circular reference prevention relies on excluding parent references from serialization
- When debugging path finding, ensure `build_coordinate_index()` has been called on the tree
- The `depth` attribute is calculated during parsing and critical for filtering operations

## Data Validation
- Verify that input JSON follows Maven's expected dependency tree format
- Check that coordinate strings match expected format: groupId:artifactId:version
- Use example data files in data/ directories for comparison when debugging parsing issues