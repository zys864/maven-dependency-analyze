# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview
Python tool for analyzing Maven dependency trees from Java repositories. Processes Maven dependency tree JSON and dependency analysis text outputs to detect issues and redundancy.

## Stack & Requirements
- Python 3.13+ (specified in `.python-version`)
- Uses `uv` for package management (not pip/poetry/pipenv)
- Core dependencies: pydantic, polars, xlsxwriter, click, rich

## Commands
```bash
# Install dependencies
uv sync

# Run the CLI tool
python main.py

# Run with uv (recommended)
uv run python main.py

# Run tests (when implemented)
uv run pytest

# Run linter (when configured)
uv run ruff check .
```

## Data Formats
- Dependency tree JSON: Generated with `mvn dependency:tree -DoutputType=json -DoutputFile=dependency-tree.json`
- Dependency analysis: Generated with `mvn dependency:analyze > deps-analysis.txt`
- Expected in `data/deps/` and `data/deps-analysis/` respectively

## Key Functionalities
- `show-tree`: Display dependency tree with filtering options
- `analyze`: Analyze dependency issues (used undeclared / unused declared)

## Code Style & Patterns
- Type hints required (uses Pydantic models extensively)
- Rich console output for user interaction
- Recursive data structures for dependency trees
- Computed properties in Pydantic models for derived data
- Dependency coordinates follow format: `{groupId}:{artifactId}:{version}`

## Non-Obvious Implementation Details
- Dependency objects maintain parent references (for path finding) but exclude from serialization to avoid cycles
- Coordinate system: `simple_coordinate` (groupId:artifactId:version) vs full `coordinate` (includes type and scope)
- Tree visualization uses Rich library for console display
- Parser handles both file paths and string inputs
- Depth tracking in dependency tree for analysis purposes
- Polars DataFrames used for advanced analysis (via to_polars_df methods)

## Testing Approach
- CLI functionality likely needs integration tests with sample data files
- Parser validation against example JSON/text files in data/ directories
- Model validation tests for edge cases in dependency structures